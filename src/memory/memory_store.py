"""
Memoria persistente: evita postular dos veces al mismo trabajo
"""
import json
import os
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'applied_jobs.json')
SENT_LOG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sent_log.json')

class MemoryStore:
    def __init__(self):
        os.makedirs(os.path.dirname(os.path.abspath(MEMORY_FILE)), exist_ok=True)
        self.data = self._load()
        self.sent_log = self._load_sent_log()

    def _load(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _load_sent_log(self):
        if os.path.exists(SENT_LOG_FILE):
            try:
                with open(SENT_LOG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {'applications': []}
        return {'applications': []}

    def _save(self):
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def _save_sent_log(self):
        with open(SENT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.sent_log, f, indent=2, ensure_ascii=False)

    def already_applied(self, url: str) -> bool:
        """Alias de is_applied para compatibilidad."""
        return url in self.data

    def is_applied(self, url: str) -> bool:
        """Verifica si ya se postuló a esta URL."""
        return url in self.data

    def mark_applied(self, job: dict, email_sent_to: str = None, cover_letter_path: str = None):
        """Registra una postulación en la memoria."""
        url = job.get('url', '')
        if url:
            entry = {
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'source': job.get('source', ''),
                'applied_at': datetime.now().isoformat(),
                'email_sent_to': email_sent_to,
                'cover_letter_path': cover_letter_path,
            }
            self.data[url] = entry
            self._save()

            # Actualizar sent_log para commit del bot
            if email_sent_to:
                self.sent_log.setdefault('applications', []).append({
                    'url': url,
                    'email': email_sent_to,
                    'date': datetime.now().isoformat()
                })
                self._save_sent_log()

    def get_all(self) -> dict:
        return self.data

    def count(self) -> int:
        return len(self.data)

    def get_stats(self) -> dict:
        """Devuelve estadísticas totales de postulaciones."""
        total = len(self.data)
        emails_enviados = sum(
            1 for v in self.data.values()
            if isinstance(v, dict) and v.get('email_sent_to')
        )
        return {
            'total_postulaciones': total,
            'emails_enviados': emails_enviados,
        }

