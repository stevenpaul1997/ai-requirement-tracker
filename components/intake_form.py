import streamlit as st
from database.mongo_client import insert_raw_intake, get_all_titles_and_descriptions
from database.postgres_client import insert_requirement, insert_user_stories, insert_conflict
from ai.processor import process_requirement, generate_priority_score
from datetime import datetime


def render_intake_form():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div style="font-size:0.72rem;font-weight:700;color:#0176d3;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:0.5rem;">Requirements Intake</div>
        <div style="font-size:1.6rem;font-weight:700;color:#032d60;letter-spacing:-0.5px;margin-bottom:0.5rem;">Submit a Business Requirement</div>
        <div style="font-size:0.9rem;color:#706e6b;line-height:1.6;max-width:580px;">Fill out the form below. The AI will automatically generate user stories, acceptance criteria, MoSCoW classification, and conflict detection.</div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize widget-bound session state (defaults)
    if "title_input" not in st.session_state:
        st.session_state.title_input = ""
    if "dept_input" not in st.session_state:
        st.session_state.dept_input = "Sales"
    if "name_input" not in st.session_state:
        st.session_state.name_input = ""
    if "role_input" not in st.session_state:
        st.session_state.role_input = "C-Suite / Executive"
    if "objective_input" not in st.session_state:
        st.session_state.objective_input = ""
    if "desc_input" not in st.session_state:
        st.session_state.desc_input = ""
    if "notes_input" not in st.session_state:
        st.session_state.notes_input = ""
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None

    # Handle a clear request queued from the PREVIOUS run.
    # This must happen BEFORE the widgets below are instantiated,
    # since Streamlit forbids modifying a widget's session_state key
    # after that widget has already been created in the current run.
    if st.session_state.get("_do_clear", False):
        st.session_state.title_input = ""
        st.session_state.dept_input = "Sales"
        st.session_state.name_input = ""
        st.session_state.role_input = "C-Suite / Executive"
        st.session_state.objective_input = ""
        st.session_state.desc_input = ""
        st.session_state.notes_input = ""
        st.session_state.analysis_result = None
        st.session_state._do_clear = False

    dept_options = ["Sales", "Marketing", "Operations", "Finance", "HR", "IT", "Product", "Customer Success", "Legal", "Other"]
    role_options = ["C-Suite / Executive", "VP / Director", "Department Head / Manager", "Team Lead", "End User", "External Stakeholder"]

    with st.form("requirement_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Requirement Title *", placeholder="e.g. Customer Purchase History Dashboard", key="title_input")
            department = st.selectbox("Department *", dept_options, key="dept_input")
            submitted_by = st.text_input("Your Name *", placeholder="e.g. John Smith", key="name_input")
        with col2:
            role = st.selectbox("Your Role *", role_options, key="role_input")
            business_objective = st.text_input("Business Objective *", placeholder="e.g. Improve sales rep efficiency before customer calls", key="objective_input")

        description = st.text_area("Requirement Description *", placeholder="Describe the business need in as much detail as possible. What problem are you solving? Who is affected? What does success look like?", height=150, key="desc_input")
        additional_notes = st.text_area("Additional Notes (Optional)", placeholder="Any constraints, deadlines, dependencies, or context that might be relevant.", height=80, key="notes_input")

        col_submit, col_clear = st.columns([3, 1])
        with col_submit:
            submitted = st.form_submit_button("Submit and Analyse", use_container_width=True, type="primary")
        with col_clear:
            cleared = st.form_submit_button("Clear", use_container_width=True, type="secondary")

    if cleared:
        st.session_state._do_clear = True
        st.rerun()

    if submitted:
        if not all([title, description, submitted_by, department, role, business_objective]):
            st.error("Please fill in all required fields marked with *")
            return

        with st.spinner("💾 Saving to MongoDB..."):
            raw_data = {
                "title": title, "description": description,
                "department": department, "submitted_by": submitted_by,
                "role": role, "business_objective": business_objective,
                "additional_notes": additional_notes,
                "submitted_at": datetime.utcnow().isoformat()
            }
            mongo_id = insert_raw_intake(raw_data)

        with st.spinner("🤖 AI is analyzing your requirement..."):
            existing = get_all_titles_and_descriptions()
            existing = [r for r in existing if str(r["_id"]) != mongo_id]
            result = process_requirement(title, description, department, role, business_objective, existing)

        with st.spinner("📊 Saving structured data to Postgres..."):
            priority = generate_priority_score(role, department, business_objective)
            req_id = insert_requirement(
                mongo_id=mongo_id, title=title, submitted_by=submitted_by,
                department=department, role=role,
                priority=result.get("priority", priority),
                moscow=result.get("moscow", "Should Have")
            )
            insert_user_stories(req_id, result.get("user_stories", []))
            for conflict in result.get("conflicts", []):
                if conflict.get("conflicting_req_id") and conflict["conflicting_req_id"] != "null":
                    insert_conflict(req_id, None, conflict["description"])

        st.session_state.analysis_result = result

    # Render results from session state (persists across reruns)
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result

        st.success("Requirement submitted and analyzed successfully.")
        st.divider()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style="background:#eaf5fe;border:1px solid #b3d1ff;border-top:3px solid #0176d3;border-radius:6px;padding:1.2rem 1.4rem;">
                <div style="font-size:0.68rem;font-weight:700;color:#706e6b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.4rem;">MoSCoW</div>
                <div style="font-size:1.5rem;font-weight:700;color:#032d60;">{result.get('moscow', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="background:#eaf5fe;border:1px solid #b3d1ff;border-top:3px solid #0176d3;border-radius:6px;padding:1.2rem 1.4rem;">
                <div style="font-size:0.68rem;font-weight:700;color:#706e6b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.4rem;">Priority</div>
                <div style="font-size:1.5rem;font-weight:700;color:#032d60;">{result.get('priority', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div style="background:#eaf5fe;border:1px solid #b3d1ff;border-top:3px solid #0176d3;border-radius:6px;padding:1.2rem 1.4rem;">
                <div style="font-size:0.68rem;font-weight:700;color:#706e6b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.4rem;">User Stories</div>
                <div style="font-size:1.5rem;font-weight:700;color:#032d60;">{len(result.get('user_stories', []))}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.markdown("""<div style="font-size:0.72rem;font-weight:700;color:#0176d3;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:1rem;">Generated User Stories</div>""", unsafe_allow_html=True)

        for i, story in enumerate(result.get("user_stories", []), 1):
            with st.expander(f"User Story {i}", expanded=True):
                st.markdown(f"""
                <div style="margin-bottom:0.75rem;">
                    <div style="font-size:0.72rem;font-weight:700;color:#706e6b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.3rem;">Story</div>
                    <div style="font-size:0.9rem;color:#181818;line-height:1.6;">{story['story']}</div>
                </div>
                <div>
                    <div style="font-size:0.72rem;font-weight:700;color:#706e6b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.3rem;">Acceptance Criteria</div>
                    <div style="font-size:0.9rem;color:#181818;line-height:1.6;">{story['acceptance_criteria']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.markdown("""<div style="font-size:0.72rem;font-weight:700;color:#0176d3;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:0.75rem;">Conflict Analysis</div>""", unsafe_allow_html=True)
        conflicts = result.get("conflicts", [])
        if conflicts and conflicts[0]["description"] != "No conflicts detected.":
            for conflict in conflicts:
                st.warning(f"{conflict['description']}")
        else:
            st.success("No conflicts detected with existing requirements.")

        st.divider()
        st.markdown("""<div style="font-size:0.72rem;font-weight:700;color:#0176d3;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:0.5rem;">Priority Justification</div>""", unsafe_allow_html=True)
        st.info(result.get("priority_justification", ""))