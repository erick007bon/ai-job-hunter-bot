"""
debug_linkedin_api.py — Inspecciona los payloads reales de linkedin-api.

Ejecutar UNA VEZ en el servidor para ver qué estructura exacta devuelve
LinkedIn en los campos de Easy Apply y search_people.

Uso:
    python debug_linkedin_api.py
"""
import json
import os
from dotenv import load_dotenv
load_dotenv()

from src.linkedin.linkedin_client import LinkedInClient

client = LinkedInClient()

print("=" * 60)
print("DEBUG — Payloads reales de linkedin-api")
print("=" * 60)

# ── 1. Inspectar un empleo de búsqueda ────────────────────────────────────────
print("\n[1] Búsqueda de empleos — raw de 2 items:")
try:
    raw = client.api.search_jobs(
        keywords="Data Scientist",
        location_name="Remote",
        limit=3,
        listed_at=86400,
    )
    for i, item in enumerate(raw[:2]):
        print(f"\n--- JOB {i+1}: {item.get('title', '?')} ---")
        apply_method = item.get("applyMethod", {})
        print(f"  applyMethod keys: {list(apply_method.keys())}")
        print(f"  applyMethod raw:\n{json.dumps(apply_method, indent=4, default=str)}")
        
        tracking_urn = item.get("trackingUrn", "")
        job_id = tracking_urn.split(":")[-1]
        print(f"  job_id: {job_id}")
        print(f"  title: {item.get('title')}")
        print(f"  all keys: {list(item.keys())}")
except Exception as e:
    print(f"  ERROR: {e}")

# ── 2. Inspectar get_job() para ver URL externa ───────────────────────────────
print("\n[2] get_job() — detalle de un empleo:")
try:
    raw2 = client.api.search_jobs(
        keywords="Data Engineer",
        location_name="Remote",
        limit=2,
        listed_at=86400,
    )
    if raw2:
        job_id = raw2[0].get("trackingUrn", "").split(":")[-1]
        print(f"  Inspeccionando job_id: {job_id}")
        detail = client.api.get_job(job_id)
        apply_method = detail.get("applyMethod", {})
        print(f"  applyMethod keys: {list(apply_method.keys())}")
        print(f"  applyMethod raw:\n{json.dumps(apply_method, indent=4, default=str)}")
except Exception as e:
    print(f"  ERROR: {e}")

# ── 3. Inspectar search_people() ──────────────────────────────────────────────
print("\n[3] search_people() — raw de 3 perfiles:")
try:
    people = client.api.search_people(
        keywords="data science recruiter",
        limit=3,
    )
    print(f"  Total retornado: {len(people)}")
    for i, p in enumerate(people[:2]):
        print(f"\n  --- PERSONA {i+1} ---")
        print(f"  keys: {list(p.keys())}")
        print(f"  firstName: {p.get('firstName')}")
        print(f"  lastName:  {p.get('lastName')}")
        print(f"  headline:  {p.get('headline')}")
        print(f"  publicIdentifier: {p.get('publicIdentifier')}")
        print(f"  urn_id: {p.get('urn_id')}")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "=" * 60)
print("DEBUG COMPLETO — copia y pega este output para análisis")
print("=" * 60)
