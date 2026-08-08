from playwright.sync_api import sync_playwright, Page, BrowserContext
import os
import time

class BrowserAgent:
    def __init__(self, headless=True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.browser_context: BrowserContext = None
        self.page: Page = None

    def start(self):
        self.playwright = sync_playwright().start()
        print("[BrowserAgent] Iniciando navegador en modo Headless (Bajo el agua)...")
        
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.browser_context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Inyectar cookies de sesión desde GitHub Secrets para saltar el login de LinkedIn
        li_at = os.environ.get("LINKEDIN_LI_AT")
        jsessionid = os.environ.get("LINKEDIN_JSESSIONID")
        
        if li_at and jsessionid:
            print("[BrowserAgent] Inyectando cookies de sesión desde GitHub Secrets...")
            self.browser_context.add_cookies([
                {"name": "li_at", "value": li_at, "domain": ".linkedin.com", "path": "/"},
                {"name": "JSESSIONID", "value": jsessionid, "domain": ".linkedin.com", "path": "/"}
            ])
        else:
            print("[BrowserAgent] ADVERTENCIA: No se encontraron las variables LINKEDIN_LI_AT en el entorno.")
            
        self.page = self.browser_context.new_page()
        
    def navigate(self, url: str):
        print(f"[BrowserAgent] Navegando a {url}")
        self.page.goto(url, wait_until="domcontentloaded")
        time.sleep(3)
        
    def close(self):
        if self.browser_context:
            self.browser_context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
