import json
import os
from playwright.sync_api import Page

CV_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cv_erick_data.json')

class FormFiller:
    def __init__(self):
        self.cv_data = self._load_cv()
        
    def _load_cv(self):
        if os.path.exists(CV_FILE):
            with open(CV_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def fill_linkedin_easy_apply(self, page: Page):
        """
        Lógica básica para LinkedIn Easy Apply
        """
        print("[FormFiller] Intentando buscar el botón Easy Apply...")
        try:
            # Buscar el botón de postulación sencilla
            apply_button = page.locator("button:has-text('Easy Apply'), button:has-text('Solicitar Sencillamente')")
            if apply_button.count() > 0:
                apply_button.first.click()
                print("  -> ¡Botón presionado! Entrando al flujo de postulación.")
                
                # Aquí iría la lógica recursiva para presionar Next/Siguiente y llenar campos
                return True
            else:
                print("  -> No se encontró el botón de Easy Apply.")
                return False
        except Exception as e:
            print(f"[FormFiller] Error al llenar formulario: {e}")
            return False
