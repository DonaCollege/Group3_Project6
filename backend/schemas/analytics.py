from pydantic import BaseModel

class AnalyticsRequest(BaseModel):
    iterations: int = 500_000
