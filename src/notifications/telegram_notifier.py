"""
Telegram Notifier — Envía alertas cuando el bot encuentra oportunidades.
Configurar: crear bot con @BotFather en Telegram, obtener token y chat_id.
"""
import os
import requests

DEFAULT_TELEGRAM_BOT_TOKEN = "<TU_TELEGRAM_BOT_TOKEN>"
DEFAULT_TELEGRAM_CHAT_ID = "<TU_CHAT_ID>"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or DEFAULT_TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or DEFAULT_TELEGRAM_CHAT_ID


def send_telegram(message: str) -> bool:
    """Envía mensaje a Telegram. Retorna True si exitoso. Si falla Markdown, reintenta en texto plano."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or TELEGRAM_BOT_TOKEN or DEFAULT_TELEGRAM_BOT_TOKEN
    chat_id = os.environ.get("TELEGRAM_CHAT_ID") or TELEGRAM_CHAT_ID or DEFAULT_TELEGRAM_CHAT_ID
    if not token or not chat_id:
        print("  [TELEGRAM] Token o chat_id no configurados — saltando notificación.")
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        # Intento 1: con formato Markdown
        r = requests.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False,
        }, timeout=10)
        if r.status_code == 200:
            return True

        # Intento 2: si falló por parse error de Markdown (ej. guiones en URLs), reintentar en texto plano
        plain_text = message.replace('*', '').replace('_', '').replace('`', '')
        r2 = requests.post(url, json={
            "chat_id": chat_id,
            "text": plain_text,
            "disable_web_page_preview": False,
        }, timeout=10)
        if r2.status_code == 200:
            return True

        print(f"  [TELEGRAM] Error al enviar: {r.text} | {r2.text}")
        return False
    except Exception as e:
        print(f"  [TELEGRAM] Error: {e}")
        return False


def notify_job_found(job: dict, manual_action: bool = True, reason: str = ""):
    """Envía una oferta compatible a Telegram con enlace directo para postulación en 1 click."""
    title   = job.get('title', 'Puesto')
    company = job.get('company', 'Empresa')
    source  = job.get('source', 'Web')
    url     = job.get('url', '')
    location = job.get('location', 'Remoto')

    header = "⚡ *OFERTA COMPATIBLE — POSTULA EN 1 CLICK*" if manual_action else "🤖 *Nueva Oportunidad Detectada*"
    reason_line = f"\nℹ️ _{reason}_" if reason else ""

    msg = (
        f"{header}\n\n"
        f"💼 *{title}*\n"
        f"🏢 {company} | 📍 {location}\n"
        f"🌐 Fuente: {source}{reason_line}\n\n"
        f"👉 *Link directo para postular:*\n"
        f"{url}\n\n"
        f"📝 *Pitch para copiar/pegar si lo piden:*\n"
        f"\"Hola, soy Erick Flores Zambrano. Cuento con experiencia práctica en Análisis de Datos, Machine Learning y BI con Python y SQL. Me entusiasma postular a esta posición. Portfolio y código: https://github.com/erick007bon\""
    )
    return send_telegram(msg)


def notify_scholarship_found(scholarship: dict):
    msg = (
        f"🎓 *BECA ENCONTRADA*\n\n"
        f"📌 *{scholarship.get('name')}*\n"
        f"🏛️ {scholarship.get('organization')}\n"
        f"💰 {scholarship.get('amount')}\n"
        f"📅 Deadline: {scholarship.get('deadline')}\n"
        f"🔗 {scholarship.get('url')}"
    )
    send_telegram(msg)


def notify_cycle_summary(total_extracted: int, total_filtered: int,
                          emails_sent: int, drafts: int):
    msg = (
        f"📊 *Ciclo Completado — AI Job Hunter*\n\n"
        f"🔍 Extraídas: {total_extracted}\n"
        f"✅ Relevantes: {total_filtered}\n"
        f"📤 Emails enviados: {emails_sent}\n"
        f"📝 Drafts guardados: {drafts}"
    )
    send_telegram(msg)


def notify_applied(result) -> bool:
    """Notifica en Telegram el resultado de una postulación automática con link completo."""
    icon = "✅" if result.success else "❌"
    msg = (
        f"{icon} *Postulación Automática — {result.portal}*\n\n"
        f"💼 *{result.job_title}*\n"
        f"🏢 {result.company}\n"
        f"📌 Resultado: {result.message}\n"
        f"🔗 {result.url}"
    )
    return send_telegram(msg)


def notify_application_summary(results: list, manual_notified: list = None):
    """Envía resumen diario de postulaciones automáticas y ofertas notificadas."""
    manual_notified = manual_notified or []
    total   = len(results)
    success = sum(1 for r in results if r.success)
    failed  = total - success

    lines = [
        f"🤖 *AI Job Hunter V6 — Reporte del Ciclo*\n",
        f"📊 Postulaciones automáticas: *{total}* (✅ {success} exitosas | ❌ {failed} fallidas)",
        f"📲 Ofertas enviadas para postulación manual: *{len(manual_notified)}*\n",
    ]

    if success > 0:
        lines.append("✅ *Postuladas automáticamente:*")
        for r in results:
            if r.success:
                lines.append(f"• {r.job_title} @ {r.company} ({r.portal})")
        lines.append("")

    if manual_notified:
        lines.append("👉 *Revisa las ofertas enviadas arriba para postularte en 1 tap.*")

    send_telegram("\n".join(lines))

