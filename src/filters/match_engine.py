import re
from typing import List, Dict
from src.config import Config

# Roles objetivo: SOLO estos tipos de trabajos (ES y EN)
WHITELIST_ROLES = [
    # Inteligencia Artificial / Machine Learning
    "aprendizaje automático", "machine learning", "ml engineer", "ml developer",
    "inteligencia artificial", "ai engineer", "ai developer", "ai specialist",
    "deep learning", "nlp", "llm", "prompt engineer", "computer vision",
    "product builder", "generative ai",

    # Datos / Analytics / BI
    "data scientist", "científico de datos", "científica de datos", "ciencia de datos",
    "data engineer", "ingeniero de datos", "ingeniería de datos",
    "data analyst", "analista de datos", "analista", "analytics", "analytics engineer",
    "research analyst", "research scientist", "applied scientist",
    "business intelligence", "bi developer", "analista bi", "power bi",
    "data architect", "arquitecto de datos", "data infrastructure", "data entry",
    "feature engineer", "mlops", "ml ops",

    # Programación / Herramientas / Economía
    "python", "sql", "excel", "expert", "software engineer",
    "econometrist", "economist", "economista", "econometría", "quantitative", "quant",
]

# Roles que NUNCA debemos postular (off-topic absoluto)
BLACKLIST_ROLES = [
    "office assistant", "copywriter", "ios developer", "android developer",
    "customer support", "customer service", "sales representative", "asesor de viajes",
    "marketing manager", "content writer", "freelance writer", "copyeditor",
    "graphic designer", "ux designer", "ui designer", "social media",
    "account manager", "devops intern", "customer retention",
    "java developer", "ruby developer", "php developer", "frontend developer",
    "react developer", "angular developer", "vue developer",
    "video editor", "motion designer", "recruiter", "hr manager",
]

class MatchEngine:
    def __init__(self):
        self.senior_keywords = [
            "senior", "lead", "staff", "principal",
            "10+ years", "8+ years", "7+ years",
            "sr.", "sr ", "head of", "director of", "vp of"
        ]
        self.english_reject_keywords = [
            "native english", "c1", "c2",
            "fluent in english is mandatory", "english native speaker"
        ]

    def _is_senior(self, title: str) -> bool:
        title = title.lower()
        return any(keyword in title for keyword in self.senior_keywords)

    def _demands_high_english(self, text: str) -> bool:
        text = text.lower()
        return any(keyword in text for keyword in self.english_reject_keywords)

    def _is_relevant_role(self, title: str) -> bool:
        """Verifica que el titulo sea un rol de IA/Datos/ML — lista blanca explícita en ES y EN."""
        title_lower = title.lower()
        # Primero verificar blacklist (rechazo absoluto)
        for bad in BLACKLIST_ROLES:
            if bad in title_lower:
                return False

        # Para siglas cortas independientes (ia, ai, bi, ml), usar límites de palabra
        short_acronyms = {"ia", "ai", "bi", "ml"}
        words = set(re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]+\b', title_lower))
        if any(acronym in words for acronym in short_acronyms):
            return True

        # Luego verificar whitelist
        for good in WHITELIST_ROLES:
            if good in title_lower:
                return True
        return False

    def filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
        matched_jobs = []
        rejected_counts = {"senior": 0, "irrelevant_role": 0, "english": 0, "passed": 0}

        for job in jobs:
            title = job.get('title', '')
            title_desc = (title + " " + job.get('description', '')).lower()

            # 1. Filtro de relevancia del rol (el más importante — evita Office Assistant etc.)
            if not self._is_relevant_role(title):
                rejected_counts["irrelevant_role"] += 1
                continue

            # 2. Filtro Seniority (Rechazar si es Senior en el título)
            if self._is_senior(title):
                rejected_counts["senior"] += 1
                continue

            # 3. Filtro Inglés (Rechazar si exige Nativo o C1/C2)
            if Config.ENGLISH_LEVEL == "B2" and self._demands_high_english(title_desc):
                rejected_counts["english"] += 1
                continue

            rejected_counts["passed"] += 1
            matched_jobs.append(job)

        print(f"  [FILTRO] Pasaron: {rejected_counts['passed']} | "
              f"Rol irrelevante: {rejected_counts['irrelevant_role']} | "
              f"Senior: {rejected_counts['senior']} | "
              f"Inglés alto: {rejected_counts['english']}")

        return matched_jobs
