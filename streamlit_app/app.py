import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from snowflake_conn import query_snowflake

# --- Page Config ---
st.set_page_config(page_title="COVID-19 Public Health Dashboard", layout="wide")
st.title("COVID-19 Public Health Dashboard")

# --- Load MART tables ---
try:
    cases_data = query_snowflake("SELECT * FROM MART_CASES_SUMMARY")
    vacc_data = query_snowflake("SELECT * FROM MART_VACCINATION_VS_CASES")
    freshness_data = query_snowflake("SELECT * FROM MART_DATA_FRESHNESS")
    regional_data = query_snowflake("SELECT * FROM MART_REGIONAL_SUMMARY")
    st.sidebar.success("Data loaded successfully")
except Exception as e:
    st.error(f"Error loading data: {e}")

# --- Convert dates ---
for df in [cases_data, vacc_data, regional_data]:
    df['WEEK_START_DATE'] = pd.to_datetime(df['WEEK_START_DATE']).dt.date

# --- Sidebar Filters ---
states = sorted(vacc_data['STATE_NAME'].unique())
selected_state = st.sidebar.selectbox("Select State_NAME", states)

weeks = sorted(vacc_data['WEEK_START_DATE'].unique())
selected_week_range = st.sidebar.slider(
    "Select Week Range",
    min_value=weeks[0],
    max_value=weeks[-1],
    value=(weeks[0], weeks[-1])
)

# --- Data Freshness ---
if not freshness_data.empty:
    st.sidebar.subheader("Data Freshness")
    for _, row in freshness_data.iterrows():
        st.sidebar.markdown(
            f"- **{row['SOURCE_NAME']}**  \n"
            f"Last Updated: {row['LAST_UPDATED']}  \n"
            f"({row['DAYS_SINCE_LAST_UPDATE']} days ago)"
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
    state_cases_sorted = state_cases.sort_values('WEEK_START_DATE')

    total_cases = state_cases_sorted['TOTAL_CASES'].iloc[-1]
    total_deaths = state_cases_sorted['TOTAL_DEATHS'].iloc[-1]
    avg_cfr = round(state_cases['CASE_FATALITY_RATE'].mean(), 2)

    kpi1, kpi2, kpi3 = st.columns(3)

    kpi1.metric(f"{selected_state} Total Cases", f"{int(total_cases):,}")
    kpi2.metric(f"{selected_state} Total Deaths", f"{int(total_deaths):,}")
    kpi3.metric(f"{selected_state} Avg CFR (%)", f"{avg_cfr}%")

# --- Regional Summary ---
st.subheader("Regional Summary")

col1, col2 = st.columns(2)

latest_regional = (
    regional_data.sort_values('WEEK_START_DATE')
    .groupby("REGION")
    .last()
    .reset_index()
)

with col1:
    if not latest_regional.empty:
        fig = px.bar(
            latest_regional,
            x="REGION",
            y="TOTAL_CASES",
            title="Total Cases by Region",
            color="TOTAL_CASES",
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig, use_container_width=True)

# with col2:
#     if not regional_data.empty:
#         fig = px.line(
#             regional_data.sort_values('WEEK_START_DATE'),
#             x="WEEK_START_DATE",
#             y="CASES_PER_100K",
#             title="Cases per 100K by Region",
#             color="REGION"
#         )
#         st.plotly_chart(fig, use_container_width=True)

# ── State Map ─────────────────────────────────────────────────
latest_cases = (
    cases_data.sort_values("WEEK_START_DATE")
    .groupby("STATE_ABBR")
    .last()
    .reset_index()
)

fig = px.choropleth(
    latest_cases,
    locations="STATE_ABBR",   
    locationmode="USA-states",
    color="TOTAL_CASES",
    scope="usa",
    title="Total Cases by State (Map)",
    color_continuous_scale="Reds"
)

st.plotly_chart(fig, use_container_width=True)


# --- Monthly Trend Chart ---
if not state_vacc.empty:
    st.subheader(f"Monthly Trend: New Cases vs Vaccinated People ({selected_state})")

    state_vacc = state_vacc.copy()
    state_vacc['WEEK_START_DATE'] = pd.to_datetime(state_vacc['WEEK_START_DATE'])
    state_vacc['MONTH'] = state_vacc['WEEK_START_DATE'].dt.to_period('M').astype(str)

    monthly_df = state_vacc.groupby('MONTH').agg({
        'NEW_CASES': 'sum',
        'TOTAL_ADMINISTERED': 'max'
    }).reset_index()

    fig = go.Figure()

    # New Cases
    fig.add_trace(go.Scatter(
        x=monthly_df['MONTH'],
        y=monthly_df['NEW_CASES'],
        name='New Cases',
        mode='lines+markers',
        line=dict(color='dimgray', width=3)
    ))

    # Vaccination
    fig.add_trace(go.Scatter(
        x=monthly_df['MONTH'],
        y=monthly_df['TOTAL_ADMINISTERED'],
        name='Vaccinated People',
        mode='lines+markers',
        line=dict(color='steelblue', width=3),
        yaxis='y2'
    ))

    fig.update_layout(
        xaxis_title="Month",
        yaxis=dict(title="New Cases"),
        yaxis2=dict(title="Vaccinated People", overlaying='y', side='right'),
        template="plotly_white",
        legend=dict(x=0.1, y=1.1)
    )

    st.plotly_chart(fig, use_container_width=True)