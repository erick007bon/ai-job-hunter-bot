"""
Google Jobs Scraper — Via python-jobspy
Busca vacantes en Google Jobs, Indeed y Glassdoor sin API key
"""
import sys
import os

# Agregar el directorio raiz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from jobspy import scrape_jobs
    JOBSPY_AVAILABLE = True
except (ImportError, Exception):
    JOBSPY_AVAILABLE = False
    scrape_jobs = None

from src.scrapers.base_scraper import BaseScraper


class GoogleJobsScraper(BaseScraper):
    """
    Scraper de Google Jobs usando python-jobspy.
    Tambien captura Indeed y Glassdoor en el mismo ciclo.
    """

    SEARCH_QUERIES = [
        "Data Scientist remote",
        "Data Engineer remote",
        "Machine Learning Engineer remote",
        "AI Engineer remote",
        "Python Developer remote",
        "Business Intelligence Analyst remote",
        "Economista datos remoto",
    ]

    def fetch_jobs(self) -> list:
        if not JOBSPY_AVAILABLE:
            print("  [GOOGLE JOBS] jobspy no instalado. Saltando.")
            return []

        all_jobs = []
        seen_urls = set()

        for query in self.SEARCH_QUERIES[:4]:  # Max 4 queries por ciclo
            try:
                print(f"  [GOOGLE JOBS] Buscando: '{query}'...")
                df = scrape_jobs(
                    site_name=["google", "indeed"],
                    search_term=query,
                    results_wanted=15,
                    hours_old=72,
                    is_remote=True,
                    job_type="fulltime",
                )

                if df is None or df.empty:
                    print(f"  [GOOGLE JOBS] Sin resultados para '{query}'")
                    continue

                for _, row in df.iterrows():
                    job_url = str(row.get("job_url", "") or "")
                    if not job_url or job_url in seen_urls:
                        continue
                    seen_urls.add(job_url)

                    title = str(row.get("title", "") or "")
                    company = str(row.get("company", "") or "")
                    description = str(row.get("description", "") or "")[:2000]
                    location = str(row.get("location", "") or "")
                    site = str(row.get("site", "") or "Google Jobs")

                    if not title or not company:
                        continue

                    # Detectar idioma del puesto para seleccionar CV correcto
                    es_keywords = ["datos", "economista", "analista", "remoto"]
                    lang = "es" if any(k in title.lower() for k in es_keywords) else "en"

                    all_jobs.append({
                        "title": title,
                        "company": company,
                        "location": location or "Remote",
                        "url": job_url,
                        "description": description,
                        "source": f"Google Jobs ({site.capitalize()})",
                        "lang": lang,
                        "salary": str(row.get("min_amount", "") or ""),
                    })

                print(f"  [GOOGLE JOBS] {len(df)} encontrados para '{query}'")

            except Exception as e:
                print(f"  [GOOGLE JOBS] Error con '{query}': {e}")
                continue

        print(f"  [GOOGLE JOBS] Total unico: {len(all_jobs)} vacantes")
        return all_jobs
