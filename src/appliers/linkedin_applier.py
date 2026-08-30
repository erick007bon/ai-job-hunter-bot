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
            print(f"  [LinkedIn] 🟢 Easy Apply detectado (SimpleOnsiteApply) → enviando...")
            try:
                client.api.easy_apply(
                    job_id,
                    phone_number=os.environ.get("PROFILE_PHONE", "+593963951193"),
                    follow_company=True,
                )
                return ApplyResult(
                    success=True, job_title=title, company=company,
                    portal="LinkedIn Easy Apply", url=url,
                    message="Easy Apply enviado correctamente via linkedin-api"
                )
            except Exception as e:
                logger.warning(f"[LinkedInApplier] Easy Apply falló para {job_id}: {e}")
                return ApplyResult(
                    success=False, job_title=title, company=company,
                    portal="LinkedIn Easy Apply", url=url,
                    message=f"Easy Apply falló: {e}"
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
