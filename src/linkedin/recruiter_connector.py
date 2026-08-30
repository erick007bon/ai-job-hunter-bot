"""
recruiter_connector.py — Auto-conexión con reclutadores usando linkedin-api.

Reemplaza el Voyager API / GraphQL manual que fallaba con 403/redirect loops.
Usa linkedin-api que hace las mismas llamadas internas que el navegador real.
"""
import os
import time
import random
import json
import logging
from typing import Set

logger = logging.getLogger(__name__)

# Nota personalizada según idioma detectado
CONNECTION_MESSAGES = {
    "es": (
        "Hola {nombre}, soy Erick — Economista & Data Scientist buscando roles remotos "
        "en Data/AI. Me encantaría conectar y explorar si hay alguna oportunidad afín. "
        "github.com/erick007bon"
    ),
    "en": (
        "Hi {nombre}, I'm Erick — Economist & Data Scientist looking for remote "
        "Data/AI roles. Would love to connect and explore potential opportunities. "
        "github.com/erick007bon"
    ),
}

# Keywords para buscar reclutadores (3 por corrida para evitar rate-limiting)
RECRUITER_SEARCHES = [
    "data science recruiter remote",
    "AI engineer talent acquisition",
    "machine learning hiring manager",
]


class RecruiterConnector:
    """
    Busca y conecta con reclutadores de Data/AI usando linkedin-api.
    Mantiene un historial local para no repetir conexiones.
    """

    LOG_FILE = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "connector_log.json"
    )

    def __init__(self):
        self.already_connected: Set[str] = set()
        self._load_log()

    # ──────────────────────────────────────────────────────── #
    #  HISTORIAL                                               #
    # ──────────────────────────────────────────────────────── #
    def _load_log(self):
        if os.path.exists(self.LOG_FILE):
            try:
                with open(self.LOG_FILE, "r") as f:
                    data = json.load(f)
                    self.already_connected = set(data.get("sent", []))
            except Exception:
                self.already_connected = set()

    def _save_log(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.LOG_FILE)), exist_ok=True)
        with open(self.LOG_FILE, "w") as f:
            json.dump(
                {"sent": list(self.already_connected), "total": len(self.already_connected)},
                f, indent=2
            )

    # ──────────────────────────────────────────────────────── #
    #  PIPELINE PRINCIPAL                                      #
    # ──────────────────────────────────────────────────────── #
    def run_weekly_connections(self, target: int = 8) -> dict:
        """
        Busca y conecta con hasta `target` reclutadores de Data/AI.
        Usa linkedin-api — sin queryId rotante, sin 403, sin redirects.
        """
        stats = {"sent": 0, "skipped": 0, "failed": 0}

        try:
            from src.linkedin.linkedin_client import LinkedInClient
            client = LinkedInClient()
        except RuntimeError as e:
            print(f"  [CONNECTOR] ⚠️ {e}")
            return stats

        print(f"\n[CONNECTOR] Objetivo: {target} conexiones con reclutadores Data/AI")
        print(f"[CONNECTOR] Ya conectados históricamente: {len(self.already_connected)}")

        for i, keywords in enumerate(RECRUITER_SEARCHES):
            if stats["sent"] >= target:
                break

            print(f"\n[CONNECTOR] Buscando: '{keywords}'...")
            profiles = client.search_people(keywords=keywords, limit=10)

            # Filtrar ya conectados
            profiles = [
                p for p in profiles
                if p.get("public_id") not in self.already_connected
            ]
            print(f"  → {len(profiles)} nuevos perfiles encontrados")

            for profile in profiles:
                if stats["sent"] >= target:
                    break

                # Campos reales de search_people(): name, jobtitle, urn_id
                nombre    = profile.get("nombre", "")       # ya mapeado en linkedin_client
                urn_id    = profile.get("urn_id", "")
                headline  = profile.get("area", "")

                # Detectar idioma por el headline / jobtitle del perfil
                lang = "en" if any(
                    w in headline.lower()
                    for w in ["recruiter", "hiring", "talent", "acquisition", "engineer"]
                ) else "es"

                first_name = nombre.split()[0] if nombre else ""
                message = CONNECTION_MESSAGES[lang].format(nombre=first_name)

                print(f"  [->] Conectando con {nombre} ({headline[:50]})...")
                ok = client.add_connection(profile, message=message)

                if ok:
                    self.already_connected.add(public_id)
                    stats["sent"] += 1
                    print(f"  [OK] Conexión enviada ({stats['sent']}/{target})")
                else:
                    stats["failed"] += 1

            # Pausa anti-rate-limit entre búsquedas
            if i < len(RECRUITER_SEARCHES) - 1 and stats["sent"] < target:
                wait = random.randint(45, 75)
                print(f"\n[CONNECTOR] Pausa {wait}s entre búsquedas...")
                time.sleep(wait)

        self._save_log()
        print(f"\n[CONNECTOR] Resultado: {stats['sent']} conexiones enviadas")
        print(f"[CONNECTOR] Total histórico: {len(self.already_connected)} reclutadores contactados")
        return stats

    def run(self, max_connections: int = 8) -> int:
        """Método de conveniencia para llamar desde el pipeline principal."""
        stats = self.run_weekly_connections(target=max_connections)
        return stats.get("sent", 0)
