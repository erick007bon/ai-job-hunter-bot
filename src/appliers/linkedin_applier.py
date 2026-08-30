"""
linkedin_applier.py — Auto-postulación en LinkedIn usando linkedin-api.

Estrategia:
  1. Si el empleo tiene Easy Apply → enviar directamente via linkedin-api
  2. Si tiene postulación externa → obtener URL del ATS → router lo procesa
  3. Funciona en servidor headless sin Playwright ni detección de bot
"""
import os
import logging
from src.appliers.base_applier import ApplyResult

logger = logging.getLogger(__name__)


class LinkedInApplier:
    """
    Aplica a empleos de LinkedIn via linkedin-api.
    No usa navegador, por lo tanto no puede ser detectado como bot.
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
                portal="LinkedIn", url=url,
                message=str(e)
            )

        # ── Caso 1: Easy Apply disponible ──────────────────────────────────
        if job.get("easy_apply", False):
            print(f"  [LinkedIn] 🟢 Easy Apply disponible → enviando...")
            ok = client.easy_apply(job, cv_path=os.environ.get("CV_PATH", ""))
            if ok:
                return ApplyResult(
                    success=True, job_title=title, company=company,
                    portal="LinkedIn Easy Apply", url=url,
                    message="Easy Apply enviado correctamente"
                )
            else:
                return ApplyResult(
                    success=False, job_title=title, company=company,
                    portal="LinkedIn Easy Apply", url=url,
                    message="Easy Apply falló — ver logs"
                )

        # ── Caso 2: Postulación externa → buscar URL del ATS ───────────────
        print(f"  [LinkedIn] 🔗 Sin Easy Apply → buscando URL externa...")
        external_url = client.get_external_apply_url(job_id)

        if external_url:
            print(f"  [LinkedIn] → Redirigiendo a ATS externo: {external_url[:60]}")
            from src.appliers.router import get_applier_for_url
            applier = get_applier_for_url(external_url, "LinkedIn-External")
            if applier:
                job_copy = dict(job)
                job_copy["url"] = external_url
                return applier.apply_sync(job_copy)

        return ApplyResult(
            success=False, job_title=title, company=company,
            portal="LinkedIn", url=url,
            message="Sin Easy Apply ni URL externa detectable"
        )
