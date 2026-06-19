import streamlit as st
from database.mongo_client import insert_raw_intake, get_all_titles_and_descriptions
from database.postgres_client import insert_requirement, insert_user_stories, insert_conflict
from ai.processor import process_requirement, generate_priority_score
from datetime import datetime


def render_intake_form():
    st.markdown("## 📋 Submit a Business Requirement")
    st.markdown("Fill out the form below. The AI will automatically generate user stories, acceptance criteria, and priority classification.")
    st.divider()

    with st.form("requirement_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input(
                "Requirement Title *",
                placeholder="e.g. Customer Purchase History Dashboard"
            )
            department = st.selectbox(
                "Department *",
                ["Sales", "Marketing", "Operations", "Finance", "HR", "IT", "Product", "Customer Success", "Legal", "Other"]
            )
            submitted_by = st.text_input(
                "Your Name *",
                placeholder="e.g. John Smith"
            )

        with col2:
            role = st.selectbox(
                "Your Role *",
                ["C-Suite / Executive", "VP / Director", "Department Head / Manager", "Team Lead", "End User", "External Stakeholder"]
            )
            business_objective = st.text_input(
                "Business Objective *",
                placeholder="e.g. Improve sales rep efficiency before customer calls"
            )

        description = st.text_area(
            "Requirement Description *",
            placeholder="Describe the business need in as much detail as possible. What problem are you solving? Who is affected? What does success look like?",
            height=150
        )

        additional_notes = st.text_area(
            "Additional Notes (Optional)",
            placeholder="Any constraints, deadlines, dependencies, or context that might be relevant.",
            height=80
        )

        submitted = st.form_submit_button("🚀 Submit & Generate AI Analysis", use_container_width=True)

    if submitted:
        if not all([title, description, submitted_by, department, role, business_objective]):
            st.error("Please fill in all required fields marked with *")
            return

        with st.spinner("💾 Saving to MongoDB..."):
            raw_data = {
                "title": title,
                "description": description,
                "department": department,
                "submitted_by": submitted_by,
                "role": role,
                "business_objective": business_objective,
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
                mongo_id=mongo_id,
                title=title,
                submitted_by=submitted_by,
                department=department,
                role=role,
                priority=result.get("priority", priority),
                moscow=result.get("moscow", "Should Have")
            )
            insert_user_stories(req_id, result.get("user_stories", []))

            conflicts = result.get("conflicts", [])
            for conflict in conflicts:
                if conflict.get("conflicting_req_id") and conflict["conflicting_req_id"] != "null":
                    insert_conflict(req_id, None, conflict["description"])

        st.success("✅ Requirement submitted and analyzed successfully!")
        st.divider()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("MoSCoW", result.get("moscow", "N/A"))
        with col2:
            st.metric("Priority", result.get("priority", "N/A"))
        with col3:
            st.metric("User Stories", len(result.get("user_stories", [])))

        st.divider()
        st.markdown("### 📖 Generated User Stories")
        for i, story in enumerate(result.get("user_stories", []), 1):
            with st.expander(f"User Story {i}", expanded=True):
                st.markdown(f"**Story:** {story['story']}")
                st.markdown(f"**Acceptance Criteria:** {story['acceptance_criteria']}")

        st.markdown("### ⚠️ Conflict Analysis")
        conflicts = result.get("conflicts", [])
        if conflicts and conflicts[0]["description"] != "No conflicts detected.":
            for conflict in conflicts:
                st.warning(f"🔴 {conflict['description']}")
        else:
            st.success("✅ No conflicts detected with existing requirements.")

        st.markdown("### 💡 Priority Justification")
        st.info(result.get("priority_justification", ""))