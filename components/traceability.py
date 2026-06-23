import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from database.postgres_client import get_all_for_traceability

STATUS_COLORS = {
    "Submitted": "#0176d3", "Under Review": "#dd7a01",
    "Approved": "#2e844a", "In Development": "#9050e9",
    "Done": "#032d60", "Rejected": "#ba0517"
}
PRIORITY_COLORS = {"High": "#ba0517", "Medium": "#dd7a01", "Low": "#2e844a"}
MOSCOW_COLORS = {
    "Must Have": "#ba0517", "Should Have": "#dd7a01",
    "Could Have": "#2e844a", "Won't Have": "#706e6b"
}

def badge(val, color_map):
    color = color_map.get(val, "#706e6b")
    return f'<span style="background:{color};color:#fff;font-size:11px;font-weight:600;padding:2px 10px;border-radius:20px;white-space:nowrap;">{val}</span>'

def render_traceability():
    st.markdown("""
    <div style="margin-bottom:2rem;">
        <div style="font-size:0.72rem;font-weight:700;color:#0176d3;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:0.4rem;">Documentation</div>
        <div style="font-size:1.5rem;font-weight:700;color:#032d60;letter-spacing:-0.5px;margin-bottom:0.4rem;">Traceability Matrix</div>
        <div style="font-size:0.9rem;color:#706e6b;">A complete mapping of every requirement to its user stories, acceptance criteria, and current status.</div>
    </div>
    """, unsafe_allow_html=True)

    rows = get_all_for_traceability()
    if not rows:
        st.info("No requirements found.")
        return

    columns = ["REQ ID", "Title", "Submitted By", "Department",
               "Status", "Priority", "MoSCoW", "User Story", "Acceptance Criteria"]
    df = pd.DataFrame(rows, columns=columns)
    df["REQ ID"] = df["REQ ID"].apply(lambda x: f"REQ-{x:04d}")

    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Submitted", "Under Review", "Approved", "In Development", "Done", "Rejected"],
            key="trace_status"
        )
    with col2:
        moscow_filter = st.selectbox(
            "Filter by MoSCoW",
            ["All", "Must Have", "Should Have", "Could Have", "Won't Have"],
            key="trace_moscow"
        )

    if status_filter != "All":
        df = df[df["Status"] == status_filter]
    if moscow_filter != "All":
        df = df[df["MoSCoW"] == moscow_filter]

    st.markdown(f"""
    <div style="font-size:0.72rem;font-weight:700;color:#0176d3;letter-spacing:1.5px;text-transform:uppercase;margin:1.5rem 0 1rem;">{len(df)} Row(s) in Matrix</div>
    """, unsafe_allow_html=True)

    table_rows = ""
    for _, row in df.iterrows():
        story = str(row["User Story"])
        story_short = story[:120] + "..." if len(story) > 120 else story
        table_rows += f"""<tr>
            <td style="font-weight:700;color:#0176d3;white-space:nowrap;">{row["REQ ID"]}</td>
            <td style="font-weight:600;color:#032d60;">{row["Title"]}</td>
            <td style="color:#706e6b;">{row["Submitted By"]}</td>
            <td style="color:#706e6b;">{row["Department"]}</td>
            <td>{badge(row["Status"], STATUS_COLORS)}</td>
            <td>{badge(row["Priority"], PRIORITY_COLORS)}</td>
            <td>{badge(row["MoSCoW"], MOSCOW_COLORS)}</td>
            <td style="color:#3e3e3c;line-height:1.4;">{story_short}</td>
        </tr>"""

    html = f"""
    <html><head><style>
        * {{ font-family: Inter, sans-serif; box-sizing: border-box; }}
        body {{ margin: 0; padding: 0; background: #fff; }}
        table {{ width:100%; border-collapse:collapse; font-size:13px; }}
        th {{
            background:#f3f2f2; color:#706e6b; font-size:11px; font-weight:700;
            text-transform:uppercase; letter-spacing:0.8px; padding:10px 14px;
            text-align:left; border-bottom:2px solid #dddbda; white-space:nowrap;
        }}
        td {{ padding:10px 14px; border-bottom:1px solid #f3f2f2; vertical-align:top; color:#181818; }}
        tr:hover td {{ background:#f8f9fb; }}
    </style></head><body>
    <div style="border:1px solid #dddbda;border-radius:6px;overflow:hidden;overflow-x:auto;">
    <table>
        <thead><tr>
            <th>REQ ID</th><th>Title</th><th>Submitted By</th>
            <th>Department</th><th>Status</th><th>Priority</th>
            <th>MoSCoW</th><th>User Story</th>
        </tr></thead>
        <tbody>{table_rows}</tbody>
    </table>
    </div>
    </body></html>
    """

    components.html(html, height=500, scrolling=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name="traceability_matrix.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col2:
        st.markdown("""
        <div style="background:#f8f9fb;border:1px solid #dddbda;border-left:3px solid #0176d3;border-radius:4px;padding:1rem;">
            <div style="font-size:0.72rem;font-weight:700;color:#0176d3;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.3rem;">What is a Traceability Matrix?</div>
            <div style="font-size:0.85rem;color:#3e3e3c;line-height:1.5;">Links business requirements to user stories and acceptance criteria, ensuring complete coverage and audit-ready documentation.</div>
        </div>
        """, unsafe_allow_html=True)