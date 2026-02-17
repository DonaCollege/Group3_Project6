"""
Risk Analysis API Routes

Architecture Overview:
- This module defines endpoints related to financial risk analysis.
- It represents the API (presentation) layer for risk computations.
- Routes in this file delegate all heavy logic to the service layer.

Design Rationale:
- Risk calculations are computationally expensive by nature.
- This endpoint is designed to simulate real-world financial risk workloads.
- The API surface is kept stable while internal logic evolves.

Performance & Testing Notes:
- This endpoint is intentionally designed to be heavy under load.
- Computational complexity is controlled via request parameters.
- Used as a primary target for JMeter performance and stress testing.

Team Notes:
- API routes are owned and maintained by Dona.
- Database-backed aggregation and optimization will be implemented later.
- Route signatures should not be modified without team coordination.
"""

from fastapi import APIRouter
from backend.schemas.risk import VaRRequest
from backend.services.risk_service import calculate_var

# Router for all risk-related endpoints
# Grobackenups risk analytics under a clear RESTful namespace
router = APIRouter(prefix="/risk", tags=["Risk"])


@router.post(
    "/var",
    summary="Calculate Value at Risk (VaR)",
    description=(
        "Calculates Value at Risk (VaR) for a given financial instrument. "
        "This endpoint simulates heavy analytical computation and will later "
        "incorporate database-driven aggregation and optimization."
    )
)
def get_var(request: VaRRequest):
    """
    Architectural Notes:
    - Demonstrates a compute-intensive analytical operation using HTTP POST.
    - Uses request body validation via Pydantic schemas.
    - Abstracts all business logic into the service layer.

    Performance Notes:
    - Designed to scale computational cost with input parameters.
    - Used by JMeter to evaluate system behavior under concurrent load.
    - Serves as a baseline before performance optimizations are applied.

    Future Integration:
    - Will aggregate historical price data from the database.
    - Will support optimized queries and caching strategies.
    """
    return calculate_var(request)
