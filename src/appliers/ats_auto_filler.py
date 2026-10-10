"""ATS Auto-Filler via Playwright — postulación a formularios ocultos."""
import re
from typing import Optional, Dict


class ATSAutoFiller:
    """Auto-llenador headless para formularios ATS ocultos identificados en URLs."""

    ATS_PATTERNS = {
        "airtable": r"(https?://airtable\.com/[a-zA-Z0-9_\-/]+)",
        "teamtailor": r"(https?://[a-zA-Z0-9-]+\.teamtailor\.net/[a-zA-Z0-9_\-/]+)",
        "micro1": r"(https?://[a-zA-Z0-9-]+\.micro1\.ai/[a-zA-Z0-9_\-/]+)",
        "bairesdev": r"(https?://[a-zA-Z0-9-]+\.bairesdev\.com/[a-zA-Z0-9_\-/]+)",
    }

    def __init__(self, cv_path: str = "data/CV_Erick_Flores_Data_AI.pdf"):
        self.cv_path = cv_path
        self.filled = 0

    def extract_ats_url(self, linkedin_url: str) -> Optional[str]:
        """Extrae URL de formulario ATS oculto de una URL de oferta."""
        for name, pat in self.ATS_PATTERNS.items():
            m = re.search(pat, linkedin_url, re.IGNORECASE)
            if m:
                return m.group(1)
        return None

    def fill_form(self, form_url: str, fields: Dict) -> bool:
        """Simula llenado headless de formulario ATS."""
        if not form_url or not fields.get("email"):
            return False
        self.filled += 1
        # Playwright headless se integrará aquí con browser.launch()
        return True
