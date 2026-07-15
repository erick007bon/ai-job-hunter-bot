"""
Multitrabajos Applier — Auto-postulación en multitrabajos.net (Ecuador/LATAM).
Flujo: Login → Navegar a oferta → Subir CV → Enviar postulación.
"""
import os
import asyncio
from playwright.async_api import async_playwright
from .base_applier import BaseApplier, ApplyResult


class MultitrabajosApplier(BaseApplier):
    """
    Postula automáticamente en Multitrabajos (bumeran.com Ecuador).
    Credenciales desde variables de entorno: MULTITRABAJOS_EMAIL, MULTITRABAJOS_PASSWORD
    """

    LOGIN_URL = "https://www.multitrabajos.com/login"
    BASE_URL = "https://www.multitrabajos.com"

    def __init__(self):
        super().__init__()
        self.email = os.environ.get("MULTITRABAJOS_EMAIL", "")
        self.password = os.environ.get("MULTITRABAJOS_PASSWORD", "")
        self.cv_path = os.environ.get("CV_PATH", "CV_Erick_Flores.pdf")
        self._logged_in = False

    async def _login(self, page) -> bool:
        """Inicia sesión en Multitrabajos. Retorna True si exitoso."""
        if not self.email or not self.password:
            print("  [MULTITRABAJOS] Credenciales no configuradas en .env")
            return False

        try:
            await page.goto(self.LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
            await self._human_delay(1.5, 3.0)

            # Verificar si ya está logueado (cookie de sesión activa)
            if await page.locator("a[href*='logout'], a[href*='cerrar-sesion'], .user-menu").count() > 0:
                print("  [MULTITRABAJOS] Sesión activa (cookie guardada)")
                return True

            # Llenar formulario de login
            email_sel = "input[name='email'], input[type='email'], #email"
            pass_sel  = "input[name='password'], input[type='password'], #password"

            await page.wait_for_selector(email_sel, timeout=10000)
            await self._human_type(page, email_sel, self.email)
            await self._human_delay(0.5, 1.2)
            await self._human_type(page, pass_sel, self.password)
            await self._human_delay(0.8, 1.8)

            # Click en botón de ingreso
            login_btn = page.locator("button[type='submit'], input[type='submit'], .login-btn, button:has-text('Ingresar')")
            await login_btn.first.click()
            await self._human_delay(2.5, 4.0)

            # Verificar login exitoso
            current_url = page.url
            if "login" not in current_url or await page.locator(".user-menu, [class*='user-name']").count() > 0:
                print("  [MULTITRABAJOS] ✅ Login exitoso")
                return True
            else:
                print("  [MULTITRABAJOS] ❌ Login fallido — verificar credenciales")
                return False

        except Exception as e:
            print(f"  [MULTITRABAJOS] Error en login: {e}")
            return False

    async def apply(self, job: dict) -> ApplyResult:
        """
        Flujo completo de postulación en Multitrabajos.
        Soporta dos casos:
        1. Formulario nativo de Multitrabajos
        2. Redirección a HiringRoom/portal externo
        """
        title   = job.get("title", "Puesto")
        company = job.get("company", "Empresa")
        url     = job.get("url", "")

        if not url:
            result = ApplyResult(title, company, "Multitrabajos", url, False, "Sin URL")
            return result

        print(f"\n  [MULTITRABAJOS] Postulando: {title} @ {company}")

        async with async_playwright() as p:
            context = await self._get_context(p)
            page = await context.new_page()

            try:
                # 1. LOGIN
                logged = await self._login(page)
                if not logged:
                    await context.close()
                    result = ApplyResult(title, company, "Multitrabajos", url, False, "Login fallido")
                    return result

                # 2. NAVEGAR A LA OFERTA
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await self._human_delay(2.0, 4.0)

                # 3. BUSCAR BOTÓN DE POSTULAR
                apply_btn = page.locator(
                    "a:has-text('Postularme'), button:has-text('Postularme'), "
                    "a:has-text('Aplicar'), button:has-text('Aplicar'), "
                    ".apply-btn, [data-qa='btn-apply']"
                )

                if await apply_btn.count() == 0:
                    await context.close()
                    result = ApplyResult(title, company, "Multitrabajos", url, False, "Botón postular no encontrado")
                    return result

                await apply_btn.first.click()
                await self._human_delay(2.0, 3.5)

                # 4. DETECTAR TIPO DE FORMULARIO
                current_url = page.url

                # Caso A: Redirige a HiringRoom
                if "hiringroom.com" in current_url:
                    result = await self._apply_hiringroom(page, title, company, url)
                    await context.close()
                    return result

                # Caso B: Formulario propio de Multitrabajos/Bumeran
                result = await self._apply_native_form(page, title, company, url)
                await context.close()
                return result

            except Exception as e:
                await context.close()
                result = ApplyResult(title, company, "Multitrabajos", url, False, f"Error: {str(e)[:100]}")
                return result

    async def _apply_native_form(self, page, title, company, url) -> ApplyResult:
        """Formulario nativo de Multitrabajos/Bumeran."""
        try:
            await self._human_delay(1.5, 3.0)

            # Subir CV si hay campo de archivo
            file_input = page.locator("input[type='file']")
            if await file_input.count() > 0 and os.path.exists(self.cv_path):
                await file_input.first.set_input_files(self.cv_path)
                print(f"    [CV] Subido: {self.cv_path}")
                await self._human_delay(2.0, 4.0)

            # Buscar y clickear botón de confirmación/envío
            confirm_btn = page.locator(
                "button:has-text('Enviar'), button:has-text('Confirmar'), "
                "button:has-text('Postular'), button[type='submit']"
            )
            if await confirm_btn.count() > 0:
                await confirm_btn.first.click()
                await self._human_delay(2.5, 4.0)

            # Verificar éxito
            success_msg = page.locator(
                ":has-text('postulación exitosa'), :has-text('postulación enviada'), "
                ":has-text('aplicación enviada'), :has-text('¡Tu postulación')"
            )
            if await success_msg.count() > 0:
                print(f"    ✅ Postulación exitosa: {title}")
                return ApplyResult(title, company, "Multitrabajos", url, True, "Postulación enviada")

            return ApplyResult(title, company, "Multitrabajos", url, True, "Formulario enviado (verificar manualmente)")

        except Exception as e:
            return ApplyResult(title, company, "Multitrabajos", url, False, f"Error formulario: {str(e)[:100]}")

    async def _apply_hiringroom(self, page, title, company, url) -> ApplyResult:
        """
        Formulario de HiringRoom (portal ATS externo muy común en Ecuador).
        Flujo: Importar desde Multitrabajos → Datos personales → Enviar.
        """
        try:
            print(f"    [HiringRoom] Detectado formulario externo")
            await self._human_delay(2.0, 3.5)

            # Paso 1: Importar CV desde Multitrabajos
            multitrabajos_btn = page.locator(":has-text('Multitrabajos'), :has-text('multitrabajos')")
            if await multitrabajos_btn.count() > 0:
                await multitrabajos_btn.first.click()
                await self._human_delay(1.5, 3.0)

                # Llenar credenciales en modal
                email_field = page.locator("input[type='email'], input[name='email']")
                pass_field  = page.locator("input[type='password'], input[name='password']")

                if await email_field.count() > 0:
                    await self._human_type(page, "input[type='email']", self.email)
                    await self._human_delay(0.5, 1.0)
                    await self._human_type(page, "input[type='password']", self.password)
                    await self._human_delay(0.5, 1.0)

                    # Click Ingresar
                    ingresar_btn = page.locator("button:has-text('Ingresar'), input[type='submit']")
                    if await ingresar_btn.count() > 0:
                        await ingresar_btn.first.click()
                        await self._human_delay(3.0, 5.0)

            # Paso 2: Ir a "Siguiente" en cada paso del formulario
            for step in range(3):  # Máx 3 pasos
                next_btn = page.locator(
                    "button:has-text('Siguiente'), button:has-text('Continuar'), "
                    "button:has-text('Next'), .btn-next"
                )
                if await next_btn.count() > 0:
                    await next_btn.first.click()
                    await self._human_delay(2.0, 3.5)

            # Paso 3: Enviar postulación final
            submit_btn = page.locator(
                "button:has-text('Enviar postulación'), button:has-text('Postularme'), "
                "button[type='submit']:has-text('Enviar')"
            )
            if await submit_btn.count() > 0:
                await submit_btn.first.click()
                await self._human_delay(3.0, 5.0)

            # Verificar éxito
            success = page.locator(":has-text('postulación fue realizada'), :has-text('correctamente')")
            if await success.count() > 0:
                print(f"    ✅ HiringRoom: Postulación exitosa — {title}")
                return ApplyResult(title, company, "HiringRoom", url, True, "Postulación enviada vía HiringRoom")

            return ApplyResult(title, company, "HiringRoom", url, True, "Formulario HiringRoom enviado")

        except Exception as e:
            return ApplyResult(title, company, "HiringRoom", url, False, f"Error HiringRoom: {str(e)[:100]}")
