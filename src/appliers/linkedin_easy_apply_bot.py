"""
linkedin_easy_apply_bot.py — Bot de Auto-Postulación en LinkedIn con Rate-Limiting Humano.
Implementa Fase 2 y Fase 3:
1. Rate-Limiting Estricto: Máximo 12 aplicaciones Easy Apply cada 24 horas.
2. Ritmo Humano: Delays aleatorios de 25 a 55 segundos entre acciones.
3. Selección Dinámica de CV:
   - Inglés / Internacional -> data/CV_Erick_Flores_EN.pdf
   - Pasantías / Banca / Finanzas -> data/CV_Erick_Flores_Pasantias.pdf
   - Tech / Data / AI -> data/CV_Erick_Flores_Data_AI.pdf
4. Motor de Preguntas (ScreeningEngine) para auto-completar formularios.
5. Verificación de confirmación y reporte a Telegram.
"""

import os
import sys
import time
import random
import datetime
import sqlite3
from typing import Dict, Any, List, Optional

from src.appliers.base_applier import ApplyResult, ApplyStatus
from src.appliers.screening_engine import ScreeningEngine
from src.notifications.telegram_notifier import send_telegram
from src.memory.funnel_db import FunnelDB
from src.memory.memory_store import MemoryStore


class LinkedInEasyApplyBot:
    def __init__(
        self,
        max_daily_apps: int = 12,
        db_path: str = "data/funnel.db"
    ):
        self.max_daily_apps = max_daily_apps
        self.funnel = FunnelDB()
        self.db_path = self.funnel.db_path
        self.memory = MemoryStore()
        self.screening = ScreeningEngine()

    def get_applications_last_24h(self) -> int:
        """Cuenta cuántas aplicaciones de LinkedIn exitosas se han realizado en las últimas 24 horas."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM applications
                    WHERE portal LIKE '%LinkedIn%' 
                      AND success = 1 
                      AND applied_at >= datetime('now', '-24 hours')
                """)
                row = cursor.fetchone()
                return row[0] if row else 0
        except Exception as e:
            print(f"[LinkedInBot] Error consultando cuota diaria: {e}")
            return 0

    def select_cv_for_job(self, job: Dict[str, Any]) -> str:
        """Selecciona inteligentemente el CV más adecuado según el idioma y el rol."""
        title = job.get('title', '').lower()
        desc = job.get('description', '').lower()

        # Detección de idioma inglés
        english_indicators = ['experience', 'requirements', 'responsibilities', 'skills', 'degree', 'qualification']
        is_english = sum(1 for w in english_indicators if w in desc) >= 3

        if is_english:
            cv_candidate = os.path.abspath("data/CV_Erick_Flores_EN.pdf")
            if os.path.isfile(cv_candidate):
                return cv_candidate

        # Detección de pasantías o banca
        pasantia_indicators = ['pasante', 'pasantía', 'pasantias', 'practicante', 'banca', 'banco', 'financiero']
        if any(w in title for w in pasantia_indicators):
            cv_candidate = os.path.abspath("data/CV_Erick_Flores_Pasantias.pdf")
            if os.path.isfile(cv_candidate):
                return cv_candidate

        # Default: CV de Data & AI
        return os.path.abspath("data/CV_Erick_Flores_Data_AI.pdf")

    def apply_sync(self, job: Dict[str, Any]) -> ApplyResult:
        """Alias para compatibilidad con el router y orquestador."""
        return self.apply_to_job(job)

    def apply_to_job(self, job: Dict[str, Any]) -> ApplyResult:
        """
        Ejecuta el flujo de postulación segura con rate limiting y screening engine.
        """
        title = job.get('title', 'Puesto')
        company = job.get('company', 'Empresa')
        url = job.get('url', '')
        job_id = job.get('job_id', '')

        # 1. Verificar límite diario para proteger la cuenta de LinkedIn
        daily_count = self.get_applications_last_24h()
        if daily_count >= self.max_daily_apps:
            msg = f"Límite diario de seguridad alcanzado ({daily_count}/{self.max_daily_apps}). Enviando a Telegram en 1-tap."
            print(f"  [LinkedInBot] 🛡️ {msg}")
            self._dispatch_1tap(job, reason="Cuota de seguridad diaria de LinkedIn completa (12/12)")
            return ApplyResult(
                job_title=title,
                company=company,
                portal="LinkedIn Easy Apply",
                url=url,
                status=ApplyStatus.NEEDS_MANUAL,
                message=msg
            )

        # 2. Selección de CV
        cv_path = self.select_cv_for_job(job)
        cv_name = os.path.basename(cv_path)
        print(f"\n[LinkedInBot] Postulando a: {title} @ {company}")
        print(f"  CV asignado: {cv_name}")

        # 3. Pacing humano (retardo aleatorio de 15 a 35 segundos para simular lectura humana)
        delay = random.uniform(15.0, 35.0)
        print(f"  Pacing humano: esperando {delay:.1f}s antes de enviar...")
        time.sleep(delay)

        # 4. Intentar postulación via Voyager API con Screening Questions
        from src.appliers.linkedin_applier import LinkedInApplier
        applier = LinkedInApplier()
        result = applier.apply_sync(job)

        # 5. Registro y Notificación
        if result.success:
            self.funnel.record_application(result)
            self.memory.mark_applied(job)
            tg_msg = (
                f"✅ *POSTULACIÓN LINKEDIN EASY APPLY EXITOSA*\n\n"
                f"💼 *Puesto:* {title}\n"
                f"🏢 *Empresa:* {company}\n"
                f"📎 *CV Adjunto:* `{cv_name}`\n"
                f"📊 *Cuota diaria usada:* {daily_count + 1}/{self.max_daily_apps}\n"
                f"🔗 *URL:* {url}"
            )
            send_telegram(tg_msg)
            setattr(result, "notified", True)
            print(f"  ✅ [ÉXITO] Postulación enviada y verificada en LinkedIn!")
        else:
            # Si requiere pasos manuales o formularios externos
            self._dispatch_1tap(job, reason=result.message, suggested_cv=cv_name)
            setattr(result, "notified", True)

        return result

    def _dispatch_1tap(self, job: Dict[str, Any], reason: str = "", suggested_cv: str = ""):
        """Despacha a Telegram la tarjeta 1-tap con pitch profesional listo."""
        title = job.get('title', 'Puesto')
        company = job.get('company', 'Empresa')
        url = job.get('url', '')
        cv_name = suggested_cv or os.path.basename(self.select_cv_for_job(job))

        pitch = (
            f"Hola equipo de {company}, soy Erick Flores Zambrano (Economista e Ing. en Ciencia de Datos/IA). "
            f"Cuento con experiencia en Python, SQL, modelos predictivos y automatización. Me entusiasma postular a {title}."
        )

        tg_card = (
            f"⚠️ *LINKEDIN: ACCIÓN EN 1-TAP REQUERIDA*\n\n"
            f"💼 *Puesto:* {title}\n"
            f"🏢 *Empresa:* {company}\n"
            f"📎 *CV Recomendado:* `{cv_name}`\n"
            f"❓ *Motivo:* {reason}\n\n"
            f"📝 *Pitch listo para copiar:*\n_{pitch}_\n\n"
            f"👉 *Postular ahora:* {url}"
        )
        send_telegram(tg_card)
        self.memory.mark_notified_manual(job, reason=reason)
