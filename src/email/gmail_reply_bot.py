"""
Gmail Reply Bot — Lee respuestas de reclutadores y responde automáticamente.
===============================================================================
Flujo:
  1. Lee el INBOX de Gmail buscando respuestas a postulaciones enviadas
  2. Clasifica el email: interesado / rechazo / silencio / pregunta específica
  3. Genera respuesta personalizada con IA según el tipo
  4. Envía respuesta y notifica por Telegram
"""
import os
import json
import base64
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests

from src.config import Config
from src.notifications.telegram_notifier import send_telegram

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-31b-it:free",
    "deepseek/deepseek-v4-flash:free",
]

# Palabras que indican respuesta positiva (interesado)
POSITIVE_SIGNALS = [
    "interview", "entrevista", "interested", "interesado", "call", "llamada",
    "schedule", "agendar", "meet", "reunión", "shortlisted", "seleccionado",
    "next step", "siguiente paso", "candidato", "candidate", "availability",
    "disponibilidad", "zoom", "teams", "google meet", "cuando puedes",
]

# Palabras que indican rechazo
REJECTION_SIGNALS = [
    "unfortunately", "lamentablemente", "not moving forward", "no continuaremos",
    "other candidates", "otros candidatos", "not a fit", "not selected",
    "no seleccionado", "rejected", "rechazado", "position has been filled",
    "thank you for your interest", "gracias por tu interés, sin embargo",
]


class GmailReplyBot:
    """Lee respuestas de reclutadores y responde automáticamente."""

    def __init__(self):
        self.cv_data = self._load_cv()
        self.replied_log = self._load_replied_log()
        self.service = self._build_gmail_service()

    def _load_cv(self) -> dict:
        if os.path.exists(Config.CV_PATH):
            with open(Config.CV_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_replied_log(self) -> dict:
        log_path = os.path.join(Config.DATA_DIR, "replied_log.json")
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"replied_thread_ids": []}

    def _save_replied_log(self):
        log_path = os.path.join(Config.DATA_DIR, "replied_log.json")
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.replied_log, f, indent=2)

    def _build_gmail_service(self):
        try:
            creds = Credentials.from_authorized_user_file(
                os.path.join(Config.DATA_DIR, 'token.json'),
                ['https://www.googleapis.com/auth/gmail.modify']
            )
            return build('gmail', 'v1', credentials=creds)
        except Exception as e:
            print(f"[REPLY BOT] Error conectando Gmail: {e}")
            return None

    def _decode_body(self, payload: dict) -> str:
        """Extrae el texto del cuerpo del email."""
        body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    body = base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='ignore')
                    break
        elif 'body' in payload:
            data = payload['body'].get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='ignore')
        return body[:3000]  # Limitar a 3000 chars

    def _classify_email(self, subject: str, body: str) -> str:
        """Clasifica el email: 'positive', 'rejection', 'question', 'unknown'"""
        text = (subject + " " + body).lower()
        if any(signal in text for signal in POSITIVE_SIGNALS):
            return "positive"
        if any(signal in text for signal in REJECTION_SIGNALS):
            return "rejection"
        if "?" in body:
            return "question"
        return "unknown"

    def _generate_reply(self, email_type: str, recruiter_name: str,
                        company: str, email_body: str, subject: str) -> str:
        """Genera respuesta automática con IA según el tipo de email."""
        nombre = self.cv_data.get('personal_info', {}).get('nombre', 'Erick Flores Zambrano')

        # Detectar idioma del email
        is_spanish = any(w in email_body.lower() for w in [
            "estimado", "hola", "gracias", "disponibilidad", "entrevista",
            "candidato", "proceso", "por favor"
        ])
        lang = "ESPAÑOL" if is_spanish else "ENGLISH"

        if email_type == "positive":
            prompt = f"""You are a professional job seeker responding to a recruiter who is interested in you.

CONTEXT:
- My name: {nombre}
- Company: {company}
- Recruiter email subject: {subject}
- Recruiter email body: {email_body[:1000]}
- Language to respond: {lang}

TASK: Write a SHORT (max 100 words), professional, enthusiastic reply that:
1. Thanks them for their interest
2. Confirms availability for an interview (Monday-Friday, any time works)
3. Asks for the next steps or offers specific times like "Tuesday or Thursday afternoon"
4. Is warm but not over-the-top
5. Signs as: {nombre} | Data Scientist & AI Engineer | +593 0963951193

Write ONLY the email body. Start directly with the greeting."""

        elif email_type == "rejection":
            prompt = f"""Write a SHORT (max 60 words), graceful rejection response in {lang}.
Company: {company}
Thank them, ask to be kept in mind for future roles, wish them well.
Sign as: {nombre}
Write ONLY the email body."""

        elif email_type == "question":
            prompt = f"""You are {nombre}, a Data Scientist & AI Engineer from Ecuador.
A recruiter from {company} asked: {email_body[:500]}
Reply in {lang} with accurate, confident answers about:
- Availability: immediately (1 week notice)
- Salary expectation: $2,000-4,000 USD/month remote (negotiable)
- Location: Ecuador (UTC-5), fully remote preferred
- Visa: not required for remote work
- English: B2 level, professional written communication
Keep reply under 150 words. Sign as {nombre}."""

        else:
            return ""  # No responder emails ambiguos

        # Llamar a OpenRouter
        headers = {
            "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        for model in FREE_MODELS:
            try:
                r = requests.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json={"model": model,
                          "messages": [{"role": "user", "content": prompt}],
                          "max_tokens": 300},
                    timeout=30
                )
                r.raise_for_status()
                result = r.json()['choices'][0]['message']['content']
                if result and len(result) > 30:
                    return result
            except Exception:
                continue
        return ""

    def _send_reply(self, thread_id: str, message_id: str,
                    to_email: str, subject: str, body: str) -> bool:
        """Envía respuesta al hilo del email original."""
        try:
            import email.mime.text as mime_text
            msg = mime_text.MIMEText(body, 'plain', 'utf-8')
            msg['To'] = to_email
            msg['Subject'] = f"Re: {subject}" if not subject.startswith("Re:") else subject
            msg['In-Reply-To'] = message_id
            msg['References'] = message_id

            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw, 'threadId': thread_id}
            ).execute()
            return True
        except Exception as e:
            print(f"  [REPLY] Error enviando respuesta: {e}")
            return False

    def run(self, max_replies: int = 10) -> dict:
        """Busca y responde emails de reclutadores. Retorna estadísticas."""
        stats = {"positive": 0, "rejection": 0, "question": 0, "skipped": 0}

        if not self.service:
            print("[REPLY BOT] Sin conexión a Gmail — skipping")
            return stats

        print("\n[REPLY BOT] Buscando respuestas de reclutadores en Gmail...")

        try:
            # Buscar en INBOX emails de los últimos 14 días
            query = "in:inbox is:unread -from:me"
            result = self.service.users().messages().list(
                userId='me', q=query, maxResults=50
            ).execute()
            messages = result.get('messages', [])
        except Exception as e:
            print(f"[REPLY BOT] Error leyendo Gmail: {e}")
            return stats

        print(f"  -> {len(messages)} emails sin leer encontrados")
        replied_count = 0

        for msg_ref in messages:
            if replied_count >= max_replies:
                break

            msg_id = msg_ref['id']
            thread_id = msg_ref.get('threadId', msg_id)

            # No responder dos veces al mismo hilo
            if thread_id in self.replied_log['replied_thread_ids']:
                stats['skipped'] += 1
                continue

            try:
                msg = self.service.users().messages().get(
                    userId='me', id=msg_id, format='full'
                ).execute()
            except Exception:
                continue

            # Extraer headers
            headers = {h['name']: h['value']
                       for h in msg['payload'].get('headers', [])}
            subject = headers.get('Subject', '')
            from_email = headers.get('From', '')
            message_id_header = headers.get('Message-ID', msg_id)

            # Extraer email del remitente
            email_match = re.search(r'<(.+?)>', from_email)
            sender_email = email_match.group(1) if email_match else from_email
            sender_name = from_email.split('<')[0].strip().strip('"')

            # Extraer company del email (ej: hr@company.com -> company)
            domain_match = re.search(r'@([\w.-]+)', sender_email)
            company = domain_match.group(1).split('.')[0].title() if domain_match else "la empresa"

            # Extraer cuerpo
            body_text = self._decode_body(msg['payload'])

            # Clasificar
            email_type = self._classify_email(subject, body_text)
            print(f"\n  📧 De: {sender_name} | {email_type.upper()} | Asunto: {subject[:50]}")

            if email_type == "unknown":
                stats['skipped'] += 1
                continue

            # Generar respuesta
            reply_text = self._generate_reply(
                email_type, sender_name, company, body_text, subject
            )
            if not reply_text:
                stats['skipped'] += 1
                continue

            # Enviar respuesta
            sent = self._send_reply(thread_id, message_id_header,
                                    sender_email, subject, reply_text)
            if sent:
                stats[email_type] += 1
                replied_count += 1
                self.replied_log['replied_thread_ids'].append(thread_id)
                self._save_replied_log()

                # Notificar por Telegram
                emoji = "🎉" if email_type == "positive" else ("❌" if email_type == "rejection" else "❓")
                send_telegram(
                    f"{emoji} *Email respondido automáticamente*\n\n"
                    f"De: {sender_name} ({company})\n"
                    f"Tipo: {email_type.upper()}\n"
                    f"Asunto: {subject[:60]}\n"
                    f"✅ Respuesta enviada"
                )
                print(f"  ✅ Respuesta enviada a {sender_email}")
            else:
                stats['skipped'] += 1

        print(f"\n[REPLY BOT] Resumen: {stats}")
        return stats
