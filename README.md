# duckdb-healthcare-analytics

Setup and run instructions 
1. Navigate to project folder:
   cd code/PulseInsight_DuckDB_Queries.ipynb

2. Install required packages (ONE TIME ONLY):
   pip install duckdb pandas notebook

3. Launch Jupyter Notebook:
   jupyter notebook

4. Open and run:
   PulseInsight_DuckDB_Queries.ipynb

Alternately, if you prefer to run the queries directly without using the notebook, you can use the DuckDB command-line interface (CLI).

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
