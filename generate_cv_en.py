"""
Generador de CV en Ingles (PDF) - AI Job Hunter Bot
Usa reportlab para crear un PDF profesional desde cv_erick_data.json
"""
import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

CV_DATA_PATH = r"c:\Users\Erick Zambrano\Desktop\linkedin\cv\cv_erick_data.json"
OUTPUT_PATH = r"c:\Users\Erick Zambrano\Desktop\linkedin\PROYECTOS\08_gematria_torah\JOB_SEARCH_MISSION\ai-job-hunter-bot\data\CV_Erick_Flores_EN.pdf"

def load_cv():
    with open(CV_DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_cv_en():
    cv = load_cv()
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        rightMargin=1.8*cm,
        leftMargin=1.8*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    # ===================== STYLES =====================
    styles = getSampleStyleSheet()
    
    DARK_BLUE = colors.HexColor('#1a2e4a')
    ACCENT    = colors.HexColor('#2563eb')
    GRAY      = colors.HexColor('#6b7280')
    LIGHTGRAY = colors.HexColor('#f1f5f9')
    
    name_style = ParagraphStyle('Name', fontSize=22, textColor=DARK_BLUE,
                                 fontName='Helvetica-Bold', alignment=TA_LEFT,
                                 spaceAfter=2)
    title_style = ParagraphStyle('Title', fontSize=11, textColor=ACCENT,
                                  fontName='Helvetica', alignment=TA_LEFT,
                                  spaceAfter=4)
    contact_style = ParagraphStyle('Contact', fontSize=8.5, textColor=GRAY,
                                    fontName='Helvetica', alignment=TA_LEFT,
                                    spaceAfter=8)
    section_style = ParagraphStyle('Section', fontSize=11, textColor=DARK_BLUE,
                                    fontName='Helvetica-Bold', alignment=TA_LEFT,
                                    spaceBefore=10, spaceAfter=3)
    body_style = ParagraphStyle('Body', fontSize=9, textColor=colors.black,
                                 fontName='Helvetica', alignment=TA_JUSTIFY,
                                 spaceAfter=4, leading=13)
    bullet_style = ParagraphStyle('Bullet', fontSize=9, textColor=colors.black,
                                   fontName='Helvetica', leftIndent=12,
                                   spaceAfter=2, leading=13,
                                   bulletIndent=4, bulletFontName='Helvetica')
    job_title_style = ParagraphStyle('JobTitle', fontSize=10, textColor=DARK_BLUE,
                                      fontName='Helvetica-Bold', spaceAfter=1)
    job_sub_style = ParagraphStyle('JobSub', fontSize=9, textColor=ACCENT,
                                    fontName='Helvetica-Oblique', spaceAfter=2)
    
    # ===================== CONTENT =====================
    story = []
    pi = cv['personal_info']
    
    # --- HEADER ---
    story.append(Paragraph("ERICK FLORES ZAMBRANO", name_style))
    story.append(Paragraph("Economist & Data Scientist | Applied AI & Financial Analysis Specialist", title_style))
    
    contact_line = (
        f"Email: adanrivas6655@gmail.com  |  Phone: +593 963-951-193  |  "
        f"Location: Machala, Ecuador (Open to Remote)  |  "
        f"GitHub: github.com/erick6655  |  "
        f"LinkedIn: linkedin.com/in/erick-flores-zambrano-69075b198"
    )
    story.append(Paragraph(contact_line, contact_style))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT))
    
    # --- PROFESSIONAL PROFILE ---
    story.append(Paragraph("PROFESSIONAL PROFILE", section_style))
    profile_en = (
        "Economist and Data Scientist with dual academic training (Economics + Data Science & AI Engineering), "
        "specializing in the intersection of financial analysis, machine learning, and intelligent automation. "
        "Proven experience building end-to-end AI solutions: from predictive models in Python (scikit-learn, PyTorch, TensorFlow) "
        "to conversational agent architectures with LLMs, API integrations, and MCP (Model Context Protocol) for multi-agent systems. "
        "Core competencies in applied econometrics (ARIMA/GARCH time series, panel data, causal inference), "
        "MLOps (Docker, FastAPI, MLflow), and business intelligence (Power BI, advanced SQL). "
        "English level B2 — fully capable of collaborating in international remote teams."
    )
    story.append(Paragraph(profile_en, body_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHTGRAY))
    
    # --- TECHNICAL SKILLS ---
    story.append(Paragraph("TECHNICAL SKILLS", section_style))
    
    skills_table_data = [
        [Paragraph("<b>AI & Machine Learning</b>", body_style),
         Paragraph("<b>Econometrics & Finance</b>", body_style),
         Paragraph("<b>MLOps & Engineering</b>", body_style),
         Paragraph("<b>Business Intelligence</b>", body_style)],
        [
            Paragraph("LLMs & Generative AI (Hugging Face)<br/>Conversational Agents & MCP<br/>Deep Learning (PyTorch, TensorFlow)<br/>ML (scikit-learn, ensembles)<br/>Predictive modeling with Neural Nets", body_style),
            Paragraph("Time Series (ARIMA, GARCH)<br/>Panel Data & Causal Inference<br/>Risk Analysis (VaR, backtesting)<br/>Econometric modeling<br/>Financial analysis", body_style),
            Paragraph("Docker & FastAPI (REST APIs)<br/>Experiment Tracking (MLflow)<br/>GitHub Actions (CI/CD)<br/>Web Scraping (requests, BS4)<br/>MCP Architecture", body_style),
            Paragraph("Power BI (DAX, dashboards)<br/>Advanced SQL (window funcs)<br/>Advanced Excel & VBA<br/>Data Storytelling<br/>Automated Reporting", body_style),
        ]
    ]
    
    skills_table = Table(skills_table_data, colWidths=[4.4*cm, 4.4*cm, 4.4*cm, 4.4*cm])
    skills_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK_BLUE),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, LIGHTGRAY),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHTGRAY]),
    ]))
    story.append(skills_table)
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHTGRAY))
    
    # --- WORK EXPERIENCE ---
    story.append(Paragraph("WORK EXPERIENCE", section_style))
    
    exp_translations = {
        "Asesor Comercial": "Sales & Data Advisor",
        "Vendedor por catalogo": "Catalog Sales Representative",
    }
    
    for exp in cv.get('experiencia', []):
        title_en = exp_translations.get(exp.get('cargo', ''), exp.get('cargo', ''))
        story.append(Paragraph(f"{title_en} | {exp.get('empresa', '')}", job_title_style))
        story.append(Paragraph(f"{exp.get('periodo', '')} — {exp.get('ubicacion', '')}", job_sub_style))
        
        for resp in exp.get('responsabilidades', [])[:5]:
            # Translate key responsibilities
            resp_en = resp
            translations = {
                'Análisis': 'Analysis', 'datos': 'data', 'ventas': 'sales',
                'Gestión': 'Management', 'Coordinación': 'Coordination',
                'Desarrollo': 'Development', 'automatizada': 'automated',
                'clientes': 'clients', 'informes': 'reports',
                'Power BI': 'Power BI', 'estratégico': 'strategic',
                'Elaboración': 'Preparation', 'reportes': 'reports',
                'modelos': 'models', 'predicción': 'prediction',
                'portafolio': 'portfolio', 'inventarios': 'inventory',
                'metas': 'targets', 'equipo': 'team', 'supervisión': 'supervision'
            }
            for es, en in translations.items():
                resp_en = resp_en.replace(es, en)
            story.append(Paragraph(f"• {resp_en}", bullet_style))
        story.append(Spacer(1, 4))
    
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHTGRAY))
    
    # --- KEY PROJECTS ---
    story.append(Paragraph("KEY PROJECTS", section_style))
    
    projects_en = [
        {
            "name": "AI Job Hunter Bot V3",
            "desc": "Autonomous AI agent that scrapes 8+ job platforms (Ecuador + Global Remote), extracts RRHH contact emails, generates personalized cover letters using LLMs (DeepSeek, Llama-3), and automatically sends CVs via Gmail API. Built with Python, GitHub Actions (24/7 cloud automation), OAuth 2.0."
        },
        {
            "name": "MCP Multi-Agent Financial System",
            "desc": "Multi-agent system using Model Context Protocol (MCP) for automated financial analysis. Agents communicate via standardized protocol to retrieve market data, compute risk indicators, and generate investment reports. Stack: Python, FastAPI, LLMs."
        },
        {
            "name": "LSTM Algorithmic Trading Model",
            "desc": "PyTorch LSTM model for BTC/USDT price direction forecasting. Achieved 68% directional accuracy with custom loss function and backtesting framework. Deployed as REST API with FastAPI and Docker, CI/CD via GitHub Actions."
        },
        {
            "name": "FCH-ARX Cryptographic Hash (NIST SAC Certified)",
            "desc": "Original cryptographic hash algorithm achieving 49.95% avalanche effect (NIST FIPS 180-4 standard). Uses ARX (Add-Rotate-XOR) architecture with Saturn-Tesla mathematical constants. Benchmarked at 185 MB/s in C (outperforms SHA-256 on IoT ARM Cortex-M0)."
        },
    ]
    
    for proj in cv.get('proyectos', [])[:4]:
        # Use pre-translated versions if available
        name = proj.get('nombre', '')
        for p_en in projects_en:
            if any(word in name for word in p_en['name'].split()[:2]):
                story.append(Paragraph(f"<b>{p_en['name']}</b>", bullet_style))
                story.append(Paragraph(p_en['desc'], ParagraphStyle('ProjDesc', parent=body_style, leftIndent=12)))
                story.append(Spacer(1, 3))
                break
    
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHTGRAY))
    
    # --- EDUCATION ---
    story.append(Paragraph("EDUCATION", section_style))
    for edu in cv.get('educacion', []):
        titulo_en = edu.get('titulo', '').replace('Ingeniería', 'Engineering').replace('Ciencia de Datos', 'Data Science').replace('Economía', 'Economics').replace('Carrera de', 'Bachelor in')
        story.append(Paragraph(f"<b>{titulo_en}</b> — {edu.get('institucion', '')}", job_title_style))
        story.append(Paragraph(f"{edu.get('periodo', '')}", job_sub_style))
    
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHTGRAY))
    
    # --- LANGUAGES & CERTIFICATIONS ---
    story.append(Paragraph("LANGUAGES & CERTIFICATIONS", section_style))
    lang_data = [
        [Paragraph("<b>Language</b>", body_style), Paragraph("<b>Level</b>", body_style), Paragraph("<b>Notes</b>", body_style)],
        [Paragraph("Spanish", body_style), Paragraph("Native", body_style), Paragraph("Mother tongue", body_style)],
        [Paragraph("English", body_style), Paragraph("B2 (Upper-Intermediate)", body_style), Paragraph("Professional written & verbal communication in remote teams", body_style)],
    ]
    lang_table = Table(lang_data, colWidths=[3.5*cm, 5*cm, 9.2*cm])
    lang_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK_BLUE),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, LIGHTGRAY),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHTGRAY]),
    ]))
    story.append(lang_table)
    
    # ===================== BUILD PDF =====================
    doc.build(story)
    print(f"[CV EN] PDF generado: {OUTPUT_PATH}")
    return OUTPUT_PATH

if __name__ == "__main__":
    build_cv_en()
