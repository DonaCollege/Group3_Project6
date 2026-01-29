"""
Company API Routes

Architecture Overview:
- This module defines RESTful endpoints for managing company-related data.
- It demonstrates the full CRUD lifecycle using standard HTTP verbs.
- Routes in this file represent the API (presentation) layer only.

Design Rationale:
- The API surface is intentionally simple and stable.
- Business logic and database access are abstracted away from routes.
- Current implementation uses an in-memory placeholder store.
- Database-backed logic will be integrated later via the service layer.

Performance & Testing Notes:
- Includes both lightweight and heavy endpoints.
- Lightweight routes provide baseline performance metrics.
- Heavy payload routes are used to stress network and memory during load testing.

Team Notes:
- Database schema and query logic will be implemented by Nikhil.
- Endpoint behavior should not be modified without coordinating API changes.
"""

from fastapi import APIRouter
from schemas.company import CompanyCreate, CompanyUpdate

# Router for company-related endpoints
# Prefix ensures consistent RESTful structure
router = APIRouter(prefix="/companies", tags=["Companies"])


# Temporary in-memory data store
# Used only as a placeholder until database integration is complete
fake_db = []


@router.get(
    "",
    summary="Retrieve companies",
    description=(
        "Lightweight GET endpoint that returns a list of companies. "
        "Used as a baseline endpoint for performance comparison during load testing."
    )
)
def get_companies(limit: int = 10, sort: str = "name"):
    """
    Architectural Notes:
    - Demonstrates a READ operation using HTTP GET.
    - Designed to be fast and low-cost.
    - Serves as a control endpoint when comparing performance against heavier routes.

    Performance Notes:
    - Minimal processing to establish baseline response time.
    """
    return fake_db[:limit]


@router.post(
    "",
    summary="Create a new company",
    description=(
        "Creates a new company record using a JSON payload. "
        "Demonstrates POST semantics and request validation."
    )
)
def create_company(company: CompanyCreate):
    """
    Architectural Notes:
    - Demonstrates a CREATE operation using HTTP POST.
    - Uses Pydantic schema validation.
    - Database persistence will be added later via service layer.
    """
    fake_db.append(company)
    return {"message": "Company created", "company": company}


@router.put(
    "/{company_id}",
    summary="Update company details",
    description=(
        "Updates an existing company resource. "
        "Demonstrates full replacement semantics using HTTP PUT."
    )
)
def update_company(company_id: int, company: CompanyUpdate):
    """
    Architectural Notes:
    - Demonstrates a full UPDATE operation.
    - Resource is identified via URL path parameter.
    - Current implementation is a placeholder for database-backed logic.
    """
    return {
        "message": "Company updated",
        "company_id": company_id,
        "data": company
    }


@router.patch(
    "/{company_id}/status",
    summary="Update company status",
    description=(
        "Partially updates a company resource. "
        "Demonstrates PATCH semantics for targeted updates."
    )
)
def patch_company_status(company_id: int, status: str):
    """
    Architectural Notes:
    - Demonstrates a PARTIAL UPDATE using HTTP PATCH.
    - Used to satisfy REST requirements and illustrate resource mutation patterns.
    """
    return {
        "message": "Status updated",
        "company_id": company_id,
        "status": status
    }


@router.delete(
    "/{company_id}",
    summary="Delete company",
    description=(
        "Deletes a company resource. "
        "Demonstrates DELETE semantics in RESTful design."
    )
)
def delete_company(company_id: int):
    """
    Architectural Notes:
    - Demonstrates a DELETE operation.
    - Exists primarily to satisfy REST verb coverage requirements.
    """
    return {"message": "Company deleted", "company_id": company_id}


@router.get(
    "/{company_id}/logo",
    summary="Retrieve company logo (large payload)",
    description=(
        "Returns a large payload to intentionally stress network bandwidth "
        "and memory usage during load testing."
    )
)
def get_company_logo(size_kb: int = 500):
    """
    Architectural Notes:
    - This endpoint intentionally returns a large response body.
    - Used to simulate transferring images or binary assets.
    - Payload size is configurable via query parameter.

    Performance Notes:
    - Increasing 'size_kb' increases response size and memory usage.
    - Primary endpoint for network-level stress testing in JMeter.
    """
    payload = "A" * (size_kb * 1024)
    return {"logo": payload}
