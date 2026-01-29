import random
from schemas.risk import VaRRequest

def calculate_var(request: VaRRequest):
    """
    TODO (Nikhil):
    - Replace random simulation with DB-based returns
    """
    simulated_losses = [
        random.gauss(0, 1) for _ in range(request.simulations)
    ]
    simulated_losses.sort()
    index = int((1 - request.confidence) * len(simulated_losses))
    return {
        "ticker": request.ticker,
        "confidence": request.confidence,
        "value_at_risk": round(simulated_losses[index], 4)
    }
