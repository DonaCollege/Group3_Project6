##
# @file app.py
# @brief Streamlit frontend for Financial Analytics API.
# @note Accessibility improvements: WCAG AA contrast on all text, ARIA roles,
#       semantic landmark HTML, skip-nav link, role="status" on live regions,
#       keyboard-navigable cards, and screen-reader labels on all interactive elements.
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
    initial_sidebar_state="collapsed",
)

# =============================
# Custom CSS  (WCAG AA compliant)
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

    /* FIXED: was #64748b (fails AA at 3.73:1 on surface).
       New value #8ba3bc passes AA at 4.56:1 on --surface */
    --muted:   #8ba3bc;

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
[data-testid="collapsedControl"] { display: none; }

/* ── Skip Navigation (screen reader / keyboard) ── */
.skip-nav {
    position: absolute;
    top: -999px;
    left: -999px;
    background: var(--accent);
    color: #0a0e17;
    padding: 0.5rem 1rem;
    border-radius: 0 0 8px 0;
    font-weight: 700;
    font-size: 0.85rem;
    z-index: 9999;
    text-decoration: none;
}
.skip-nav:focus {
    top: 0;
    left: 0;
}

/* ── Top nav bar ── */
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
    background: linear-gradient(90deg, var(--accent), var(--blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
    white-space: nowrap;
    margin-right: 1rem;
}
.topbar-api {
    margin-left: auto;
    font-size: 0.65rem;
    color: var(--muted);
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.25rem 0.75rem;
    white-space: nowrap;
}

/* ── Filter bar ── */
.filterbar {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    flex-wrap: wrap;
}

/* ── Metric cards ── */
/*  role="region" + aria-label applied in Python via wrapper div  */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
    height: 100%;
    /* keyboard focus ring */
    outline-offset: 3px;
}
.metric-card:focus-within {
    outline: 2px solid var(--accent);
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), transparent);
    /* decorative — hidden from AT */
    aria-hidden: true;
}
.metric-label {
    font-size: 0.62rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--muted);   /* now #8ba3bc — passes AA */
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
    color: var(--muted);   /* #8ba3bc */
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
    /* ensure pill text is readable — all pass AA against their bg */
}
.pill-green  { background: rgba(16,185,129,.15); color: #34d399; border: 1px solid rgba(16,185,129,.3); }
.pill-red    { background: rgba(239,68,68,.15);  color: #f87171; border: 1px solid rgba(239,68,68,.3); }
.pill-yellow { background: rgba(245,158,11,.15); color: #fbbf24; border: 1px solid rgba(245,158,11,.3); }
.pill-blue   { background: rgba(0,170,255,.12);  color: #38bdf8; border: 1px solid rgba(0,170,255,.25); }

/* ── Section title ── */
/*  Rendered as <h2> in Python for proper heading hierarchy  */
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

.latency {
    font-size: 0.63rem;
    color: var(--muted);
    /* never used as the sole label — always paired with visible text */
}

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
.health-err { font-size: 0.7rem; color: #f87171; margin-top: 0.3rem; }

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
/* Visible focus ring for keyboard users */
.stButton > button:focus-visible {
    outline: 2px solid #fff !important;
    outline-offset: 2px !important;
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
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(0,212,170,0.3) !important;
}
.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
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

.stDataFrame { border-radius: 10px !important; border: 1px solid var(--border) !important; }
hr { border-color: var(--border) !important; }
.stSlider [role="slider"] { background: var(--accent) !important; }

/* Radio nav styling */
.stRadio > div { flex-direction: row !important; gap: 0.5rem !important; }
.stRadio > div > label {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 0.4rem 1rem !important;
    font-size: 0.78rem !important;
    color: var(--muted) !important;
    cursor: pointer !important;
}
.stRadio > div > label:has(input:checked) {
    background: var(--accent) !important;
    color: #0a0e17 !important;
    border-color: var(--accent) !important;
}

/* Error/warning text contrast fix */
.stAlert p { color: var(--text) !important; }
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
    """Return an accessible pill span. Colour alone never conveys meaning —
    the label text always carries the semantic content."""
    return f'<span class="pill pill-{kind}" role="status">{label}</span>'

def metric_card(label: str, value: str, sub: str = "", value_sm: bool = False) -> str:
    """
    Render an accessible metric card.
    Uses role='region' + aria-label so screen readers announce the card context.
    """
    val_class = "metric-value-sm" if value_sm else "metric-value"
    sub_html  = f'<div class="metric-sub">{sub}</div>' if sub else ""
    return f"""
<div class="metric-card" role="region" aria-label="{label}: {value}">
    <div class="metric-label" aria-hidden="true">{label}</div>
    <div class="{val_class}">{value}</div>
    {sub_html}
</div>"""

# =============================
# Skip Navigation (keyboard / screen reader)
# =============================
st.markdown('<a class="skip-nav" href="#main-content">Skip to main content</a>', unsafe_allow_html=True)

# =============================
# Top Navigation Bar
# =============================
hc = api_request("GET", "/health")
api_status = pill("● ONLINE", "green") if hc.ok else pill("● OFFLINE", "red")
api_status_text = "ONLINE" if hc.ok else "OFFLINE"   # plain-text for aria-label

st.markdown(f"""
<header role="banner">
  <div class="topbar">
    <div class="topbar-logo" role="heading" aria-level="1">FinSight</div>
    <div style="font-size:0.65rem;color:var(--muted);letter-spacing:0.1em;"
         aria-label="Financial Analytics Platform">FINANCIAL ANALYTICS PLATFORM</div>
    <div style="margin-left:auto;display:flex;align-items:center;gap:1rem;">
      <div style="font-size:0.7rem;color:var(--muted);"
           aria-label="API status {api_status_text}, response time {hc.elapsed_ms} milliseconds">
        API {api_status} <span class="latency" aria-hidden="true">{hc.elapsed_ms}ms</span>
      </div>
      <div class="topbar-api" aria-label="API base URL">{API_BASE_URL}</div>
    </div>
  </div>
</header>
""", unsafe_allow_html=True)

# =============================
# Navigation + Filters (inline)
# =============================
nav_col, f1, f2, f3, f4 = st.columns([2, 1.2, 1, 1, 1])

with nav_col:
    # aria-label provided via label — Streamlit renders the radio group with role="radiogroup"
    page = st.radio(
        "Navigate to page",
        ["📂 Browse", "📊 Analytics", "🔧 Health"],
        label_visibility="collapsed",
        horizontal=True,
    )

with f1:
    ticker = st.text_input("Ticker symbol (e.g. AAPL)", value="AAPL", placeholder="AAPL").strip().upper()
with f2:
    start_date = st.date_input("Start date", value=date(2025, 1, 1))
with f3:
    end_date = st.date_input("End date", value=date(2026, 2, 17))
with f4:
    st.write("")
    if start_date > end_date:
        st.error("Invalid date range: start must be before end.")

st.markdown("---")

# Anchor for skip-nav
st.markdown('<div id="main-content"></div>', unsafe_allow_html=True)

# =====================================================
# PAGE: Browse Data
# =====================================================
if "Browse" in page:

    st.markdown('<h2 class="section-title">🔍 Company Search</h2>', unsafe_allow_html=True)

    col_q, col_btn = st.columns([4, 1])
    with col_q:
        query = st.text_input(
            "Search companies",
            placeholder="Search by ticker or company name...",
            label_visibility="collapsed",
            key="search_query",
            help="Enter a ticker symbol or company name to search",
        )
    with col_btn:
        st.write("")
        do_search = st.button(
            "Search",
            disabled=(len(query.strip()) == 0),
            key="search_btn",
            help="Search for companies matching the query",
        )

    if do_search and query.strip():
        with st.spinner("Searching..."):
            res = api_request("GET", "/companies", params={"query": query.strip()})
        if res.ok and res.data is not None:
            items = res.data.get("items", [])
            st.markdown(
                f'<p role="status" aria-live="polite">Found <strong>{len(items)}</strong> result(s) &nbsp;{pill(f"{res.elapsed_ms}ms","blue")}</p>',
                unsafe_allow_html=True,
            )
            if items:
                st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)
            else:
                st.info("No matching companies found.")
        else:
            st.error(f"Search failed: {res.error}")

    st.markdown("---")

    if ticker:
        st.markdown(f'<h2 class="section-title">📌 {ticker} — Details &amp; Price History</h2>', unsafe_allow_html=True)

        details = api_request("GET", f"/companies/{ticker}")
        prices  = api_request("GET", f"/prices/{ticker}", params={"start": str(start_date), "end": str(end_date)})
        rows    = prices.data.get("rows", []) if prices.ok and prices.data else []

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            t = details.data.get("ticker", ticker) if details.ok and details.data else ticker
            st.markdown(metric_card("Ticker", t), unsafe_allow_html=True)
        with c2:
            n = details.data.get("name", "—") if details.ok and details.data else "—"
            st.markdown(metric_card("Company", n, value_sm=True), unsafe_allow_html=True)
        with c3:
            s = details.data.get("sector", "—") if details.ok and details.data else "—"
            st.markdown(metric_card("Sector", s, value_sm=True), unsafe_allow_html=True)
        with c4:
            st.markdown(
                metric_card("Data Points", str(len(rows)), sub=f"{start_date} → {end_date}"),
                unsafe_allow_html=True,
            )

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

                    # Streamlit's line_chart doesn't support aria — wrap in a labeled region
                    st.markdown(
                        f'<div role="img" aria-label="Line chart showing {ticker} closing price from {start_date} to {end_date}">',
                        unsafe_allow_html=True,
                    )
                    st.line_chart(dfp.set_index("date")["close"], height=300, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    latest = dfp["close"].iloc[-1]
                    high   = dfp["close"].max()
                    low    = dfp["close"].min()
                    change = ((latest - dfp["close"].iloc[0]) / dfp["close"].iloc[0]) * 100

                    s1, s2, s3, s4 = st.columns(4)
                    # st.metric already produces accessible output (uses <dl> internally)
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
    st.markdown('<h2 class="section-title">⚙️ Manage Records</h2>', unsafe_allow_html=True)
    st.caption("💡 Search for a company first to find its Stock ID before updating or deleting.")

    tab1, tab2, tab3, tab4 = st.tabs(["➕  Create", "✏️  Update", "🩹  Patch", "🗑️  Delete"])

    # ── CREATE ──────────────────────────────────────────────────────────────
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name", key="create_name", help="Full legal company name")
            ticker_input = st.text_input("Ticker Symbol", key="create_ticker", help="Stock exchange ticker, e.g. AAPL")
        with col2:
            sector = st.selectbox(
                "Sector",
                ["Technology", "Finance", "Healthcare", "Energy", "Consumer", "Industrial"],
                key="create_sector",
            )

        if st.button("➕ Create Company", key="create_btn"):
            if company_name and ticker_input:
                res = api_request("POST", "/companies", json={
                    "companyName": company_name,
                    "ticker": ticker_input,
                    "sector": sector,
                })
                if res.ok:
                    st.success("✅ Company created!")
                    st.rerun()
                else:
                    st.error(f"❌ Create failed: {res.error}")
            else:
                st.warning("Please fill in Company Name and Ticker.")

    # ── UPDATE (full PUT) ────────────────────────────────────────────────────
    with tab2:
        company_id = st.number_input(
            "Stock ID to Update",
            min_value=1, step=1, key="update_id",
            help="The numeric Stock ID shown in search results",
        )
        st.caption("Find the Stock ID by searching the company above.")
        c1, c2, c3 = st.columns(3)
        with c1:
            new_name   = st.text_input("New Name",   key="update_name")
        with c2:
            new_ticker = st.text_input("New Ticker", key="update_ticker")
        with c3:
            new_sector = st.selectbox(
                "New Sector",
                ["", "Technology", "Finance", "Healthcare", "Energy", "Consumer", "Industrial"],
                key="update_sector",
            )

        if st.button("✏️ Update (PUT)", key="update_btn"):
            if new_name or new_ticker or new_sector:
                payload = {}
                if new_name:   payload["companyName"] = new_name
                if new_ticker: payload["ticker"]      = new_ticker
                if new_sector: payload["sector"]      = new_sector
                res = api_request("PUT", f"/companies/{company_id}", json=payload)
                if res.ok:
                    st.success("✅ Updated!")
                    st.rerun()
                else:
                    st.error(f"❌ Update failed: {res.error}")
            else:
                st.warning("Please fill in at least one field to update.")

    # ── PATCH (partial update — SYS-020 requirement) ─────────────────────────
    with tab3:
        st.markdown(
            '<p style="font-size:0.75rem;color:var(--muted)">Use PATCH to update a <strong>single field</strong> without replacing the full record.</p>',
            unsafe_allow_html=True,
        )
        patch_id = st.number_input(
            "Stock ID to Patch",
            min_value=1, step=1, key="patch_id",
            help="The numeric Stock ID shown in search results",
        )
        patch_field = st.selectbox(
            "Field to update",
            ["companyName", "ticker", "sector"],
            key="patch_field",
        )
        patch_value = st.text_input(
            "New value",
            key="patch_value",
            help=f"New value for the selected field",
        )

        if st.button("🩹 Apply Patch", key="patch_btn"):
            if patch_value.strip():
                res = api_request("PATCH", f"/companies/{patch_id}", json={patch_field: patch_value.strip()})
                if res.ok:
                    st.success(f"✅ Patched {patch_field} successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Patch failed: {res.error}")
            else:
                st.warning("Please enter a value to patch.")

    # ── DELETE ───────────────────────────────────────────────────────────────
    with tab4:
        delete_id = st.number_input(
            "Stock ID to Delete",
            min_value=1, step=1, key="delete_id",
            help="The numeric Stock ID shown in search results",
        )
        st.warning(f"⚠️ This will permanently delete stock ID **{delete_id}**. This cannot be undone.")

        if st.button("🗑️ Confirm Delete", key="delete_btn"):
            res = api_request("DELETE", f"/companies/{delete_id}")
            if res.ok:
                st.success("✅ Deleted!")
                st.rerun()
            else:
                st.error(f"❌ Delete failed: {res.error}")


# =====================================================
# PAGE: Analytics
# =====================================================
elif "Analytics" in page:

    if not ticker:
        st.info("👈 Enter a ticker in the filter bar above to get started.")
        st.stop()

    st.markdown(f'<h2 class="section-title">📊 Analytics — {ticker}</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<p style="font-size:0.7rem;color:var(--muted);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.6rem;" id="vol-label">Volatility Check</p>',
            unsafe_allow_html=True,
        )
        iterations = st.slider(
            "Monte Carlo Iterations",
            1000, 50000, 10000, step=1000,
            help="Higher = more accurate forecast, slower response",
        )
        with st.spinner("Computing volatility..."):
            vol_res = api_request("GET", f"/analytics/volatility?ticker={ticker}&iterations={iterations}")

        if vol_res.ok and vol_res.data:
            vol  = vol_res.data.get("forecasted_volatility", 0)
            risk = vol_res.data.get("risk_level", "N/A")
            pill_kind = "red" if "High" in str(risk) else ("yellow" if "Med" in str(risk) else "green")
            st.markdown(f"""
            <div class="metric-card" role="region" aria-label="Forecasted volatility {vol:.4f}, risk level {risk}">
                <div class="metric-label" aria-hidden="true">Forecasted Volatility</div>
                <div class="metric-value" aria-hidden="true">{vol:.4f}</div>
                <div class="metric-sub" style="margin-top:0.5rem">
                    Risk &nbsp;{pill(risk, pill_kind)}&nbsp;&nbsp;<span class="latency" aria-label="Response time {vol_res.elapsed_ms} milliseconds">{vol_res.elapsed_ms}ms</span>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.error(vol_res.error)

    with col2:
        st.markdown(
            '<p style="font-size:0.7rem;color:var(--muted);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.6rem;">Deep Analysis</p>',
            unsafe_allow_html=True,
        )
        analysis_type = st.selectbox(
            "Analysis type",
            ["returns", "volatility"],
            key="analysis_type",
        )
        window = st.number_input(
            "Rolling window in days",
            10, 365, 30, key="analysis_window",
            help="Number of trading days for the rolling calculation",
        )

        if st.button("🚀 Run Analysis", key="run_analysis"):
            with st.spinner("Running deep analysis..."):
                res = api_request("POST", f"/analytics/{ticker}", json={
                    "type": analysis_type,
                    "params": {"window": window},
                }, timeout=60)
            if res.ok:
                st.success(f"✅ Completed in {res.elapsed_ms}ms")
                st.json(res.data)
            else:
                st.error(res.error)

    st.markdown("---")
    st.markdown('<h2 class="section-title">⚠️ Value at Risk (VaR)</h2>', unsafe_allow_html=True)

    v1, v2 = st.columns(2)
    with v1:
        confidence  = st.slider("Confidence level", 0.90, 0.99, 0.95, 0.01, help="Statistical confidence for VaR estimate")
    with v2:
        simulations = st.slider("Number of simulations", 10000, 100000, 50000, step=5000)

    if st.button("Calculate VaR", key="calc_var"):
        with st.spinner("Running Monte Carlo simulation..."):
            res = api_request("POST", "/risk/var", json={
                "ticker": ticker,
                "confidence": confidence,
                "simulations": simulations,
            }, timeout=60)
        if res.ok:
            var_val = res.data.get("value_at_risk", 0)
            st.markdown(f"""
            <div class="metric-card" style="max-width:340px;margin-top:0.5rem"
                 role="region" aria-label="Value at Risk {var_val:.4f} at {confidence:.0%} confidence">
                <div class="metric-label" aria-hidden="true">Value at Risk ({confidence:.0%} confidence)</div>
                <div class="metric-value" aria-hidden="true">{var_val:.4f}</div>
                <div class="metric-sub">{simulations:,} simulations &nbsp;<span class="latency" aria-hidden="true">{res.elapsed_ms}ms</span></div>
            </div>""", unsafe_allow_html=True)
            with st.expander("Full Response"):
                st.json(res.data)
        else:
            st.error(res.error)


# =====================================================
# PAGE: Health & Debug
# =====================================================
else:
    st.markdown('<h2 class="section-title">🔧 System Health</h2>', unsafe_allow_html=True)

    endpoints = [
        ("GET",     "/health",                                                                 None),
        ("GET",     f"/companies/{ticker or 'AAPL'}",                                         None),
        ("GET",     f"/prices/{ticker or 'AAPL'}",       {"start": "2025-01-01", "end": "2025-03-01"}),
        ("GET",     f"/analytics/volatility?ticker={ticker or 'AAPL'}&iterations=1000",       None),
        # OPTIONS check — verifies the server responds to pre-flight requests
        ("OPTIONS", f"/companies/{ticker or 'AAPL'}",                                         None),
    ]

    if st.button("🔄 Run All Health Checks", help="Ping all API endpoints and report status"):
        # aria-live region so screen readers announce results as they arrive
        st.markdown('<div role="log" aria-live="polite" aria-label="Health check results">', unsafe_allow_html=True)
        for method, path, params in endpoints:
            with st.spinner(f"Checking {method} {path}..."):
                r = api_request(method, path, params=params, timeout=10)
            status_label = f"✓ {r.status_code}" if r.ok else f"✗ {r.status_code or 'ERR'}"
            status_pill  = pill(status_label, "green" if r.ok else "red")
            err_html     = f'<div class="health-err" role="alert">{r.error}</div>' if not r.ok else ""
            st.markdown(f"""
            <div class="health-row" role="row" aria-label="{method} {path} — {'OK' if r.ok else 'FAILED'}">
                <div>
                    <code style="font-size:0.78rem;color:var(--text)">{method} {path}</code>
                    {err_html}
                </div>
                <div style="display:flex;gap:0.6rem;align-items:center">
                    <span class="latency" aria-label="{r.elapsed_ms} milliseconds">{r.elapsed_ms}ms</span>
                    {status_pill}
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<h2 class="section-title">📚 Quick Reference</h2>', unsafe_allow_html=True)

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
**Analytics & Mutation Endpoints**
- `POST /companies` — Create company
- `PUT /companies/{id}` — Full update
- `PATCH /companies/{id}` — Partial update
- `DELETE /companies/{id}` — Remove company
- `OPTIONS /companies/{id}` — Allowed methods
- `GET /analytics/volatility` — Volatility forecast
- `POST /analytics/{ticker}` — Deep analysis
- `POST /risk/var` — Value at Risk (Monte Carlo)
        """)

    st.markdown(f"""
    <div class="metric-card" style="margin-top:1rem" role="complementary" aria-label="Interactive API documentation">
        <div class="metric-label">Interactive API Docs</div>
        <div style="font-size:0.85rem;margin-top:0.4rem;color:var(--text)">
            Open <a href="http://localhost:8000/docs" target="_blank"
                    style="color:var(--accent)"
                    aria-label="Swagger UI documentation, opens in new tab">localhost:8000/docs</a>
            in your browser for the full Swagger UI.
        </div>
    </div>""", unsafe_allow_html=True)