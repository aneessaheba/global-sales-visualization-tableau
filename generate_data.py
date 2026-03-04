"""
generate_data.py
Generates a synthetic Global Retail Sales dataset (2021-2024).
Run this first — all other scripts depend on retail_sales.csv.
"""
import numpy as np
import pandas as pd

np.random.seed(42)
N = 5000  # number of transactions

regions    = ['North America', 'Europe', 'Asia-Pacific', 'Latin America', 'Middle East & Africa']
categories = ['Electronics', 'Clothing', 'Food & Beverage', 'Home & Garden', 'Sports & Outdoors']
segments   = ['Consumer', 'Corporate', 'Home Office']
channels   = ['Online', 'In-Store', 'Mobile App']

region_weights   = [0.35, 0.28, 0.22, 0.09, 0.06]
category_weights = [0.25, 0.22, 0.20, 0.18, 0.15]

dates = pd.date_range(start='2021-01-01', end='2024-12-31', periods=N)
dates = np.sort(np.random.choice(dates, N, replace=False))

region_col   = np.random.choice(regions,    N, p=region_weights)
category_col = np.random.choice(categories, N, p=category_weights)
segment_col  = np.random.choice(segments,   N)
channel_col  = np.random.choice(channels,   N)

# Base price by category
base_price = {'Electronics': 450, 'Clothing': 80, 'Food & Beverage': 35,
              'Home & Garden': 120, 'Sports & Outdoors': 95}
prices = np.array([base_price[c] * np.random.uniform(0.5, 2.5) for c in category_col])

quantity   = np.random.randint(1, 15, N)
discount   = np.round(np.random.choice([0, 0.05, 0.10, 0.15, 0.20, 0.25], N,
                                        p=[0.40, 0.20, 0.18, 0.12, 0.07, 0.03]), 2)
revenue    = np.round(prices * quantity * (1 - discount), 2)
cost_ratio = np.random.uniform(0.45, 0.75, N)
profit     = np.round(revenue * (1 - cost_ratio), 2)

df = pd.DataFrame({
    'order_id':    [f'ORD-{i:05d}' for i in range(1, N + 1)],
    'date':        pd.to_datetime(dates),
    'region':      region_col,
    'category':    category_col,
    'segment':     segment_col,
    'channel':     channel_col,
    'unit_price':  np.round(prices, 2),
    'quantity':    quantity,
    'discount':    discount,
    'revenue':     revenue,
    'profit':      profit,
})

df['year']  = df['date'].dt.year
df['month'] = df['date'].dt.month
df['quarter'] = df['date'].dt.quarter

df.to_csv('retail_sales.csv', index=False)
print(f"Dataset saved → retail_sales.csv  ({N} rows, {df.shape[1]} columns)")
print(df.dtypes)
print(df.head())
