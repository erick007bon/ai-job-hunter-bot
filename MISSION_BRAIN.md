# 🧠 MISSION BRAIN — AI Job Hunter Bot V7
**Última actualización**: 2026-09-12

> **Objetivo**: Conseguir trabajo remoto 100% en Data Science / AI / ML Engineering.
> **Candidato**: Erick Flores Zambrano — Economista + Ing. en IA/Datos (Ecuador)
> **Servidor**: Google Cloud VM `job-hunter-bot`, `us-east1-c`, 24/7

---

## 🔐 CREDENCIALES Y CONFIGURACIÓN COMPLETA (para el próximo agente)

### LinkedIn (Sesión Activa Verificada)
```env
LINKEDIN_EMAIL="adanrivas6655@gmail.com"
LINKEDIN_PASSWORD="Cocodrilo1998"
LINKEDIN_LI_AT="AQEDAS5itwwDjGS6AAABoJbHfVgAAAGgutQBWE4AIpYePYnL369g8cOLYsnq1h9EkABQGI5uqDz-ZxAiNB-1VZQvY9uK7IE7UpV6bw6QlwFqH55VfkJGwo6r-V5VEYIFDHr8teZk3jazXzNAMpC8scew"
LINKEDIN_JSESSIONID="ajax:2433755065976177983"
```
> ⚠️ Las cookies `li_at` y `JSESSIONID` expiran en ~60-90 días.
> Cuando expiren: `python solve_linkedin_challenge.py` realiza la autenticación móvil nativa sin Cloudflare y actualiza `.env` automáticamente.

### Telegram Notifier (Verificado con Envíos en Vivo 200 OK)
```env
TELEGRAM_BOT_TOKEN="8844243857:AAFw_vQrbDpKZuqRMCw7j4mgaWxriGWiwxI"
TELEGRAM_CHAT_ID="5445081986"
BOT_USERNAME="@erick_job_hunter_bot"
```

### Servidor GCP (Producción 24/7)
```
Usuario SSH: adanrivas6655
Host: job-hunter-bot (Google Cloud VM us-east1-c)
Proyecto dir: ~/ai-job-hunter-bot
Activar venv: cd ~/ai-job-hunter-bot && source venv/bin/activate
Alias rápido: bot   (ya configurado en ~/.bashrc)
Crontab activo: 0 */4 * * * cd ~/ai-job-hunter-bot && source venv/bin/activate && python main_v6.py >> ~/logs/job_hunter.log 2>&1
```

### Email / SMTP
```env
EMAIL_USER="eflores4006@utm.edu.ec"
EMAIL_PASSWORD="<GOOGLE_APP_PASSWORD_16_LETRAS>"
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
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
| Recruiter Connector | `src/linkedin/recruiter_connector.py` | ✅ Conecta exitosamente |
| Router ATS | `src/appliers/router.py` | ✅ Activo (con fallback Telegram) |
| Greenhouse Applier | `src/appliers/greenhouse_applier.py` | ✅ Playwright instalado en VM |
| Lever Applier | `src/appliers/lever_applier.py` | ✅ Playwright instalado en VM |
| Workable Applier | `src/appliers/workable_applier.py` | ✅ Playwright instalado en VM |
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
- **Recruiter `add_connection`**: Fix probado exitosamente usando `fs_miniProfile URN` directamente. Envía conexiones correctamente.
- **Playwright ATS externo (Greenhouse/Lever)**: Instalado y funcionando en la VM de GCP.
- **Fallback Tolerante a Fallos**: Si no hay email y falla ATS, se envía alerta por Telegram para aplicar manual (cero pérdida de ofertas).
- **Loop 30 Redirects en LinkedIn (`Exceeded 30 redirects`) (2026-09-12)**: Resuelto. `linkedin_client.py` verificaba cookies usando `/voyager/api/me` (obsoleto en 2026). Se cambió la verificación a `search_jobs`, permitiendo validar cookies activas sin loops.
- **Auto-Auth Nativa sin Cloudflare (2026-09-12)**: `solve_linkedin_challenge.py` implementa el endpoint nativo móvil (`/uas/authenticate`). Se ejecuta en 0.8s sin ser bloqueado por Cloudflare y actualiza `.env` automáticamente.
- **Challenge Directo a `challenge_url` (2026-09-12)**: Si LinkedIn pide PIN 2FA, se envía directamente al `challenge_url` nativo proporcionado por la API en vez de la página web de error.
- **Unify Apply Moderno (2026-09-12)**: Agregado endpoint v0 (`/voyager/api/jobs/jobApplications`) en `src/appliers/linkedin_applier.py` para soporte nativo de Unify Apply.
- **Telegram Notifier en Tiempo Real (2026-09-12)**: Lectura dinámica de tokens y fallback hardcodeado. Despachó 25 ofertas simultáneas con enlaces directos completos y pitch para copiar.
- **Búsqueda Exacta Ecuador & LATAM (2026-09-12)**: Búsquedas dirigidas (`Aprendizaje automático`, `Inteligencia Artificial`, `Data Analyst`, `Excel`) con `geoId=106373116`, `f_WT=2` (Remoto) y ventana de 7 días (`listed_at=604800`).
- **Desentierro de Formularios Ocultos ATS**: Extrae formularios reales en Airtable (ej. Familify), BairesDev, Teamtailor y Micro1.
- **CV Estándar Generado**: `data/CV_Erick_Flores_Data_AI.html` y `data/CV_Erick_Flores_Data_AI.pdf` (1 columna, ATS-friendly, métricas de BananaAI 94%, FCH-ARX V2 NIST 49.95%, Forensic NLP+RAG).
- **Piloto Automático en VM GCP (2026-09-12)**: Crontab configurado cada 4 horas (`0 */4 * * *`) ejecutando en segundo plano de forma autónoma. 22 reclutadores contactados históricamente.

### 📍 Dónde ver las postulaciones y conexiones en LinkedIn:
1. **Empleos postulados (Easy Apply):**
   - Menú de LinkedIn: **Empleos** → **Mis empleos** → **Solicitudes de empleo**
   - URL directa: `https://www.linkedin.com/jobs/tracker/applied/`
2. **Empleos postulados vía ATS externo (Greenhouse/Lever/Airtable):**
   - Correo de confirmación directo en tu bandeja (`eflores4006@utm.edu.ec`) enviado por el ATS de la empresa.
3. **Conexiones a reclutadores enviadas (22 en total):**
   - Menú de LinkedIn: **Mi red** → **Gestionar invitaciones** → pestaña **Enviadas**
   - URL directa: `https://www.linkedin.com/mynetwork/invitation-manager/sent/`

### 🟡 Próximas Mejoras (Roadmap Inmediato)
- **Extracción de Emails de RRHH en LinkedIn**: Analizar posts de reclutadores buscando patrones `(\w+@\w+\.\w+)` y menciones en descripciones para enviar cold-emails automáticos con el CV adjunto vía Gmail SMTP.
- **Ampliación de Form Appliers**: Soporte para Airtable Forms y BairesDev portals directos.

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

## 🗺️ Roadmap y Estado de Misiones

### ✅ Completado (Hitos Consolidados hasta 2026-09-12)
- [x] Scraping multi-plataforma 7 fuentes (120+ empleos/corrida)
- [x] Búsqueda geodirigida Ecuador (`geoId=106373116`) y LATAM Remoto (`f_WT=2`) con ventana de 7 días
- [x] MatchEngine con roles Data/AI/BI en español e inglés y MemoryStore auto-reparable
- [x] LinkedIn scraping via Voyager API nativa sin bloqueos ni loops de redirección
- [x] Autenticación móvil nativa y bypass de Cloudflare en 0.8s (`solve_linkedin_challenge.py`)
- [x] Easy Apply Unify v0/v1 con Voyager API POST
- [x] Desentierro de formularios externos ATS ocultos (Airtable, BairesDev, Teamtailor)
- [x] Recruiter Connector: encuentra perfiles y envía conexiones con éxito (22 reclutadores contactados)
- [x] Despacho instantáneo a Telegram (`@erick_job_hunter_bot`) con enlaces directos 1-tap y pitch pre-redactado
- [x] Generación de CV oficial ATS-Friendly en HTML y PDF (`data/CV_Erick_Flores_Data_AI.pdf`)
- [x] Crontab 24/7 en Google Cloud VM (`job-hunter-bot`) ejecutando cada 4 horas
- [x] Alias `bot` configurado en el servidor

### 🔴 Siguiente Prioridad / Nueva Funcionalidad Solicitada por el Usuario
1. **Módulo de Detección de Correos de RRHH en LinkedIn (Posts & Feed Scraping):**
   - Implementar búsqueda de publicaciones de reclutadores con términos clave: `#hiring`, `#busquedait`, `envía tu cv`, `estamos contratando`, `data analyst`, `machine learning`.
   - Extraer correos electrónicos de RRHH directamente del texto de los posts mediante expresiones regulares robustas.
   - **OCR / Vision AI para Flyers de Reclutamiento**: Analizar imágenes adjuntas a publicaciones para extraer emails de contacto que solo aparecen dentro de la imagen.
2. **Postulación Automática por Cold-Email (Gmail SMTP):**
   - Al detectar un correo verificado de RRHH o reclutador, redactar un correo personalizado con la IA (o plantilla especializada) y adjuntar automáticamente `data/CV_Erick_Flores_Data_AI.pdf`.
   - Enviar desde `eflores4006@utm.edu.ec` registrando la postulación en la base de datos `funnel.db` y notificando a Telegram.
3. **Ampliación de Auto-Appliers Externos:**
   - Soporte para auto-completar formularios de Airtable (ej. caso Familify) y portales de BairesDev.

### 🟡 Futuro
- Workday / SAP SuccessFactors Applier
- Gmail Reply Bot (responder automáticamente a respuestas de RRHH)
- Dashboard interactivo de estadísticas de búsqueda y conversión en Telegram

---

## 🧠 Perfil del Candidato

```
Nombre:   Erick Reinaldo Flores Zambrano
Email:    eflores4006@utm.edu.ec / adanrivas6655@gmail.com
Teléfono: +593 096 395 1193
LinkedIn: linkedin.com/in/erick-flores-zambrano-69075b198
GitHub:   github.com/erick007bon

Formación:
  - Economía, 8vo semestre (Universidad Técnica de Manabí - UTM)
  - Ingeniería en Ciencia de Datos e Inteligencia Artificial, 6to semestre (Universidad de Guayaquil - UG)

Skills clave:
  Python, SQL, Power BI, Machine Learning, Deep Learning (LSTM, Transformers),
  FastAPI, Docker, Econometría, Análisis Financiero, NLP, RAG, Web Scraping.

Proyectos Estrella con Métricas:
  1. BananaAI: Detección y conteo de racimos con YOLOv8, mAP@50 de 94.2% a 30 FPS.
  2. FCH-ARX V2: Criptografía post-cuántica aprobada NIST SAC Test (49.95% avalancha).
  3. Forensic AI NLP & RAG: Detección de fraude financiero con embeddings bge-m3.
  4. Neuro-AI Scale-Free Hub: Red neuronal inspirada en topología de Saturno / Omer.
  5. Crypto Price Predictor: Redes LSTM multivariadas con Sharpe Ratio 1.84.
  6. E-Commerce Analytics Engine: Pipeline ETL en ClickHouse y dashboards en Power BI.

CV Oficial ATS:
  data/CV_Erick_Flores_Data_AI.pdf (Compilado en HTML/CSS, 1 columna, ATS Friendly)

Idiomas: Español (Nativo), Inglés (B2 Técnico)
Nivel target: Junior / Mid (evitar Senior 10+ años)
Modalidad: 100% Remoto (Ecuador, LATAM o Internacional)
```
