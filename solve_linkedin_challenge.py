"""
solve_linkedin_challenge.py
Ejecutar UNA VEZ en el servidor para verificar el dispositivo en LinkedIn.
Después de esto, linkedin-api funciona sin pedir verificación.

Uso:
    python solve_linkedin_challenge.py
"""
import os
import sys
import requests

EMAIL    = "adanrivas6655@gmail.com"
PASSWORD = "<CAMBIADA_POR_SEGURIDAD>"

LI_LOGIN_URL     = "https://www.linkedin.com/uas/login"
LI_SUBMIT_URL    = "https://www.linkedin.com/uas/login-submit"
LI_CHALLENGE_URL = "https://www.linkedin.com/checkpoint/challenge/verify"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-EC,es;q=0.9,en;q=0.8",
}

def main():
    session = requests.Session()
    session.headers.update(HEADERS)

    # ── Paso 1: Obtener csrf token del login ──────────────────────────
    print("[1/3] Conectando a LinkedIn...")
    resp = session.get(LI_LOGIN_URL)
    
    # Extraer CSRF token
    csrf = ""
    if "loginCsrfParam" in resp.text:
        start = resp.text.find('name="loginCsrfParam" value="') + len('name="loginCsrfParam" value="')
        end   = resp.text.find('"', start)
        csrf  = resp.text[start:end]

    if not csrf:
        # Intentar otro formato
        for line in resp.text.split("\n"):
            if "loginCsrfParam" in line and "value" in line:
                parts = line.split('value="')
                if len(parts) > 1:
                    csrf = parts[1].split('"')[0]
                    break

    print(f"   CSRF token: {csrf[:20]}..." if csrf else "   ⚠️ No se encontró CSRF token")

    # ── Paso 2: Enviar credenciales ───────────────────────────────────
    print("[2/3] Enviando credenciales...")
    login_data = {
        "session_key":        EMAIL,
        "session_password":   PASSWORD,
        "loginCsrfParam":     csrf,
        "trk":                "guest_homepage-basic_nav-header-signin",
    }
    resp2 = session.post(LI_SUBMIT_URL, data=login_data, allow_redirects=True)

    print(f"   URL tras login: {resp2.url}")

    # ── Paso 3: Verificar si hay challenge ─────────────────────────────
    if "checkpoint" in resp2.url or "challenge" in resp2.url:
        print("\n⚠️ LinkedIn pide verificación de dispositivo.")
        print("   Revisa tu email (adanrivas6655@gmail.com) — LinkedIn envió un código.")
        pin = input("\n👉 Ingresa el código de verificación de 6 dígitos: ").strip()

        # Enviar PIN
        verify_data = {
            "pin":   pin,
            "isTrackingCookie": False,
        }
        resp3 = session.post(LI_CHALLENGE_URL, data=verify_data, allow_redirects=True)
        print(f"   URL tras verificación: {resp3.url}")

        if "feed" in resp3.url or "mynetwork" in resp3.url or resp3.status_code == 200:
            print("\n✅ Verificación exitosa!")
        else:
            print(f"\n❌ Verificación falló. Status: {resp3.status_code}")
            print("   Prueba ejecutando el script de nuevo.")
            sys.exit(1)

    elif "feed" in resp2.url or resp2.status_code == 200:
        print("   ✅ Login directo sin challenge!")
    else:
        print(f"   ⚠️ Respuesta inesperada: {resp2.status_code} - {resp2.url}")

    # ── Paso 4: Guardar cookies en .env ───────────────────────────────
    li_at      = session.cookies.get("li_at", "")
    jsessionid = session.cookies.get("JSESSIONID", "").strip('"').replace("ajax:", "")

    if li_at:
        print("\n[3/3] Guardando cookies en .env...")
        
        env_path = ".env"
        with open(env_path, "r") as f:
            lines = f.readlines()

        lines = [l for l in lines if not l.startswith("LINKEDIN_LI_AT=") and not l.startswith("LINKEDIN_JSESSIONID=")]
        lines.append(f'LINKEDIN_LI_AT="{li_at}"\n')
        lines.append(f'LINKEDIN_JSESSIONID="ajax:{jsessionid}"\n')

        with open(env_path, "w") as f:
            f.writelines(lines)

        print(f"   li_at guardado: {li_at[:30]}...")
        print(f"   JSESSIONID guardado: ajax:{jsessionid[:20]}...")
        print("\n🎉 ¡Listo! Ahora ejecuta: python main_v6.py")
    else:
        print("\n❌ No se encontraron cookies. Intenta de nuevo.")
        print(f"   Cookies disponibles: {dict(session.cookies)}")


if __name__ == "__main__":
    main()
