# 🧠 MISSION BRAIN — AI JOB HUNTER V4
**Estado: 🟢 PRODUCCION AUTONOMA 24/7 (Fase 1, 2 y 3)**
**Ultima actualizacion: 15 Mayo 2026**

---

## 🎯 ARQUITECTURA DEL SISTEMA V4 (El Trinomio)

El sistema ahora opera de forma completamente autonoma desde los servidores de GitHub Actions, ejecutando 3 fases tacticas independientes para maximizar las oportunidades laborales.

### 🌐 FASE 1: Omniscape & Emailing (Cada 6 Horas)
1. **Scraping Multi-Canal (12 Plataformas):**
   - Google Jobs, Indeed, Glassdoor (Via `python-jobspy` - ¡NUEVO!)
   - LinkedIn, Remotive, RemoteOK, GetOnBoard, Torre, WeWorkRemotely, WorkingNomads, Computrabajo, SocioEmpleo.
2. **Filtrado NLP:** Filtra roles Entry/Mid-level descartando Senior/Lead.
3. **Hunter.io:** Extrae correos directos de los dominios de las empresas.
4. **Gemini AI:** Redacta Cover Letters hiper-personalizadas al JD.
5. **Generacion Dinamica:** Compila CV en PDF en-vuelo usando `reportlab` (Ingles/Español segun rol).
6. **Gmail API OAuth2:** Envia el correo directo al reclutador.

### 🚀 FASE 2: LinkedIn InMail Direct Access
Por cada rol procesado, el bot busca reclutadores de esa empresa en LinkedIn.
1. Utiliza **LinkedIn Voyager API** (Ingenieria Inversa) saltandose limites basicos.
2. Extrae Top-3 skills del Job Description usando NLP.
3. Redacta un **InMail Corto** conectando las skills con el **Portafolio Real** (FCH-ARX V4, Trading LSTM, etc).
4. El InMail apela a la humildad: "Solo pido una oportunidad para demostrar mi valia tecnica".

### 🤝 FASE 3: Recruiter Connection Network (Diario, 7:00 AM)
Modulo de crecimiento pasivo de red enfocado en roles Data/AI.
1. **Target:** 10 nuevos reclutadores de IA/Datos al dia (50+ semanales).
2. **Contexto:** Lee el area del reclutador (Tech, Talent, Data).
3. **Invitacion AI:** Envia nota de conexion contextual a su area con link directo al GitHub.
4. **Proteccion Anti-Ban:** Memoriza los perfiles contactados para jamas enviar duplicados. Pausas aleatorias (20-45s) simulando humanos.

---

## 🔒 SEGURIDAD Y DEPLOYMENT (CI/CD)

Todo el codigo se ejecuta en **GitHub Actions (Ubuntu Server)**.
Los secretos estan inyectados via variables de entorno, evitando quemarlos en codigo fuente.

**Secretos en Github:**
- `GMAIL_CREDENTIALS_B64`
- `GMAIL_TOKEN_B64`
- `HUNTER_API_KEY`
- `LINKEDIN_LI_AT`
- `LINKEDIN_JSESSIONID`
- `OPENROUTER_API_KEY`
- `EMAIL_SENDER`

---

## 🛠️ CAMBIOS RECIENTES (LOG)

- **[FIX]** Dependencias de Windows (`pywin32`) eliminadas del `requirements.txt`. El bot ahora compila y corre perfecto en Linux (Ubuntu/Actions).
- **[FEATURE]** Integrado `python-jobspy` para capturar Google Jobs, Indeed y Glassdoor (suma ~130 vacantes nuevas al pool diario).
- **[FEATURE]** Construido `RecruiterConnector` (Fase 3) para automatizar networking con Headhunters.
- **[MIGRACION]** Todo el proyecto se esta sincronizando con el repositorio `BOT-DE-ENCONTRAR-TRABAJO` para presentacion publica de portafolio (como experto en automatizacion/IA).

---

## 📋 PASOS MANUALES PENDIENTES (USUARIO)
El bot hace el 90% del trabajo pesado (encontrar ofertas, descifrar correos, redactar y enviar cold-emails).
**El 10% que te toca a ti:**
1. Monitorear tu bandeja `eflores4006@utm.edu.ec` para respuestas reales.
2. Abrir `OPORTUNIDADES_HOY.md` en GitHub y aplicar manualmente en 3 o 4 vacantes top del dia.
3. Optimizar perfil de LinkedIn (Foto profesional, Titular de Data Scientist, Banner) para cuando los reclutadores de la Fase 3 acepten la solicitud.
