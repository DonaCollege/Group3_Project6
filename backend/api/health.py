"""
Health Check API Routes

Architecture Overview:
- This module defines a lightweight health check endpoint.
- It serves as the simplest entry point into the system.
- Represents the most minimal path through the HTTP stack.

Design Rationale:
- Used to verify server availability and responsiveness.
- Provides a baseline endpoint for performance comparison.
- Acts as a control endpoint during load and stress testing.

Performance & Testing Notes:
- Intentionally minimal logic and payload.
- Expected to have the lowest response time under load.
- Used by JMeter to establish baseline latency and throughput.

Team Notes:
- This endpoint should remain lightweight and unchanged.
- No database or service layer dependencies by design.
"""

from fastapi import APIRouter

# Router for health and status-related endpoints
router = APIRouter(tags=["Health"])


@router.get(
    "/",
    summary="Health check",
    description=(
        "Lightweight endpoint used to verify that the API is running. "
        "Serves as a baseline reference for performance and availability testing."
    )
)
def health_check():
    """
    Architectural Notes:
    - Demonstrates a minimal HTTP GET request.
    - Used as a reference point when analyzing system performance.
    - Exists independently of business logic and data access layers.
    """
    return {"status": "API running"}
