import os
from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    # Check if the data directory/database exists
    db_path = "./data/finance.db" 
    db_status = os.path.exists(db_path)
    
    return {
        "status": "API running",
        "database_connected": db_status,
        "environment": "Docker" if os.getenv("PYTHONPATH") else "Local"
    }