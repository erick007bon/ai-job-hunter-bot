# 🤖 AI Job Hunter Bot V6

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-black)
![Runs/day](https://img.shields.io/badge/Runs-4x%20daily-orange)

Bot autónomo que busca ofertas remotas de **Data Science / AI / Data Engineering** en 6 plataformas, detecta el ATS de la empresa, intenta postular automáticamente y envía un email con tu CV si no puede aplicar directamente. Todo corre en **GitHub Actions gratis**, 4 veces al día.

---

## 🗺️ Cómo funciona (pipeline real)

```
┌─────────────────────────────────────────────────────────┐
│  GitHub Actions — 4x/día (7am, 12pm, 5pm, 10pm ECT)   │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────▼────────────┐
        │  1. SCRAPING (6 fuentes)│
        │  Remotive, RemoteOK,   │
        │  GetOnBoard, Jobicy,   │
        │  WeWorkRemotely,       │
        │  WorkingNomads         │
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │  2. FILTRADO           │
        │  MatchEngine por       │
        │  keywords, seniority,  │
        │  ubicación remota      │
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │  3. DEDUPLICACIÓN      │
        │  MemoryStore (JSON)    │
        │  evita re-aplicar      │
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │  4. ENRIQUECIMIENTO    │
        │  Hunter.io → email     │
        │  real de RRHH          │
        └───────────┬────────────┘
                    │
          ┌─────────┴────────────┐
          │                      │
┌─────────▼───────┐   ┌─────────▼────────────┐
│ ATS detectado   │   │  Job board genérico  │
│ (Greenhouse,    │   │  (Remotive, etc.)    │
│ Lever, Workable,│   │                      │
│ Ashby, etc.)   │   │  Seguir redirect HTTP │
│                 │   │  para detectar ATS   │
│ Playwright      │   │  real de la empresa  │
│ auto-apply ✅   │   └─────────┬────────────┘
└─────────┬───────┘             │
          │            ┌────────▼─────────────┐
          │            │  COLD EMAIL con CV   │
          │            │  SMTP directo o      │
          │            │  Gmail OAuth2        │
          │            │  Cover letter con IA │
          │            │  (OpenRouter)        │
          └────────────└─────────┬────────────┘
                                  │
                      ┌───────────▼────────────┐
                      │  5. TELEGRAM + REPORTE │
                      │  Notificación por cada │
                      │  oferta y resumen final│
                      └────────────────────────┘
```

---

## ⚙️ Configuración de Secrets (obligatorio)

Ve a: **Settings → Secrets and variables → Actions** en tu fork.

### 🔴 Obligatorios (sin estos el bot solo notifica, no postula)

| Secret | Descripción | Cómo obtener |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Token de tu bot de Telegram | Crea un bot con [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | ID de tu chat | Usa [@userinfobot](https://t.me/userinfobot) |
| `CV_PDF_B64` | Tu CV en PDF codificado en base64 | Ver instrucciones abajo |

#### Cómo codificar tu CV en base64

**Linux / Mac:**
```bash
base64 -i CV_Erick_Flores_EN.pdf | pbcopy   # Mac (copia al portapapeles)
base64 -i CV_Erick_Flores_EN.pdf            # Linux (imprime en terminal)
```

**Windows (PowerShell):**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\ruta\CV_Erick_Flores_EN.pdf")) | Set-Clipboard
```

Pega el resultado como valor del secret `CV_PDF_B64` en GitHub.

---

### 🟡 Opcionales (mejoran la tasa de postulación)

| Secret | Descripción | Gratis? |
|---|---|---|
| `EMAIL_USER` | Tu correo para SMTP | ✅ (cualquier Gmail/Outlook) |
| `EMAIL_PASSWORD` | App Password de tu correo | ✅ |
| `OPENROUTER_API_KEY` | IA para generar cover letters personalizadas | ✅ plan gratuito |
| `HUNTER_API_KEY` | Detecta emails reales de RRHH | ✅ 25 búsquedas/mes gratis |
| `GMAIL_CREDENTIALS_B64` | OAuth2 Google Cloud (alternativa a SMTP) | ✅ |
| `GMAIL_TOKEN_B64` | Token OAuth2 (expira cada 7 días) | ⚠️ requiere renovación |
| `LINKEDIN_LI_AT` | Cookie de sesión LinkedIn (solo scrapers) | ⚠️ riesgo de ban |

#### Configurar App Password en Gmail (para SMTP)
1. Activa la verificación en 2 pasos en tu cuenta Google
2. Ve a: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Crea una app password para "Correo"
4. Úsala como `EMAIL_PASSWORD` (NO tu contraseña normal)

---

## 🏗️ Estructura del proyecto

```
ai-job-hunter-bot/
├── main_v6.py                    # Orquestador principal
├── scholarship_hunter.py         # Búsqueda de becas (1x/día)
├── auto_apply_main.py            # LinkedIn EasyApply (manual, ver abajo)
├── requirements.txt
├── .env.example
├── .github/
│   └── workflows/
│       ├── job_hunter.yml        # Workflow principal (4x/día)
│       └── linkedin_demo.yml     # LinkedIn manual (workflow_dispatch)
└── src/
    ├── scrapers/                 # Fuentes de ofertas
    │   ├── api_scrapers.py       # Remotive, RemoteOK, GetOnBoard, Jobicy
    │   └── latam_scrapers.py     # WeWorkRemotely, WorkingNomads
    ├── filters/
    │   └── match_engine.py       # Filtros por keywords/seniority
    ├── appliers/
    │   ├── router.py             # Detecta ATS por URL (sigue redirects)
    │   ├── greenhouse_applier.py
    │   ├── lever_applier.py
    │   ├── workable_applier.py
    │   ├── ashby_applier.py
    │   ├── bamboohr_applier.py
    │   ├── jobvite_applier.py
    │   ├── smartrecruiters_applier.py
    │   ├── icims_applier.py
    │   └── multitrabajos_applier.py
    ├── memory/
    │   ├── memory_store.py       # JSON: URLs ya aplicadas
    │   └── funnel_db.py          # SQLite: historial de postulaciones
    ├── extractors/
    │   └── email_extractor.py    # Hunter.io API
    ├── notifications/
    │   └── telegram_notifier.py  # Notificaciones Telegram
    └── email/
        └── gmail_sender.py       # Gmail OAuth2 (fallback)
```

---

## 📊 Estado de cada módulo

| Módulo | Estado | Notas |
|---|---|---|
| Scraping (6 fuentes) | ✅ Funciona | APIs y RSS estables |
| MatchEngine / filtros | ✅ Funciona | Filtra por keywords y seniority |
| MemoryStore (deduplicación) | ✅ Funciona | JSON persistido en `data/` |
| Notificaciones Telegram | ✅ Funciona | Por eso llegan las notificaciones |
| EmailExtractor (Hunter.io) | ✅ Funciona | Requiere `HUNTER_API_KEY` |
| FunnelDB (SQLite) | ✅ Funciona | Registra postulaciones |
| Router ATS + redirect | ✅ Funciona | Sigue redirects de job boards |
| Appliers ATS (Playwright) | ⚠️ Implementados | Funcionan cuando la URL llega directo al ATS |
| Cold Email SMTP | ✅ Funciona | Requiere `EMAIL_USER` + `EMAIL_PASSWORD` + `CV_PDF_B64` |
| Cold Email Gmail OAuth2 | ⚠️ Funciona | Expira cada 7 días, requiere renovación manual |
| Cover Letters con IA | ✅ Funciona | Requiere `OPENROUTER_API_KEY` (gratis) |
| LinkedIn EasyApply | ⚠️ **DESACTIVADO** | Ver sección abajo |
| LinkedIn InMail | ❌ **DESACTIVADO** | Riesgo de ban de cuenta |
| Búsqueda de becas | ✅ Funciona | 1x/día a las 7am ECT |

---

## ⚠️ LinkedIn EasyApply — Importante leer

El workflow `linkedin_demo.yml` puede correr **LinkedIn EasyApply** de forma manual (`workflow_dispatch`), pero está **desactivado en el cron automático** por diseño:

**Razones:**
1. LinkedIn detecta y banea cuentas que se conectan desde IPs de datacenters (GitHub Actions usa IPs de Azure)
2. Sin `OPENAI_API_KEY`, los formularios se rellenan con respuestas en blanco — postulaciones de mala calidad a tu nombre
3. Viola los Términos de Servicio de LinkedIn

Si quieres usarlo bajo tu responsabilidad:
1. Configura todos los secrets `CANDIDATE_*` en GitHub
2. Corre el workflow `LinkedIn Autonomy Demo` **manualmente** desde la pestaña Actions
3. Revisa los logs inmediatamente

---

## 🚀 Para empezar

1. Haz **fork** de este repositorio
2. Configura los secrets obligatorios (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `CV_PDF_B64`)
3. (Opcional) Configura SMTP (`EMAIL_USER` + `EMAIL_PASSWORD`) para que postule por email
4. Activa GitHub Actions en tu fork
5. El bot corre solo 4 veces al día. Puedes forzar un run desde la pestaña **Actions → Run workflow**

---

*Desarrollado por [Erick Flores Zambrano](https://github.com/erick007bon) — Economista, Data Scientist, AI Engineer — Ecuador 🇪🇨*
