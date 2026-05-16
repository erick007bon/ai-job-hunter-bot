import re
from typing import List, Dict
from src.config import Config

class MatchEngine:
    def __init__(self):
        self.senior_keywords = ["senior", "lead", "staff", "principal", "10+ years", "sr.", "sr ", "head"]
        self.english_reject_keywords = ["native english", "c1", "c2", "fluent in english is mandatory"]
        
    def _is_senior(self, text: str) -> bool:
        text = text.lower()
        return any(keyword in text for keyword in self.senior_keywords)
        
    def _demands_high_english(self, text: str) -> bool:
        text = text.lower()
        return any(keyword in text for keyword in self.english_reject_keywords)

    def filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
        matched_jobs = []
        for job in jobs:
            title_desc = (job['title'] + " " + job.get('description', '')).lower()
            
            # 1. Filtro Seniority (Rechazar si es Senior)
            if self._is_senior(job['title']):
                continue
                
            # 2. Filtro Inglés (Rechazar si exige Nativo o C1/C2 y no somos de ese nivel)
            if Config.ENGLISH_LEVEL == "B2" and self._demands_high_english(title_desc):
                continue
                
            matched_jobs.append(job)
            
        return matched_jobs
