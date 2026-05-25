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

    def mark_applied(self, job: dict):
        url = job.get('url', '')
        if url:
            self.data[url] = {
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'applied_at': datetime.now().isoformat(),
            }
            self._save()

    def get_all(self) -> dict:
        return self.data

    def count(self) -> int:
        return len(self.data)
