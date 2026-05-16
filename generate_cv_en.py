"""
Genera el CV profesional de Erick en inglés — versión corregida con reportlab
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import os

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "CV_Erick_Flores_EN.pdf")

# ── Colores ──────────────────────────────────────────────────────────────────
DARK_BLUE   = colors.HexColor("#1A237E")
MED_BLUE    = colors.HexColor("#1565C0")
LIGHT_GRAY  = colors.HexColor("#F5F5F5")
DARK_GRAY   = colors.HexColor("#424242")
ACCENT      = colors.HexColor("#0D47A1")

def build_cv():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=letter,
        leftMargin=0.6*inch,
        rightMargin=0.6*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
    )

    styles = getSampleStyleSheet()

    # ── Estilos personalizados ────────────────────────────────────────────────
    name_style = ParagraphStyle("Name", fontSize=22, textColor=DARK_BLUE,
                                 fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
    title_style = ParagraphStyle("Title", fontSize=11, textColor=MED_BLUE,
                                  fontName="Helvetica", alignment=TA_CENTER, spaceAfter=2)
    contact_style = ParagraphStyle("Contact", fontSize=8.5, textColor=DARK_GRAY,
                                    fontName="Helvetica", alignment=TA_CENTER, spaceAfter=12)
    section_style = ParagraphStyle("Section", fontSize=11, textColor=DARK_BLUE,
                                    fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=3)
    body_style = ParagraphStyle("Body", fontSize=9, textColor=DARK_GRAY,
                                 fontName="Helvetica", spaceAfter=3, leading=13)
    bullet_style = ParagraphStyle("Bullet", fontSize=9, textColor=DARK_GRAY,
                                   fontName="Helvetica", spaceAfter=2, leading=12,
                                   leftIndent=12, firstLineIndent=-8)
    bold_label = ParagraphStyle("BoldLabel", fontSize=9, textColor=DARK_BLUE,
                                 fontName="Helvetica-Bold", spaceAfter=2)

    story = []

    # ── HEADER ────────────────────────────────────────────────────────────────
    story.append(Paragraph("ERICK REINALDO FLORES ZAMBRANO", name_style))
    story.append(Paragraph("Economist &amp; Data Scientist | AI Engineer | ML Engineer", title_style))
    story.append(Paragraph(
        "📧 eflores4006@utm.edu.ec  |  📱 +593 963951193  |  📍 Machala, Ecuador (Remote Available)<br/>"
        "🔗 linkedin.com/in/erick-flores-zambrano-69075b198  |  💻 github.com/erick007bon",
        contact_style
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=DARK_BLUE, spaceAfter=8))

    # ── PROFESSIONAL SUMMARY ──────────────────────────────────────────────────
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MED_BLUE, spaceAfter=4))
    story.append(Paragraph(
        "Economist and Data Scientist with dual academic formation (Economics + Data Science &amp; AI), "
        "specialized in the intersection of financial analysis, machine learning, and intelligent automation. "
        "Demonstrated experience building end-to-end AI solutions: from predictive models in Python "
        "(scikit-learn, PyTorch, TensorFlow) to conversational agent architectures with LLMs, "
        "API integrations, and MCP (Model Context Protocol) for multi-agent systems. "
        "Currently pursuing two simultaneous university degrees — a testament to discipline, "
        "self-directed learning, and resilience. Seeking a remote opportunity to contribute and grow.",
        body_style
    ))

    # ── KEY PROJECTS ──────────────────────────────────────────────────────────
    story.append(Paragraph("KEY PROJECTS &amp; PORTFOLIO", section_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MED_BLUE, spaceAfter=6))

    projects = [
        (
            "FCH-ARX V4 — Original Cryptographic Algorithm",
            "Python, C, NIST FIPS 180-4",
            "Designed and implemented a novel hash algorithm from scratch using ARX (Add-Rotate-XOR) operations "
            "with mathematically derived constants (Tesla 3-6-9, 26 rounds). Passed SAC-NIST test with 49.95% avalanche "
            "(SHA-256 reference: 50.02%). Speed: 185 MB/s in optimized C. Attack complexity: 2^256."
        ),
        (
            "AI Job Hunter Bot V4 — Autonomous 24/7 Agent",
            "Python, LinkedIn API, Gmail API, OpenRouter, GitHub Actions",
            "Full automation pipeline: scraping 9+ job platforms, real email verification via Hunter.io API, "
            "personalized cover letters generated with LLMs, automatic Gmail sending with CV attachment, "
            "anti-duplicate memory, and 24/7 deployment on GitHub Actions. This CV was sent using this bot."
        ),
        (
            "Algorithmic Trading with Deep Learning",
            "PyTorch, LSTM, Backtrader, MLflow, Python",
            "LSTM model for S&amp;P 500 price forecasting achieving 68% directional accuracy. Complete pipeline: "
            "data ingestion, feature engineering, momentum/mean-reversion backtesting, experiment tracking with MLflow."
        ),
        (
            "Multi-Agent System with MCP (Model Context Protocol)",
            "Python, FastAPI, Docker, LLMs, GARCH",
            "Distributed agent architecture for automated financial analysis: scraping agent (Alpha Vantage, TradingView), "
            "econometric agent (GARCH volatility models), LLM agent for executive report generation."
        ),
        (
            "ETL Data Warehouse — Star Schema",
            "Pentaho, PostgreSQL, SQL, ETL",
            "Complete ETL pipeline for an airline Data Warehouse: dimension tables (Aircraft, Route, Flight, Passenger), "
            "SQL data cleaning, transformations in Pentaho Data Integration, production-level PostgreSQL integration."
        ),
        (
            "RESTful API for Predictive Models",
            "FastAPI, Docker, Random Forest, GitHub Actions",
            "ML inference service in production: credit risk classification (Random Forest), Docker containerization, "
            "automatic Swagger documentation, pytest testing, basic CI/CD with GitHub Actions."
        ),
    ]

    for proj_name, tech, desc in projects:
        story.append(Paragraph(f"<b>{proj_name}</b>  <font color='#1565C0' size='8'>[ {tech} ]</font>", bold_label))
        story.append(Paragraph(f"• {desc}", bullet_style))
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

    # ── PROFESSIONAL EXPERIENCE ───────────────────────────────────────────────
    story.append(Paragraph("PROFESSIONAL EXPERIENCE", section_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MED_BLUE, spaceAfter=6))

    exp = [
        (
            "Commercial Advisor", "Vamoret S.A. (Palmón Group)", "Nov 2022 – Present",
            [
                "Lead a team of 3 people in customer service and operational improvement.",
                "Designed executive Power BI dashboards with real-time KPIs, RFM segmentation, and DAX forecasting — deployed in production.",
                "Automated monthly inventory reporting with Excel VBA macros, reducing processing time by 60%.",
                "Applied data analysis for pricing strategies and customer retention decisions.",
            ]
        ),
        (
            "Commercial Advisor", "Hularuss S.A. (PepsiCo)", "Oct 2018 – Mar 2021",
            [
                "Managed a portfolio of clients using data-driven strategies (Excel + Power BI).",
                "Trained new advisors in negotiation techniques and NLP (Neuro-Linguistic Programming).",
                "Implemented inventory rotation and merchandising optimization at points of sale.",
            ]
        ),
    ]
    for job_title, company, dates, bullets in exp:
        story.append(Paragraph(f"<b>{job_title}</b> — {company} <font color='#9E9E9E'>| {dates}</font>", bold_label))
        for b in bullets:
            story.append(Paragraph(f"• {b}", bullet_style))
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

    # ── BUILD ─────────────────────────────────────────────────────────────────
    doc.build(story)
    size = os.path.getsize(OUTPUT_PATH)
    print(f"[CV EN] OK - PDF generado: {OUTPUT_PATH}")
    print(f"[CV EN] Tamano: {size:,} bytes ({size/1024:.1f} KB)")

if __name__ == "__main__":
    build_cv()
