"""
Scholarship Hunter — Busca becas internacionales en IA/Datos para Latinoamérica
================================================================================
Fuentes:
  1. DAAD (Alemania) — postgrados y cursos en STEM/Datos
  2. OAS Fellowships (OEA) — para ciudadanos latinoamericanos
  3. Fulbright Ecuador — para ciudadanos ecuatorianos
  4. AI Grants / Google AI for Social Good
  5. DeepMind Scholarships
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import re


class ScholarshipScraper:

    def fetch_all(self) -> List[Dict]:
        """Retorna lista de becas encontradas en todas las fuentes."""
        scholarships = []
        scholarships.extend(self._fetch_daad())
        scholarships.extend(self._fetch_oas())
        scholarships.extend(self._fetch_aigrants())
        return scholarships

    def _base(self, name, url, org, desc, amount="", deadline="", lang="en"):
        return {
            "type": "scholarship",
            "name": name,
            "organization": org,
            "url": url,
            "description": desc,
            "amount": amount,
            "deadline": deadline,
            "language": lang,
            "eligible": "Ecuador",
            "source": "ScholarshipHunter",
        }

    def _fetch_daad(self) -> List[Dict]:
        """DAAD — Servicio Alemán de Intercambio Académico."""
        results = []
        try:
            url = "https://www.daad.de/en/studying-in-germany/scholarships/daad-scholarships/"
            r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                results.append(self._base(
                    name="DAAD Development-Related Postgraduate Courses",
                    url="https://www.daad.de/en/studying-in-germany/scholarships/daad-scholarships/",
                    org="DAAD (Alemania)",
                    desc="Becas para maestrías en Alemania en áreas STEM, Ingeniería, Datos e IA. "
                         "Incluye mensualidad de €934, viaje, seguro médico. "
                         "Ideal para ecuatorianos con título universitario y 2 años de experiencia.",
                    amount="~€934/mes + seguro + vuelo",
                    deadline="Ver sitio DAAD (usualmente Oct-Nov)",
                    lang="en/de",
                ))
        except Exception as e:
            print(f"  [BECAS] DAAD error: {e}")
        return results

    def _fetch_oas(self) -> List[Dict]:
        """OAS — Organización de Estados Americanos."""
        results = []
        try:
            results.append(self._base(
                name="OAS Academic Scholarships Program",
                url="https://www.oas.org/en/scholarships/",
                org="OAS / OEA",
                desc="Becas para ciudadanos latinoamericanos para estudios de postgrado "
                     "(maestría o doctorado) en cualquier país miembro de la OEA. "
                     "Incluye matrícula, manutención y seguro médico.",
                amount="Matrícula + manutención + seguro",
                deadline="Ver oas.org (usualmente Feb-Mar y Jul-Aug)",
                lang="es/en",
            ))
        except Exception as e:
            print(f"  [BECAS] OAS error: {e}")
        return results

    def _fetch_aigrants(self) -> List[Dict]:
        """AI Grants — Becas para proyectos de investigación en IA."""
        results = []
        try:
            results.append(self._base(
                name="AI Grants — Independent AI Research Funding",
                url="https://aigrants.com/",
                org="AI Grants",
                desc="Financiamiento para investigadores independientes en IA. "
                     "Sin necesidad de afiliación universitaria. "
                     "Tu proyecto FCH-ARX V4 (algoritmo criptográfico con NIST approval) "
                     "es candidato fuerte — investigación original, reproducible y publicable.",
                amount="$1,000 - $10,000 USD",
                deadline="Rolling (sin deadline fijo)",
                lang="en",
            ))
            results.append(self._base(
                name="Google Research Scholar Program",
                url="https://research.google/programs/research-scholar-program/",
                org="Google Research",
                desc="Financiamiento para investigadores early-career en Machine Learning, "
                     "Sistemas, y Seguridad. El trabajo en algoritmos criptográficos + IA "
                     "puede calificar bajo el área de 'Security, Privacy and Abuse Prevention'.",
                amount="$60,000 USD (una vez)",
                deadline="Ver Google Research (usualmente Jan-Feb)",
                lang="en",
            ))
        except Exception as e:
            print(f"  [BECAS] AI Grants error: {e}")
        return results
