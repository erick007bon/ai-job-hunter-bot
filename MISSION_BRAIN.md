# 🧠 MISSION BRAIN — AI Job Hunter Bot

> **Objetivo**: Conseguir trabajo remoto 100% en Data Science / AI / ML Engineering.
> **Operando**: 24/7 en Google Cloud VM (`job-hunter-bot`, `us-east1-c`, IP: `34.24.28.172`)

---

## 🏗️ Arquitectura del Sistema (V6 — Producción)

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
   │  ~50% jobs  │    │  ~50% jobs     │     │ 8 conexiones/run  │
   └──────┬──────┘    └─────────┬──────┘     └──────────────────-┘
          └─────────────────────┘
                      │
          ┌───────────▼────────────┐
          │  MatchEngine (filtro)  │
          │  MemoryStore (dupes)   │
          └───────────┬────────────┘
                      │
          ┌───────────▼────────────┐
          │   EmailExtractor       │
          │   (Hunter.io API)      │
          └───────────┬────────────┘
                      │
          ┌───────────▼────────────────────────────────────┐
          │              AUTO-POSTULACIÓN                   │
          │  Router → ATS Playwright (Greenhouse/Lever/...) │
          │  Fallback → Cold-Email SMTP + CV adjunto        │
          └───────────┬────────────────────────────────────┘
                      │
          ┌───────────▼────────────┐
          │   Telegram Notifier    │
          │   Markdown Report      │
          └────────────────────────┘
```

---

## 📦 Módulos Activos

| Módulo | Archivo | Estado |
|--------|---------|--------|
| Orquestador principal | `main_v6.py` | ✅ Activo |
| LinkedIn Scraper | `src/scrapers/linkedin_scraper.py` | ✅ Activo |
| Recruiter Connector | `src/linkedin/recruiter_connector.py` | ✅ Activo |
| LinkedIn Messenger | `src/linkedin/linkedin_messenger.py` | ✅ Activo |
| Remotive API | `src/scrapers/api_scrapers.py` | ✅ Activo |
| RemoteOK API | `src/scrapers/api_scrapers.py` | ✅ Activo |
| GetOnBoard API (LATAM) | `src/scrapers/api_scrapers.py` | ✅ Activo |
| Jobicy API | `src/scrapers/api_scrapers.py` | ✅ Activo |
| WeWorkRemotely RSS | `src/scrapers/latam_scrapers.py` | ✅ Activo |
| WorkingNomads JSON | `src/scrapers/latam_scrapers.py` | ✅ Activo |
| LinkedIn Easy Apply | `auto_apply_main.py` | ✅ Activo |
| MatchEngine (Filtros) | `src/filters/match_engine.py` | ✅ Activo |
| MemoryStore (Anti-dupes) | `src/memory/memory_store.py` | ✅ Activo |
| EmailExtractor (Hunter.io) | `src/extractors/email_extractor.py` | ✅ Activo |
| Router ATS | `src/appliers/router.py` | ✅ Activo |
| Greenhouse Applier | `src/appliers/greenhouse_applier.py` | ✅ Activo |
| Lever Applier | `src/appliers/lever_applier.py` | ✅ Activo |
| Workable Applier | `src/appliers/workable_applier.py` | ✅ Activo |
| Multitrabajos Applier | `src/appliers/multitrabajos_applier.py` | ✅ Activo |
| Gmail Sender | `src/email/gmail_sender.py` | ✅ Activo |
| Gmail Reply Bot | `src/email/gmail_reply_bot.py` | ✅ Activo |
| Telegram Notifier | `src/notifications/telegram_notifier.py` | ✅ Activo |
| CV Generator | `generate_cv_en.py` | ✅ Activo |

---

## 🔄 Flujo de Ejecución

```
Cada 4 horas (crontab en GCP VM):

1. [LINKEDIN]     Scrape 30 empleos Data/AI (3 keywords × 10)
2. [BOARDS]       Scrape 6 APIs/RSS (~60+ ofertas adicionales)
3. [FILTRO]       MatchEngine filtra por rol, nivel, idioma
4. [DEDUP]        MemoryStore elimina ya aplicados
5. [ENRICH]       Hunter.io busca email real de RRHH
6. [APPLY]        Router → ATS Playwright o Cold-Email SMTP
7. [NETWORK]      RecruiterConnector → 8 solicitudes LinkedIn/corrida
8. [NOTIF]        Telegram reporta resultados
9. [REPORTE]      Markdown en /reportes/
```

---

## 🌐 Infraestructura

| Componente | Detalles |
|------------|----------|
| **Servidor 24/7** | Google Cloud VM `job-hunter-bot` (Debian 13, `us-east1-c`) |
| **IP Externa** | `34.24.28.172` |
| **Crontab** | `0 */4 * * *` — cada 4 horas |
| **Python** | 3.13 + venv en `/home/adanrivas6655/ai-job-hunter-bot/venv` |
| **GitHub Actions** | Backup paralelo — 6 corridas/día (7am, 10am, 1pm, 4pm, 7pm, 10pm ECT) |
| **Email** | `eflores4006@utm.edu.ec` via SMTP (`smtp.gmail.com:587`) |
| **LinkedIn Easy Apply** | Workflow separado `linkedin_demo.yml` — diario 8am ECT |

---

## 🔐 Secrets Necesarios (GitHub Actions)

| Secret | Uso |
|--------|-----|
| `TELEGRAM_BOT_TOKEN` | Notificaciones |
| `TELEGRAM_CHAT_ID` | Chat destino |
| `OPENROUTER_API_KEY` | Cover letters con IA |
| `GMAIL_CREDENTIALS_B64` | Gmail OAuth2 |
| `GMAIL_TOKEN_B64` | Gmail OAuth2 token |
| `HUNTER_API_KEY` | Extracción de emails RRHH |
| `LINKEDIN_LI_AT` | Cookie sesión LinkedIn |
| `LINKEDIN_JSESSIONID` | Cookie CSRF LinkedIn |
| `CV_PDF_B64` | PDF del CV en Base64 |
| `EMAIL_SENDER` | `eflores4006@utm.edu.ec` |
| `MULTITRABAJOS_EMAIL` | Para Multitrabajos Ecuador |
| `MULTITRABAJOS_PASSWORD` | Para Multitrabajos Ecuador |

---

## 🗺️ Roadmap (Próximos Pasos)

- [ ] LinkedIn Easy Apply con Playwright (postulación directa en LinkedIn)
- [ ] Gmail Reply Bot activo en GCP (responder emails de RRHH automáticamente)
- [ ] Scholarship Hunter integrado al pipeline diario
- [ ] Métricas de funnel en dashboard Telegram (tasa de respuesta, entrevistas)
- [ ] FCH-ARX V2 paper submission a revista indexada LATAM
