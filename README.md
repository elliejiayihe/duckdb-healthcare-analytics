# duckdb-healthcare-analytics

Setup and run instructions 

Option 1 — Run Interactive Dashboard 
Step 1 — Open Terminal

Navigate to the project data folder:
cd /Users/elliehe/Desktop/DSCI_551/PulseInsight_Project/data
Step 2 — Create Conda Environment (ONE TIME ONLY)
conda create -n pulseinsight python=3.10 -y
Step 3 — Activate Environment
conda activate pulseinsight
Step 4 — Install Required Packages
pip install streamlit duckdb pandas plotly
Step 5 — Run the Streamlit Dashboard
python -m streamlit run streamlit_app.py
Step 6 — Open the Dashboard

Option 2 - Run Notebook Queries

All queries are executed through DuckDB.
1. Navigate to project folder:
   cd code/PulseInsight_DuckDB_Queries.ipynb

2. Install required packages (ONE TIME ONLY):
   pip install duckdb pandas notebook

3. Launch Jupyter Notebook:
   jupyter notebook

4. Open and run:
   PulseInsight_DuckDB_Queries.ipynb

Option 3  DuckDB command-line interface (CLI)
if you prefer to run the queries directly without using the notebook, you can use the DuckDB command-line interface (CLI).

1. brew install duckdb
2. cd PulseInsight_Project
3. duckdb diabetes.db
4. run queries manually. e.g.

SELECT COUNT(*) FROM diabetes;

SELECT AVG(Glucose) FROM diabetes;

SELECT Outcome, AVG(BMI)
FROM diabetes
GROUP BY Outcome;

SELECT *
FROM diabetes
WHERE Age BETWEEN 30 AND 50;

SELECT *
FROM diabetes
WHERE Glucose > 150 AND BMI > 35;

* This step is optional — all queries are already included in the notebook
* The notebook is the recommended way to run the project
