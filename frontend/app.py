##
# @file app.py
# @brief Streamlit frontend for Financial Analytics API.
# @note Accessibility: WCAG AA contrast, ARIA roles, keyboard-navigable.
##

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
import requests
import pandas as pd
import streamlit as st
from datetime import date

# =============================
# Config
# =============================
API_BASE_URL = os.getenv("API_BASE_URL", "http://financial_api:8000").rstrip("/")

st.set_page_config(
    page_title="FinSight - Financial Analytics",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================
# Custom CSS (WCAG AA compliant)
# =============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

:root {
    --bg:      #0a0e17;
    --surface: #111827;
    --border:  #1e2d40;
    --accent:  #00d4aa;
    --text:    #e2e8f0;
    --muted:   #8ba3bc;
    --green:   #10b981;
    --red:     #ef4444;
}

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

.topbar {
    background: #0d1520;
    border-bottom: 1px solid var(--border);
    padding: 0.9rem 2rem;
    margin: -1rem -1rem 1.5rem -1rem;
    display: flex;
    align-items: center;
    gap: 2rem;
}

.topbar-logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--accent);
}

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.2rem;
}

.pill {
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
}
.pill-green { background: rgba(16,185,129,.15); color: #34d399; }
.pill-red { background: rgba(239,68,68,.15); color: #f87171; }

.health-row {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.6rem 1rem;
    margin-bottom: 0.4rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
</style>
""", unsafe_allow_html=True)

# =============================
# API Helper
# =============================
@dataclass
class ApiResult:
    ok: bool
    status_code: int
    elapsed_ms: int
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

def api_request(method: str, path: str, *, params=None, json=None, timeout=15) -> ApiResult:
    url = f"{API_BASE_URL}{path}"
    start = time.perf_counter()
    try:
        r = requests.request(method, url, params=params, json=json, timeout=timeout)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        if r.ok:
            return ApiResult(True, r.status_code, elapsed_ms, data=r.json() if r.text else {})
        msg = r.text[:500]
        return ApiResult(False, r.status_code, elapsed_ms, error=msg)
    except Exception as e:
        return ApiResult(False, 0, 0, error=str(e))

def pill(label, kind="green"):
    return f'<span class="pill pill-{kind}">{label}</span>'

# =============================
# Navigation
# =============================
hc = api_request("GET", "/health")
status_ui = pill("ONLINE", "green") if hc.ok else pill("OFFLINE", "red")

st.markdown(f"""
<div class="topbar">
    <div class="topbar-logo">FinSight</div>
    <div style="margin-left:auto; display:flex; gap:1.5rem; align-items:center;">
        <div style="font-size:0.7rem;">API STATUS: {status_ui}</div>
        <div style="font-size:0.7rem; color:var(--muted);">{API_BASE_URL}</div>
    </div>
</div>
""", unsafe_allow_html=True)

nav_col, f1, f2, f3 = st.columns([2, 1, 1, 1])
with nav_col:
    page = st.radio("Navigation", ["Data Management", "Analytics", "System Health"], label_visibility="collapsed", horizontal=True)
with f1:
    ticker = st.text_input("Ticker", value="AAPL").strip().upper()
with f2:
    start_date = st.date_input("Start", value=date(2025, 1, 1))
with f3:
    end_date = st.date_input("End", value=date(2026, 2, 17))

st.divider()

# =====================================================
# PAGE: Data Management
# =====================================================
if page == "Data Management":
    st.subheader("Search and Records")
    
    q_col, btn_col = st.columns([4, 1])
    with q_col:
        query = st.text_input("Search companies...", label_visibility="collapsed")
    with btn_col:
        do_search = st.button("Search", use_container_width=True)

    if do_search and query:
        res = api_request("GET", "/companies", params={"query": query})
        if res.ok:
            st.dataframe(pd.DataFrame(res.data.get("items", [])), use_container_width=True, hide_index=True)

    st.write("---")
    
    t1, t2, t3, t4 = st.tabs(["Create", "Update (PUT)", "Patch (PATCH)", "Delete"])
    
    with t1:
        c_name = st.text_input("Name", key="c1")
        c_tick = st.text_input("Ticker", key="c2")
        if st.button("Execute POST"):
            res = api_request("POST", "/companies", json={"companyName": c_name, "ticker": c_tick})
            st.success("Record Created") if res.ok else st.error(res.error)

    with t2:
        u_id = st.number_input("Stock ID", min_value=1, key="u1")
        u_name = st.text_input("New Name", key="u2")
        if st.button("Execute PUT"):
            res = api_request("PUT", f"/companies/{u_id}", json={"companyName": u_name})
            st.success("Full Update Successful") if res.ok else st.error(res.error)

    with t3:
        p_id = st.number_input("Stock ID", min_value=1, key="p1")
        p_field = st.selectbox("Field", ["companyName", "ticker", "sector"])
        p_val = st.text_input("New Value")
        if st.button("Execute PATCH"):
            res = api_request("PATCH", f"/companies/{p_id}", json={p_field: p_val})
            st.success("Partial Update Successful") if res.ok else st.error(res.error)

    with t4:
        d_id = st.number_input("Stock ID", min_value=1, key="d1")
        if st.button("Execute DELETE"):
            res = api_request("DELETE", f"/companies/{d_id}")
            st.success("Record Deleted") if res.ok else st.error(res.error)

# =====================================================
# PAGE: System Health (Demonstrating SYS-020)
# =====================================================
elif page == "System Health":
    st.subheader("Route Verification (SYS-020)")
    
    # Updated to check the new PATCH and OPTIONS verbs specifically
    test_endpoints = [
        ("GET", "/health", None),
        ("GET", f"/companies/{ticker}", None),
        ("POST", "/companies", {"companyName": "Test", "ticker": "TEST"}),
        ("PUT", "/companies/1", {"companyName": "Updated"}),
        ("PATCH", "/companies/1", {"sector": "Tech"}),
        ("DELETE", "/companies/999", None),
        ("OPTIONS", f"/companies/1", None),
    ]

    if st.button("Run Protocol Diagnostic"):
        for method, path, body in test_endpoints:
            res = api_request(method, path, json=body)
            color = "green" if res.status_code < 400 or res.status_code == 404 else "red"
            st.markdown(f"""
            <div class="health-row">
                <code>{method} {path}</code>
                <div>
                    <span style="font-size:0.7rem; color:var(--muted); margin-right:10px;">{res.elapsed_ms}ms</span>
                    {pill(res.status_code, color)}
                </div>
            </div>
            """, unsafe_allow_html=True)

# =====================================================
# PAGE: Analytics
# =====================================================
else:
    st.subheader(f"Analysis: {ticker}")
    if not ticker:
        st.warning("Please enter a ticker symbol.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.write("Volatility Forecast")
            iter = st.slider("Iterations", 1000, 10000, 5000)
            if st.button("Run"):
                res = api_request("GET", f"/analytics/volatility?ticker={ticker}&iterations={iter}")
                if res.ok:
                    st.metric("Forecasted Volatility", f"{res.data.get('forecasted_volatility', 0):.4f}")
        with col2:
            st.write("Risk Simulation")
            if st.button("Calculate VaR"):
                res = api_request("POST", "/risk/var", json={"ticker": ticker, "confidence": 0.95})
                if res.ok:
                    st.metric("Value at Risk", f"{res.data.get('value_at_risk', 0):.4f}")