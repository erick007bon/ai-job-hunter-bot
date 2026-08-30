# 🧠 MISSION BRAIN — AI Job Hunter Bot V7
**Última actualización**: 2026-08-30

> **Objetivo**: Conseguir trabajo remoto 100% en Data Science / AI / ML Engineering.
> **Candidato**: Erick Flores Zambrano — Economista + Ing. en IA/Datos (Ecuador)
> **Servidor**: Google Cloud VM `job-hunter-bot`, `us-east1-c`, 24/7

---

## 🔐 CREDENCIALES COMPLETAS (para el próximo agente)

### LinkedIn
```
LINKEDIN_EMAIL="adanrivas6655@gmail.com"
LINKEDIN_PASSWORD="<CAMBIADA_POR_SEGURIDAD>"
LINKEDIN_LI_AT="..."
LINKEDIN_JSESSIONID="..."
```
> ⚠️ Las cookies `li_at` y `JSESSIONID` expiran en ~60-90 días.
> Cuando expiren: abrir LinkedIn.com en el navegador → F12 → Application → Cookies → copiar nuevas.

### Servidor GCP
```
Usuario SSH: adanrivas6655
Host: job-hunter-bot (Google Cloud VM us-east1-c)
Proyecto dir: ~/ai-job-hunter-bot
Activar venv: cd ~/ai-job-hunter-bot && source venv/bin/activate
Alias rápido: bot   (ya configurado en ~/.bashrc)
```

### Email / SMTP
```
EMAIL_USER="eflores4006@utm.edu.ec"
EMAIL_PASSWORD="<CAMBIADA_POR_SEGURIDAD>"
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

### APIs y Bots
```
OPENROUTER_API_KEY=sk-or-v1-... (en .env del servidor)
TELEGRAM_BOT_TOKEN=... (en .env del servidor)
TELEGRAM_CHAT_ID=... (en .env del servidor)
```

### GitHub
```
Repo: https://github.com/erick007bon/ai-job-hunter-bot
Branch: main
Deploy: git add -A && git commit -m "..." && git push origin main
```

---

## 🏗️ Arquitectura del Sistema (V7)

### 🔌 Acceso Remoto IA-to-Server (SSH-MCP)
Para evitar que el usuario copie y pegue comandos en la consola de Google Cloud, el siguiente paso evolutivo es conectar la instancia directamente a Antigravity usando **SSH-MCP**.
- **Ventaja**: Es el método más rápido, robusto y 100% resistente a fallos visuales (al ser nativo de terminal, no usa scraping web).
- **Cómo configurarlo (Futuro)**: 
  1. Instalar el servidor `mcp-server-ssh` en la máquina local.
  2. Proveerle la IP de Google Cloud (`35.235.240.65` o similar) y el archivo de la llave privada SSH (`.pem` o `.ppk`).
  3. Antigravity tendrá control `bash` directo sobre la instancia de producción para arreglar bugs, hacer `git pull` o reiniciar el entorno.

```
                ┌──────────────────────────────────────────┐
                │          main_v6.py  (Orquestador)       │
                └───────────────┬──────────────────────────┘
                                │
          ┌─────────────────────┼────────────────────────┐
          │                     │                        │
   ┌──────▼──────┐    ┌─────────▼──────┐     ┌──────────▼───────┐
   │  LINKEDIN   │    │  JOB BOARDS    │     │ LINKEDIN NETWORK  │
   │  Scraper    │    │  API Scrapers  │     │ RecruiterConnector│
   │  ~30 jobs   │    │  ~80+ jobs     │     │ 8 conexiones/run  │
   │  (API real) │    │  (APIs/RSS)    │     │ (linkedin-api)    │
   └──────┬──────┘    └─────────┬──────┘     └──────────────────-┘
          └─────────────────────┘
                      │
          ┌───────────▼────────────────────────────────────┐
          │              AUTO-POSTULACIÓN                   │
          │  1. LinkedIn Easy Apply → Voyager API POST      │
          │  2. ATS Externo (Greenhouse/Lever/Workable)     │
          │  3. Fallback → Cold-Email SMTP + CV adjunto     │
          └───────────┬────────────────────────────────────┘
```

---

## 📦 Estado Real de Módulos

| Módulo | Archivo | Estado |
|--------|---------|--------|
| Orquestador | `main_v6.py` | ✅ Activo |
| LinkedIn Scraper | `src/scrapers/linkedin_scraper.py` | ✅ ~30 empleos/corrida |
| LinkedIn Client | `src/linkedin/linkedin_client.py` | ✅ Cookies auth OK |
| LinkedIn Applier | `src/appliers/linkedin_applier.py` | ✅ Easy Apply via Voyager API |
| Recruiter Connector | `src/linkedin/recruiter_connector.py` | ⚠️ Encuentra 27 perfiles, add_connection falla → fix en progreso |
| Router ATS | `src/appliers/router.py` | ✅ Activo |
| Greenhouse Applier | `src/appliers/greenhouse_applier.py` | ⚠️ No probado en VM |
| Lever Applier | `src/appliers/lever_applier.py` | ⚠️ No probado en VM |
| Workable Applier | `src/appliers/workable_applier.py` | ⚠️ No probado en VM |
| Remotive/RemoteOK/etc. | `src/scrapers/api_scrapers.py` | ✅ ~80 empleos/corrida |
| Email Extractor | `src/extractors/email_extractor.py` | ⚠️ 0 emails (no hay Hunter.io API key activa) |
| Gmail SMTP | directo | ✅ Activo |
| Telegram Notifier | `src/notifications/telegram_notifier.py` | ✅ Activo |

---

## 🔄 Flujo de Ejecución

```
Cada 4 horas (crontab en GCP VM):

1. [LINKEDIN]  30+ empleos (linkedin-api con cookies li_at+JSESSIONID)
2. [BOARDS]    80+ empleos (Remotive, RemoteOK, GetOnBoard, Jobicy, WWR, WorkingNomads)
3. [FILTRO]    MatchEngine: filtra por rol (Data/AI), nivel (no Senior), idioma
4. [DEDUP]     MemoryStore: omite ya aplicados
5. [ENRICH]    Hunter.io: busca email RRHH (0 resultados sin API key)
6. [APPLY]     LinkedIn Easy Apply (Voyager POST) → ATS externo → Cold-email SMTP
7. [NETWORK]   RecruiterConnector: 8 solicitudes de conexión a reclutadores Data/AI
8. [NOTIF]     Telegram: notificación de resultados
9. [REPORTE]   /reportes/reporte_YYYYMMDD_HHMM.md
```

---

## 🐛 Bugs Conocidos y Estado

### ✅ Resueltos
- Easy Apply: ahora usa Voyager API POST (el método `easy_apply()` no existe en linkedin-api)
- search_people: corregido campos (`name`, `jobtitle`, `urn_id` en vez de `firstName`, `lastName`, `headline`)
- Dedup recruiter: ahora usa `urn_id` como clave (antes usaba `public_id` = vacío)
- network_depths: eliminado (causaba 0 resultados)

### 🔴 Pendiente
- **Recruiter `add_connection`**: Falla con `'message'` al llamar `get_profile(urn_id)`. Fix nuevo: usar `fs_miniProfile URN` directamente (`urn:li:fs_miniProfile:{urn_id}`). Este fix está en el último commit pero aún no probado.
- **Easy Apply Voyager POST**: Detecta OK, pero el endpoint exacto puede necesitar ajuste de payload (ver logs de status code).
- **Playwright ATS externo (Greenhouse/Lever)**: No instalado en VM. Instalar: `playwright install chromium`.

### 🟡 No urgente
- GetOnBoard 404: La API pública `/api/v0/categories/ai-machine-learning/jobs` fue deprecada.
- Hunter.io: Sin API key, 0 emails encontrados. Agregar `HUNTER_API_KEY` al .env si se consigue.

---

## 📋 Comandos Útiles en el Servidor

```bash
# Entrar al proyecto (alias ya configurado)
bot

# Correr el bot en modo prueba
python main_v6.py --dry-run

# Correr el bot en modo real
python main_v6.py

# Ver últimos reportes
ls -lt reportes/ | head -5
cat reportes/reporte_YYYYMMDD_HHMM.md

# Renovar cookies LinkedIn (cuando expiren)
# 1. Ir a LinkedIn.com en navegador → F12 → Application → Cookies
# 2. Copiar li_at y JSESSIONID
sed -i '/^LINKEDIN_LI_AT=/d' .env
sed -i '/^LINKEDIN_JSESSIONID=/d' .env
echo 'LINKEDIN_LI_AT="NUEVA_COOKIE"' >> .env
echo 'LINKEDIN_JSESSIONID="ajax:NUEVO_JSESSIONID"' >> .env

# Instalar Playwright (para ATS externos como Greenhouse/Lever)
playwright install chromium
playwright install-deps
```

---

## 🗺️ Roadmap

### ✅ Completado
- [x] Scraping multi-plataforma 7 fuentes (~110 empleos/corrida)
- [x] MatchEngine + MemoryStore (anti-duplicados)
- [x] LinkedIn scraping via linkedin-api (sin anti-bot)
- [x] Autenticación LinkedIn via cookies (RequestsCookieJar)
- [x] Easy Apply: detección correcta (SimpleOnsiteApply) + POST Voyager API
- [x] Recruiter: encuentra 27+ perfiles por corrida
- [x] Cold-email SMTP con CV adjunto + cover letter IA
- [x] Telegram notifications en tiempo real
- [x] Alias `bot` en servidor para entrar rápido

### 🔴 Siguiente sesión (prioridad)
1. Probar `add_connection` con `fs_miniProfile URN` (último commit, no probado aún)
2. Verificar status code del Voyager Easy Apply POST (ver logs)
3. Instalar Playwright en VM y probar Greenhouse/Lever appliers

### 🟡 Futuro
- Workday / SAP SuccessFactors Applier
- Gmail Reply Bot (responder automáticamente a RRHH)
- Dashboard métricas en Telegram

---

## 🧠 Perfil del Candidato

```
Nombre:   Erick Flores Zambrano
Email:    eflores4006@utm.edu.ec
Teléfono: +593 096 395 1193
LinkedIn: linkedin.com/in/erick-flores-zambrano-69075b198
GitHub:   github.com/erick007bon

Formación:
  - Economía, 8vo semestre (UTM)
  - Ingeniería en Ciencia de Datos e IA, 6to semestre (UG)

Skills clave:
  Python, SQL, Power BI, Machine Learning, FastAPI, LSTM, econometría

Idiomas: Español (nativo), Inglés (B2)
Nivel target: Junior / Mid (NO Senior)
Modalidad: 100% Remoto
```
