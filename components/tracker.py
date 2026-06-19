import streamlit as st
import pandas as pd
from database.postgres_client import get_all_requirements, update_status, get_requirement_with_stories
from database.mongo_client import get_raw_by_id


STATUSES = ["Submitted", "Under Review", "Approved", "In Development", "Done", "Rejected"]

STATUS_COLORS = {
    "Submitted": "🔵",
    "Under Review": "🟡",
    "Approved": "🟢",
    "In Development": "🟠",
    "Done": "✅",
    "Rejected": "🔴"
}

PRIORITY_COLORS = {
    "High": "🔴",
    "Medium": "🟡",
    "Low": "🟢"
}

MOSCOW_COLORS = {
    "Must Have": "🔴",
    "Should Have": "🟠",
    "Could Have": "🟡",
    "Won't Have": "⚪"
}


def render_tracker():
    st.markdown("## 📊 Requirements Tracker")
    st.markdown("Track the lifecycle of all submitted requirements. Update statuses and view AI-generated details.")
    st.divider()

    rows = get_all_requirements()

    if not rows:
        st.info("No requirements submitted yet. Go to the Submit tab to add your first requirement.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All"] + STATUSES, key="trk_status")
    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"], key="trk_priority")
    with col3:
        moscow_filter = st.selectbox("Filter by MoSCoW", ["All", "Must Have", "Should Have", "Could Have", "Won't Have"], key="trk_moscow")

    columns = ["ID", "Mongo ID", "Title", "Submitted By", "Department", "Role", "Status", "Priority", "MoSCoW", "Created At", "Stories"]
    df = pd.DataFrame(rows, columns=columns)

    if status_filter != "All":
        df = df[df["Status"] == status_filter]
    if priority_filter != "All":
        df = df[df["Priority"] == priority_filter]
    if moscow_filter != "All":
        df = df[df["MoSCoW"] == moscow_filter]

    st.markdown(f"### Showing {len(df)} requirement(s)")

    for _, row in df.iterrows():
        req_id = row["ID"]
        status_icon = STATUS_COLORS.get(row["Status"], "⚪")
        priority_icon = PRIORITY_COLORS.get(row["Priority"], "⚪")
        moscow_icon = MOSCOW_COLORS.get(row["MoSCoW"], "⚪")

        with st.expander(f"{status_icon} REQ-{req_id:04d} — {row['Title']}", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**Submitted By:** {row['Submitted By']}")
                st.markdown(f"**Department:** {row['Department']}")
            with col2:
                st.markdown(f"**Role:** {row['Role']}")
                st.markdown(f"**Created:** {str(row['Created At'])[:10]}")
            with col3:
                st.markdown(f"**Priority:** {priority_icon} {row['Priority']}")
                st.markdown(f"**MoSCoW:** {moscow_icon} {row['MoSCoW']}")
            with col4:
                st.markdown(f"**User Stories:** {row['Stories']}")
                st.markdown(f"**Status:** {status_icon} {row['Status']}")

            st.divider()

            col_status, col_btn = st.columns([3, 1])
            with col_status:
                new_status = st.selectbox(
                    "Update Status",
                    STATUSES,
                    index=STATUSES.index(row["Status"]) if row["Status"] in STATUSES else 0,
                    key=f"trk_upd_{req_id}"
                )
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Update", key=f"trk_btn_{req_id}"):
                    if new_status != row["Status"]:
                        update_status(req_id, new_status, row["Status"])
                        st.success(f"Status updated to {new_status}")
                        st.rerun()
                    else:
                        st.warning("Please select a different status.")

            st.divider()

            if st.button(f"📄 View Full Details", key=f"trk_det_{req_id}"):
                req, stories, audit = get_requirement_with_stories(req_id)

                st.markdown("### 📖 User Stories & Acceptance Criteria")
                if stories:
                    for i, story in enumerate(stories, 1):
                        st.markdown(f"**Story {i}:** {story[2]}")
                        st.markdown(f"**Acceptance Criteria:** {story[3]}")
                        st.markdown("---")
                else:
                    st.info("No user stories found.")

                st.markdown("### 🕐 Status Audit Trail")
                if audit:
                    for entry in audit:
                        st.markdown(f"- `{str(entry[4])[:16]}` — **{entry[2]}** → **{entry[3]}**")
                else:
                    st.info("No status changes recorded yet.")

                st.markdown("### 📝 Original Raw Intake (MongoDB)")
                if row["Mongo ID"]:
                    raw = get_raw_by_id(row["Mongo ID"])
                    if raw:
                        st.markdown(f"**Description:** {raw.get('description', 'N/A')}")
                        st.markdown(f"**Business Objective:** {raw.get('business_objective', 'N/A')}")
                        if raw.get("additional_notes"):
                            st.markdown(f"**Additional Notes:** {raw.get('additional_notes')}")