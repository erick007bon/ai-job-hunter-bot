# 🧠 MISSION BRAIN — AI Job Hunter V6 (Autonomous Engineering System)
> Estado: **AUTO-POSTULACIÓN MULTI-CANAL ACTIVA** | CI/CD: **GitHub Actions 6x/día**

---

## 🎯 Arquitectura de Optimización de Procesos (Ingeniería de Automatización)

Este proyecto es un sistema de ingeniería autónomo para optimizar el embudo de colocación laboral en Data Science, IA y Economía. Opera como un pipeline distribuido de extremo a extremo:

```
┌────────────────────────────────────────────────────────┐
│  GITHUB ACTIONS CRON (6x al día — Horario Ecuador 🇪🇨) │
│  07:00 AM | 10:00 AM | 01:00 PM | 04:00 PM | 07:00 PM  │
└──────────────────────────┬─────────────────────────────┘
                           │
             ┌─────────────▼─────────────┐
             │  1. OMNISCAPE MULTI-CANAL │
             │  Remotive, RemoteOK,      │
             │  GetOnBoard, Jobicy,      │
             │  WeWorkRemotely, Nomads   │
             └─────────────┬─────────────┘
                           │
             ┌─────────────▼─────────────┐
             │  2. NLP MATCH ENGINE      │
             │  Filtra Data/AI/Econ      │
             │  Excluye Senior/Lead      │
             └─────────────┬─────────────┘
                           │
             ┌─────────────▼─────────────┐
             │  3. DEDUPLICACIÓN & MEM   │
             │  MemoryStore (JSON)       │
             │  FunnelDB (SQLite)        │
             └─────────────┬─────────────┘
                           │
             ┌─────────────▼─────────────┐
             │  4. ENRIQUECIMIENTO RRHH  │
             │  Hunter.io API            │
             └─────────────┬─────────────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
  ┌──────────▼──────────┐     ┌──────────▼──────────┐
  │ RUTA ATS AUTOMÁTICA │     │ RUTA COLD-EMAIL     │
  │ Playwright headless │     │ SMTP directo /      │
  │ Greenhouse, Lever,  │     │ Gmail API           │
  │ Workable, Ashby     │     │ Cover Letter IA     │
  │ (Auto-formulario)   │     │ CV PDF adjunto      │
  └──────────┬──────────┘     └──────────┬──────────┘
             │                           │
             └─────────────┬─────────────┘
                           │
             ┌─────────────▼─────────────┐
             │ 5. TELEGRAM + LINKEDIN    │
             │ Notificaciones en tiempo  │
             │ real + Easy Apply Bot     │
             │ + Scholarship Hunter      │
             └───────────────────────────┘
```

---

## 🚀 Módulos del Ecosistema

### 1. 📧 Auto-Postulación por Correo (Cold-Email con IA)
- **Motor de IA:** Generación dinámica de Cover Letters personalizadas usando `OpenRouter` (Mistral/Gemini) analizando el Job Description.
- **Motor de Envío:** Soporte dual: **SMTP directo autenticado** (sin vencimiento de token) + **Gmail OAuth2**.
- **Generación de CV:** PDF generado con ReportLab sin sobremontado de texto, tipografía optimizada ATS y codificación en `CV_PDF_B64`.

### 2. 🤖 LinkedIn Easy Apply Bot (Headless / Invisible)
- **Ejecución:** Workflow `linkedin_demo.yml` (automático diario 8:00 AM y dispatch manual).
- **Mecanismo:** Inyección de sesión con cookies `LINKEDIN_LI_AT` y `LINKEDIN_JSESSIONID` en Chromium headless.
- **Acción:** Búsqueda de posiciones remotas con "Solicitud sencilla", llenado de formularios EEO, respuesta a preguntas de reclutadores y carga automática del CV PDF.

### 3. 🎓 Scholarship Hunter (Cazador de Becas Internacionales)
- Se ejecuta automáticamente a las **07:00 AM** todos los días.
- Rastrea convocatorias internacionales de becas para maestrías y certificaciones en Inteligencia Artificial y Economía, enviando el reporte a Telegram.

### 4. 📊 Funnel Analytics (FunnelDB)
- Base de datos SQLite (`data/funnel.db`) que registra cada intento, portal, éxito/fallo y clasificación de respuestas recibidas.

---

## 📈 Roadmap de Escalabilidad (Llevarlo al Siguiente Nivel)

1. **Servidor Dedicado / VPS (Contabo / Hetzner / AWS EC2 Free Tier):**
   - Para correr Playwright con perfil de navegador persistente y bypass total de Cloudflare/Datadome mediante proxies residenciales.
2. **Pool de Proxies Residenciales (BrightData / Webshare):**
   - Evita rate-limiting al consultar 50+ plataformas por hora.
3. **Agente Conversacional con MCP (Model Context Protocol):**
   - Responder automáticamente a correos de reclutadores agendando entrevistas en Google Calendar.
