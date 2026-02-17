

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
