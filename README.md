# 🤖 AI Job Hunter Bot V7

Bot de búsqueda y postulación automática de empleo remoto en Data Science / AI / ML Engineering.

**Candidato**: Erick Flores Zambrano — Ecuador  
**Servidor**: Google Cloud VM 24/7 + GitHub Actions (backup)

---

## ¿Qué hace?

Cada **4 horas** automáticamente:

1. **Scraping** — busca empleos en 7 fuentes simultáneas:
   - LinkedIn (~30 empleos via API nativa, sin anti-bot)
   - Remotive, RemoteOK, GetOnBoard, Jobicy
   - WeWorkRemotely, WorkingNomads

2. **Filtrado** — descarta Senior, irrelevantes, idioma no compatible

3. **Deduplicación** — no postula dos veces al mismo empleo

4. **Auto-postulación**:
   - LinkedIn Easy Apply → POST directo al Voyager API de LinkedIn
   - ATS externos (Greenhouse, Lever, Workable) → Playwright headless
   - Fallback → Cold-email SMTP con CV adjunto + cover letter generada por IA

5. **Network** — envía 8 solicitudes de conexión a reclutadores Data/AI en LinkedIn

6. **Notificación** → Telegram con resultados en tiempo real

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

## Variables de entorno requeridas

En el servidor GCP en `~/ai-job-hunter-bot/.env`:

```env
# LinkedIn (cookies — renovar cada 60-90 días)
LINKEDIN_LI_AT="..."
LINKEDIN_JSESSIONID="ajax:..."
LINKEDIN_EMAIL="..."
LINKEDIN_PASSWORD="..."

# Telegram
TELEGRAM_BOT_TOKEN="..."
TELEGRAM_CHAT_ID="..."

# Email SMTP
EMAIL_USER="eflores4006@utm.edu.ec"
EMAIL_PASSWORD="..."

# IA (cover letters)
OPENROUTER_API_KEY="..."

# CV
CV_PATH="data/CV_Erick_Flores_EN.pdf"
PROFILE_PHONE="+593963951193"
```

Para GitHub Actions, configurar como **Secrets** en:  
`https://github.com/erick007bon/ai-job-hunter-bot/settings/secrets/actions`

---

## Estado actual (2026-08-30)

| Función | Estado |
|---------|--------|
| Scraping LinkedIn | ✅ ~30 empleos/corrida |
| Scraping 6 job boards | ✅ ~80 empleos/corrida |
| LinkedIn Easy Apply | ✅ Voyager API POST |
| Recruiter connections | ✅ 8 conexiones/corrida |
| Cold-email SMTP | ✅ Con CV adjunto + IA cover letter |
| ATS externos (Playwright) | ⚠️ Instalar: `playwright install chromium` |
