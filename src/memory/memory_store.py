import os
import json
import datetime
from typing import Dict, Optional
from src.config import Config

SENT_LOG_PATH = os.path.join(Config.DATA_DIR, "sent_log.json")

class MemoryStore:
    """Memoria persistente del bot: evita postular dos veces a la misma oferta"""
    
    def __init__(self):
        self.log = self._load()
    
    def _load(self) -> dict:
        if os.path.exists(SENT_LOG_PATH):
            with open(SENT_LOG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"applications": []}
    
    def _save(self):
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        with open(SENT_LOG_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.log, f, ensure_ascii=False, indent=2)
    
    def is_applied(self, job_url: str) -> bool:
        """Verifica si ya se postuló a esta oferta"""
        applied_urls = [app['url'] for app in self.log.get('applications', [])]
        return job_url in applied_urls
    
    def mark_applied(self, job: Dict, email_sent_to: Optional[str] = None, cover_letter_path: Optional[str] = None):
        """Registra una postulación"""
        entry = {
            "date": str(datetime.datetime.now()),
            "url": job.get('url', ''),
            "title": job.get('title', ''),
            "company": job.get('company', ''),
            "source": job.get('source', ''),
            "email_sent_to": email_sent_to,
            "cover_letter_path": cover_letter_path,
            "status": "sent" if email_sent_to else "draft"
        }
        self.log['applications'].append(entry)
        self._save()
        print(f"  [MEMORIA] Registrado: {job.get('title')} @ {job.get('company')}")

    def get_stats(self) -> dict:
        apps = self.log.get('applications', [])
        sent = [a for a in apps if a.get('status') == 'sent']
        return {
            "total_postulaciones": len(apps),
            "emails_enviados": len(sent),
            "solo_drafts": len(apps) - len(sent)
        }
