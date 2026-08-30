"""
linkedin_applier.py — Auto-postulación en LinkedIn usando linkedin-api.

Estrategia (confirmada con debug de payloads reales):
  1. Llama a get_job(job_id) para obtener el applyMethod real
  2. Si tiene SimpleOnsiteApply → Easy Apply nativo de LinkedIn
  3. Si tiene OffsiteApply → obtener URL del ATS externo → router lo procesa
  4. Sin Playwright, sin anti-bot, funciona en GCP 24/7
"""
import os
import logging
from src.appliers.base_applier import ApplyResult

logger = logging.getLogger(__name__)

# Claves confirmadas por debug real de la API de LinkedIn
EASY_APPLY_KEY    = "com.linkedin.voyager.jobs.SimpleOnsiteApply"
OFFSITE_APPLY_KEY = "com.linkedin.voyager.jobs.OffsiteApply"


class LinkedInApplier:
    """
    Aplica a empleos de LinkedIn via linkedin-api.
    No usa navegador — inmune a detección de bot en servidores.
    """

    def apply_sync(self, job: dict) -> ApplyResult:
        title   = job.get("title", "Puesto")
        company = job.get("company", "Empresa")
        url     = job.get("url", "")
        job_id  = job.get("job_id", "")

        # Extraer job_id de la URL si no viene en el dict
        if not job_id and "jobs/view/" in url:
            job_id = url.rstrip("/").split("/")[-1]

        if not job_id:
            return ApplyResult(
                success=False, job_title=title, company=company,
                portal="LinkedIn", url=url,
                message="Sin job_id — no se puede aplicar"
            )

        try:
            from src.linkedin.linkedin_client import LinkedInClient
            client = LinkedInClient()
        except RuntimeError as e:
            return ApplyResult(
                success=False, job_title=title, company=company,
                portal="LinkedIn", url=url, message=str(e)
            )

        # ── Obtener detalles del empleo (applyMethod real) ─────────────────
        try:
            detail       = client.api.get_job(job_id)
            apply_method = detail.get("applyMethod", {})
        except Exception as e:
            return ApplyResult(
                success=False, job_title=title, company=company,
                portal="LinkedIn", url=url,
                message=f"Error al obtener detalles del empleo: {e}"
            )

        # ── Caso 1: Easy Apply nativo de LinkedIn ──────────────────────────
        if EASY_APPLY_KEY in apply_method:
            print(f"  [LinkedIn] 🟢 Easy Apply detectado (SimpleOnsiteApply) → enviando via Voyager API...")
            ok = self._easy_apply_voyager(client, job_id, title, company)
            if ok:
                return ApplyResult(
                    success=True, job_title=title, company=company,
                    portal="LinkedIn Easy Apply", url=url,
                    message="Easy Apply enviado correctamente via Voyager API"
                )
            else:
                return ApplyResult(
                    success=False, job_title=title, company=company,
                    portal="LinkedIn Easy Apply", url=url,
                    message="Easy Apply falló — ver logs para detalles"
                )

        # ── Caso 2: Postulación externa (ATS de la empresa) ───────────────
        offsite     = apply_method.get(OFFSITE_APPLY_KEY, {})
        external_url = (
            offsite.get("companyApplyUrl", "")
            or offsite.get("easyApplyUrl", "")
        )

        if external_url:
            print(f"  [LinkedIn] 🔗 ATS externo detectado → {external_url[:70]}")
            try:
                from src.appliers.router import get_applier_for_url
                applier = get_applier_for_url(external_url, "LinkedIn-External")
                if applier:
                    job_copy       = dict(job)
                    job_copy["url"] = external_url
                    return applier.apply_sync(job_copy)
            except Exception as e:
                logger.warning(f"[LinkedInApplier] Error al redirigir ATS externo: {e}")

            return ApplyResult(
                success=False, job_title=title, company=company,
                portal="LinkedIn-External", url=external_url,
                message="ATS externo detectado pero sin applier disponible"
            )

        # ── Caso 3: Sin método de aplicación detectable ────────────────────
        print(f"  [LinkedIn] ⚠️ applyMethod vacío o desconocido: {list(apply_method.keys())}")
        return ApplyResult(
            success=False, job_title=title, company=company,
            portal="LinkedIn", url=url,
            message=f"Sin Easy Apply ni URL externa detectable. Keys: {list(apply_method.keys())}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    def _easy_apply_voyager(self, client, job_id: str, title: str, company: str) -> bool:
        """
        Implementa Easy Apply usando la sesión autenticada de linkedin-api
        para hacer POST directo al Voyager API de LinkedIn.

        La librería linkedin-api no expone easy_apply() en versiones recientes,
        pero sí nos da acceso a la sesión requests con cookies válidas.
        """
        try:
            session    = client.api.client.session
            jsessionid = os.environ.get("LINKEDIN_JSESSIONID", "").strip('"').replace("ajax:", "").strip()

            payload = {
                "jobs": [
                    {
                        "jobPostingUrn":  f"urn:li:fsd_jobPosting:{job_id}",
                        "trackingId":     job_id,
                        "resumeHidden":   False,
                        "followCompany":  True,
                        "questionAndAnswers": [],
                        "contactInfo": {
                            "firstName":    "Erick",
                            "lastName":     "Flores Zambrano",
                            "emailAddress": os.environ.get("EMAIL_USER", "eflores4006@utm.edu.ec"),
                            "phoneNumber":  os.environ.get("PROFILE_PHONE", "+593963951193"),
                        },
                    }
                ]
            }

            headers = {
                "csrf-token":               jsessionid,
                "Content-Type":             "application/json",
                "X-RestLi-Protocol-Version": "2.0.0",
                "Accept":                   "application/vnd.linkedin.normalized+json+2.1",
                "Referer":                  f"https://www.linkedin.com/jobs/view/{job_id}/",
            }

            resp = session.post(
                "https://www.linkedin.com/voyager/api/jobs/normalizedJobApplications",
                json=payload,
                headers=headers,
                timeout=20,
            )

            logger.info(f"[EasyApply] Response {resp.status_code} para job {job_id}")

            if resp.status_code in (200, 201):
                print(f"  [LinkedIn] ✅ Easy Apply enviado (status {resp.status_code})")
                return True
            else:
                logger.warning(
                    f"[EasyApply] Error {resp.status_code}: {resp.text[:200]}"
                )
                return False

        except Exception as e:
            logger.warning(f"[EasyApply] Excepción al llamar Voyager API: {e}")
            return False
