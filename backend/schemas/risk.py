from pydantic import BaseModel

class VaRRequest(BaseModel):
    ticker: str
    confidence: float = 0.95
    simulations: int = 100_000
