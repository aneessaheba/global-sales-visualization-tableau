"""
analysis_tableau.py  —  Global Retail Sales: Tableau-Ready Data Export
=======================================================================
Run AFTER generate_data.py.

Tableau is a desktop BI tool — this script prepares the pre-aggregated
CSV files that feed each Tableau dashboard view, and prints step-by-step
connection instructions.

Exports to tableau_exports/:
  1. retail_sales_full.csv          ← raw data (Tableau Live Connection)
  2. monthly_kpis.csv               ← KPI trend sheet
  3. region_category_matrix.csv     ← geo × product heat-map
  4. segment_channel_summary.csv    ← customer analysis
  5. discount_margin_scatter.csv    ← scatter / dual-axis chart
"""

import os
import pandas as pd
import numpy as np

OUT = 'tableau_exports'
os.makedirs(OUT, exist_ok=True)

# ── Load raw data ─────────────────────────────────────────────────────────────
df = pd.read_csv('retail_sales.csv', parse_dates=['date'])
df['profit_margin'] = (df['profit'] / df['revenue']).round(4)

# ─────────────────────────────────────────────────────────────────────────────
# Export 1: Full dataset (Tableau Live Connection source)
# ─────────────────────────────────────────────────────────────────────────────
df.to_csv(f'{OUT}/retail_sales_full.csv', index=False)
print(f"[1] retail_sales_full.csv  ({df.shape[0]} rows)")

# ─────────────────────────────────────────────────────────────────────────────
# Export 2: Monthly KPIs
# ─────────────────────────────────────────────────────────────────────────────
monthly = (df.groupby(['year', 'month'])
             .agg(orders        =('order_id','count'),
                  revenue       =('revenue','sum'),
                  profit        =('profit','sum'),
                  avg_discount  =('discount','mean'),
                  avg_margin    =('profit_margin','mean'))
             .reset_index()
             .assign(revenue    =lambda x: x['revenue'].round(2),
                     profit     =lambda x: x['profit'].round(2),
                     avg_discount=lambda x: (x['avg_discount']*100).round(2),
                     avg_margin =lambda x: (x['avg_margin']*100).round(2)))
monthly['date_label'] = pd.to_datetime(
    monthly['year'].astype(str) + '-' + monthly['month'].astype(str).str.zfill(2) + '-01')
monthly['mom_revenue_pct'] = (monthly['revenue'].pct_change() * 100).round(2)
monthly.to_csv(f'{OUT}/monthly_kpis.csv', index=False)
print(f"[2] monthly_kpis.csv  ({monthly.shape[0]} rows)")

# ─────────────────────────────────────────────────────────────────────────────
# Export 3: Region × Category matrix (Tableau heat-map / treemap)
# ─────────────────────────────────────────────────────────────────────────────
matrix = (df.groupby(['region', 'category', 'year'])
            .agg(revenue=('revenue','sum'),
                 profit =('profit','sum'),
                 orders =('order_id','count'))
            .reset_index()
            .assign(revenue=lambda x: x['revenue'].round(2),
                    profit =lambda x: x['profit'].round(2),
                    margin =lambda x: (x['profit']/x['revenue']*100).round(2)))
matrix.to_csv(f'{OUT}/region_category_matrix.csv', index=False)
print(f"[3] region_category_matrix.csv  ({matrix.shape[0]} rows)")

# ─────────────────────────────────────────────────────────────────────────────
# Export 4: Segment × Channel summary
# ─────────────────────────────────────────────────────────────────────────────
seg_ch = (df.groupby(['segment', 'channel', 'year'])
            .agg(orders        =('order_id','count'),
                 revenue       =('revenue','sum'),
                 profit        =('profit','sum'),
                 avg_order_val =('revenue','mean'))
            .reset_index()
            .assign(revenue      =lambda x: x['revenue'].round(2),
                    profit       =lambda x: x['profit'].round(2),
                    avg_order_val=lambda x: x['avg_order_val'].round(2),
                    margin_pct   =lambda x: (x['profit']/x['revenue']*100).round(2)))
seg_ch.to_csv(f'{OUT}/segment_channel_summary.csv', index=False)
print(f"[4] segment_channel_summary.csv  ({seg_ch.shape[0]} rows)")

# ─────────────────────────────────────────────────────────────────────────────
# Export 5: Discount vs Margin scatter (individual orders, sampled for perf)
# ─────────────────────────────────────────────────────────────────────────────
scatter = (df[['order_id','date','region','category','segment','channel',
               'unit_price','quantity','discount','revenue','profit','profit_margin']]
            .sample(2000, random_state=42)
            .reset_index(drop=True))
scatter['discount_pct']   = (scatter['discount'] * 100).round(1)
scatter['margin_pct']     = (scatter['profit_margin'] * 100).round(2)
scatter.to_csv(f'{OUT}/discount_margin_scatter.csv', index=False)
print(f"[5] discount_margin_scatter.csv  ({scatter.shape[0]} rows)")

# ─────────────────────────────────────────────────────────────────────────────
# Print Tableau connection guide
# ─────────────────────────────────────────────────────────────────────────────
guide = """
╔══════════════════════════════════════════════════════════════════╗
║          TABLEAU DESKTOP — STEP-BY-STEP CONNECTION GUIDE         ║
╚══════════════════════════════════════════════════════════════════╝

STEP 1 ─ Connect to Data
  • Open Tableau Desktop → "Connect" → "Text File"
  • Browse to:  tableau_exports/retail_sales_full.csv
  • Tableau auto-detects column types; verify:
      date          → Date
      revenue/profit → Number (decimal)
      year/month    → Number (whole)

STEP 2 ─ Recommended Dashboard Sheets
┌─────┬──────────────────────────────┬────────────────────────────────────┐
│  #  │  Sheet Name                  │  Tableau Chart Type                │
├─────┼──────────────────────────────┼────────────────────────────────────┤
│  1  │ Revenue Over Time            │ Line chart: Date → SUM(Revenue)    │
│  2  │ Revenue by Region            │ Map / Horizontal Bar               │
│  3  │ Category Treemap             │ Treemap: size=Revenue,color=Margin │
│  4  │ Discount vs Profit Scatter   │ Scatter: Discount% vs Margin%      │
│  5  │ Segment Profitability        │ Bar chart grouped by Segment       │
│  6  │ Channel Performance          │ Stacked bar: Channel × Region      │
│  7  │ Monthly KPI Dashboard        │ KPI tiles + dual-axis line         │
│  8  │ YoY Growth                   │ Bar-in-bar or line with reference  │
└─────┴──────────────────────────────┴────────────────────────────────────┘

STEP 3 ─ Calculated Fields to create in Tableau
  • Profit Margin %  :  SUM([Profit]) / SUM([Revenue])
  • Revenue (M)      :  SUM([Revenue]) / 1000000
  • Discount Tier    :  IF [Discount]=0 THEN '0%'
                        ELSEIF [Discount]<=0.05 THEN '1-5%'
                        ELSEIF [Discount]<=0.10 THEN '6-10%'
                        ELSEIF [Discount]<=0.15 THEN '11-15%'
                        ELSEIF [Discount]<=0.20 THEN '16-20%'
                        ELSE '21-25%' END

STEP 4 ─ Filters & Parameters to add
  • Date Range Filter : drag [Date] to Filters pane → Range
  • Region Filter     : drag [Region] to Filters
  • Category Filter   : drag [Category] to Filters
  • Year parameter    : Integer, range 2021–2024, for YoY comparison

STEP 5 ─ Build a Story
  1. Sheet 1: Revenue KPI overview
  2. Sheet 2: Geographic breakdown (map or bar)
  3. Sheet 3: Category & segment deep-dive
  4. Sheet 4: Discount impact analysis
  Combine into a Dashboard → Story for executive presentation.

KEY FINDINGS TO HIGHLIGHT IN TABLEAU:
  ✦ North America drives the largest share of revenue
  ✦ Electronics is the highest-revenue category
  ✦ Higher discounts correlate with lower profit margins
  ✦ Online channel revenue has grown YoY
  ✦ Corporate segment shows strongest profit margins
"""
print(guide)

# Save guide as text file
with open(f'{OUT}/TABLEAU_GUIDE.txt', 'w') as f:
    f.write(guide)
print(f"Guide saved → {OUT}/TABLEAU_GUIDE.txt")
