"""ATS Auto-Filler via Playwright — postulación directa a formularios ocultos."""
import re
from typing import Optional

class ATSAutoFiller:
    def __init__(self, cv_path: str = "data/CV_Erick_Flores_Data_AI.pdf"):
        self.cv_path = cv_path
        self.filled = 0

    def extract_form_url(self, linkedin_url: str) -> Optional[str]:
        # Regex para formularios ATS conocidos: Airtable, Teamtailor, BairesDev, Micro1
        patterns = [
            r"(https?://airtable\.com/[^\s\"]+)",
            r"(https?://apply\.workable\.com/[^\s\"]+)",
            r"(https?://boards\.greenhouse\.io/[^\s\"]+)",
            r"(https?://jobs\.lever\.co/[^\s\"]+)",
        ]
        for p in patterns:
            m = re.search(p, linkedin_url)
            if m:
                return m.group(1)
        return None

    def fill_and_submit(self, form_url: str, fields: dict) -> bool:
        # Playwright headless llenaría campos; aquí es esqueleto para TDD
        if not form_url or not fields.get("email"):
            return False
        self.filled += 1
        return True
