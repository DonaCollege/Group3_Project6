"""
Analytics API Routes

Architecture Overview:
- This module defines HTTP endpoints related to financial analytics.
- It represents the API (presentation) layer in a layered architecture.
- No heavy business logic is implemented directly in the routes.
- All computational work is delegated to the service layer.

Design Rationale:
- Endpoints in this file are intentionally designed to be CPU-intensive.
- These routes are primary targets for performance and load testing using JMeter.
- Query parameters are used to dynamically control computation intensity.

Team Notes:
- Service-layer logic may be optimized or replaced later without changing routes.
- Database-backed implementations will be introduced in the service layer.
"""

from fastapi import APIRouter
from schemas.analytics import AnalyticsRequest
from services.analytics_service import (
    run_cpu_heavy_analysis,
    compute_volatility
)

# Router for all analytics-related endpoints
# Prefix ensures logical grouping and RESTful structure
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/volatility",
    summary="Forecast volatility for a company",
    description=(
        "CPU-intensive endpoint designed for performance testing. "
        "Returns a simulated volatility metric based on the provided parameters. "
        "The 'iterations' parameter intentionally increases computational load "
        "to simulate real-world analytical workloads."
    )
)
def get_volatility(
    ticker: str,
    period: str = "1y",
    iterations: int = 10000
):
    """
    Architectural Notes:
    - This endpoint demonstrates a READ-only analytical operation (HTTP GET).
    - The computation is intentionally unoptimized in the initial version.
    - Used as a baseline endpoint for stress testing and performance comparison.
    - Future versions may replace in-memory computation with database aggregation.

    Performance Notes:
    - Increasing 'iterations' increases CPU utilization.
    - Designed to degrade predictably under load for JMeter analysis.
    """
    return compute_volatility(ticker, period, iterations)


@router.post(
    "/run",
    summary="Run heavy analytical computation",
    description=(
        "POST-based endpoint used to simulate long-running analytical jobs. "
        "Accepts parameters that control computational intensity and execution time. "
        "Primarily used for stress and load testing scenarios."
    )
)
def run_analysis(request: AnalyticsRequest):
    """
    Architectural Notes:
    - Demonstrates a WRITE/EXECUTE-style operation using HTTP POST.
    - Request body is validated using Pydantic schemas.
    - Endpoint exists to satisfy REST requirements and performance testing goals.

    Performance Notes:
    - Computation intensity is controlled via request payload.
    - Used by JMeter to simulate concurrent analytical workloads.
    - Serves as a baseline before performance optimizations are applied.
    """
    result = run_cpu_heavy_analysis(request.iterations)
    return {"result": result}
