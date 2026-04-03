import streamlit as st
import pandas as pd
import snowflake.connector
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os

load_dotenv()

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="COVID-19 Public Health Dashboard",
    page_icon="🦠",
    layout="wide"
)

# ── Snowflake Connection ──────────────────────────────────────
@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        schema="MARTS"
    )

@st.cache_data(ttl=600)
def run_query(query):
    conn = get_connection()
    return pd.read_sql(query, conn)

# ── Load Data ─────────────────────────────────────────────────
df_cases     = run_query("SELECT * FROM MARTS.MART_CASES_SUMMARY")
df_regional  = run_query("SELECT * FROM MARTS.MART_REGIONAL_SUMMARY")
df_vacc      = run_query("SELECT * FROM MARTS.MART_VACC_VS_CASES")
df_freshness = run_query("SELECT * FROM MARTS.MART_DATA_FRESHNESS")

# ── Fix Numeric Types ─────────────────────────────────────────
numeric_vacc = [
    "SERIES_COMPLETE_PCT", "DOSE1_POP_PCT", "BOOSTER_VAX_PCT",
    "FULLY_VACC_PER_100K", "ADMINISTERED_PER_100K", "CASE_FATALITY_RATE",
    "VACC_TO_CFR_RATIO", "NEW_CASES_PER_100K"
]
numeric_cases = [
    "NEW_CASES", "NEW_DEATHS", "TOTAL_CASES", "TOTAL_DEATHS",
    "NEW_CASES_PER_100K", "NEW_DEATHS_PER_100K", "CASE_FATALITY_RATE",
    "ROLLING_4WK_AVG_CASES", "ROLLING_4WK_AVG_DEATHS", "WOW_CASE_CHANGE_PCT"
]
numeric_regional = [
    "REGIONAL_NEW_CASES", "REGIONAL_NEW_DEATHS", "REGIONAL_TOTAL_CASES",
    "REGIONAL_TOTAL_DEATHS", "REGIONAL_POPULATION", "REGIONAL_CFR",
    "REGIONAL_CASES_PER_100K", "BOOSTER_ADOPTION_RATE_PCT", "AVG_VACC_COVERAGE_PCT"
]

for col in numeric_vacc:
    if col in df_vacc.columns:
        df_vacc[col] = pd.to_numeric(df_vacc[col], errors="coerce")

for col in numeric_cases:
    if col in df_cases.columns:
        df_cases[col] = pd.to_numeric(df_cases[col], errors="coerce")

for col in numeric_regional:
    if col in df_regional.columns:
        df_regional[col] = pd.to_numeric(df_regional[col], errors="coerce")

# ── Fix Date Types ────────────────────────────────────────────
for df in [df_cases, df_vacc, df_regional]:
    for date_col in ["WEEK_START_DATE", "WEEK_END_DATE", "LATEST_CASE_DATE", "LATEST_VACC_DATE"]:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# ── Debug Section ─────────────────────────────────────────────
with st.expander("🔍 Debug Info (remove before presentation)"):
    st.write("### df_vacc dtypes")
    st.write(df_vacc.dtypes)
    st.write("### df_vacc sample")
    st.write(df_vacc.head(3))
    st.write("### df_regional sample")
    st.write(df_regional.head(3))
    st.write("### df_cases sample")
    st.write(df_cases.head(3))

# ── Header ────────────────────────────────────────────────────
st.title("🦠 COVID-19 Public Health Dashboard")
st.caption("Data sourced from CDC, Census Bureau & Vaccination Records via Snowflake")
st.divider()

# ── KPI Cards ─────────────────────────────────────────────────
st.subheader("📊 National Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_cases = df_cases["TOTAL_CASES"].max()
    st.metric("Total Cases", f"{total_cases:,.0f}")

with col2:
    total_deaths = df_cases["TOTAL_DEATHS"].max()
    st.metric("Total Deaths", f"{total_deaths:,.0f}")

with col3:
    avg_cfr = df_cases["CASE_FATALITY_RATE"].mean()
    st.metric("Avg Case Fatality Rate", f"{avg_cfr:.2f}%" if pd.notna(avg_cfr) else "N/A")

with col4:
    fresh = df_freshness[df_freshness["FRESHNESS_STATUS"] == "Fresh"].shape[0]
    st.metric("Fresh Data Sources", f"{fresh} / {len(df_freshness)}")

st.divider()

# ── Cases & Deaths Over Time ──────────────────────────────────
st.subheader("📈 Cases & Deaths Over Time")

states = sorted(df_cases["STATE_ABBR"].dropna().unique())
selected_states = st.multiselect(
    "Filter by State (leave empty for all):",
    options=states,
    default=[]
)

df_filtered = df_cases[df_cases["STATE_ABBR"].isin(selected_states)] if selected_states else df_cases
df_time = df_filtered.groupby("WEEK_START_DATE")[["NEW_CASES", "NEW_DEATHS"]].sum().reset_index()

col1, col2 = st.columns(2)

with col1:
    fig = px.line(
        df_time.sort_values("WEEK_START_DATE"),
        x="WEEK_START_DATE",
        y="NEW_CASES",
        title="Weekly New Cases",
        color_discrete_sequence=["#e74c3c"]
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="New Cases")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.line(
        df_time.sort_values("WEEK_START_DATE"),
        x="WEEK_START_DATE",
        y="NEW_DEATHS",
        title="Weekly New Deaths",
        color_discrete_sequence=["#8e44ad"]
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="New Deaths")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Surge Weeks ───────────────────────────────────────────────
st.subheader("⚠️ Surge Weeks by State")

surge_counts = (
    df_cases[df_cases["IS_SURGE_WEEK"] == True]
    .groupby("STATE_ABBR")["IS_SURGE_WEEK"]
    .count()
    .reset_index()
)
surge_counts.columns = ["STATE_ABBR", "SURGE_WEEKS"]

if not surge_counts.empty:
    fig = px.bar(
        surge_counts.nlargest(15, "SURGE_WEEKS"),
        x="STATE_ABBR",
        y="SURGE_WEEKS",
        title="Top 15 States by Surge Weeks (>20% WoW increase)",
        color="SURGE_WEEKS",
        color_continuous_scale="Oranges"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No surge weeks data available.")

st.divider()

# ── Regional Comparison ───────────────────────────────────────
st.subheader("🗺️ Regional & State Comparison")

col1, col2 = st.columns(2)

with col1:
    latest_regional = (
        df_regional.sort_values("WEEK_START_DATE")
        .groupby("REGION").last().reset_index()
    )
    if not latest_regional.empty:
        fig = px.bar(
            latest_regional,
            x="REGION",
            y="REGIONAL_TOTAL_CASES",
            title="Total Cases by Region",
            color="REGIONAL_TOTAL_CASES",
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if not df_regional.empty:
        fig = px.line(
            df_regional.sort_values("WEEK_START_DATE"),
            x="WEEK_START_DATE",
            y="REGIONAL_CASES_PER_100K",
            color="REGION",
            title="Cases per 100K by Region Over Time"
        )
        st.plotly_chart(fig, use_container_width=True)

# ── State Map ─────────────────────────────────────────────────
latest_cases = (
    df_cases.sort_values("WEEK_START_DATE")
    .groupby("STATE_ABBR").last().reset_index()
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

st.divider()

# ── Vaccination vs Cases ──────────────────────────────────────
st.subheader("💉 Vaccination vs Case Fatality Rate")

latest_vacc = (
    df_vacc.sort_values("WEEK_START_DATE")
    .groupby("STATE_ABBR").last().reset_index()
)

col1, col2 = st.columns(2)

with col1:
    if not latest_vacc.empty and latest_vacc["ADMINISTERED_PER_100K"].notna().any():
        fig = px.scatter(
            latest_vacc,
            x="ADMINISTERED_PER_100K",
            y="CASE_FATALITY_RATE",
            hover_name="STATE_ABBR",
            color="HERD_IMMUNITY_STATUS",
            size="SERIES_COMPLETE_PCT",
            title="Vaccinations per 100K vs Case Fatality Rate",
            category_orders={
                "HERD_IMMUNITY_STATUS": ["Achieved", "In Progress", "Early Stage", "Minimal"]
            },
            color_discrete_map={
                "Achieved":    "#2ecc71",
                "In Progress": "#f39c12",
                "Early Stage": "#e67e22",
                "Minimal":     "#e74c3c"
            }
        )
        fig.update_layout(xaxis_title="Vaccinations per 100K", yaxis_title="Case Fatality Rate")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No vaccination scatter data available.")

with col2:
    if not latest_vacc.empty and latest_vacc["SERIES_COMPLETE_PCT"].notna().any():
        fig = px.bar(
            latest_vacc.nlargest(15, "SERIES_COMPLETE_PCT"),
            x="STATE_ABBR",
            y="SERIES_COMPLETE_PCT",
            title="Top 15 States by Vaccination Coverage %",
            color="SERIES_COMPLETE_PCT",
            color_continuous_scale="Greens"
        )
        fig.update_layout(xaxis_title="State", yaxis_title="Series Complete %")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No vaccination coverage data available.")

st.divider()

# ── Herd Immunity Status ──────────────────────────────────────
st.subheader("🛡️ Herd Immunity Status by State")

herd_counts = (
    latest_vacc.groupby("HERD_IMMUNITY_STATUS")["STATE_ABBR"]
    .count().reset_index()
)
herd_counts.columns = ["HERD_IMMUNITY_STATUS", "STATE_COUNT"]

col1, col2 = st.columns(2)

with col1:
    if not herd_counts.empty:
        fig = px.pie(
            herd_counts,
            names="HERD_IMMUNITY_STATUS",
            values="STATE_COUNT",
            title="States by Herd Immunity Status",
            color="HERD_IMMUNITY_STATUS",
            color_discrete_map={
                "Achieved":    "#2ecc71",
                "In Progress": "#f39c12",
                "Early Stage": "#e67e22",
                "Minimal":     "#e74c3c"
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No herd immunity data available.")

with col2:
    vacc_ratio = latest_vacc.dropna(subset=["VACC_TO_CFR_RATIO"])
    if not vacc_ratio.empty:
        fig = px.bar(
            vacc_ratio.sort_values("VACC_TO_CFR_RATIO", ascending=False).head(15),
            x="STATE_ABBR",
            y="VACC_TO_CFR_RATIO",
            title="Top 15 States: Vaccination to CFR Ratio",
            color="VACC_DEATH_CORRELATION",
            color_discrete_map={
                "Strong Positive":   "#2ecc71",
                "Moderate Positive": "#f39c12",
                "Weak/Negative":     "#e74c3c"
            }
        )
        fig.update_layout(xaxis_title="State", yaxis_title="Vacc to CFR Ratio")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No CFR ratio data available.")

st.divider()

# ── Booster Adoption ──────────────────────────────────────────
st.subheader("🔋 Booster Adoption by Region")

latest_regional = (
    df_regional.sort_values("WEEK_START_DATE")
    .groupby("REGION").last().reset_index()
)

if not latest_regional.empty and latest_regional["BOOSTER_ADOPTION_RATE_PCT"].notna().any():
    fig = px.bar(
        latest_regional,
        x="REGION",
        y="BOOSTER_ADOPTION_RATE_PCT",
        title="Booster Adoption Rate % by Region",
        color="BOOSTER_ADOPTION_RATE_PCT",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No booster adoption data available.")

st.divider()

# ── Data Freshness ────────────────────────────────────────────
st.subheader("🕐 Data Freshness Status")

def color_freshness(val):
    if val == "Fresh":
        return "background-color: #2ecc71; color: white"
    elif val == "Stale":
        return "background-color: #f39c12; color: white"
    else:
        return "background-color: #e74c3c; color: white"

if not df_freshness.empty:
    st.dataframe(
        df_freshness.style.map(color_freshness, subset=["FRESHNESS_STATUS"]),
        use_container_width=True
    )

st.divider()
st.caption("Built with Streamlit • Data from Snowflake MARTS layer • COVID-19-VB Project")