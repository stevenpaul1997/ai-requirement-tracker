import streamlit as st
import pandas as pd
from database.postgres_client import get_all_for_traceability


def render_traceability():
    st.markdown("## 🔗 Traceability Matrix")
    st.markdown("A complete mapping of every requirement to its user stories, acceptance criteria, and current status. Downloadable as CSV.")
    st.divider()

    rows = get_all_for_traceability()

    if not rows:
        st.info("No requirements found. Submit a requirement first.")
        return

    columns = [
        "REQ ID", "Title", "Submitted By", "Department",
        "Status", "Priority", "MoSCoW", "User Story", "Acceptance Criteria"
    ]

    df = pd.DataFrame(rows, columns=columns)
    df["REQ ID"] = df["REQ ID"].apply(lambda x: f"REQ-{x:04d}")

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        status_options = ["All", "Submitted", "Under Review", "Approved", "In Development", "Done", "Rejected"]
        status_filter = st.selectbox("Filter by Status", status_options, key="trace_status")
    with col2:
        moscow_options = ["All", "Must Have", "Should Have", "Could Have", "Won't Have"]
        moscow_filter = st.selectbox("Filter by MoSCoW", moscow_options, key="trace_moscow")

    if status_filter != "All":
        df = df[df["Status"] == status_filter]
    if moscow_filter != "All":
        df = df[df["MoSCoW"] == moscow_filter]

    st.markdown(f"### {len(df)} row(s) in matrix")

    def color_moscow(val):
        colors = {
            "Must Have": "background-color: #ff4b4b; color: white",
            "Should Have": "background-color: #ff8c00; color: white",
            "Could Have": "background-color: #ffd700; color: black",
            "Won't Have": "background-color: #555555; color: white"
        }
        return colors.get(val, "")

    def color_priority(val):
        colors = {
            "High": "background-color: #ff4b4b; color: white",
            "Medium": "background-color: #ffd700; color: black",
            "Low": "background-color: #00cc44; color: white"
        }
        return colors.get(val, "")

    def color_status(val):
        colors = {
            "Submitted": "background-color: #1e90ff; color: white",
            "Under Review": "background-color: #ffd700; color: black",
            "Approved": "background-color: #00cc44; color: white",
            "In Development": "background-color: #ff8c00; color: white",
            "Done": "background-color: #228b22; color: white",
            "Rejected": "background-color: #ff4b4b; color: white"
        }
        return colors.get(val, "")

    styled_df = df.style.map(color_moscow, subset=["MoSCoW"]) \
                        .map(color_priority, subset=["Priority"]) \
                        .map(color_status, subset=["Status"])

    st.dataframe(styled_df, use_container_width=True, height=500)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download as CSV",
            data=csv,
            file_name="traceability_matrix.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col2:
        st.markdown("**What is a Traceability Matrix?**")
        st.caption("A traceability matrix links business requirements to their corresponding user stories and acceptance criteria, ensuring complete coverage and enabling audit-ready documentation.")