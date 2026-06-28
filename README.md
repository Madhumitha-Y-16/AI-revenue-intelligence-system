# AI-Powered Revenue Intelligence System

I built this project to simulate what a real revenue analytics system looks like at an Indian B2B company. The idea was simple instead of just building dashboards, I wanted to go one step further and let anyone ask business questions in plain English and get answers backed by real data.

The fictional company is **SalesForce Pro Inc.** which is selling Electronics, Furniture, Software, Clothing and Office Supplies across 5 regions in India.

## What I Built

- Generated a realistic 50,000 row sales dataset with intentional data quality issues
- Cleaned the data using Python — fixed nulls, duplicates, outliers and date errors
- Did a full EDA to find business insights across revenue, categories, regions and segments
- Wrote 10 business SQL queries in PostgreSQL using window functions, CTEs and CASE statements
- Built two ML models — a churn prediction model and a 6 month revenue forecast
- Created a 2 page Power BI dashboard with a dark navy theme
- Built a LangChain + Groq interface that converts plain English to SQL and returns AI generated answers
- Wrapped everything in a Streamlit web app so non-technical stakeholders can use it too

## Tech Stack

Python · PostgreSQL · SQL · LangChain · Groq LLM · Power BI · Streamlit · Scikit-learn · Pandas · Matplotlib

## Power BI Dashboard

### Executive Summary
![Executive Summary](https://github.com/Madhumitha-Y-16/AI-revenue-intelligence-system/blob/main/screenshots/summary.png?raw=true)

### ML Insights
![ML Insights](https://github.com/Madhumitha-Y-16/AI-revenue-intelligence-system/blob/main/screenshots/ml%20insights.png?raw=true)


## AI Revenue Assistant — Streamlit App

Non-technical stakeholders can open this app in a browser and ask questions like "Which region has the lowest sales?" or "Who is the top sales rep?" and get a plain English answer backed by real SQL queries running on the database.

![Question 1](https://github.com/Madhumitha-Y-16/AI-revenue-intelligence-system/blob/main/screenshots/question%201.png?raw=true)

![Question 2](https://github.com/Madhumitha-Y-16/AI-revenue-intelligence-system/blob/main/screenshots/question%202.png?raw=true)

![Question 3](https://github.com/Madhumitha-Y-16/AI-revenue-intelligence-system/blob/main/screenshots/question%203.png?raw=true)

## Key Business Findings

- Revenue grew 3x from ₹168 Cr in 2021 to ₹507 Cr in 2024
- Software has 55% profit margin vs Electronics at 18% — completely different story when you look at profit vs revenue
- Every 5% increase in discount reduces profit by ₹4,000-4,500 per order — the business is over-discounting
- 26.3% of customers have churned — spending pattern is the strongest predictor
- December is consistently the highest revenue month — festive season effect

## Project Files

| File | What it does |
|---|---|
| `01_data_cleaning.ipynb` | Raw data cleaning pipeline |
| `02_eda.ipynb` | Exploratory data analysis |
| `03_sql_setup.ipynb` | PostgreSQL connection and data load |
| `04_ml_models.ipynb` | Churn prediction and revenue forecasting |
| `05_langchain_interface.ipynb` | LangChain + Groq NL interface |
| `app.py` | Streamlit web app |
| `business_queries.sql` | 10 business SQL queries |
| `dashboard.pbix` | Power BI dashboard |

## How to Run

1. Clone this repository
2. Create a `.env` file:
```
GROQ_API_KEY=your-groq-key
POSTGRES_PASSWORD=your-postgres-password
```
3. Install dependencies:
```
pip install pandas numpy scikit-learn sqlalchemy psycopg2-binary langchain langchain-groq streamlit python-dotenv
```
4. Load data into PostgreSQL by running `03_sql_setup.ipynb`
5. Run the Streamlit app:
```
streamlit run app.py
```

## Dataset

I generated this dataset myself using Python to simulate a realistic Indian B2B company. It has 50,000 orders, 8,000 unique customers, 50 sales reps across 5 regions and 4 years of data (2021–2024). I intentionally injected data quality issues including nulls, duplicates, outliers, date errors and formatting inconsistencies to make the cleaning phase realistic.
