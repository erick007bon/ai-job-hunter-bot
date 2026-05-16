import requests
import datetime
from typing import List, Dict
from .base_scraper import BaseScraper

class RemotiveScraper(BaseScraper):
    def fetch_jobs(self) -> List[Dict]:
        url = "https://remotive.com/api/remote-jobs?category=data"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            jobs = response.json().get('jobs', [])[:15]
            
            return [{
                "title": job.get("title", ""),
                "company": job.get("company_name", ""),
                "location": job.get("candidate_required_location", ""),
                "salary": job.get("salary", ""),
                "url": job.get("url", ""),
                "source": "Remotive",
                "description": job.get("description", ""),
                "date": str(datetime.datetime.now().date())
            } for job in jobs]
        except Exception as e:
            print(f"Error en Remotive: {e}")
            return []

class RemoteOKScraper(BaseScraper):
    def fetch_jobs(self) -> List[Dict]:
        url = "https://remoteok.com/api?tag=data"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            jobs = data[1:] if len(data) > 1 else []
            jobs = jobs[:10]
            
            return [{
                "title": job.get("position", ""),
                "company": job.get("company", ""),
                "location": job.get("location", ""),
                "salary": "",
                "url": job.get("url", ""),
                "source": "RemoteOK",
                "description": job.get("description", ""),
                "date": job.get("date", "")[:10]
            } for job in jobs]
        except Exception as e:
            print(f"Error en RemoteOK: {e}")
            return []

class GetOnBoardScraper(BaseScraper):
    def fetch_jobs(self) -> List[Dict]:
        # GetOnBoard API for Data jobs (LATAM/Remote focused)
        url = "https://www.getonbrd.com/api/v0/search/jobs?query=data+python+ai&per_page=15"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json().get('data', [])
            
            parsed_jobs = []
            for item in data:
                attr = item.get('attributes', {})
                # Filtrar solo si es remoto (GetOnBoard suele indicarlo)
                if attr.get('remote', False):
                    parsed_jobs.append({
                        "title": attr.get("title", ""),
                        "company": attr.get("company", {}).get("data", {}).get("attributes", {}).get("name", "Empresa Confidencial"),
                        "location": "Remoto (GetOnBoard)",
                        "salary": f"Min: {attr.get('min_salary', '')} - Max: {attr.get('max_salary', '')}",
                        "url": attr.get("url", ""),
                        "source": "GetOnBoard",
                        "description": attr.get("description", ""),
                        "date": str(datetime.datetime.now().date())
                    })
            return parsed_jobs
        except Exception as e:
            print(f"Error en GetOnBoard: {e}")
            return []
