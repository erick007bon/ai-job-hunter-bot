# 🤖 AI Job Hunter Bot

Bot autónomo que busca oportunidades de empleo remoto en Data Science, AI Engineering y Machine Learning todos los días a las 6:00 AM (Ecuador) usando GitHub Actions.

## Fuentes de Datos
- **Remotive.com** — Empleos remotos internacionales (Data, ML, AI)
- **RemoteOK** — Startups tech con trabajo 100% remoto

## Cómo funciona
1. GitHub Actions ejecuta `job_hunter.py` todos los días a las 06:00 AM Ecuador.
2. El script consulta las APIs de empleo remoto.
3. Genera un reporte Markdown con las oportunidades del día.
4. Hace commit automático del reporte al repositorio.

## Ejecutar localmente
```bash
pip install requests
python job_hunter.py
```

## Autor
**Erick Reinaldo Flores Zambrano**  
Economista & Ingeniero en Ciencia de Datos e IA  
Universidad Técnica de Manabí | Universidad de Guayaquil  
