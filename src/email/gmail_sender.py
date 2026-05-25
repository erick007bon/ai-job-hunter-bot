"""
Email sender con soporte Gmail (smtp.gmail.com) y Outlook/Microsoft 365 (smtp.office365.com)
Usa App Password para Gmail o contraseña normal para cuentas institucionales Microsoft.
"""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class GmailSender:
    """
    Soporta:
      - Gmail:   SMTP_HOST=smtp.gmail.com   SMTP_PORT=465  SSL
      - Outlook: SMTP_HOST=smtp.office365.com SMTP_PORT=587 TLS
    """
    def __init__(self):
        self.email_user = os.environ.get('EMAIL_USER', 'eflores4006@utm.edu.ec')
        self.email_pass = os.environ.get('EMAIL_PASSWORD', '')
        self.smtp_host  = os.environ.get('SMTP_HOST', 'smtp.office365.com')
        self.smtp_port  = int(os.environ.get('SMTP_PORT', '587'))
        self.use_tls    = os.environ.get('SMTP_TLS', 'true').lower() == 'true'

    def send(self, to: str, subject: str, body: str, attachment_path: str = None) -> bool:
        if not self.email_pass:
            print(f"[Email] MODO DRAFT — sin EMAIL_PASSWORD configurado")
            print(f"  Para: {to}")
            print(f"  Asunto: {subject}")
            print(f"  Body: {body[:150]}...")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = f"Erick Flores Zambrano <{self.email_user}>"
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

            if self.use_tls:
                # Office365 / Outlook — TLS en puerto 587
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.ehlo()
                    server.starttls()
                    server.login(self.email_user, self.email_pass)
                    server.sendmail(self.email_user, to, msg.as_string())
            else:
                # Gmail — SSL directo en puerto 465
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                    server.login(self.email_user, self.email_pass)
                    server.sendmail(self.email_user, to, msg.as_string())

            print(f"[Email] OK enviado a {to} — {subject}")
            return True

        except Exception as e:
            print(f"[Email] ERROR enviando a {to}: {e}")
            return False
