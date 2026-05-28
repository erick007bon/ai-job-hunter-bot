"""
Scholarship Agent — Genera cartas de aplicación para becas usando IA.
"""
import os
import json
import requests
from typing import Dict
from src.config import Config

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-31b-it:free",
    "deepseek/deepseek-v4-flash:free",
]

class ScholarshipAgent:
    """Genera cartas de motivación personalizadas para becas internacionales."""

    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.cv = self._load_cv()

    def _load_cv(self) -> dict:
        if os.path.exists(Config.CV_PATH):
            with open(Config.CV_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _call_ai(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/erick007bon",
        }
        for model in FREE_MODELS:
            try:
                r = requests.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json={"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 800},
                    timeout=30
                )
                r.raise_for_status()
                result = r.json()['choices'][0]['message']['content']
                if result and len(result) > 100:
                    return result
            except Exception:
                continue
        return self._fallback_letter()

    def generate_motivation_letter(self, scholarship: Dict) -> str:
        nombre = self.cv.get('personal_info', {}).get('nombre', 'Erick Flores Zambrano')
        perfil = self.cv.get('perfil_profesional', '')

        prompt = f"""You are an expert at writing scholarship motivation letters for Latin American researchers.

APPLICANT:
- Name: {nombre}
- Profile: {perfil}
- Key Achievement: Developed FCH-ARX V4, a cryptographic hash algorithm that passed NIST FIPS 180-4 
  validation (49.95% avalanche effect, 2^256 collision resistance). Research is original and publishable.
- Education: Double degree — Economics (UTM) + Data Science & AI Engineering (U. Guayaquil, 4th semester)
- Current job: Commercial Advisor at Vamoret S.A. (not related to AI) — wants to transition to AI research
- Country: Ecuador, Latin America
- English: B2 level

SCHOLARSHIP:
- Name: {scholarship['name']}
- Organization: {scholarship['organization']}
- Description: {scholarship['description']}
- Amount: {scholarship['amount']}

TASK: Write a 300-word motivation letter in English that:
1. Opens with the specific research problem (cryptography + AI for IoT/embedded systems)
2. Connects FCH-ARX V4 research to the scholarship's goals
3. Shows the "gap" — researching independently while working full-time, scholarship would allow full focus
4. Mentions the double academic background as strength (economics + CS = unique perspective)
5. Ends with a concrete research plan for what you'd do with this funding
6. Tone: humble but confident, data-driven, not generic

Write ONLY the letter body (no subject, no greeting header needed).
"""
        return self._call_ai(prompt)

    def _fallback_letter(self) -> str:
        return """I am writing to apply for this scholarship opportunity. As an independent researcher 
from Ecuador, I have been developing FCH-ARX V4, a novel cryptographic hash algorithm that successfully 
passed the NIST FIPS 180-4 standard validation, achieving a 49.95% avalanche effect and demonstrating 
2^256 collision resistance.

My research sits at the intersection of applied cryptography and embedded systems AI, addressing real 
security needs for IoT devices that cannot afford hardware SHA accelerators. While pursuing dual degrees 
in Economics and Data Science & AI Engineering, I have conducted this research independently while 
working full-time — a testament to my commitment to advancing my field.

This scholarship would allow me to dedicate full attention to formalizing the mathematical proof of 
FCH-ARX V4, extending it to a 512-bit variant for digital signatures, and publishing in indexed 
Latin American journals (Scielo, RISTI). I am seeking peer review from external cryptographers to 
strengthen the academic contribution.

My background in economics combined with computer science gives me a unique perspective on optimization 
problems — I approach algorithm design with both mathematical rigor and practical resource constraints 
in mind.

I would be honored to represent Ecuador and Latin America in this program.

Sincerely,
Erick Flores Zambrano
Data Science & AI Engineering Student | Independent Cryptography Researcher
adanrivas6655@gmail.com | github.com/erick007bon"""

    def save_letter(self, scholarship: Dict, letter: str) -> str:
        safe_name = "".join(c for c in scholarship['name'] if c.isalnum() or c in '_- ')[:30]
        os.makedirs(Config.COVER_LETTERS_DIR, exist_ok=True)
        path = os.path.join(Config.COVER_LETTERS_DIR, f"BECA_{safe_name.replace(' ', '_')}.md")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# Motivation Letter — {scholarship['name']}\n\n")
            f.write(f"**Organization:** {scholarship['organization']}\n")
            f.write(f"**URL:** {scholarship['url']}\n")
            f.write(f"**Amount:** {scholarship['amount']}\n")
            f.write(f"**Deadline:** {scholarship['deadline']}\n\n---\n\n")
            f.write(letter)
        return path
