import sqlite3
import os
from datetime import datetime

class FunnelDB:
    """
    Base de datos SQLite para registrar el Funnel de Conversión.
    Registra postulaciones enviadas y las respuestas recibidas (positivas/negativas)
    para poder analizar qué keywords y fuentes generan más conversiones.
    """
    def __init__(self):
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            "data", 
            "funnel.db"
        )
        self._init_db()
        
    def _get_conn(self):
        return sqlite3.connect(self.db_path)
        
    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # Tabla de postulaciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    title TEXT,
                    company TEXT,
                    source TEXT,
                    portal TEXT,
                    applied_at TIMESTAMP,
                    success BOOLEAN,
                    message TEXT
                )
            ''')
            
            # Tabla de respuestas (Gmail)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS replies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id INTEGER,
                    reply_date TIMESTAMP,
                    classification TEXT, -- 'positive', 'rejection', 'question'
                    email_body TEXT,
                    FOREIGN KEY (application_id) REFERENCES applications (id)
                )
            ''')
            conn.commit()

    def record_application(self, result) -> bool:
        """Registra el ApplyResult de una postulación o actualiza su estado si ya existía."""
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO applications 
                    (url, title, company, source, portal, applied_at, success, message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(url) DO UPDATE SET
                        applied_at = excluded.applied_at,
                        success = excluded.success,
                        message = excluded.message,
                        portal = excluded.portal
                ''', (
                    result.url,
                    result.job_title,
                    result.company,
                    getattr(result, 'source', ''), 
                    result.portal,
                    datetime.now().isoformat(),
                    result.success,
                    result.message
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"[FunnelDB] ⚠️ Error registrando postulación ({result.job_title}): {e}")
            return False

    def record_reply(self, url: str, classification: str, email_body: str):
        """Registra una respuesta basada en la URL (si se conoce) o la empresa."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # Buscar el ID de la postulación
            cursor.execute('SELECT id FROM applications WHERE url = ?', (url,))
            row = cursor.fetchone()
            app_id = row[0] if row else None
            
            cursor.execute('''
                INSERT INTO replies (application_id, reply_date, classification, email_body)
                VALUES (?, ?, ?, ?)
            ''', (
                app_id,
                datetime.now().isoformat(),
                classification,
                email_body
            ))
            conn.commit()
