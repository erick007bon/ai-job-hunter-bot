"""
Main orquestador del bot — versión funcional V5
"""
import os
import sys
import datetime

# Fix encoding Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.api_scrapers import RemotiveScraper, RemoteOKScraper, GetOnBoardScraper
from src.filters.match_engine import MatchEngine
from src.email.gmail_sender import GmailSender
from src.memory.memory_store import MemoryStore

CV_PATH = os.environ.get('CV_PATH', 'CV_Erick_Flores.pdf')

PROFILE = {
    'name': 'Erick Flores Zambrano',
    'email': 'eflores4006@utm.edu.ec',
    'phone': '+593 096 395 1193',
    'github': 'github.com/erick007bon',
    'linkedin': 'linkedin.com/in/erick-flores-zambrano-69075b198',
}

def build_cover_letter(job: dict) -> str:
    title = job.get('title', 'la posición')
    company = job.get('company', 'su empresa')
    return f"""Estimado equipo de Selección — {company},

Me dirijo a ustedes con interés en el puesto de {title}. Cuento con experiencia en análisis de datos, Python, SQL y Power BI, complementada con formación simultánea en Economía (8.° sem.) e Ingeniería en IA/Datos (6.° sem.).

He liderado equipos en retail y desarrollado proyectos de ML aplicados a negocios reales. Mi GitHub ({PROFILE['github']}) incluye proyectos en FastAPI, modelos LSTM y análisis econométrico.

Adjunto mi CV. Quedo disponible para una entrevista.

Atentamente,
{PROFILE['name']}
{PROFILE['phone']} | {PROFILE['email']}"""

def generate_report(jobs_applied: list, jobs_skipped: int, total_found: int) -> str:
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 🤖 AI Job Hunter V5 — Reporte {today}",
        f"**Total encontrados:** {total_found} | **Compatibles:** {len(jobs_applied) + jobs_skipped} | **Aplicados:** {len(jobs_applied)}",
        "",
        "## ✅ Postulaciones enviadas",
    ]
    for j in jobs_applied:
        lines.append(f"- **{j.get('title')}** @ {j.get('company')} ({j.get('source')}) → {j.get('url')}")
    return "\n".join(lines)

def main():
    print("=" * 60)
    print(" 🤖 AI JOB HUNTER V5 — ARRANQUE")
    print("=" * 60)

    memory = MemoryStore()
    sender = GmailSender()
    engine = MatchEngine()

    scrapers = [
        RemotiveScraper(),
        RemoteOKScraper(),
        GetOnBoardScraper(),
    ]

    all_jobs = []
    for scraper in scrapers:
        name = scraper.__class__.__name__
        print(f"\n[SCRAPER] {name}...")
        try:
            jobs = scraper.fetch_jobs()
            print(f"  -> {len(jobs)} trabajos")
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"  -> [ERROR] {name}: {str(e)[:80]}")

    print(f"\n[TOTAL] {len(all_jobs)} ofertas brutas")

    filtered = engine.filter_jobs(all_jobs)
    print(f"[FILTRO] {len(filtered)} compatibles con el perfil")

    applied = []
    skipped = 0
    max_apps = int(os.environ.get('MAX_APPLICATIONS', '5'))

    for job in filtered:
        if len(applied) >= max_apps:
            break

        url = job.get('url', '')
        if memory.already_applied(url):
            print(f"  [SKIP] Ya aplicado: {job.get('title')} @ {job.get('company')}")
            skipped += 1
            continue

        print(f"\n[APP] {job.get('title')} @ {job.get('company')} ({job.get('source')})")

        body = build_cover_letter(job)
        company_email = job.get('company_email', '')

        if company_email:
            sent = sender.send(
                to=company_email,
                subject=f"Postulación: {job.get('title')} — Erick Flores Zambrano",
                body=body,
                attachment_path=CV_PATH if os.path.exists(CV_PATH) else None
            )
        else:
            print(f"  [INFO] Sin email directo — registrando para seguimiento manual")
            sent = False

        memory.mark_applied(job)
        applied.append(job)

    # Generar reporte
    report = generate_report(applied, skipped, len(all_jobs))
    report_path = os.path.join('reportes', f"reporte_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md")
    os.makedirs('reportes', exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    # Actualizar OPORTUNIDADES_HOY.md en el repo
    with open('OPORTUNIDADES_HOY.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n[DONE] Aplicado a {len(applied)} trabajos. Reporte: {report_path}")
    print("=" * 60)

if __name__ == '__main__':
    main()
