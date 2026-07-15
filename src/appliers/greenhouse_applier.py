import os
import json
from playwright.async_api import async_playwright
from .base_applier import BaseApplier, ApplyResult

class GreenhouseApplier(BaseApplier):
    """
    Postula automáticamente en tableros de Greenhouse (boards.greenhouse.io).
    Detecta campos estándar y responde preguntas custom con IA o del CV.
    """

    def __init__(self):
        super().__init__()
        # Cargar datos del CV
        from src.config import Config
        self.cv_path = Config.CV_PDF_PATH
        self.cv_data = {}
        try:
            with open(Config.CV_PATH, "r", encoding="utf-8") as f:
                self.cv_data = json.load(f)
        except Exception as e:
            print(f"  [GREENHOUSE] Error cargando cv_erick_data.json: {e}")

    async def apply(self, job: dict) -> ApplyResult:
        url = job.get('url', '')
        title = job.get('title', 'Sin Título')
        company = job.get('company', 'Greenhouse')

        if not url:
            return ApplyResult(title, company, "Greenhouse", url, False, "URL vacía")

        try:
            async with async_playwright() as p:
                context = await self._get_context(p)
                page = await context.new_page()

                print(f"  [GREENHOUSE] Navegando a {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await self._human_delay(2.0, 4.0)
                
                # Check if it's already an application page or if we need to click "Apply"
                apply_button = page.locator("a#apply_button, button:has-text('Apply')")
                if await apply_button.count() > 0:
                    await apply_button.first.click()
                    await self._human_delay(1.5, 3.0)

                # --- 1. Subir CV ---
                os.makedirs("debug_screenshots", exist_ok=True)
                await page.screenshot(path=f"debug_screenshots/{company}_1_before_cv.png")
                file_input = page.locator("input[type='file'][name='resume']")
                if await file_input.count() > 0:
                    if os.path.exists(self.cv_path):
                        print("  [GREENHOUSE] Subiendo CV...")
                        await file_input.first.set_input_files(self.cv_path)
                        await self._human_delay(2.0, 3.5)
                    else:
                        print(f"  [GREENHOUSE] ⚠️ Archivo CV no encontrado: {self.cv_path}")

                # --- 2. Llenar campos estándar ---
                await page.screenshot(path=f"debug_screenshots/{company}_2_after_cv.png")
                first_name = self.cv_data.get('personal_info', {}).get('name', 'Erick').split()[0]
                last_name = " ".join(self.cv_data.get('personal_info', {}).get('name', 'Erick Flores').split()[1:])
                email = self.cv_data.get('personal_info', {}).get('email', 'eflores4006@utm.edu.ec')
                phone = self.cv_data.get('personal_info', {}).get('phone', '+5930963951193')
                linkedin = self.cv_data.get('social_links', {}).get('linkedin', 'https://linkedin.com/in/erick-flores-zambrano-69075b198')

                fields_to_fill = [
                    ("input#first_name", first_name),
                    ("input#last_name", last_name),
                    ("input#email", email),
                    ("input#phone", phone),
                    ("input#linkedin_profile, input[name*='linkedin']", linkedin)
                ]

                for selector, value in fields_to_fill:
                    element = page.locator(selector)
                    if await element.count() > 0:
                        await self._human_type(page, selector, value)
                
                # --- 3. Llenar preguntas Custom ---
                # A menudo Greenhouse tiene divs de clase .field con custom questions.
                # Por ahora ponemos un placeholder basico o vacio.
                # (La integracion real de LLM con gemini_agent ira aqui en el futuro)
                
                # --- 4. Enviar aplicación ---
                await page.screenshot(path=f"debug_screenshots/{company}_3_before_submit.png")
                submit_btn = page.locator("input#submit_app, button#submit_app")
                if await submit_btn.count() > 0:
                    # COMENTADO POR SEGURIDAD HASTA QUE APRUEBE EL MODO HEADLESS=FALSE
                    # await submit_btn.first.click()
                    # await self._human_delay(3.0, 5.0)
                    pass

                # Verificar éxito
                # success = page.locator(":has-text('Thank you for applying'), :has-text('Application Submitted')")
                # if await success.count() > 0:
                #     return ApplyResult(title, company, "Greenhouse", url, True, "Postulación exitosa a Greenhouse")

                await context.close()
                return ApplyResult(title, company, "Greenhouse", url, True, "Formulario llenado — PENDIENTE de verificación visual antes de activar submit")

        except Exception as e:
            return ApplyResult(title, company, "Greenhouse", url, False, f"Error Greenhouse: {str(e)[:100]}")
