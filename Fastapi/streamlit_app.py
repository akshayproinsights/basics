"""Run with: streamlit run streamlit_app.py."""
import math
import pandas as pd
import streamlit as st
from email_validator import validate_email, EmailNotValidError
from api_client import ApiClient, ApiError, id_path, normalize, status_for

st.set_page_config(page_title="Student Registry", page_icon="🎓", layout="wide")
st.markdown("""<style>
.block-container {max-width:1440px;padding-top:2rem;}
h1 {letter-spacing:-.045em;} h2,h3 {letter-spacing:-.025em;}
[data-testid="stMetric"] {border:1px solid color-mix(in srgb, currentColor 15%, transparent);
border-radius:16px;padding:18px;}
div.stButton > button {border-radius:10px;}
</style>""", unsafe_allow_html=True)
st.session_state.setdefault("activity", [])


def changed():
    st.session_state["notice"] = "Changes saved successfully."
    st.rerun()


@st.dialog("Student details", width="large")
def editor(api, record=None):
    existing = record is not None
    record = record or {}
    identity = st.text_input("Student ID", value=record.get("id_new", ""), disabled=existing)
    name = st.text_input("Full name", value=record.get("full_name") or "", max_chars=100)
    email = st.text_input("Email", value=record.get("email") or "")
    major = st.text_input("Major", value=record.get("major") or "")
    current = record.get("gpa")
    valid = status_for(current) != "Invalid GPA"
    if existing and not valid:
        st.warning(f"Stored GPA ({current}) is invalid. Enter a corrected value before saving.")
    gpa = st.number_input("GPA", min_value=0.0, max_value=10.0,
                          value=float(current) if valid else None, step=0.1)
    st.caption(f"GPA status: {status_for(gpa)}")
    values = {"full_name": name.strip(), "email": email.strip(), "major": major.strip(), "gpa": gpa}
    updates = {k: v for k, v in values.items() if v != record.get(k)}
    if existing:
        st.caption("Changed fields: " + (", ".join(updates) or "None"))
    if st.button("Save changes" if existing else "Create student", type="primary"):
        try:
            if not identity.strip() or "/" in identity:
                raise ValueError("Enter a student ID without a slash; the API uses single-segment IDs.")
            if not 2 <= len(values["full_name"]) <= 100 or not values["major"]:
                raise ValueError("Enter a name of 2–100 characters and a major.")
            validate_email(values["email"], check_deliverability=False)
            if gpa is None:
                raise ValueError("Enter a GPA from 0 to 10.")
            if existing and not updates:
                st.info("No fields have changed.")
                return
            with st.spinner("Saving student…"):
                api.request("PUT", id_path("update_student", identity), json=updates) if existing else api.request(
                    "POST", "/add_student", json={"id_new": identity.strip(), **values})
            changed()
        except (ApiError, ValueError, EmailNotValidError) as exc:
            st.error(str(exc))


@st.dialog("Delete student")
def delete_dialog(api, record):
    st.write(f"Delete {record.get('full_name') or 'student'} (ID {record['id_new']})?")
    confirmed = st.checkbox("I understand this permanently deletes the record.")
    if st.button("Delete student", type="primary", disabled=not confirmed):
        try:
            api.request("DELETE", id_path("delete_student", record["id_new"]))
            st.session_state.pop("profile_id", None)
            changed()
        except ApiError as exc:
            st.error(str(exc))


with st.sidebar:
    st.title("🎓 Registry")
    st.caption("STUDENT WORKSPACE")
    base = st.text_input("API base URL", "http://127.0.0.1:8000")
    api = ApiClient(base, st.session_state.activity)
    st.button("Refresh data", width="stretch")
    with st.form("lookup"):
        lookup = st.text_input("Quick lookup by student ID")
        submitted = st.form_submit_button("Find student")
    if submitted and lookup.strip():
        try:
            found = normalize(api.request("GET", id_path("data_read", lookup.strip())), lookup.strip())[0]
            st.write(found)
        except ApiError as exc:
            st.error(str(exc))
    with st.expander("API routes"):
        st.code("GET /\nGET /data_read\nGET /data_read/{item_id}\nGET /data_filter?branch=…\nGET /data_sort?sort_by=…&order=…\nGET /data_paginate?page=…&limit=…\nPOST /add_student\nPUT /update_student/{student_id}\nDELETE /delete_student/{student_id}")

title, action = st.columns([5, 1])
title.title("Student Registry")
title.caption("One place to explore, review, and manage your students.")
if action.button("＋ Add student", type="primary", width="stretch"):
    editor(api)
if notice := st.session_state.pop("notice", None):
    st.success(notice)
try:
    with st.spinner("Loading students…"):
        records = normalize(api.request("GET", "/data_read"))
    st.sidebar.success("Connected · live API data")
except ApiError as exc:
    st.sidebar.error("API unavailable")
    st.error(str(exc))
    st.info("Start the backend from the project directory, then refresh.")
    st.code(".\\first_venv\\Scripts\\python.exe -m uvicorn main:app --reload")
    st.stop()

valid_records = [r for r in records if r["validate_gpa"] != "Invalid GPA"]
metrics = st.columns(4)
metrics[0].metric("Students", len(records))
metrics[1].metric("Average GPA", f"{sum(float(r['gpa']) for r in valid_records) / len(valid_records):.2f}" if valid_records else "—")
best = max(valid_records, key=lambda r: float(r["gpa"]), default=None)
metrics[2].metric("Highest GPA", best["gpa"] if best else "—")
if best:
    metrics[2].caption(best["full_name"] or best["id_new"])
metrics[3].metric("Needs review", sum(r["data_quality"] != "Complete" for r in records))
st.caption("GPA statistics exclude missing and out-of-range values. Status: Fail ≤ 3 · Pass ≤ 5 · Excellent > 5.")
directory, insights, activity = st.tabs(["Directory", "Insights", "Activity"])
with directory:
    controls = st.columns([3, 2, 1, 1])
    search = controls[0].text_input("Search", placeholder="ID, name, email, or major")
    major = controls[1].selectbox("Major", ["All majors"] + sorted({r["major"] for r in records if isinstance(r["major"], str) and r["major"]}))
    sort = controls[2].selectbox("Sort by", ["Default", "major", "gpa"])
    order = controls[3].selectbox("Order", ["asc", "desc"])
    view = records
    if major != "All majors":
        try:
            view = normalize(api.request("GET", "/data_filter", params={"branch": major}))
        except ApiError as exc:
            st.warning(f"Backend filter failed. Filtering the fetched records locally. {exc}")
            view = [r for r in records if r["major"] == major]
    if sort != "Default":
        try:
            sorted_records = normalize(api.request("GET", "/data_sort", params={"sort_by": sort, "order": order}))
            allowed = {r["id_new"] for r in view}
            view = [r for r in sorted_records if r["id_new"] in allowed]
        except ApiError as exc:
            st.warning(f"Backend sort failed. Sorting fetched records locally; incomplete values appear last. {exc}")
            complete = [r for r in view if (status_for(r[sort]) != "Invalid GPA" if sort == "gpa" else isinstance(r[sort], str))]
            missing = [r for r in view if r not in complete]
            view = sorted(complete, key=lambda r: float(r[sort]) if sort == "gpa" else r[sort], reverse=order == "desc") + missing
    if search.strip():
        view = [r for r in view if any(search.strip().casefold() in str(r[k] or "").casefold() for k in ("id_new", "full_name", "email", "major"))]
    rows = st.selectbox("Rows per page", [5, 10, 20, 50, 100], index=1)
    signature = (base, search, major, sort, order, rows)
    if st.session_state.get("view_signature") != signature:
        st.session_state.page = 1
        st.session_state.view_signature = signature
    pages = max(1, math.ceil(len(view) / rows))
    st.session_state.page = min(st.session_state.get("page", 1), pages)
    page = st.number_input("Page", min_value=1, max_value=pages, step=1, key="page")
    visible = view[(page - 1) * rows:page * rows]
    if search == "" and major == "All majors" and sort == "Default" and view:
        try:
            visible = normalize(api.request("GET", "/data_paginate", params={"page": page, "limit": rows}))
        except ApiError as exc:
            st.warning(f"Backend pagination failed; showing fetched records. {exc}")
    st.caption(f"{len(view)} matching students · Page {page} of {pages}")
    if not view:
        st.info("No students match this view. Adjust your filters or add a student.")
    else:
        columns = ["id_new", "full_name", "email", "major", "gpa", "validate_gpa", "data_quality"]
        st.dataframe(pd.DataFrame(visible)[columns], hide_index=True)
        ids = [r["id_new"] for r in view]
        if st.session_state.get("profile_id") not in ids:
            st.session_state.pop("profile_id", None)
        selected = st.selectbox("Open student profile", ids, index=None, key="profile_id")
        if selected:
            record = next(r for r in view if r["id_new"] == selected)
            with st.container(border=True):
                st.subheader(record["full_name"] or "Incomplete profile")
                st.write(f"ID: {selected}")
                st.write(f"Email: {record['email'] or 'Missing'} · Major: {record['major'] or 'Missing'}")
                st.write(f"GPA: {record['gpa']} · {record['validate_gpa']}")
                left, right = st.columns(2)
                if left.button("Edit student"):
                    editor(api, record)
                if right.button("Delete student"):
                    delete_dialog(api, record)
with insights:
    if not records:
        st.info("Add students to see insights.")
    else:
        left, right = st.columns(2)
        left.subheader("GPA status distribution")
        left.bar_chart(pd.Series([r["validate_gpa"] for r in records]).value_counts())
        right.subheader("Average GPA by major")
        chart_records = [r for r in valid_records if r["major"]]
        if chart_records:
            frame = pd.DataFrame(chart_records)
            frame["gpa"] = pd.to_numeric(frame["gpa"])
            right.bar_chart(frame.groupby("major")["gpa"].mean())
        else:
            right.info("No valid GPA and major pairs to chart.")
with activity:
    st.caption("Requests from this browser session only · latest 300 requests · times use the frontend server timezone.")
    log = pd.DataFrame(st.session_state.activity)
    st.dataframe(log, hide_index=True)
    st.download_button("Export activity CSV", log.to_csv(index=False), "activity.csv", "text/csv")
    if st.button("Clear activity"):
        st.session_state.activity.clear()
        st.rerun()
