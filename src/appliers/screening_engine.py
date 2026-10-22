"""
screening_engine.py — Motor Inteligente de Resolución de Preguntas Frecuentes (Screening Questions).
Resuelve automáticamente formularios de Easy Apply y portales ATS en español e inglés:
1. Reglas deterministas de alta precisión basadas en data/screening_answers.json.
2. Inferencia con IA (OmniRoute local en localhost:20128/v1, Gemini o OpenRouter) para opciones complejas.
3. Fallback a Telegram si la pregunta es ambigua o de bajo puntaje de confianza.
"""

import json
import os
import re
from typing import Dict, Any, List, Optional, Tuple


class ScreeningEngine:
    def __init__(self, config_path: str = "data/screening_answers.json"):
        self.config_path = config_path
        self.data = self._load_data()
        self.omniroute_url = os.environ.get("OMNIROUTE_URL", "http://localhost:20128/v1")
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "")

    def _load_data(self) -> Dict[str, Any]:
        if os.path.isfile(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ScreeningEngine] Error cargando {self.config_path}: {e}")
        return {}

    def resolve(
        self,
        question_text: str,
        input_type: str = "text",
        options: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Resuelve una pregunta de screening.
        Retorna:
            {
                "answer": str/int/bool,
                "confidence": float (0.0 a 1.0),
                "needs_manual": bool,
                "method": "rule" | "ai" | "fallback"
            }
        """
        q_norm = self._normalize(question_text)
        options = options or []

        # 1. Reglas Deterministas Directas
        rule_result = self._match_rules(q_norm, input_type, options)
        if rule_result and rule_result.get("confidence", 0) >= 0.85:
            return rule_result

        # 2. IA Fallback para preguntas no triviales o selección múltiple
        ai_result = self._resolve_with_ai(question_text, input_type, options)
        if ai_result and ai_result.get("confidence", 0) >= 0.70:
            return ai_result

        # 3. Si no hay suficiente certeza, marcar para acción manual en 1-tap
        return {
            "answer": options[0] if options else "",
            "confidence": 0.4,
            "needs_manual": True,
            "method": "needs_manual_review"
        }

    def _normalize(self, text: str) -> str:
        t = text.lower().strip()
        t = re.sub(r'[^\w\s]', ' ', t)
        return ' '.join(t.split())

    def _match_rules(self, q: str, input_type: str, options: List[str]) -> Optional[Dict[str, Any]]:
        # Años de experiencia con tecnologías específicas
        if any(w in q for w in ["años", "years", "experiencia", "experience"]):
            exp_map = self.data.get("experience_years", {})
            for tech, yrs in exp_map.items():
                if tech in q:
                    return {"answer": str(yrs), "confidence": 0.95, "needs_manual": False, "method": "rule"}
            # Si pregunta por experiencia general
            return {"answer": str(exp_map.get("default", 2)), "confidence": 0.85, "needs_manual": False, "method": "rule"}

        # Autorización legal para trabajar
        if any(w in q for w in ["autorizado", "authorized", "derecho a trabajar", "legally authorized", "permiso de trabajo"]):
            ans = "Yes" if not options else self._select_best_option(["yes", "sí", "si"], options)
            return {"answer": ans, "confidence": 0.95, "needs_manual": False, "method": "rule"}

        # Patrocinio de visa (Sponsorship)
        if any(w in q for w in ["patrocinio", "sponsorship", "require visa", "visa sponsorship"]):
            ans = "No" if not options else self._select_best_option(["no"], options)
            return {"answer": ans, "confidence": 0.95, "needs_manual": False, "method": "rule"}

        # Nivel de inglés
        if "inglés" in q or "english" in q:
            ans = self._select_best_option(["professional", "profesional", "b2", "intermedio", "avanzado", "fluent"], options) or "Professional"
            return {"answer": ans, "confidence": 0.90, "needs_manual": False, "method": "rule"}

        # Nivel de español
        if "español" in q or "spanish" in q:
            ans = self._select_best_option(["native", "nativo", "bilingual", "bilingüe"], options) or "Native"
            return {"answer": ans, "confidence": 0.95, "needs_manual": False, "method": "rule"}

        # Modalidad remota
        if any(w in q for w in ["remoto", "remote", "teletrabajo", "work from home"]):
            ans = "Yes" if not options else self._select_best_option(["yes", "sí", "si"], options)
            return {"answer": ans, "confidence": 0.90, "needs_manual": False, "method": "rule"}

        # Expectativa salarial
        if any(w in q for w in ["salario", "salary", "compensación", "compensation", "expectativa"]):
            sal = self.data.get("salary", {})
            val = str(sal.get("monthly_target_usd", 800))
            return {"answer": val, "confidence": 0.90, "needs_manual": False, "method": "rule"}

        # Disponibilidad / Notice period
        if any(w in q for w in ["disponibilidad", "incorporación", "incorporar", "incorporarte", "start date", "notice period", "empezar", "iniciar"]):
            ans = self._select_best_option(["inmediata", "immediately", "immediate", "0"], options) or "Inmediata"
            return {"answer": ans, "confidence": 0.90, "needs_manual": False, "method": "rule"}

        return None

    def _select_best_option(self, targets: List[str], options: List[str]) -> Optional[str]:
        if not options:
            return None
        for opt in options:
            opt_low = opt.lower()
            if any(t in opt_low for t in targets):
                return opt
        return options[0]

    def _resolve_with_ai(self, question: str, input_type: str, options: List[str]) -> Optional[Dict[str, Any]]:
        """Intenta inferir la mejor respuesta vía OmniRoute o Gemini."""
        prompt = f"""Eres un asistente de postulación laboral para Erick Flores Zambrano:
- Perfil: Economista (8vo sem.) e Ingeniero en Ciencia de Datos e IA (6to sem.)
- Ciudad: Machala, Ecuador
- Inglés: B2 Profesional, Español: Nativo
- Autorizado para trabajar: Sí, sin necesidad de patrocinio
- Expectativa salarial: $700 - $900 USD mensuales
- Python/SQL: 3 años de experiencia

Pregunta del reclutador: "{question}"
Tipo de entrada: {input_type}
Opciones disponibles: {options if options else 'Texto libre o numérico'}

Responde ÚNICAMENTE con la opción más adecuada o el valor exacto (sin explicaciones ni texto adicional)."""

        # Intento 1: OmniRoute local en localhost:20128
        try:
            import requests
            resp = requests.post(
                f"{self.omniroute_url}/chat/completions",
                json={
                    "model": "openrouter/free",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 50,
                    "temperature": 0.1
                },
                timeout=4
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"].strip()
                return {"answer": content, "confidence": 0.80, "needs_manual": False, "method": "omniroute_ai"}
        except Exception:
            pass

        return None
