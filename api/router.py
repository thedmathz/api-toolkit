from fastapi import APIRouter
# 
from api.endpoints import forecast_arima, forecast_prophet
from api.endpoints import sms_semaphore

router = APIRouter()

router.include_router(forecast_arima.router, prefix="/arima", tags=["Arima Forecasting"])
router.include_router(forecast_prophet.router, prefix="/prophet", tags=["Prophet Forecasting"])
router.include_router(sms_semaphore.router, prefix="/sms-semaphore", tags=["SMS API Semaphore"])
