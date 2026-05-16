import os
import json
from src.config import Config

class CoverLetterGenerator:
    def __init__(self):
        self.cv_data = self._load_cv()
        
    def _load_cv(self) -> dict:
        if os.path.exists(Config.CV_PATH):
            with open(Config.CV_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def generate_for_job(self, job: dict) -> str:
        """
        Genera una Cover Letter en base al CV JSON y los detalles del trabajo.
        (Versión de plantilla inicial. Lista para conectar a OpenAI/Gemini)
        """
        if not self.cv_data:
            return "Error: CV JSON no encontrado."
            
        nombre = self.cv_data.get('personal_info', {}).get('nombre', 'Erick Flores')
        titulo_cv = self.cv_data.get('personal_info', {}).get('titulo', 'Data Scientist')
        
        # Plantilla inteligente basada en variables
        letter = f"""# Cover Letter for {job.get('title')} at {job.get('company')}

Dear Hiring Manager at {job.get('company')},

I am writing to express my strong interest in the **{job.get('title')}** position. As an **{titulo_cv}**, I bring a unique blend of Economics background and advanced Data Science skills, particularly in Python, Machine Learning, and API Integrations.

Throughout my career and academic journey, I have built complete end-to-end solutions, including:
- Multi-Agent Systems using MCP (Model Context Protocol).
- Algorithmic Trading predictive models with PyTorch.
- CI/CD automated pipelines and APIs via FastAPI and Docker.

My English proficiency is at a solid B2 level, allowing me to effectively communicate technical concepts and collaborate in remote international environments, while continuing to improve rapidly.

I am eager to bring my combination of technical execution (Python/SQL/ML) and business/economic understanding to {job.get('company')}. 

Thank you for your time and consideration. I have attached my resume for more details.

Best regards,
{nombre}
        """
        
        # Guardar en la carpeta
        safe_company = "".join([c for c in job.get('company', 'Company') if c.isalpha() or c.isdigit()]).rstrip()
        filename = f"{safe_company}_{job.get('title', 'Role').replace(' ', '_')[:15]}.md"
        filepath = os.path.join(Config.COVER_LETTERS_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(letter)
            
        return filepath
