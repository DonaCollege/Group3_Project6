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

##
# @file companies.py
# @brief Company-related REST endpoints.
#
# @details
# Provides search and retrieval functionality for stock/company data
# stored in the SQLite database. Supports GET operations for browsing
# company data and retrieving historical stock prices.
##
from fastapi import APIRouter, Query, HTTPException
from data.database import Database
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/companies", tags=["Companies"])
db = Database()

class CompanyCreate(BaseModel):
    companyName: str
    ticker: str
    sector: str

class CompanyUpdate(BaseModel):
    companyName: Optional[str] = None
    ticker: Optional[str] = None
    sector: Optional[str] = None

@router.get("/")
def search_companies(query: str = Query(default=""), limit: int = 20):
    ##
    # @brief Search companies by ticker or name.
    #
    # @param query Search string for filtering company names.
    # @param limit Maximum number of records to return.
    # @return JSON list of matching companies.
    ##
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
def create_company(payload: dict):  # <- Changed to dict, not Pydantic
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
    ##
    # @brief Update a stock record by its stockId.
    # Fixed: now does a real SELECT to check existence and a real UPDATE.
    ##
    conn = db.connect()
    cursor = conn.cursor()

    # Check the record actually exists by primary key
    cursor.execute("SELECT * FROM stocks WHERE stockId = ?", (stock_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Stock not found")

    # Build dynamic SET clause from whichever fields were provided
    fields = []
    values = []
    if update_data.companyName is not None:
        fields.append("companyName = ?")
        values.append(update_data.companyName)
    if update_data.ticker is not None:
        fields.append("companyName = ?")  # ticker is stored as companyName in this schema
        values.append(update_data.ticker)

    if not fields:
        conn.close()
        return {"message": "Nothing to update", "stockId": stock_id}

    values.append(stock_id)
    sql = f"UPDATE stocks SET {', '.join(fields)} WHERE stockId = ?"
    cursor.execute(sql, values)
    conn.commit()
    conn.close()

    return {"message": f"Stock {stock_id} updated successfully", "stockId": stock_id}


@router.delete("/{stock_id}")
def delete_company(stock_id: int):
    ##
    # @brief Delete a stock record by its stockId.
    # Fixed: now does a real DELETE from the database.
    ##
    conn = db.connect()
    cursor = conn.cursor()

    # Check it exists first
    cursor.execute("SELECT stockId FROM stocks WHERE stockId = ?", (stock_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Stock not found")

    cursor.execute("DELETE FROM stocks WHERE stockId = ?", (stock_id,))
    conn.commit()
    conn.close()

    return {"message": f"Stock {stock_id} deleted successfully"}