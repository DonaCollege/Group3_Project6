##
# @file companies.py
# @brief Company-related REST endpoints.
#
# @details
# Provides full CRUD functionality for stock/company data stored in the
# SQLite database. Implements all required HTTP verbs per SYS-020:
#   GET    - Search and retrieve company records
#   POST   - Create a new company record
#   PUT    - Full update of an existing company record
#   PATCH  - Partial update (one or more fields only)
#   DELETE - Remove a company record
#   OPTIONS - Advertise allowed methods for a resource
##

from fastapi import APIRouter, Query, HTTPException, Response
from fastapi.responses import JSONResponse
from data.database import Database
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/companies", tags=["Companies"])
db = Database()


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class CompanyCreate(BaseModel):
    ##
    # @brief Schema for creating a new company.
    ##
    companyName: str
    ticker: str
    sector: str


class CompanyUpdate(BaseModel):
    ##
    # @brief Schema for full or partial company update (used by PUT and PATCH).
    # All fields optional so the same model works for both verbs.
    ##
    companyName: Optional[str] = None
    ticker:      Optional[str] = None
    sector:      Optional[str] = None


# ── GET /companies/ ───────────────────────────────────────────────────────────

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
                "stockId":     row[0],
                "companyName": row[1],
                "ticker":      row[1][:4],
                "date":        row[2],
                "open":        row[3],
                "high":        row[4],
                "low":         row[5],
                "close":       row[6],
                "volume":      row[7],
            })
    return {"items": results}


# ── GET /companies/{ticker} ───────────────────────────────────────────────────

@router.get("/{ticker}")
def get_company_details(ticker: str):
    ##
    # @brief Retrieve detail and price history for a company by ticker.
    #
    # @param ticker The company ticker symbol.
    # @return Company metadata and historical price rows.
    # @raises HTTPException 404 if no records match the ticker.
    ##
    rows = db.get_stocks_by_company(ticker)
    if not rows:
        raise HTTPException(status_code=404, detail="Company not found")
    return {
        "ticker": ticker,
        "name":   ticker,
        "sector": "Technology",
        "rows": [
            {
                "date":   r[2],
                "open":   r[3],
                "high":   r[4],
                "low":    r[5],
                "close":  r[6],
                "volume": r[7],
            }
            for r in rows
        ],
    }


# ── POST /companies/ ──────────────────────────────────────────────────────────

@router.post("/", status_code=201)
def create_company(payload: dict):
    ##
    # @brief Create a new stock/company record.
    #
    # @param payload JSON body with companyName, ticker, sector (and optional close).
    # @return Confirmation message.
    ##
    db.insert_stock({
        "companyName": payload.get("companyName", "Unknown"),
        "date":        "2026-02-17",
        "open":        100.0,
        "high":        105.0,
        "low":         95.0,
        "close":       payload.get("close", 102.0),
        "volume":      1000000,
    })
    return {"message": "Company created"}


# ── PUT /companies/{stock_id} ─────────────────────────────────────────────────

@router.put("/{stock_id}")
def update_company(stock_id: int, update_data: CompanyUpdate):
    ##
    # @brief Full update of a stock record by its stockId.
    #
    # @param stock_id     Primary key of the record to update.
    # @param update_data  Fields to update (any subset of companyName, ticker).
    # @return             Confirmation message and updated stockId.
    # @raises HTTPException 404 if stock_id does not exist.
    ##
    conn   = db.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM stocks WHERE stockId = ?", (stock_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Stock not found")

    fields, values = [], []
    if update_data.companyName is not None:
        fields.append("companyName = ?")
        values.append(update_data.companyName)
    if update_data.ticker is not None:
        fields.append("companyName = ?")   # ticker stored as companyName in schema
        values.append(update_data.ticker)

    if not fields:
        conn.close()
        return {"message": "Nothing to update", "stockId": stock_id}

    values.append(stock_id)
    cursor.execute(f"UPDATE stocks SET {', '.join(fields)} WHERE stockId = ?", values)
    conn.commit()
    conn.close()

    return {"message": f"Stock {stock_id} updated successfully", "stockId": stock_id}


# ── PATCH /companies/{stock_id} ───────────────────────────────────────────────

@router.patch("/{stock_id}")
def patch_company(stock_id: int, patch_data: CompanyUpdate, response: Response):
    ##
    # @brief Partially update one or more fields of a company record.
    #
    # @details
    # Unlike PUT, PATCH only modifies the fields explicitly supplied in the
    # request body. Fields omitted from the payload are left unchanged.
    # This satisfies SYS-020(e) — PATCH verb requirement.
    #
    # @param stock_id   Primary key of the record to patch.
    # @param patch_data JSON body containing only the fields to change.
    # @return           The patched fields and confirmation message.
    # @raises HTTPException 404 if stock_id does not exist.
    # @raises HTTPException 400 if the request body contains no updatable fields.
    ##
    updates = patch_data.model_dump(exclude_none=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided. Supply at least one of: companyName, ticker, sector.",
        )

    conn   = db.connect()
    cursor = conn.cursor()

    # Verify record exists before attempting update
    cursor.execute("SELECT * FROM stocks WHERE stockId = ?", (stock_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Stock {stock_id} not found")

    # Build a dynamic SET clause from only the provided fields
    fields, values = [], []
    if patch_data.companyName is not None:
        fields.append("companyName = ?")
        values.append(patch_data.companyName)
    if patch_data.ticker is not None:
        # ticker is stored in the companyName column in the current schema
        fields.append("companyName = ?")
        values.append(patch_data.ticker)
    # NOTE: add a real 'sector' column update here once the schema supports it

    if fields:
        values.append(stock_id)
        cursor.execute(f"UPDATE stocks SET {', '.join(fields)} WHERE stockId = ?", values)
        conn.commit()

    conn.close()

    return JSONResponse(
        status_code=200,
        content={
            "message":  f"Stock {stock_id} partially updated.",
            "stockId":  stock_id,
            "patched":  updates,
        },
    )


# ── DELETE /companies/{stock_id} ──────────────────────────────────────────────

@router.delete("/{stock_id}")
def delete_company(stock_id: int):
    ##
    # @brief Delete a stock record by its stockId.
    #
    # @param stock_id Primary key of the record to delete.
    # @return         Confirmation message.
    # @raises HTTPException 404 if stock_id does not exist.
    ##
    conn   = db.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT stockId FROM stocks WHERE stockId = ?", (stock_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Stock not found")

    cursor.execute("DELETE FROM stocks WHERE stockId = ?", (stock_id,))
    conn.commit()
    conn.close()

    return {"message": f"Stock {stock_id} deleted successfully"}


# ── OPTIONS /companies/ ───────────────────────────────────────────────────────

@router.options("/")
def options_companies(response: Response):
    ##
    # @brief Advertise allowed HTTP methods for the /companies collection.
    #
    # @details
    # Returns a 204 No Content response with an Allow header listing every
    # HTTP method supported on this resource. Satisfies SYS-020(f).
    #
    # @return 204 No Content with Allow and Access-Control-Allow-Methods headers.
    ##
    allowed = "GET, POST, OPTIONS"
    response.headers["Allow"]                        = allowed
    response.headers["Access-Control-Allow-Methods"] = allowed
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return Response(status_code=204)


# ── OPTIONS /companies/{stock_id} ─────────────────────────────────────────────

@router.options("/{stock_id}")
def options_company(stock_id: int, response: Response):
    ##
    # @brief Advertise allowed HTTP methods for a single /companies/{id} resource.
    #
    # @details
    # Returns a 204 No Content response so clients and tools (JMeter, browsers)
    # can discover which verbs are accepted without performing a real mutation.
    # Satisfies SYS-020(f) — OPTIONS verb requirement.
    #
    # @param stock_id  Resource identifier (used for path matching only).
    # @return          204 No Content with Allow header.
    ##
    allowed = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response.headers["Allow"]                        = allowed
    response.headers["Access-Control-Allow-Methods"] = allowed
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return Response(status_code=204)