"""
linkedin_applier.py — Aplica a ofertas de LinkedIn usando Easy Apply (Playwright).

Estrategia:
  1. Navega a la URL del empleo en LinkedIn con cookies de sesión
  2. Si existe el botón "Easy Apply" → hace clic y completa el formulario automáticamente
  3. Si hay redirección externa → retorna la URL del ATS para que el router la procese
"""
import os
import time
import asyncio
from typing import Optional
from src.appliers.base_applier import BaseApplier, ApplyResult
from src.config import Config


class LinkedInApplier(BaseApplier):
    """
    Aplica a empleos de LinkedIn usando Easy Apply.
    Usa Playwright con cookies de sesión para autenticarse automáticamente.
    """

    def __init__(self):
        self.li_at      = Config.LINKEDIN_LI_AT
        self.jsessionid = Config.LINKEDIN_JSESSIONID

    async def apply(self, job: dict) -> ApplyResult:
        from playwright.async_api import async_playwright

        url     = job.get('url', '')
        title   = job.get('title', 'Puesto')
        company = job.get('company', 'Empresa')
        cv_path = os.environ.get('CV_PATH', 'data/CV_Erick_Flores_EN.pdf')

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            # Inyectar cookies de sesión de LinkedIn
            await context.add_cookies([
                {
                    "name": "li_at",
                    "value": self.li_at,
                    "domain": ".linkedin.com",
                    "path": "/",
                    "httpOnly": True,
                    "secure": True,
                },
                {
                    "name": "JSESSIONID",
                    "value": f'"{self.jsessionid}"',
                    "domain": ".linkedin.com",
                    "path": "/",
                    "httpOnly": False,
                    "secure": True,
                },
            ])

            page = await context.new_page()

            try:
                # CRÍTICO: ir a linkedin.com primero para activar las cookies de sesión
                # De lo contrario Playwright arranca sin sesión y LinkedIn entra en redirect loop
                await page.goto("https://www.linkedin.com/", wait_until="domcontentloaded", timeout=20000)
                await asyncio.sleep(2)

                # Verificar que estamos logueados (no en página de login)
                if "login" in page.url or "authwall" in page.url:
                    await browser.close()
                    return ApplyResult(
                        success=False, job_title=title, company=company,
                        portal="LinkedIn", url=url,
                        message="Cookies expiradas — renovar li_at y JSESSIONID en .env"
                    )

                # Ahora sí navegar al empleo
                await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                await asyncio.sleep(2)

                # ── Buscar botón Easy Apply ──────────────────────────────────
                easy_apply = page.locator(
                    "button.jobs-apply-button, "
                    "button[aria-label*='Easy Apply'], "
                    "button[data-control-name='jobdetails_topcard_inapply']"
                ).first

                if await easy_apply.is_visible(timeout=5000):
                    await easy_apply.click()
                    await asyncio.sleep(2)

                    # Subir CV si hay campo de upload
                    upload_input = page.locator("input[type='file']").first
                    if cv_path and os.path.isfile(cv_path) and await upload_input.is_visible(timeout=3000):
                        await upload_input.set_input_files(cv_path)
                        await asyncio.sleep(1)

                    # Siguiente / Revisar / Enviar
                    for btn_label in ["Siguiente", "Next", "Revisar", "Review", "Enviar solicitud", "Submit application"]:
                        btn = page.locator(f"button:has-text('{btn_label}')").first
                        if await btn.is_visible(timeout=2000):
                            await btn.click()
                            await asyncio.sleep(1.5)

                    await browser.close()
                    return ApplyResult(
                        success=True,
                        job_title=title,
                        company=company,
                        portal="LinkedIn Easy Apply",
                        url=url,
                        message="Easy Apply enviado"
                    )

                # ── Sin Easy Apply → reportar para cold-email ────────────────
                await browser.close()
                return ApplyResult(
                    success=False,
                    job_title=title,
                    company=company,
                    portal="LinkedIn",
                    url=url,
                    message="Sin botón Easy Apply — postulación manual necesaria"
                )

            except Exception as e:
                await browser.close()
                return ApplyResult(
                    success=False,
                    job_title=title,
                    company=company,
                    portal="LinkedIn",
                    url=url,
                    message=f"Error: {str(e)[:120]}"
                )
