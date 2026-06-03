import os
import re
from playwright.sync_api import sync_playwright
from src.config import Config

class DynamicCVGenerator:
    """Generates a dynamic ATS-friendly PDF CV tailored to the job description."""
    
    def __init__(self):
        self.template_path = os.path.join(Config.BASE_DIR, "premium_ats_template.html")
    
    def generate_tailored_pdf(self, job: dict, summary_text: str = None) -> str:
        """
        Takes the HTML template, optionally injects a tailored summary,
        and generates a PDF using Playwright.
        Returns the path to the generated PDF.
        """
        # 1. Read the HTML template
        with open(self.template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        # 2. Inject tailored summary if provided
        if summary_text:
            # We look for the exact <div class="summary"> block to replace its content
            # A simple regex substitution to replace the content inside the summary div
            pattern = re.compile(r'(<div class="summary">)(.*?)(</div>)', re.DOTALL)
            html_content = pattern.sub(r'\1\n        ' + summary_text + r'\n      \3', html_content)
        
        # 3. Create a temporary HTML file
        temp_html_path = os.path.join(Config.DATA_DIR, "temp_cv.html")
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # 4. Generate PDF path
        safe_company = "".join([c for c in job.get('company', 'Company') if c.isalnum() or c == '_'])[:20]
        pdf_filename = f"CV_Erick_Flores_{safe_company}.pdf"
        pdf_path = os.path.join(Config.DATA_DIR, pdf_filename)
        
        # 5. Use Playwright to render the HTML to PDF
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Load the local HTML file
            file_url = f"file:///{os.path.abspath(temp_html_path).replace(chr(92), '/')}"
            page.goto(file_url, wait_until="networkidle")
            
            # Generate the PDF (Background graphics true to keep the blue lines)
            page.pdf(
                path=pdf_path,
                format="A4",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
            )
            browser.close()
            
        # Clean up temp HTML
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
            
        return pdf_path
