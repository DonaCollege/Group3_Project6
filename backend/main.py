"""
Main Application Entry Point

Architecture Overview:
- This file defines the root FastAPI application.
- Acts as the HTTP boundary for the entire system.
- No business logic is implemented in this module.

Design Principles:
- Follows RESTful API design principles.
- Uses a modular router-based structure for scalability.
- Separates HTTP concerns from business logic and data access.

System Structure:
- API Layer: Handles HTTP requests and responses (api/*)
- Service Layer: Contains computational and business logic (services/*)
- Data Layer: Database integration (implemented separately)

Performance & Testing Focus:
- Designed specifically to support load and stress testing.
- Routes are intentionally unoptimized in the initial version.
- Used as the baseline system for JMeter performance analysis.

Team Notes:
- This file is owned and maintained by Dona.
- New features should be added via routers, not directly here.
- Changes to routing should be coordinated across the team.
"""

from fastapi import FastAPI
from api import health, companies, analytics, risk

# Create the FastAPI application instance
# Metadata is used for OpenAPI documentation and demo purposes
app = FastAPI(
    title="Financial Performance & Risk API",
    description="API designed for load, stress, and performance testing",
    version="1.0"
)

# Register feature-specific routers
# Each router represents a bounded functional area of the system
app.include_router(health.router)
app.include_router(companies.router)
app.include_router(analytics.router)
app.include_router(risk.router)
