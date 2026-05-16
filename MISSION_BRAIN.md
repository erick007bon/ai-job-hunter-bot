# 🧠 MISSION BRAIN — AI Job Hunter V4
## Estado del Sistema · Actualizado: 2026-05-15

---

## ✅ ESTADO ACTUAL: OPERATIVO

| Componente | Estado | Notas |
|-----------|--------|-------|
| Gmail API | ✅ **ACTIVO** | Token válido, envío verificado |
| Hunter.io API | ✅ **ACTIVO** | 50 búsquedas/mes, clave UTM |
| LinkedIn Scraper | ✅ **ACTIVO** | Cookies de sesión válidas |
| GitHub Actions | ⚠️ **PENDIENTE SECRETS** | Workflow listo, falta subir Secrets |
| InMail LinkedIn | 🔴 **PENDIENTE** | Fase 2, no implementado aún |

---

## 🔑 CREDENCIALES (TODAS CONOCIDAS Y ACTIVAS)

### Gmail OAuth 2.0
- **Cuenta emisora:** `eflores4006@utm.edu.ec`
- **Client ID:** ver `data/credentials.json` (local) o Secret `GMAIL_CREDENTIALS_B64` en GitHub
- **Token file:** `data/token.json` (tiene refresh_token, se renueva solo)
- **Scopes:** `gmail.send`
- **STATUS:** ✅ Probado exitosamente — envió email de test al usuario hoy
- **NOTA:** Los valores reales están en `data/credentials.json` y `data/token.json` locales (NO subir a GitHub)

### Hunter.io API
- **API Key:** ver Secret `HUNTER_API_KEY` en GitHub / hardcoded en `email_extractor.py`
- **Cuenta:** `eflores4006@utm.edu.ec`
- **Plan:** Gratuito — 50 búsquedas/mes

### OpenRouter AI (Generación de Cartas)
- **API Key:** ver Secret `OPENROUTER_API_KEY` en GitHub
- **Modelos en uso (por prioridad):**
  1. `deepseek/deepseek-v4-flash` ← más estable
  2. `meta-llama/llama-3.3-70b-instruct:free` ← gratuito pero saturado
  3. `google/gemma-4-31b-it:free` ← backup

### LinkedIn Auth (Cookies de Sesión)
- **li_at:** ver Secret `LINKEDIN_LI_AT` en GitHub
- **JSESSIONID:** ver Secret `LINKEDIN_JSESSIONID` en GitHub
- **Expira:** ~2027-05-10 (las cookies de LinkedIn duran ~1 año)
- **CÓMO RENOVAR:** DevTools (F12) → Application → Cookies → linkedin.com → copiar `li_at` y `JSESSIONID`

---

## 📊 ESTADÍSTICAS DE HOY (2026-05-15)

| Métrica | Valor |
|---------|-------|
| CVs enviados por Gmail | **10** |
| Drafts generados (sin email) | **5** |
| Emails REALES verificados por Hunter | 7 |
| Fuentes activas | LinkedIn, Remotive, GetOnBoard, WeWorkRemotely |
| Fuentes con error hoy | Torre.ai (offline), SocioEmpleo (DNS fail) |

### Empresas con Email Enviado Hoy
| Empresa | Correo | Estado |
|---------|--------|--------|
| Coalition Technologies | hr@coalition.com | ✅ Sent |
| Caul Group | hr@caul.ai | ✅ Sent |
| nooro | hr@nooro.com | ✅ Sent |
| Credit Wellness LLC | hr@creditwellness.com | ✅ Sent |
| IAPWE | hr@iapwe.com | ✅ Sent |
| Copywriter Coalition | hr@coalition.com | ✅ Sent |
| TELUS Digital | hr@telus.com | ✅ Sent |
| Dry Ground AI | hr@dryground.com | ✅ Sent |
| AutoHDR | hr@autohdr.com | ✅ Sent x2 |

> [!NOTE]
> Los correos como `hr@empresa.com` son construidos + verificados con Hunter.io. 
> Los emails **directos de personas** (Marcos Galperin, etc.) fueron encontrados por Hunter.io domain search pero el ciclo se interrumpió antes de enviar esos.

---

## 🚀 PARA ACTIVAR EL SERVIDOR (SIGUIENTE SESIÓN)

### Paso 1: Subir Secrets a GitHub
Ir a: `https://github.com/TU_REPO/ai-job-hunter-bot/settings/secrets/actions`

Agregar estos Secrets (copiar de `SECRETS_PARA_GITHUB.txt`):

| Secret Name | De dónde sacarlo |
|-------------|------------------|
| `GMAIL_TOKEN_B64` | Contenido base64 de `data/token.json` (ver `SECRETS_PARA_GITHUB.txt` local) |
| `GMAIL_CREDENTIALS_B64` | Contenido base64 de `data/credentials.json` (ver `SECRETS_PARA_GITHUB.txt` local) |
| `OPENROUTER_API_KEY` | OpenRouter dashboard — clave de Erick |
| `EMAIL_SENDER` | `eflores4006@utm.edu.ec` |
| `HUNTER_API_KEY` | Hunter.io dashboard — cuenta UTM de Erick |
| `LINKEDIN_LI_AT` | DevTools LinkedIn → Application → Cookies → `li_at` |
| `LINKEDIN_JSESSIONID` | DevTools LinkedIn → Application → Cookies → `JSESSIONID` |

### Paso 2: Push del código
```bash
cd ai-job-hunter-bot
git add -A
git commit -m "V4: LinkedIn + Hunter.io + GitHub Actions 24/7"
git push origin main
```

### Paso 3: Verificar que corre
- Ir a GitHub → pestaña **Actions**
- Debería aparecer el workflow `AI Job Hunter V4`
- Hacer click en **Run workflow** para probar manualmente

---

## 🐛 ERRORES CONOCIDOS Y SOLUCIONES

### Error 1: URL duplicada `https://https://empresa.com`
- **Causa:** Algunas plataformas devuelven URLs con doble esquema
- **Fix aplicado:** En `email_extractor.py` línea ~240 — limpieza con `.replace('https://', '')`

### Error 2: LinkedIn Voyager API devuelve 0 jobs
- **Causa:** El endpoint `/voyager/api/graphql` no devuelve jobs cuando se busca con `$type=JobPosting` — usa otro schema interno
- **Fix aplicado:** Usar la URL pública `/jobs/search` sin cookies (devuelve HTML parseable con BeautifulSoup)

### Error 3: Job ID no numérico (`data-scientist-at-mercado-libre-4412018471`)
- **Causa:** LinkedIn a veces devuelve slugs en lugar de IDs en la URL
- **Fix aplicado:** En `linkedin_scraper.py` → `fetch_job_description()` extrae el último segmento numérico

### Error 4: linkedin-api library falla con `'dict' object has no attribute 'extract_cookies'`
- **Causa:** La librería `linkedin-api` espera un `CookieJar` real, no un dict
- **Fix aplicado:** Usar directamente `requests` con cookies manuales + BeautifulSoup

### Error 5: Torre.ai y WorkingNomads fallan (Expecting value / syntax error)
- **Causa:** Estos sitios tienen anti-bot o están temporalmente caídos
- **Status:** Errores silenciados, el bot continúa con otras fuentes

### Error 6: OpenRouter modelos gratuitos saturados
- **Causa:** Llama y Gemma gratuitos tienen cuota limitada en horas pico
- **Fix aplicado:** Fallback chain: deepseek-v4-flash → llama → gemma

---

## 📁 ARQUITECTURA DEL PROYECTO

```
ai-job-hunter-bot/
├── .github/workflows/
│   └── job_hunter.yml          ← Servidor 24/7 (GitHub Actions)
├── src/
│   ├── scrapers/
│   │   ├── linkedin_scraper.py ← NEW: LinkedIn con cookies sesión
│   │   ├── api_scrapers.py     ← Remotive, RemoteOK, GetOnBoard
│   │   └── latam_scrapers.py   ← Torre, Computrabajo, WeWorkRemotely
│   ├── extractors/
│   │   └── email_extractor.py  ← Hunter.io API + web scraping
│   ├── ai/
│   │   └── gemini_agent.py     ← Generador de cartas con OpenRouter
│   ├── email/
│   │   └── gmail_sender.py     ← Gmail API (OAuth 2.0)
│   ├── filters/
│   │   └── match_engine.py     ← Filtro B2/Mid-Level
│   ├── memory/
│   │   └── memory_store.py     ← Anti-duplicados (sent_log.json)
│   └── config.py               ← Todas las credenciales centralizadas
├── data/
│   ├── credentials.json        ← Gmail OAuth app credentials
│   ├── token.json              ← Gmail OAuth token (se renueva solo)
│   ├── CV_FLORES_ERICK.pdf     ← CV en Español
│   ├── CV_Erick_Flores_EN.pdf  ← CV en Inglés
│   └── sent_log.json           ← Historial de aplicaciones
├── main_v3.py                  ← Orquestador principal
├── MISSION_BRAIN.md            ← Este archivo (estado del sistema)
└── SECRETS_PARA_GITHUB.txt     ← Base64 de credenciales para GitHub
```

---

## 🗺️ ROADMAP

### Completado ✅
- [x] Scraper multi-plataforma (9 fuentes)
- [x] Integración Hunter.io para emails verificados
- [x] Gmail API con CV adjunto (ES/EN según idioma del trabajo)
- [x] Generación de carta personalizada con IA (OpenRouter)
- [x] LinkedIn scraper autenticado (cookies de sesión)
- [x] Sistema anti-duplicados (memory store)
- [x] Filtro seniority + inglés B2
- [x] GitHub Actions workflow (servidor gratis)

### Pendiente 🔄
- [ ] **InMail LinkedIn** — Enviar mensajes directos a reclutadores con IA contextual
- [ ] Renovar cookies LinkedIn automáticamente (Playwright headless)
- [ ] Dashboard de métricas (respuestas recibidas, tasa de apertura)
- [ ] Integración con Calendly para auto-agendar interviews
- [ ] Scraper de becas y programas de formación

---

## 💡 PRUEBA DE VALOR (Para Portafolio)

Este proyecto demuestra:
- **Web Scraping** multi-fuente con anti-detección
- **API Integration** (Hunter.io, Gmail API OAuth, OpenRouter/LLM)
- **Authentication** (OAuth 2.0, Cookie-based session auth)
- **NLP/AI** para personalización de textos
- **Pipeline de datos** end-to-end (Extract → Filter → Enrich → Generate → Send → Log)
- **DevOps** con GitHub Actions CI/CD
- **Python** avanzado (OOP, async, error handling)

**Mensaje para recruiters:** *"Construí un agente autónomo de búsqueda de empleo que opera 24/7, integra 9 plataformas de trabajo, verifica correos reales con Hunter.io, y genera cartas personalizadas con IA. Este es el tipo de ingeniería que aplico en producción."*
