# 🤖 AI Job Hunter Bot V6

> **Agente autónomo 24/7 de búsqueda y postulación de empleo remoto.**
> Desplegado en Google Cloud VM + GitHub Actions para cobertura máxima.

---

## 🚀 ¿Qué hace este bot?

1. **Scraping multi-canal** — LinkedIn + 6 plataformas remotas (~80-100 ofertas/ciclo)
2. **Filtrado inteligente** — MatchEngine filtra por rol, nivel y idioma
3. **Anti-duplicados** — Nunca postula dos veces al mismo trabajo
4. **Auto-postulación** — Vía ATS (Greenhouse, Lever, Workable) o Cold-Email con CV adjunto
5. **LinkedIn Networking** — Conecta automáticamente con 8 reclutadores de Data/AI por corrida
6. **Notificaciones** — Todo llega a Telegram en tiempo real

---

## 🏗️ Arquitectura

```
main_v6.py
├── src/scrapers/
│   ├── linkedin_scraper.py      ← 🔵 LinkedIn (50% del sourcing)
│   ├── api_scrapers.py          ← Remotive, RemoteOK, GetOnBoard, Jobicy
│   └── latam_scrapers.py        ← WeWorkRemotely, WorkingNomads
├── src/linkedin/
│   ├── recruiter_connector.py   ← Auto-conexión con reclutadores
│   └── linkedin_messenger.py    ← InMail vía Voyager API
├── src/filters/
│   └── match_engine.py          ← Filtrado por perfil
├── src/appliers/
│   ├── router.py                ← Detecta ATS de la oferta
│   ├── greenhouse_applier.py
│   ├── lever_applier.py
│   ├── workable_applier.py
│   └── multitrabajos_applier.py
├── src/email/
│   ├── gmail_sender.py          ← Envío OAuth2
│   └── gmail_reply_bot.py       ← Auto-respuestas de RRHH
├── src/memory/
│   └── memory_store.py          ← Anti-duplicados
├── src/notifications/
│   └── telegram_notifier.py
└── generate_cv_en.py            ← PDF ATS con ReportLab
```

---

## ⚙️ Instalación local

```bash
git clone https://github.com/erick007bon/ai-job-hunter-bot.git
cd ai-job-hunter-bot
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env              # Editar con tus claves
python main_v6.py --dry-run       # Prueba sin postular
python main_v6.py                 # Ejecución real
```

---

## 🌐 Despliegue en Google Cloud (Producción)

La instancia `job-hunter-bot` en `us-east1-c` corre el bot cada 4 horas:

```bash
# En la VM de GCP:
source venv/bin/activate
crontab -e
# Agregar:
0 */4 * * * cd ~/ai-job-hunter-bot && venv/bin/python main_v6.py >> cron.log 2>&1
```

**GitHub Actions** actúa como respaldo paralelo (6 corridas/día).

---

## 🔐 Variables de entorno requeridas

Crear `.env` con:

```ini
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
OPENROUTER_API_KEY=...
EMAIL_USER=eflores4006@utm.edu.ec
EMAIL_PASSWORD=...
EMAIL_SENDER=eflores4006@utm.edu.ec
HUNTER_API_KEY=...
LINKEDIN_LI_AT=...
LINKEDIN_JSESSIONID=...
AUTO_APPLY=true
MAX_APPLICATIONS=5
CV_PATH=data/CV_Erick_Flores_EN.pdf
```

---

## 📊 Métricas del sistema

- **Fuentes activas**: 7 (LinkedIn + 6 APIs/RSS)
- **Ofertas por ciclo**: ~80-100 únicas
- **Filtradas compatibles**: ~5-10 por ciclo
- **Postulaciones por día**: hasta 30 (6 ciclos × 5 apps)
- **Conexiones LinkedIn/día**: hasta 48 (6 ciclos × 8 conexiones)
- **Cobertura**: Global remoto + LATAM

---

## 🧠 Tecnologías

`Python 3.13` · `Playwright` · `BeautifulSoup4` · `ReportLab` · `Gmail API OAuth2`
`LinkedIn Voyager API` · `Hunter.io API` · `OpenRouter (Mistral/Gemini)` · `Telegram Bot API`
`GitHub Actions` · `Google Cloud Compute Engine` · `Debian 13`
