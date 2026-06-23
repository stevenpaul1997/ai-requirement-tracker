import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database.postgres_client import get_all_requirements

STATUS_COLORS = {
    "Submitted": "#0176d3", "Under Review": "#dd7a01",
    "Approved": "#2e844a", "In Development": "#9050e9",
    "Done": "#032d60", "Rejected": "#ba0517"
}
MOSCOW_COLORS = {
    "Must Have": "#ba0517", "Should Have": "#dd7a01",
    "Could Have": "#2e844a", "Won't Have": "#706e6b"
}
PRIORITY_COLORS = {"High": "#ba0517", "Medium": "#dd7a01", "Low": "#2e844a"}
BAR_COLORS = ["#0176d3", "#2e844a", "#9050e9", "#dd7a01", "#ba0517",
              "#032d60", "#0176d3", "#2e844a", "#9050e9", "#dd7a01"]

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#3e3e3c", size=12),
    margin=dict(t=20, b=60, l=20, r=20),
    showlegend=False
)


def section(title):
    st.markdown(f"""
    <div style="font-size:0.72rem;font-weight:700;color:#0176d3;letter-spacing:1.5px;
    text-transform:uppercase;margin:2rem 0 1rem;padding-bottom:0.5rem;
    border-bottom:2px solid #e5e5e5;">{title}</div>
    """, unsafe_allow_html=True)


def render_analytics():
    st.markdown("""
    <div style="margin-bottom:2rem;">
        <div style="font-size:0.72rem;font-weight:700;color:#0176d3;letter-spacing:1.5px;
        text-transform:uppercase;margin-bottom:0.4rem;">Insights</div>
        <div style="font-size:1.5rem;font-weight:700;color:#032d60;
        letter-spacing:-0.5px;margin-bottom:0.4rem;">Analytics Dashboard</div>
        <div style="font-size:0.9rem;color:#706e6b;">
        Real-time insights into your requirements pipeline.</div>
    </div>
    """, unsafe_allow_html=True)

    rows = get_all_requirements()
    if not rows:
        st.info("No data yet.")
        return

    columns = ["ID", "Mongo ID", "Title", "Submitted By", "Department",
               "Role", "Status", "Priority", "MoSCoW", "Created At", "Stories"]
    df = pd.DataFrame(rows, columns=columns)

    total = len(df)
    approved = len(df[df["Status"] == "Approved"])
    in_dev = len(df[df["Status"] == "In Development"])
    done = len(df[df["Status"] == "Done"])
    high = len(df[df["Priority"] == "High"])
    must = len(df[df["MoSCoW"] == "Must Have"])

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total", total)
    c2.metric("Approved", approved)
    c3.metric("In Development", in_dev)
    c4.metric("Done", done)
    c5.metric("High Priority", high)
    c6.metric("Must Have", must)

    st.divider()

    # ── Row 1: Pie Charts ──
    section("Distribution Overview")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""<div style="font-size:0.82rem;font-weight:600;color:#032d60;margin-bottom:0.5rem;">Requirements by Status</div>""", unsafe_allow_html=True)
        sc = df["Status"].value_counts().reset_index()
        sc.columns = ["Status", "Count"]
        fig1 = go.Figure(go.Pie(
            labels=sc["Status"].tolist(),
            values=sc["Count"].tolist(),
            hole=0.5,
            marker=dict(
                colors=[STATUS_COLORS.get(s, "#706e6b") for s in sc["Status"].tolist()],
                line=dict(color="#ffffff", width=2)
            ),
            textinfo="percent+label",
            textfont=dict(size=11, family="Inter"),
        ))
        fig1.update_layout(**LAYOUT)
        fig1.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    with col2:
        st.markdown("""<div style="font-size:0.82rem;font-weight:600;color:#032d60;margin-bottom:0.5rem;">MoSCoW Breakdown</div>""", unsafe_allow_html=True)
        mc = df["MoSCoW"].value_counts().reset_index()
        mc.columns = ["MoSCoW", "Count"]
        fig2 = go.Figure(go.Pie(
            labels=mc["MoSCoW"].tolist(),
            values=mc["Count"].tolist(),
            hole=0.5,
            marker=dict(
                colors=[MOSCOW_COLORS.get(m, "#706e6b") for m in mc["MoSCoW"].tolist()],
                line=dict(color="#ffffff", width=2)
            ),
            textinfo="percent+label",
            textfont=dict(size=11, family="Inter"),
        ))
        fig2.update_layout(**LAYOUT)
        fig2.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # ── Row 2: Bar Charts ──
    section("Submission Breakdown")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""<div style="font-size:0.82rem;font-weight:600;color:#032d60;margin-bottom:0.5rem;">By Department</div>""", unsafe_allow_html=True)
        dc = df["Department"].value_counts().reset_index()
        dc.columns = ["Department", "Count"]
        depts = dc["Department"].tolist()
        counts = dc["Count"].tolist()
        n = len(depts)
        colors = BAR_COLORS[:n]
        fig3 = go.Figure()
        for i, (dept, count, color) in enumerate(zip(depts, counts, colors)):
            fig3.add_trace(go.Bar(
                x=[count],
                y=[dept],
                orientation="h",
                marker=dict(color=color, line=dict(color="#ffffff", width=1)),
                text=[str(count)],
                textposition="inside",
                textfont=dict(size=12, color="#ffffff", family="Inter", weight=700),
                name=dept,
                showlegend=False
            ))
        fig3.update_layout(**LAYOUT)
        fig3.update_layout(
            height=max(320, n * 44),
            barmode="stack",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                      range=[0, max(counts) + 0.5]),
            yaxis=dict(showgrid=False, autorange="reversed",
                      tickfont=dict(size=12, color="#032d60", family="Inter")),
            margin=dict(t=10, b=10, l=120, r=40),
            bargap=0.2
        )
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with col2:
        st.markdown("""<div style="font-size:0.82rem;font-weight:600;color:#032d60;margin-bottom:0.5rem;">By Priority</div>""", unsafe_allow_html=True)
        pc_order = ["High", "Medium", "Low"]
        pc = df["Priority"].value_counts().reindex(pc_order).dropna().reset_index()
        pc.columns = ["Priority", "Count"]
        pc_labels = pc["Priority"].tolist()
        pc_counts = pc["Count"].tolist()
        fig4 = go.Figure()
        for label, count in zip(pc_labels, pc_counts):
            fig4.add_trace(go.Bar(
                x=[label],
                y=[count],
                marker=dict(
                    color=PRIORITY_COLORS.get(label, "#706e6b"),
                    line=dict(color="#ffffff", width=1)
                ),
                text=[str(count)],
                textposition="outside",
                textfont=dict(size=13, color="#3e3e3c", family="Inter", weight=700),
                name=label,
                showlegend=False,
                width=0.4
            ))
        fig4.update_layout(**LAYOUT)
        fig4.update_layout(
            height=320,
            barmode="group",
            xaxis=dict(showgrid=False,
                      tickfont=dict(size=13, color="#032d60", family="Inter", weight=600)),
            yaxis=dict(showgrid=True, gridcolor="#f3f2f2", zeroline=False,
                      showticklabels=False, range=[0, max(pc_counts) + 3]),
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

    # ── Timeline ──
    section("Submission Timeline")
    df["Created At"] = pd.to_datetime(df["Created At"])
    df["Date"] = df["Created At"].dt.date
    tc = df.groupby("Date").size().reset_index(name="Count")
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(
        x=tc["Date"].tolist(),
        y=tc["Count"].tolist(),
        mode="lines+markers",
        line=dict(color="#0176d3", width=2.5),
        marker=dict(color="#0176d3", size=8, line=dict(color="#ffffff", width=2)),
        fill="tozeroy",
        fillcolor="rgba(1,118,211,0.07)",
    ))
    fig5.update_layout(**LAYOUT)
    fig5.update_layout(
        height=240,
        xaxis=dict(showgrid=False, zeroline=False,
                  tickfont=dict(size=11, color="#706e6b", family="Inter")),
        yaxis=dict(showgrid=True, gridcolor="#f3f2f2", zeroline=False,
                  tickfont=dict(size=11, color="#706e6b", family="Inter")),
        margin=dict(t=10, b=40, l=40, r=20)
    )
    st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})

    # ── Role ──
    section("Submissions by Role")
    rc = df["Role"].value_counts().reset_index()
    rc.columns = ["Role", "Count"]
    rc_roles = rc["Role"].tolist()
    rc_counts = rc["Count"].tolist()
    fig6 = go.Figure()
    for role, count, color in zip(rc_roles, rc_counts, BAR_COLORS[:len(rc_roles)]):
        fig6.add_trace(go.Bar(
            x=[role],
            y=[count],
            marker=dict(color=color, line=dict(color="#ffffff", width=1)),
            text=[str(count)],
            textposition="outside",
            textfont=dict(size=12, color="#3e3e3c", family="Inter", weight=700),
            name=role,
            showlegend=False,
            width=0.5
        ))
    fig6.update_layout(**LAYOUT)
    fig6.update_layout(
        height=320,
        barmode="group",
        xaxis=dict(showgrid=False, tickangle=-15,
                  tickfont=dict(size=11, color="#032d60", family="Inter")),
        yaxis=dict(showgrid=True, gridcolor="#f3f2f2", zeroline=False,
                  showticklabels=False, range=[0, max(rc_counts) + 2]),
        margin=dict(t=20, b=80, l=20, r=20)
    )
    st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})