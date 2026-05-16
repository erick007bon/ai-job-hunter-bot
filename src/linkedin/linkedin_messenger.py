"""
LinkedIn InMail Messenger — Fase 2 Ultra Avanzado
Envía mensajes directos a reclutadores via Voyager API con contexto IA
"""
import requests
import json
import time
import re
import random
from typing import Optional
from src.config import Config

# ============================================================
# PERFIL COMPLETO DE ERICK — Todos sus proyectos reales
# ============================================================
ERICK_PROFILE = {
    "nombre": "Erick Flores",
    "titulo": "Economista & Data Scientist | AI Engineer",
    "github": "https://github.com/erick007bon",
    "linkedin": "https://www.linkedin.com/in/erick-flores-zambrano-69075b198",
    "email": "eflores4006@utm.edu.ec",
    "mensaje_core": (
        "Solo busco una oportunidad para demostrar lo que puedo hacer. "
        "Soy aprendiz rápido y me comprometo al 100%."
    ),
    "proyectos": [
        {
            "nombre": "FCH-ARX V4 — Algoritmo Criptográfico Original",
            "descripcion": (
                "Diseñé e implementé desde cero un algoritmo hash criptográfico "
                "basado en operaciones ARX (Add-Rotate-XOR) con constantes derivadas de "
                "estructuras matemáticas (Tesla 3-6-9, 26 rondas YHVH). "
                "Aprobó el test SAC-NIST con 49.95% de avalancha (referencia SHA-256: 50.02%). "
                "Velocidad: 185 MB/s en C optimizado. Resistencia demostrada: complejidad 2^256."
            ),
            "tecnologias": ["C", "Python", "Criptografía", "NIST FIPS"],
        },
        {
            "nombre": "AI Job Hunter Bot V4 — Agente Autónomo 24/7",
            "descripcion": (
                "Pipeline completo de automatización: scraping de 9 plataformas de empleo "
                "(LinkedIn, Remotive, GetOnBoard, Torre...), verificación de correos reales "
                "con Hunter.io API, generación de cartas personalizadas con LLMs via OpenRouter, "
                "envío automático con Gmail API OAuth 2.0, memoria anti-duplicados y despliegue "
                "24/7 en GitHub Actions. Este bot lo estás usando para contactarme."
            ),
            "tecnologias": ["Python", "LinkedIn API", "Gmail API", "OpenRouter", "GitHub Actions"],
        },
        {
            "nombre": "Trading Algorítmico con Deep Learning",
            "descripcion": (
                "Sistema LSTM (PyTorch) para forecasting de precios S&P 500 con 68% de accuracy "
                "en direccionalidad. Pipeline completo: ingesta de datos, feature engineering, "
                "backtesting de estrategias momentum y mean reversion con Backtrader, "
                "tracking de experimentos con MLflow."
            ),
            "tecnologias": ["PyTorch", "LSTM", "Backtrader", "MLflow", "Python"],
        },
        {
            "nombre": "Sistema Multi-Agente con MCP (Model Context Protocol)",
            "descripcion": (
                "Arquitectura distribuida de agentes especializados para análisis financiero: "
                "agente de scraping (Alpha Vantage, TradingView), agente econométrico (modelos GARCH), "
                "agente LLM para reportes ejecutivos. Implementado con FastAPI y Docker."
            ),
            "tecnologias": ["Python", "FastAPI", "Docker", "MCP", "LLMs", "GARCH"],
        },
        {
            "nombre": "Data Warehouse ETL — Star Schema con Pentaho",
            "descripcion": (
                "Pipeline ETL completo para un Data Warehouse de aerolíneas: "
                "tablas de dimensiones (Aeronave, Ruta, Vuelo, Pasajero), "
                "limpieza SQL, transformaciones en Pentaho Data Integration, "
                "conexión a PostgreSQL. Proyecto académico de nivel producción."
            ),
            "tecnologias": ["Pentaho", "PostgreSQL", "SQL", "ETL", "Star Schema"],
        },
        {
            "nombre": "API RESTful para Modelos Predictivos",
            "descripcion": (
                "Servicio de inferencia ML en producción: clasificación de riesgo crediticio "
                "(Random Forest), containerización Docker, documentación Swagger automática, "
                "CI/CD con GitHub Actions."
            ),
            "tecnologias": ["FastAPI", "Docker", "Random Forest", "GitHub Actions", "REST API"],
        },
        {
            "nombre": "Dashboard BI — Análisis de Ventas 360° (Power BI)",
            "descripcion": (
                "Panel ejecutivo en producción real en Vamoret S.A. (Grupo Palmón): "
                "KPIs en tiempo real, segmentación RFM, análisis de cohortes, "
                "forecasting DAX, conexión directa SQL Server."
            ),
            "tecnologias": ["Power BI", "SQL Server", "DAX", "Data Storytelling"],
        },
        {
            "nombre": "Detección de Enfermedades en Banano (Computer Vision)",
            "descripcion": (
                "CNN para clasificación de enfermedades en cultivos de banano con imágenes reales, "
                "datos del sector agrícola ecuatoriano. Modelo de predicción de precios "
                "con R²=94.53%."
            ),
            "tecnologias": ["CNN", "Computer Vision", "scikit-learn", "Python"],
        },
    ],
    "formacion": [
        "Ing. Ciencia de Datos & IA — Universidad de Guayaquil (4.º semestre)",
        "Economía — Universidad Técnica de Manabí (7.º semestre)",
        "Dos carreras universitarias simultáneas",
    ],
    "skills_clave": [
        "Python avanzado", "Machine Learning (scikit-learn, PyTorch, TensorFlow)",
        "LLMs & Prompt Engineering", "FastAPI + Docker", "SQL avanzado",
        "Power BI", "Econometría (ARIMA, GARCH)", "GitHub Actions / CI-CD",
    ],
}


class LinkedInMessenger:
    """
    Módulo Ultra Avanzado — Envía InMails inteligentes a reclutadores de LinkedIn.
    Usa la Voyager API para encontrar reclutadores y la IA para personalizar mensajes.
    """

    BASE_URL = "https://www.linkedin.com"

    def __init__(self):
        self.li_at = Config.LINKEDIN_LI_AT
        self.jsessionid = Config.LINKEDIN_JSESSIONID.strip('"')
        self.session = self._init_session()
        self.sent_inmails = []

    def _init_session(self) -> requests.Session:
        """Inicializa sesión autenticada con cookies de LinkedIn"""
        session = requests.Session()
        session.cookies.set("li_at", self.li_at, domain=".linkedin.com")
        session.cookies.set("JSESSIONID", f'"{self.jsessionid}"', domain=".linkedin.com")
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/vnd.linkedin.normalized+json+2.1",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
            "csrf-token": self.jsessionid,
            "x-li-lang": "en_US",
            "x-restli-protocol-version": "2.0.0",
        })
        return session

    # ------------------------------------------------------------------ #
    # 1. BUSCAR RECLUTADOR de una oferta de trabajo                        #
    # ------------------------------------------------------------------ #
    def find_recruiter_from_job(self, job_id: str) -> Optional[dict]:
        """
        Intenta obtener el perfil del reclutador/hiring manager de una oferta.
        Usa el endpoint de detalle de oferta para extraer el poster.
        """
        try:
            url = f"{self.BASE_URL}/voyager/api/jobs/jobPostings/{job_id}"
            params = {
                "decorationId": "com.linkedin.voyager.deco.jobs.web.shared.WebFullJobPosting-65"
            }
            r = self.session.get(url, params=params, timeout=10)
            if r.status_code != 200:
                return None

            data = r.json()
            # Buscar el poster en los datos incluidos
            included = data.get("included", [])
            for item in included:
                if "recruitingActions" in str(item) or "poster" in str(item).lower():
                    urn = item.get("entityUrn", "")
                    if "fsd_profile" in urn or "fs_miniProfile" in urn:
                        return {
                            "urn": urn,
                            "nombre": item.get("firstName", "") + " " + item.get("lastName", ""),
                            "titulo": item.get("occupation", "Recruiter"),
                            "public_id": item.get("publicIdentifier", ""),
                        }
            return None
        except Exception as e:
            print(f"  [INMAIL] Error buscando reclutador: {e}")
            return None

    def search_recruiters_by_company(self, company_name: str, max_results: int = 3) -> list:
        """
        Busca perfiles de RRHH/Recruiting en una empresa usando la búsqueda de personas.
        """
        results = []
        try:
            keywords = f"recruiter OR \"talent acquisition\" OR \"human resources\" OR RRHH"
            url = f"{self.BASE_URL}/voyager/api/graphql"
            params = {
                "queryId": "voyagerSearchDashClusters.b0928897b71bd00a5a7291755dcd64f0",
                "variables": json.dumps({
                    "count": max_results,
                    "origin": "GLOBAL_SEARCH_HEADER",
                    "query": {
                        "keywords": keywords,
                        "flagshipSearchIntent": "SEARCH_SRP",
                        "queryParameters": {
                            "currentCompany": [company_name],
                        },
                    },
                    "start": 0,
                }),
            }
            r = self.session.get(url, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                included = data.get("included", [])
                for item in included:
                    if item.get("$type") == "com.linkedin.voyager.dash.search.EntityResultViewModel":
                        urn = item.get("entityUrn", "")
                        title = item.get("primarySubtitle", {}).get("text", "")
                        name = item.get("title", {}).get("text", "")
                        if name:
                            results.append({
                                "urn": urn,
                                "nombre": name,
                                "titulo": title,
                                "public_id": urn.split(":")[-1] if urn else "",
                            })
        except Exception as e:
            print(f"  [INMAIL] Error buscando en empresa: {e}")
        return results

    # ------------------------------------------------------------------ #
    # 2. GENERAR MENSAJE PERSONALIZADO con IA                              #
    # ------------------------------------------------------------------ #
    def generate_smart_message(
        self,
        recruiter: dict,
        job_title: str,
        company: str,
        job_description: str = "",
        lang: str = "es",
    ) -> str:
        """
        Genera un InMail ultra personalizado usando OpenRouter IA.
        Analiza el JD, extrae las 3 skills más pedidas y las conecta con los proyectos reales de Erick.
        """
        # Extraer skills clave del JD (si existe)
        top_skills = self._extract_top_skills(job_description) if job_description else []
        skills_str = ", ".join(top_skills) if top_skills else "data science y automatización"

        # Construir resumen de proyectos para el prompt
        proyectos_str = "\n".join([
            f"- {p['nombre']}: {p['descripcion'][:120]}..."
            for p in ERICK_PROFILE["proyectos"][:5]
        ])

        if lang == "en":
            prompt = f"""You are a job applicant. Write a SHORT LinkedIn InMail (MAX 280 characters) to {recruiter.get('nombre', 'Hiring Manager')} ({recruiter.get('titulo', 'Recruiter')}) at {company} for the role: {job_title}.

The most requested skills in this job are: {skills_str}.

My real projects (choose 2-3 most relevant):
{proyectos_str}

KEY TONE: Humble, genuine, NOT salesy. Say I just want ONE opportunity to prove myself. I'm a fast learner.
My GitHub: github.com/erick007bon

Write ONLY the message, no subject, max 280 chars."""
        else:
            prompt = f"""Eres un candidato a empleo. Escribe un InMail de LinkedIn BREVE (MÁX 280 caracteres) para {recruiter.get('nombre', 'el/la reclutador/a')} ({recruiter.get('titulo', 'Reclutador/a')}) de {company} para el puesto: {job_title}.

Las skills más pedidas en esta oferta son: {skills_str}.

Mis proyectos reales (elige 2-3 los más relevantes para el puesto):
{proyectos_str}

TONO CLAVE: Humilde, genuino, NO vendedor. Decir que solo quiero UNA oportunidad para demostrar lo que puedo hacer. Soy un aprendiz rápido y me comprometo al 100%.
Mi GitHub: github.com/erick007bon

Escribe SOLO el mensaje, sin asunto, máx 280 caracteres."""

        try:
            import requests as req
            resp = req.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek/deepseek-v4-flash",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 120,
                    "temperature": 0.7,
                },
                timeout=15,
            )
            if resp.status_code == 200:
                message = resp.json()["choices"][0]["message"]["content"].strip()
                # Truncar a 280 chars si excede (límite de LinkedIn InMail corto)
                if len(message) > 280:
                    message = message[:277] + "..."
                return message
        except Exception as e:
            print(f"  [INMAIL] Error generando mensaje IA: {e}")

        # Fallback: mensaje pre-armado con proyectos reales
        return self._fallback_message(recruiter, job_title, company, lang)

    def _fallback_message(self, recruiter: dict, job_title: str, company: str, lang: str) -> str:
        """Mensaje de respaldo si la IA falla"""
        nombre = recruiter.get("nombre", "").split()[0] if recruiter.get("nombre") else ""
        saludo = f"Hola {nombre}," if nombre else "Hola,"

        if lang == "en":
            return (
                f"Hi {nombre or 'there'}, I'm Erick, Data Scientist & Economist. "
                f"I built FCH-ARX (crypto algorithm passing NIST), trading bots (LSTM 68% acc) "
                f"and this very bot that found your job. Just seeking one chance to prove myself. "
                f"GitHub: github.com/erick007bon"
            )[:280]
        else:
            return (
                f"{saludo} Soy Erick, Economista y Data Scientist. Construí FCH-ARX "
                f"(algoritmo criptográfico aprobado por NIST), bots de trading con LSTM y "
                f"este mismo bot que encontró tu oferta en {company}. "
                f"Solo busco una oportunidad para demostrar lo que puedo hacer. "
                f"GitHub: github.com/erick007bon"
            )[:280]

    def _extract_top_skills(self, job_description: str, n: int = 3) -> list:
        """Extrae las skills más mencionadas en el JD comparando contra el perfil de Erick"""
        all_skills = [
            "Python", "SQL", "Machine Learning", "Data Science", "AI", "Deep Learning",
            "FastAPI", "Docker", "Power BI", "ETL", "NLP", "LLM", "TensorFlow", "PyTorch",
            "scikit-learn", "Pandas", "NumPy", "AWS", "GCP", "Azure", "Spark", "Airflow",
            "PostgreSQL", "MongoDB", "REST API", "Git", "GitHub", "R", "Tableau",
            "Statistics", "Econometrics", "Economics", "Finance", "Blockchain",
        ]
        jd_lower = job_description.lower()
        found = [(skill, jd_lower.count(skill.lower())) for skill in all_skills if skill.lower() in jd_lower]
        found.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in found[:n]]

    # ------------------------------------------------------------------ #
    # 3. ENVIAR EL MENSAJE via Voyager API                                 #
    # ------------------------------------------------------------------ #
    def send_inmail(self, profile_urn: str, message: str, subject: str = "") -> bool:
        """
        Envía un mensaje directo (InMail) a un perfil de LinkedIn.
        Usa el endpoint de messaging de Voyager.
        """
        try:
            # Limpiar URN para obtener el ID limpio
            member_id = profile_urn.split(":")[-1]

            # Crear conversación nueva
            url = f"{self.BASE_URL}/voyager/api/messaging/conversations"
            payload = {
                "keyVersion": "LEGACY_INBOX",
                "conversationCreate": {
                    "eventCreate": {
                        "value": {
                            "com.linkedin.voyager.messaging.create.MessageCreate": {
                                "attributedBody": {
                                    "text": message,
                                    "attributes": [],
                                },
                                "attachments": [],
                            }
                        }
                    },
                    "recipients": [member_id],
                    "subtype": "MEMBER_TO_MEMBER",
                },
            }

            headers = {
                **self.session.headers,
                "Content-Type": "application/json",
            }

            r = self.session.post(url, json=payload, headers=headers, timeout=15)

            if r.status_code in (200, 201):
                print(f"  [INMAIL] ✅ Mensaje enviado a {profile_urn}")
                self.sent_inmails.append({
                    "urn": profile_urn,
                    "message": message[:80] + "...",
                })
                return True
            else:
                # Intentar endpoint alternativo (connection request + nota)
                return self._send_connection_request(member_id, message[:300])

        except Exception as e:
            print(f"  [INMAIL] ❌ Error enviando InMail: {e}")
            return False

    def _send_connection_request(self, member_id: str, note: str) -> bool:
        """
        Fallback: envía solicitud de conexión con nota personalizada.
        LinkedIn permite 300 chars en la nota de conexión.
        """
        try:
            url = f"{self.BASE_URL}/voyager/api/growth/normInvitations"
            payload = {
                "emberEntityName": "growth/invitation/norm-invitation",
                "invitee": {
                    "com.linkedin.voyager.growth.invitation.InviteeProfile": {
                        "profileId": member_id,
                    }
                },
                "trackingId": self._generate_tracking_id(),
                "message": note[:300],
            }
            r = self.session.post(url, json=payload, timeout=15)
            if r.status_code in (200, 201):
                print(f"  [INMAIL] ✅ Solicitud de conexión enviada con nota a {member_id}")
                return True
            else:
                print(f"  [INMAIL] ⚠️ Conexión devolvió: {r.status_code}")
                return False
        except Exception as e:
            print(f"  [INMAIL] ❌ Error en conexión: {e}")
            return False

    def _generate_tracking_id(self) -> str:
        """Genera un tracking ID aleatorio para la solicitud"""
        import base64
        import os
        return base64.b64encode(os.urandom(16)).decode("utf-8")

    # ------------------------------------------------------------------ #
    # 4. PIPELINE PRINCIPAL — Procesar una lista de trabajos               #
    # ------------------------------------------------------------------ #
    def process_jobs_batch(self, jobs: list, max_inmails: int = 10) -> dict:
        """
        Pipeline completo: dado un batch de ofertas, encuentra reclutadores y les envía
        un InMail inteligente personalizado con los proyectos de Erick.

        Args:
            jobs: Lista de dicts con keys: job_id, title, company, description, url, lang
            max_inmails: Máximo de mensajes a enviar en este ciclo

        Returns:
            dict con estadísticas del ciclo
        """
        stats = {"sent": 0, "failed": 0, "skipped": 0, "details": []}
        processed = 0

        print(f"\n[INMAIL] 🚀 Iniciando ciclo de InMails para {len(jobs)} ofertas...")

        for job in jobs:
            if processed >= max_inmails:
                print(f"[INMAIL] Límite de {max_inmails} InMails alcanzado.")
                break

            job_title = job.get("title", "Posición")
            company = job.get("company", "la empresa")
            job_id = job.get("job_id", "")
            description = job.get("description", "")
            lang = job.get("lang", "es")

            print(f"\n[INMAIL] Procesando: {job_title} @ {company}")

            # 1. Buscar reclutador
            reclutador = None
            if job_id:
                reclutador = self.find_recruiter_from_job(job_id)

            if not reclutador and company:
                print(f"  [INMAIL] Buscando reclutadores en {company}...")
                reclutadores = self.search_recruiters_by_company(company, max_results=2)
                if reclutadores:
                    reclutador = reclutadores[0]

            if not reclutador:
                print(f"  [INMAIL] ⚠️ No se encontró reclutador para {company}")
                stats["skipped"] += 1
                continue

            print(f"  [INMAIL] Reclutador: {reclutador.get('nombre')} — {reclutador.get('titulo')}")

            # 2. Generar mensaje inteligente con todos los proyectos
            mensaje = self.generate_smart_message(
                recruiter=reclutador,
                job_title=job_title,
                company=company,
                job_description=description,
                lang=lang,
            )
            print(f"  [INMAIL] Mensaje generado ({len(mensaje)} chars):\n  → {mensaje[:100]}...")

            # 3. Enviar
            urn = reclutador.get("urn", "")
            ok = self.send_inmail(urn, mensaje)

            if ok:
                stats["sent"] += 1
                stats["details"].append({
                    "empresa": company,
                    "puesto": job_title,
                    "reclutador": reclutador.get("nombre"),
                    "mensaje_preview": mensaje[:100],
                })
            else:
                stats["failed"] += 1

            processed += 1

            # Pausa anti-rate-limit: esperar entre 15 y 40 segundos
            wait = random.randint(15, 40)
            print(f"  [INMAIL] Esperando {wait}s antes del siguiente...")
            time.sleep(wait)

        print(f"\n[INMAIL] 📊 Resumen: ✅ {stats['sent']} enviados | ❌ {stats['failed']} fallidos | ⚠️ {stats['skipped']} sin reclutador")
        return stats
