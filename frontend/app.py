import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests
import pandas as pd
import streamlit as st

# quick config
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(
    page_title="Financial Analytics UI",
    page_icon="📈",
    layout="wide",
)


# small helpers
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

        # backend gave us something, but not a success
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



# sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Browse Data", "Run Analytics", "Health / Debug"])

st.sidebar.divider()
st.sidebar.subheader("Common filters")
ticker = st.sidebar.text_input("Ticker (e.g., AAPL)", value="").strip().upper()
start_date = st.sidebar.date_input("Start date")
end_date = st.sidebar.date_input("End date")

if start_date > end_date:
    st.sidebar.error("Heads up: start date needs to be before the end date.")


#Page: Browse data
if page == "Browse Data":
    header_with_meta("Browse Data", "Look up companies and view their price history.")

    query = st.text_input("Search companies (ticker or name)", value="").strip()

    left, right = st.columns([1, 2], vertical_alignment="bottom")
    with left:
        do_search = st.button("Search", type="primary", disabled=(len(query) == 0))
    with right:
        st.caption("Tip: search by ticker (AAPL) or partial company name.")

    if do_search:
        res = api_request("GET", "/companies", params={"query": query})
        if res.ok and res.data is not None:
            items = res.data.get("items", res.data)  # flexible: list or wrapped list
            st.success(f"Found results in {res.elapsed_ms} ms (status {res.status_code})")

            df = pd.DataFrame(items)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.error(f"That didn’t work. Took {res.elapsed_ms} ms. {res.error}")

    st.divider()
    st.subheader("Company details")

    if not ticker:
        st.info("Type a ticker on the left so we know what to load.")
        st.stop()

    details = api_request("GET", f"/companies/{ticker}")
    if details.ok and details.data is not None:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Ticker", details.data.get("ticker", ticker))
        with c2:
            st.metric("Name", details.data.get("name", "—"))
        with c3:
            st.metric("Sector", details.data.get("sector", "—"))

        st.caption(f"Loaded in {details.elapsed_ms} ms (status {details.status_code})")
        st.json(details.data, expanded=False)
    else:
        st.error(f"Couldn’t load company details. {details.error}")
        st.stop()

    st.divider()
    st.subheader("Price history")

    prices = api_request(
        "GET",
        f"/prices/{ticker}",
        params={"start": str(start_date), "end": str(end_date)},
    )

    if prices.ok and prices.data is not None:
        rows = prices.data.get("rows", prices.data)
        dfp = pd.DataFrame(rows)

        st.caption(f"Loaded in {prices.elapsed_ms} ms (status {prices.status_code})")
        st.dataframe(dfp, use_container_width=True, hide_index=True)

        # keep chart simple and cheap
        if "date" in dfp.columns and "close" in dfp.columns:
            dfp["date"] = pd.to_datetime(dfp["date"], errors="coerce")
            dfp = dfp.dropna(subset=["date"]).sort_values("date")
            st.line_chart(dfp.set_index("date")["close"])
        else:
            st.caption("No date/close columns found for a chart, so showing the table only.")
    else:
        st.error(f"Couldn’t load price data. {prices.error}")


#Page: Run analytics
elif page == "Run Analytics":
    header_with_meta("Run Analytics", "Trigger server-side analytics and show the results.")

    if not ticker:
        st.info("Pick a ticker on the left first so we know what to analyze.")
        st.stop()

    if start_date > end_date:
        st.error("Fix the date range in the sidebar first.")
        st.stop()

    left, right = st.columns([1, 1])

    with left:
        st.subheader("What do you want to run?")
        analysis_type = st.selectbox(
            "Analysis type",
            ["returns", "volatility", "moving_average", "correlation"],
            help="The server does the actual computation. The UI just sends inputs.",
        )

        window = st.number_input("Window (days)", min_value=2, max_value=365, value=30)
        include_benchmark = st.checkbox("Include benchmark comparison", value=False)

        payload = {
            "type": analysis_type,
            "start": str(start_date),
            "end": str(end_date),
            "params": {
                "window": int(window),
                "include_benchmark": include_benchmark,
            },
        }

        run = st.button("Run analysis", type="primary")

    with right:
        st.subheader("What we’re sending to the API")
        st.json(payload, expanded=False)

    if run:
        with st.spinner("Crunching numbers on the server... hang tight"):
            res = api_request("POST", f"/analytics/{ticker}", json=payload, timeout=30)

        if res.ok and res.data is not None:
            st.success(f"Finished in {res.elapsed_ms} ms (status {res.status_code})")

            st.subheader("Results")

            summary = res.data.get("summary")
            rows = res.data.get("rows")
            series = res.data.get("series")

            if summary:
                st.write("**Summary**")
                st.json(summary, expanded=False)

            if rows:
                dfr = pd.DataFrame(rows)
                st.dataframe(dfr, use_container_width=True, hide_index=True)

            if series:
                dfs = pd.DataFrame(series)

                if "date" in dfs.columns and "value" in dfs.columns:
                    dfs["date"] = pd.to_datetime(dfs["date"], errors="coerce")
                    dfs = dfs.dropna(subset=["date"]).sort_values("date")
                    st.line_chart(dfs.set_index("date")["value"])
                else:
                    st.write("**Series**")
                    st.dataframe(dfs, use_container_width=True, hide_index=True)

            if not any([summary, rows, series]):
                st.caption("No structured result fields found, so here’s the raw response:")
                st.json(res.data, expanded=False)

        else:
            st.error(f"Analysis failed. {res.error}")

#Page: Health check
else:
    header_with_meta("Health / Debug", "Quick checks to make sure the backend is reachable.")

    if st.button("Check /health", type="primary"):
        res = api_request("GET", "/health", timeout=10)

        if res.ok:
            st.success(f"Server looks good. Responded in {res.elapsed_ms} ms (status {res.status_code})")
            st.json(res.data or {}, expanded=False)
        else:
            st.error(f"Server didn’t respond properly. {res.error}")

    st.divider()
    st.subheader("Notes for load testing")
    st.markdown(
        """
        """.strip()
    )
