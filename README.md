# 🤖 AI Job Hunter Agent — Autonomous Headhunting & Application Pipeline

![Status](https://img.shields.io/badge/Status-Active%20(Production)-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Architecture](https://img.shields.io/badge/Architecture-Autonomous%20AI%20Agent-purple)

An enterprise-grade, fully autonomous AI agent designed to revolutionize the job search process. By orchestrating a multi-layered pipeline of web scrapers, Natural Language Processing (NLP), and cloud APIs, this agent autonomously discovers remote opportunities in Data Science and AI, reverse-engineers recruiter contact information, generates hyper-personalized cover letters, and executes direct outreach via Email and LinkedIn InMail.

---

## 🎯 Core Capabilities (The Trinity Pipeline)

### Phase 1: Omniscape & Automated Application
The agent scans 12 different platforms simultaneously to find high-probability matches.
- **Aggregators:** Google Jobs, Indeed, Glassdoor (via `jobspy` integration).
- **Specialized Boards:** RemoteOK, Remotive, GetOnBoard, WeWorkRemotely, WorkingNomads.
- **LATAM Integration:** Torre.ai, Computrabajo, SocioEmpleo.
- **Workflow:** 
  1. Identifies entry/mid-level roles (filtering out senior noise).
  2. Extracts verified corporate emails via **Hunter.io API**.
  3. Uses **Gemini AI (LLM)** to draft custom cover letters aligned strictly with the Job Description.
  4. Generates a dynamic PDF CV (English/Spanish depending on the role) using `reportlab`.
  5. Dispatches the application directly to the hiring manager via **Gmail OAuth2 API**.

### Phase 2: Direct LinkedIn InMail Injection
Applying to the portal is rarely enough. The agent leverages the **LinkedIn Voyager API** (internal endpoint) to bypass standard limitations and reach decision-makers directly.
- Maps the target company to its LinkedIn corporate page.
- Finds technical recruiters or talent acquisition managers at that specific company.
- Extracts the Top 3 required skills from the original Job Description using NLP.
- Sends a highly targeted, 300-character InMail connecting the candidate's real-world portfolio (e.g., NIST-approved cryptographic algorithms, LSTM trading bots) directly to those 3 skills.

### Phase 3: Autonomous Networking (Recruiter Graph Expansion) [DISABLED FOR SECURITY]
To build a passive funnel of opportunities, the agent *can* run a scheduled daily cron job to expand the professional network.
**Note (May 2026):** This phase is currently disabled by design to strictly protect the user's LinkedIn account from being flagged for spam or automated mass connections with 3rd-degree profiles.
- Autonomously searches for "Data Science Recruiter", "AI Talent Acquisition", etc.
- Sends 10 targeted connection requests daily (50+ weekly) with a personalized introductory note.
- Maintains a local vector log to ensure 0% duplicate outreach and simulates human pacing (anti-ban heuristics).

---

## 🏗️ Technical Architecture

- **Language:** Python 3.11
- **Deployment:** Serverless GitHub Actions (Ubuntu CI/CD)
- **AI/NLP Engine:** Google Gemini via OpenRouter API
- **Web Scraping:** Beautiful Soup 4, lxml, python-jobspy
- **Authentication:** OAuth 2.0 (Gmail), Session Cookies (LinkedIn Voyager)
- **Document Generation:** ReportLab (Dynamic PDF compilation in-flight)

---

## 🔒 Security & Privacy First

This repository is designed with strict security boundaries. **No credentials or secrets are hardcoded in the source.**
- Uses `python-dotenv` for local environments.
- Relies on injected GitHub Secrets (`GMAIL_TOKEN_B64`, `LINKEDIN_LI_AT`, `HUNTER_API_KEY`) for production runs.
- All sensitive `.json` and `.env` files are strictly enforced in `.gitignore`.

---

## 🚀 Why this exists?
Traditional job hunting is a numbers game governed by applicant tracking systems (ATS) that filter out candidates without a human ever seeing their resume. This agent shifts the paradigm from "passive applying" to "aggressive, intelligent headhunting"—putting the candidate's portfolio directly into the inbox and LinkedIn DMs of the actual decision-makers.

*Built by [Erick Flores Zambrano](https://github.com/erick007bon) — Economist, Data Scientist, and AI Engineer.*
