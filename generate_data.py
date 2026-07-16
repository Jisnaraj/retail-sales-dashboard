"""
Generates a realistic synthetic retail sales + inventory dataset
and loads it into a local SQLite database (retail.db).

Run this once before starting the app:
    python generate_data.py
"""

import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

# ---------------------------------------------------------
# 1. Dimension data
# ---------------------------------------------------------
REGIONS = ["North", "South", "East", "West", "Central"]

CATEGORIES = {
    "Electronics": ["Headphones", "Smartphone", "Laptop", "Smartwatch", "Tablet"],
    "Furniture": ["Office Chair", "Desk", "Bookshelf", "Sofa", "Bed Frame"],
    "Apparel": ["T-Shirt", "Jeans", "Jacket", "Sneakers", "Cap"],
    "Groceries": ["Coffee", "Snacks", "Cereal", "Juice", "Pasta"],
    "Home & Kitchen": ["Blender", "Cookware Set", "Vacuum Cleaner", "Lamp", "Toaster"],
}

PRODUCTS = []
pid = 1
for cat, items in CATEGORIES.items():
    for item in items:
        base_price = np.random.uniform(15, 800)
        base_cost = base_price * np.random.uniform(0.45, 0.7)
        PRODUCTS.append({
            "product_id": pid,
            "product_name": item,
            "category": cat,
            "unit_price": round(base_price, 2),
            "unit_cost": round(base_cost, 2),
        })
        pid += 1

products_df = pd.DataFrame(PRODUCTS)

# ---------------------------------------------------------
# 2. Generate daily transactions over 2 years
# ---------------------------------------------------------
start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 12, 31)
date_range = pd.date_range(start_date, end_date, freq="D")

rows = []
order_id = 1

for d in date_range:
    # seasonality: weekends + Nov/Dec holiday boost + slight upward yearly trend
    weekday_factor = 1.3 if d.weekday() >= 5 else 1.0
    month_factor = 1.6 if d.month in (11, 12) else (0.85 if d.month in (1, 2) else 1.0)
    year_trend = 1.0 + (d.year - 2024) * 0.08
    n_orders = int(np.random.poisson(18 * weekday_factor * month_factor * year_trend))

    for _ in range(n_orders):
        product = products_df.sample(1).iloc[0]
        region = np.random.choice(REGIONS, p=[0.25, 0.2, 0.2, 0.2, 0.15])
        qty = np.random.randint(1, 6)
        discount = np.random.choice([0, 0, 0, 0.05, 0.1, 0.15], p=[0.55, 0.1, 0.1, 0.1, 0.1, 0.05])
        unit_price = product["unit_price"]
        revenue = round(qty * unit_price * (1 - discount), 2)
        cost = round(qty * product["unit_cost"], 2)
        profit = round(revenue - cost, 2)

        rows.append({
            "order_id": order_id,
            "order_date": d.strftime("%Y-%m-%d"),
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "category": product["category"],
            "region": region,
            "quantity": qty,
            "unit_price": unit_price,
            "discount": discount,
            "revenue": revenue,
            "cost": cost,
            "profit": profit,
        })
        order_id += 1

# inject a handful of anomalies (revenue spikes/drops) so anomaly detection has something to find
sales_df = pd.DataFrame(rows)

# ---------------------------------------------------------
# 3. Inventory snapshot (current stock levels per product)
# ---------------------------------------------------------
inventory_rows = []
for _, p in products_df.iterrows():
    stock = np.random.randint(0, 250)
    reorder_level = np.random.randint(20, 60)
    inventory_rows.append({
        "product_id": p["product_id"],
        "product_name": p["product_name"],
        "category": p["category"],
        "stock_on_hand": stock,
        "reorder_level": reorder_level,
        "stockout_flag": 1 if stock < reorder_level else 0,
    })
inventory_df = pd.DataFrame(inventory_rows)

# ---------------------------------------------------------
# 4. Write to SQLite
# ---------------------------------------------------------
conn = sqlite3.connect("retail.db")
sales_df.to_sql("fact_sales", conn, if_exists="replace", index=False)
products_df.to_sql("dim_product", conn, if_exists="replace", index=False)
inventory_df.to_sql("dim_inventory", conn, if_exists="replace", index=False)
conn.close()

print(f"Done. {len(sales_df):,} transactions generated across {len(date_range)} days.")
print("Database saved as retail.db")
