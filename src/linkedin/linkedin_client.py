"""
linkedin_client.py — Cliente centralizado para linkedin-api.

Proporciona autenticación y acceso unificado a todas las funciones
de LinkedIn: búsqueda de empleos, Easy Apply, búsqueda de personas
y envío de solicitudes de conexión.

Usa email + password (más estable que cookies para automatización 24/7).
"""
import os
import logging
import time
import random
from typing import Optional

logger = logging.getLogger(__name__)


def _get_client():
    """
    Retorna una instancia autenticada de la Linkedin API.
    Intenta cookies primero (más estable en IPs de servidor),
    y si no, usa email + password.
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

    # Método 1: cookies (más estable en servidores — no activa verificación de IP)
    if li_at and jsessionid:
        raw_jsession = jsessionid.replace('ajax:', '')
        cookies = {
            "li_at":     li_at,
            "JSESSIONID": f'"ajax:{raw_jsession}"',
        }
        try:
            api = Linkedin("", "", cookies=cookies)
            logger.info("[LinkedInClient] Autenticado via cookies")
            return api
        except Exception as e:
            logger.warning(f"[LinkedInClient] Cookie auth falló: {e}")

    # Método 2: email + password
    if email and password:
        try:
            api = Linkedin(email, password)
            logger.info("[LinkedInClient] Autenticado via email+password")
            return api
        except Exception as e:
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
                    "easy_apply":  item.get("applyMethod", {}).get(
                                       "com.linkedin.voyager.jobs.ComplexOnsiteApply"
                                   ) is not None,
                    "description": "",
                })
        except Exception as e:
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
                network_depths=["S", "O"],   # 2do y 3er grado
            )

            for item in raw:
                public_id  = item.get("publicIdentifier", "")
                name       = item.get("firstName", "") + " " + item.get("lastName", "")
                headline   = item.get("headline", "")
                urn_id     = item.get("urn_id", "")

                if public_id:
                    results.append({
                        "public_id": public_id,
                        "urn_id":    urn_id,
                        "nombre":    name.strip(),
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
        Envía solicitud de conexión con nota personalizada.
        """
        public_id = profile.get("public_id", "")
        if not public_id:
            return False

        try:
            self.api.add_connection(public_id, message=message)
            # Pausa anti-detección
            time.sleep(random.randint(15, 30))
            return True
        except Exception as e:
            logger.warning(f"[LinkedInClient] Error conectando con {public_id}: {e}")
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
