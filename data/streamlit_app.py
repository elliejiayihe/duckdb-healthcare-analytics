"""
PulseInsight Streamlit Dashboard
DSCI 551 Course Project
Author: Ellie He

This app provides an interactive dashboard on top of DuckDB.
It loads the diabetes.csv dataset into DuckDB if needed, then allows
users to filter cohorts and run analytical queries through UI controls.
"""

from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="PulseInsight DuckDB Dashboard",
    page_icon="🩺",
    layout="wide",
)

st.title("PulseInsight: DuckDB Healthcare Analytics")
st.caption("Interactive analytical dashboard powered by DuckDB columnar execution")

# -----------------------------
# File paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "diabetes.csv"
DB_PATH = BASE_DIR / "diabetes.db"

# -----------------------------
# Database helper functions
# -----------------------------
@st.cache_resource
def get_connection():
    """Create a cached DuckDB connection."""
    return duckdb.connect(str(DB_PATH))


def ensure_table_exists(con: duckdb.DuckDBPyConnection):
    """Create the diabetes table from CSV if it does not already exist."""
    table_exists = con.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = 'diabetes'
        """
    ).fetchone()[0]

    if not table_exists:
        if not CSV_PATH.exists():
            st.error(
                "diabetes.csv was not found. Please place diabetes.csv in the same folder as streamlit_app.py."
            )
            st.stop()
        con.execute(
            f"""
            CREATE TABLE diabetes AS
            SELECT *
            FROM read_csv_auto('{CSV_PATH.as_posix()}')
            """
        )


@st.cache_data
def load_base_dataframe(_db_path: str) -> pd.DataFrame:
    """Load the full diabetes table as a DataFrame for UI control ranges."""
    con = duckdb.connect(_db_path)
    df = con.execute("SELECT * FROM diabetes").fetchdf()
    con.close()
    return df


# -----------------------------
# Initialize database
# -----------------------------
con = get_connection()
ensure_table_exists(con)
base_df = load_base_dataframe(str(DB_PATH))

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Cohort Filters")

min_age = int(base_df["Age"].min())
max_age = int(base_df["Age"].max())
age_range = st.sidebar.slider(
    "Age range",
    min_value=min_age,
    max_value=max_age,
    value=(30, 50),
)

min_bmi = float(base_df["BMI"].min())
max_bmi = float(base_df["BMI"].max())
bmi_threshold = st.sidebar.slider(
    "Minimum BMI",
    min_value=float(round(min_bmi, 1)),
    max_value=float(round(max_bmi, 1)),
    value=0.0,
    step=0.1,
)

min_glucose = int(base_df["Glucose"].min())
max_glucose = int(base_df["Glucose"].max())
glucose_threshold = st.sidebar.slider(
    "Minimum glucose",
    min_value=min_glucose,
    max_value=max_glucose,
    value=min_glucose,
)

outcome_filter = st.sidebar.selectbox(
    "Diabetes outcome",
    options=["All", "0 = Non-diabetic", "1 = Diabetic"],
)

show_query = st.sidebar.checkbox("Show generated SQL", value=True)

# -----------------------------
# Dynamic SQL generation
# -----------------------------
where_clauses = [
    "Age BETWEEN ? AND ?",
    "BMI >= ?",
    "Glucose >= ?",
]
params = [age_range[0], age_range[1], bmi_threshold, glucose_threshold]

if outcome_filter.startswith("0"):
    where_clauses.append("Outcome = ?")
    params.append(0)
elif outcome_filter.startswith("1"):
    where_clauses.append("Outcome = ?")
    params.append(1)

where_sql = " AND ".join(where_clauses)

cohort_sql = f"""
SELECT *
FROM diabetes
WHERE {where_sql}
"""

summary_sql = f"""
SELECT
    COUNT(*) AS patient_count,
    AVG(Glucose) AS avg_glucose,
    AVG(BMI) AS avg_bmi,
    AVG(Outcome) AS diabetes_rate
FROM diabetes
WHERE {where_sql}
"""

group_sql = f"""
SELECT
    Outcome,
    COUNT(*) AS patient_count,
    AVG(Glucose) AS avg_glucose,
    AVG(BMI) AS avg_bmi,
    AVG(Age) AS avg_age
FROM diabetes
WHERE {where_sql}
GROUP BY Outcome
ORDER BY Outcome
"""

# -----------------------------
# Execute queries
# -----------------------------
cohort_df = con.execute(cohort_sql, params).fetchdf()
summary_df = con.execute(summary_sql, params).fetchdf()
group_df = con.execute(group_sql, params).fetchdf()

# -----------------------------
# Dashboard layout
# -----------------------------
metric_cols = st.columns(4)
summary = summary_df.iloc[0]

metric_cols[0].metric("Patients in Cohort", int(summary["patient_count"]))
metric_cols[1].metric("Average Glucose", f"{summary['avg_glucose']:.2f}" if pd.notnull(summary["avg_glucose"]) else "N/A")
metric_cols[2].metric("Average BMI", f"{summary['avg_bmi']:.2f}" if pd.notnull(summary["avg_bmi"]) else "N/A")
metric_cols[3].metric("Diabetes Rate", f"{summary['diabetes_rate'] * 100:.1f}%" if pd.notnull(summary["diabetes_rate"]) else "N/A")

if show_query:
    with st.expander("Generated SQL Query"):
        st.code(cohort_sql, language="sql")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "Cohort Table",
    "Grouped Analysis",
    "Visual Analysis",
    "Internals Mapping",
])

with tab1:
    st.subheader("Filtered Patient Cohort")
    st.write("This table updates based on the sidebar filters.")
    st.dataframe(cohort_df, use_container_width=True, height=420)

with tab2:
    st.subheader("Grouped Aggregation by Diabetes Outcome")
    st.write("DuckDB computes grouped aggregates using only the columns needed for the query.")
    st.dataframe(group_df, use_container_width=True)

with tab3:
    st.subheader("Interactive Visual Analysis")

    left, right = st.columns(2)

    with left:
        st.markdown("**Average Glucose by Outcome**")
        if not group_df.empty:
            chart_df = group_df.set_index("Outcome")[["avg_glucose"]]
            st.bar_chart(chart_df)
        else:
            st.info("No rows match the selected filters.")

    with right:
        st.markdown("**Average BMI by Outcome**")
        if not group_df.empty:
            chart_df = group_df.set_index("Outcome")[["avg_bmi"]]
            st.bar_chart(chart_df)
        else:
            st.info("No rows match the selected filters.")

    st.markdown("**Glucose vs BMI Cohort View**")
    if not cohort_df.empty:
        st.scatter_chart(cohort_df, x="BMI", y="Glucose", color="Outcome")
    else:
        st.info("No rows match the selected filters.")

with tab4:
    st.subheader("Mapping Application Behavior to DuckDB Internals")
    st.markdown(
        """
        **Application behavior:** The user adjusts filters such as age range, BMI threshold, glucose threshold, and outcome.

        **Generated database operation:** The dashboard dynamically generates SQL queries with `WHERE`, `GROUP BY`, and aggregation operations.

        **DuckDB internal behavior:**
        - Column pruning reads only the columns needed for each query, such as `Age`, `BMI`, `Glucose`, and `Outcome`.
        - Predicate pushdown applies filters early, reducing the number of rows processed by later operators.
        - Vectorized execution processes data in batches rather than tuple by tuple.

        **Why it matters:** These internals make DuckDB efficient for analytical dashboard workloads where users repeatedly filter cohorts and compute aggregate statistics.
        """
    )

st.divider()
st.caption("PulseInsight demo app | DuckDB + Streamlit | DSCI 551")
