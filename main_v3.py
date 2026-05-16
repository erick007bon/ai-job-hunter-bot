"""
AI Job Hunter Bot V3 - Agente Autonomo de Postulacion
======================================================
Flujo:
  1. Extrae trabajos de 8+ plataformas (Ecuador + Sudamerica + Global Remoto)
  2. Filtra por seniority y nivel de ingles B2
  3. Extrae emails de contacto de cada oferta
  4. Genera Cover Letter personalizada con Gemini AI (leyendo el JD real)
  5. Envia email desde Gmail con CV adjunto
  6. Registra en memoria para no repetir postulaciones
"""
import os
import sys
import datetime

# Fix encoding para Windows (evita crash con caracteres especiales en nombres de empresas)
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.scrapers.api_scrapers import RemotiveScraper, RemoteOKScraper, GetOnBoardScraper
from src.scrapers.latam_scrapers import (
    SocioEmpleoScraper, ComputrabajoScraper,
    WeWorkRemotelyScraper, TorreScraper, WorkingNomadsScraper
)
from src.scrapers.linkedin_scraper import LinkedInScraper
from src.filters.match_engine import MatchEngine
from src.extractors.email_extractor import EmailExtractor
from src.ai.gemini_agent import GeminiAgent
from src.email.gmail_sender import GmailSender
from src.memory.memory_store import MemoryStore

def main(send_emails: bool = False, max_new_jobs: int = 5):
    """
    Args:
        send_emails: Si True, envia emails reales. Si False, solo genera drafts.
        max_new_jobs: Maximo de nuevas postulaciones en este ciclo.
    """
    print("=" * 60)
    print(" AI JOB HUNTER V3 - AGENTE AUTONOMO EN ACCION")
    print(f" Modo: {'[EMAIL REAL]' if send_emails else '[MODO DRAFT - sin enviar]'}")
    print("=" * 60)
    
    # PASO 1: RECOLECTAR TRABAJOS BRUTOS
    scrapers = [
        LinkedInScraper(),
        RemotiveScraper(),
        RemoteOKScraper(),
        GetOnBoardScraper(),
        TorreScraper(),
        WeWorkRemotelyScraper(),
        WorkingNomadsScraper(),
        ComputrabajoScraper(),
        SocioEmpleoScraper(),
    ]
    
    all_jobs = []
    for scraper in scrapers:
        name = scraper.__class__.__name__
        print(f"\n[SCRAPER] Cazando en {name}...")
        jobs = scraper.fetch_jobs()
        print(f"  -> {len(jobs)} trabajos encontrados.")
        all_jobs.extend(jobs)
        
    print(f"\n[TOTAL] Extraido en bruto: {len(all_jobs)} ofertas de {len(scrapers)} plataformas.")
    
    # PASO 2: FILTRADO INTELIGENTE
    engine = MatchEngine()
    filtered_jobs = engine.filter_jobs(all_jobs)
    print(f"[FILTRO] Despues de filtros B2/Mid-Level: {len(filtered_jobs)} ofertas compatibles.")
    
    # PASO 2.5: COMPLETAR DESCRIPCIONES DE LINKEDIN PARA LOS FILTRADOS
    linkedin_scraper_instance = next((s for s in scrapers if isinstance(s, LinkedInScraper)), None)
    if linkedin_scraper_instance:
        print("\n[LINKEDIN] Descargando descripciones detalladas de ofertas seleccionadas...")
        for job in filtered_jobs:
            if job['source'] == "LinkedIn" and not job.get('description'):
                job_id = ""
                if "view/" in job['url']:
                    job_id = job['url'].split("view/")[-1].replace("/", "")
                elif "currentJobId=" in job['url']:
                    job_id = job['url'].split("currentJobId=")[-1].split("&")[0]
                    
                if job_id:
                    desc = linkedin_scraper_instance.fetch_job_description(job_id)
                    job['description'] = desc

    # PASO 3: EXTRAER EMAILS
    print("\n[EMAIL EXTRACTOR] Buscando emails de contacto...")
    extractor = EmailExtractor()
    enriched_jobs = extractor.enrich_all(filtered_jobs)
    jobs_with_real_email = [j for j in enriched_jobs if j.get('contact_email')]
    print(f"  -> {len(jobs_with_real_email)} trabajos con email REAL encontrado.")
    print(f"  -> {len(enriched_jobs) - len(jobs_with_real_email)} sin email -> se generaran drafts manuales.")
    
    # PASO 4+5+6: GEMINI AI + ENVIO + MEMORIA
    memory = MemoryStore()
    gemini = GeminiAgent()
    gmail = GmailSender() if send_emails else None
    
    processed = 0
    report_lines = []
    
    print(f"\n[AGENTE] Procesando hasta {max_new_jobs} nuevas postulaciones...")
    
    for job in enriched_jobs:
        if processed >= max_new_jobs:
            break
            
        job_url = job.get('url', '')
        
        # Verificar si ya postulamos antes
        if memory.is_applied(job_url):
            print(f"  [SKIP] Ya postulado: {job.get('title')} @ {job.get('company')}")
            continue
        
        print(f"\n  [PROCESANDO] {job.get('title')} @ {job.get('company')} ({job.get('source')})")
        
        # Generar Cover Letter con Gemini
        print(f"    -> Generando carta con Gemini AI...")
        letter_text = gemini.generate_cover_letter(job)
        cl_path = gemini.save_cover_letter(job, letter_text)
        subject = gemini.generate_email_subject(job)
        
        email_sent = False
        contact_email = job.get('contact_email')  # None si no se encontro email real
        source = job.get('source', '').lower()
        
        # Detectar idioma del trabajo para enviar CV correcto
        SPANISH_SOURCES = ['computrabajo', 'socioempleo', 'getonbrd', 'torre']
        use_english_cv = not any(s in source for s in SPANISH_SOURCES)
        lang_tag = '[EN CV]' if use_english_cv else '[ES CV]'
        
        # Solo enviar si hay email REAL (nunca inventado)
        can_send = (
            send_emails and gmail
            and contact_email  # None = no enviar
            and job.get('email_verified', False)  # Debe ser verificado
        )
        
        if can_send:
            print(f"    -> Enviando {lang_tag} a {contact_email} (email verificado)...")
            email_sent = gmail.send(contact_email, subject, letter_text, use_english_cv=use_english_cv)
        elif contact_email and send_emails and not job.get('email_verified', False):
            # Email encontrado pero no verificado -> enviar igual pero avisar
            print(f"    -> Enviando {lang_tag} a {contact_email} (email encontrado, no verificado)...")
            email_sent = gmail.send(contact_email, subject, letter_text, use_english_cv=use_english_cv)
        else:
            url = job.get('url', 'N/A')
            print(f"    -> Sin email real. Draft guardado. Postula aqui: {url[:70]}")
        
        # Registrar en memoria
        memory.mark_applied(
            job,
            email_sent_to=contact_email if email_sent else None,
            cover_letter_path=cl_path
        )
        
        status = "[EMAIL ENVIADO]" if email_sent else "[DRAFT - POSTULA MANUALMENTE]"
        report_lines.append(f"### {status}: {job.get('title')} @ {job.get('company')}")
        if email_sent:
            report_lines.append(f"- **Email enviado a:** {contact_email}")
        else:
            report_lines.append(f"- **APLICA AQUI:** {job.get('url', 'N/A')}")
            report_lines.append(f"- **Carta guardada en:** {cl_path}")
        report_lines.append(f"- **Fuente:** {job.get('source')}\n")
        
        processed += 1
    
    # GENERAR REPORTE FINAL
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    stats = memory.get_stats()
    
    report = f"# AI JOB HUNTER V3 - Reporte {today}\n\n"
    report += f"> **Extraidas:** {len(all_jobs)} | **Filtradas:** {len(filtered_jobs)} | **Procesadas hoy:** {processed}\n"
    report += f"> **Total historico postulaciones:** {stats['total_postulaciones']} | **Emails enviados total:** {stats['emails_enviados']}\n\n"
    report += "---\n\n"
    report += "\n".join(report_lines)
    report += "\n\n---\n*Bot V3 - Gemini AI + Gmail API + 8 Plataformas. Mente fria, ingresos altos.*"
    
    today_file = datetime.datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(Config.REPORTS_DIR, f"reporte_v3_{today_file}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)
    
    with open(os.path.join(Config.BASE_DIR, "OPORTUNIDADES_HOY.md"), "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"\n[DONE] Reporte V3 guardado. {processed} nuevas postulaciones procesadas.")
    print(f"  Emails enviados (historico): {stats['emails_enviados']}")
    print(f"  Ver cartas en: cover_letters/")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='AI Job Hunter Bot V3')
    parser.add_argument('--send', action='store_true', help='Enviar emails reales (por defecto: solo drafts)')
    parser.add_argument('--max', type=int, default=20, help='Maximo de nuevas postulaciones por ciclo (default: 20)')
    args = parser.parse_args()
    
    main(send_emails=args.send, max_new_jobs=args.max)
