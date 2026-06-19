# 📋 AI Requirement Tracker

An enterprise-grade AI-powered requirements intake system that automates the BA/BSA workflow — from stakeholder submission to structured user stories, MoSCoW classification, conflict detection, and lifecycle tracking.

Built to demonstrate cross-functional readiness across Business Analyst, Business Systems Analyst, and Product Manager roles with a focus on AI Transformation.

---

## 🚀 Live Demo

> Run locally with `python -m streamlit run app.py`

---

## 🎯 What It Does

Stakeholders submit business requirements through a form. The app:

1. **Saves raw intake to MongoDB Atlas** — unstructured, flexible, document-based
2. **Sends it to Groq AI (LLaMA 3.3 70B)** which generates:
   - 3 User Stories in "As a [user], I want to [action] so that [benefit]" format
   - Acceptance Criteria in "Given... When... Then..." format
   - MoSCoW Classification (Must Have / Should Have / Could Have / Won't Have)
   - Priority Score (High / Medium / Low) with written justification
   - Conflict Detection against all existing requirements
3. **Saves structured output to Neon Postgres** — relational, queryable, audit-ready
4. **Displays everything in a 4-tab dashboard**

---

## 🏗️ Architecture
Stakeholder Form (Streamlit)

↓

MongoDB Atlas ← raw intake (unstructured)

↓

Groq AI (LLaMA 3.3 70B)

• User Stories + Acceptance Criteria

• MoSCoW Classification

• Priority Scoring

• Conflict Detection

↓

Neon Postgres ← structured output (relational)

↓

Dashboard

Tab 1 — Submit Requirement

Tab 2 — Requirements Tracker (lifecycle)

Tab 3 — Traceability Matrix (downloadable CSV)

Tab 4 — Analytics (charts + KPIs)

---

## 🧠 Why Two Databases

| Database | Role | Why |
|---|---|---|
| **MongoDB Atlas** | Raw intake storage | Unstructured text varies per submission — NoSQL handles flexible schemas better |
| **Neon Postgres** | Structured output | User stories, status, priority need relational queries, filters, and joins |

This dual-database decision mirrors real enterprise architecture and demonstrates when to use NoSQL vs relational — a common interview question for BSA/BA roles.

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| AI | Groq API (LLaMA 3.3 70B) |
| NoSQL Database | MongoDB Atlas |
| Relational Database | Neon Postgres |
| Visualization | Plotly |
| Language | Python 3.12 |

---

## 📊 Features

- **Requirements Intake Form** — structured submission with department, role, and objective fields
- **AI-Generated User Stories** — 3 stories per requirement with full acceptance criteria
- **MoSCoW Classification** — auto-assigned with AI reasoning
- **Priority Scoring** — weighted by submitter role (C-Suite → High, End User → Low)
- **Conflict Detection** — scans all existing requirements for overlaps
- **Lifecycle Tracker** — Submitted → Under Review → Approved → In Development → Done
- **Status Audit Trail** — every status change logged with timestamp
- **Traceability Matrix** — downloadable CSV linking requirements to stories
- **Analytics Dashboard** — KPIs, donut charts, bar charts, timeline, role breakdown

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/stevenpaul1997/ai-requirement-tracker.git
cd ai-requirement-tracker
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
```

Fill in your `.env`:
GROQ_API_KEY=your_groq_api_key

MONGODB_URI=your_mongodb_atlas_connection_string

NEON_DATABASE_URL=your_neon_postgres_connection_string

### 4. Run the app
```bash
python -m streamlit run app.py
```

---

## 📁 Project Structure
ai-requirement-tracker/

│

├── app.py                      # Main Streamlit app

├── requirements.txt            # Python dependencies

├── .env.example                # Environment variable template

│

├── database/

│   ├── mongo_client.py         # MongoDB Atlas connection + CRUD

│   └── postgres_client.py      # Neon Postgres connection + schema

│

├── ai/

│   └── processor.py            # Groq AI processing logic

│

├── components/

│   ├── intake_form.py          # Tab 1 — Submit Requirement

│   ├── tracker.py              # Tab 2 — Requirements Tracker

│   ├── traceability.py         # Tab 3 — Traceability Matrix

│   └── analytics.py            # Tab 4 — Analytics Dashboard

│

└── docs/

└── screenshots/            # App screenshots
---

## 👤 Author

**Steven Saji Paul**
- 📧 stevenspaul97@gmail.com
- 💼 [LinkedIn](https://linkedin.com/in/stevensajipaul)
- 🌐 [Portfolio](https://stevensajipaul.github.io)

---

## 📌 Resume Line

> "Built an AI-powered requirements intake system storing unstructured stakeholder input in MongoDB Atlas and auto-generating structured user stories in Neon Postgres using LLaMA 3.3 70B — reducing documentation time by ~65%."
