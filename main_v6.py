"""
AI Job Hunter V6 — Orquestador principal con Auto-Postulación.

Pipeline:
  1. Scraping multi-canal (LinkedIn 50% + API boards 50%)
     - LinkedIn: scraping de empleos + conexión automática con reclutadores
     - Remotive, RemoteOK, GetOnBoard, Jobicy, WeWorkRemotely, WorkingNomads
  2. Filtrado por perfil (MatchEngine)
  3. Deduplicación (MemoryStore)
  4. Enriquecimiento con email real de RRHH (Hunter.io / EmailExtractor)
  5. Auto-postulación:
     a) Router → detecta ATS (Greenhouse, Lever, Workable, etc.) → Playwright apply
     b) Fallback → cold-email con CV adjunto (SMTP o Gmail OAuth2)
  6. LinkedIn recruiter outreach (conexión automática con nota personalizada)
  7. Notificaciones Telegram
  8. Reporte en markdown

Para configurar: ver secrets en .github/workflows/job_hunter.yml
"""
import os
import sys
import datetime
import argparse
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.api_scrapers import RemotiveScraper, RemoteOKScraper, GetOnBoardScraper, JobicyScraper
from src.scrapers.latam_scrapers import WeWorkRemotelyScraper, WorkingNomadsScraper
from src.scrapers.linkedin_scraper import LinkedInScraper
from src.linkedin.recruiter_connector import RecruiterConnector
from src.filters.match_engine import MatchEngine
from src.memory.memory_store import MemoryStore
from src.extractors.email_extractor import EmailExtractor
from src.notifications.telegram_notifier import (
    notify_job_found,
    notify_applied,
    notify_application_summary,
    send_telegram,
)
from src.email.gmail_sender import GmailSender
from src.config import Config

# ── Perfil del candidato ────────────────────────────────────────────────────
PROFILE = {
    'name':     'Erick Flores Zambrano',
    'email':    'eflores4006@utm.edu.ec',
    'phone':    '+593 096 395 1193',
    'github':   'github.com/erick007bon',
    'linkedin': 'linkedin.com/in/erick-flores-zambrano-69075b198',
}

CV_PATH    = os.environ.get('CV_PATH', Config.CV_PDF_PATH)
MAX_APPS   = int(os.environ.get('MAX_APPLICATIONS', '5'))
AUTO_APPLY = os.environ.get('AUTO_APPLY', 'true').lower() == 'true'

# ── Configuración SMTP (fallback a Gmail OAuth2) ─────────────────────────────
SMTP_HOST     = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT     = int(os.environ.get('SMTP_PORT', '587'))
SMTP_TLS      = os.environ.get('SMTP_TLS', 'true').lower() == 'true'
SMTP_USER     = os.environ.get('EMAIL_USER') or os.environ.get('EMAIL_SENDER') or ''
SMTP_PASSWORD = os.environ.get('EMAIL_PASSWORD') or ''
EMAIL_SENDER  = os.environ.get('EMAIL_SENDER') or SMTP_USER


# ── OpenRouter para IA ───────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')


def build_cover_letter_ai(job: dict) -> str:
    """
    Genera una carta de presentación personalizada usando OpenRouter (Mistral/Gemini).
    Fallback a plantilla estática si no hay API key o falla la IA.
    """
    if not OPENROUTER_API_KEY:
        return build_cover_letter_static(job)

    title   = job.get('title', 'la posición')
    company = job.get('company', 'su empresa')
    jd      = job.get('description', '')[:1500]  # Primeros 1500 chars del JD

    prompt = f"""Eres un experto en búsqueda de empleo para profesionales de Data Science e IA en Latinoamérica.
Escribe una carta de presentación profesional, concisa (máximo 200 palabras) y personalizada para esta oferta.

Candidato: {PROFILE['name']}
Perfil: Economista (8vo sem.) + Estudiante de Ingeniería en IA/Data Science (6to sem.)
Skills clave: Python, SQL, Power BI, Machine Learning, FastAPI, modelos LSTM
GitHub: {PROFILE['github']} (proyectos en ML, FastAPI, econometría)
Idiomas: Español (nativo), Inglés (B2)

Empresa: {company}
Puesto: {title}
Descripción del puesto: {jd if jd else 'No disponible'}

La carta debe:
1. Ser en español si la empresa parece latinoamericana, inglés si parece internacional
2. Conectar 2-3 skills del candidato directamente con lo que pide la JD
3. Ser directa, sin frases genéricas como "soy apasionado por..."
4. Terminar pidiendo una entrevista con datos de contacto

Devuelve SOLO el texto de la carta, sin encabezados ni instrucciones."""

    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.7,
        )
        letter = response.choices[0].message.content.strip()
        print(f"  [IA] Cover letter generada con OpenRouter ({len(letter)} chars)")
        return letter
    except Exception as e:
        print(f"  [IA] OpenRouter falló ({e}), usando plantilla estática")
        return build_cover_letter_static(job)


def build_cover_letter_static(job: dict) -> str:
    """Plantilla estática de cover letter (fallback cuando no hay IA)."""
    title   = job.get('title', 'la posición')
    company = job.get('company', 'su empresa')
    return f"""Estimado equipo de Selección — {company},

Me dirijo a ustedes con interés en el puesto de {title}. Cuento con experiencia \
en análisis de datos, Python, SQL y Power BI, complementada con formación simultánea \
en Economía (8.° sem.) e Ingeniería en IA/Datos (6.° sem.) en Ecuador.

He liderado equipos en retail y desarrollado proyectos de ML aplicados a negocios reales. \
Mi GitHub ({PROFILE['github']}) incluye proyectos en FastAPI, modelos LSTM y análisis econométrico.

Adjunto mi CV. Quedo disponible para una entrevista en cualquier horario.

Atentamente,
{PROFILE['name']}
{PROFILE['phone']} | {PROFILE['email']}
{PROFILE['linkedin']}"""


def send_cold_email_smtp(
    to_email: str,
    job: dict,
    cover_letter: str,
    cv_path: str,
) -> bool:
    """
    Envía cold-email con CV adjunto usando SMTP directo.
    Más estable que Gmail OAuth2 en CI/CD (no caduca).
    Retorna True si el envío fue exitoso.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print("  [SMTP] EMAIL_USER o EMAIL_PASSWORD no configurados")
        return False

    if not os.path.isfile(cv_path):
        print(f"  [SMTP] CV no encontrado: {cv_path}")
        return False

    title   = job.get('title', 'Postulación')
    company = job.get('company', '')

    subject = f"Application: {title} – {PROFILE['name']}"
    if any(c in company.lower() for c in ['latam', 'ec', 'col', 'peru', 'mx', 'arg', 'chile']):
        subject = f"Postulación: {title} – {PROFILE['name']}"

    msg = MIMEMultipart()
    msg['From']    = EMAIL_SENDER or SMTP_USER
    msg['To']      = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(cover_letter, 'plain', 'utf-8'))

    # Adjuntar CV
    with open(cv_path, 'rb') as f:
        cv_data = f.read()
    cv_attachment = MIMEApplication(cv_data, _subtype='pdf')
    cv_attachment.add_header('Content-Disposition', 'attachment',
                              filename='CV_Erick_Flores_Zambrano.pdf')
    msg.attach(cv_attachment)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            if SMTP_TLS:
                server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        print(f"  [SMTP] ✅ Email enviado → {to_email}")
        return True
    except Exception as e:
        print(f"  [SMTP] ❌ Error al enviar: {e}")
        return False


def generate_report(applied_results: list, all_jobs: list, filtered: list) -> str:
    today   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    success = [r for r in applied_results if r.success]
    failed  = [r for r in applied_results if not r.success]

    lines = [
        f"# 🤖 AI Job Hunter V6 — Reporte {today}",
        f"**Total encontrados:** {len(all_jobs)} | **Compatibles:** {len(filtered)} | "
        f"**Postulaciones:** {len(applied_results)}",
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
        lines.append(
            f"- [{j.get('title')} @ {j.get('company')}]({j.get('url')}) — {j.get('source')}"
        )

    return "\n".join(lines)


def dedupe_jobs(jobs: list) -> list:
    """Elimina duplicados por URL (case-insensitive, trailing slash normalizado)."""
    seen   = set()
    unique = []
    for job in jobs:
        url = job.get('url', '').rstrip('/').lower()
        if url and url not in seen:
            seen.add(url)
            unique.append(job)
    return unique


def main(dry_run: bool = False):
    print("=" * 60)
    print(" 🤖 AI JOB HUNTER V6 — CON AUTO-POSTULACIÓN")
    print(f" Modo: {'🔍 DRY-RUN (sin postular)' if dry_run else '🚀 ACTIVO (postulando)'}")
    print(f" CV disponible: {'✅ SÍ' if os.path.isfile(CV_PATH) else '❌ NO (configura CV_PDF_B64 en GitHub Secrets)'}")
    print(f" SMTP: {'✅ Configurado' if SMTP_USER and SMTP_PASSWORD else '⚠️ No configurado'}")
    print(f" IA Cover Letters: {'✅ OpenRouter' if OPENROUTER_API_KEY else '⚠️ Usando plantilla estática'}")
    print("=" * 60)

    memory = MemoryStore()
    engine = MatchEngine()

    # ── 1. SCRAPING ──────────────────────────────────────────────────────────
    # LinkedIn aporta ~50% de las búsquedas; el resto de boards el otro 50%
    scrapers = [
        LinkedInScraper(),        # 🔵 LinkedIn — empleos Data/AI/ML (cookies Voyager)
        RemotiveScraper(),        # API estable
        RemoteOKScraper(),        # API estable
        GetOnBoardScraper(),      # API v0 LATAM — Data Science & AI
        JobicyScraper(),          # API estable
        WeWorkRemotelyScraper(),  # RSS — Programming & DevOps
        WorkingNomadsScraper(),   # JSON API — remoto global
    ]

    all_jobs = []
    for scraper in scrapers:
        name = scraper.__class__.__name__
        print(f"\n[SCRAPER] {name}...")
        try:
            jobs = scraper.fetch_jobs()
            print(f"  → {len(jobs)} trabajos")
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"  → [ERROR] {name}: {str(e)[:80]}")

    all_jobs = dedupe_jobs(all_jobs)
    print(f"\n[TOTAL] {len(all_jobs)} ofertas únicas encontradas")

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

    # ── 3.5. ENRIQUECER CON EMAILS REALES ────────────────────────────────────
    if nuevas and not dry_run:
        print("\n[EMAIL EXTRACTOR] Buscando emails reales de RRHH...")
        try:
            extractor   = EmailExtractor()
            nuevas      = extractor.enrich_all(nuevas)
            emails_found = sum(1 for j in nuevas if j.get('contact_email'))
            print(f"[EMAIL EXTRACTOR] {emails_found}/{len(nuevas)} ofertas con email real")
        except Exception as e:
            print(f"[EMAIL EXTRACTOR] Error: {e}")

    # ── 4. AUTO-POSTULACIÓN ──────────────────────────────────────────────────
    applied_results = []

    if dry_run:
        print("\n[DRY-RUN] Ofertas que se postularían:")
        for job in nuevas[:MAX_APPS]:
            print(f"  → {job.get('title')} @ {job.get('company')} ({job.get('source')})")
        return

    if not AUTO_APPLY:
        for job in nuevas[:MAX_APPS]:
            notify_job_found(job)
    else:
        try:
            from src.appliers.router import get_applier_for_url
            from src.memory.funnel_db import FunnelDB
            from src.appliers.base_applier import ApplyResult

            funnel = FunnelDB()


            for job in nuevas[:MAX_APPS]:
                url    = job.get('url', '')
                source = job.get('source', '')
                title  = job.get('title', 'Puesto')
                company = job.get('company', 'Empresa')

                print(f"\n{'─'*50}")
                print(f"[JOB] {title} @ {company}")
                print(f"      Source: {source} | URL: {url[:60]}...")

                # ── Intentar applier ATS (Playwright) ──
                applier = get_applier_for_url(url, source)

                if applier:
                    print(f"[AUTO-APPLY] Usando {applier.__class__.__name__}")
                    result        = applier.apply_sync(job)
                    result.source = source
                    applied_results.append(result)
                    funnel.record_application(result)
                    if result.success:
                        memory.mark_applied(job)
                        notify_applied(result)
                    else:
                        print(f"  [APPLY FAIL] {result.message} — intentando cold-email")
                        # Si el applier falla, intentar cold-email como fallback
                        _try_cold_email(job, funnel, memory, applied_results)
                else:
                    # ── Fallback: cold-email directo ──
                    _try_cold_email(job, funnel, memory, applied_results)
                    notify_job_found(job)

        except ImportError as e:
            print(f"[ERROR] Playwright no instalado: {e}")
            print("  → Notificando ofertas sin postular...")
            for job in nuevas[:MAX_APPS]:
                notify_job_found(job)

    # ── 5. LINKEDIN RECRUITER OUTREACH ────────────────────────────────────────
    if not dry_run:
        print("\n[LINKEDIN] 🔵 Buscando reclutadores en LinkedIn para conectar...")
        try:
            connector = RecruiterConnector()
            connected = connector.run(max_connections=8)
            print(f"[LINKEDIN] ✅ Conexiones enviadas: {connected}")
            if connected > 0:
                send_telegram(f"🔵 LinkedIn: {connected} solicitudes de conexión enviadas a reclutadores de Data/AI")
        except Exception as e:
            print(f"[LINKEDIN] ⚠️ Error en recruiter outreach: {e}")

    # ── 6. REPORTE ───────────────────────────────────────────────────────────
    report = generate_report(applied_results, all_jobs, filtered)

    os.makedirs("reportes", exist_ok=True)
    ts          = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    report_path = os.path.join('reportes', f"reporte_{ts}.md")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    notify_application_summary(applied_results)

    print(f"\n[DONE] Reporte: {report_path}")
    print(f"       Postulaciones: {len(applied_results)} | "
          f"Exitosas: {sum(1 for r in applied_results if r.success)}")
    print("=" * 60)



def _try_cold_email(job: dict, funnel, memory, applied_results: list):
    """
    Intenta enviar un cold-email con el CV adjunto.
    Primero intenta SMTP directo; si falla, intenta Gmail OAuth2.
    Registra el resultado en funnel y memory.
    """
    from src.appliers.base_applier import ApplyResult

    contact_email  = job.get('contact_email')
    email_verified = job.get('email_verified', False)

    if not contact_email:
        print("  [COLD EMAIL] Sin email de contacto disponible")
        return

    if not email_verified:
        print(f"  [COLD EMAIL] Email no verificado ({contact_email}) — omitiendo")
        return

    print(f"\n[COLD EMAIL] {job.get('title')} @ {job.get('company')} → {contact_email}")

    cover_letter = build_cover_letter_ai(job)
    success      = False
    method_used  = 'Cold Email'

    # 1. Intentar SMTP directo
    if SMTP_USER and SMTP_PASSWORD:
        success     = send_cold_email_smtp(contact_email, job, cover_letter, CV_PATH)
        method_used = 'Cold Email (SMTP)'
    else:
        # 2. Fallback a Gmail OAuth2
        try:
            gmail   = GmailSender()
            success = gmail.send(
                to=contact_email,
                subject=f"Postulación: {job.get('title')} - {PROFILE['name']}",
                body=cover_letter,
                attachment_path=CV_PATH,
            )
            method_used = 'Cold Email (Gmail OAuth2)'
            if success:
                print("  → Correo enviado con Gmail OAuth2")
            else:
                print("  → [DRAFT] Gmail OAuth2 en modo draft")
        except Exception as e:
            print(f"  → [ERROR Gmail] {e}")

    result = ApplyResult(
        job_title=job.get('title'),
        company=job.get('company'),
        portal=method_used,
        url=job.get('url'),
        success=success,
        message='Email enviado exitosamente' if success else 'Fallo el envío de email',
        source=job.get('source', ''),
    )

    applied_results.append(result)
    funnel.record_application(result)
    if success:
        memory.mark_applied(job)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="AI Job Hunter V6")
    parser.add_argument('--dry-run', action='store_true',
                        help='Mostrar qué se postularía sin postular de verdad')
    args = parser.parse_args()
    main(dry_run=args.dry_run)
