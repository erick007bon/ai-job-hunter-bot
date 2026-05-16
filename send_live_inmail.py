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
        nota_ia = (
            f"Hi {nombre.split()[0]}, I saw you recruit for AI/Data roles. "
            "I'm an AI Engineer & Data Scientist. Built a crypto algorithm (NIST standard) "
            "and autonomous LLM agents. Looking for remote opportunities. Let's connect! github.com/erick007bon"
        )
        print(f"    Mensaje: '{nota_ia}'\n")
        
        print("[4] ENVIANDO SOLICITUD DE CONEXION A LA API DE LINKEDIN...")
        
        # Enviar directamente usando la logica del conector pero con nuestra nota custom
        url = f"{connector.BASE_URL}/voyager/api/growth/normInvitations"
        payload = {
            "emberEntityName": "growth/invitation/norm-invitation",
            "invitee": {
                "com.linkedin.voyager.growth.invitation.InviteeProfile": {
                    "profileId": member_id,
                }
            },
            "trackingId": connector._tracking_id(),
            "message": nota_ia,
        }
        headers = {**connector.session.headers, "Content-Type": "application/json"}
        r = connector.session.post(url, json=payload, headers=headers, timeout=12)
        
        if r.status_code in (200, 201):
            print(f"✅ ¡EXITO ABSOLUTO! Solicitud y mensaje entregados a {nombre} en LinkedIn.")
            # Lo marcamos como contactado
            connector.already_connected.add(member_id)
            connector._save_log()
        elif r.status_code == 400:
            print(f"⚠️ El perfil de {nombre} tiene restricciones o ya enviaste solicitud antes.")
        else:
            print(f"❌ Error HTTP {r.status_code}: {r.text}")
            
    except Exception as e:
        print(f"Error en la prueba: {e}")

if __name__ == "__main__":
    send_demo_message()
