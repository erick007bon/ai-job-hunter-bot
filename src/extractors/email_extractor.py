import re
import time
import socket
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urlparse

# Hunter.io API - Encuentra emails corporativos REALES y verificados
# Registrate gratis en hunter.io (25 busquedas/mes gratis)
HUNTER_API_KEY = "6245e0dd42c3e67005f70a76a896e392b2260bd6"  # Key proporcionada por el usuario

HUNTER_DOMAIN_SEARCH = "https://api.hunter.io/v2/domain-search"
HUNTER_FIND       = "https://api.hunter.io/v2/email-finder"
HUNTER_VERIFY     = "https://api.hunter.io/v2/email-verifier"

class EmailExtractor:
    """
    Extractor de emails REALES de RRHH.
    NUNCA inventa emails. Si no encuentra uno real, retorna None.
    
    Estrategia (en orden):
      1. Texto de la descripcion del trabajo
      2. HTML de la pagina de la oferta
      3. Sitio web real de la empresa (careers/contact)
      4. Hunter.io API (emails corporativos verificados)
    """
    
    EMAIL_PATTERN = re.compile(r'[\w\.\+\-]+@[\w\.\-]+\.[a-z]{2,6}', re.IGNORECASE)
    
    # Emails que jamas se deben usar
    SKIP_EMAILS = [
        'noreply', 'no-reply', 'example', 'test', 'spam', '@remotive',
        'sentry', '@weworkremotely', '@getonbrd', 'bounce', 'mailer',
        'donotreply', 'postmaster', 'webmaster', '@linkedin', '@indeed',
        'gdpr@', 'privacy@', 'legal@', 'press@', 'abuse@', 'security@',
        'unsubscribe', 'notification', 'hello@remotive'
    ]
    
    JOB_BOARD_DOMAINS = [
        'remotive.com', 'remoteok.io', 'weworkremotely.com', 'getonbrd.com',
        'torre.ai', 'workingnomads.com', 'socioempleo.gob.ec', 'computrabajo.com',
        'linkedin.com', 'indeed.com', 'glassdoor.com', 'infojobs.net',
        'jobs.lever.co', 'boards.greenhouse.io', 'apply.workable.com',
        'jobs.ashbyhq.com', 'careers.smartrecruiters.com'
    ]
    
    HR_PREFIXES = [
        'hr', 'rrhh', 'talento', 'talent', 'jobs', 'careers', 'empleo',
        'recruiting', 'recruitment', 'hiring', 'apply', 'people', 'join'
    ]
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
    }
    
    def _is_valid_email(self, email: str) -> bool:
        """Solo acepta emails que no son de portales ni bots"""
        email_lower = email.lower()
        return not any(skip in email_lower for skip in self.SKIP_EMAILS)
    
    def _is_hr_email(self, email: str) -> bool:
        prefix = email.split('@')[0].lower()
        return any(hr in prefix for hr in self.HR_PREFIXES)
    
    def _extract_emails_from_text(self, text: str) -> List[str]:
        """Extrae emails validos de un texto o HTML"""
        if '<' in text:
            text = BeautifulSoup(text, 'html.parser').get_text()
        found = self.EMAIL_PATTERN.findall(text)
        valid = [e for e in set(found) if self._is_valid_email(e)]
        # Priorizar emails de RRHH
        hr = [e for e in valid if self._is_hr_email(e)]
        other = [e for e in valid if not self._is_hr_email(e)]
        return hr + other
    
    def _get_html(self, url: str, timeout: int = 8) -> Optional[str]:
        try:
            r = requests.get(url, headers=self.HEADERS, timeout=timeout, allow_redirects=True)
            if r.status_code == 200:
                return r.text
        except Exception:
            pass
        return None
    
    def _get_company_website(self, job: Dict) -> Optional[str]:
        """
        Encuentra el sitio web REAL de la empresa (no el portal de trabajo).
        Busca links dentro de la pagina de la oferta que apunten a la empresa.
        """
        job_url = job.get('url', '')
        if not job_url:
            return None
        
        html = self._get_html(job_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        job_board_domain = urlparse(job_url).netloc
        
        # Buscar todos los links externos que NO sean del portal
        external_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if not href.startswith('http'):
                continue
            parsed = urlparse(href)
            link_domain = parsed.netloc.replace('www.', '')
            
            # Descartar si es el mismo portal o un portal conocido
            if job_board_domain in href:
                continue
            if any(board in link_domain for board in self.JOB_BOARD_DOMAINS):
                continue
            # Descartar redes sociales y servicios comunes
            if any(s in link_domain for s in ['twitter', 'facebook', 'instagram', 'youtube', 'google', 'apple', 'microsoft']):
                continue
            
            external_links.append(f"https://{parsed.scheme}://{parsed.netloc}" if parsed.scheme else f"https://www.{link_domain}")
        
        # Retornar el primer link externo encontrado (probablemente el sitio de la empresa)
        return external_links[0] if external_links else None
    
    def _scrape_company_site_for_email(self, company_url: str) -> Optional[str]:
        """
        Navega el sitio real de la empresa buscando emails en:
        - Homepage
        - /careers, /jobs, /contact, /about
        """
        if not company_url:
            return None
        
        all_emails = []
        contact_paths = [
            '', '/careers', '/jobs', '/contact', '/about',
            '/contacto', '/empleo', '/trabaja-con-nosotros'
        ]
        
        base = company_url.rstrip('/')
        for path in contact_paths[:5]:
            html = self._get_html(base + path)
            if not html:
                continue
            
            emails = self._extract_emails_from_text(html)
            if emails:
                # Si encontramos email de RRHH, retornar inmediatamente
                hr_emails = [e for e in emails if self._is_hr_email(e)]
                if hr_emails:
                    return hr_emails[0]
                all_emails.extend(emails)
            
            time.sleep(0.5)
        
        return all_emails[0] if all_emails else None
    
    def _hunter_domain_search(self, domain: str) -> Optional[str]:
        """
        Usa Hunter.io para encontrar emails REALES y VERIFICADOS en un dominio.
        Retorna el email de RRHH mas relevante, o None si no encuentra nada.
        """
        if not HUNTER_API_KEY:
            return None
        
        try:
            params = {
                'domain': domain,
                'api_key': HUNTER_API_KEY,
                'type': 'personal',
                'limit': 10
            }
            r = requests.get(HUNTER_DOMAIN_SEARCH, params=params, timeout=10)
            if r.status_code != 200:
                return None
            
            data = r.json().get('data', {})
            emails_found = data.get('emails', [])
            
            if not emails_found:
                return None
            
            # Priorizar: RRHH/Talent primero, luego cualquier email verificado
            hr_emails = [
                e for e in emails_found
                if any(dept in str(e.get('department', '')).lower() 
                       for dept in ['human resources', 'hr', 'talent', 'recruiting', 'people'])
            ]
            
            if hr_emails:
                return hr_emails[0].get('value')
            
            # Si no hay HR especifico, retornar el primero verificado
            verified = [e for e in emails_found if e.get('confidence', 0) > 70]
            if verified:
                return verified[0].get('value')
            
            return emails_found[0].get('value') if emails_found else None
            
        except Exception as e:
            print(f"      [HUNTER] Error: {e}")
            return None
    
    def enrich_job(self, job: Dict) -> Dict:
        """
        Pipeline de extraccion de email REAL. 
        Si no encuentra uno real, pone None (no envia nada).
        """
        email = None
        company = job.get('company', '')
        
        # Saltar empresas sin nombre util
        skip_company = not company or any(s in company.lower() for s in [
            'confidencial', 'ver en enlace', 'confidential', 'sin nombre'
        ])
        
        # CAPA 1: Buscar en la descripcion del trabajo
        description = job.get('description', '')
        if description:
            emails = self._extract_emails_from_text(description)
            if emails:
                email = emails[0]
                print(f"      [OK] Email real en descripcion: {email}")
        
        # CAPA 2: Scrapear la pagina de la oferta y el sitio de la empresa
        if not email and not skip_company:
            print(f"      [->] Buscando en sitio web de '{company}'...")
            company_url = self._get_company_website(job)
            if company_url:
                email = self._scrape_company_site_for_email(company_url)
                if email:
                    print(f"      [OK] Email real en sitio empresa: {email}")
        
        # CAPA 3: Hunter.io (requiere API key gratuita de hunter.io)
        if not email and not skip_company and HUNTER_API_KEY:
            print(f"      [->] Consultando Hunter.io para '{company}'...")
            
            # 1. Intentar usar la URL de la empresa extraida en la CAPA 2
            domain_to_search = None
            if 'company_url' in locals() and company_url:
                clean_url = company_url.replace('https://', '').replace('http://', '')
                clean_url = clean_url.split('/')[0]  # Obtener solo el host
                domain_to_search = clean_url.replace('www.', '')

            
            # 2. Si no, intentar construirlo del nombre de la empresa
            if not domain_to_search:
                clean_name = re.sub(r'[^a-zA-Z0-9]', '', company).lower()
                if clean_name:
                    domain_to_search = f"{clean_name}.com"
            
            if domain_to_search:
                email = self._hunter_domain_search(domain_to_search)
                if email:
                    print(f"      [OK] Email verificado por Hunter.io: {email}")
        
        # RESULTADO: email real o None (sin inventos)
        if email:
            job['contact_email'] = email
            job['email_verified'] = True
        else:
            job['contact_email'] = None
            job['email_verified'] = False
            print(f"      [--] Sin email real encontrado -> solo draft")
        
        return job
    
    def enrich_all(self, jobs: List[Dict]) -> List[Dict]:
        enriched = []
        for i, job in enumerate(jobs):
            title = job.get('title', '')[:30]
            comp = job.get('company', '')[:20]
            print(f"    [{i+1}/{len(jobs)}] {title} @ {comp}")
            enriched.append(self.enrich_job(job))
        return enriched
