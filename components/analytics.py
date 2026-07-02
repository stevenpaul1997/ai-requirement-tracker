import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database.postgres_client import get_all_requirements

# ── Unified Blue Palette ──
NAVY = "#032d60"
BLUE = "#0176d3"
MIDBLUE = "#1b96ff"
LIGHTBLUE = "#5ebbff"
PALEBLUE = "#aad9ff"
GRAY = "#706e6b"

STATUS_COLORS = {
    "Submitted": BLUE, "Under Review": MIDBLUE,
    "Approved": NAVY, "In Development": LIGHTBLUE,
    "Done": "#001a3d", "Rejected": GRAY
}
MOSCOW_COLORS = {
    "Must Have": NAVY, "Should Have": BLUE,
    "Could Have": MIDBLUE, "Won't Have": GRAY
}
PRIORITY_COLORS = {"High": NAVY, "Medium": BLUE, "Low": LIGHTBLUE}
BAR_COLORS = [NAVY, BLUE, MIDBLUE, LIGHTBLUE, PALEBLUE,
              NAVY, BLUE, MIDBLUE, LIGHTBLUE, PALEBLUE]

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#3e3e3c", size=12),
    margin=dict(t=20, b=60, l=20, r=20),
    showlegend=False
)


def section(title):
    st.markdown(f"""
    <div style="font-size:0.72rem;font-weight:700;color:{BLUE};letter-spacing:1.5px;
    text-transform:uppercase;margin:2rem 0 1rem;padding-bottom:0.5rem;
    border-bottom:2px solid #e5e5e5;">{title}</div>
    """, unsafe_allow_html=True)


def render_analytics():
    st.markdown(f"""
    <div style="margin-bottom:2rem;">
        <div style="font-size:0.72rem;font-weight:700;color:{BLUE};letter-spacing:1.5px;
        text-transform:uppercase;margin-bottom:0.4rem;">Insights</div>
        <div style="font-size:1.5rem;font-weight:700;color:{NAVY};
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

    # ── KPI Row - unified blue tones ──
    kpi_data = [
        ("Total", total, NAVY, "#e6eef5"),
        ("Approved", approved, BLUE, "#eaf5fe"),
        ("In Development", in_dev, MIDBLUE, "#eaf5fe"),
        ("Done", done, "#001a3d", "#e6eef5"),
        ("High Priority", high, NAVY, "#e6eef5"),
        ("Must Have", must, BLUE, "#eaf5fe"),
    ]

    cols = st.columns(6)
    for col, (label, value, color, bg) in zip(cols, kpi_data):
        with col:
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {color}33;border-radius:10px;
            padding:1.4rem 1rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                <div style="font-size:2.4rem;font-weight:800;color:{color};line-height:1;
                margin-bottom:0.4rem;letter-spacing:-1px;">{value}</div>
                <div style="font-size:0.7rem;font-weight:700;color:{color};text-transform:uppercase;
                letter-spacing:0.8px;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ── Row 1: Pie Charts ──
    section("Distribution Overview")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""<div style="font-size:0.82rem;font-weight:600;color:{NAVY};margin-bottom:0.5rem;">Requirements by Status</div>""", unsafe_allow_html=True)
        sc = df["Status"].value_counts().reset_index()
        sc.columns = ["Status", "Count"]
        fig1 = go.Figure(go.Pie(
            labels=sc["Status"].tolist(),
            values=sc["Count"].tolist(),
            hole=0.5,
            marker=dict(
                colors=[STATUS_COLORS.get(s, GRAY) for s in sc["Status"].tolist()],
                line=dict(color="#ffffff", width=2)
            ),
            textinfo="percent+label",
            textfont=dict(size=11, family="Inter"),
            insidetextorientation="horizontal",
        ))
        fig1.update_layout(**LAYOUT)
        fig1.update_layout(height=340, margin=dict(t=50, b=50, l=50, r=50))
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    with col2:
        st.markdown(f"""<div style="font-size:0.82rem;font-weight:600;color:{NAVY};margin-bottom:0.5rem;">MoSCoW Breakdown</div>""", unsafe_allow_html=True)
        mc = df["MoSCoW"].value_counts().reset_index()
        mc.columns = ["MoSCoW", "Count"]
        fig2 = go.Figure(go.Pie(
            labels=mc["MoSCoW"].tolist(),
            values=mc["Count"].tolist(),
            hole=0.5,
            marker=dict(
                colors=[MOSCOW_COLORS.get(m, GRAY) for m in mc["MoSCoW"].tolist()],
                line=dict(color="#ffffff", width=2)
            ),
            textinfo="percent+label",
            textfont=dict(size=11, family="Inter"),
            insidetextorientation="horizontal",
        ))
        fig2.update_layout(**LAYOUT)
        fig2.update_layout(height=340, margin=dict(t=50, b=50, l=50, r=50))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # ── Row 2: Bar Charts ──
    section("Submission Breakdown")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""<div style="font-size:0.82rem;font-weight:600;color:{NAVY};margin-bottom:0.5rem;">By Department</div>""", unsafe_allow_html=True)
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
                      tickfont=dict(size=12, color=NAVY, family="Inter")),
            margin=dict(t=10, b=10, l=120, r=40),
            bargap=0.2
        )
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with col2:
        st.markdown(f"""<div style="font-size:0.82rem;font-weight:600;color:{NAVY};margin-bottom:0.5rem;">By Priority</div>""", unsafe_allow_html=True)
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
                    color=PRIORITY_COLORS.get(label, GRAY),
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
                      tickfont=dict(size=13, color=NAVY, family="Inter", weight=600)),
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
        line=dict(color=BLUE, width=2.5),
        marker=dict(color=BLUE, size=8, line=dict(color="#ffffff", width=2)),
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
                  tickfont=dict(size=11, color=NAVY, family="Inter")),
        yaxis=dict(showgrid=True, gridcolor="#f3f2f2", zeroline=False,
                  showticklabels=False, range=[0, max(rc_counts) + 2]),
        margin=dict(t=20, b=80, l=20, r=20)
    )
    st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})