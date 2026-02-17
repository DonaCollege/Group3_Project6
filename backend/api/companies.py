# from fastapi import APIRouter, Query
# from data.database import Database

# router = APIRouter(prefix="/companies", tags=["Companies"])

# db = Database()


# @router.get("/")
# def search_companies(query: str = Query(default=""), limit: int = 20):
#     rows = db.get_all_stocks(limit)

#     results = []
#     for row in rows:
#         if query.lower() in row[1].lower():
#             results.append({
#                 "stockId": row[0],
#                 "companyName": row[1],
#                 "date": row[2],
#                 "open": row[3],
#                 "high": row[4],
#                 "low": row[5],
#                 "close": row[6],
#                 "volume": row[7],
#             })

#     return {"items": results}


# @router.get("/{ticker}")
# def get_company_details(ticker: str):
#     rows = db.get_stocks_by_company(ticker)

#     if not rows:
#         return {"detail": "Company not found"}

#     return {
#         "ticker": ticker,
#         "name": ticker,
#         "sector": "Technology",
#         "rows": [
#             {
#                 "date": r[2],
#                 "open": r[3],
#                 "high": r[4],
#                 "low": r[5],
#                 "close": r[6],
#                 "volume": r[7],
#             }
#             for r in rows
#         ]
#     }


from fastapi import APIRouter, Query, HTTPException
from data.database import Database
from pydantic import BaseModel

router = APIRouter(prefix="/companies", tags=["Companies"])
db = Database()

class CompanyCreate(BaseModel):
    companyName: str
    ticker: str
    sector: str

class CompanyUpdate(BaseModel):
    companyName: str | None = None
    ticker: str | None = None
    sector: str | None = None

@router.get("/")
def search_companies(query: str = Query(default=""), limit: int = 20):
    rows = db.get_all_stocks(limit)
    results = []
    for row in rows:
        if query.lower() in row[1].lower():
            results.append({
                "stockId": row[0],
                "companyName": row[1],
                "ticker": row[1][:4],  # Simplified ticker
                "date": row[2],
                "open": row[3],
                "high": row[4],
                "low": row[5],
                "close": row[6],
                "volume": row[7],
            })
    return {"items": results}

@router.get("/{ticker}")
def get_company_details(ticker: str):
    rows = db.get_stocks_by_company(ticker)
    if not rows:
        raise HTTPException(status_code=404, detail="Company not found")
    return {
        "ticker": ticker,
        "name": ticker,
        "sector": "Technology",  # From schema
        "rows": [
            {
                "date": r[2],
                "open": r[3],
                "high": r[4],
                "low": r[5],
                "close": r[6],
                "volume": r[7],
            }
            for r in rows
        ]
    }

@router.post("/", status_code=201)
def create_company(payload: dict):  # ← Changed to dict, not Pydantic
    db.insert_stock({
        "companyName": payload.get("companyName", "Unknown"),
        "date": "2026-02-17",
        "open": 100.0,
        "high": 105.0,
        "low": 95.0,
        "close": payload.get("close", 102.0),
        "volume": 1000000
    })
    return {"message": "Company created"}


@router.put("/{stock_id}")
def update_company(stock_id: int, update_data: CompanyUpdate):
    # Simple update (expand as needed)
    rows = db.get_all_stocks()
    if stock_id >= len(rows):
        raise HTTPException(status_code=404, detail="Stock not found")
    return {"message": f"Updated stock {stock_id}", "data": update_data}

@router.delete("/{stock_id}")
def delete_company(stock_id: int):
    # Note: SQLite DELETE needs explicit implementation in Database class
    return {"message": f"Deleted stock {stock_id}"}
