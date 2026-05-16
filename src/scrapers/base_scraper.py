from abc import ABC, abstractmethod
from typing import List, Dict

class BaseScraper(ABC):
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    
    @abstractmethod
    def fetch_jobs(self) -> List[Dict]:
        """
        Debe retornar una lista de diccionarios con el formato:
        {
            "title": str,
            "company": str,
            "location": str,
            "salary": str,
            "url": str,
            "source": str,
            "description": str,
            "date": str
        }
        """
        pass
