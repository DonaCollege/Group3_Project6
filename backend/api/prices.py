# from fastapi import APIRouter
# from data.database import Database

# router = APIRouter(prefix="/prices", tags=["Prices"])

# db = Database()

# @router.get("/{ticker}")
# def get_prices(ticker: str, start: str = None, end: str = None):
#     rows = db.get_stocks_by_company(ticker)

#     data = [
#         {
#             "date": r[2],
#             "close": r[6],
#         }
#         for r in rows
#     ]

#     return {"rows": data}


from fastapi import APIRouter
from data.database import Database

router = APIRouter(prefix="/prices", tags=["Prices"])
db = Database()

@router.get("/{ticker}")
def get_prices(ticker: str, start: str = None, end: str = None):
    rows = db.get_stocks_by_company(ticker)
    data = [
        {
            "date": r[2],
            "close": r[6],
        }
        for r in rows
        if (not start or r[2] >= start) and (not end or r[2] <= end)
    ]
    return {"rows": data}
