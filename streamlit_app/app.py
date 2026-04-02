import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from snowflake_conn import query_snowflake

# --- Page Config ---
st.set_page_config(page_title="COVID-19 Dashboard", layout="wide")
st.title("COVID-19 Public Health Dashboard")

# --- Load MART tables ---
try:
    cases_df = query_snowflake("SELECT * FROM MART_CASES_SUMMARY")
    vacc_df = query_snowflake("SELECT * FROM MART_VACCINATION_VS_CASES")
    freshness_df = query_snowflake("SELECT * FROM MART_DATA_FRESHNESS")
    st.sidebar.success("Data loaded successfully")
except Exception as e:
    st.error(f"Error loading data: {e}")

# --- Convert dates to date only (no timestamp) ---
for df in [cases_df, vacc_df]:
    df['WEEK_START_DATE'] = pd.to_datetime(df['WEEK_START_DATE']).dt.date

# --- Sidebar Filters ---
states = sorted(vacc_df['STATE'].unique())
selected_state = st.sidebar.selectbox("Select State", states)

weeks = sorted(vacc_df['WEEK_START_DATE'].unique())
selected_week_range = st.sidebar.slider(
    "Select Week Range",
    min_value=weeks[0],
    max_value=weeks[-1],
    value=(weeks[0], weeks[-1]),
    format="YYYY-MM-DD"
)

# --- Data Freshness (bullet points) ---
if not freshness_df.empty:
    st.sidebar.subheader("Data Freshness")
    for _, row in freshness_df.iterrows():
        st.sidebar.markdown(
            f"- **{row['SOURCE_NAME']}**  \n  Last Updated: {row['LAST_UPDATED']}  \n  ({row['DAYS_SINCE_LAST_UPDATE']} days ago)"
        )

# --- Filter data by state and week ---
state_cases = cases_df[
    (cases_df['STATE'] == selected_state) &
    (cases_df['WEEK_START_DATE'] >= selected_week_range[0]) &
    (cases_df['WEEK_START_DATE'] <= selected_week_range[1])
]

state_vacc = vacc_df[
    (vacc_df['STATE'] == selected_state) &
    (vacc_df['WEEK_START_DATE'] >= selected_week_range[0]) &
    (vacc_df['WEEK_START_DATE'] <= selected_week_range[1])
]

# --- Dynamic KPIs by State ---
if not state_cases.empty:
    total_cases = state_cases['TOTAL_CASES'].sum()
    total_deaths = state_cases['TOTAL_DEATHS'].sum()
    avg_cfr = (state_cases['CASE_FATALITY_RATE'].mean()).round(2)
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(f"{selected_state} Total Cases", f"{total_cases:,}")
    kpi2.metric(f"{selected_state} Total Deaths", f"{total_deaths:,}")
    kpi3.metric(f"{selected_state} Avg Case Fatality Rate (%)", f"{avg_cfr}%")

# --- Line Chart: Monthly Trend of New Cases vs Vaccinated People ---
if not state_vacc.empty:
    st.subheader(f"Monthly Trend: New Cases vs Vaccinated People ({selected_state})")

    # Convert to datetime for grouping
    state_vacc['WEEK_START_DATE'] = pd.to_datetime(state_vacc['WEEK_START_DATE'])
    state_vacc['MONTH'] = state_vacc['WEEK_START_DATE'].dt.to_period('M').astype(str)

    # Aggregate monthly
    monthly_df = state_vacc.groupby('MONTH').agg({
        'NEW_CASES': 'sum',
        'ADMINISTERED': 'max'  # cumulative vaccinated people
    }).reset_index()

    # Plot
    fig = go.Figure()

    # New Cases (dark gray)
    fig.add_trace(go.Scatter(
        x=monthly_df['MONTH'],
        y=monthly_df['NEW_CASES'],
        name='New Cases',
        mode='lines+markers',
        line=dict(color='dimgray', width=3)
    ))

    # Vaccinated People (soft blue-gray)
    fig.add_trace(go.Scatter(
        x=monthly_df['MONTH'],
        y=monthly_df['ADMINISTERED'],
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