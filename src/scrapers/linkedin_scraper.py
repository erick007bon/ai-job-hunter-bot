import requests
import json
import datetime
from typing import List, Dict
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from src.config import Config

class LinkedInScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.source_name = "LinkedIn"
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/vnd.linkedin.normalized+json+2.1',
            'csrf-token': Config.LINKEDIN_JSESSIONID.strip('"')
        }
        
        self.cookies = {
            'li_at': Config.LINKEDIN_LI_AT,
            'JSESSIONID': Config.LINKEDIN_JSESSIONID
        }

    def fetch_jobs(self) -> List[Dict]:
        jobs = []
        try:
            # Buscar roles tech/data usando la API de búsqueda abierta de LinkedIn (protegida por cookies de sesión)
            keywords = ["Data Scientist", "AI Engineer", "Machine Learning"]
            
            for keyword in keywords:
                # Filtrar remotas y publicadas recientemente
                url = f"https://www.linkedin.com/jobs/search?keywords={keyword}&location=Remote&f_TPR=r86400"
                # Usamos headers publicos sin cookies para que LinkedIn devuelva el HTML facil de parsear (no el SPA de React)
                public_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
                r = requests.get(url, headers=public_headers, timeout=15)
                r.raise_for_status()
                
                soup = BeautifulSoup(r.text, 'html.parser')
                job_cards = soup.find_all('div', class_='base-card')
                
                for card in job_cards[:10]:  # Max 10 por keyword para evitar ban
                    title_elem = card.find('h3', class_='base-search-card__title')
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    location_elem = card.find('span', class_='job-search-card__location')
                    link_elem = card.find('a', class_='base-card__full-link')
                    
                    if not title_elem or not link_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                    location = location_elem.get_text(strip=True) if location_elem else "Remote"
                    job_url = link_elem.get('href', '').split('?')[0]  # Limpiar UTM params
                    
                    # Extraer ID del trabajo desde la URL
                    job_id = ""
                    if "view/" in job_url:
                        job_id = job_url.split("view/")[-1].replace("/", "")
                    elif "currentJobId=" in job_url:
                        job_id = job_url.split("currentJobId=")[-1].split("&")[0]
                        
                    if job_id:
                        job_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
                        
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "salary": "",
                        "url": job_url,
                        "source": self.source_name,
                        "description": "",  # Se llena luego con fetch_job_description
                        "date": str(datetime.datetime.now().date())
                    })
                    
        except Exception as e:
            print(f"Error en {self.source_name}: {e}")
            
        return jobs

    def fetch_job_description(self, job_id: str) -> str:
        # Extraer detalle completo del trabajo usando la web publica o la API
        try:
            # Asegurar que solo tenemos el ID numerico
            if '-' in job_id:
                job_id = job_id.split('-')[-1]
            if '?' in job_id:
                job_id = job_id.split('?')[0]
                
            url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                desc = soup.find('div', class_='description__text')
                if desc:
                    return desc.get_text(separator=' ')
                
                # Intentar tambien sacar el nombre de la empresa real
                company_tag = soup.find('a', class_='topcard__org-name-link')
                if company_tag:
                    return f"__COMPANY__:{company_tag.get_text(strip=True)}\n{soup.get_text()}"
        except:
            pass
        return ""
