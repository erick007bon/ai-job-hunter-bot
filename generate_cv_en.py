"""
Genera el CV profesional de Erick en ingles - Version Adaptativa por Puesto
Uso:
  python generate_cv_en.py                    # CV generico (ML Engineer)
  python generate_cv_en.py "Data Engineer"    # CV orientado al rol
  python generate_cv_en.py "Business Analyst" # CV orientado al rol
  python generate_cv_en.py "Store Manager"    # Activa experiencia Vasari Mozioni
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.config import Config

# ---- Role detection ----
ROLE_PROFILES = {
    "data_engineer": ["data engineer","etl","pipeline","warehouse","spark","airflow","dbt","snowflake"],
    "ml_engineer":   ["machine learning","ml engineer","deep learning","ai engineer","nlp","llm","pytorch","tensorflow","computer vision"],
    "data_analyst":  ["data analyst","business analyst","bi ","power bi"," analyst","reporting","analytics","business intelligence"],
    "finance":       ["economist","finance","financial analyst","quant","trading","econometrics","risk","fintech"],
    "commercial":    ["commercial","sales","store manager","retail","jefe de tienda","gerente","supervisor","customer success"],
}

def detect_role(job_title):
    title_lower = job_title.lower()
    for role, keywords in ROLE_PROFILES.items():
        if any(kw in title_lower for kw in keywords):
            return role
    return "ml_engineer"

# ---- Dynamic summaries per role ----
SUMMARIES = {
    "ml_engineer": (
        "Economist and AI/ML Engineer with dual academic formation, "
        "specialized in end-to-end intelligent systems: predictive models (PyTorch, TensorFlow, scikit-learn), "
        "LLM-powered agents, and API-driven automation. Developed FCH-ARX V4, a novel hash algorithm that "
        "passed NIST SAC validation, and an autonomous 24/7 job-hunting agent deployed on cloud. "
        "Seeking a remote ML/AI engineering role."
    ),
    "data_engineer": (
        "Economist and Data Engineer with dual academic background, specialized in ETL pipelines, "
        "SQL-based Data Warehouses (Star Schema, PostgreSQL), and automation with Python. "
        "Built production ETL systems in Pentaho plus PostgreSQL, REST APIs in FastAPI/Docker, "
        "and CI/CD pipelines with GitHub Actions. Seeking a remote Data Engineering role."
    ),
    "data_analyst": (
        "Economist and Data Analyst with expertise in business intelligence, SQL, Power BI (DAX, Power Query), "
        "and Python analytics. Delivered executive dashboards with real-time KPIs and RFM segmentation. "
        "Automated Excel/VBA reporting reducing processing time by 60 pct. "
        "Seeking a remote Data Analyst or BI role to turn data into actionable insights."
    ),
    "finance": (
        "Economist and Quantitative Analyst specialized in financial modeling, time series (ARIMA, GARCH), "
        "algorithmic trading (LSTM model, 68 pct directional accuracy on SP500), and risk analysis. "
        "Built multi-agent financial systems combining LLMs and econometric models. "
        "Seeking a remote Quantitative Finance or Fintech role."
    ),
    "commercial": (
        "Commercial leader and Data-Driven Manager with 5+ years driving sales performance, team leadership, "
        "and operational excellence in retail and distribution. Led teams of 3-8 people, implemented KPI dashboards "
        "in Power BI, and automated inventory reporting (60 pct time reduction). "
        "Additionally skilled in AI and ML automation. Seeking a remote commercial or operations leadership role."
    ),
}

# ---- Vasari Mozioni experience (commercial roles only) ----
VASARI_EXPERIENCE = (
    "Store Manager", "Vasari Mozioni - Fashion Retail (Plaza)", "2021 - 2023",
    [
        "Managed day-to-day store operations: inventory, visual merchandising, and customer experience for a premium fashion brand.",
        "Led a team of 5-8 sales associates; conducted weekly performance reviews and sales coaching sessions.",
        "Implemented a demand forecasting model using Excel to reduce stockouts by approximately 30 pct.",
        "Achieved top-3 regional store ranking for 2 consecutive quarters based on revenue targets.",
        "Coordinated with suppliers and logistics for product replenishment and promotional campaigns.",
    ]
)

# ── Colores ──────────────────────────────────────────────────────────────────
DARK_BLUE   = colors.HexColor("#1A237E")
MED_BLUE    = colors.HexColor("#1565C0")
LIGHT_GRAY  = colors.HexColor("#F5F5F5")
DARK_GRAY   = colors.HexColor("#424242")
ACCENT      = colors.HexColor("#0D47A1")

def build_cv(job_title=""):
    role = detect_role(job_title) if job_title else "ml_engineer"
    include_commercial = (role == "commercial")

    suffix = "_" + role if job_title else ""
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data",
        "CV_Erick_Flores_EN" + suffix + ".pdf"
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.6*inch,
        rightMargin=0.6*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
    )

    styles = getSampleStyleSheet()

    # ── Estilos personalizados (con leading explícito para evitar sobremontado) ─
    name_style = ParagraphStyle(
        "Name",
        fontSize=20,
        leading=25,
        textColor=DARK_BLUE,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=4
    )
    title_style = ParagraphStyle(
        "Title",
        fontSize=10.5,
        leading=14,
        textColor=MED_BLUE,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceBefore=2,
        spaceAfter=5
    )
    contact_style = ParagraphStyle(
        "Contact",
        fontSize=8.5,
        leading=13,
        textColor=DARK_GRAY,
        fontName="Helvetica",
        alignment=TA_CENTER,
        spaceBefore=2,
        spaceAfter=10
    )
    section_style = ParagraphStyle(
        "Section",
        fontSize=10.5,
        leading=14,
        textColor=DARK_BLUE,
        fontName="Helvetica-Bold",
        spaceBefore=8,
        spaceAfter=3
    )
    body_style = ParagraphStyle("Body", fontSize=9, textColor=DARK_GRAY,
                                 fontName="Helvetica", spaceAfter=3, leading=13)
    bullet_style = ParagraphStyle("Bullet", fontSize=9, textColor=DARK_GRAY,
                                   fontName="Helvetica", spaceAfter=2, leading=12,
                                   leftIndent=12, firstLineIndent=-8)
    bold_label = ParagraphStyle("BoldLabel", fontSize=9, textColor=DARK_BLUE,
                                 fontName="Helvetica-Bold", spaceAfter=2)

    headlines = {
        "ml_engineer":   "Economist and AI Engineer | Machine Learning | LLM Systems",
        "data_engineer": "Economist and Data Engineer | ETL Pipelines | SQL and Python",
        "data_analyst":  "Economist and Data Analyst | Power BI | SQL | Python",
        "finance":       "Economist and Quantitative Analyst | Algorithmic Trading | ML",
        "commercial":    "Commercial Leader and Data-Driven Manager | Retail | BI | AI",
    }

    story = []

    # HEADER
    story.append(Paragraph("ERICK REINALDO FLORES ZAMBRANO", name_style))
    story.append(Paragraph(headlines.get(role, headlines["ml_engineer"]), title_style))
    story.append(Paragraph(
        "Email: " + Config.EMAIL_SENDER + "  |  Machala, Ecuador (Remote Available)<br/>"
        "LinkedIn: linkedin.com/in/erick-flores-zambrano-69075b198  |  GitHub: github.com/erick007bon",
        contact_style
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=DARK_BLUE, spaceAfter=8))

    # PROFESSIONAL SUMMARY (adaptive)
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MED_BLUE, spaceAfter=4))
    story.append(Paragraph(SUMMARIES[role], body_style))

    # KEY PROJECTS (role-prioritized)
    story.append(Paragraph("KEY PROJECTS AND PORTFOLIO", section_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MED_BLUE, spaceAfter=6))

    all_projects = [
        ("FCH-ARX V4 - Original Cryptographic Algorithm",
         "Python, C, NIST FIPS 180-4",
         "Novel hash algorithm from scratch using ARX (Add-Rotate-XOR) with 26 rounds. "
         "Passed SAC-NIST: 49.95 pct avalanche (SHA-256 ref: 50.02 pct). Speed: 185 MB/s. Complexity: 2^256.",
         ["ml_engineer", "data_engineer"]),
        ("AI Job Hunter Bot V7 - Autonomous 24/7 Agent",
         "Python, LinkedIn API, Gmail API, OpenRouter, GitHub Actions",
         "Full automation: scraping 9+ job platforms, LLM cover letters, Gmail with CV, "
         "anti-duplicate memory, 24/7 cloud deployment. This CV was sent using this bot.",
         ["ml_engineer", "data_engineer", "commercial"]),
        ("Algorithmic Trading with Deep Learning",
         "PyTorch, LSTM, Backtrader, MLflow",
         "LSTM model for SP500: 68 pct directional accuracy. Full pipeline with backtesting and MLflow tracking.",
         ["ml_engineer", "finance"]),
        ("Multi-Agent Financial Analysis System (MCP)",
         "Python, FastAPI, Docker, LLMs, GARCH",
         "Distributed agents: data scraping (Alpha Vantage), GARCH volatility models, LLM report generation.",
         ["ml_engineer", "data_engineer", "finance"]),
        ("ETL Data Warehouse - Star Schema",
         "Pentaho, PostgreSQL, SQL, ETL",
         "Full ETL pipeline for airline DWH: dimension tables, SQL cleaning, Pentaho transformations, PostgreSQL.",
         ["data_engineer", "data_analyst"]),
        ("Power BI Executive Dashboard - Retail KPIs",
         "Power BI, DAX, Power Query, Excel VBA",
         "Real-time KPI dashboards with RFM segmentation in production. Excel VBA cut reporting time by 60 pct.",
         ["data_analyst", "commercial", "finance"]),
        ("RESTful ML Inference API",
         "FastAPI, Docker, Random Forest, GitHub Actions",
         "Credit risk classification service: Docker, Swagger docs, pytest, CI/CD with GitHub Actions.",
         ["data_engineer", "ml_engineer"]),
    ]

    priority = [p for p in all_projects if role in p[3]]
    rest     = [p for p in all_projects if role not in p[3]]
    selected = (priority + rest)[:5]

    for proj_name, tech, desc, _ in selected:
        story.append(Paragraph("<b>" + proj_name + "</b>  <font color='#1565C0' size='8'>[" + tech + "]</font>", bold_label))
        story.append(Paragraph("- " + desc, bullet_style))
        story.append(Spacer(1, 3))

    # ── TECHNICAL SKILLS ──────────────────────────────────────────────────────
    story.append(Paragraph("TECHNICAL SKILLS", section_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MED_BLUE, spaceAfter=6))

    skills_data = [
        ["AI / ML", "Python (expert), scikit-learn, PyTorch, TensorFlow, LLMs, Prompt Engineering, Hugging Face"],
        ["Data Engineering", "SQL (advanced), PostgreSQL, ETL Pipelines, Pentaho, Airflow (concepts), Spark (concepts)"],
        ["MLOps / DevOps", "FastAPI, Docker, REST APIs, GitHub Actions CI/CD, MLflow, Git"],
        ["Finance / Econometrics", "Time Series (ARIMA, GARCH), Panel Data, Causal Inference, VaR, Backtesting"],
        ["Business Intelligence", "Power BI (DAX, Power Query), Excel VBA, Data Storytelling, SQL Server"],
        ["Languages", "Spanish (Native), English (B2 — technical reading/writing proficient)"],
    ]
    for label, value in skills_data:
        story.append(Paragraph(f"<b>{label}:</b>  {value}", body_style))

    # PROFESSIONAL EXPERIENCE (Vasari Mozioni added for commercial roles)
    story.append(Paragraph("PROFESSIONAL EXPERIENCE", section_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MED_BLUE, spaceAfter=6))

    base_exp = [
        (
            "Commercial Advisor", "Vamoret S.A. (Palmon Group)", "Nov 2022 - Present",
            [
                "Lead a team of 3 people in customer service and operational improvement.",
                "Designed executive Power BI dashboards with real-time KPIs, RFM segmentation, and DAX forecasting.",
                "Automated monthly inventory reporting with Excel VBA macros - 60 pct time reduction.",
                "Applied data analysis for pricing strategies and customer retention decisions.",
            ]
        ),
        (
            "Commercial Advisor", "Hularuss S.A. (PepsiCo)", "Oct 2018 - Mar 2021",
            [
                "Managed a portfolio of clients using data-driven strategies (Excel + Power BI).",
                "Trained new advisors in negotiation techniques and NLP (Neuro-Linguistic Programming).",
                "Implemented inventory rotation and merchandising optimization at points of sale.",
            ]
        ),
    ]

    exp_list = ([VASARI_EXPERIENCE] + base_exp) if include_commercial else base_exp

    for job_title_exp, company, dates, bullets in exp_list:
        story.append(Paragraph("<b>" + job_title_exp + "</b> - " + company + " <font color='#9E9E9E'>| " + dates + "</font>", bold_label))
        for b in bullets:
            story.append(Paragraph("- " + b, bullet_style))
        story.append(Spacer(1, 4))

    # ── EDUCATION ─────────────────────────────────────────────────────────────
    story.append(Paragraph("EDUCATION", section_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MED_BLUE, spaceAfter=4))
    story.append(Paragraph(
        "<b>B.Eng. Data Science &amp; Artificial Intelligence</b> — Universidad de Guayaquil &nbsp; "
        "<font color='#9E9E9E'>| 2023 – Present (4th semester)</font>", bold_label))
    story.append(Paragraph(
        "<b>B.A. Economics</b> — Universidad Técnica de Manabí (UTM) &nbsp; "
        "<font color='#9E9E9E'>| 2021 – Present (7th semester, online)</font>", bold_label))
    story.append(Paragraph(
        "★ Managing two simultaneous university degrees remotely — demonstrates exceptional time management, "
        "self-discipline, and commitment to continuous learning.", body_style))

    # ── CERTIFICATIONS ────────────────────────────────────────────────────────
    story.append(Paragraph("CERTIFICATIONS", section_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MED_BLUE, spaceAfter=4))
    certs = [
        "Python for Finance &amp; Algorithmic Trading — Udemy (40h)",
        "SQL for Big Data — IBM (40h)",
        "Deep Learning Specialization — Coursera (in progress)",
        "LLMs &amp; Prompt Engineering — DeepLearning.AI (in progress)",
        "Digital Marketing &amp; Web Analytics — Google Activate (50h)",
        "Power BI for Data Analysis — Universidad de Guayaquil",
    ]
    for cert in certs:
        story.append(Paragraph(f"• {cert}", bullet_style))

    # BUILD
    doc.build(story)
    size = os.path.getsize(output_path)
    print("[CV EN] OK - PDF generado: " + output_path)
    print("[CV EN] Rol detectado: " + role)
    print("[CV EN] Tamano: " + str(size) + " bytes (" + str(round(size/1024, 1)) + " KB)")
    return output_path

if __name__ == "__main__":
    job_title_arg = sys.argv[1] if len(sys.argv) > 1 else ""
    build_cv(job_title_arg)
