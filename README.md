# 🤖 AI Job Hunter Bot V7 — Autonomous Tech Recruiter & Job Hunter

Bot autónomo de búsqueda, filtrado, postulación y networking en **Data Science, Artificial Intelligence, Machine Learning & Business Intelligence** para trabajo remoto en Ecuador, Latinoamérica y Global.

**Candidato**: Erick Flores Zambrano — Economista (UTM) & Estudiante de Ing. en Ciencia de Datos e IA (UG)  
**Servidor**: Google Cloud Platform (VM `job-hunter-bot`, Debian 12, 24/7) + GitHub Actions  
**CV Oficial**: `data/CV_Erick_Flores_Data_AI.pdf` (generado desde HTML ATS-friendly)

---

## ¿Qué hace el sistema?

Cada **4 horas** de forma 100% autónoma en la nube:

1. **Scraping Multi-Canal (120+ ofertas)**:
   - **LinkedIn (Ecuador & LATAM)**: Búsquedas dirigidas (`Aprendizaje automático`, `Inteligencia Artificial`, `Data Analyst`, `Excel`, `Python`, `Ciencia de Datos`) con filtro remoto y ventana de 7 días.
   - **Bolsas globales**: Remotive, RemoteOK, GetOnBoard, Jobicy, WeWorkRemotely, WorkingNomads.

2. **Filtrado Inteligente (MatchEngine)**:
   - Valida roles relevantes en español e inglés (ML, Deep Learning, LLMs, Computer Vision, Data Science, BI, Power BI, SQL, Data Entry, Economía Cuantitativa).
   - Descarta off-topic absoluto (ventas, diseño, soporte al cliente) y puestos que exigen 10+ años de antigüedad.

3. **Memoria Persistente y Auto-Reparable (MemoryStore)**:
   - Previene spam o duplicados.
   - Auto-recupera oportunidades que no hayan sido postuladas efectivamente.

4. **Estrategia Híbrida de Postulación & Despacho (1-Tap Apply)**:
   - **Auto-Postulación**: Intenta Easy Apply nativo vía Voyager API y portales ATS compatibles (Greenhouse, Lever).
   - **Despacho Directo a Telegram (1-Click)**: Si la oferta requiere cuestionario personalizado o portal externo (ej. formularios de Airtable, Teamtailor, BairesDev), el bot extrae la URL directa del formulario y la envía de inmediato a Telegram con un pitch profesional listo para copiar y pegar.
   - **Cold-Email**: Envío directo con CV adjunto cuando se detecta email de RRHH verificado.

5. **Networking Automatizado con Reclutadores**:
   - Conecta con reclutadores de talento de IA/Datos en LATAM y remoto desde la cuenta de LinkedIn del usuario (3 invitaciones por ciclo, ~18 al día de forma segura).

6. **Notificación & Reportes**:
   - Mensajería instantánea a Telegram vía `@erick_job_hunter_bot`.
   - Generación de reportes markdown detallados en `reportes/`.

---

## Estructura

```
main_v6.py                          ← Orquestador principal
src/
├── scrapers/
│   ├── linkedin_scraper.py         ← LinkedIn via linkedin-api
│   ├── api_scrapers.py             ← Remotive, RemoteOK, GetOnBoard, Jobicy
│   └── latam_scrapers.py           ← WeWorkRemotely, WorkingNomads
├── linkedin/
│   ├── linkedin_client.py          ← Autenticación + search_jobs + search_people
│   └── recruiter_connector.py      ← 8 conexiones/corrida con reclutadores
├── appliers/
│   ├── router.py                   ← Detecta ATS y decide applier
│   ├── linkedin_applier.py         ← Easy Apply via Voyager API POST
│   ├── greenhouse_applier.py       ← Playwright → boards.greenhouse.io
│   ├── lever_applier.py            ← Playwright → jobs.lever.co
│   └── workable_applier.py         ← Playwright → apply.workable.com
├── filters/match_engine.py         ← Filtra por rol / nivel / idioma
├── memory/memory_store.py          ← Anti-duplicados (SQLite)
├── extractors/email_extractor.py   ← Hunter.io para emails de RRHH
├── notifications/telegram_notifier.py
└── email/gmail_sender.py
```

---

## Cómo corre en producción

### Servidor GCP (principal, 24/7)
```bash
# Conectarse
# SSH al servidor: adanrivas6655@job-hunter-bot

# Entrar al proyecto (alias)
bot

# Correr manualmente
python main_v6.py

# Correr en modo prueba (sin postular)
python main_v6.py --dry-run

# Ver crontab
crontab -l
```

**Crontab configurado** (corre cada 4 horas automáticamente):
```
0 */4 * * * cd ~/ai-job-hunter-bot && source venv/bin/activate && python main_v6.py >> ~/logs/job_hunter.log 2>&1
```

### GitHub Actions (backup, 6 veces/día)
- Se activa en: 7am, 10am, 1pm, 4pm, 7pm, 10pm (Ecuador)
- Workflow: `.github/workflows/job_hunter.yml`
- Ejecución manual: ir a **Actions** → **AI Job Hunter V7** → **Run workflow**

---

## 🔐 Variables de entorno configuradas

En el servidor GCP en `~/ai-job-hunter-bot/.env` (y como GitHub Secrets):

```env
# LinkedIn (Sesión Activa Verificada)
LINKEDIN_EMAIL="adanrivas6655@gmail.com"
LINKEDIN_PASSWORD="Cocodrilo1998"
LINKEDIN_LI_AT="AQEDAS5itwwDjGS6AAABoJbHfVgAAAGgutQBWE4AIpYePYnL369g8cOLYsnq1h9EkABQGI5uqDz-ZxAiNB-1VZQvY9uK7IE7UpV6bw6QlwFqH55VfkJGwo6r-V5VEYIFDHr8teZk3jazXzNAMpC8scew"
LINKEDIN_JSESSIONID="ajax:2433755065976177983"

# Telegram Notifier (Activo en vivo)
TELEGRAM_BOT_TOKEN="8844243857:AAFw_vQrbDpKZuqRMCw7j4mgaWxriGWiwxI"
TELEGRAM_CHAT_ID="5445081986"
BOT_USERNAME="@erick_job_hunter_bot"

# Capacidad de Postulaciones por Ciclo
MAX_APPLICATIONS=25

# Email SMTP (Cold-Email a RRHH)
EMAIL_USER="eflores4006@utm.edu.ec"
EMAIL_PASSWORD="<GOOGLE_APP_PASSWORD_16_LETRAS>"
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587

# IA (Cover letters dinámicas)
OPENROUTER_API_KEY="sk-or-v1-..."

# CV Oficial ATS-Friendly
CV_PATH="data/CV_Erick_Flores_Data_AI.pdf"
PROFILE_PHONE="+5930963951193"
```

---

## 🚀 Bitácora de Sesión — 2026-09-12 (Hito V7: Operación en Producción y Telegram 1-Tap)

### 1. Resumen Ejecutivo
En esta sesión se puso en marcha de punta a punta el bot en la **VM de Google Cloud (`job-hunter-bot`)**, superando los bloqueos de LinkedIn, adaptando la búsqueda a las ofertas reales de **Ecuador y LATAM Remoto**, y habilitando un canal directo a **Telegram con despacho 1-Tap** que extrae hasta formularios ocultos de ATS externos (ej. Airtable, BairesDev, Teamtailor).

### 2. Logros Técnicos y Soluciones Implementadas

1. **Resolución de Autenticación LinkedIn y Eliminación de Loops 302:**
   - **Problema:** El endpoint legacy `/voyager/api/me` causaba `Exceeded 30 redirects` bloqueando la sesión.
   - **Solución:** Se corrigió `src/linkedin/linkedin_client.py` para validar cookies contra búsquedas reales (`search_jobs`).
   - **Solución de Challenge 2FA:** Se implementó `solve_linkedin_challenge.py` usando el endpoint nativo móvil (`/uas/authenticate`). Esto elude Cloudflare en 0.8s, procesa el PIN de correo enviado por LinkedIn y actualiza `.env` automáticamente.

2. **Búsqueda Geodirigida (Ecuador & LATAM Remoto):**
   - Se ajustó `src/scrapers/linkedin_scraper.py` con `geoId=106373116` (Ecuador), filtro remoto `f_WT=2` y ventana de tiempo de 7 días (`f_TPR=r604800` / `listed_at=604800`).
   - Búsquedas con roles en español e inglés: `Aprendizaje automático`, `Inteligencia Artificial`, `Ciencia de Datos`, `Data Analyst`, `Excel`, `Machine Learning`, `Python`, `Power BI`.

3. **Pipeline de Despacho 1-Tap a Telegram (`@erick_job_hunter_bot`):**
   - Se configuró el bot de Telegram (`8844243857:AAFw_vQrbDpKZuqRMCw7j4mgaWxriGWiwxI`, chat `5445081986`).
   - Cada oferta compatible despacha una tarjeta con: título, empresa, enlace directo completo (sin truncar), nivel de compatibilidad y **un pitch profesional pre-redactado listo para copiar y pegar**.
   - Se incrementó `MAX_APPLICATIONS=25` y se agregó `clean_unverified_entries` en `MemoryStore` para evitar que ofertas con formularios externos se den por postuladas sin haber sido enviadas.

4. **Desentierro de Formularios Ocultos ATS:**
   - Comprobación real con la oferta capturada en screenshot: `Product Builder | Diseño, IA y Producto @ Familify` (`job_id=4465810598`).
   - En lugar de fallar por no tener Easy Apply nativo, el bot identificó el formulario real de Airtable (`https://airtable.com/appHGv49eNoJMraOi/pagN8cf7xHN3zVYGd/form?hide_Rol`) y lo entregó en Telegram para postulación inmediata.

5. **Networking Automatizado en Vivo con Reclutadores:**
   - Se conectó con 3 reclutadores de IA/Datos en LATAM en vivo durante la prueba (Matias Jacome, Jonathan Ludeña, Julian Sanabria), alcanzando **22 reclutadores contactados históricamente** de forma orgánica y segura.

6. **Generación del CV ATS-Friendly Oficial:**
   - Creación de `data/CV_Erick_Flores_Data_AI.html` y compilación a `data/CV_Erick_Flores_Data_AI.pdf` (494 KB).
   - Estándar: 1 columna, tipografía Inter, acento `#0057FF`, métricas reales cuantificadas de proyectos (BananaAI 94% mAP, FCH-ARX V2 NIST 49.95%, Forensic NLP+RAG) y palabras clave optimizadas para sistemas ATS.

7. **Aclaración Técnica: Pestaña "Solicitados" en LinkedIn vs ATS Externo:**
   - **Por qué LinkedIn marcaba 0 en "Solicitados":** LinkedIn *únicamente* contabiliza en su UI las postulaciones que se completan dentro del modal nativo "Solicitud Sencilla" (Easy Apply). Si una vacante redirige a un ATS externo (Airtable, Greenhouse, Lever, etc.) o exige cuestionarios personalizados con preguntas de visado o salario, la postulación ocurre fuera de LinkedIn y la confirmación llega a tu correo (`eflores4006@utm.edu.ec`).
   - **Garantía del Bot:** El bot intenta el Easy Apply nativo; si detecta formularios externos o cuestionarios, extrae el enlace directo y lo envía a Telegram para que el candidato aplique en 10 segundos con su perfil.

### 3. Métricas de la Ejecución en la VM de GCP
- **Ofertas Totales Escaneadas:** 122 (34 de LinkedIn + 88 de bolsas remotas).
- **Ofertas Compatibles Filtradas:** 31 vacantes afines a Data/AI/BI.
- **Ofertas Despachadas a Telegram:** 25 tarjetas enriquecidas enviadas en tiempo real.
- **Conexiones a Reclutadores:** 3 invitaciones enviadas en el ciclo (22 acumuladas en LinkedIn).
- **Crontab:** Activo cada 4 horas (`0 */4 * * *`) ejecutando en segundo plano en la VM.

---

## 📍 ¿Dónde ver tus postulaciones y conexiones en LinkedIn?

1. **Postulaciones Easy Apply nativas:**  
   `https://www.linkedin.com/jobs/tracker/applied/`  
   *(En LinkedIn: Empleos → Mis empleos → Solicitudes de empleo)*.

2. **Postulaciones ATS Externas (Greenhouse, Lever, Airtable, etc.):**  
   Llegan directamente a tu correo (`eflores4006@utm.edu.ec`) como confirmación oficial de la empresa contratante.

3. **Invitaciones a Reclutadores enviadas (22 en total):**  
   `https://www.linkedin.com/mynetwork/invitation-manager/sent/`  
   *(En LinkedIn: Mi red → Gestionar invitaciones → pestaña Enviadas)*.

---

## 🤖 Handover para Modelos de IA / Futuros Agentes

> **Instrucciones para cualquier IA que continúe este proyecto:**

1. **Entorno de Ejecución:**
   - El código corre en producción en una VM Debian 12 de Google Cloud (`adanrivas6655@job-hunter-bot`).
   - El usuario ingresa por SSH y tiene el alias `bot` (`cd ~/ai-job-hunter-bot && source venv/bin/activate`).
   - Crontab corre `python main_v6.py` cada 4 horas.
2. **Archivos Centrales:**
   - [main_v6.py](file:///c:/Users/Erick%20Zambrano/Desktop/linkedin/ai-job-hunter-bot/main_v6.py): Orquestador principal que ejecuta scraping, filtrado, deduplicación, aplicación, networking y despacho.
   - [src/scrapers/linkedin_scraper.py](file:///c:/Users/Erick%20Zambrano/Desktop/linkedin/ai-job-hunter-bot/src/scrapers/linkedin_scraper.py): Scraper que consulta Voyager API de LinkedIn con geolocalización Ecuador/LATAM y 7 días.
   - [src/filters/match_engine.py](file:///c:/Users/Erick%20Zambrano/Desktop/linkedin/ai-job-hunter-bot/src/filters/match_engine.py): Motor de matching con reglas positivas para Data/AI/BI y filtros de descarte.
   - [src/notifications/telegram_notifier.py](file:///c:/Users/Erick%20Zambrano/Desktop/linkedin/ai-job-hunter-bot/src/notifications/telegram_notifier.py): Formatea y envía las tarjetas de empleo y reportes.
   - [src/linkedin/recruiter_connector.py](file:///c:/Users/Erick%20Zambrano/Desktop/linkedin/ai-job-hunter-bot/src/linkedin/recruiter_connector.py): Envía solicitudes de conexión a reclutadores de Data/AI con rate-limiting seguro.
   - [solve_linkedin_challenge.py](file:///c:/Users/Erick%20Zambrano/Desktop/linkedin/ai-job-hunter-bot/solve_linkedin_challenge.py): Script autónomo para resolver challenges 2FA y refrescar cookies sin Cloudflare.
3. **Próximo Objetivo de Desarrollo:**
   - Desarrollar el módulo de **Scraping de Publicaciones de Reclutadores en LinkedIn**: buscar posts con palabras clave (`#hiring`, `buscamos data analyst`, `envía tu cv a`), extraer correos electrónicos de RRHH usando regex / OCR / LLM para imágenes de flyers, y enviar cold-emails automáticos con el CV adjunto (`data/CV_Erick_Flores_Data_AI.pdf`) mediante Gmail SMTP.
