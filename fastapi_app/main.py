from fastapi import FastAPI
import pandas as pd
from streamlit_app.snowflake_conn import query_snowflake


#consider sperating handlers fromn routes
# single responsibility principle, better organization as the app grows, easier testing and maintenance

app = FastAPI(
    title="COVID-19 Public Health API",
    version="1.0.0",
    description="API layer serving COVID-19 analytics data."
)

# a lot of slect * here, consider optimizing queries to only pull necessary columns for each endpoint
cases_data = query_snowflake("SELECT * FROM MART_CASES_SUMMARY")
vacc_data = query_snowflake("SELECT * FROM MART_VACCINATION_VS_CASES")
regional_data = query_snowflake("SELECT * FROM MART_REGIONAL_SUMMARY")
freshness_data = query_snowflake("SELECT * FROM MART_DATA_FRESHNESS")


for data_sets in [cases_data, vacc_data, regional_data]:
    data_sets['WEEK_START_DATE'] = pd.to_datetime(data_sets['WEEK_START_DATE']).dt.date


@app.get("/api/v1/state/{state_code}/summary")
def state_summary(state_code: str):
    state_cases = cases_data[cases_data['STATE_ABBR'] == state_code.upper()]
    if state_cases.empty:
        return {"error": "State not found or no data."}

    total_cases = int(state_cases['TOTAL_CASES'].sum())
    total_deaths = int(state_cases['TOTAL_DEATHS'].sum())
    new_cases = int(state_cases['NEW_CASES'].sum())
    avg_cfr = round(state_cases['CASE_FATALITY_RATE'].mean(), 2)

    return {
        "state_name": state_code.upper(),
        "total_cases": total_cases,
        "total_deaths": total_deaths,
        "new_cases": new_cases,
        "avg_case_fatality_rate": avg_cfr
    }


@app.get("/api/v1/state/{state_code}/vaccination_trend")
def vaccination_trend(state_code: str):
    state_vacc = vacc_data[vacc_data['STATE_ABBR'] == state_code.upper()]

    if state_vacc.empty:
        return {"error": "State not found or no data."}

    trend = state_vacc[
        ['WEEK_START_DATE', 'TOTAL_ADMINISTERED','TOTAL_DISTRIBUTED' ,'NEW_CASES']
    ].sort_values('WEEK_START_DATE')


    trend = trend.replace({float("nan"): None})

    return trend.to_dict(orient="records")

@app.get("/api/v1/health")
def health_status():
    health_data = freshness_data.fillna("N/A") 
    return health_data.to_dict(orient="records")