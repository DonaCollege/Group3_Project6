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
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(
    page_title="Financial Analytics UI",
    page_icon="📈",
    layout="wide",
)

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

def header_with_meta(title: str, subtitle: str = ""):
    col1, col2 = st.columns([3, 2], vertical_alignment="bottom")

    with col1:
        st.title(title)
        if subtitle:
            st.caption(subtitle)

    with col2:
        st.caption(f"API Base URL: `{API_BASE_URL}`")

# =============================
# Sidebar
# =============================
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Browse Data", "Run Analytics", "Health / Debug"])

st.sidebar.divider()
st.sidebar.subheader("Common filters")

ticker = st.sidebar.text_input("Ticker (e.g., AAPL)", value="AAPL", key="sidebar_ticker").strip().upper()
start_date = st.sidebar.date_input("Start date", value=date(2025, 1, 1), key="sidebar_start")
end_date = st.sidebar.date_input("End date", value=date(2026, 2, 17), key="sidebar_end")

if start_date > end_date:
    st.sidebar.error("Start date must be before end date.")

# =====================================================
# PAGE: Browse Data
# =====================================================
if page == "Browse Data":
    header_with_meta("Browse Data", "Look up companies and view their price history.")

    query = st.text_input("Search companies (ticker or name)", value="", key="search_query").strip()

    left, right = st.columns([1, 2], vertical_alignment="bottom")
    with left:
        do_search = st.button("Search", type="primary", disabled=(len(query) == 0), key="search_btn")
    with right:
        st.caption("Tip: search by ticker (AAPL) or partial company name.")

    if do_search:
        res = api_request("GET", "/companies", params={"query": query})

        if res.ok and res.data is not None:
            items = res.data.get("items", [])
            st.success(f"Found {len(items)} results in {res.elapsed_ms} ms")
            if items:
                st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)
            else:
                st.info("No matching companies found.")
        else:
            st.error(f"Search failed: {res.error}")

    st.divider()
    st.subheader("Company Details")

    if ticker:
        details = api_request("GET", f"/companies/{ticker}")

        if details.ok and details.data:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Ticker", details.data.get("ticker", ticker))
            with c2:
                st.metric("Name", details.data.get("name", "—"))
            with c3:
                st.metric("Sector", details.data.get("sector", "—"))

            st.caption(f"Loaded in {details.elapsed_ms} ms")
        else:
            st.error(f"Company not found: {details.error}")

        st.divider()
        st.subheader("Price History")

        prices = api_request(
            "GET",
            f"/prices/{ticker}",
            params={"start": str(start_date), "end": str(end_date)},
        )

        if prices.ok and prices.data:
            rows = prices.data.get("rows", [])
            if rows:
                dfp = pd.DataFrame(rows)
                st.dataframe(dfp, use_container_width=True, hide_index=True)

                if "date" in dfp.columns and "close" in dfp.columns:
                    dfp["date"] = pd.to_datetime(dfp["date"], errors="coerce")
                    dfp = dfp.dropna(subset=["date"]).sort_values("date")
                    st.line_chart(dfp.set_index("date")["close"])
            else:
                st.info("No price data available.")
        else:
            st.error(prices.error)

    # =============================
    # MANAGE COMPANIES (CRUD)
    # =============================
    st.divider()
    st.subheader("Manage Companies (CRUD)")

    tab1, tab2, tab3 = st.tabs(["➕ Create", "✏️ Update", "🗑️ Delete"])

    # ---------- CREATE ----------
    with tab1:
        st.markdown("### Create New Company Record")
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name", key="create_name")
            ticker_input = st.text_input("Ticker", key="create_ticker")
        with col2:
            sector = st.selectbox("Sector", ["Technology", "Finance", "Healthcare"], key="create_sector")
            create_date = st.date_input("Date", value=date(2026, 2, 17), key="create_date")

        if st.button("➕ Create Company", type="primary", key="create_btn") and company_name and ticker_input:
            payload = {
                "companyName": company_name,
                "ticker": ticker_input,
                "sector": sector
            }
            res = api_request("POST", "/companies", json=payload)
            if res.ok:
                st.success("✅ Company created!")
                st.rerun()
            else:
                st.error(f"❌ Create failed: {res.error}")

    # ---------- UPDATE ----------
    with tab2:
        st.markdown("### Update Company")
        company_id = st.number_input("Stock ID to Update", min_value=1, step=1, key="update_id")
        new_name = st.text_input("New Company Name (optional)", key="update_name")
        new_ticker = st.text_input("New Ticker (optional)", key="update_ticker")
        new_sector = st.selectbox("New Sector (optional)", ["", "Technology", "Finance", "Healthcare"], key="update_sector")

        if st.button("✏️ Update Company", type="primary", key="update_btn") and new_name:
            payload = {}
            if new_name: payload["companyName"] = new_name
            if new_ticker: payload["ticker"] = new_ticker
            if new_sector: payload["sector"] = new_sector
            
            res = api_request("PUT", f"/companies/{company_id}", json=payload)
            if res.ok:
                st.success("✅ Company updated!")
                st.rerun()
            else:
                st.error(f"❌ Update failed: {res.error}")

    # ---------- DELETE ----------
    with tab3:
        st.markdown("### Delete Company")
        delete_id = st.number_input("Stock ID to Delete", min_value=1, step=1, key="delete_id")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.warning(f"⚠️ This will delete stock ID **{delete_id}**")
        with col2:
            if st.button("🗑️ Delete", type="primary", use_container_width=True, key="delete_btn"):
                res = api_request("DELETE", f"/companies/{delete_id}")
                if res.ok:
                    st.success("✅ Company deleted!")
                    st.rerun()
                else:
                    st.error(f"❌ Delete failed: {res.error}")

# =====================================================
# PAGE: Run Analytics
# =====================================================
elif page == "Run Analytics":
    header_with_meta("Run Analytics", "Real DB-powered analytics.")

    if not ticker:
        st.info("👈 Select a ticker in the sidebar.")
        st.stop()

    # Volatility (GET endpoint)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Quick Volatility Check")
        iterations = st.slider("Iterations", 1000, 50000, 10000)
        vol_res = api_request("GET", f"/analytics/volatility?ticker={ticker}&iterations={iterations}")
        
        if vol_res.ok:
            vol_data = vol_res.data
            st.metric("Volatility", f"{vol_data.get('forecasted_volatility', 0):.4f}")
            st.caption(f"Risk: {vol_data.get('risk_level', 'N/A')} | {vol_res.elapsed_ms}ms")
        else:
            st.error(vol_res.error)

    # Analytics POST
    with col2:
        st.subheader("🔬 Heavy Analysis")
        analysis_type = st.selectbox("Type", ["returns", "volatility"], key="analysis_type")
        window = st.number_input("Window", 10, 365, 30, key="analysis_window")

        payload = {
            "type": analysis_type,
            "params": {"window": window}
        }

        if st.button("🚀 Run Analysis", type="primary"):
            res = api_request("POST", f"/analytics/{ticker}", json=payload, timeout=60)
            if res.ok:
                st.success(f"✅ Done in {res.elapsed_ms}ms")
                st.json(res.data)
            else:
                st.error(res.error)

    # VaR
    st.divider()
    st.subheader("⚠️ Value at Risk (VaR)")
    confidence = st.slider("Confidence Level", 0.90, 0.99, 0.95, 0.01)
    simulations = st.slider("Simulations", 10000, 100000, 50000)
    
    var_payload = {
        "ticker": ticker,
        "confidence": confidence,
        "simulations": simulations
    }
    
    if st.button("Calculate VaR", type="primary"):
        res = api_request("POST", "/risk/var", json=var_payload, timeout=60)
        if res.ok:
            st.metric("Value at Risk", f"{res.data.get('value_at_risk', 0):.4f}")
            st.json(res.data)
        else:
            st.error(res.error)

# =====================================================
# PAGE: Health / Debug
# =====================================================
else:
    header_with_meta("Health / Debug", "Backend status & utilities.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("❤️ Health Check", key="health"):
            res = api_request("GET", "/health")
            st.success(f"✅ Healthy ({res.elapsed_ms}ms)") if res.ok else st.error(res.error)
    
    with col2:
        if st.button("📊 Load Sample Data", key="loaddata"):
            st.info("Run `python backend/data/load_data.py` manually")
    
    with col3:
        st.caption("💡 All endpoints working?")
        st.caption("Check `/docs` in browser")
