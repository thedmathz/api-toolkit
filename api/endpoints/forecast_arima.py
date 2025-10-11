from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pandas as pd

router = APIRouter()

'''
Expected JSON:
{
    "year"          : 2024,
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
    "year"          : 2024,
    "has_decimal"   : 0,
    "dataset"       : {
        "2021": [100, 120, 150, 180, 200, 300, 250, 220, 180, 150, 200, 350],
        "2022": [110, 130, 160, 190, 210, 320, 270, 230, 190, 160, 210, 370],
        "2023": [120, 140, 170, 200, 220, 350, 280, 240, 200, 170, 220, 400]
    }
}
'''

@router.post("/")
async def forecast(request: Request):
    try:
        data = await request.json()
        year = str(data.get("year", ""))
        has_decimal = data.get("has_decimal", 0)
        dataset = data.get("dataset", {})
        steps = int(data.get("steps", 12))

        if not dataset:
            raise HTTPException(status_code=400, detail="Dataset is missing or empty")
        if steps < 1:
            raise HTTPException(status_code=400, detail="steps must be at least 1")
        if not year:
            raise HTTPException(status_code=400, detail="Year is required")

        # Flatten dataset into a single time series
        values = []
        dates = []
        for y, monthly_values in dataset.items():
            for month_idx, val in enumerate(monthly_values, start=1):
                values.append(float(val) if has_decimal else int(val))
                dates.append(pd.Timestamp(f"{y}-{month_idx:02d}-01"))

        df = pd.DataFrame({'Bookings': values}, index=dates)

        if len(df) < 24:
            raise HTTPException(status_code=400, detail="At least 2 years of monthly data are required for seasonal forecasting")

        # Prepare forecast output for the requested year
        forecast_output = []
        months_in_dataset = dataset.get(year, [])
        existing_months_count = len(months_in_dataset)

        months_to_forecast = [i for i in range(existing_months_count + 1, 13)]
        forecast_values = []
        lower_ci = []
        upper_ci = []

        if months_to_forecast:
            # Fit SARIMA model
            model = SARIMAX(
                df['Bookings'],
                order=(1, 1, 1),
                seasonal_order=(1, 1, 1, 12),
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            model_fit = model.fit(disp=False)

            # Forecast missing months
            forecast_result = model_fit.get_forecast(steps=len(months_to_forecast))
            forecast_values = forecast_result.predicted_mean
            conf_int = forecast_result.conf_int(alpha=0.05)
            lower_ci = conf_int.iloc[:, 0]
            upper_ci = conf_int.iloc[:, 1]

        # Combine existing data and forecasted data
        for i in range(12):
            month_number = i + 1
            if i < existing_months_count:
                # Existing data
                value = months_in_dataset[i]
                forecast_output.append({
                    "month": month_number,
                    "forecast": float(value) if has_decimal else int(value),
                    "lower95CI": float(value) if has_decimal else int(value),
                    "upper95CI": float(value) if has_decimal else int(value),
                    "is_forecast": False
                })
            else:
                idx = i - existing_months_count
                value = forecast_values[idx]
                lower = lower_ci[idx]
                upper = upper_ci[idx]

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
                    "upper95CI": upper,
                    "is_forecast": True
                })

        return JSONResponse(content={
            "forecast_year": int(year),
            "forecast_result": forecast_output
        })

    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
'''
Example Output:
{
    "forecast_year": 2024,
    "forecast_result": [
        {
            "month": 1,
            "forecast": 126,
            "lower95CI": 113,
            "upper95CI": 138
        },
        {
            "month": 2,
            "forecast": 155,
            "lower95CI": 141,
            "upper95CI": 168
        },
        {
            "month": 3,
            "forecast": 181,
            "lower95CI": 167,
            "upper95CI": 194
        },
        {
            "month": 4,
            "forecast": 212,
            "lower95CI": 199,
            "upper95CI": 226
        },
        {
            "month": 5,
            "forecast": 232,
            "lower95CI": 218,
            "upper95CI": 245
        },
        {
            "month": 6,
            "forecast": 372,
            "lower95CI": 359,
            "upper95CI": 385
        },
        {
            "month": 7,
            "forecast": 288,
            "lower95CI": 275,
            "upper95CI": 302
        },
        {
            "month": 8,
            "forecast": 252,
            "lower95CI": 238,
            "upper95CI": 265
        },
        {
            "month": 9,
            "forecast": 212,
            "lower95CI": 198,
            "upper95CI": 225
        },
        {
            "month": 10,
            "forecast": 182,
            "lower95CI": 168,
            "upper95CI": 195
        },
        {
            "month": 11,
            "forecast": 232,
            "lower95CI": 218,
            "upper95CI": 245
        },
        {
            "month": 12,
            "forecast": 422,
            "lower95CI": 408,
            "upper95CI": 435
        }
    ]
}
'''
