"""
Gmail sender usando SMTP + App Password (sin OAuth, 100% estable en CI/CD)
"""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class GmailSender:
    def __init__(self):
        self.gmail_user = os.environ.get('GMAIL_USER', 'erickflores6655@gmail.com')
        self.gmail_pass = os.environ.get('GMAIL_APP_PASSWORD', '')

    def send(self, to: str, subject: str, body: str, attachment_path: str = None) -> bool:
        """
        Envia email con Gmail SMTP.
        to: email del destinatario
        subject: asunto
        body: cuerpo en texto plano
        attachment_path: ruta al PDF del CV (opcional)
        """
        if not self.gmail_pass:
            print(f"[Gmail] MODO DRAFT — sin GMAIL_APP_PASSWORD configurado")
            print(f"  Para: {to}")
            print(f"  Asunto: {subject}")
            print(f"  Body preview: {body[:120]}...")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = f"Erick Flores Zambrano <{self.gmail_user}>"
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(attachment_path)
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                msg.attach(part)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.gmail_user, self.gmail_pass)
                server.sendmail(self.gmail_user, to, msg.as_string())

            print(f"[Gmail] ✅ Email enviado a {to} — {subject}")
            return True

        except Exception as e:
            print(f"[Gmail] ❌ Error enviando a {to}: {e}")
            return False
