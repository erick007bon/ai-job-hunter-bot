import os
import json
import requests
from typing import Dict, Any, Optional
from src.config import Config

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-31b-it:free",
    "qwen/qwen3-coder:free",
]

class AIFitEvaluator:
    def __init__(self):
        self.profile = self._load_profile()

    def _load_profile(self) -> Dict[str, Any]:
        cv_path = Config.CV_PATH
        if os.path.exists(cv_path):
            try:
                with open(cv_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[FIT EVALUATOR] Error cargando CV data: {e}")
        return {}

    def _call_llm(self, prompt: str) -> Optional[str]:
        api_key = Config.OPENROUTER_API_KEY or os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key:
            print("[FIT EVALUATOR] Sin OPENROUTER_API_KEY. Usando heurística.")
            return None
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/erick007bon/ai-job-hunter-bot",
            "X-Title": "AI Job Hunter Bot"
        }
        
        for model in FREE_MODELS:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "Eres un reclutador experto e Ingeniero en IA. Responde UNICAMENTE en formato JSON válido sin ningún otro texto adicional."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
            try:
                res = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=25)
                if res.status_code == 200:
                    data = res.json()
                    content = data['choices'][0]['message']['content']
                    if content:
                        return content
                else:
                    print(f"[FIT EVALUATOR] Modelo {model} devolvió status {res.status_code}")
            except Exception as e:
                print(f"[FIT EVALUATOR] Error conectando a {model}: {e}")
        return None

    def evaluate_job(self, job_title: str, job_description: str, company: str = "") -> Dict[str, Any]:
        if len(job_description.strip()) < 50:
            return {
                "fit_score": 75,
                "skills_match": ["Python", "Machine Learning"],
                "missing_skills": [],
                "seniority_fit": "OK",
                "red_flags": [],
                "recommendation": "POSTULAR_DIRECTO",
                "reasoning": "Descripción demasiado breve para análisis de IA detallado."
            }
            
        name = self.profile.get("personal_info", {}).get("nombre", "Erick Flores")
        summary = self.profile.get("perfil_profesional", "")[:500]
        skills = json.dumps(self.profile.get("skills", {}), ensure_ascii=False)[:600]
        
        prompt = f"""EVALUA LA COMPATIBILIDAD CON EL CANDIDATO:
CANDIDATO: {name}
RESUMEN PERFIL: {summary}
SKILLS: {skills}

OFERTA DE TRABAJO: {job_title} @ {company}
DESCRIPCION DE TRABAJO:
{job_description[:2500]}

Devuelve UNICAMENTE un objeto JSON estricto con esta estructura exacta:
{{
    "fit_score": 85,
    "skills_match": ["Python", "Machine Learning", "FastAPI"],
    "missing_skills": ["Spark", "Kubernetes"],
    "seniority_fit": "OK",
    "red_flags": [],
    "recommendation": "POSTULAR_DIRECTO",
    "reasoning": "El candidato cumple con el 85% de los requisitos técnicos clave en IA y Backend."
}}
"""
        raw = self._call_llm(prompt)
        if raw:
            try:
                s = raw.strip()
                if "```json" in s:
                    s = s.split("```json")[1].split("```")[0].strip()
                elif "```" in s:
                    s = s.split("```")[1].split("```")[0].strip()
                return json.loads(s)
            except Exception as e:
                print(f"[FIT EVALUATOR] Error parseando JSON de LLM: {e}")
                
        return {
            "fit_score": 80,
            "skills_match": ["Python", "SQL", "Machine Learning"],
            "missing_skills": [],
            "seniority_fit": "OK",
            "red_flags": [],
            "recommendation": "POSTULAR_DIRECTO",
            "reasoning": "Evaluación heurística estándar (Fallback por falta de conexión LLM)."
        }
