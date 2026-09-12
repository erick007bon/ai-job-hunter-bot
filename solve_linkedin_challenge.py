"""
solve_linkedin_challenge.py
Renueva las cookies de LinkedIn y las guarda en .env.
Funciona en modo NO-INTERACTIVO (cron/GitHub Actions).

Si LinkedIn pide verificación:
  - Envía alerta por Telegram con instrucciones
  - Espera hasta 10 minutos que alguien ponga el código en /tmp/linkedin_pin.txt
  - Continúa automaticamente cuando recibe el PIN

Uso manual:
    python solve_linkedin_challenge.py

Uso automático (desde refresh_auth.py):
    subprocess.run([sys.executable, "solve_linkedin_challenge.py"], ...)
"""
import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

EMAIL    = os.environ.get("LINKEDIN_EMAIL",    "tu_email@gmail.com")
PASSWORD = os.environ.get("LINKEDIN_PASSWORD", "")

LI_LOGIN_URL     = "https://www.linkedin.com/uas/login"
LI_SUBMIT_URL    = "https://www.linkedin.com/uas/login-submit"
LI_CHALLENGE_URL = "https://www.linkedin.com/checkpoint/challenge/verify"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-EC,es;q=0.9,en;q=0.8",
}

PIN_FILE = "/tmp/linkedin_pin.txt"   # En la VM GCP (Linux)


def _send_telegram(msg: str):
    """Envía mensaje por Telegram si hay token configurado."""
    token   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        try:
            print(f"  [Telegram] No configurado — mensaje: {msg[:100]}")
        except Exception:
            print("  [Telegram] No configurado")
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"},
            timeout=10,
        )
    except Exception as e:
        print(f"  [Telegram] Error: {e}")


def _wait_for_pin_noninteractive(timeout_seconds: int = 600) -> str:
    """
    Espera (no-interactivo) hasta que exista /tmp/linkedin_pin.txt con el PIN.
    Envía alerta por Telegram. Útil en cron/GitHub Actions.
    """
    _send_telegram(
        "🔑 *LinkedIn: Verificación de dispositivo requerida*\n\n"
        "LinkedIn envió un código de 6 dígitos a tu email `tu_email@gmail.com`.\n\n"
        "Para continuar, ejecuta en el servidor:\n"
        f"`echo '123456' > {PIN_FILE}`\n"
        "_(reemplaza 123456 con el código real)_\n\n"
        f"El bot esperará {timeout_seconds // 60} minutos."
    )

    print(f"\n[Challenge] Esperando PIN en {PIN_FILE} (timeout: {timeout_seconds}s)...")
    start = time.time()
    while time.time() - start < timeout_seconds:
        if os.path.exists(PIN_FILE):
            try:
                with open(PIN_FILE) as f:
                    pin = f.read().strip()
                os.remove(PIN_FILE)
                if pin and pin.isdigit() and len(pin) == 6:
                    print(f"[Challenge] PIN recibido: {pin}")
                    return pin
            except Exception:
                pass
        time.sleep(10)

    print("[Challenge] Timeout — no se recibió PIN.")
    return ""


def main():
    if not PASSWORD:
        print("[ERROR] LINKEDIN_PASSWORD no configurado en .env")
        _send_telegram(
            "❌ *LinkedIn Auto-Refresh falló*\n"
            "`LINKEDIN_PASSWORD` no está configurado en `.env`.\n"
            "Renueva las cookies manualmente."
        )
        sys.exit(1)

    session = requests.Session()
    session.headers.update(HEADERS)

    # ── Paso 1: Obtener CSRF token ────────────────────────────────────────────
    print("[1/3] Conectando a LinkedIn...")
    resp = session.get(LI_LOGIN_URL, timeout=15)

    csrf = ""
    if "loginCsrfParam" in resp.text:
        start = resp.text.find('name="loginCsrfParam" value="') + len('name="loginCsrfParam" value="')
        end   = resp.text.find('"', start)
        csrf  = resp.text[start:end]
    # Fallback: buscar con regex o usar cookie session
    if not csrf:
        import re
        m = re.search(r'name="loginCsrfParam"[^>]*value="([^"]+)"', resp.text)
        if m:
            csrf = m.group(1)
    if not csrf:
        # Ultimo fallback: cookie de sesión (LinkedIn a veces usa JSESSIONID como csrf)
        csrf = session.cookies.get("JSESSIONID", "").strip('"')

    print(f"   CSRF: {csrf[:20]}..." if csrf else "   Warning: Sin CSRF token")

    # ── Paso 2: Login ─────────────────────────────────────────────────────────
    print("[2/3] Enviando credenciales...")
    resp2 = session.post(
        LI_SUBMIT_URL,
        data={
            "session_key":      EMAIL,
            "session_password": PASSWORD,
            "loginCsrfParam":   csrf,
            "trk":              "guest_homepage-basic_nav-header-signin",
        },
        allow_redirects=True,
        timeout=15,
    )
    print(f"   URL: {resp2.url}")

    # ── Paso 3: Challenge (si existe) ─────────────────────────────────────────
    if "checkpoint" in resp2.url or "challenge" in resp2.url:
        print("\n[Challenge] LinkedIn pide verificación de dispositivo.")

        # Modo interactivo (terminal real) vs no-interactivo (cron)
        pin = _wait_for_pin_noninteractive(timeout_seconds=30)
        if not pin and sys.stdin.isatty():
            pin = input("Input: Ingresa el código de 6 dígitos: ").strip()
        if not pin:
            pin = _wait_for_pin_noninteractive(timeout_seconds=30)

        # Extraer challengeId y csrfToken del HTML del challenge
        challenge_id = ""
        csrf_token = ""
        import re
        m_ch = re.search(r'name="challengeId"[^>]*value="([^"]+)"', resp2.text)
        if m_ch:
            challenge_id = m_ch.group(1)
        m_cs = re.search(r'name="csrfToken"[^>]*value="([^"]+)"', resp2.text)
        if m_cs:
            csrf_token = m_cs.group(1)
        # Fallback a cookie JSESSIONID si no hay csrfToken explícito
        if not csrf_token:
            csrf_token = session.cookies.get("JSESSIONID", "").strip('"')

        resp3 = session.post(
            resp2.url,
            data={
                "pin": pin,
                "isTrackingCookie": False,
                "challengeId": challenge_id,
                "csrfToken": csrf_token,
            },
            allow_redirects=True,
            timeout=15,
        )
        print(f"   URL tras verificación: {resp3.url}")

        if "feed" in resp3.url or "mynetwork" in resp3.url or resp3.status_code == 200:
            print("\n[OK] Verificación exitosa!")
        else:
            print(f"\n[ERROR] Verificación falló. Status: {resp3.status_code}")
            sys.exit(1)

    elif "feed" in resp2.url or "mynetwork" in resp2.url:
        print("   [OK] Login directo sin challenge!")
    else:
        print(f"   [Warning] Respuesta inesperada: {resp2.status_code} — {resp2.url}")

    # ── Paso 4: Guardar cookies en .env ───────────────────────────────────────
    li_at      = session.cookies.get("li_at", "")
    jsessionid = session.cookies.get("JSESSIONID", "").strip('"').replace("ajax:", "")

    if not li_at:
        print("\n[ERROR] No se encontró li_at en las cookies.")
        print(f"   Cookies: {dict(session.cookies)}")
        sys.exit(1)

    print("[3/3] Guardando cookies en .env...")

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        env_path = ".env"

    with open(env_path, "r") as f:
        lines = f.readlines()

    lines = [
        l for l in lines
        if not l.startswith("LINKEDIN_LI_AT=") and not l.startswith("LINKEDIN_JSESSIONID=")
    ]
    lines.append(f'LINKEDIN_LI_AT="{li_at}"\n')
    lines.append(f'LINKEDIN_JSESSIONID="ajax:{jsessionid}"\n')

    with open(env_path, "w") as f:
        f.writelines(lines)

    print(f"   li_at: {li_at[:30]}...")
    print(f"   JSESSIONID: ajax:{jsessionid[:20]}...")
    print("\n[Done] Cookies renovadas. Ejecuta: python main_v6.py")

    _send_telegram(
        "✅ *LinkedIn: Cookies renovadas automáticamente*\n"
        "El bot continuará operando normalmente."
    )


if __name__ == "__main__":
    main()
