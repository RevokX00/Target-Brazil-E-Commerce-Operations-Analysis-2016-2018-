"""
Target Brazil — E-Commerce Operations Analysis
Author: Sadi Jagdish Reddy | Data Analyst
Period: September 2016 – October 2018
Dataset: 8 CSV files | 99,441 orders | 27 states | 4,119 cities
Tools: Python (Pandas, NumPy, Matplotlib, Seaborn), SQL (via Pandas)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings, os, json
warnings.filterwarnings('ignore')

os.makedirs('charts', exist_ok=True)

# ── LOAD ──────────────────────────────────────────────────────────────────────
print("Loading 8 datasets...")
customers = pd.read_csv('data/customers.csv')
orders    = pd.read_csv('data/orders.csv', parse_dates=['order_purchase_timestamp','order_delivered_customer_date','order_estimated_delivery_date'])
payments  = pd.read_csv('data/payments.csv')
products  = pd.read_csv('data/products.csv', encoding='latin-1')
sellers   = pd.read_csv('data/sellers.csv', encoding='latin-1')
items     = pd.read_csv('data/order_items.csv')
reviews   = pd.read_csv('data/reviews.csv', encoding='latin-1')
geo       = pd.read_csv('data/geolocation.csv', encoding='latin-1')

# ── CLEAN ─────────────────────────────────────────────────────────────────────
print("Cleaning data...")
products.rename(columns={'product category': 'product_category_name'}, inplace=True)
geo = geo.drop_duplicates(subset='geolocation_zip_code_prefix', keep='first')

orders['year']      = orders['order_purchase_timestamp'].dt.year
orders['month']     = orders['order_purchase_timestamp'].dt.month
orders['hour']      = orders['order_purchase_timestamp'].dt.hour
orders['yearmonth'] = orders['order_purchase_timestamp'].dt.to_period('M').astype(str)

def tod(h):
    if 0 <= h <= 6:    return 'Dawn'
    elif 7 <= h <= 12: return 'Morning'
    elif 13 <= h <= 18:return 'Afternoon'
    else:              return 'Night'

orders['time_of_day'] = orders['hour'].apply(tod)

orders_clean = orders.dropna(subset=['order_delivered_customer_date']).copy()
orders_clean['time_to_deliver'] = (orders_clean['order_delivered_customer_date'] - orders_clean['order_purchase_timestamp']).dt.days
orders_clean['diff_estimated']  = (orders_clean['order_delivered_customer_date'] - orders_clean['order_estimated_delivery_date']).dt.days

orders_cust  = orders_clean.merge(customers[['customer_id','customer_state']], on='customer_id', how='left')
orders_items = orders_cust.merge(items, on='order_id', how='left')
orders_pay   = orders.merge(payments, on='order_id', how='left')

# ── KPIs ──────────────────────────────────────────────────────────────────────
kpis = {
    'total_orders':     len(orders),
    'total_revenue':    round(payments['payment_value'].sum(), 2),
    'avg_order_value':  round(orders_pay.groupby('order_id')['payment_value'].sum().mean(), 2),
    'total_customers':  customers['customer_unique_id'].nunique(),
    'unique_cities':    customers['customer_city'].nunique(),
    'unique_states':    customers['customer_state'].nunique(),
    'avg_delivery_days':round(orders_clean['time_to_deliver'].mean(), 2),
    'avg_freight':      round(items['freight_value'].mean(), 2),
    'avg_review_score': round(reviews['review_score'].mean(), 4),
    'total_sellers':    sellers['seller_id'].nunique(),
    'total_products':   products['product_id'].nunique(),
}

with open('data/kpis.json', 'w') as f:
    json.dump(kpis, f, indent=2)

print("\nKey Performance Indicators:")
for k, v in kpis.items():
    print(f"  {k:25s}: {v}")

print("\n✅ Analysis complete. Run chart generation separately or view saved kpis.json")
