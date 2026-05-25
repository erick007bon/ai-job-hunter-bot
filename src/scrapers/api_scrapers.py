"""
Scrapers para APIs públicas de empleo: Remotive y RemoteOK
"""
import requests

HEADERS = {'User-Agent': 'Mozilla/5.0 (JobHunterBot/5.0)'}

class RemotiveScraper:
    def fetch_jobs(self):
        try:
            r = requests.get("https://remotive.com/api/remote-jobs?category=data", headers=HEADERS, timeout=12)
            r.raise_for_status()
            jobs = r.json().get('jobs', [])[:20]
            return [self._normalize(j) for j in jobs]
        except Exception as e:
            print(f"[Remotive] Error: {e}")
            return []

    def _normalize(self, j):
        return {
            'title': j.get('title', ''),
            'company': j.get('company_name', ''),
            'url': j.get('url', ''),
            'description': j.get('description', '')[:800],
            'salary': j.get('salary', 'N/A'),
            'source': 'Remotive',
            'location': j.get('candidate_required_location', 'Remote'),
            'tags': j.get('tags', []),
        }

class RemoteOKScraper:
    def fetch_jobs(self):
        tags = ['python', 'data', 'ai', 'machine-learning', 'economist']
        jobs = []
        for tag in tags:
            try:
                r = requests.get(f"https://remoteok.com/api?tag={tag}", headers=HEADERS, timeout=12)
                r.raise_for_status()
                data = r.json()
                items = data[1:] if len(data) > 1 else []
                for j in items[:5]:
                    jobs.append(self._normalize(j))
            except Exception as e:
                print(f"[RemoteOK:{tag}] Error: {e}")
        return jobs

    def _normalize(self, j):
        return {
            'title': j.get('position', ''),
            'company': j.get('company', ''),
            'url': j.get('url', f"https://remoteok.com/remote-jobs/{j.get('id','')}"),
            'description': j.get('description', '')[:800],
            'salary': f"{j.get('salary_min','?')} - {j.get('salary_max','?')}",
            'source': 'RemoteOK',
            'location': 'Remote',
            'tags': j.get('tags', []),
        }

class GetOnBoardScraper:
    def fetch_jobs(self):
        try:
            r = requests.get(
                "https://www.getonbrd.com/api/v0/jobs?per_page=20&page=1",
                headers=HEADERS, timeout=12
            )
            r.raise_for_status()
            jobs = r.json().get('data', [])
            return [self._normalize(j) for j in jobs[:10]]
        except Exception as e:
            print(f"[GetOnBoard] Error: {e}")
            return []

    def _normalize(self, j):
        attrs = j.get('attributes', {})
        return {
            'title': attrs.get('title', ''),
            'company': attrs.get('company', {}).get('name', '') if isinstance(attrs.get('company'), dict) else '',
            'url': attrs.get('url', ''),
            'description': attrs.get('description', '')[:800],
            'salary': f"{attrs.get('min_salary','?')} - {attrs.get('max_salary','?')}",
            'source': 'GetOnBoard',
            'location': 'Ecuador/LATAM',
            'tags': [],
        }
