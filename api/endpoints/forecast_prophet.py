import pandas as pd
from prophet import Prophet
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

'''
Expected JSON:
{
    "has_decimal"   : 0,  # 0 for int, 1 for float
    "type"          : 1,  # 1=annually, 2=monthly, 3=weekly
    "dataset"       : [N, N, N, N, ...],
    "steps"         : 3  # optional, default 5
}

Example JSON body:
{
    "has_decimal": 1,
    "last_date": "2023-03-01",
    "type": 3, 
    "dataset": [120, 150, 180, 200, 250, 300, 280, 270, 260, 240, 300, 500],
    "steps": 6 
}
'''
@router.post("/")
async def forecast(request: Request):
    try:
        data = await request.json()

        # Validate input
        if "type" not in data or "dataset" not in data:
            raise HTTPException(status_code=400, detail="'type' and 'dataset' are required")
        
        ts_type = data["type"]
        dataset = data["dataset"]
        steps = data.get("steps", 5)
        last_date = data.get("last_date")  # optional

        if not isinstance(dataset, list) or len(dataset) == 0:
            raise HTTPException(status_code=400, detail="'dataset' must be a non-empty list")

        # Determine frequency
        if ts_type == 1:  # yearly
            freq = 'Y'
            yearly_seasonality = True
            weekly_seasonality = False
        elif ts_type == 2:  # monthly
            freq = 'M'
            yearly_seasonality = True
            weekly_seasonality = False
        elif ts_type == 3:  # weekly
            freq = 'W'
            yearly_seasonality = False
            weekly_seasonality = True
        else:
            raise HTTPException(status_code=400, detail="Invalid 'type' (1=annual,2=monthly,3=weekly)")

        # Generate historical dates
        if last_date:
            last_date = pd.to_datetime(last_date)
            dates = pd.date_range(end=last_date, periods=len(dataset), freq=freq)
        else:
            # fallback to fixed start date
            start_date = '2023-01-01'
            dates = pd.date_range(start=start_date, periods=len(dataset), freq=freq)

        df = pd.DataFrame({"ds": dates, "y": dataset})

        # Build and fit Prophet model
        model = Prophet(yearly_seasonality=yearly_seasonality,
                        weekly_seasonality=weekly_seasonality,
                        daily_seasonality=False)
        if ts_type == 2:
            model.add_seasonality(name="monthly", period=30.5, fourier_order=5)
        model.fit(df)

        # Forecast future
        future = model.make_future_dataframe(periods=steps, freq=freq)
        forecast = model.predict(future)

        # Prepare JSON response
        result = forecast[["ds","yhat","yhat_lower","yhat_upper"]].tail(steps).copy()
        result["ds"] = result["ds"].dt.strftime("%Y-%m-%d")  # convert Timestamp -> string

        # Round values if has_decimal == 0
        has_decimal = data.get("has_decimal", 1)
        if has_decimal == 0:
            result["yhat"] = result["yhat"].round(0).astype(int)
            result["yhat_lower"] = result["yhat_lower"].round(0).astype(int)
            result["yhat_upper"] = result["yhat_upper"].round(0).astype(int)

        result_list = result.to_dict(orient="records")

        return JSONResponse(content={"forecast": result_list})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
'''
Example Output:
{
    "forecast": [
        {
            "ds": "2023-03-05",
            "yhat": 397.0598984933295,
            "yhat_lower": 332.83148346633357,
            "yhat_upper": 468.0835582817408
        },
        {
            "ds": "2023-03-12",
            "yhat": 419.04435304626617,
            "yhat_lower": 355.5786169637112,
            "yhat_upper": 482.58921105356666
        },
        {
            "ds": "2023-03-19",
            "yhat": 441.0288075992028,
            "yhat_lower": 376.83426759225114,
            "yhat_upper": 507.7947749755616
        },
        {
            "ds": "2023-03-26",
            "yhat": 463.0132621521394,
            "yhat_lower": 394.6845472628718,
            "yhat_upper": 529.2559618819809
        },
        {
            "ds": "2023-04-02",
            "yhat": 484.9977167050762,
            "yhat_lower": 415.1323407024654,
            "yhat_upper": 554.1616881661565
        },
        {
            "ds": "2023-04-09",
            "yhat": 506.9821712580128,
            "yhat_lower": 431.9973927529089,
            "yhat_upper": 575.4991457613587
        }
    ]
}
'''