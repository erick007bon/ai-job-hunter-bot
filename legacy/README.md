# Scripts archivados (no se usan en producción)

Estos archivos fueron versiones anteriores del orquestador principal.
El workflow de GitHub Actions (`.github/workflows/job_hunter.yml`) solo
ejecuta **`main_v6.py`** (más `scholarship_hunter.py`). Nada en el
pipeline activo importa estos scripts.

Se movieron aquí en vez de borrarse para no perder el historial/contexto,
pero no deben tomarse como referencia de cómo funciona el bot hoy:

- `job_hunter.py` — primera versión, solo Remotive + RemoteOK, sin filtrado
  por seniority ni envío de emails.
- `main_v3.py` — versión con Hunter.io + Gemini + InMail de LinkedIn (Fase 2).
  Es la única versión que sí conectaba el extractor de emails con el envío;
  esa lógica se portó a `main_v6.py` el 2026-08-04.
- `main_v5.py` — versión intermedia, sin auto-apply vía Playwright.

Si vas a revivir alguno de estos, primero confirma que no reintroduce los
bugs ya corregidos en `main_v6.py` (extracción de emails desconectada,
duplicados sin filtrar, respuestas en blanco en formularios).
