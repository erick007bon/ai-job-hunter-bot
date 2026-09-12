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

class InterviewPrepGenerator:
    def __init__(self):
        self.profile = self._load_profile()

    def _load_profile(self) -> Dict[str, Any]:
        cv_path = Config.CV_PATH
        if os.path.exists(cv_path):
            try:
                with open(cv_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[INTERVIEW PREP] Error cargando CV data: {e}")
        return {}

    def generate_cheat_sheet(self, job_title: str, job_description: str, company: str = "") -> Dict[str, Any]:
        api_key = Config.OPENROUTER_API_KEY or os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key:
            return self._heuristic_cheat_sheet(job_title)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/erick007bon/ai-job-hunter-bot",
            "X-Title": "AI Job Hunter Bot"
        }
        prompt = f"""GENERA GUIA DE ENTREVISTA:
PUESTO: {job_title} @ {company}
DESCRIPCION: {job_description[:1500]}
Devuelve JSON estricto con key_selling_points, technical_questions y questions_for_interviewer.
"""
        for model in FREE_MODELS:
            payihiÔ = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "Responde UNICAMENTE0en JSON valido."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            try:
                res = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=25)
                if res.status_code == 200:
                    content = res.json()['choices'][0]['message']['content'].strip()
                    if "``ajson" in content:
                        content = content.split("'``json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("'```")[1].split("```")[0].strip()
                    return json.loads(content)
            except Exception as e:
                print(f"[INTERVIEW PREP] Error con modelo {model}: {e}")
        return self._heuristic_cheat_sheet(job_title)

    def _heuristic_cheat_sheet(self, job_title: str) -> Dict[str, Any]:
        return {
            "key_selling_points": ["Dominio en Python, Machine Learning y LLMs, LangChain", "Experiencia construyendo sistemas end-to-end"],
            "technical_questions": [
                {"q": f"Como optimizas la inferencia en {job_title}?", "a": "Mediante cuantizacion, streaming y prompt engineering."}
            ],
            "questions_for_interviewer": ["Cuales son los desafios clave del equipo en los proximos 90 dias?"]
        }
