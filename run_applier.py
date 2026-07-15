import time
import os
from src.auto_applier.browser_agent import BrowserAgent
from src.auto_applier.form_filler import FormFiller

def main():
    print("="*50)
    print("🤖 AUTO-APPLIER INICIADO (Modo GitHub Actions / Bajo el agua)")
    print("="*50)
    
    # headless=True significa que NUNCA se abrirá una ventana. Corre invisible.
    agent = BrowserAgent(headless=True)
    filler = FormFiller()
    
    try:
        agent.start()
        
        url = "https://www.linkedin.com/jobs/search/?keywords=Data%20Scientist&f_AL=true"
        agent.navigate(url)
        
        print("[INFO] Verificando acceso silencioso a LinkedIn usando cookies...")
        
        job_cards = agent.page.locator(".job-card-container")
        if job_cards.count() > 0:
            print(f"[INFO] Encontrados {job_cards.count()} empleos. Intentando clic en el primero...")
            job_cards.first.click()
            time.sleep(3)
            
            # Llamamos al Form Filler para que intente presionar Easy Apply
            filler.fill_linkedin_easy_apply(agent.page)
        else:
            print("[INFO] No se encontraron tarjetas de empleo. ¿Las cookies caducaron?")
            
        print("\n[INFO] Ejecución completada en modo oculto.")
        
    except Exception as e:
        print(f"[ERROR CRÍTICO] {e}")
    finally:
        agent.close()

if __name__ == "__main__":
    main()
