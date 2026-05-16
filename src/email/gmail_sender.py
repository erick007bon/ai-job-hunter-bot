import os
import base64
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.config import Config

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_PATH = os.path.join(Config.DATA_DIR, "credentials.json")
TOKEN_PATH = os.path.join(Config.DATA_DIR, "token.json")
CV_PDF_ES = Config.CV_PDF_PATH_ES
CV_PDF_EN = Config.CV_PDF_PATH_EN

class GmailSender:
    """Envía emails de postulación directamente desde Gmail via API oficial"""
    
    def __init__(self):
        self.service = self._authenticate()
        
    def _authenticate(self):
        """Autentica con Gmail API usando OAuth 2.0"""
        creds = None
        
        # Si hay token guardado, usarlo
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        
        # Si no hay creds o están vencidas, renovar
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Esto abre el browser UNA SOLA VEZ para autorización
                if not os.path.exists(CREDENTIALS_PATH):
                    print(f"[GMAIL] ATENCIÓN: Coloca credentials.json en {CREDENTIALS_PATH}")
                    print("[GMAIL] Descárgalo desde: https://console.cloud.google.com/apis/credentials")
                    return None
                    
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
                
            # Guardar el token para la próxima vez
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)

    def create_message(self, to: str, subject: str, body: str, use_english_cv: bool = False) -> dict:
        """Crea el mensaje de email con adjunto del CV correcto (ES o EN)"""
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = Config.EMAIL_SENDER
        message['subject'] = subject
        
        # Cuerpo del email
        message.attach(MIMEText(body, 'plain'))
        
        # Seleccionar CV segun idioma
        cv_path = CV_PDF_EN if use_english_cv and os.path.exists(CV_PDF_EN) else CV_PDF_ES
        cv_filename = 'CV_Erick_Flores_DataScientist_EN.pdf' if use_english_cv else 'CV_Erick_Flores_DataScientist.pdf'
        
        # Adjuntar CV PDF
        if os.path.exists(cv_path):
            with open(cv_path, 'rb') as f:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', 'attachment', filename=cv_filename)
                message.attach(attachment)
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

    def send(self, to: str, subject: str, body: str, use_english_cv: bool = False) -> bool:
        """Envia el email con el CV correcto. Retorna True si fue exitoso."""
        if not self.service:
            print("[GMAIL] Sin servicio Gmail. Configura credentials.json primero.")
            return False
        
        try:
            message = self.create_message(to, subject, body, use_english_cv=use_english_cv)
            cv_lang = 'EN' if use_english_cv else 'ES'
            sent_message = self.service.users().messages().send(
                userId='me', body=message).execute()
            print(f"  [GMAIL] [OK] Email enviado a {to} | CV: {cv_lang} | ID: {sent_message['id']}")
            return True
        except HttpError as error:
            print(f"  [GMAIL] [ERROR] Error enviando a {to}: {error}")
            return False
