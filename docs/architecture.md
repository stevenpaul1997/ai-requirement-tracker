# System Architecture Document
## AI Requirement Intake & Tracker

| Field | Details |
|---|---|
| **Document Version** | 1.0 |
| **Author** | Steven Saji Paul |
| **Role** | Business Systems Analyst |
| **Date** | June 2026 |
| **Status** | Final |

---

## 1. Architecture Overview

The AI Requirement Intake & Tracker follows a three-tier architecture: a Streamlit frontend, a Python business logic layer, and a dual-database persistence layer. The AI processing layer sits between the business logic and data tiers, acting as an intelligent transformation engine.

┌─────────────────────────────────────────────────────────┐

│                    PRESENTATION TIER                     │

│                  Streamlit Web Application               │

│   Tab 1: Submit │ Tab 2: Tracker │ Tab 3: Trace │ Tab 4 │

└─────────────────────────┬───────────────────────────────┘

│

┌─────────────────────────▼───────────────────────────────┐

│                    BUSINESS LOGIC TIER                   │

│                                                          │

│   ┌─────────────────┐      ┌─────────────────────────┐  │

│   │  Form Processor  │      │      AI Processor        │  │

│   │  (validation,   │─────►│  Groq API                │  │

│   │   orchestration)│      │  llama-3.3-70b-versatile │  │

│   └─────────────────┘      └─────────────────────────┘  │

└──────────────┬──────────────────────────┬───────────────┘

│                          │

┌──────────────▼──────────┐  ┌────────────▼──────────────┐

│      DATA TIER (NoSQL)   │  │    DATA TIER (Relational)  │

│                          │  │                            │

│     MongoDB Atlas        │  │      Neon Postgres         │

│     raw_intake           │  │      requirements          │

│     collection           │  │      user_stories          │

│                          │  │      status_audit          │

│  • Unstructured text     │  │      conflicts             │

│  • Flexible schema       │  │                            │

│  • Document storage      │  │  • Structured output       │

│  • Fast writes           │  │  • Relational queries      │

└──────────────────────────┘  └────────────────────────────┘

---

## 2. The Dual-Database Decision

This is the most architecturally significant decision in the system. The choice to use two databases — one NoSQL, one relational — is deliberate and defensible.

### Why MongoDB for Raw Intake

Requirements intake is inherently unstructured. Every stakeholder describes their need differently:

- One submission might be 2 sentences
- Another might be 10 paragraphs with bullet points
- A third might include URLs, references, and attachments

Forcing this into a rigid relational schema at intake time would mean:
- Designing columns for every possible field upfront
- Losing flexibility as intake forms evolve
- Schema migrations every time a new field is added

MongoDB's document model stores each submission exactly as received — no schema enforcement, no data loss, no migrations. This mirrors how enterprise systems like Salesforce and ServiceNow handle unstructured intake.

### Why Neon Postgres for Structured Output

Once the AI processes a requirement, the output is highly structured and predictable:
- Every requirement has exactly one MoSCoW classification
- Every requirement has exactly one priority
- Every requirement has a status that changes over time
- User stories follow a fixed format

This structured, relational data benefits from:
- SQL queries for filtering and reporting
- Foreign key relationships between requirements, stories, and audit logs
- ACID transactions for status updates
- Joins for the traceability matrix

### The Pattern This Mirrors

This dual-database pattern is common in enterprise systems:

| System | NoSQL Layer | Relational Layer |
|---|---|---|
| E-commerce | Product catalog (varied attributes) | Orders, payments (structured) |
| Healthcare | Patient notes (free text) | Appointments, billing (structured) |
| HR Systems | Resumes, cover letters | Employee records, payroll |
| This App | Raw requirement intake | User stories, lifecycle, audit |

---

## 3. Component Architecture
ai-requirement-tracker/

│

├── app.py                          # Entry point

│   └── initialize_tables()         # Creates Postgres schema on startup

│   └── Tab routing                 # Renders correct component per tab

│

├── database/

│   ├── mongo_client.py

│   │   ├── get_collection()        # MongoDB connection

│   │   ├── insert_raw_intake()     # Write raw requirement

│   │   ├── mark_as_processed()     # Update processed flag

│   │   ├── get_all_raw_intake()    # Read all documents

│   │   ├── get_raw_by_id()         # Read single document

│   │   └── get_all_titles_and_descriptions() # For conflict detection

│   │

│   └── postgres_client.py

│       ├── initialize_tables()     # Schema creation

│       ├── insert_requirement()    # Write structured requirement

│       ├── insert_user_stories()   # Write user stories

│       ├── insert_conflict()       # Write conflict records

│       ├── update_status()         # Update + audit log

│       ├── get_all_requirements()  # Read all with story count

│       ├── get_requirement_with_stories() # Read full detail

│       └── get_all_for_traceability()    # Read for matrix

│

├── ai/

│   └── processor.py

│       ├── process_requirement()   # Main AI processing function

│       └── generate_priority_score() # Role-based priority weighting

│

└── components/

├── intake_form.py              # Tab 1 — Submit

├── tracker.py                  # Tab 2 — Lifecycle

├── traceability.py             # Tab 3 — Matrix

└── analytics.py               # Tab 4 — Charts

---

## 4. Data Flow

### Submission Flow
User fills form

│

▼

Form validation (all required fields present)

│

▼

insert_raw_intake() → MongoDB Atlas

│ returns mongo_id

▼

get_all_titles_and_descriptions() → fetch existing for conflict check

│

▼

process_requirement() → Groq API

│ returns {user_stories, moscow, priority, conflicts}

▼

insert_requirement() → Postgres requirements table

│ returns req_id

▼

insert_user_stories() → Postgres user_stories table

│

▼

insert_conflict() → Postgres conflicts table (if conflicts found)

│

▼

Display results to user

### Status Update Flow
BA selects new status

│

▼

update_status() called with req_id, new_status, old_status

│

├── UPDATE requirements SET status = new_status

│

└── INSERT INTO status_audit (req_id, old_status, new_status, timestamp)

### Traceability Query Flow
BA opens Traceability tab

│

▼

get_all_for_traceability()

│

▼

SELECT r.*, us.story, us.acceptance_criteria

FROM requirements r

LEFT JOIN user_stories us ON r.id = us.requirement_id

ORDER BY r.id

│

▼

Render colored dataframe

│

▼

Optional CSV export

---

## 5. Security Architecture

| Area | Implementation |
|---|---|
| API Keys | Stored in .env file, never in source code |
| .env Protection | Listed in .gitignore, excluded from all commits |
| Database Connections | SSL enforced on both MongoDB and Neon Postgres |
| Secret Scanning | GitHub push protection enabled on repo |
| Credentials Rotation | All credentials rotated after any accidental exposure |

---

## 6. Deployment Architecture

### Local Development
Developer Machine

└── VS Code

└── Python 3.12

└── Streamlit (localhost:8501)

├── MongoDB Atlas (cloud)

└── Neon Postgres (cloud)

### Production (Streamlit Cloud)
Streamlit Cloud

└── app.py

├── Secrets Manager (replaces .env)

├── MongoDB Atlas (cloud)

└── Neon Postgres (cloud)

---

## 7. Technology Decisions

| Decision | Option Chosen | Alternatives Considered | Reason |
|---|---|---|---|
| Frontend | Streamlit | Flask, FastAPI, React | Fastest Python-native UI for data apps |
| AI Model | Groq llama-3.3-70b | OpenAI GPT-4, Gemini | Free tier, fastest inference, confirmed working |
| NoSQL DB | MongoDB Atlas | Firebase, DynamoDB | Industry standard, generous free tier |
| Relational DB | Neon Postgres | Supabase, PlanetScale | Serverless Postgres, scales to zero |
| Visualization | Plotly | Matplotlib, Altair | Interactive charts, Streamlit native integration |