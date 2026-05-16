import os
import datetime
from src.config import Config
from src.scrapers.api_scrapers import RemotiveScraper, RemoteOKScraper, GetOnBoardScraper
from src.filters.match_engine import MatchEngine
from src.generator.cover_letter import CoverLetterGenerator

def main():
    print("Iniciando AI Job Hunter Bot V2...")
    
    # 1. Extraer Trabajos
    scrapers = [
        RemotiveScraper(),
        RemoteOKScraper(),
        GetOnBoardScraper()
    ]
    
    all_jobs = []
    for scraper in scrapers:
        name = scraper.__class__.__name__
        print(f"Cazando en {name}...")
        jobs = scraper.fetch_jobs()
        print(f"  -> {len(jobs)} trabajos encontrados.")
        all_jobs.extend(jobs)
        
    print(f"\nTotal extraído en bruto: {len(all_jobs)} ofertas.")
    
    # 2. Filtrado Inteligente (Nivel B2, Seniority Mid)
    engine = MatchEngine()
    filtered_jobs = engine.filter_jobs(all_jobs)
    
    print(f"Total después de filtros (B2 / Mid-Level): {len(filtered_jobs)} ofertas altamente compatibles.\n")
    
    # 3. Generación de Reporte y Cover Letters
    generator = CoverLetterGenerator()
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    report = f"# 💸 AI JOB HUNTER V2: Reporte Diario de Ingresos - {today}\n\n"
    report += f"> **Ofertas Filtradas:** {len(filtered_jobs)} / {len(all_jobs)} (Aplicando reglas B2 Inglés y Max Mid-Level)\n"
    report += "---\n\n"
    
    if filtered_jobs:
        for job in filtered_jobs:
            title = job.get('title', 'Sin título')
            company = job.get('company', 'Confidencial')
            salary = job.get('salary', 'No especificado')
            link = job.get('url', '#')
            source = job.get('source', 'Web')
            
            # Generar Cover Letter
            cl_path = generator.generate_for_job(job)
            
            report += f"### 💼 [{title} @ {company}]({link})\n"
            report += f"- **Fuente:** {source} | **Ubicación:** {job.get('location', 'Remoto')}\n"
            report += f"- **Salario/Rango:** {salary}\n"
            report += f"- **🤖 Cover Letter Autogenerada:** Listo en `cover_letters/`\n\n"
    else:
        report += "*No se encontraron ofertas altamente compatibles el día de hoy.*\n\n"

    report += "\n---\n*Bot ejecutado con arquitectura modular. Mente fría, ingresos altos.*"
    
    # Save the report
    filepath = os.path.join(Config.REPORTS_DIR, f"oportunidades_v2_{today}.md")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)
        
    # Also update the main one
    with open(os.path.join(Config.BASE_DIR, "OPORTUNIDADES_HOY.md"), "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"[OK] Reporte V2 guardado en {filepath}")

if __name__ == "__main__":
    main()
