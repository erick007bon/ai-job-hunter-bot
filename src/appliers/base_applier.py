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


@dataclass
class ApplyResult:
    """Resultado de una postulación."""
    job_title: str
    company: str
    portal: str
    url: str
    success: bool
    message: str = ""


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
