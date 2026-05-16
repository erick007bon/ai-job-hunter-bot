"""
Recruiter Connector — Fase 3
Encuentra y conecta con 50 reclutadores de Data/AI en LinkedIn automaticamente.
Envia solicitud de conexion con nota personalizada contextual al perfil del reclutador.
"""
import requests
import json
import time
import random
import os
from typing import Optional
from src.config import Config


# Mensajes de nota para la solicitud de conexion (rotar para no sonar repetitivo)
CONNECTION_NOTES = [
    (
        "Hola {nombre}, soy Erick — Data Scientist & Economist con proyectos en "
        "ML, criptografia y automatizacion IA. Me interesa conectar con profesionales "
        "del area. Mi GitHub: github.com/erick007bon"
    ),
    (
        "Hola {nombre}, vi tu perfil y me parece muy interesante tu trayectoria en "
        "{area}. Soy Erick, estoy buscando oportunidades remotas en Data Science / AI. "
        "Seria un placer conectar."
    ),
    (
        "Hola {nombre}! Soy Economista y Data Scientist, construi un algoritmo "
        "criptografico propio (aprobado NIST) y bots de IA en Python. Busco mi "
        "primera oportunidad remota. Me gustaria estar en tu red."
    ),
    (
        "Hi {nombre}, I'm Erick — Data Scientist from Ecuador. I've built ML systems "
        "(trading bot LSTM 68% acc, crypto algorithm passing NIST). Looking for remote "
        "opportunities. Would love to connect! github.com/erick007bon"
    ),
    (
        "Hi {nombre}, saw your work in {area} — very relevant to what I do. "
        "I'm a Data Scientist & Economist seeking remote roles. Would be great to connect "
        "and learn from your experience."
    ),
]

# Keywords para buscar reclutadores relevantes
RECRUITER_SEARCHES = [
    {"keywords": "data science recruiter", "location": ""},
    {"keywords": "AI engineer recruiter", "location": ""},
    {"keywords": "machine learning talent", "location": ""},
    {"keywords": "tech recruiter data", "location": ""},
    {"keywords": "reclutador data scientist", "location": ""},
    {"keywords": "talent acquisition data engineer", "location": ""},
    {"keywords": "hiring manager data science", "location": ""},
    {"keywords": "recruiter python developer", "location": ""},
    {"keywords": "reclutador tecnologia IA", "location": ""},
    {"keywords": "talent data engineer remote", "location": ""},
]


class RecruiterConnector:
    """
    Busca reclutadores de Data/AI en LinkedIn y les envia
    solicitudes de conexion con nota personalizada.
    """

    BASE_URL = "https://www.linkedin.com"

    def __init__(self):
        self.li_at = Config.LINKEDIN_LI_AT
        self.jsessionid = Config.LINKEDIN_JSESSIONID.strip('"')
        self.session = self._init_session()
        self.connected = []
        self.log_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "connections_log.json"
        )
        self._load_log()

    def _init_session(self) -> requests.Session:
        session = requests.Session()
        session.cookies.set("li_at", self.li_at, domain=".linkedin.com")
        session.cookies.set("JSESSIONID", f'"{self.jsessionid}"', domain=".linkedin.com")
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/vnd.linkedin.normalized+json+2.1",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
            "csrf-token": self.jsessionid,
            "x-restli-protocol-version": "2.0.0",
        })
        return session

    def _load_log(self):
        """Carga historial de conexiones para no repetir"""
        if os.path.exists(self.log_file):
            with open(self.log_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.already_connected = set(data.get("sent", []))
        else:
            self.already_connected = set()

    def _save_log(self):
        """Guarda historial de conexiones"""
        data = {"sent": list(self.already_connected), "total": len(self.already_connected)}
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # ------------------------------------------------------------------ #
    # 1. BUSCAR RECLUTADORES                                               #
    # ------------------------------------------------------------------ #
    def search_recruiters(self, keywords: str, max_results: int = 10) -> list:
        """
        Busca perfiles de reclutadores en LinkedIn usando la API de busqueda.
        Retorna lista de perfiles con URN y nombre.
        """
        results = []
        try:
            # Formato custom de LinkedIn para las variables GraphQL
            k_encoded = keywords.replace(' ', '%20')
            variables = f"(start:0,query:(flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:keywords,value:List({k_encoded})),(key:resultType,value:List(PEOPLE)))))"
            
            # Usar string crudo para evitar que requests URL-encode los parentesis a %28, lo cual rompe LinkedIn
            raw_url = f"{self.BASE_URL}/voyager/api/graphql?variables={variables}&queryId=voyagerSearchDashClusters.b0928897b71bd00a5a7291755dcd64f0"
            r = self.session.get(raw_url, timeout=12)

            if r.status_code == 200:
                data = r.json()
                included = data.get("included", [])
                for item in included:
                    item_type = item.get("$type", "")
                    if "EntityResultViewModel" in item_type or "MiniProfile" in item_type:
                        urn = item.get("entityUrn", "")
                        name = (
                            item.get("title", {}).get("text", "")
                            or f"{item.get('firstName', '')} {item.get('lastName', '')}".strip()
                        )
                        subtitle = item.get("primarySubtitle", {}).get("text", "")
                        public_id = item.get("publicIdentifier", "")
                        member_id = urn.split(":")[-1].split(",")[0] if urn else ""

                        if name and member_id and member_id not in self.already_connected:
                            results.append({
                                "urn": urn,
                                "member_id": member_id,
                                "nombre": name,
                                "area": subtitle,
                                "public_id": public_id,
                            })
            else:
                print(f"  [CONNECTOR] Busqueda retorno {r.status_code}")
                print(f"  [CONNECTOR] Body: {r.text[:500]}")

        except Exception as e:
            print(f"  [CONNECTOR] Error en busqueda: {e}")

        return results

    # ------------------------------------------------------------------ #
    # 2. ENVIAR SOLICITUD DE CONEXION CON NOTA                            #
    # ------------------------------------------------------------------ #
    def send_connection(self, profile: dict, lang: str = "es") -> bool:
        """
        Envia solicitud de conexion con nota personalizada.
        LinkedIn permite notas de hasta 300 caracteres.
        """
        member_id = profile.get("member_id", "")
        nombre = profile.get("nombre", "").split()[0] if profile.get("nombre") else "ahi"
        area = profile.get("area", "Tecnologia")

        if not member_id:
            return False

        # Elegir nota aleatoria y personalizar
        note_template = random.choice(CONNECTION_NOTES)
        # Usar nota en ingles si el perfil parece internacional
        if lang == "en":
            note_template = random.choice([n for n in CONNECTION_NOTES if n.startswith("Hi")])

        note = note_template.format(nombre=nombre, area=area)[:300]

        try:
            url = f"{self.BASE_URL}/voyager/api/growth/normInvitations"
            payload = {
                "emberEntityName": "growth/invitation/norm-invitation",
                "invitee": {
                    "com.linkedin.voyager.growth.invitation.InviteeProfile": {
                        "profileId": member_id,
                    }
                },
                "trackingId": self._tracking_id(),
                "message": note,
            }
            headers = {**self.session.headers, "Content-Type": "application/json"}
            r = self.session.post(url, json=payload, headers=headers, timeout=12)

            if r.status_code in (200, 201):
                self.already_connected.add(member_id)
                self.connected.append({
                    "nombre": profile.get("nombre"),
                    "area": area,
                    "member_id": member_id,
                })
                return True
            elif r.status_code == 400:
                # Ya conectado o perfil restringido
                self.already_connected.add(member_id)
                return False
            else:
                print(f"  [CONNECTOR] Respuesta {r.status_code} para {nombre}")
                return False

        except Exception as e:
            print(f"  [CONNECTOR] Error enviando conexion a {nombre}: {e}")
            return False

    def _tracking_id(self) -> str:
        import base64
        return base64.b64encode(os.urandom(16)).decode("utf-8")

    # ------------------------------------------------------------------ #
    # 3. PIPELINE COMPLETO — 50 reclutadores                              #
    # ------------------------------------------------------------------ #
    def run_weekly_connections(self, target: int = 50) -> dict:
        """
        Ciclo semanal: busca y conecta con hasta `target` reclutadores de Data/AI.
        Distribuye las busquedas entre multiples keywords para mayor cobertura.
        """
        stats = {"sent": 0, "skipped": 0, "failed": 0, "profiles": []}
        print(f"\n[CONNECTOR] Objetivo: {target} conexiones con reclutadores Data/AI")
        print(f"[CONNECTOR] Ya conectados historicamente: {len(self.already_connected)}")

        for search in RECRUITER_SEARCHES:
            if stats["sent"] >= target:
                break

            keywords = search["keywords"]
            print(f"\n[CONNECTOR] Buscando: '{keywords}'...")
            profiles = self.search_recruiters(keywords, max_results=8)
            print(f"  -> {len(profiles)} nuevos perfiles encontrados")

            for profile in profiles:
                if stats["sent"] >= target:
                    break

                nombre = profile.get("nombre", "?")
                area = profile.get("area", "")

                # Detectar idioma por el area/titulo
                lang = "en" if any(
                    w in area.lower() for w in ["recruiter", "hiring", "talent", "acquisition"]
                ) else "es"

                print(f"  [->] Conectando con {nombre} ({area[:50]})...")
                ok = self.send_connection(profile, lang=lang)

                if ok:
                    stats["sent"] += 1
                    stats["profiles"].append({"nombre": nombre, "area": area})
                    print(f"  [OK] Conexion enviada ({stats['sent']}/{target})")
                else:
                    stats["failed"] += 1

                # Pausa anti-deteccion: 20-45 segundos entre solicitudes
                wait = random.randint(20, 45)
                print(f"  [->] Esperando {wait}s...")
                time.sleep(wait)

        # Guardar log
        self._save_log()

        print(f"\n[CONNECTOR] Resultado: {stats['sent']} conexiones enviadas")
        print(f"[CONNECTOR] Total historico: {len(self.already_connected)} reclutadores contactados")
        return stats
