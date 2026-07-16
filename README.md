# 📊 Retail Sales & Inventory Intelligence Dashboard

An interactive web app for retail business reporting — KPIs, trend analysis,
category/region breakdowns, revenue forecasting, and inventory risk tracking,
all backed by a SQL database.

Built to demonstrate: dashboard development, SQL-based data modeling,
data-driven business insights, trend/anomaly detection, and forecasting.

---

## Features

| Area | What it does |
|---|---|
| **KPIs** | Total revenue, total profit, profit margin, average order value, units sold, period-over-period % change |
| **Filters** | Date range, region, product category |
| **Trends** | Daily revenue & profit line chart |
| **Anomaly Detection** | Z-score based flagging of unusual revenue days |
| **Breakdown** | Revenue by category (treemap), by region (bar chart), top 10 products |
| **Forecasting** | Holt-Winters exponential smoothing to project revenue 7–90 days ahead |
| **Inventory** | Stock-on-hand vs reorder level, stockout rate, at-risk product list |

---

## Tech Stack

- **Frontend/App framework:** Streamlit
- **Database:** SQLite (`retail.db`) — easily swappable for PostgreSQL/MySQL
- **Data processing:** Pandas, NumPy
- **Visualization:** Plotly
- **Forecasting:** statsmodels (Holt-Winters Exponential Smoothing)

---

## Project Structure

```
retail-dashboard/
├── generate_data.py     # Creates synthetic retail data + loads it into SQLite
├── app.py                # The Streamlit dashboard application
├── requirements.txt       # Python dependencies
├── retail.db              # SQLite database (generated after running generate_data.py)
└── README.md
```

### Data Model (SQLite tables)

**`fact_sales`** — one row per line-item transaction
| column | description |
|---|---|
| order_id | unique order identifier |
| order_date | date of the transaction |
| product_id / product_name / category | product dimension |
| region | sales region |
| quantity, unit_price, discount | order details |
| revenue, cost, profit | calculated financials |

**`dim_product`** — product catalog (id, name, category, unit price/cost)

**`dim_inventory`** — current stock snapshot (stock_on_hand, reorder_level, stockout_flag)

This is a simplified star schema — `fact_sales` is the fact table, `dim_product`
and `dim_inventory` are dimension/reference tables. In a production setting you'd
add `dim_date` and `dim_region` tables and use foreign keys.

---

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate the dataset
This creates `retail.db` with ~16,000 synthetic but realistic transactions
across 2 years, 5 regions, 5 categories and 25 products.
```bash
python generate_data.py
```

### 3. Launch the app
```bash
streamlit run app.py
```
Then open the URL Streamlit prints (typically `http://localhost:8501`).

---

## Using Your Own Data

To connect this to real data instead of the synthetic generator:

1. Replace the contents of `generate_data.py`'s data-generation section with a
   load of your own CSV/Excel file (e.g. Kaggle's Superstore or Olist datasets
   work as drop-in replacements — just map their columns to the schema above).
2. Keep the same table names (`fact_sales`, `dim_product`, `dim_inventory`) or
   update the `pd.read_sql(...)` calls in `app.py` to match your schema.
3. For a production database (PostgreSQL/MySQL), swap
   `sqlite3.connect("retail.db")` for a SQLAlchemy engine, e.g.:
   ```python
   from sqlalchemy import create_engine
   engine = create_engine("postgresql://user:password@host:5432/retail_db")
   ```

---

## Possible Extensions

- **Natural-language querying:** add a text box where a user asks a question
  ("top 5 products in the South region last quarter") and an LLM (Claude/OpenAI
  API) translates it into a SQL query against `retail.db`, executed read-only.
- **Power BI / Tableau companion:** connect either tool directly to `retail.db`
  (or the CSV export) to rebuild the same KPIs as a BI report, to demonstrate
  BI-tool proficiency alongside the custom web app.
- **Deployment:** push to GitHub and deploy free on
  [Streamlit Community Cloud](https://streamlit.io/cloud) for a live demo link.
- **Auth & multi-tenant data:** add `streamlit-authenticator` if this needs to
  be shared with multiple stakeholders with different data access levels.

---

## Notes on the Data

All data in this project is **synthetically generated** (`generate_data.py`,
seeded with `np.random.seed(42)` for reproducibility) — there is no real
company or customer data involved. This makes the project safe to share
publicly (e.g., on GitHub, in a portfolio) while still demonstrating realistic
seasonality, trends, and anomalies.
