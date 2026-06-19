# Use Case Document
## AI Requirement Intake & Tracker

| Field | Details |
|---|---|
| **Document Version** | 1.0 |
| **Author** | Steven Saji Paul |
| **Role** | Business Systems Analyst |
| **Date** | June 2026 |
| **Status** | Final |

---

## 1. Actors

| Actor | Description |
|---|---|
| **Stakeholder** | Business user submitting a requirement (any department) |
| **Business Analyst** | Reviews, manages, and approves requirements |
| **AI Processor** | Groq LLM that generates user stories and classifications |
| **System** | The AI Requirement Tracker application |

---

## 2. Use Case Diagram (Text)
Stakeholder ──► UC-01: Submit Requirement

│

▼

System      ──► UC-02: Save Raw Intake to MongoDB

│

▼

AI Processor──► UC-03: Generate User Stories

──► UC-04: Classify MoSCoW

──► UC-05: Assign Priority Score

──► UC-06: Detect Conflicts

│

▼

System      ──► UC-07: Save Structured Output to Postgres

│

▼

BA          ──► UC-08: Review Requirements in Tracker

──► UC-09: Update Requirement Status

──► UC-10: View Traceability Matrix

──► UC-11: Export Traceability CSV

──► UC-12: View Analytics Dashboard

---

## 3. Use Cases

---

### UC-01: Submit Business Requirement

| Field | Details |
|---|---|
| **ID** | UC-01 |
| **Name** | Submit Business Requirement |
| **Actor** | Stakeholder |
| **Trigger** | Stakeholder has a business need to document |
| **Precondition** | Stakeholder has access to the web application |
| **Postcondition** | Requirement is saved and AI analysis is displayed |

**Main Flow:**
1. Stakeholder navigates to the Submit Requirement tab
2. Stakeholder enters requirement title
3. Stakeholder selects department and role from dropdowns
4. Stakeholder enters name and business objective
5. Stakeholder enters detailed requirement description
6. Stakeholder optionally enters additional notes
7. Stakeholder clicks Submit & Generate AI Analysis
8. System validates all required fields
9. System saves raw intake to MongoDB
10. System sends data to AI Processor
11. System displays generated user stories, MoSCoW, priority, and conflict analysis

**Alternative Flow — Validation Failure:**
- At step 8, if required fields are missing, system displays error message and halts submission

---

### UC-02: Save Raw Intake to MongoDB

| Field | Details |
|---|---|
| **ID** | UC-02 |
| **Name** | Save Raw Intake to MongoDB |
| **Actor** | System |
| **Trigger** | Stakeholder submits requirement form |
| **Precondition** | Form validation passes |
| **Postcondition** | Document saved in MongoDB with unique ObjectId |

**Main Flow:**
1. System collects all form fields into a document object
2. System appends submission timestamp
3. System sets processed flag to False
4. System inserts document into MongoDB raw_intake collection
5. System returns MongoDB ObjectId for cross-referencing

---

### UC-03: Generate User Stories

| Field | Details |
|---|---|
| **ID** | UC-03 |
| **Name** | Generate User Stories |
| **Actor** | AI Processor |
| **Trigger** | Raw requirement saved to MongoDB |
| **Precondition** | Valid requirement text available |
| **Postcondition** | 3 user stories with acceptance criteria returned |

**Main Flow:**
1. System constructs prompt with requirement details and existing requirements list
2. System sends prompt to Groq API (llama-3.3-70b-versatile)
3. AI generates 3 user stories in standard format
4. AI generates 2-3 acceptance criteria per story in Given/When/Then format
5. System parses JSON response
6. System returns structured story objects

**Alternative Flow — JSON Parse Failure:**
- System retries API call once
- If second attempt fails, system displays error and logs failure

---

### UC-04: Classify MoSCoW

| Field | Details |
|---|---|
| **ID** | UC-04 |
| **Name** | Classify MoSCoW |
| **Actor** | AI Processor |
| **Trigger** | Requirement text received for processing |
| **Precondition** | Requirement description is available |
| **Postcondition** | One MoSCoW category assigned |

**Main Flow:**
1. AI reads requirement title, description, and business objective
2. AI evaluates business criticality and dependencies
3. AI assigns one of: Must Have / Should Have / Could Have / Won't Have
4. Classification returned as part of JSON response

---

### UC-05: Assign Priority Score

| Field | Details |
|---|---|
| **ID** | UC-05 |
| **Name** | Assign Priority Score |
| **Actor** | AI Processor + System |
| **Trigger** | Requirement submitted with submitter role |
| **Precondition** | Submitter role is captured in form |
| **Postcondition** | Priority (High/Medium/Low) assigned with justification |

**Main Flow:**
1. System reads submitter role from form data
2. System applies role-weight mapping:
   - C-Suite / Executive → High
   - VP / Director → High
   - Department Head / Manager → Medium
   - Team Lead → Medium
   - End User → Low
   - External Stakeholder → Low
3. AI provides written justification for priority
4. Priority and justification stored in Postgres

---

### UC-06: Detect Conflicts

| Field | Details |
|---|---|
| **ID** | UC-06 |
| **Name** | Detect Requirement Conflicts |
| **Actor** | AI Processor |
| **Trigger** | New requirement submitted |
| **Precondition** | At least one existing requirement in the system |
| **Postcondition** | Conflict report returned (conflicts found or none detected) |

**Main Flow:**
1. System retrieves all existing requirement titles and descriptions from MongoDB
2. System includes existing requirements in AI prompt
3. AI compares new requirement against all existing ones
4. AI identifies overlaps, contradictions, or scope conflicts
5. AI returns list of conflicts with descriptions
6. If no conflicts found, AI returns "No conflicts detected"
7. Conflicts stored in Postgres conflicts table

---

### UC-07: Save Structured Output to Postgres

| Field | Details |
|---|---|
| **ID** | UC-07 |
| **Name** | Save Structured Output to Postgres |
| **Actor** | System |
| **Trigger** | AI processing complete |
| **Precondition** | AI response successfully parsed |
| **Postcondition** | Requirement, stories, and conflicts saved to Postgres |

**Main Flow:**
1. System inserts requirement record into requirements table
2. System stores MongoDB ObjectId as foreign reference
3. System inserts 3 user story records into user_stories table
4. System inserts any detected conflicts into conflicts table
5. System marks MongoDB document as processed

---

### UC-08: Review Requirements in Tracker

| Field | Details |
|---|---|
| **ID** | UC-08 |
| **Name** | Review Requirements in Tracker |
| **Actor** | Business Analyst |
| **Trigger** | BA navigates to Requirements Tracker tab |
| **Precondition** | At least one requirement exists in system |
| **Postcondition** | BA views requirement details |

**Main Flow:**
1. System loads all requirements from Postgres
2. System displays requirements in expandable list sorted by date
3. BA applies optional filters (status, priority, MoSCoW)
4. BA expands a requirement to view details
5. BA views submitter info, priority, MoSCoW, story count
6. BA clicks View Full Details to see user stories and audit trail
7. System retrieves and displays raw intake from MongoDB

---

### UC-09: Update Requirement Status

| Field | Details |
|---|---|
| **ID** | UC-09 |
| **Name** | Update Requirement Status |
| **Actor** | Business Analyst |
| **Trigger** | BA selects new status from dropdown |
| **Precondition** | Requirement exists in tracker |
| **Postcondition** | Status updated and audit log entry created |

**Main Flow:**
1. BA selects new status from dropdown within requirement card
2. BA clicks Update button
3. System validates new status differs from current status
4. System updates status in requirements table
5. System inserts audit log entry with old status, new status, timestamp
6. System refreshes tracker view

**Alternative Flow — Same Status Selected:**
- System displays warning: "Please select a different status"
- No database changes made

---

### UC-10: View Traceability Matrix

| Field | Details |
|---|---|
| **ID** | UC-10 |
| **Name** | View Traceability Matrix |
| **Actor** | Business Analyst |
| **Trigger** | BA navigates to Traceability Matrix tab |
| **Precondition** | Requirements with user stories exist |
| **Postcondition** | Full matrix displayed with color coding |

**Main Flow:**
1. System queries Postgres joining requirements and user_stories tables
2. System displays matrix with REQ ID, title, submitter, department, status, priority, MoSCoW, story, criteria
3. System applies color coding to status, priority, and MoSCoW columns
4. BA applies optional filters by status or MoSCoW
5. Matrix updates dynamically based on filters

---

### UC-11: Export Traceability CSV

| Field | Details |
|---|---|
| **ID** | UC-11 |
| **Name** | Export Traceability CSV |
| **Actor** | Business Analyst |
| **Trigger** | BA clicks Download as CSV button |
| **Precondition** | Traceability matrix has data |
| **Postcondition** | CSV file downloaded to BA's device |

**Main Flow:**
1. System converts current filtered matrix to CSV format
2. System encodes as UTF-8
3. Browser initiates file download
4. File saved as traceability_matrix.csv

---

### UC-12: View Analytics Dashboard

| Field | Details |
|---|---|
| **ID** | UC-12 |
| **Name** | View Analytics Dashboard |
| **Actor** | Business Analyst / Project Manager |
| **Trigger** | User navigates to Analytics tab |
| **Precondition** | At least one requirement exists |
| **Postcondition** | All charts and KPIs rendered |

**Main Flow:**
1. System loads all requirements from Postgres
2. System calculates KPIs: total, approved, high priority, must have
3. System renders donut chart for status distribution
4. System renders pie chart for MoSCoW breakdown
5. System renders horizontal bar chart for department distribution
6. System renders bar chart for priority distribution
7. System renders line chart for submissions over time
8. System renders bar chart for role distribution
