# 🧠 MISSION BRAIN — AI Job Hunter Bot V7

> **Objetivo**: Conseguir trabajo remoto 100% en Data Science / AI / ML Engineering.
> **Operando**: 24/7 en Google Cloud VM (`job-hunter-bot`, `us-east1-c`)

---

## 🏗️ Arquitectura del Sistema (V7 — Producción)

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
          ┌───────────▼────────────┐
          │  MatchEngine (filtro)  │
          │  MemoryStore (dupes)   │
          └───────────┬────────────┘
                      │
          ┌───────────▼────────────────────────────────────┐
          │              AUTO-POSTULACIÓN                   │
          │  1. LinkedIn Easy Apply (linkedin-api nativo)   │
          │  2. ATS Externo (Greenhouse/Lever/Workable)     │
          │     via Playwright headless                     │
          │  3. Fallback → Cold-Email SMTP + CV adjunto     │
          └───────────┬────────────────────────────────────┘
                      │
          ┌───────────▼────────────┐
          │   Telegram Notifier    │
          │   Markdown Report      │
          └────────────────────────┘
```

---

## 📦 Módulos — Estado Real

| Módulo | Archivo | Estado |
|--------|---------|--------|
| Orquestador | `main_v6.py` | ✅ Activo |
| LinkedIn Scraper | `src/scrapers/linkedin_scraper.py` | ✅ Funciona (linkedin-api + cookies) |
| LinkedIn Client | `src/linkedin/linkedin_client.py` | ✅ Cookies + email/password fallback |
| LinkedIn Easy Apply | `src/appliers/linkedin_applier.py` | ⚠️ Detecta mal el campo Easy Apply |
| Recruiter Connector | `src/linkedin/recruiter_connector.py` | ⚠️ search_people() devuelve 0 |
| Router ATS | `src/appliers/router.py` | ✅ Activo |
| Greenhouse Applier | `src/appliers/greenhouse_applier.py` | ⚠️ Playwright no probado en VM |
| Lever Applier | `src/appliers/lever_applier.py` | ⚠️ Playwright no probado en VM |
| Workable Applier | `src/appliers/workable_applier.py` | ⚠️ Playwright no probado en VM |
| Multitrabajos | `src/appliers/multitrabajos_applier.py` | ✅ Activo LATAM |
| Remotive/RemoteOK/etc. | `src/scrapers/api_scrapers.py` | ✅ Activo |
| WeWorkRemotely/WorkingNomads | `src/scrapers/latam_scrapers.py` | ✅ Activo |
| EmailExtractor | `src/extractors/email_extractor.py` | ✅ Activo (0 emails = sin API key Hunter.io) |
| Gmail SMTP | SMTP directo | ✅ Activo |
| Telegram Notifier | `src/notifications/telegram_notifier.py` | ✅ Activo |

---

## 🔄 Flujo de Ejecución

```
Cada 4 horas (crontab en GCP VM):

1. [LINKEDIN]     Scrape ~30 empleos Data/AI (5 keywords × 10) via linkedin-api
2. [BOARDS]       Scrape 6 APIs/RSS (~80+ ofertas)
3. [FILTRO]       MatchEngine filtra por rol, nivel, idioma
4. [DEDUP]        MemoryStore elimina ya aplicados
5. [ENRICH]       Hunter.io busca email real de RRHH
6. [APPLY]        Router → LinkedIn Easy Apply → ATS Playwright → Cold-Email
7. [NETWORK]      RecruiterConnector → 8 solicitudes LinkedIn/corrida
8. [NOTIF]        Telegram reporta resultados
9. [REPORTE]      Markdown en /reportes/
```

---

## 🌐 Infraestructura

| Componente | Detalles |
|------------|----------|
| **Servidor 24/7** | Google Cloud VM `job-hunter-bot` (Debian 13, `us-east1-c`) |
| **Crontab** | `0 */4 * * *` — cada 4 horas |
| **Auth LinkedIn** | Cookies `li_at` + `JSESSIONID` (renovar cada ~60-90 días) |
| **Python** | 3.13 + venv en `~/ai-job-hunter-bot/venv` |
| **Email** | `eflores4006@utm.edu.ec` via SMTP (`smtp.gmail.com:587`) |

---

## 🔐 Secrets en .env (GCP VM)

| Variable | Uso |
|--------|-----|
| `TELEGRAM_BOT_TOKEN` | Notificaciones |
| `TELEGRAM_CHAT_ID` | Chat destino |
| `OPENROUTER_API_KEY` | Cover letters con IA |
| `HUNTER_API_KEY` | Extracción de emails RRHH |
| `LINKEDIN_LI_AT` | Cookie sesión LinkedIn (renovar cada 60-90 días) |
| `LINKEDIN_JSESSIONID` | Cookie CSRF LinkedIn |
| `LINKEDIN_EMAIL` | Email LinkedIn (fallback si cookies expiran) |
| `LINKEDIN_PASSWORD` | Contraseña LinkedIn (fallback) |
| `CV_PATH` | Ruta local al CV en PDF |
| `EMAIL_USER` | `eflores4006@utm.edu.ec` |
| `EMAIL_PASSWORD` | Contraseña SMTP |

---

## 🗺️ Roadmap V7

### ✅ Completado
- [x] Scraping multi-plataforma (7 fuentes, ~110 empleos/corrida)
- [x] MatchEngine + MemoryStore (anti-duplicados)
- [x] LinkedIn scraping via linkedin-api (sin anti-bot, sin Playwright)
- [x] Autenticación LinkedIn via cookies (RequestsCookieJar)
- [x] Cold-email SMTP con CV adjunto + cover letter IA (OpenRouter)
- [x] Telegram notifications en tiempo real
- [x] Reporte Markdown automático en `/reportes/`

### 🔴 Pendiente (CRÍTICO — próximas iteraciones)
- [ ] **FASE 1**: Debug payloads reales (`python debug_linkedin_api.py` en servidor)
- [ ] **FASE 2**: Arreglar detección de Easy Apply (campo incorrecto en `linkedin_client.py`)
- [ ] **FASE 3**: Instalar y probar Playwright en VM (`playwright install chromium`)
- [ ] **FASE 3**: Activar flujo LinkedIn → URL externa → GreenhouseApplier/LeverApplier
- [ ] **FASE 4**: Arreglar `search_people()` del Recruiter Connector (0 perfiles)

### 🟡 Futuro
- [ ] Workday / SAP SuccessFactors Applier (ATS enterprise)
- [ ] Gmail Reply Bot (responder automáticamente a RRHH)
- [ ] Dashboard métricas en Telegram (funnel: visto → aplicado → entrevista → oferta)
