"""
@file main.py
@brief Main FastAPI application entry point

Central application router that mounts all API modules (health, companies, analytics, 
risk, prices). Provides OpenAPI/Swagger documentation and health monitoring for 
performance testing baseline (SYS-010, SV-FR-010).

@see SDD Section 3 - API Backend Services Module
@author Group 3 - CSCN73060
@version 1.0
@date 2026
"""

from fastapi import FastAPI
from backend.api import health, companies, analytics, risk, prices


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
app.include_router(prices.router)
