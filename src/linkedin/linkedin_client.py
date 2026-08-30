"""
linkedin_client.py — Cliente centralizado para linkedin-api.

Autenticación:
  1. Cookies li_at + JSESSIONID (preferida, dura 60-90 días en uso moderado)
  2. Email + password (fallback, puede requerir CHALLENGE en IP de datacenter)

Cuando las cookies expiran, el bot detecta el loop de redirección automáticamente
y envía alerta por Telegram para que el usuario renueve las cookies.
El usuario solo necesita hacerlo una vez cada 60-90 días.
"""
import os
import re
import logging
import time
import random
from typing import Optional

logger = logging.getLogger(__name__)

_COOKIES_EXPIRED_NOTIFIED = False  # flag para no spamear Telegram


def _notify_cookies_expired():
    """Envía alerta Telegram cuando las cookies de LinkedIn expiran."""
    global _COOKIES_EXPIRED_NOTIFIED
    if _COOKIES_EXPIRED_NOTIFIED:
        return
    _COOKIES_EXPIRED_NOTIFIED = True
    try:
        from src.notifications.telegram_notifier import send_telegram
        send_telegram(
            "🔑 *LinkedIn: Cookies expiradas*\n\n"
            "Las cookies de LinkedIn expiraron (pasa cada 60-90 días).\n\n"
            "Para renovarlas:\n"
            "1. Abre LinkedIn.com en el navegador\n"
            "2. F12 → Application → Cookies\n"
            "3. Copia `li_at` y `JSESSIONID`\n"
            "4. En el servidor ejecuta:\n"
            "`sed -i '/^LINKEDIN_LI_AT=/d' .env`\n"
            "`sed -i '/^LINKEDIN_JSESSIONID=/d' .env`\n"
            "`echo 'LINKEDIN_LI_AT=\"NUEVA\"' >> .env`\n"
            "`echo 'LINKEDIN_JSESSIONID=\"ajax:NUEVO\"' >> .env`"
        )
    except Exception:
        pass


def _save_cookies_to_env(api) -> None:
    """Guarda cookies frescas de una sesión email+password en el .env del servidor."""
    try:
        session_cookies = api.client.session.cookies
        li_at = session_cookies.get("li_at", domain=".linkedin.com")
        jsession = session_cookies.get("JSESSIONID", domain=".linkedin.com", default="")
        jsession = jsession.strip('"').replace('ajax:', '')

        if not li_at:
            return

        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.env')
        env_path = os.path.normpath(env_path)
        if not os.path.exists(env_path):
            return

        with open(env_path, 'r') as f:
            lines = f.readlines()
        lines = [l for l in lines if not l.startswith('LINKEDIN_LI_AT=') and not l.startswith('LINKEDIN_JSESSIONID=')]
        lines.append(f'LINKEDIN_LI_AT="{li_at}"\n')
        lines.append(f'LINKEDIN_JSESSIONID="ajax:{jsession}"\n')
        with open(env_path, 'w') as f:
            f.writelines(lines)
        logger.info("[LinkedInClient] Cookies frescas guardadas en .env automáticamente")
    except Exception as e:
        logger.warning(f"[LinkedInClient] No se pudieron guardar cookies: {e}")


def _get_client():
    """
    Retorna una instancia autenticada de la Linkedin API.
    Intenta cookies primero; si expiraron, usa email+password y guarda cookies nuevas.
    """
    try:
        from linkedin_api import Linkedin
    except ImportError:
        raise RuntimeError(
            "linkedin-api no está instalado. Ejecuta: pip install linkedin-api"
        )

    li_at      = os.environ.get("LINKEDIN_LI_AT", "").strip('"')
    jsessionid = os.environ.get("LINKEDIN_JSESSIONID", "").strip('"')
    email      = os.environ.get("LINKEDIN_EMAIL", "")
    password   = os.environ.get("LINKEDIN_PASSWORD", "")

    # Método 1: cookies (más estable en servidores)
    if li_at and jsessionid:
        import requests as _requests
        raw_jsession = jsessionid.replace('ajax:', '').strip('"')
        jar = _requests.cookies.RequestsCookieJar()
        jar.set("li_at",      li_at,                      domain=".linkedin.com", path="/")
        jar.set("JSESSIONID", f'"ajax:{raw_jsession}"',   domain=".linkedin.com", path="/")
        try:
            api = Linkedin("", "", cookies=jar)
            logger.info("[LinkedInClient] Autenticado via cookies")
            return api
        except Exception as e:
            logger.warning(f"[LinkedInClient] Cookie auth falló: {e}")

    # Método 2: email + password → guarda cookies nuevas automáticamente
    if email and password:
        try:
            api = Linkedin(email, password)
            logger.info("[LinkedInClient] Autenticado via email+password")
            _save_cookies_to_env(api)  # guarda cookies frescas para próxima vez
            return api
        except Exception as e:
            if "CHALLENGE" in str(e):
                _notify_cookies_expired()
                raise RuntimeError(
                    "LinkedIn pide verificación. Se envió alerta a Telegram. "
                    "Ejecuta 'python solve_linkedin_challenge.py' en el servidor."
                )
            raise RuntimeError(f"LinkedIn auth falló (email+password): {e}")

    raise RuntimeError(
        "Configura LINKEDIN_LI_AT + LINKEDIN_JSESSIONID (o LINKEDIN_EMAIL + LINKEDIN_PASSWORD) en .env"
    )


class LinkedInClient:
    """
    Singleton lazy-init: crea la conexión con LinkedIn una sola vez
    por ejecución del bot para evitar múltiples logins.
    """
    _instance: Optional["LinkedInClient"] = None
    _api = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._api = None
        return cls._instance

    @property
    def api(self):
        if self._api is None:
            self._api = _get_client()
        return self._api

    # ─────────────────────────────────────────────────────── #
    #  BÚSQUEDA DE EMPLEOS                                    #
    # ─────────────────────────────────────────────────────── #
    def search_jobs(
        self,
        keywords: str,
        location: str = "Remote",
        limit: int = 15,
        experience: list = None,
    ) -> list:
        """
        Busca empleos en LinkedIn. Retorna lista de dicts con campos
        normalizados para ser compatibles con el resto del pipeline.
        """
        results = []
        try:
            raw = self.api.search_jobs(
                keywords=keywords,
                location_name=location,
                limit=limit,
                experience=experience or [],   # e.g. ["2", "3"] = Mid/Senior
                listed_at=86400,               # últimas 24 horas
                remote=["2"],                  # On-site=1, Remote=2, Hybrid=3
            )

            for item in raw:
                job_id  = item.get("trackingUrn", "").split(":")[-1]
                title   = item.get("title", "")
                company = (
                    item.get("companyDetails", {})
                        .get("com.linkedin.voyager.jobs.jobPostingCompany", {})
                        .get("companyResolutionResult", {})
                        .get("name", "")
                    or item.get("formattedLocation", "")
                )
                url = f"https://www.linkedin.com/jobs/view/{job_id}/" if job_id else ""

                if not title or not job_id:
                    continue

                results.append({
                    "title":       title,
                    "company":     company,
                    "location":    item.get("formattedLocation", "Remote"),
                    "url":         url,
                    "job_id":      job_id,
                    "source":      "LinkedIn",
                    # easy_apply se determina en linkedin_applier al llamar get_job()
                    # search_jobs() devuelve applyMethod vacío siempre
                    "easy_apply":  None,
                    "description": "",
                })
        except Exception as e:
            err = str(e)
            if "30 redirects" in err or "redirect" in err.lower():
                logger.error("[LinkedInClient] Cookies expiradas (redirect loop detectado)")
                _notify_cookies_expired()
            else:
                logger.warning(f"[LinkedInClient] Error buscando '{keywords}': {e}")

        return results

    # ─────────────────────────────────────────────────────── #
    #  EASY APPLY                                             #
    # ─────────────────────────────────────────────────────── #
    def easy_apply(self, job: dict, cv_path: str = None) -> bool:
        """
        Aplica a un empleo con Easy Apply via linkedin-api.
        Retorna True si la aplicación fue enviada exitosamente.
        """
        job_id = job.get("job_id", "")
        if not job_id:
            return False

        try:
            # Obtener detalles del empleo (necesario para el payload de Easy Apply)
            job_detail = self.api.get_job(job_id)

            # linkedin-api maneja el payload de Easy Apply internamente
            # incluyendo los campos del formulario según el puesto
            self.api.easy_apply(
                job_id,
                phone_number=os.environ.get("PROFILE_PHONE", "+593 999999999"),
                follow_company=True,
            )
            return True

        except Exception as e:
            logger.warning(f"[LinkedInClient] Easy Apply falló para job {job_id}: {e}")
            return False

    # ─────────────────────────────────────────────────────── #
    #  BÚSQUEDA DE RECLUTADORES                               #
    # ─────────────────────────────────────────────────────── #
    def search_people(self, keywords: str, limit: int = 10) -> list:
        """
        Busca personas en LinkedIn por keywords.
        Retorna lista de perfiles.
        """
        results = []
        try:
            raw = self.api.search_people(
                keywords=keywords,
                limit=limit,
                # network_depths eliminado: causa 0 resultados en algunas versiones
            )

            for item in raw:
                # Campos reales confirmados por debug: name, jobtitle, urn_id, distance, location
                urn_id   = item.get("urn_id", "")
                nombre   = item.get("name", "")
                headline = item.get("jobtitle", "")

                if urn_id:
                    results.append({
                        "public_id": "",    # se resuelve en add_connection() via urn_id
                        "urn_id":    urn_id,
                        "nombre":    nombre.strip(),
                        "area":      headline,
                    })
        except Exception as e:
            logger.warning(f"[LinkedInClient] Error buscando personas '{keywords}': {e}")

        return results

    # ─────────────────────────────────────────────────────── #
    #  ENVIAR SOLICITUD DE CONEXIÓN                           #
    # ─────────────────────────────────────────────────────── #
    def add_connection(self, profile: dict, message: str = "") -> bool:
        """
        Envía solicitud de conexión usando fs_miniProfile URN.
        El urn_id de search_people() es un fs_miniProfile URN base64.
        linkedin-api acepta profile_urn en format urn:li:fs_miniProfile:{urn_id}.
        """
        urn_id    = profile.get("urn_id", "")
        public_id = profile.get("public_id", "")

        if not urn_id and not public_id:
            logger.warning("[LinkedInClient] Sin urn_id ni public_id para conectar")
            return False

        try:
            if urn_id:
                # Formato correcto para la API de LinkedIn
                profile_urn = f"urn:li:fs_miniProfile:{urn_id}"
                self.api.add_connection(
                    public_id or "",
                    message=message,
                    profile_urn=profile_urn,
                )
            else:
                self.api.add_connection(public_id, message=message)

            # Pausa anti-detección
            time.sleep(random.randint(15, 30))
            return True
        except Exception as e:
            logger.warning(f"[LinkedInClient] Error conectando con {urn_id or public_id}: {e}")
            return False

    # ─────────────────────────────────────────────────────── #
    #  OBTENER URL EXTERNA DE POSTULACIÓN (no Easy Apply)     #
    # ─────────────────────────────────────────────────────── #
    def get_external_apply_url(self, job_id: str) -> str:
        """
        Para empleos sin Easy Apply, obtiene la URL del ATS externo.
        """
        try:
            detail = self.api.get_job(job_id)
            apply_method = detail.get("applyMethod", {})
            # Postulación externa
            external = apply_method.get(
                "com.linkedin.voyager.jobs.OffsiteApply", {}
            )
            return external.get("companyApplyUrl", "")
        except Exception:
            return ""
