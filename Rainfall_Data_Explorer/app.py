import json
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from modules.data_manager import load_records, save_records, validate_import_dataframe
from modules.analytics import get_summary, monthly_summary

st.set_page_config(page_title="Rainfall Data Explorer", page_icon="🌧️", layout="wide")

# Demo login credentials. Change these before deploying publicly.
DEMO_USERNAME = "admin"
DEMO_PASSWORD = "rainfall123"

def login_screen():
    st.markdown("""
    <style>
    .stApp {background: linear-gradient(135deg,#eaf4ff 0%,#f7fbff 100%);}
    .login-title {text-align:center;color:#12345a;font-size:2.25rem;font-weight:800;}
    .login-sub {text-align:center;color:#52677f;margin-bottom:1.5rem;}
    </style>
    """, unsafe_allow_html=True)
    left, center, right = st.columns([1, 1.1, 1])
    with center:
        st.markdown("<div class='login-title'>🌧️ Rainfall Data Explorer</div>", unsafe_allow_html=True)
        st.markdown("<div class='login-sub'>Sign in to access the rainfall monitoring dashboard</div>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            if username == DEMO_USERNAME and password == DEMO_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")
        st.info("Demo login — Username: `admin`  |  Password: `rainfall123`")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    login_screen()
    st.stop()

st.title("🌧️ Rainfall Data Explorer")
st.caption("Explore rainfall records, monthly patterns, and summary insights.")
with st.sidebar:
    st.success("Logged in")
    if st.button("Log out", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    page = st.radio("Navigation", ["Dashboard", "Add Record", "View & Search", "Data Import", "Reports", "About"])

records = load_records()
required = ["record_id", "date", "location", "rainfall_mm", "weather_condition", "remarks"]

if page == "Dashboard":
    st.subheader("Rainfall Overview")
    if records.empty:
        st.info("No records yet. Import the sample CSV from the Data Import page to get started.")
    else:
        s = get_summary(records)
        cols = st.columns(4)
        cols[0].metric("Total rainfall", f"{s['total']:.1f} mm")
        cols[1].metric("Average rainfall", f"{s['average']:.1f} mm")
        cols[2].metric("Highest rainfall", f"{s['maximum']:.1f} mm")
        cols[3].metric("Records", str(s["count"]))
        st.write(f"**Locations covered:** {s['locations']}  |  **Date range:** {s['date_range']}")
        monthly = monthly_summary(records)
        if not monthly.empty:
            st.subheader("Monthly rainfall trend")
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(monthly["month"], monthly["rainfall_mm"], marker="o")
            ax.set_xlabel("Month")
            ax.set_ylabel("Rainfall (mm)")
            ax.set_title("Total rainfall by month")
            ax.grid(True, alpha=.3)
            plt.xticks(rotation=35, ha="right")
            st.pyplot(fig)
            plt.close(fig)
        st.subheader("Recent records")
        st.dataframe(records.sort_values("date", ascending=False).head(10), use_container_width=True)

elif page == "Add Record":
    st.subheader("Add a rainfall record")
    with st.form("add_record"):
        c1, c2 = st.columns(2)
        record_id = c1.text_input("Record ID")
        record_date = c2.date_input("Date", value=date.today())
        location = c1.text_input("Location")
        rainfall = c2.number_input("Rainfall (mm)", min_value=0.0, max_value=2000.0, step=0.5)
        weather = c1.selectbox("Weather condition", ["Light Rain", "Moderate Rain", "Heavy Rain", "Very Heavy Rain", "No Rain"])
        remarks = c2.text_input("Remarks")
        submitted = st.form_submit_button("Save record")
    if submitted:
        if not record_id.strip() or not location.strip():
            st.error("Record ID and location are required.")
        elif record_id.strip() in records["record_id"].astype(str).tolist():
            st.error("That record ID already exists.")
        else:
            new = pd.DataFrame([{
                "record_id": record_id.strip(), "date": str(record_date),
                "location": location.strip(), "rainfall_mm": float(rainfall),
                "weather_condition": weather, "remarks": remarks.strip()
            }])
            records = pd.concat([records, new], ignore_index=True)
            save_records(records)
            st.success("Record saved successfully.")
            st.rerun()

elif page == "View & Search":
    st.subheader("View, search, and manage records")
    if records.empty:
        st.info("No records available.")
    else:
        query = st.text_input("Search by ID, location, weather, or remarks")
        filtered = records.copy()
        if query:
            mask = filtered.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
            filtered = filtered[mask]
        st.dataframe(filtered, use_container_width=True)
        ids = filtered["record_id"].astype(str).tolist()
        if ids:
            chosen = st.selectbox("Select a record ID to delete", ids)
            if st.button("Delete selected record"):
                records = records[records["record_id"].astype(str) != chosen]
                save_records(records)
                st.success(f"Deleted record {chosen}.")
                st.rerun()

elif page == "Data Import":
    st.subheader("Import rainfall data")
    st.write("CSV must contain: " + ", ".join(required))
    sample_path = Path("data/rainfall_data.csv")
    if sample_path.exists():
        st.download_button("Download sample CSV", sample_path.read_bytes(), "rainfall_data.csv", "text/csv")
    upload = st.file_uploader("Upload a CSV file", type=["csv"])
    if upload is not None:
        try:
            incoming = pd.read_csv(upload)
            valid, errors, cleaned = validate_import_dataframe(incoming, records)
            if errors:
                st.error("Import was not completed. Please correct these issues:")
                for error in errors:
                    st.write("• " + error)
            else:
                st.success(f"Validation passed: {len(cleaned)} records ready to import.")
                if st.button("Validate and Import"):
                    combined = pd.concat([records, cleaned], ignore_index=True)
                    save_records(combined)
                    st.success(f"Imported {len(cleaned)} records successfully.")
                    st.rerun()
        except Exception as exc:
            st.error(f"Could not read this CSV: {exc}")

elif page == "Reports":
    st.subheader("Reports and exports")
    if records.empty:
        st.info("Add or import records to generate reports.")
    else:
        st.download_button("Download records as CSV", records.to_csv(index=False).encode("utf-8"), "rainfall_records.csv", "text/csv")
        st.download_button("Download records as JSON", records.to_json(orient="records", indent=2).encode("utf-8"), "rainfall_records.json", "application/json")
        s = get_summary(records)
        report = (f"# Rainfall Executive Summary\n\n"
                  f"- Number of records: {s['count']}\n- Total rainfall: {s['total']:.1f} mm\n"
                  f"- Average rainfall: {s['average']:.1f} mm\n- Maximum rainfall: {s['maximum']:.1f} mm\n"
                  f"- Minimum rainfall: {s['minimum']:.1f} mm\n- Locations: {s['locations']}\n"
                  f"- Date range: {s['date_range']}\n")
        st.download_button("Download executive summary (Markdown)", report, "rainfall_summary.md", "text/markdown")
        monthly = monthly_summary(records)
        if not monthly.empty:
            st.dataframe(monthly, use_container_width=True)

else:
    st.subheader("About this project")
    st.write("Rainfall Data Explorer is a learning project for recording, searching, analyzing, and visualizing rainfall measurements.")
    st.warning("The included sample measurements are illustrative and are not official meteorological observations.")
    st.markdown("**Demo login:** `admin`  \n**Demo password:** `rainfall123`")
