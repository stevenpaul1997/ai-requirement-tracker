import streamlit as st
import pandas as pd
from database.postgres_client import get_all_requirements, update_status, get_requirement_with_stories
from database.mongo_client import get_raw_by_id
import streamlit.components.v1 as components

STATUSES = ["Submitted", "Under Review", "Approved", "In Development", "Done", "Rejected"]

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
    return f'<span style="background:{color};color:#fff;font-size:0.68rem;font-weight:600;padding:3px 10px;border-radius:20px;white-space:nowrap;">{val}</span>'

def render_tracker():
    st.markdown("""
    <div style="margin-bottom:2rem;">
        <div style="font-size:0.72rem;font-weight:700;color:#0176d3;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:0.4rem;">Lifecycle Management</div>
        <div style="font-size:1.5rem;font-weight:700;color:#032d60;letter-spacing:-0.5px;margin-bottom:0.4rem;">Requirements Tracker</div>
        <div style="font-size:0.9rem;color:#706e6b;">Track and manage the full lifecycle of every submitted requirement.</div>
    </div>
    """, unsafe_allow_html=True)

    rows = get_all_requirements()
    if not rows:
        st.info("No requirements submitted yet.")
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

    st.markdown(f"""
    <div style="font-size:0.72rem;font-weight:700;color:#0176d3;letter-spacing:1.5px;text-transform:uppercase;margin:1.5rem 0 1rem;">{len(df)} Requirement(s)</div>
    """, unsafe_allow_html=True)

    for _, row in df.iterrows():
        req_id = row["ID"]
        sc = STATUS_COLORS.get(row["Status"], "#706e6b")
        pc = PRIORITY_COLORS.get(row["Priority"], "#706e6b")
        mc = MOSCOW_COLORS.get(row["MoSCoW"], "#706e6b")

        with st.expander(f"REQ-{req_id:04d}   ·   {row['Title']}", expanded=False):
            # Badge row
            st.markdown(f"""
            <div style="display:flex;gap:0.5rem;margin-bottom:1.5rem;flex-wrap:wrap;align-items:center;">
                <span style="background:{sc};color:#fff;font-size:0.72rem;font-weight:600;padding:4px 14px;border-radius:20px;">{row['Status']}</span>
                <span style="background:{pc};color:#fff;font-size:0.72rem;font-weight:600;padding:4px 14px;border-radius:20px;">{row['Priority']} Priority</span>
                <span style="background:{mc};color:#fff;font-size:0.72rem;font-weight:600;padding:4px 14px;border-radius:20px;">{row['MoSCoW']}</span>
                <span style="background:#f3f2f2;color:#706e6b;font-size:0.72rem;font-weight:600;padding:4px 14px;border-radius:20px;border:1px solid #dddbda;">{row['Stories']} Stories</span>
            </div>
            """, unsafe_allow_html=True)

            # Info grid
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;background:#f8f9fb;border:1px solid #dddbda;border-radius:6px;padding:1.2rem;margin-bottom:1.2rem;">
                <div>
                    <div style="font-size:0.65rem;font-weight:700;color:#706e6b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">Submitted By</div>
                    <div style="font-size:0.88rem;color:#032d60;font-weight:600;">{row['Submitted By']}</div>
                </div>
                <div>
                    <div style="font-size:0.65rem;font-weight:700;color:#706e6b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">Department</div>
                    <div style="font-size:0.88rem;color:#032d60;font-weight:600;">{row['Department']}</div>
                </div>
                <div>
                    <div style="font-size:0.65rem;font-weight:700;color:#706e6b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">Role</div>
                    <div style="font-size:0.88rem;color:#032d60;font-weight:600;">{row['Role']}</div>
                </div>
                <div>
                    <div style="font-size:0.65rem;font-weight:700;color:#706e6b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">Created</div>
                    <div style="font-size:0.88rem;color:#032d60;font-weight:600;">{str(row['Created At'])[:10]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_s, col_b = st.columns([3, 1])
            with col_s:
                new_status = st.selectbox(
                    "Update Status",
                    STATUSES,
                    index=STATUSES.index(row["Status"]) if row["Status"] in STATUSES else 0,
                    key=f"trk_upd_{req_id}"
                )
            with col_b:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Update", key=f"trk_btn_{req_id}"):
                    if new_status != row["Status"]:
                        update_status(req_id, new_status, row["Status"])
                        st.success(f"Status updated to {new_status}")
                        st.rerun()
                    else:
                        st.warning("Select a different status.")

            if st.button("View Full Details", key=f"trk_det_{req_id}"):
                req, stories, audit = get_requirement_with_stories(req_id)

                if stories:
                    st.markdown("""<div style="font-size:0.65rem;font-weight:700;color:#706e6b;text-transform:uppercase;letter-spacing:0.8px;margin:1rem 0 0.75rem;">User Stories</div>""", unsafe_allow_html=True)
                    for i, story in enumerate(stories, 1):
                        st.markdown(f"""
                        <div style="background:#ffffff;border:1px solid #dddbda;border-left:3px solid #0176d3;border-radius:4px;padding:1.2rem;margin-bottom:0.75rem;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                            <div style="font-size:0.65rem;font-weight:700;color:#0176d3;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">Story {i}</div>
                            <div style="font-size:0.9rem;color:#181818;margin-bottom:0.75rem;line-height:1.6;">{story[2]}</div>
                            <div style="font-size:0.65rem;font-weight:700;color:#706e6b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">Acceptance Criteria</div>
                            <div style="font-size:0.85rem;color:#3e3e3c;line-height:1.5;">{story[3]}</div>
                        </div>
                        """, unsafe_allow_html=True)

                if audit:
                    st.markdown("""<div style="font-size:0.65rem;font-weight:700;color:#706e6b;text-transform:uppercase;letter-spacing:0.8px;margin:1.2rem 0 0.5rem;">Audit Trail</div>""", unsafe_allow_html=True)
                    for entry in audit:
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid #f3f2f2;font-size:0.82rem;">
                            <span style="color:#706e6b;font-size:0.75rem;min-width:130px;">{str(entry[4])[:16]}</span>
                            <span style="background:#f3f2f2;color:#3e3e3c;padding:2px 10px;border-radius:4px;font-size:0.75rem;font-weight:500;">{entry[2]}</span>
                            <span style="color:#b0b0b0;">→</span>
                            <span style="background:#eaf5fe;color:#0176d3;padding:2px 10px;border-radius:4px;font-size:0.75rem;font-weight:700;">{entry[3]}</span>
                        </div>
                        """, unsafe_allow_html=True)

                if row["Mongo ID"]:
                    raw = get_raw_by_id(row["Mongo ID"])
                    if raw:
                        st.markdown("""<div style="font-size:0.65rem;font-weight:700;color:#706e6b;text-transform:uppercase;letter-spacing:0.8px;margin:1.2rem 0 0.5rem;">Original Intake (MongoDB)</div>""", unsafe_allow_html=True)
                        st.markdown(f"""
                        <div style="background:#f8f9fb;border:1px solid #dddbda;border-radius:4px;padding:1.2rem;">
                            <div style="margin-bottom:0.75rem;">
                                <div style="font-size:0.65rem;font-weight:700;color:#706e6b;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Description</div>
                                <div style="font-size:0.88rem;color:#3e3e3c;line-height:1.5;">{raw.get('description','N/A')}</div>
                            </div>
                            <div>
                                <div style="font-size:0.65rem;font-weight:700;color:#706e6b;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Business Objective</div>
                                <div style="font-size:0.88rem;color:#3e3e3c;">{raw.get('business_objective','N/A')}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)