"""
router.py — Detecta el ATS de una URL de oferta y retorna el Applier correcto.

Estrategia (en orden):
1. Dominios directos conocidos (Greenhouse, Lever, Workable, etc.)
2. ATSs detectados por dominio en la URL
3. Job boards → seguir redirect HTTP para descubrir el ATS final
4. Retorna None → main_v6 intentará cold-email
"""
from typing import Optional
from urllib.parse import urlparse
import re
import requests


def _follow_redirect(url: str, timeout: int = 8) -> str:
    """
    Sigue redirects HTTP y retorna la URL final.
    Útil para job boards (Remotive, RemoteOK) cuyas URLs
    apuntan directamente al ATS de la empresa.
    """
    try:
        resp = requests.head(
            url,
            allow_redirects=True,
            timeout=timeout,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            }
        )
        final_url = resp.url
        if final_url and final_url != url:
            print(f"[ROUTER] Redirect detectado: {url} → {final_url}")
        return final_url
    except Exception as e:
        print(f"[ROUTER] No se pudo seguir redirect de {url}: {e}")
        return url


def _get_applier_by_domain(domain: str, url: str) -> Optional["BaseApplier"]:
    """
    Retorna un applier basado en el dominio ya analizado.
    Separado para reutilizarlo tanto con la URL original como con la URL final tras redirect.
    """
    from src.appliers.base_applier import BaseApplier

    # Greenhouse
    if 'greenhouse.io' in domain:
        from src.appliers.greenhouse_applier import GreenhouseApplier
        return GreenhouseApplier()

    # Lever
    if 'lever.co' in domain:
        from src.appliers.lever_applier import LeverApplier
        return LeverApplier()

    # Workable
    if 'workable.com' in domain:
        from src.appliers.workable_applier import WorkableApplier
        return WorkableApplier()

    # Ashby
    if 'ashbyhq.com' in domain:
        from src.appliers.ashby_applier import AshbyApplier
        return AshbyApplier()

    # SmartRecruiters
    if 'smartrecruiters.com' in domain:
        from src.appliers.smartrecruiters_applier import SmartRecruitersApplier
        return SmartRecruitersApplier()

    # iCIMS
    if 'icims.com' in domain:
        from src.appliers.icims_applier import ICIMSApplier
        return ICIMSApplier()

    # BambooHR
    if 'bamboohr.com' in domain:
        from src.appliers.bamboohr_applier import BambooHRApplier
        return BambooHRApplier()

    # Jobvite
    if 'jobvite.com' in domain:
        from src.appliers.jobvite_applier import JobviteApplier
        return JobviteApplier()

    # Multitrabajos (Ecuador)
    if 'multitrabajos' in domain:
        from src.appliers.multitrabajos_applier import MultitrabajosApplier
        return MultitrabajosApplier()

    # LinkedIn: NO se puede hacer Easy Apply desde servidor headless (anti-bot)
    # El main_v6 maneja las ofertas de LinkedIn con notificación Telegram directa
    if 'linkedin.com' in domain:
        return None

    return None


# Dominios que son "job boards" (no el ATS final)
# Para estos, intentamos seguir el redirect para llegar al ATS real
JOB_BOARD_DOMAINS = {
    'remotive.com', 'remoteok.com', 'remoteok.io',
    'weworkremotely.com', 'getonbrd.com', 'torre.ai',
    'workingnomads.com', 'workingnomads.co',
    'jobicy.com', 'wellfound.com', 'angel.co',
    'linkedin.com', 'indeed.com', 'glassdoor.com',
    'stackoverflow.com', 'github.com',
    'socioempleo.gob.ec', 'computrabajo.com',
}


def get_applier_for_url(url: str, source: str = "") -> Optional["BaseApplier"]:
    """
    Inspecciona la URL y retorna el Applier ATS correcto.
    Si la URL es de un job board, sigue el redirect para detectar el ATS real.
    Retorna None si no hay applier disponible (→ main_v6 intentará cold-email).
    """
    if not url:
        return None

    try:
        domain = re.sub(r'^www\.', '', urlparse(url).netloc.lower())

        # 1. Intentar con la URL/dominio original
        applier = _get_applier_by_domain(domain, url)
        if applier:
            print(f"[ROUTER] ATS detectado directamente: {applier.__class__.__name__} ({domain})")
            return applier

        # 2. Si es un job board, seguir redirect para llegar al ATS real
        is_job_board = any(board in domain for board in JOB_BOARD_DOMAINS)
        if is_job_board:
            final_url = _follow_redirect(url)
            if final_url and final_url != url:
                final_domain = re.sub(r'^www\.', '', urlparse(final_url).netloc.lower())
                applier = _get_applier_by_domain(final_domain, final_url)
                if applier:
                    print(f"[ROUTER] ATS detectado tras redirect: {applier.__class__.__name__} ({final_domain})")
                    return applier

            print(f"[ROUTER] Job board sin ATS detectable ({domain}) → cold-email")

            return None

        # 3. URL desconocida — sin applier
        print(f"[ROUTER] Dominio desconocido ({domain}) → cold-email")
        return None

    except Exception as e:
        print(f"[ROUTER ERROR] Fallo al parsear URL {url}: {e}")
        return None


def detect_ats_from_url(url: str) -> Optional[str]:
    """
    Detecta qué ATS usa una URL (útil para logging/debugging).
    Retorna el nombre del ATS o None.
    """
    if not url:
        return None

    url_lower = url.lower()

    ats_domains = {
        'Greenhouse': ['greenhouse.io', 'boards.greenhouse.io'],
        'Lever': ['jobs.lever.co', 'lever.co'],
        'Workable': ['workable.com', 'apply.workable.com'],
        'Ashby': ['ashbyhq.com', 'jobs.ashbyhq.com'],
        'SmartRecruiters': ['smartrecruiters.com', 'careers.smartrecruiters.com'],
        'ICIMS': ['icims.com', 'careers.icims.com'],
        'BambooHR': ['bamboohr.com', 'careers.bamboohr.com'],
        'Jobvite': ['jobvite.com', 'jobs.jobvite.com'],
        'Workday': ['workday.com', 'myworkdayjobs.com'],
        'SAP SuccessFactors': ['successfactors.com', 'sapsf.com'],
        'Oracle Taleo': ['taleo.net', 'oraclecloud.com'],
        'Multitrabajos': ['multitrabajos.com'],
    }

    for ats, domains in ats_domains.items():
        if any(d in url_lower for d in domains):
            return ats

    return None