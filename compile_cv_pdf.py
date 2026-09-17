import os
import pathlib
import shutil
from playwright.sync_api import sync_playwright

def compile_cv():
    html_src = r"c:\Users\Erick Zambrano\Desktop\linkedin\ai-job-hunter-bot\data\CV_Erick_Flores_Jefe_Mayoristas.html"
    pdf_dest1 = r"c:\Users\Erick Zambrano\Desktop\linkedin\ai-job-hunter-bot\data\CV_Erick_Flores_Jefe_Mayoristas.pdf"
    pdf_dest2 = r"c:\Users\Erick Zambrano\Desktop\linkedin\ai-job-hunter-bot\data\CV_Erick_Flores_Data_AI_Updated.pdf"
    preview_img = r"c:\Users\Erick Zambrano\Desktop\linkedin\ai-job-hunter-bot\data\cv_preview.png"
    
    html_uri = pathlib.Path(html_src).resolve().as_uri()
    print(f"Compilando desde: {html_uri}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 850, "height": 1100})
        page.goto(html_uri, wait_until="networkidle")
        page.wait_for_timeout(2000)
        
        # Generar PDF
        page.pdf(
            path=pdf_dest1,
            format="Letter",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
        )
        print(f"PDF generado: {pdf_dest1} ({os.path.getsize(pdf_dest1)} bytes)")
        
        # Generar captura de imagen
        page.screenshot(path=preview_img, full_page=True)
        print(f"Preview generado: {preview_img}")
        
        browser.close()
        
    try:
        shutil.copyfile(pdf_dest1, pdf_dest2)
        print(f"PDF copiado a: {pdf_dest2}")
    except Exception as e:
        print(f"Nota copia a pdf_dest2: {e}")

if __name__ == "__main__":
    compile_cv()
