import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from snowflake_conn import query_snowflake
import plotly.express as px
from datetime import datetime, timezone

st.set_page_config(page_title="COVID Dashboard", layout="wide")

st.title("COVID Impact & Vaccination Progress Analysis")

# --- Load Data ---
cases_data = query_snowflake("SELECT * FROM MART_CASES_SUMMARY")
vacc_data = query_snowflake("SELECT * FROM MART_VACCINATION_VS_CASES")
freshness_data = query_snowflake("SELECT * FROM MART_DATA_FRESHNESS")
regional_data = query_snowflake("SELECT * FROM MART_REGIONAL_SUMMARY")
# --- Convert date ---
for df in [cases_data, vacc_data]:
    df['WEEK_START_DATE'] = pd.to_datetime(df['WEEK_START_DATE']).dt.date

# --- Sidebar Filters ---
states = sorted(cases_data['STATE_NAME'].unique())
selected_state = st.sidebar.selectbox("Select State", states)

weeks = sorted(cases_data['WEEK_START_DATE'].unique())
selected_week_range = st.sidebar.slider(
    "Select Week Range",
    min_value=weeks[0],
    max_value=weeks[-1],
    value=(weeks[0], weeks[-1])
)

# --- Data Freshness ---
st.sidebar.subheader("Data Freshness")
now = datetime.now(timezone.utc)

for _, row in freshness_data.iterrows():
    last_updated = row["LAST_UPDATED"]

    # Convert to datetime if not NaT
    if pd.notna(last_updated):
        last_updated = pd.to_datetime(last_updated, utc=True)
        time_diff = now - last_updated
        days = time_diff.days
        hours = time_diff.seconds // 3600

        if days > 0:
            staleness = f"{days} days old"
        else:
            staleness = f"{hours} hours old"

        last_updated_str = last_updated.strftime('%Y-%m-%d %H:%M')
    else:
        staleness = "unknown"
        last_updated_str = "N/A"

    st.sidebar.write(
        f"- {row['SOURCE_NAME']} (Last updated: {last_updated_str}, {staleness})"
    )

# --- Filter Data ---
state_cases = cases_data[
    (cases_data['STATE_NAME'] == selected_state) &
    (cases_data['WEEK_START_DATE'] >= selected_week_range[0]) &
    (cases_data['WEEK_START_DATE'] <= selected_week_range[1])
]

state_vacc = vacc_data[
    (vacc_data['STATE_NAME'] == selected_state) &
    (vacc_data['WEEK_START_DATE'] >= selected_week_range[0]) &
    (vacc_data['WEEK_START_DATE'] <= selected_week_range[1])
]

# --- KPIs ---
if not state_cases.empty:
    total_cases = int(state_cases['TOTAL_CASES'].sum())
    total_deaths = int(state_cases['TOTAL_DEATHS'].sum())
    new_cases = int(state_cases['NEW_CASES'].sum())
    avg_cfr = round(state_cases['CASE_FATALITY_RATE'].mean(), 2)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Cases", f"{total_cases:,}")
    c2.metric("Total Deaths", f"{total_deaths:,}")
    c3.metric("New Cases", f"{new_cases:,}")
    c4.metric("Fatality Rate (%)", f"{avg_cfr}%")

# --- Regional Summary ---

st.subheader("Regional Summary") 
col1, col2 = st.columns(2) 
latest_regional = ( regional_data.sort_values('WEEK_START_DATE') .groupby("REGION") .last() .reset_index() )

fig = px.bar(
    latest_regional,
    x="REGION",
    y="CASES_PER_100K",
    title="Cases per 100K by Region",
    color="CASES_PER_100K",
    color_continuous_scale="Greys"
)
st.plotly_chart(fig, use_container_width=True)

# State Map
latest_cases = ( cases_data.sort_values("WEEK_START_DATE") .groupby("STATE_ABBR") .last() .reset_index() )
fig = px.choropleth(
    latest_cases,
    locations="STATE_ABBR",
    locationmode="USA-states",
    color="CASES_PER_100K",
    scope="usa",
    title="Cases per 100K by State",
    color_continuous_scale="Greys"
)
st.plotly_chart(fig, use_container_width=True)

# --- Monthly Aggregation ---
state_cases['MONTH'] = pd.to_datetime(state_cases['WEEK_START_DATE']).dt.to_period('M').dt.to_timestamp()

monthly_cases = state_cases.groupby('MONTH').agg({
    'NEW_CASES': 'sum',
    'ROLLING_7D_AVG_NEW_CASES': 'mean',
    'CASES_PER_100K': 'mean'
}).reset_index()

state_vacc['MONTH'] = pd.to_datetime(state_vacc['WEEK_START_DATE']).dt.to_period('M').dt.to_timestamp()

monthly_vacc = state_vacc.groupby('MONTH').agg({
    'TOTAL_ADMINISTERED': 'sum'
}).reset_index()

# --- Chart Selection ---
chart_option = st.radio(
    "Select Analysis View",
    ["Cases Trend ", "Cases per 100K", "Cases vs Vaccination"]
)


# OPTION A: BEST STORY

if chart_option == "Cases Trend ":
    st.subheader(f"COVID Waves Over Time ({selected_state})")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=monthly_cases['MONTH'],
        y=monthly_cases['NEW_CASES'],
        name="New Cases",
        line=dict(color="black", width=3)
    ))

    fig.add_trace(go.Scatter(
        x=monthly_cases['MONTH'],
        y=monthly_cases['ROLLING_7D_AVG_NEW_CASES'],
        name="7-Day Avg",
        line=dict(color="gray", width=3, dash='dot')
    ))

    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.info("Insight: This clearly shows COVID waves over time, including major peaks like early 2022.")


# OPTION B: PER 100K

elif chart_option == "Cases per 100K":
    st.subheader(f"Cases per 100K Population ({selected_state})")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=monthly_cases['MONTH'],
        y=monthly_cases['CASES_PER_100K'],
        name="Cases per 100K",
        line=dict(color="dimgray", width=3)
    ))

    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.info("Insight: This adjusts cases for population, allowing fair comparison across states.")


# OPTION C: CASES vs VACCINATION

elif chart_option == "Cases vs Vaccination":
    st.subheader(f"Cases vs Vaccination Activity ({selected_state})")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=monthly_cases['MONTH'],
        y=monthly_cases['NEW_CASES'],
        name="New Cases",
        line=dict(color="black", width=3)
    ))

    fig.add_trace(go.Scatter(
        x=monthly_vacc['MONTH'],
        y=monthly_vacc['TOTAL_ADMINISTERED'],
        name="Vaccinations",
        line=dict(color="gray", width=3),
        yaxis="y2"
    ))

    fig.update_layout(
        yaxis=dict(title="New Cases"),
        yaxis2=dict(title="Vaccinations", overlaying="y", side="right"),
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info("Insight: Vaccination increases steadily, while cases show wave patterns.")