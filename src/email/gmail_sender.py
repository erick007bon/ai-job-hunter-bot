"""
Email sender usando Gmail API con OAuth2.
Usa los mismos credentials.json y token.json que el reply bot.
NO necesita App Password — funciona con el token OAuth que ya tenemos.
"""
import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from src.config import Config


class GmailSender:
    """
    Envía emails via Gmail API (OAuth2).
    Credenciales: data/credentials.json + data/token.json
    (reconstruidos desde GMAIL_CREDENTIALS_B64 y GMAIL_TOKEN_B64 en GitHub Actions)
    """
    def __init__(self):
        self.service = self._build_service()

    def _build_service(self):
        token_path = os.path.join(Config.DATA_DIR, 'token.json')
        creds_path = os.path.join(Config.DATA_DIR, 'credentials.json')

        try:
            creds = Credentials.from_authorized_user_file(
                token_path,
                ['https://www.googleapis.com/auth/gmail.send']
            )
            # Refrescar token si expiró
            if creds and creds.expired and creds.refresh_token:
                print("[Email] Token expirado, refrescando...")
                creds.refresh(Request())
                # Guardar token actualizado
                with open(token_path, 'w') as f:
                    f.write(creds.to_json())
                print("[Email] Token refrescado OK")

            return build('gmail', 'v1', credentials=creds)
        except Exception as e:
            print(f"[Email] ERROR conectando Gmail API: {e}")
            return None

    def send(self, to: str, subject: str, body: str,
             attachment_path: str = None, use_english_cv: bool = True) -> bool:
        """Envía email con Gmail API. Retorna True si exitoso."""
        if not self.service:
            print(f"[Email] MODO DRAFT — sin conexión Gmail API")
            print(f"  Para: {to}")
            print(f"  Asunto: {subject}")
            print(f"  Body: {body[:150]}...")
            return False

        try:
            msg = MIMEMultipart()
            sender = Config.EMAIL_SENDER or 'eflores4006@utm.edu.ec'
            msg['From'] = f"Erick Flores Zambrano <{sender}>"
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Adjuntar CV si existe
            cv_path = attachment_path
            if not cv_path:
                cv_path = Config.CV_PDF_PATH_EN if use_english_cv else Config.CV_PDF_PATH_ES
            
            if cv_path and os.path.exists(cv_path):
                with open(cv_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(cv_path)
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                msg.attach(part)

            # Enviar via Gmail API
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            print(f"[Email] OK enviado a {to} — {subject}")
            return True

        except Exception as e:
            print(f"[Email] ERROR enviando a {to}: {e}")
            return False
