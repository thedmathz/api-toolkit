from fastapi import APIRouter
# 
from api.endpoints import forecast_arima, forecast_prophet

router = APIRouter()

router.include_router(forecast_arima.router, prefix="/arima", tags=["Arima Forecasting"])
router.include_router(forecast_prophet.router, prefix="/prophet", tags=["Prophet Forecasting"])
