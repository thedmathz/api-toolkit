from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pandas as pd

router = APIRouter()

'''
Expected JSON:
{
    "has_decimal"   : 0,  # 0 for int, 1 for float
    "dataset"       : {
        "2021": [100, 120, 320, 123, 100, ...],
        "2022": [...],
        "2023": [...]
    },
    "steps"         : 12  # optional, default 12 months
}

Example JSON body:
{
    "has_decimal": 0,
    "dataset": {
        "2021": [100, 120, 150, 180, 200, 300, 250, 220, 180, 150, 200, 350],
        "2022": [110, 130, 160, 190, 210, 320, 270, 230, 190, 160, 210, 370],
        "2023": [120, 140, 170, 200, 220, 350, 280, 240, 200, 170, 220, 400]
    }
}
'''

@router.post("/")
async def forecast(request: Request):
    try:
        # Parse JSON body
        data = await request.json()
        has_decimal = data.get("has_decimal", 0)
        dataset = data.get("dataset", {})
        steps = int(data.get("steps", 12))

        if not dataset:
            raise HTTPException(status_code=400, detail="Dataset is missing or empty")
        if steps < 1:
            raise HTTPException(status_code=400, detail="steps must be at least 1")

        # Flatten dataset into a single time series
        all_years = sorted(dataset.keys())
        values = []
        dates = []
        for year in all_years:
            monthly_values = dataset[year]
            if len(monthly_values) != 12:
                raise HTTPException(status_code=400, detail=f"Year {year} must have 12 monthly values")
            for month_idx, val in enumerate(monthly_values, start=1):
                values.append(float(val) if has_decimal else int(val))
                dates.append(pd.Timestamp(f"{year}-{month_idx:02d}-01"))

        # Create DataFrame
        df = pd.DataFrame({'Bookings': values}, index=dates)

        if len(df) < 24:
            raise HTTPException(status_code=400, detail="At least 2 years of monthly data are required for seasonal forecasting")

        # Fit SARIMA model with yearly seasonality (s=12)
        model = SARIMAX(
            df['Bookings'], 
            order=(1,1,1), 
            seasonal_order=(1,1,1,12),
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        model_fit = model.fit(disp=False)

        # Forecast for requested number of steps
        forecast_result = model_fit.get_forecast(steps=steps)
        forecast_values = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int(alpha=0.05)
        lower_ci = conf_int.iloc[:,0]
        upper_ci = conf_int.iloc[:,1]

        # Determine the forecast year (all months belong to the next year)
        last_date = df.index[-1]
        forecast_year = (last_date + pd.DateOffset(months=1)).year

        # Prepare result
        forecast_output = []
        for i in range(steps):
            month_number = (i % 12) + 1  # month from 1 to 12
            value = forecast_values[i]
            lower = lower_ci[i]
            upper = upper_ci[i]

            if not has_decimal:
                value = int(round(value))
                lower = int(round(lower))
                upper = int(round(upper))
            else:
                value = round(value, 2)
                lower = round(lower, 2)
                upper = round(upper, 2)

            forecast_output.append({
                "month": month_number,
                "forecast": value,
                "lower95CI": lower,
                "upper95CI": upper
            })

        return JSONResponse(content={
            "forecast_year": forecast_year,
            "forecast_result": forecast_output
        })

    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
'''
Example Output:
{
    "forecast": [
        {
            "year": 2024,
            "month": 1,
            "forecast": 126,
            "lower95CI": 113,
            "upper95CI": 138
        },
        {
            "year": 2024,
            "month": 2,
            "forecast": 155,
            "lower95CI": 141,
            "upper95CI": 168
        },
        {
            "year": 2024,
            "month": 3,
            "forecast": 181,
            "lower95CI": 167,
            "upper95CI": 194
        },
        {
            "year": 2024,
            "month": 4,
            "forecast": 212,
            "lower95CI": 199,
            "upper95CI": 226
        },
        {
            "year": 2024,
            "month": 5,
            "forecast": 232,
            "lower95CI": 218,
            "upper95CI": 245
        },
        {
            "year": 2024,
            "month": 6,
            "forecast": 372,
            "lower95CI": 359,
            "upper95CI": 385
        },
        {
            "year": 2024,
            "month": 7,
            "forecast": 288,
            "lower95CI": 275,
            "upper95CI": 302
        },
        {
            "year": 2024,
            "month": 8,
            "forecast": 252,
            "lower95CI": 238,
            "upper95CI": 265
        },
        {
            "year": 2024,
            "month": 9,
            "forecast": 212,
            "lower95CI": 198,
            "upper95CI": 225
        },
        {
            "year": 2024,
            "month": 10,
            "forecast": 182,
            "lower95CI": 168,
            "upper95CI": 195
        },
        {
            "year": 2024,
            "month": 11,
            "forecast": 232,
            "lower95CI": 218,
            "upper95CI": 245
        },
        {
            "year": 2024,
            "month": 12,
            "forecast": 422,
            "lower95CI": 408,
            "upper95CI": 435
        }
    ]
}
'''
