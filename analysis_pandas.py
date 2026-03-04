"""
analysis_pandas.py  —  Global Retail Sales: Pandas Deep-Dive
=============================================================
Run AFTER generate_data.py.

Analyses:
  A. Dataset overview & data quality
  B. Descriptive statistics
  C. Time-series aggregations (monthly, quarterly, annual)
  D. Top-N performers (products, regions)
  E. Customer segment profitability
  F. Discount impact analysis
  G. YoY & MoM growth rates
  H. Correlation matrix
  I. Pandas-native bar/line charts saved to pandas_figures/
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

OUT_DIR = 'pandas_figures'
os.makedirs(OUT_DIR, exist_ok=True)
PALETTE = ['#264653', '#2a9d8f', '#e9c46a', '#f4a261', '#e76f51']

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv('retail_sales.csv', parse_dates=['date'])
df['profit_margin'] = (df['profit'] / df['revenue']).round(4)
df['month_period']  = df['date'].dt.to_period('M')

# ─────────────────────────────────────────────────────────────────────────────
# A.  Dataset Overview & Data Quality
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 65)
print("A.  DATASET OVERVIEW")
print("=" * 65)
print(f"Shape         : {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"Date range    : {df['date'].min().date()} → {df['date'].max().date()}")
print(f"Total revenue : ${df['revenue'].sum():,.0f}")
print(f"Total profit  : ${df['profit'].sum():,.0f}")
print(f"Overall margin: {df['profit'].sum()/df['revenue'].sum():.1%}")
print("\nColumn dtypes:")
print(df.dtypes)
print("\nMissing values per column:")
print(df.isnull().sum())
print(f"\nDuplicate rows: {df.duplicated().sum()}")

# ─────────────────────────────────────────────────────────────────────────────
# B.  Descriptive Statistics
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("B.  DESCRIPTIVE STATISTICS")
print("=" * 65)
num_cols = ['unit_price', 'quantity', 'discount', 'revenue', 'profit', 'profit_margin']
desc = df[num_cols].describe().round(2)
print(desc.to_string())

# ─────────────────────────────────────────────────────────────────────────────
# C.  Time-Series Aggregations
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("C.  MONTHLY AGGREGATIONS (last 6 months of data)")
print("=" * 65)
monthly = (df.groupby('month_period')
             .agg(orders=('order_id','count'),
                  revenue=('revenue','sum'),
                  profit=('profit','sum'),
                  avg_margin=('profit_margin','mean'))
             .assign(revenue=lambda x: x['revenue'].round(0),
                     profit=lambda x: x['profit'].round(0),
                     avg_margin=lambda x: (x['avg_margin']*100).round(1)))
monthly.index = monthly.index.astype(str)
print(monthly.tail(6).to_string())

# Save monthly chart
fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
monthly_rev = monthly['revenue'] / 1e3
axes[0].plot(monthly_rev.index, monthly_rev.values, color=PALETTE[0], linewidth=1.8)
axes[0].fill_between(range(len(monthly_rev)), monthly_rev.values, alpha=0.15, color=PALETTE[0])
axes[0].set_ylabel('Revenue (K USD)')
axes[0].set_title('Monthly Revenue & Profit Trend', fontsize=12, fontweight='bold')
axes[0].set_xticks(range(0, len(monthly), 6))
axes[0].set_xticklabels(monthly_rev.index[::6], rotation=45, ha='right', fontsize=7)

monthly_prof = monthly['profit'] / 1e3
axes[1].bar(range(len(monthly_prof)), monthly_prof.values, color=PALETTE[2], alpha=0.85)
axes[1].set_ylabel('Profit (K USD)')
axes[1].set_xticks(range(0, len(monthly_prof), 6))
axes[1].set_xticklabels(monthly_prof.index[::6], rotation=45, ha='right', fontsize=7)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/C_monthly_trend.png', dpi=150)
plt.close()
print("  → Chart saved: C_monthly_trend.png")

# ─────────────────────────────────────────────────────────────────────────────
# D.  Top Performers — Region & Category cross-tab
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("D.  REVENUE BY REGION × CATEGORY (pivot table)")
print("=" * 65)
cross = pd.pivot_table(df, values='revenue', index='region',
                        columns='category', aggfunc='sum').round(0)
cross['TOTAL'] = cross.sum(axis=1)
cross.loc['TOTAL'] = cross.sum()
cross = (cross / 1e3).round(1)   # thousands
print(cross.to_string())
print("(values in USD Thousands)")

# Chart
fig, ax = plt.subplots(figsize=(11, 5))
cross_plot = cross.drop('TOTAL', axis=1).drop('TOTAL', axis=0)
cross_plot.T.plot(kind='bar', ax=ax, color=PALETTE, edgecolor='white', width=0.75)
ax.set_title('Revenue by Region × Category (USD Thousands)', fontsize=12, fontweight='bold')
ax.set_ylabel('Revenue (USD K)')
ax.legend(title='Region', fontsize=8, loc='upper right')
plt.xticks(rotation=20, ha='right', fontsize=9)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/D_region_category_pivot.png', dpi=150)
plt.close()
print("  → Chart saved: D_region_category_pivot.png")

# ─────────────────────────────────────────────────────────────────────────────
# E.  Customer Segment Profitability
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("E.  CUSTOMER SEGMENT PROFITABILITY")
print("=" * 65)
seg = (df.groupby('segment')
         .agg(orders       =('order_id','count'),
              total_revenue =('revenue','sum'),
              total_profit  =('profit','sum'),
              avg_order_val =('revenue','mean'),
              avg_margin    =('profit_margin','mean'))
         .assign(total_revenue =lambda x: x['total_revenue'].round(0),
                 total_profit  =lambda x: x['total_profit'].round(0),
                 avg_order_val =lambda x: x['avg_order_val'].round(2),
                 avg_margin    =lambda x: (x['avg_margin']*100).round(2)))
print(seg.to_string())

fig, axes = plt.subplots(1, 3, figsize=(12, 4.5))
metrics = [('total_revenue', 'Total Revenue ($)', PALETTE[0]),
           ('total_profit',  'Total Profit ($)',  PALETTE[1]),
           ('avg_margin',    'Avg Margin (%)',    PALETTE[2])]
for ax, (col, title, color) in zip(axes, metrics):
    ax.bar(seg.index, seg[col], color=color, edgecolor='white')
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.set_xticklabels(seg.index, rotation=15, ha='right', fontsize=8)
    for spine in ['top','right']: ax.spines[spine].set_visible(False)
plt.suptitle('Customer Segment Profitability Analysis', fontsize=12, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/E_segment_profitability.png', dpi=150, bbox_inches='tight')
plt.close()
print("  → Chart saved: E_segment_profitability.png")

# ─────────────────────────────────────────────────────────────────────────────
# F.  Discount Impact Analysis
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("F.  DISCOUNT IMPACT ON PROFIT MARGIN")
print("=" * 65)
disc_bins = pd.cut(df['discount'], bins=[-0.01, 0, 0.05, 0.10, 0.15, 0.20, 0.25],
                   labels=['0%','1-5%','6-10%','11-15%','16-20%','21-25%'])
disc_analysis = (df.groupby(disc_bins, observed=True)
                   .agg(orders =('order_id','count'),
                        avg_margin =('profit_margin','mean'),
                        total_revenue=('revenue','sum'))
                   .assign(avg_margin=lambda x: (x['avg_margin']*100).round(2),
                           total_revenue=lambda x: (x['total_revenue']/1e3).round(1)))
print(disc_analysis.to_string())

fig, ax = plt.subplots(figsize=(9, 4.5))
colors = [PALETTE[0] if m > 0 else '#e63946' for m in disc_analysis['avg_margin']]
bars = ax.bar(disc_analysis.index.astype(str), disc_analysis['avg_margin'],
              color=colors, edgecolor='white')
ax.axhline(df['profit_margin'].mean() * 100, color='red', linestyle='--',
           linewidth=1.5, label=f"Overall avg: {df['profit_margin'].mean():.1%}")
ax.set_title('Average Profit Margin by Discount Tier', fontsize=12, fontweight='bold')
ax.set_xlabel('Discount Tier'); ax.set_ylabel('Avg Profit Margin (%)')
ax.legend(fontsize=9)
for spine in ['top','right']: ax.spines[spine].set_visible(False)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/F_discount_impact.png', dpi=150)
plt.close()
print("  → Chart saved: F_discount_impact.png")

# Key finding
high_disc = disc_analysis.loc['21-25%','avg_margin']
no_disc   = disc_analysis.loc['0%','avg_margin']
print(f"\n  KEY FINDING: 25% discount reduces avg margin from "
      f"{no_disc:.1f}% → {high_disc:.1f}% "
      f"({(high_disc-no_disc):.1f} pp drop)")

# ─────────────────────────────────────────────────────────────────────────────
# G.  YoY & MoM Growth Rates
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("G.  YEAR-OVER-YEAR GROWTH")
print("=" * 65)
annual = (df.groupby('year')['revenue'].sum() / 1e6).round(2)
yoy    = annual.pct_change().round(4) * 100
growth = pd.DataFrame({'Revenue_M': annual, 'YoY_Growth_%': yoy.round(2)})
print(growth.to_string())

print("\nMONTH-OVER-MONTH GROWTH (last 6 months):")
monthly_rev_raw = df.groupby('month_period')['revenue'].sum()
monthly_rev_raw.index = monthly_rev_raw.index.astype(str)
mom = monthly_rev_raw.pct_change() * 100
mom_df = pd.DataFrame({'Revenue': monthly_rev_raw.round(0),
                        'MoM_%':   mom.round(2)}).tail(6)
print(mom_df.to_string())

# ─────────────────────────────────────────────────────────────────────────────
# H.  Correlation Matrix
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("H.  CORRELATION MATRIX (numeric features)")
print("=" * 65)
corr = df[['unit_price','quantity','discount','revenue','profit','profit_margin']].corr().round(3)
print(corr.to_string())

fig, ax = plt.subplots(figsize=(7, 6))
import matplotlib.colors as mcolors
cmap = plt.get_cmap('RdYlGn')
im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1)
plt.colorbar(im, ax=ax, label='Pearson r')
labels = corr.columns.tolist()
ax.set_xticks(range(len(labels)));  ax.set_xticklabels(labels, rotation=40, ha='right', fontsize=8)
ax.set_yticks(range(len(labels)));  ax.set_yticklabels(labels, fontsize=8)
for i in range(len(labels)):
    for j in range(len(labels)):
        ax.text(j, i, f'{corr.values[i,j]:.2f}', ha='center', va='center',
                fontsize=8, color='black')
ax.set_title('Feature Correlation Matrix', fontsize=12, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/H_correlation_matrix.png', dpi=150)
plt.close()
print("  → Chart saved: H_correlation_matrix.png")

print(f"\n All Pandas analyses complete. Charts saved to ./{OUT_DIR}/")
print("\nKEY INSIGHTS SUMMARY:")
print("─" * 55)
best_region  = df.groupby('region')['revenue'].sum().idxmax()
best_cat     = df.groupby('category')['revenue'].sum().idxmax()
best_channel = df.groupby('channel')['revenue'].sum().idxmax()
best_seg_margin = df.groupby('segment')['profit_margin'].mean().idxmax()
print(f"  • Top revenue region   : {best_region}")
print(f"  • Top revenue category : {best_cat}")
print(f"  • Top sales channel    : {best_channel}")
print(f"  • Best margin segment  : {best_seg_margin}")
print(f"  • Overall profit margin: {df['profit_margin'].mean():.1%}")
print(f"  • Revenue CAGR (21→24) : {((annual.iloc[-1]/annual.iloc[0])**(1/3)-1):.1%}")
