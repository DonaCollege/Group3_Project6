from pydantic import BaseModel

class CompanyCreate(BaseModel):
    name: str
    ticker: str
    sector: str

class CompanyUpdate(BaseModel):
    name: str | None = None
    sector: str | None = None
