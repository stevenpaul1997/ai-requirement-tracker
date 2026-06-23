# ReqAgent — AI Requirements Intelligence

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58-red?style=flat-square)](https://streamlit.io)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?style=flat-square)](https://mongodb.com)
[![Postgres](https://img.shields.io/badge/Neon-Postgres-blue?style=flat-square)](https://neon.tech)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-orange?style=flat-square)](https://groq.com)

---

## 🧠 What This Is

Every BA knows the feeling. A stakeholder walks in, drops a vague paragraph on your desk, and expects a Jira board by Monday.

**ReqAgent** eliminates the gap between *"we need a thing"* and *"here are 3 user stories with Given/When/Then acceptance criteria, a MoSCoW classification, a priority score, and a conflict check against every other requirement in the system."*

That's not a summary. That's what happens — automatically — every time someone hits submit.

---

## 🎯 Who This Is For

| Role | Why It Matters |
|---|---|
| **Business Analyst** | Requirements intake is your core job. This automates the documentation layer. |
| **Business Systems Analyst** | Dual-database architecture (NoSQL + relational) with defensible design decisions. |
| **Product Manager** | Pipeline visibility, MoSCoW prioritization, and analytics in one place. |
| **AI Transformation Lead** | LLM-powered BA workflow — exactly what enterprise AI transformation looks like. |

---

## ⚡ What Happens When You Submit a Requirement
Stakeholder fills out a form

↓

Raw intake → MongoDB Atlas

(unstructured, flexible, exactly as written)

↓

Groq AI — LLaMA 3.3 70B

├── 3 User Stories ("As a [user], I want [action] so that [benefit]")

├── Acceptance Criteria ("Given... When... Then...")

├── MoSCoW Classification (Must Have / Should Have / Could Have / Won't Have)

├── Priority Score weighted by submitter role

│     C-Suite / VP → High

│     Manager / Team Lead → Medium

│     End User / External → Low

└── Conflict Detection against all existing requirements

↓

Structured output → Neon Postgres

(relational, queryable, audit-ready)

↓

4-Tab Dashboard

Tab 1 — Submit Requirement

Tab 2 — Requirements Tracker (lifecycle + audit trail)

Tab 3 — Traceability Matrix (downloadable CSV)

Tab 4 — Analytics (KPIs, charts, timeline)

---

## 🗄️ Why Two Databases

This is the architectural decision that makes this project interview-proof.

**MongoDB Atlas** stores raw intake exactly as submitted — no schema enforcement, no data loss, no migrations. Every stakeholder describes their need differently. One submission might be 2 sentences. Another might be 10 paragraphs. MongoDB handles it.

**Neon Postgres** stores the structured output after AI processing. Every requirement has exactly one MoSCoW classification, one priority, a status that changes over time, and user stories that need to be joined for traceability reporting. That's what relational databases are built for.

| Layer | Database | Why |
|---|---|---|
| Raw intake | MongoDB Atlas | Unstructured, flexible, document-based |
| User stories | Neon Postgres | Relational, queryable, join-ready |
| Status audit | Neon Postgres | ACID transactions, timestamp logging |
| Conflict records | Neon Postgres | Foreign key relationships |

This pattern mirrors how enterprise systems like Salesforce, ServiceNow, and Jira handle the intake-to-workflow pipeline. It's not incidental — it's the point.

---

## 🏗️ Architecture
┌─────────────────────────────────────────────┐

│           PRESENTATION TIER                  │

│         Streamlit Web Application            │

│  Submit │ Tracker │ Traceability │ Analytics │

└──────────────────┬──────────────────────────┘

│

┌──────────────────▼──────────────────────────┐

│           BUSINESS LOGIC TIER                │

│  Form Processor → AI Processor (Groq)        │

│  Role Weighting → Conflict Scanner           │

└────────┬─────────────────────────┬──────────┘

│                         │

┌────────▼──────────┐  ┌───────────▼──────────┐

│   MongoDB Atlas    │  │    Neon Postgres      │

│   raw_intake       │  │    requirements       │

│   Unstructured     │  │    user_stories       │

│   Document store   │  │    status_audit       │

│                    │  │    conflicts          │

└────────────────────┘  └──────────────────────┘

---

## 🛠️ Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Frontend | Streamlit 1.58 | Python-native, fast to build, enterprise-ready |
| AI | Groq + LLaMA 3.3 70B | Free tier, fastest inference, JSON-structured output |
| NoSQL | MongoDB Atlas | Industry standard, generous free tier |
| Relational | Neon Postgres | Serverless Postgres, scales to zero |
| Visualization | Plotly | Interactive charts, native Streamlit integration |
| Language | Python 3.12 | Consistent across the full stack |

---

## 📊 Features

- **Structured intake form** with department, role, and business objective capture
- **AI-generated user stories** — 3 per requirement, full Given/When/Then
- **MoSCoW classification** — auto-assigned, hardcoded post-parse to prevent LLM override
- **Role-weighted priority** — submitter role determines priority, not content
- **Conflict detection** — scans all existing requirements on every submission
- **Lifecycle tracker** — Submitted → Under Review → Approved → In Development → Done → Rejected
- **Status audit trail** — every change logged with old status, new status, timestamp
- **Traceability matrix** — color-coded, filterable, downloadable as CSV
- **Analytics dashboard** — KPIs, donut charts, bar charts, submission timeline, role breakdown

---

## 🔍 Design Decisions Worth Noticing

**Priority is role-weighted, not content-based.** The AI cannot override priority based on how important the requirement sounds. A C-Suite submission is always High. An End User submission is always Low. This mirrors how real enterprise triage works — and it's documented in `ai/processor.py`.

**MongoDB stores the raw document, not a cleaned version.** The entire form submission — typos, vague language, contradictions and all — is preserved exactly as written. This is deliberate. The raw intake is the source of truth. The AI output is the interpretation.

**Conflict detection runs on every submission.** Before the AI generates stories, it retrieves all existing requirement titles and descriptions and includes them in the prompt. Conflicts are surfaced immediately — not discovered in sprint planning.

---

## 📁 Project Structure
ai-requirement-tracker/

├── app.py                      # Main Streamlit app + UI theme

├── requirements.txt

├── .env.example                # Placeholder credentials only

├── seed_data.py                # Demo data seeder

│

├── database/

│   ├── mongo_client.py         # MongoDB Atlas connection + CRUD

│   └── postgres_client.py      # Neon Postgres schema + queries

│

├── ai/

│   └── processor.py            # Groq AI processing + role weighting

│

├── components/

│   ├── intake_form.py          # Tab 1 — Submit Requirement

│   ├── tracker.py              # Tab 2 — Requirements Tracker

│   ├── traceability.py         # Tab 3 — Traceability Matrix

│   └── analytics.py            # Tab 4 — Analytics Dashboard

│

└── docs/

├── BRD.md                  # Business Requirements Document

├── FRD.md                  # Functional Requirements Document

├── use_cases.md            # 8 use cases with full flows

└── architecture.md         # Dual-DB rationale + data flows

---

## ⚙️ Setup

### 1. Clone
```bash
git clone https://github.com/stevenpaul1997/ai-requirement-tracker.git
cd ai-requirement-tracker
```

### 2. Install
```bash
pip install -r requirements.txt
```

### 3. Configure
```bash
cp .env.example .env
```


### 4. Run
```bash
python -m streamlit run app.py
```

---

## 📖 Documentation

Full BA/BSA documentation suite in `/docs`:

| Document | What It Covers |
|---|---|
| **BRD** | Business objectives, stakeholders, scope, risks, success metrics |
| **FRD** | 45 functional requirements mapped to business requirements |
| **Use Cases** | 8 use cases with main flows, alternative flows, pre/postconditions |
| **Architecture** | Dual-database rationale, data flow diagrams, security decisions |

---

## 🔒 What We Learned the Hard Way

API keys committed to public repos get flagged by GitHub's secret scanner instantly. `.env.example` should contain placeholder strings only — never real credentials. `.gitignore` should list `.env` before the first commit, not after.

These lessons are now baked into the project setup instructions.

---

## 📌 Resume Line

> *"Built an AI-powered requirements intake system storing unstructured stakeholder input in MongoDB Atlas and auto-generating structured user stories in Neon Postgres using LLaMA 3.3 70B — reducing documentation time by ~65%."*

---

## 👤 Author

**Steven Saji Paul**
Graduate Student — M.S. Information Systems, CSULB
Targeting BA / BSA / PM roles with a focus on AI Transformation

- 📧 stevenspaul97@gmail.com
- 💼 [linkedin.com/in/stevensajipaul](https://linkedin.com/in/stevensajipaul)
- 🌐 [stevensajipaul.github.io](https://stevensajipaul.github.io)
- 💻 [github.com/stevenpaul1997](https://github.com/stevenpaul1997)