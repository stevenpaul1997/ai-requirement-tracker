import streamlit as st
import pandas as pd
import plotly.express as px
from database.postgres_client import get_all_requirements


def render_analytics():
    st.markdown("## 📈 Analytics Dashboard")
    st.markdown("Real-time insights into your requirements pipeline.")
    st.divider()

    rows = get_all_requirements()

    if not rows:
        st.info("No data yet. Submit some requirements to see analytics.")
        return

    columns = ["ID", "Mongo ID", "Title", "Submitted By", "Department",
               "Role", "Status", "Priority", "MoSCoW", "Created At", "Stories"]
    df = pd.DataFrame(rows, columns=columns)

    # KPI Row
    total = len(df)
    approved = len(df[df["Status"] == "Approved"])
    high_priority = len(df[df["Priority"] == "High"])
    must_have = len(df[df["MoSCoW"] == "Must Have"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Requirements", total)
    with col2:
        st.metric("Approved", approved)
    with col3:
        st.metric("High Priority", high_priority)
    with col4:
        st.metric("Must Have", must_have)

    st.divider()

    # Row 1 — Status + MoSCoW
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Requirements by Status")
        status_counts = df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_status = px.pie(
            status_counts,
            values="Count",
            names="Status",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_status.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        st.markdown("### MoSCoW Breakdown")
        moscow_counts = df["MoSCoW"].value_counts().reset_index()
        moscow_counts.columns = ["MoSCoW", "Count"]
        moscow_colors = {
            "Must Have": "#ff4b4b",
            "Should Have": "#ff8c00",
            "Could Have": "#ffd700",
            "Won't Have": "#555555"
        }
        colors = [moscow_colors.get(m, "#888") for m in moscow_counts["MoSCoW"]]
        fig_moscow = px.pie(
            moscow_counts,
            values="Count",
            names="MoSCoW",
            hole=0.4,
            color_discrete_sequence=colors
        )
        fig_moscow.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_moscow, use_container_width=True)

    st.divider()

    # Row 2 — Department + Priority
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Requirements by Department")
        dept_counts = df["Department"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Count"]
        fig_dept = px.bar(
            dept_counts,
            x="Count",
            y="Department",
            orientation="h",
            color="Count",
            color_continuous_scale="Blues"
        )
        fig_dept.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            margin=dict(t=20, b=20, l=20, r=20),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_dept, use_container_width=True)

    with col2:
        st.markdown("### Requirements by Priority")
        priority_counts = df["Priority"].value_counts().reset_index()
        priority_counts.columns = ["Priority", "Count"]
        priority_colors = {"High": "#ff4b4b", "Medium": "#ffd700", "Low": "#00cc44"}
        fig_priority = px.bar(
            priority_counts,
            x="Priority",
            y="Count",
            color="Priority",
            color_discrete_map=priority_colors
        )
        fig_priority.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=False
        )
        st.plotly_chart(fig_priority, use_container_width=True)

    st.divider()

    # Row 3 — Submissions over time
    st.markdown("### Requirements Submitted Over Time")
    df["Created At"] = pd.to_datetime(df["Created At"])
    df["Date"] = df["Created At"].dt.date
    time_counts = df.groupby("Date").size().reset_index(name="Count")
    fig_time = px.line(
        time_counts,
        x="Date",
        y="Count",
        markers=True,
        color_discrete_sequence=["#00cc44"]
    )
    fig_time.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_time, use_container_width=True)

    st.divider()

    # Row 4 — Role distribution
    st.markdown("### Submissions by Role")
    role_counts = df["Role"].value_counts().reset_index()
    role_counts.columns = ["Role", "Count"]
    fig_role = px.bar(
        role_counts,
        x="Role",
        y="Count",
        color="Count",
        color_continuous_scale="Purples"
    )
    fig_role.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        margin=dict(t=20, b=20, l=20, r=20),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_role, use_container_width=True)