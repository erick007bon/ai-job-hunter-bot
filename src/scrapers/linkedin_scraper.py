"""
linkedin_scraper.py — Scraper de empleos usando linkedin-api.

Reemplaza el scraping HTML anterior (que era frágil) con llamadas
directas a la API interna de LinkedIn via linkedin-api.
"""
import logging
from typing import List, Dict

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

# Búsquedas de empleos — keywords × locations
JOB_SEARCHES = [
    {"keywords": "Data Scientist",        "location": "Remote"},
    {"keywords": "AI Engineer",           "location": "Remote"},
    {"keywords": "Machine Learning Engineer", "location": "Remote"},
    {"keywords": "Data Engineer",         "location": "Remote"},
    {"keywords": "Data Analyst",          "location": "Remote"},
]


class LinkedInScraper(BaseScraper):
    """
    Scraper de empleos de LinkedIn usando linkedin-api.
    Retorna empleos normalizados compatibles con el pipeline.
    """

    def __init__(self):
        super().__init__()
        self.source_name = "LinkedIn"

    def fetch_jobs(self) -> List[Dict]:
        try:
            from src.linkedin.linkedin_client import LinkedInClient
            client = LinkedInClient()
        except RuntimeError as e:
            # Si no hay credenciales, advertir y retornar vacío
            logger.warning(f"[LinkedInScraper] {e}")
            print(f"  [LinkedIn] ⚠️ {e}")
            return []

        jobs = []
        seen_ids = set()

        for search in JOB_SEARCHES:
            keywords = search["keywords"]
            location = search["location"]
            try:
                results = client.search_jobs(
                    keywords=keywords,
                    location=location,
                    limit=10,               # 10 por keyword × 5 searches = 50 max
                )
                new = 0
                for job in results:
                    job_id = job.get("job_id", "")
                    if job_id and job_id not in seen_ids:
                        seen_ids.add(job_id)
                        jobs.append(job)
                        new += 1

                print(f"  [LinkedIn:{keywords}] {new} empleos")

            except Exception as e:
                logger.warning(f"[LinkedInScraper] Error en '{keywords}': {e}")

        return jobs
