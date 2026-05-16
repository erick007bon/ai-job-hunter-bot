import http.server
import socketserver
import json
import subprocess
import os

PORT = 1337

class SyncHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/sync':
            content_length = int(self.headers['Content-Length'])
            post_data = self.read_bytes(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                li_at = data.get('li_at')
                jsessionid = data.get('jsessionid')
                
                if li_at and jsessionid:
                    print("\n[+] Recibidas cookies frescas de la Extensión de Chrome!")
                    print(f"    - JSESSIONID: {jsessionid}")
                    print("    - li_at: [OCULTO POR SEGURIDAD]")
                    
                    self.update_github_secrets(li_at, jsessionid)
                    
                    self.send_response(200)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(b'{"status": "success"}')
                else:
                    self.send_error(400, "Missing cookies in payload")
            except Exception as e:
                print(f"[-] Error: {e}")
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Not Found")

    def read_bytes(self, length):
        """Leer bytes de forma segura para Python 3"""
        return self.rfile.read(length)

    def update_github_secrets(self, li_at, jsessionid):
        print("\n[+] Actualizando GitHub Actions Secrets vía GH CLI...")
        
        try:
            # Repositorio Principal (ai-job-hunter-bot)
            subprocess.run(
                f'gh secret set LINKEDIN_LI_AT --body "{li_at}" --repo erick007bon/ai-job-hunter-bot',
                shell=True, check=True
            )
            subprocess.run(
                f'gh secret set LINKEDIN_JSESSIONID --body "{jsessionid}" --repo erick007bon/ai-job-hunter-bot',
                shell=True, check=True
            )
            
            # Repositorio Portafolio
            subprocess.run(
                f'gh secret set LINKEDIN_LI_AT --body "{li_at}" --repo erick007bon/BOT-DE-ENCONTRAR-TRABAJO',
                shell=True, check=True
            )
            subprocess.run(
                f'gh secret set LINKEDIN_JSESSIONID --body "{jsessionid}" --repo erick007bon/BOT-DE-ENCONTRAR-TRABAJO',
                shell=True, check=True
            )
            
            print("[OK] Secretos actualizados exitosamente en la nube.")
        except Exception as e:
            print(f"[ERROR] actualizando GitHub: {e}")
            print("Asegúrate de tener la herramienta 'gh' instalada y autenticada.")

if __name__ == "__main__":
    print(f"==================================================")
    print(f" [AI] AI JOB HUNTER - SERVIDOR DE SINCRONIZACION")
    print(f"==================================================")
    print(f" Escuchando en el puerto {PORT}...")
    print(f" Esperando cookies desde la Extensión de Chrome.")
    print(f" (No cierres esta ventana mientras navegues)")
    print(f"==================================================\n")
    
    with socketserver.TCPServer(("", PORT), SyncHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nApagando servidor...")
