import requests
import datetime
import os
import xml.etree.ElementTree as ET

def fetch_remotive_jobs():
    """Busca trabajos remotos en Remotive.com (Excelentes para Data/Software)"""
    url = "https://remotive.com/api/remote-jobs?category=data"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        jobs = data.get('jobs', [])
        
        # Filtrar solo los más recientes (últimos 15)
        return jobs[:15]
    except Exception as e:
        print(f"Error consultando Remotive: {e}")
        return []

def fetch_remoteok_jobs(tag="data"):
    """Extrae trabajos de RemoteOK"""
    url = f"https://remoteok.com/api?tag={tag}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        # RemoteOK API returns a legal notice as the first item, so we skip [0]
        jobs = data[1:] if len(data) > 1 else []
        return jobs[:10]
    except Exception as e:
        print(f"Error consultando RemoteOK ({tag}): {e}")
        return []

def generate_report(remotive_jobs, remoteok_jobs):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    report = f"# 💸 JOB HUNTER BOT: Reporte Diario de Ingresos - {today}\n\n"
    report += "Erick, este es tu reporte automatizado. **Tu misión es postular y cerrar tratos.**\n"
    report += "---\n\n"

    # Sección 1: Trabajos Remotos Full-Time
    report += "## 🌐 Empleos 100% Remotos Internacionales (Remotive)\n"
    report += "> *Data Science, Engineering & Machine Learning*\n\n"
    
    if remotive_jobs:
        for job in remotive_jobs:
            title = job.get('title', 'Sin título')
            company = job.get('company_name', 'Confidencial')
            salary = job.get('salary', 'No especificado')
            if not salary: salary = 'No especificado'
            link = job.get('url', '#')
            
            report += f"### 💼 [{title} @ {company}]({link})\n"
            report += f"- **Salario/Rango:** {salary}\n"
            report += f"- **Tipo:** {job.get('job_type', 'N/A')} | **Ubicación Requerida:** {job.get('candidate_required_location', 'Anywhere')}\n\n"
    else:
        report += "*No se encontraron ofertas recientes hoy.*\n\n"

    # Sección 2: RemoteOK
    report += "---\n## 🚀 Oportunidades Data Science & AI (RemoteOK)\n\n"
    
    if remoteok_jobs:
        for job in remoteok_jobs:
            title = job.get('position', 'Sin título')
            company = job.get('company', 'Confidencial')
            location = job.get('location', 'Global')
            link = job.get('url', '#')
            
            report += f"- **[{title} @ {company}]({link})** | Ubicación: {location} | ({job.get('date', '')[:10]})\n"
    else:
        report += "*Sin resultados hoy.*\n"

    report += "\n---\n"
    report += "### 💡 Próximos pasos a implementar:\n"
    report += "- [ ] Integrar API de Torre.ai y GetOnBoard para LATAM.\n"
    report += "- [ ] Añadir scraping para Becas Europeas (Erasmus/DAAD).\n"
    report += "\n*Bot ejecutado desde GitHub Actions. Mente fría, ingresos altos.*"
    return report

def main():
    print("Iniciando Job Hunter Bot...")
    
    print("Cazando en Remotive.com...")
    remotive_jobs = fetch_remotive_jobs()
    
    print("Cazando en RemoteOK (Data)...")
    remoteok_jobs = fetch_remoteok_jobs("data")
    
    print("Generando reporte maestro...")
    report_content = generate_report(remotive_jobs, remoteok_jobs)
    
    # Save the report
    os.makedirs("reportes", exist_ok=True)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join("reportes", f"oportunidades_{today}.md")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    with open("OPORTUNIDADES_HOY.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"[OK] Reporte guardado en {filepath} y OPORTUNIDADES_HOY.md")

if __name__ == "__main__":
    main()
