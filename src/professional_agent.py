"""Agente de Mejora Continua Profesional — tracking + sugerencias CV/perfil."""
class ProfessionalAgent:
    def __init__(self):
        self.applications = 0
        self.suggestions = []

    def track_postulation(self, job_title: str, company: str) -> dict:
        self.applications += 1
        return {"job": job_title, "company": company, "count": self.applications}

    def generate_suggestion(self, profile_data: dict) -> str:
        # Sugerencia simple basada en datos del candidato
        if profile_data.get("projects") < 3:
            return "Añadir proyecto insignia con métricas cuantificadas (mAP, NIST, etc.)"
        return "Perfil actualizado; optimizar palabras clave ATS para roles remotos LATAM"
