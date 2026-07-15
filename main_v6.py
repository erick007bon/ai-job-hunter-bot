"""
AI Job Hunter V6 — Orquestador principal con Auto-Postulación.
Mejora V5 agregando: Playwright → Postulación automática → Reporte Telegram.
"""
import os
import sys
import datetime
import argparse

if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.api_scrapers import RemotiveScraper, RemoteOKScraper, GetOnBoardScraper
from src.scrapers.latam_scrapers import ComputrabajoScraper, TorreScraper
from src.filters.match_engine import MatchEngine
from src.memory.memory_store import MemoryStore
from src.notifications.telegram_notifier import (
    notify_job_found,
    notify_applied,
    notify_application_summary,
    send_telegram,
)
from src.email.gmail_sender import GmailSender

# ── Credenciales del perfil ──────────────────────────────────────────────────
PROFILE = {
    'name':     'Erick Flores Zambrano',
    'email':    'eflores4006@utm.edu.ec',
    'phone':    '+593 096 395 1193',
    'github':   'github.com/erick007bon',
    'linkedin': 'linkedin.com/in/erick-flores-zambrano-69075b198',
}

CV_PATH      = os.environ.get('CV_PATH', 'CV_Erick_Flores.pdf')
MAX_APPS     = int(os.environ.get('MAX_APPLICATIONS', '5'))
AUTO_APPLY   = os.environ.get('AUTO_APPLY', 'true').lower() == 'true'


def build_cover_letter(job: dict) -> str:
    title   = job.get('title', 'la posición')
    company = job.get('company', 'su empresa')
    return f"""Estimado equipo de Selección — {company},

Me dirijo a ustedes con interés en el puesto de {title}. Cuento con experiencia \
en análisis de datos, Python, SQL y Power BI, complementada con formación simultánea \
en Economía (8.° sem.) e Ingeniería en IA/Datos (6.° sem.).

He liderado equipos en retail y desarrollado proyectos de ML aplicados a negocios reales. \
Mi GitHub ({PROFILE['github']}) incluye proyectos en FastAPI, modelos LSTM y análisis econométrico.

Adjunto mi CV. Quedo disponible para una entrevista.

Atentamente,
{PROFILE['name']}
{PROFILE['phone']} | {PROFILE['email']}"""


def generate_report(applied_results: list, all_jobs: list, filtered: list) -> str:
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    success = [r for r in applied_results if r.success]
    failed  = [r for r in applied_results if not r.success]

    lines = [
        f"# 🤖 AI Job Hunter V6 — Reporte {today}",
        f"**Total encontrados:** {len(all_jobs)} | **Compatibles:** {len(filtered)} | **Postulaciones:** {len(applied_results)}",
        f"**✅ Exitosas:** {len(success)} | **❌ Fallidas:** {len(failed)}",
        "",
        "## ✅ Postulaciones Exitosas",
    ]
    for r in success:
        lines.append(f"- **{r.job_title}** @ {r.company} ({r.portal}) → {r.url}")

    if failed:
        lines.append("\n## ⚠️ Postulaciones con Error")
        for r in failed:
            lines.append(f"- **{r.job_title}** @ {r.company} → _{r.message}_")

    lines.append("\n## 🔍 Todas las Ofertas Compatibles (para revisión manual)")
    for j in filtered:
        lines.append(f"- [{j.get('title')} @ {j.get('company')}]({j.get('url')}) — {j.get('source')}")

    return "\n".join(lines)


def main(dry_run: bool = False):
    print("=" * 60)
    print(" 🤖 AI JOB HUNTER V6 — CON AUTO-POSTULACIÓN")
    print(f" Modo: {'🔍 DRY-RUN (sin postular)' if dry_run else '🚀 ACTIVO (postulando)'}")
    print("=" * 60)

    memory = MemoryStore()
    engine = MatchEngine()
    gmail = GmailSender()

    # ── 1. SCRAPING ──────────────────────────────────────────────────────────
    scrapers = [
        RemotiveScraper(),
        RemoteOKScraper(),
        GetOnBoardScraper(),
        ComputrabajoScraper(),
        TorreScraper(),
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

    print(f"\n[TOTAL] {len(all_jobs)} ofertas encontradas")

    # ── 2. FILTRAR ───────────────────────────────────────────────────────────
    filtered = engine.filter_jobs(all_jobs)
    print(f"[FILTRO] {len(filtered)} compatibles con el perfil")

    # ── 3. DESCARTAR YA APLICADOS ────────────────────────────────────────────
    nuevas = []
    for job in filtered:
        if memory.already_applied(job.get('url', '')):
            print(f"  [SKIP] Ya aplicado: {job.get('title')} @ {job.get('company')}")
        else:
            nuevas.append(job)

    print(f"[NUEVAS] {len(nuevas)} ofertas nuevas (no aplicadas antes)")

    # ── 4. AUTO-POSTULACIÓN ──────────────────────────────────────────────────
    applied_results = []

    if dry_run:
        print("\n[DRY-RUN] Mostrando ofertas que se postularían:")
        for job in nuevas[:MAX_APPS]:
            print(f"  → {job.get('title')} @ {job.get('company')} ({job.get('source')})")
    elif AUTO_APPLY and nuevas:
        # Importar aquí para no fallar si Playwright no está instalado en modo dry-run
        try:
            from src.appliers.router import get_applier_for_url
            from src.memory.funnel_db import FunnelDB
            
            funnel = FunnelDB()

            for job in nuevas[:MAX_APPS]:
                url = job.get('url', '')
                source = job.get('source', '')
                
                applier = get_applier_for_url(url, source)

                if applier:
                    print(f"\n[AUTO-APPLY] {job.get('title')} @ {job.get('company')} via {applier.__class__.__name__}")
                    result = applier.apply_sync(job)
                    
                    # Añadir el source original al ApplyResult para la base de datos
                    result.source = source 
                    
                    applied_results.append(result)
                    memory.mark_applied(job)
                    funnel.record_application(result)
                    notify_applied(result)
                else:
                    email_sent = False
                    if job.get('company_email'):
                        print(f"  [EMAIL] Enviando correo en frío a {job['company_email']}")
                        try:
                            cover_letter = build_cover_letter(job)
                            gmail.send_email(
                                to_address=job['company_email'],
                                subject=f"Postulación: {job.get('title')} - {PROFILE['name']}",
                                body_text=cover_letter,
                                cv_path=CV_PATH
                            )
                            email_sent = True
                            print("  -> Correo enviado con éxito")
                            
                            # Mock object for applied_results
                            class EmailResult:
                                success = True
                                job_title = job.get('title')
                                company = job.get('company')
                                portal = 'Cold Email'
                                url = job.get('url')
                                message = 'Correo enviado exitosamente'
                            
                            applied_results.append(EmailResult)
                            memory.mark_applied(job)
                        except Exception as e:
                            print(f"  -> [ERROR CORREO] {e}")

                    notify_job_found(job)
                    if email_sent:
                        print(f"  [NOTIFY] Notificado por Telegram (CON CORREO): {job.get('title')}")
                    else:
                        print(f"  [NOTIFY] Notificado por Telegram (SIN CORREO): {job.get('title')}")

        except ImportError as e:
            print(f"[ERROR] Playwright no instalado: {e}")
            print("  Ejecuta: pip install playwright && playwright install chromium")
    else:
        # Sin auto-apply, solo notificar
        for job in nuevas[:MAX_APPS]:
            notify_job_found(job)

    # ── 5. REPORTE ───────────────────────────────────────────────────────────
    report = generate_report(applied_results, all_jobs, filtered)

    os.makedirs("reportes", exist_ok=True)
    ts          = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    report_path = os.path.join('reportes', f"reporte_{ts}.md")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    with open('OPORTUNIDADES_HOY.md', 'w', encoding='utf-8') as f:
        f.write(report)

    # Resumen final a Telegram
    notify_application_summary(applied_results)

    print(f"\n[DONE] Reporte: {report_path}")
    print(f"       Postulaciones: {len(applied_results)} | Exitosas: {sum(1 for r in applied_results if r.success)}")
    print("=" * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="AI Job Hunter V6")
    parser.add_argument('--dry-run', action='store_true',
                        help='Mostrar qué se postularía sin postular de verdad')
    args = parser.parse_args()
    main(dry_run=args.dry_run)
