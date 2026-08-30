import os
import json
from playwright.async_api import async_playwright
from .base_applier import BaseApplier, ApplyResult


class JobviteApplier(BaseApplier):
    """
    Postula automáticamente en tableros de Jobvite (jobs.jobvite.com).
    """

    def __init__(self):
        super().__init__()
        from src.config import Config
        self.cv_path = Config.CV_PDF_PATH
        self.cv_data = {}
        try:
            with open(Config.CV_PATH, "r", encoding="utf-8") as f:
                self.cv_data = json.load(f)
        except Exception as e:
            print(f"  [JOBVITE] Error cargando cv_erick_data.json: {e}")

    async def apply(self, job: dict) -> ApplyResult:
        url = job.get('url', '')
        title = job.get('title', 'Sin Título')
        company = job.get('company', 'Jobvite')

        if not url:
            return ApplyResult(title, company, "Jobvite", url, False, "URL vacía")

        try:
            async with async_playwright() as p:
                context = await self._get_context(p)
                page = await context.new_page()

                print(f"  [JOBVITE] Navegando a {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await self._human_delay(2.0, 4.0)

                # Jobvite a veces tiene iframe o redirección
                apply_btn = page.locator("a:has-text('Apply'), button:has-text('Apply'), input[value='Apply']")
                if await apply_btn.count() > 0:
                    await apply_btn.first.click()
                    await self._human_delay(1.5, 3.0)

                # --- 1. Subir CV ---
                os.makedirs("debug_screenshots", exist_ok=True)
                await page.screenshot(path=f"debug_screenshots/{company}_1_before_cv.png")
                file_input = page.locator("input[type='file'][name='resume'], input[type='file'][accept*='pdf']")
                if await file_input.count() > 0:
                    if os.path.exists(self.cv_path):
                        print("  [JOBVITE] Subiendo CV...")
                        await file_input.first.set_input_files(self.cv_path)
                        await self._human_delay(2.0, 3.5)

                # --- 2. Llenar campos ---
                await page.screenshot(path=f"debug_screenshots/{company}_2_after_cv.png")
                full_name = self.cv_data.get('personal_info', {}).get('name', 'Erick Flores Zambrano')
                email = self.cv_data.get('personal_info', {}).get('email', 'eflores4006@utm.edu.ec')
                phone = self.cv_data.get('personal_info', {}).get('phone', os.environ.get('CANDIDATE_PHONE', ''))

                fields_to_fill = [
                    ("input[name='j_first_name']", full_name.split()[0]),
                    ("input[name='j_last_name']", " ".join(full_name.split()[1:])),
                    ("input[name='j_email']", email),
                    ("input[name='j_phone']", phone),
                ]

                for selector, value in fields_to_fill:
                    element = page.locator(selector)
                    if await element.count() > 0:
                        await self._human_type(page, selector, value)

                # --- 3. Enviar aplicación ---
                await page.screenshot(path=f"debug_screenshots/{company}_3_before_submit.png")
                submit_btn = page.locator("input[type='submit'], button[type='submit'], button:has-text('Submit')")
                if await submit_btn.count() > 0:
                    await submit_btn.first.click()
                    await self._human_delay(2.0, 3.5)

                await context.close()
                return ApplyResult(title, company, "Jobvite", url, True, "Postulación enviada exitosamente a Jobvite")

        except Exception as e:
            return ApplyResult(title, company, "Jobvite", url, False, f"Error Jobvite: {str(e)[:100]}")