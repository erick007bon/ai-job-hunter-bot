import os
import pathlib
from playwright.sync_api import sync_playwright
import pypdf

def compile_biess():
    base_dir = r"c:\Users\Erick Zambrano\Desktop\linkedin\ai-job-hunter-bot\data"
    html_src = os.path.join(base_dir, "CV_Erick_Flores_Pasantias_BIESS.html")
    pdf_dest = os.path.join(base_dir, "CV_Erick_Flores_Pasantias_BIESS.pdf")
    preview_img = os.path.join(base_dir, "cv_biess_preview.png")
    
    html_uri = pathlib.Path(html_src).resolve().as_uri()
    print(f"Compilando desde: {html_uri}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 850, "height": 1100})
        page.goto(html_uri, wait_until="networkidle")
        page.wait_for_timeout(2000)
        
        # Generar PDF
        page.pdf(
            path=pdf_dest,
            format="Letter",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
        )
        print(f"PDF generado: {pdf_dest} ({os.path.getsize(pdf_dest)} bytes)")
        
        # Generar captura de imagen completa
        page.screenshot(path=preview_img, full_page=True)
        print(f"Preview generado: {preview_img}")
        
        browser.close()
        
    reader = pypdf.PdfReader(pdf_dest)
    print(f"Total de paginas en PDF: {len(reader.pages)}")

if __name__ == "__main__":
    compile_biess()
