from typing import Optional
from urllib.parse import urlparse

from src.appliers.base_applier import BaseApplier
from src.appliers.multitrabajos_applier import MultitrabajosApplier

def get_applier_for_url(url: str, source: str = "") -> Optional[BaseApplier]:
    """
    Inspecciona el dominio de la URL (y opcionalmente el source) y devuelve la instancia del Applier adecuado.
    """
    try:
        domain = ""
        if url:
            domain = urlparse(url).netloc.lower()
        
        search_text = f"{domain} {source}".lower()
        
        # Enrutamiento basado en dominios/fuentes
        if any(kw in search_text for kw in ['computrabajo', 'socioempleo', 'multitrabajos', 'getonboard']):
            return MultitrabajosApplier()
            
        if 'greenhouse.io' in domain:
            from src.appliers.greenhouse_applier import GreenhouseApplier
            return GreenhouseApplier()
            
        if 'jobs.lever.co' in domain:
            from src.appliers.lever_applier import LeverApplier
            return LeverApplier()
            
    except Exception as e:
        print(f"[ROUTER ERROR] Fallo al parsear URL {url}: {e}")
        
    return None
