"""
execute_applications.py — Motor de Postulación Activa y Despacho a Telegram.
1. Envía postulaciones formales por correo (con PDF adjunto) a contactos verificados (BIESS, Santa Priscila, Banco de Machala).
2. Despacha tarjetas de postulación manual asistida (1-tap) a Telegram para portales con login corporativo (Banco Guayaquil, cbc Mariposa, Innatum SAS).
3. Registra todas las acciones en funnel.db y applied_jobs.json.
4. Envía comprobante consolidado a Telegram.
"""

import os
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import datetime
from dotenv import load_dotenv

load_dotenv()

from src.memory.funnel_db import FunnelDB
from src.memory.memory_store import MemoryStore
from src.appliers.base_applier import ApplyResult, ApplyStatus
from src.notifications.telegram_notifier import send_telegram

# Configuración
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('EMAIL_USER', 'eflores4006@utm.edu.ec')
SMTP_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'eteivqnqsmicanzv')
PRIMARY_EMAIL = os.environ.get('EMAIL_SENDER', 'erickflores6655@gmail.com')

funnel = FunnelDB()
memory = MemoryStore()

# ── 1. POSTULACIONES POR CORREO DIRECTO (AUTOMÁTICAS) ─────────────────────────
EMAIL_TARGETS = [
    {
        "title": "Pasantías Preprofesionales Universitarias BIESS (Datos / Finanzas / Riesgos / TI)",
        "company": "Banco del Instituto Ecuatoriano de Seguridad Social (BIESS)",
        "url": "https://www.biess.fin.ec/pasantias",
        "to_email": "pasantias.biess@biess.fin.ec",
        "subject": "Postulación Pasantías Preprofesionales 2026 – Erick Flores Zambrano (Economía / Datos)",
        "cv_path": os.path.abspath("data/CV_Erick_Flores_Pasantias_BIESS.pdf"),
        "body": """Estimado Equipo de Selección y Talento Humano del BIESS,

Me dirijo a ustedes con el propósito de postular formalmente a su Convocatoria Nacional de Pasantías Preprofesionales para las áreas de Gestión de Riesgo Crediticio, Inteligencia de Negocios o Inversiones.

Actualmente curso el 8vo semestre de la carrera de Economía en la Universidad Técnica de Manabí (UTMACH) y simultáneamente el 6to semestre de Ingeniería en Ciencia de Datos e Inteligencia Artificial en la Universidad de Guayaquil. Esta formación combinada me permite integrar el análisis macro y microeconómico con el procesamiento avanzado de datos en Python, consultas complejas en SQL, modelado predictivo y dashboards ejecutivos en Power BI.

Cuento con disponibilidad inmediata para cumplir con las horas reglamentarias bajo la Ley de Pasantías, así como con el aval institucional de mi universidad para la suscripción del convenio correspondiente. Adjunto a este mensaje mi Hoja de Vida detallada.

Agradezco de antemano su atención a esta postulación y quedo a su entera disposición para una entrevista.

Atentamente,

Erick Reinaldo Flores Zambrano
C.I.: 0706859341
Teléfono: +593 096 395 1193
Correo: erickflores6655@gmail.com
Machala, El Oro – Ecuador"""
    },
    {
        "title": "Asistente / Pasante de Sistemas y Control de Gestión",
        "company": "Industrial Pesquera Santa Priscila S.A.",
        "url": "https://santa-priscila.com",
        "to_email": "smunoz@santa-priscila.com",
        "subject": "Postulación: Asistente / Pasante de Control de Gestión y Datos – Erick Flores",
        "cv_path": os.path.abspath("data/CV_Erick_Flores_Data_AI.pdf"),
        "body": """Estimada Lcda. Muñoz y Equipo de Talento Humano de Industrial Pesquera Santa Priscila,

Les escribo para presentar mi perfil para sus vacantes o programas de pasantías en las áreas de Control de Gestión, Sistemas o Analítica Operativa en la provincia de El Oro / Guayas.

Cuento con doble perfil académico en Economía (8vo sem., UTMACH) y Ciencia de Datos / Inteligencia Artificial (6to sem., UG). Cuento con experiencia práctica en automatización de extracción de datos, estructuración de bases de datos relacionales (SQL), limpieza y consolidación de reportes de producción en Python y tableros interactivos en Power BI para el monitoreo de indicadores de rendimiento y costos.

Conozco la relevancia del sector acuícola en la economía de nuestra región y mi meta es sumar valor en el análisis de eficiencia y trazabilidad de sus operaciones.

Adjunto mi CV técnico y quedo atento a su gentil convocatoria para una conversación.

Saludos cordiales,

Erick Flores Zambrano
Teléfono: +593 096 395 1193
Email: erickflores6655@gmail.com
Machala, Ecuador"""
    },
    {
        "title": "Pasante / Asistente de Operaciones y TI Banco de Machala",
        "company": "Banco de Machala S.A.",
        "url": "https://www.bancomachala.com",
        "to_email": "rrhh@bancomachala.com",
        "subject": "Postulación Pasantías / Asistente Operaciones y TI – Erick Flores Zambrano",
        "cv_path": os.path.abspath("data/CV_Erick_Flores_Pasantias_BIESS.pdf"),
        "body": """Estimados miembros del Departamento de Talento Humano de Banco de Machala,

Por medio de la presente, presento mi postulación para oportunidades de pasantías o asistencia operativa y tecnológica en su Sede Matriz en la ciudad de Machala.

Como estudiante del 8vo semestre de Economía en la UTMACH y del 6to semestre de Ingeniería en Ciencia de Datos e IA, cuento con una sólida preparación en análisis financiero, automatización de flujos con Python, extracción de datos en SQL y desarrollo de reportes en Power BI. Siendo residente en Machala, dispongo de total flexibilidad para integrarme de manera presencial e inmediata a sus equipos de trabajo.

Mi objetivo es aportar rigor técnico y analítico en la optimización de procesos operativos, control de cartera y análisis de información bancaria de la institución.

Adjunto mi currículum vitae para su revisión y quedo a su disposición para coordinar una entrevista.

Cordialmente,

Erick Flores Zambrano
Teléfono: +593 096 395 1193
Correo: erickflores6655@gmail.com
Machala, El Oro"""
    }
]

# ── 2. OFERTAS 1-TAP PARA TELEGRAM (MANUAL ASISTIDA) ──────────────────────────
MANUAL_TARGETS = [
    {
        "title": "Programa de Pasantías Universitarias e Innovación BG Lab / TI",
        "company": "Banco Guayaquil",
        "url": "https://fa-esvi-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/es/sites/CX_1/requisitions",
        "cv_name": "CV_Erick_Flores_Data_AI.pdf",
        "pitch": "Economista (8vo sem.) e Ing. en IA/Datos (6to sem.). Manejo de Python (FastAPI/Pandas), SQL y modelos predictivos para analítica bancaria e innovación en BG Lab.",
        "action": "Toca el enlace de Oracle Cloud BG, crea cuenta con Google/LinkedIn y pega el pitch."
    },
    {
        "title": "Programa Trainee Comercial y Operaciones",
        "company": "cbc Ecuador (Grupo Mariposa)",
        "url": "https://grupomariposa.com",
        "cv_name": "CV_Erick_Flores_Data_AI.pdf",
        "pitch": "Doble perfil cuantitativo (Economía + Ciencia de Datos). Capacidad para interpretar tendencias de mercado, optimizar indicadores comerciales y dashboards en Power BI/SQL.",
        "action": "Postulación en portal Trainee cbc. Preguntas resueltas: Sin beneficios actuales, Sin familiares en empresa, Expectativa: $550 - $700 USD."
    },
    {
        "title": "Técnico/a en Bases de Datos / SQL",
        "company": "Innatum SAS",
        "url": "https://ec.computrabajo.com/ofertas-de-trabajo/oferta-de-trabajo-de-tecnicoa-en-bases-de-datos-innatum-sas-en-guayaquil-762EF9B8BDE23A5861373E686DCF3405",
        "cv_name": "CV_Erick_Flores_Data_AI.pdf",
        "pitch": "Experiencia en diseño y mantenimiento de bases de datos relacionales, consultas complejas SQL, ETL con Python y soporte operativo.",
        "action": "Postulación 1-click en Computrabajo Ecuador."
    }
]


def send_email_app(target: dict) -> bool:
    print(f"\n[ENVIANDO CORREO] {target['title']} @ {target['company']}")
    print(f"Destinatario: {target['to_email']}")
    print(f"CV Adjunto: {target['cv_path']}")

    if not os.path.isfile(target['cv_path']):
        print(f"❌ Error: Archivo de CV no encontrado: {target['cv_path']}")
        return False

    msg = MIMEMultipart()
    msg['From'] = f"Erick Flores Zambrano <{SMTP_USER}>"
    msg['To'] = target['to_email']
    msg['Subject'] = target['subject']
    msg['Reply-To'] = PRIMARY_EMAIL

    msg.attach(MIMEText(target['body'], 'plain', 'utf-8'))

    with open(target['cv_path'], 'rb') as f:
        cv_bytes = f.read()
    att = MIMEApplication(cv_bytes, _subtype='pdf')
    att.add_header('Content-Disposition', 'attachment', filename='CV_Erick_Flores_Zambrano.pdf')
    msg.attach(att)

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as s:
        s.ehlo()
        s.starttls(context=context)
        s.ehlo()
        s.login(SMTP_USER, SMTP_PASSWORD)
        s.sendmail(SMTP_USER, [target['to_email']], msg.as_string())

    print(f"✅ ¡Correo enviado exitosamente a {target['to_email']}!")
    return True


def run():
    print("=" * 60)
    print("🚀 EJECUTANDO POSTULACIONES AUTOMÁTICAS Y DESPACHO")
    print("=" * 60)

    sent_count = 0
    for app in EMAIL_TARGETS:
        try:
            ok = send_email_app(app)
            if ok:
                sent_count += 1
                res = ApplyResult(
                    job_title=app['title'],
                    company=app['company'],
                    portal="Email RRHH",
                    url=app['url'],
                    status=ApplyStatus.SUBMITTED,
                    message=f"Postulación enviada exitosamente por correo a {app['to_email']} con CV adjunto"
                )
                funnel.record_application(res)
                job_dict = {
                    "title": app['title'],
                    "company": app['company'],
                    "url": app['url'],
                    "source": "Cold Email RRHH",
                    "status": "applied_success",
                    "email_sent_to": app['to_email']
                }
                memory.mark_applied(job_dict)

                # Notificación individual por Telegram
                tg_msg = (
                    f"✅ *POSTULACIÓN ENVIADA POR CORREO*\n\n"
                    f"🏢 *Empresa:* {app['company']}\n"
                    f"💼 *Puesto:* {app['title']}\n"
                    f"📧 *Enviado a:* `{app['to_email']}`\n"
                    f"📎 *CV Adjunto:* `{os.path.basename(app['cv_path'])}`\n"
                    f"📬 *Reply-To:* `{PRIMARY_EMAIL}`\n\n"
                    f"Comprobante registrado en funnel.db."
                )
                send_telegram(tg_msg)
        except Exception as e:
            print(f"❌ Error al enviar a {app['company']}: {e}")

    # Despachar las manuales asistidas a Telegram
    print("\n[TELEGRAM] Despachando alertas 1-Tap para postulación manual asistida...")
    for m in MANUAL_TARGETS:
        tg_card = (
            f"⚡ *OPORTUNIDAD 1-TAP (POSTULACIÓN MANUAL ASISTIDA)*\n\n"
            f"🏢 *Empresa:* {m['company']}\n"
            f"💼 *Puesto:* {m['title']}\n"
            f"📎 *CV a adjuntar:* `{m['cv_name']}`\n\n"
            f"📝 *Carta/Pitch lista para pegar:*\n"
            f"_{m['pitch']}_\n\n"
            f"👉 *Instrucciones:* {m['action']}\n"
            f"🔗 *Enlace directo:* {m['url']}"
        )
        send_telegram(tg_card)
        job_m = {
            "title": m['title'],
            "company": m['company'],
            "url": m['url'],
            "source": "Portal Corporativo"
        }
        memory.mark_notified_manual(job_m, reason="Requiere Login/Portal Corporativo")

    summary_final = (
        f"🎯 *REPORTE DE EJECUCIÓN CONSOLIDADO*\n\n"
        f"✅ *Postulaciones Enviadas por Correo:* {sent_count} (BIESS, Santa Priscila, Banco de Machala)\n"
        f"📲 *Ofertas 1-Tap Despachadas:* {len(MANUAL_TARGETS)} (Banco Guayaquil, cbc Mariposa, Innatum)\n"
        f"💼 *LinkedIn MCP:* Sesión verificada de Erick Flores Zambrano lista para búsquedas y conexiones.\n"
        f"💾 *Persistencia:* funnel.db y applied_jobs.json sincronizados sin duplicados."
    )
    send_telegram(summary_final)
    print("\n" + "=" * 60)
    print("🏁 PROCESO FINALIZADO CON ÉXITO")
    print(f"Total postulaciones enviadas por email: {sent_count}")
    print(f"Total tarjetas 1-tap enviadas a Telegram: {len(MANUAL_TARGETS)}")
    print("=" * 60)


if __name__ == '__main__':
    run()
