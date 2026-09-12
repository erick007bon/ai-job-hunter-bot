import os
import json
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from src.config import Config

DARK_BLUE = colors.HexColor("#1A237E")
MED_BLUE  = colors.HexColor("#1565C0")
DARK_GRAY = colors.HexColor("#424242")

class TailoredCVGenerator:
    def __init__(self):
        self.profile = self._load_profile()

    def _load_profile(self) -> Dict[str, Any]:
        cv_path = Config.CV_PATH
        if os.path.exists(cv_path):
            try:
                with open(cv_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[CV GENERATOR] Error cargando base CV: {e}")
        return {}

    def generate_tailored_pdf(self, job_title: str, job_keywords: List[str], output_filename: str = "") -> str:
        if not output_filename:
            safe_title = "".join(c for c in job_title if c.isalnum() or c in (' ', '_', '-')).rstrip()
            output_filename = f"CV_Erick_Flores_{safe_title.replace(' ', '_')}.pdf"
        
        base_dir = os.path.dirname(Config.CV_PATH)
        output_path = os.path.join(base_dir, output_filename)
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=0.6*inch,
            rightMargin=0.6*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        styles = getSampleStyleSheet()
        name_style = ParagraphStyle("Name", fontSize=20, leading=24, textColor=DARK_BLUE, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
        subtitle_style = ParagraphStyle("SubTitle", fontSize=11, leading=14, textColor=MED_BLUE, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=8)
        contact_style = ParagraphStyle("Contact", fontSize=9, leading=12, textColor=DARK_GRAY, fontName="Helvetica", alignment=TA_CENTER, spaceAfter=10)
        h1_style = ParagraphStyle("Heading1", fontSize=12, leading=15, textColor=DARK_BLUE, fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3)
        body_style = ParagraphStyle("Body", fontSize=9.5, leading=13, textColor=DARK_GRAY, fontName="Helvetica", spaceAfter=4)

        story = []

        # Encabezado
        info = self.profile.get("personal_info", {})
        story.append(Paragraph(info.get("nombre", "Erick Reinaldo Flores Zambrano").upper(), name_style))
        story.append(Paragraph(f"SPECIALIZED ATS RESUME: {job_title.upper()}", subtitle_style))
        
        contact_text = f"{info.get('email', '')} | {info.get('telefono', '')} | {info.get('ubicacion', '')} | {info.get('linkedin', '')}"
        story.append(Paragraph(contact_text, contact_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=DARK_BLUE, spaceAfter=10))

        # Perfil Profesional Adaptado
        story.append(Paragraph("PROFESSIONAL SUMMARY", h1_style))
        summary_text = self.profile.get("perfil_profesional", "")
        if job_keywords:
            kw_str = ", ".join(job_keywords[:4])
            summary_text += f" Specialized in aligning technological solutions with high-impact targets such as {kw_str}."
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 8))

        # Skills Adaptados
        story.append(Paragraph("TECHNICAL & CORE SKILLS", h1_style))
        skills_dict = self.profile.get("skills", {})
        skills_lines = []
        for cat, item_list in skills_dict.items():
            if isinstance(item_list, list):
                skills_lines.append(f"<b>{cat.capitalize()}:</b> {', '.join(item_list)}")
        story.append(Paragraph("<br/>".join(skills_lines), body_style))
        story.append(Spacer(1, 8))

        # Experiencia
        story.append(Paragraph("RELEVANT EXPERIENCE", h1_style))
        exp_list = self.profile.get("experiencia_destacada", [])
        for exp in exp_list:
            role_text = f"<b>{exp.get('rol', '')}</b> | {exp.get('empresa', '')} ({exp.get('periodo', '')})"
            story.append(Paragraph(role_text, body_style))
            desc = exp.get("descripcion", "")
            story.append(Paragraph(f"- {desc}", body_style))
            story.append(Spacer(1, 4))

        doc.build(story)
        print(f"[CV GENERATOR] CV a la medida generado exitosamente en: {output_path}")
        return output_path
