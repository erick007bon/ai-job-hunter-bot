"""
Telegram Notifier — Envía alertas cuando el bot encuentra oportunidades.
Configurar: crear bot con @BotFather en Telegram, obtener token y chat_id.
"""
import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def send_telegram(message: str) -> bool:
    """Envía mensaje a Telegram. Retorna True si exitoso."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("  [TELEGRAM] Token o chat_id no configurados — saltando notificación.")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
        }, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"  [TELEGRAM] Error: {e}")
        return False


def notify_job_found(job: dict):
    msg = (
        f"🤖 *AI Job Hunter — Nueva Oportunidad*\n\n"
        f"💼 *{job.get('title')}*\n"
        f"🏢 {job.get('company')}\n"
        f"🌐 {job.get('source')}\n"
        f"📧 Email: {job.get('contact_email', 'Sin email directo')}\n"
        f"🔗 {job.get('url', '')[:100]}"
    )
    send_telegram(msg)


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
    """Notifica en Telegram el resultado de una postulación automática."""
    icon = "✅" if result.success else "❌"
    msg = (
        f"{icon} *Postulación Automática — {result.portal}*\n\n"
        f"💼 *{result.job_title}*\n"
        f"🏢 {result.company}\n"
        f"📌 {result.message}\n"
        f"🔗 {result.url[:80]}"
    )
    return send_telegram(msg)


def notify_application_summary(results: list):
    """Envía resumen diario de todas las postulaciones automáticas."""
    total   = len(results)
    success = sum(1 for r in results if r.success)
    failed  = total - success

    if total == 0:
        send_telegram("🤖 *AI Job Hunter V6*\n\nHoy no se encontraron ofertas para postular automáticamente.")
        return

    lines = [
        f"🤖 *AI Job Hunter V6 — Resumen del Día*\n",
        f"📊 Total postulaciones: *{total}*",
        f"✅ Exitosas: *{success}* | ❌ Fallidas: *{failed}*\n",
        "📋 *Detalle:*",
    ]
    for r in results:
        icon = "✅" if r.success else "❌"
        lines.append(f"{icon} {r.job_title} @ {r.company} ({r.portal})")

    send_telegram("\n".join(lines))
