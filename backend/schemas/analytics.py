from pydantic import BaseModel

class AnalyticsRequest(BaseModel):
    iterations: int = 500_000
##
# @file analytics.py
# @brief Analytics-related endpoints.
#
# @details
# Provides CPU-intensive endpoints used for performance benchmarking.
# Includes volatility forecasting and heavy computational simulation.
##
