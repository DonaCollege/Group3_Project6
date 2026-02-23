##
# @file app.py
# @brief Streamlit frontend for Financial Analytics API.
#
# @details
# Provides user interface for:
# - Browsing company data
# - Running analytics
# - Performing risk calculations
# - Monitoring API health
#
# Communicates with FastAPI backend via REST APIs.
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
    page_title="FinSight — Financial Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================
# Custom CSS
# =============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

:root {
    --bg:      #0a0e17;
    --surface: #111827;
    --border:  #1e2d40;
    --accent:  #00d4aa;
    --accent2: #ff6b35;
    --text:    #e2e8f0;
    --muted:   #64748b;
    --green:   #10b981;
    --red:     #ef4444;
    --yellow:  #f59e0b;
    --blue:    #00aaff;
}

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Header banner ── */
.fin-header {
    background: linear-gradient(135deg, #0a0e17 0%, #0f1f2e 50%, #0a0e17 100%);
    border-bottom: 1px solid var(--border);
    padding: 1.5rem 2rem 1.2rem;
    margin: -1rem -1rem 1.5rem -1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.fin-logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    background: linear-gradient(90deg, var(--accent), var(--blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
}
.fin-tagline {
    font-size: 0.7rem;
    color: var(--muted);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-top: 0.1rem;
}
.fin-api-badge {
    margin-left: auto;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.3rem 0.9rem;
    font-size: 0.68rem;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
}

/* ── Metric cards ── */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
    height: 100%;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), transparent);
}
.metric-label {
    font-size: 0.62rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.5rem;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.55rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1.1;
}
.metric-value-sm {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text);
}
.metric-sub {
    font-size: 0.66rem;
    color: var(--muted);
    margin-top: 0.35rem;
}

/* ── Pills ── */
.pill {
    display: inline-block;
    padding: 0.18rem 0.65rem;
    border-radius: 999px;
    font-size: 0.66rem;
    font-weight: 500;
    letter-spacing: 0.04em;
}
.pill-green  { background: rgba(16,185,129,.15); color: var(--green);  border: 1px solid rgba(16,185,129,.3); }
.pill-red    { background: rgba(239,68,68,.15);  color: var(--red);    border: 1px solid rgba(239,68,68,.3); }
.pill-yellow { background: rgba(245,158,11,.15); color: var(--yellow); border: 1px solid rgba(245,158,11,.3); }
.pill-blue   { background: rgba(0,170,255,.12);  color: var(--blue);   border: 1px solid rgba(0,170,255,.25); }

/* ── Section title ── */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
    margin-left: 0.4rem;
}

/* ── Latency text ── */
.latency { font-size: 0.63rem; color: var(--muted); letter-spacing: 0.04em; }

/* ── Health check row ── */
.health-row {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.75rem 1.2rem;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.health-row code {
    font-size: 0.78rem;
    color: var(--text);
    font-family: 'DM Mono', monospace;
}
.health-err {
    font-size: 0.7rem;
    color: var(--red);
    margin-top: 0.3rem;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--accent) !important;
    color: #0a0e17 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-weight: 500 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.5rem 1.2rem !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.82 !important; }
.stButton > button[kind="secondary"] {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,212,170,.15) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.76rem !important;
    color: var(--muted) !important;
    padding: 0.4rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #0a0e17 !important;
}

/* ── Dataframe ── */
.stDataFrame {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Slider ── */
.stSlider [role="slider"] { background: var(--accent) !important; }
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
            return ApiResult(True, r.status_code, elapsed_ms, data=r.json())
        try:
            payload = r.json()
            msg = payload.get("detail") or payload.get("error") or str(payload)
        except Exception:
            msg = r.text[:500]
        return ApiResult(False, r.status_code, elapsed_ms, error=msg)
    except requests.RequestException as e:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return ApiResult(False, 0, elapsed_ms, error=str(e))

def pill(label, kind="blue"):
    return f'<span class="pill pill-{kind}">{label}</span>'

# =============================
# Header
# =============================
st.markdown(f"""
<div class="fin-header">
    <div>
        <div class="fin-logo">FinSight</div>
        <div class="fin-tagline">Financial Analytics Platform</div>
    </div>
    <div class="fin-api-badge">API → {API_BASE_URL}</div>
</div>
""", unsafe_allow_html=True)

# =============================
# Sidebar
# =============================
with st.sidebar:
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:0.68rem;letter-spacing:0.14em;text-transform:uppercase;color:#64748b;margin-bottom:0.8rem;">Navigation</div>', unsafe_allow_html=True)
    page = st.radio("", ["📂  Browse Data", "📊  Analytics", "🔧  Health & Debug"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:0.68rem;letter-spacing:0.14em;text-transform:uppercase;color:#64748b;margin-bottom:0.8rem;">Filters</div>', unsafe_allow_html=True)

    ticker     = st.text_input("Ticker", value="AAPL", placeholder="e.g. AAPL, TSLA").strip().upper()
    start_date = st.date_input("Start date", value=date(2025, 1, 1))
    end_date   = st.date_input("End date",   value=date(2026, 2, 17))

    if start_date > end_date:
        st.error("Start must be before end date.")

    st.markdown("---")
    hc = api_request("GET", "/health")
    if hc.ok:
        st.markdown(f'<div style="font-size:0.72rem;color:#64748b;">API Status &nbsp;{pill("● ONLINE","green")}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="font-size:0.72rem;color:#64748b;">API Status &nbsp;{pill("● OFFLINE","red")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.63rem;color:#475569;margin-top:0.25rem;">{hc.elapsed_ms}ms response</div>', unsafe_allow_html=True)


# =====================================================
# PAGE: Browse Data
# =====================================================
if "Browse" in page:

    st.markdown('<div class="section-title">🔍 Company Search</div>', unsafe_allow_html=True)

    col_q, col_btn = st.columns([4, 1])
    with col_q:
        query = st.text_input("", placeholder="Search by ticker or company name...", label_visibility="collapsed", key="search_query")
    with col_btn:
        st.write("")
        do_search = st.button("Search", disabled=(len(query.strip()) == 0), key="search_btn")

    if do_search and query.strip():
        with st.spinner("Searching..."):
            res = api_request("GET", "/companies", params={"query": query.strip()})
        if res.ok and res.data is not None:
            items = res.data.get("items", [])
            st.markdown(f'Found **{len(items)}** result(s) &nbsp;{pill(f"{res.elapsed_ms}ms","blue")}', unsafe_allow_html=True)
            if items:
                st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)
            else:
                st.info("No matching companies found.")
        else:
            st.error(f"Search failed: {res.error}")

    st.markdown("---")

    if ticker:
        st.markdown(f'<div class="section-title">📌 {ticker} — Details & Price History</div>', unsafe_allow_html=True)

        details = api_request("GET", f"/companies/{ticker}")
        prices  = api_request("GET", f"/prices/{ticker}", params={"start": str(start_date), "end": str(end_date)})
        rows    = prices.data.get("rows", []) if prices.ok and prices.data else []

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            t = details.data.get("ticker", ticker) if details.ok and details.data else ticker
            st.markdown(f'<div class="metric-card"><div class="metric-label">Ticker</div><div class="metric-value">{t}</div></div>', unsafe_allow_html=True)
        with c2:
            n = details.data.get("name", "—") if details.ok and details.data else "—"
            st.markdown(f'<div class="metric-card"><div class="metric-label">Company</div><div class="metric-value-sm">{n}</div></div>', unsafe_allow_html=True)
        with c3:
            s = details.data.get("sector", "—") if details.ok and details.data else "—"
            st.markdown(f'<div class="metric-card"><div class="metric-label">Sector</div><div class="metric-value-sm">{s}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Data Points</div><div class="metric-value">{len(rows)}</div><div class="metric-sub">{start_date} → {end_date}</div></div>', unsafe_allow_html=True)

        st.write("")

        if not details.ok:
            st.error(f"Could not load company details: {details.error}")

        if rows:
            dfp = pd.DataFrame(rows)
            tab_chart, tab_table = st.tabs(["📈  Price Chart", "📋  Raw Data"])

            with tab_chart:
                if "date" in dfp.columns and "close" in dfp.columns:
                    dfp["date"] = pd.to_datetime(dfp["date"], errors="coerce")
                    dfp = dfp.dropna(subset=["date"]).sort_values("date")
                    st.line_chart(dfp.set_index("date")["close"], height=300, use_container_width=True)

                    latest = dfp["close"].iloc[-1]
                    high   = dfp["close"].max()
                    low    = dfp["close"].min()
                    change = ((latest - dfp["close"].iloc[0]) / dfp["close"].iloc[0]) * 100

                    s1, s2, s3, s4 = st.columns(4)
                    s1.metric("Latest Close", f"${latest:.2f}")
                    s2.metric("Period High",  f"${high:.2f}")
                    s3.metric("Period Low",   f"${low:.2f}")
                    s4.metric("Total Return", f"{change:+.2f}%", delta=f"{change:+.2f}%")

            with tab_table:
                st.dataframe(dfp, use_container_width=True, hide_index=True)

        elif prices.ok:
            st.info("No price data for the selected date range.")
        else:
            st.error(f"Price fetch failed: {prices.error}")

    st.markdown("---")
    st.markdown('<div class="section-title">⚙️ Manage Records</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["➕  Create", "✏️  Update", "🗑️  Delete"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name", key="create_name")
            ticker_input = st.text_input("Ticker Symbol", key="create_ticker")
        with col2:
            sector = st.selectbox("Sector", ["Technology", "Finance", "Healthcare"], key="create_sector")
        if st.button("➕ Create Company", key="create_btn") and company_name and ticker_input:
            res = api_request("POST", "/companies", json={"companyName": company_name, "ticker": ticker_input, "sector": sector})
            st.success("✅ Company created!") if res.ok else st.error(f"❌ {res.error}")
            if res.ok: st.rerun()

    with tab2:
        company_id = st.number_input("Stock ID to Update", min_value=1, step=1, key="update_id")
        c1, c2, c3 = st.columns(3)
        with c1: new_name   = st.text_input("New Name",   key="update_name")
        with c2: new_ticker = st.text_input("New Ticker", key="update_ticker")
        with c3: new_sector = st.selectbox("New Sector", ["", "Technology", "Finance", "Healthcare"], key="update_sector")
        if st.button("✏️ Update", key="update_btn") and new_name:
            payload = {k: v for k, v in {"companyName": new_name, "ticker": new_ticker, "sector": new_sector}.items() if v}
            res = api_request("PUT", f"/companies/{company_id}", json=payload)
            st.success("✅ Updated!") if res.ok else st.error(f"❌ {res.error}")
            if res.ok: st.rerun()

    with tab3:
        delete_id = st.number_input("Stock ID to Delete", min_value=1, step=1, key="delete_id")
        st.warning(f"⚠️ This will permanently delete stock ID **{delete_id}**.")
        if st.button("🗑️ Confirm Delete", key="delete_btn"):
            res = api_request("DELETE", f"/companies/{delete_id}")
            st.success("✅ Deleted!") if res.ok else st.error(f"❌ {res.error}")
            if res.ok: st.rerun()


# =====================================================
# PAGE: Analytics
# =====================================================
elif "Analytics" in page:

    if not ticker:
        st.info("👈 Enter a ticker in the sidebar to get started.")
        st.stop()

    st.markdown(f'<div class="section-title">📊 Analytics — {ticker}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div style="font-size:0.7rem;color:#64748b;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.6rem;">Volatility Check</div>', unsafe_allow_html=True)
        iterations = st.slider("Monte Carlo Iterations", 1000, 50000, 10000, step=1000)
        with st.spinner("Computing..."):
            vol_res = api_request("GET", f"/analytics/volatility?ticker={ticker}&iterations={iterations}")

        if vol_res.ok and vol_res.data:
            vol  = vol_res.data.get("forecasted_volatility", 0)
            risk = vol_res.data.get("risk_level", "N/A")
            pill_kind = "red" if "High" in str(risk) else ("yellow" if "Med" in str(risk) else "green")
            st.markdown(f"""
            <div class="metric-card" style="margin-top:0.5rem">
                <div class="metric-label">Forecasted Volatility</div>
                <div class="metric-value">{vol:.4f}</div>
                <div class="metric-sub" style="margin-top:0.5rem">
                    Risk &nbsp;{pill(risk, pill_kind)}&nbsp;&nbsp;<span class="latency">{vol_res.elapsed_ms}ms</span>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.error(vol_res.error)

    with col2:
        st.markdown('<div style="font-size:0.7rem;color:#64748b;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.6rem;">Deep Analysis</div>', unsafe_allow_html=True)
        analysis_type = st.selectbox("Analysis Type", ["returns", "volatility"], key="analysis_type")
        window        = st.number_input("Rolling Window (days)", 10, 365, 30, key="analysis_window")

        if st.button("🚀 Run Analysis", key="run_analysis"):
            with st.spinner("Running..."):
                res = api_request("POST", f"/analytics/{ticker}", json={"type": analysis_type, "params": {"window": window}}, timeout=60)
            if res.ok:
                st.success(f"✅ Completed in {res.elapsed_ms}ms")
                st.json(res.data)
            else:
                st.error(res.error)

    st.markdown("---")
    st.markdown('<div class="section-title">⚠️ Value at Risk (VaR)</div>', unsafe_allow_html=True)

    v1, v2 = st.columns(2)
    with v1: confidence  = st.slider("Confidence Level", 0.90, 0.99, 0.95, 0.01)
    with v2: simulations = st.slider("Simulations", 10000, 100000, 50000, step=5000)

    if st.button("Calculate VaR", key="calc_var"):
        with st.spinner("Running Monte Carlo simulation..."):
            res = api_request("POST", "/risk/var", json={"ticker": ticker, "confidence": confidence, "simulations": simulations}, timeout=60)
        if res.ok:
            var_val = res.data.get("value_at_risk", 0)
            st.markdown(f"""
            <div class="metric-card" style="max-width:340px;margin-top:0.5rem">
                <div class="metric-label">Value at Risk ({confidence:.0%} confidence)</div>
                <div class="metric-value">{var_val:.4f}</div>
                <div class="metric-sub">{simulations:,} simulations &nbsp;<span class="latency">{res.elapsed_ms}ms</span></div>
            </div>""", unsafe_allow_html=True)
            with st.expander("Full Response"):
                st.json(res.data)
        else:
            st.error(res.error)


# =====================================================
# PAGE: Health & Debug
# =====================================================
else:
    st.markdown('<div class="section-title">🔧 System Health</div>', unsafe_allow_html=True)

    endpoints = [
        ("GET", "/health",                                                           None),
        ("GET", f"/companies/{ticker or 'AAPL'}",                                   None),
        ("GET", f"/prices/{ticker or 'AAPL'}",   {"start": "2025-01-01", "end": "2025-03-01"}),
        ("GET", f"/analytics/volatility?ticker={ticker or 'AAPL'}&iterations=1000", None),
    ]

    if st.button("🔄 Run All Health Checks"):
        for method, path, params in endpoints:
            with st.spinner(f"Checking {path}..."):
                r = api_request(method, path, params=params, timeout=10)
            status_pill = pill(f"✓ {r.status_code}", "green") if r.ok else pill(f"✗ {r.status_code or 'ERR'}", "red")
            err_html = f'<div class="health-err">{r.error}</div>' if not r.ok else ""
            st.markdown(f"""
            <div class="health-row">
                <div>
                    <code>{path}</code>
                    {err_html}
                </div>
                <div style="display:flex;gap:0.6rem;align-items:center">
                    <span class="latency">{r.elapsed_ms}ms</span>
                    {status_pill}
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title">📚 Quick Reference</div>', unsafe_allow_html=True)

    ref1, ref2 = st.columns(2)
    with ref1:
        st.markdown("""
**Data Endpoints**
- `GET /health` — API liveness check
- `GET /companies` — Search companies
- `GET /companies/{ticker}` — Company details
- `GET /prices/{ticker}` — Price history
        """)
    with ref2:
        st.markdown("""
**Analytics Endpoints**
- `GET /analytics/volatility` — Volatility forecast
- `POST /analytics/{ticker}` — Deep analysis
- `POST /risk/var` — Value at Risk (Monte Carlo)
        """)

    st.markdown(f"""
    <div class="metric-card" style="margin-top:1rem">
        <div class="metric-label">Interactive API Docs</div>
        <div style="font-size:0.85rem;margin-top:0.4rem;color:var(--text)">
            Open <a href="http://localhost:8000/docs" target="_blank" style="color:var(--accent)">localhost:8000/docs</a>
            in your browser for the full Swagger UI.
        </div>
    </div>""", unsafe_allow_html=True)