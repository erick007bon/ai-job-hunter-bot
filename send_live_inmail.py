import sys
import os

# Asegurar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.linkedin.recruiter_connector import RecruiterConnector

def send_demo_message():
    print("==================================================")
    print(" INICIANDO PRUEBA DE AUTONOMIA LINKEDIN EN VIVO")
    print("==================================================")
    
    try:
        connector = RecruiterConnector()
        print("[1] Buscando reclutadores de Inteligencia Artificial...")
        
        # Buscar alguien especifico
        profiles = connector.search_recruiters("AI Recruiter", max_results=3)
        
        if not profiles:
            print("No se encontraron perfiles. Verifica las cookies.")
            return
            
        target = profiles[0]
        nombre = target.get("nombre", "Reclutador")
        area = target.get("area", "IA")
        member_id = target.get("member_id")
        
        print(f"\n[2] OBJETIVO ENCONTRADO:")
        print(f"    Nombre: {nombre}")
        print(f"    Area: {area}")
        print(f"    ID: {member_id}")
        
        print("\n[3] REDACTANDO MENSAJE AUTONOMO...")
        
        CONNECTION_NOTES = [
            "Hi {nombre}, I saw you recruit for {area} roles. I'm an AI Engineer & Data Scientist. Built a crypto algorithm (NIST standard) and autonomous LLM agents. Looking for remote opportunities. Let's connect! github.com/erick007bon"
        ]

        print("\n[3] REDACTANDO MENSAJE AUTONOMO Y ENVIANDO...")
        for target in profiles:
            nombre = target.get('nombre', '')
            area = target.get('area', '')
            member_id = target.get('member_id', '')
            
            print(f"\nIntentando conectar con: {nombre} - {area}")
            note_template = CONNECTION_NOTES[0]
            note = note_template.format(nombre=nombre.split()[0], area=area)[:300]
            print(f"    Mensaje: '{note}'")
            
            try:
                url = f"{connector.BASE_URL}/voyager/api/growth/normInvitations"
                
                # Usar public_id preferentemente, sino usar member_id
                target_id = target.get("public_id") or member_id
                
                payload = {
                    "emberEntityName": "growth/invitation/norm-invitation",
                    "invitee": {
                        "com.linkedin.voyager.growth.invitation.InviteeProfile": {
                            "profileId": target_id,
                        }
                    },
                    "trackingId": connector._tracking_id(),
                    "message": note,
                }
                headers = {**connector.session.headers, "Content-Type": "application/json"}
                r = connector.session.post(url, json=payload, headers=headers, timeout=12)
                
                if r.status_code in (200, 201):
                    print(f"[OK] ¡EXITO ABSOLUTO! Solicitud entregada a {nombre}.")
                    connector.already_connected.add(member_id)
                    connector._save_log()
                    break  # Solo enviamos uno para la prueba
                elif r.status_code == 400:
                    print(f"[WARNING] {nombre} tiene restricciones o ya enviaste solicitud.")
                elif r.status_code == 301:
                    print(f"[SKIP] {nombre} fuera de red (HTTP 301). Saltando al siguiente...")
                else:
                    print(f"[ERROR] HTTP {r.status_code}: {r.text}")
                    
            except Exception as e:
                print(f"Error en la prueba: {e}")
            
    except Exception as e:
        print(f"Error en la prueba: {e}")

if __name__ == "__main__":
    send_demo_message()
