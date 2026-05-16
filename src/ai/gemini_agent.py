import os
import json
import requests
from typing import Dict
from src.config import Config

# OpenRouter - Motor principal (acceso gratuito a Llama, DeepSeek, Mistral)
OPENROUTER_API_KEY = Config.OPENROUTER_API_KEY
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Modelos gratuitos en OpenRouter (en orden de preferencia)
FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-31b-it:free",
    "deepseek/deepseek-v4-flash:free",
    "openrouter/free"
]

class GeminiAgent:
    """Genera Cover Letters personalizadas usando OpenRouter AI (Llama 4, DeepSeek, etc.)"""
    
    def __init__(self):
        self.cv_data = self._load_cv()

    def _load_cv(self) -> dict:
        if os.path.exists(Config.CV_PATH):
            with open(Config.CV_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _call_openrouter(self, prompt: str, model: str) -> str:
        """Llama a OpenRouter con el modelo especificado"""
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/erick007bon/ai-job-hunter-bot",
            "X-Title": "AI Job Hunter Bot"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 600,
            "temperature": 0.7
        }
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']

    def generate_cover_letter(self, job: Dict) -> str:
        """
        Genera una carta de presentacion personalizada.
        Intenta modelos gratuitos de OpenRouter en cascada.
        """
        nombre = self.cv_data.get('personal_info', {}).get('nombre', 'Erick Flores Zambrano')
        perfil = self.cv_data.get('perfil_profesional', '')
        skills = json.dumps(self.cv_data.get('skills', {}), ensure_ascii=False)
        proyectos = json.dumps(self.cv_data.get('proyectos', []), ensure_ascii=False)
        
        job_title = job.get('title', 'el cargo')
        company = job.get('company', 'la empresa')
        description = job.get('description', 'No disponible')[:2000]
        source = job.get('source', 'web')
        
        # Idioma segun fuente
        is_spanish = any(s in source.lower() for s in ['computrabajo', 'socioempleo', 'getonbrd', 'torre', 'trabajando'])
        lang_instruction = "en ESPANOL" if is_spanish else "in ENGLISH (B2 level, clear and professional, avoid native slang)"
        
        prompt = f"""You are an expert at writing job application cover letters for Data Science and AI positions.

CANDIDATE PROFILE:
- Name: {nombre}
- English level: B2 (intermediate-advanced)
- Profile: {perfil}
- Skills: {skills}
- Projects: {proyectos}

JOB POSTING:
- Title: {job_title}
- Company: {company}
- Source: {source}
- Description: {description}

INSTRUCTIONS:
Write a cover letter {lang_instruction} that:
1. Has maximum 250 words (short emails have better open rates)
2. Connects 2-3 specific skills from the CV to specific requirements in the job posting
3. Mentions 1 relevant project (Trading, MCP, Power BI, or FCH-ARX cipher if applicable)
4. Shows genuine motivation for the company/role
5. Is direct and professional (no generic phrases like "I am passionate about")
6. Ends with a clear call-to-action
7. Starts with "Estimado equipo de {company}:" (if Spanish) or "Dear {company} team," (if English)

Write ONLY the email body (no subject or signature), starting directly with the greeting.
"""
        
        # Intentar cada modelo gratuito en cascada
        for model in FREE_MODELS:
            try:
                print(f"    -> Intentando con {model.split('/')[1].split(':')[0]}...")
                result = self._call_openrouter(prompt, model)
                if result and len(result) > 50:
                    print(f"    -> OK con {model.split('/')[1].split(':')[0]}")
                    return result
            except Exception as e:
                err_str = str(e)
                if "402" in err_str:
                    print(f"    [SKIP] {model}: requiere pago, probando siguiente...")
                elif "429" in err_str or "503" in err_str:
                    print(f"    [SKIP] {model}: sin cuota/ocupado, probando siguiente...")
                else:
                    print(f"    [SKIP] {model}: {err_str[:60]}")
                continue
        
        # Fallback final: plantilla profesional de alta calidad
        print("    [FALLBACK] Usando plantilla profesional...")
        return self._fallback_template(job)

    def _fallback_template(self, job: Dict) -> str:
        """Plantilla de alta calidad cuando todos los modelos AI fallan"""
        nombre = self.cv_data.get('personal_info', {}).get('nombre', 'Erick Flores Zambrano')
        titulo = self.cv_data.get('personal_info', {}).get('titulo', 'Data Scientist & AI Engineer')
        company = job.get('company', 'the company')
        job_title = job.get('title', 'the position')
        source = job.get('source', '')
        
        is_spanish = any(s in source.lower() for s in ['computrabajo', 'socioempleo', 'getonbrd', 'torre', 'trabajando'])
        
        if is_spanish:
            return f"""Estimado equipo de {company}:

Me dirijo a ustedes para postular al cargo de {job_title}. Soy economista y cientifico de datos con doble formacion academica (Economia + Ingenieria en Ciencia de Datos e IA), con experiencia practica en Python, Machine Learning, SQL y automatizacion de procesos con IA.

Entre mis proyectos destacados: construi un sistema multi-agente con MCP (Model Context Protocol) para analisis financiero automatizado, un modelo LSTM con PyTorch para prediccion de precios con 68% de precision direccional, y una API RESTful con FastAPI y Docker en produccion con CI/CD via GitHub Actions.

Actualmente lidero el analisis de datos de ventas y la toma de decisiones estrategicas en Vamoret S.A. mediante Power BI y SQL avanzado, logrando mejoras medibles en eficiencia operativa.

Mi nivel de ingles es B2, suficiente para colaborar eficientemente en entornos remotos internacionales.

Quedo disponible para una entrevista cuando lo consideren conveniente. Adjunto mi CV para mayor detalle.

Atentamente,
{nombre}
{titulo}
adanrivas6655@gmail.com | GitHub: erick007bon"""
        else:
            return f"""Dear {company} team,

I am writing to apply for the {job_title} position. I am an Economist and Data Scientist with dual academic training (Economics + Data Science & AI Engineering), with hands-on experience in Python, Machine Learning, SQL, and AI-powered automation.

Key highlights from my work: I built a multi-agent system using MCP (Model Context Protocol) for automated financial analysis, a PyTorch LSTM model for price forecasting with 68% directional accuracy, and a production-ready FastAPI/Docker REST API with CI/CD via GitHub Actions.

In my current role at Vamoret S.A., I lead sales data analysis and strategic decision-making using Power BI and advanced SQL, achieving measurable improvements in operational efficiency.

My English proficiency is B2 level, enabling effective collaboration in international remote teams. I am actively improving and can handle written and verbal communication in professional contexts.

I would welcome the opportunity to discuss how my background aligns with your team's needs. My CV is attached.

Best regards,
{nombre}
{titulo}
adanrivas6655@gmail.com | GitHub: erick007bon"""

    def generate_email_subject(self, job: Dict) -> str:
        """Genera el asunto del email"""
        return f"Application: {job.get('title', 'Position')} | Erick Flores Zambrano - Data Scientist & AI Engineer"

    def save_cover_letter(self, job: Dict, letter_text: str) -> str:
        """Guarda la carta en archivo y retorna el path"""
        safe_company = "".join([c for c in job.get('company', 'Company') if c.isalnum() or c == '_'])[:20]
        safe_title = "".join([c for c in job.get('title', 'Role') if c.isalnum() or c == '_'])[:20]
        filename = f"{safe_company}_{safe_title}.md"
        filepath = os.path.join(Config.COVER_LETTERS_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Cover Letter - {job.get('title')} @ {job.get('company')}\n\n")
            f.write(f"**Fuente:** {job.get('source')} | **Email contacto:** {job.get('contact_email', 'N/A')}\n\n")
            f.write(f"**URL:** {job.get('url')}\n\n---\n\n")
            f.write(letter_text)
        
        return filepath
