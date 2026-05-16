import os

class Config:
    # Perfil del candidato
    ENGLISH_LEVEL = "B2"
    TARGET_ROLES = ["Data Engineer", "Data Scientist", "AI Engineer", "ML Engineer", "Machine Learning", "Economista", "Economist", "Python Developer"]
    MAX_SENIORITY = "Mid-Level"  # Evitar Senior, Lead, Staff, Principal
    
    # Credenciales (leer de env vars en producción, fallback a valores locales)
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
    EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "eflores4006@utm.edu.ec")
    
    # LinkedIn Auth
    LINKEDIN_LI_AT = os.environ.get("LINKEDIN_LI_AT", "AQEDAS5itwwF3emOAAABng9cFRwAAAGeM2iZHFYARzSAOR0x-uGv9sVHcBBlbUmMLWWwXtcte5JvQLNLbOY13JKrj_XwuyJCpjPbOB6nloxHxoznCCkyMnHJb0vq7RpWGm0uWheLrApMTGyVag56Es_W")
    LINKEDIN_JSESSIONID = os.environ.get("LINKEDIN_JSESSIONID", '"ajax:9123054129527685968"')

    
    # Rutas
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    CV_PATH = os.path.join(DATA_DIR, "cv_erick_data.json")
    CV_PDF_PATH_ES = os.path.join(DATA_DIR, "CV_FLORES_ERICK.pdf")  # CV Espanol
    CV_PDF_PATH_EN = os.path.join(DATA_DIR, "CV_Erick_Flores_EN.pdf")  # CV Ingles
    CV_PDF_PATH = CV_PDF_PATH_ES  # Default
    REPORTS_DIR = os.path.join(BASE_DIR, "reportes")
    COVER_LETTERS_DIR = os.path.join(BASE_DIR, "cover_letters")
    
    # Control: Máx emails a enviar por día (seguridad anti-spam)
    MAX_EMAILS_PER_DAY = 10
    
    # Asegurar que las carpetas existan
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(COVER_LETTERS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
