"""
Base Applier — Clase base para todos los módulos de auto-postulación.
Usa Playwright en modo headless con técnicas anti-detección.
"""
import asyncio
import random
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from playwright.async_api import async_playwright, Page, BrowserContext


from enum import Enum
from typing import Optional, Any

class ApplyStatus(str, Enum):
    SUBMITTED = "SUBMITTED"        # Confirmación real verificada (texto o pantalla de éxito)
    NEEDS_MANUAL = "NEEDS_MANUAL"  # Requiere intervención humana (cuestionario custom, captcha, form dinámico)
    ERROR = "ERROR"                # Fallo técnico, timeout o bloqueo

class ApplyResult:
    """Resultado auditado y no engañoso de una postulación."""
    def __init__(
        self,
        job_title: str = "",
        company: str = "",
        portal: str = "",
        url: str = "",
        status: Any = ApplyStatus.NEEDS_MANUAL,
        message: str = "",
        source: str = "",
        proof_screenshot: str = "",
        confirmation_text: str = "",
        success: Optional[bool] = None,
        **kwargs
    ):
        self.job_title = job_title
        self.company = company
        self.portal = portal
        self.url = url
        self.message = message
        self.source = source
        self.proof_screenshot = proof_screenshot
        self.confirmation_text = confirmation_text

        # Soporte backwards-compatible para 'success' o status booleano
        if success is not None:
            self.status = ApplyStatus.SUBMITTED if success else (status if isinstance(status, ApplyStatus) else ApplyStatus.NEEDS_MANUAL)
        elif isinstance(status, bool):
            self.status = ApplyStatus.SUBMITTED if status else ApplyStatus.NEEDS_MANUAL
        elif isinstance(status, ApplyStatus):
            self.status = status
        elif isinstance(status, str):
            try:
                self.status = ApplyStatus(status)
            except ValueError:
                self.status = ApplyStatus.NEEDS_MANUAL
        else:
            self.status = ApplyStatus.NEEDS_MANUAL

    @property
    def success(self) -> bool:
        """Solo es exitoso si se verificó de forma estricta la confirmación de envío."""
        return self.status == ApplyStatus.SUBMITTED

    def __repr__(self) -> str:
        return f"ApplyResult(title={self.job_title!r}, company={self.company!r}, status={self.status.value}, message={self.message!r})"


class BaseApplier(ABC):
    """
    Clase base con Playwright configurado con anti-detección.
    Todos los appliers de portales heredan de aquí.
    """

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    ]

    def __init__(self):
        self.profile_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "browser_profiles",
            self.__class__.__name__.lower()
        )
        os.makedirs(self.profile_dir, exist_ok=True)

    async def _human_delay(self, min_s: float = 1.0, max_s: float = 3.5):
        """Espera aleatoria para imitar comportamiento humano."""
        await asyncio.sleep(random.uniform(min_s, max_s))

    async def _human_type(self, page: Page, selector: str, text: str):
        """Tipea letra por letra con delays aleatorios."""
        await page.locator(selector).click()
        await page.locator(selector).fill("")
        for char in text:
            await page.keyboard.type(char)
            await asyncio.sleep(random.uniform(0.04, 0.15))

    async def _get_context(self, playwright) -> BrowserContext:
        """Crea un contexto de navegador persistente con stealth básico."""
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=self.profile_dir,
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-infobars",
                "--lang=es-EC",
            ],
            user_agent=random.choice(self.USER_AGENTS),
            locale="es-EC",
            timezone_id="America/Guayaquil",
            viewport={"width": 1280, "height": 800},
        )
        return context

    @abstractmethod
    async def apply(self, job: dict) -> ApplyResult:
        """Implementar en cada subclase para el portal específico."""
        pass

    def apply_sync(self, job: dict) -> ApplyResult:
        """Wrapper síncrono para usar desde main_v6.py."""
        return asyncio.run(self.apply(job))
