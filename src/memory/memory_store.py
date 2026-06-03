"""
Memoria persistente: evita postular dos veces al mismo trabajo
"""
import json
import os
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'applied_jobs.json')

class MemoryStore:
    def __init__(self):
        os.makedirs(os.path.dirname(os.path.abspath(MEMORY_FILE)), exist_ok=True)
        self.data = self._load()

    def _load(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self):
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def already_applied(self, url: str) -> bool:
        return url in self.data

    def is_applied(self, url: str) -> bool:
        """Alias de already_applied() — usado por main_v3.py"""
        return self.already_applied(url)

    def mark_applied(self, job: dict, email_sent_to: str = None, cover_letter_path: str = None):
        url = job.get('url', '')
        if url:
            entry = {
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'source': job.get('source', ''),
                'applied_at': datetime.now().isoformat(),
            }
            if email_sent_to:
                entry['email_sent_to'] = email_sent_to
            if cover_letter_path:
                entry['cover_letter_path'] = cover_letter_path
            self.data[url] = entry
            self._save()

    def get_stats(self) -> dict:
        """Estadísticas para el reporte — usado por main_v3.py"""
        total = len(self.data)
        emails_sent = sum(1 for v in self.data.values() if v.get('email_sent_to'))
        return {
            'total_postulaciones': total,
            'emails_enviados': emails_sent,
        }

    def get_all(self) -> dict:
        return self.data

    def count(self) -> int:
        return len(self.data)
