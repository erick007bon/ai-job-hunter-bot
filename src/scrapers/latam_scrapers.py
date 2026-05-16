import re
import requests
from bs4 import BeautifulSoup
import datetime
from typing import List, Dict
from .base_scraper import BaseScraper

class SocioEmpleoScraper(BaseScraper):
    """Portal oficial de empleo del gobierno de Ecuador"""
    def fetch_jobs(self) -> List[Dict]:
        # SocioEmpleo busca via el portal web (Ecuador)
        url = "https://www.socioempleo.gob.ec/servicios/buscar-vacante"
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, 'lxml')
            jobs = []
            
            # Buscar tarjetas de trabajo en la estructura de la página
            job_cards = soup.select('.vacante-card, .job-card, .vacancy-item, article')
            for card in job_cards[:10]:
                title = card.select_one('h2, h3, .title, .puesto')
                company = card.select_one('.empresa, .company, .institucion')
                location = card.select_one('.ciudad, .location, .lugar')
                link = card.select_one('a')
                
                if title:
                    jobs.append({
                        "title": title.get_text(strip=True),
                        "company": company.get_text(strip=True) if company else "No especificado",
                        "location": location.get_text(strip=True) if location else "Ecuador",
                        "salary": "",
                        "url": f"https://www.socioempleo.gob.ec{link['href']}" if link and link.get('href') else url,
                        "source": "SocioEmpleo Ecuador",
                        "description": card.get_text(strip=True)[:500],
                        "date": str(datetime.datetime.now().date())
                    })
            return jobs
        except Exception as e:
            print(f"Error en SocioEmpleo: {e}")
            return []

class ComputrabajoScraper(BaseScraper):
    """Computrabajo Ecuador - Grande en LATAM"""
    def fetch_jobs(self) -> List[Dict]:
        keywords = ["data", "python", "inteligencia artificial", "analista datos", "machine learning"]
        all_jobs = []
        
        for kw in keywords[:2]:  # Solo 2 keywords para evitar bloqueos
            url = f"https://ecuador.computrabajo.com/trabajo-de-{kw.replace(' ', '-')}"
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Estructura de Computrabajo
                cards = soup.select('article.box_offer, .offerCard, .job-offer')
                for card in cards[:8]:
                    title_el = card.select_one('h2 a, .title a, h3 a')
                    company_el = card.select_one('.fc_base, .company, .empresa')
                    location_el = card.select_one('.fc_base + span, .location, .ciudad')
                    link_el = card.select_one('a[href*="/trabajo-de"]')
                    
                    if title_el:
                        all_jobs.append({
                            "title": title_el.get_text(strip=True),
                            "company": company_el.get_text(strip=True) if company_el else "Empresa",
                            "location": location_el.get_text(strip=True) if location_el else "Ecuador",
                            "salary": "",
                            "url": f"https://ecuador.computrabajo.com{link_el['href']}" if link_el and link_el.get('href') else url,
                            "source": "Computrabajo Ecuador",
                            "description": card.get_text(strip=True)[:500],
                            "date": str(datetime.datetime.now().date())
                        })
            except Exception as e:
                print(f"Error en Computrabajo ({kw}): {e}")
        
        return all_jobs

class WeWorkRemotelyScraper(BaseScraper):
    """WeWorkRemotely via RSS - Data & Programming"""
    def fetch_jobs(self) -> List[Dict]:
        import xml.etree.ElementTree as ET
        feeds = [
            "https://weworkremotely.com/categories/remote-data-science-jobs.rss",
            "https://weworkremotely.com/categories/remote-programming-jobs.rss"
        ]
        all_jobs = []
        
        for feed_url in feeds:
            try:
                response = requests.get(feed_url, headers=self.headers, timeout=10)
                root = ET.fromstring(response.content)
                items = root.findall('.//item')
                
                for item in items[:8]:
                    title = item.findtext('title', '').replace('<![CDATA[', '').replace(']]>', '')
                    link = item.findtext('link', '')
                    description = item.findtext('description', '')
                    pub_date = item.findtext('pubDate', '')
                    
                    all_jobs.append({
                        "title": title,
                        "company": "Ver en enlace",
                        "location": "Remoto Global",
                        "salary": "",
                        "url": link,
                        "source": "WeWorkRemotely",
                        "description": description[:500],
                        "date": pub_date[:10] if pub_date else str(datetime.datetime.now().date())
                    })
            except Exception as e:
                print(f"Error en WeWorkRemotely: {e}")
        
        return all_jobs

class TorreScraper(BaseScraper):
    """Torre.ai API - Muy fuerte en LATAM"""
    def fetch_jobs(self) -> List[Dict]:
        url = "https://torre.ai/api/opportunities/_search"
        payload = {
            "and": [{"remote": True}],
            "aggregate": False,
            "size": 15,
            "meta": True,
            "query": "data python ai machine learning"
        }
        try:
            response = requests.post(url, json=payload, headers={**self.headers, 'Content-Type': 'application/json'}, timeout=10)
            data = response.json()
            results = data.get('results', [])
            
            jobs = []
            for item in results:
                opp = item.get('opportunity', item)
                jobs.append({
                    "title": opp.get("objective", ""),
                    "company": opp.get("organizations", [{}])[0].get("name", "Confidencial") if opp.get("organizations") else "Confidencial",
                    "location": "Remoto (Torre.ai)",
                    "salary": f"{opp.get('compensation', {}).get('minAmount', '')} - {opp.get('compensation', {}).get('maxAmount', '')} {opp.get('compensation', {}).get('currency', '')}".strip(),
                    "url": f"https://torre.ai/jobs/{opp.get('publicId', '')}",
                    "source": "Torre.ai",
                    "description": opp.get("details", "")[:500],
                    "date": str(datetime.datetime.now().date())
                })
            return jobs
        except Exception as e:
            print(f"Error en Torre.ai: {e}")
            return []

class WorkingNomadsScraper(BaseScraper):
    """WorkingNomads.com - Data/AI remote jobs RSS"""
    def fetch_jobs(self) -> List[Dict]:
        import xml.etree.ElementTree as ET
        url = "https://www.workingnomads.com/feed?category=data-science"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            root = ET.fromstring(response.content)
            items = root.findall('.//item')
            
            jobs = []
            for item in items[:8]:
                jobs.append({
                    "title": item.findtext('title', ''),
                    "company": item.findtext('author', 'Ver enlace'),
                    "location": "Remoto Global",
                    "salary": "",
                    "url": item.findtext('link', ''),
                    "source": "WorkingNomads",
                    "description": item.findtext('description', '')[:500],
                    "date": str(datetime.datetime.now().date())
                })
            return jobs
        except Exception as e:
            print(f"Error en WorkingNomads: {e}")
            return []
