# Functional Requirements Document (FRD)
## AI Requirement Intake & Tracker

| Field | Details |
|---|---|
| **Document Version** | 1.0 |
| **Author** | Steven Saji Paul |
| **Role** | Business Systems Analyst |
| **Date** | June 2026 |
| **Status** | Final |

---

## 1. Purpose

This document defines the functional requirements for the AI Requirement Intake & Tracker system. It translates the business requirements defined in the BRD into specific, testable system behaviors.

---

## 2. System Overview

The system consists of four functional modules:

| Module | Description |
|---|---|
| **Intake Form** | Stakeholder-facing form for requirement submission |
| **AI Processor** | LLM-powered analysis and story generation |
| **Data Layer** | Dual-database storage (MongoDB + Neon Postgres) |
| **Dashboard** | Four-tab interface for tracking, traceability, and analytics |

---

## 3. Functional Requirements

### 3.1 Intake Form Module

| ID | Requirement | Business Requirement |
|---|---|---|
| FR-01 | System shall provide text input for requirement title (max 500 chars) | BR-01 |
| FR-02 | System shall provide free-text area for requirement description | BR-01 |
| FR-03 | System shall provide dropdown for department selection | BR-01 |
| FR-04 | System shall provide dropdown for submitter role selection | BR-01 |
| FR-05 | System shall provide text input for business objective | BR-01 |
| FR-06 | System shall provide optional text area for additional notes | BR-01 |
| FR-07 | System shall validate all required fields before submission | BR-01 |
| FR-08 | System shall display AI results immediately after submission | BR-02 |

---

### 3.2 AI Processing Module

| ID | Requirement | Business Requirement |
|---|---|---|
| FR-09 | System shall generate exactly 3 user stories per requirement | BR-02 |
| FR-10 | User stories shall follow "As a [user], I want [action] so that [benefit]" format | BR-02 |
| FR-11 | Each user story shall include 2-3 acceptance criteria in Given/When/Then format | BR-02 |
| FR-12 | System shall assign one MoSCoW classification per requirement | BR-03 |
| FR-13 | System shall assign priority (High/Medium/Low) with written justification | BR-04 |
| FR-14 | System shall scan all existing requirements for conflicts on each submission | BR-05 |
| FR-15 | System shall return conflict description or "No conflicts detected" | BR-05 |
| FR-16 | AI processing shall complete within 10 seconds | BR-02 |

---

### 3.3 Data Layer Module

| ID | Requirement | Business Requirement |
|---|---|---|
| FR-17 | System shall store raw intake document in MongoDB Atlas | BR-10 |
| FR-18 | MongoDB document shall include title, description, department, role, objective, notes, timestamp | BR-10 |
| FR-19 | System shall store structured user stories in Neon Postgres | BR-10 |
| FR-20 | Postgres shall maintain requirements table with status, priority, MoSCoW columns | BR-10 |
| FR-21 | Postgres shall maintain user_stories table linked to requirements | BR-10 |
| FR-22 | Postgres shall maintain status_audit table for all status changes | BR-07 |
| FR-23 | Postgres shall maintain conflicts table for detected conflicts | BR-05 |
| FR-24 | MongoDB document ID shall be stored in Postgres for cross-reference | BR-10 |

---

### 3.4 Requirements Tracker Module

| ID | Requirement | Business Requirement |
|---|---|---|
| FR-25 | System shall display all requirements in an expandable list | BR-06 |
| FR-26 | System shall support filtering by status, priority, and MoSCoW | BR-06 |
| FR-27 | System shall display status, priority, MoSCoW, submitter, and department per requirement | BR-06 |
| FR-28 | System shall allow status updates via dropdown | BR-06 |
| FR-29 | Status options: Submitted, Under Review, Approved, In Development, Done, Rejected | BR-06 |
| FR-30 | System shall log every status change with old status, new status, and timestamp | BR-07 |
| FR-31 | System shall display full user stories and acceptance criteria on demand | BR-02 |
| FR-32 | System shall display original raw intake from MongoDB on demand | BR-10 |
| FR-33 | System shall display complete audit trail per requirement | BR-07 |

---

### 3.5 Traceability Matrix Module

| ID | Requirement | Business Requirement |
|---|---|---|
| FR-34 | System shall display a matrix linking requirements to user stories | BR-08 |
| FR-35 | Matrix shall include REQ ID, title, submitter, department, status, priority, MoSCoW, story, criteria | BR-08 |
| FR-36 | Matrix shall support filtering by status and MoSCoW | BR-08 |
| FR-37 | Matrix shall apply color coding to status, priority, and MoSCoW columns | BR-08 |
| FR-38 | System shall provide CSV export of the full matrix | BR-08 |

---

### 3.6 Analytics Module

| ID | Requirement | Business Requirement |
|---|---|---|
| FR-39 | System shall display KPI metrics: total, approved, high priority, must have | BR-09 |
| FR-40 | System shall display requirements by status as donut chart | BR-09 |
| FR-41 | System shall display MoSCoW breakdown as pie chart | BR-09 |
| FR-42 | System shall display requirements by department as horizontal bar chart | BR-09 |
| FR-43 | System shall display requirements by priority as bar chart | BR-09 |
| FR-44 | System shall display submissions over time as line chart | BR-09 |
| FR-45 | System shall display submissions by role as bar chart | BR-09 |

---

## 4. Non-Functional Requirements

| ID | Requirement | Category |
|---|---|---|
| NFR-01 | App shall load within 3 seconds on standard connection | Performance |
| NFR-02 | AI processing shall complete within 10 seconds | Performance |
| NFR-03 | API keys shall never be stored in source code | Security |
| NFR-04 | All database connections shall use SSL | Security |
| NFR-05 | App shall be deployable on Streamlit Cloud | Portability |
| NFR-06 | Codebase shall follow modular architecture | Maintainability |

---

## 5. Data Dictionary

### MongoDB — raw_intake collection

| Field | Type | Description |
|---|---|---|
| _id | ObjectId | Auto-generated document ID |
| title | String | Requirement title |
| description | String | Full requirement description |
| department | String | Submitting department |
| submitted_by | String | Submitter name |
| role | String | Submitter role |
| business_objective | String | Business objective |
| additional_notes | String | Optional notes |
| submitted_at | DateTime | Submission timestamp |
| processed | Boolean | Whether AI has processed this document |

### Neon Postgres — requirements table

| Column | Type | Description |
|---|---|---|
| id | SERIAL PK | Auto-incremented requirement ID |
| mongo_id | VARCHAR | Reference to MongoDB document |
| title | VARCHAR | Requirement title |
| submitted_by | VARCHAR | Submitter name |
| department | VARCHAR | Department |
| role | VARCHAR | Submitter role |
| status | VARCHAR | Current lifecycle status |
| priority | VARCHAR | AI-assigned priority |
| moscow | VARCHAR | MoSCoW classification |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### Neon Postgres — user_stories table

| Column | Type | Description |
|---|---|---|
| id | SERIAL PK | Auto-incremented story ID |
| requirement_id | INTEGER FK | Reference to requirements table |
| story | TEXT | User story text |
| acceptance_criteria | TEXT | Acceptance criteria text |
| created_at | TIMESTAMP | Creation timestamp |

---

## 6. System Interfaces

| Interface | Type | Description |
|---|---|---|
| Groq API | External REST API | LLM processing via llama-3.3-70b-versatile |
| MongoDB Atlas | Cloud Database | Raw intake document storage |
| Neon Postgres | Cloud Database | Structured relational storage |
| Streamlit | Web Framework | Frontend rendering |