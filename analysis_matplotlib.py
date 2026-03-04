"""
analysis_matplotlib.py  —  Global Retail Sales: Matplotlib Visualizations
==========================================================================
Run AFTER generate_data.py.

Charts produced (saved to matplotlib_figures/):
  1. Annual Revenue Trend (line chart)
  2. Revenue by Region (horizontal bar)
  3. Category Revenue Share (pie chart)
  4. Monthly Revenue Heatmap (2021-2024)
  5. Profit Margin Distribution by Category (box plot)
  6. Channel × Region Revenue (stacked bar)
  7. Discount vs Profit Scatter (colored by category)
  8. Quarterly Revenue Growth YoY (grouped bar)
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')           # non-interactive backend — no display needed
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.patches import FancyBboxPatch

# ── Config ───────────────────────────────────────────────────────────────────
OUT_DIR  = 'matplotlib_figures'
PALETTE  = ['#264653', '#2a9d8f', '#e9c46a', '#f4a261', '#e76f51']
FONT_SM, FONT_MD, FONT_LG = 9, 11, 14

os.makedirs(OUT_DIR, exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'figure.dpi': 150,
                     'axes.spines.top': False, 'axes.spines.right': False})

# ── Load data ─────────────────────────────────────────────────────────────────
df = pd.read_csv('retail_sales.csv', parse_dates=['date'])
df['profit_margin'] = df['profit'] / df['revenue']
categories = df['category'].unique()
regions    = df['region'].unique()

# ─────────────────────────────────────────────────────────────────────────────
# 1.  Annual Revenue Trend
# ─────────────────────────────────────────────────────────────────────────────
annual = df.groupby('year')['revenue'].sum() / 1e6   # millions

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(annual.index, annual.values, marker='o', linewidth=2.5,
        markersize=9, color=PALETTE[0])
for yr, rev in annual.items():
    ax.annotate(f'${rev:.1f}M', (yr, rev), textcoords='offset points',
                xytext=(0, 10), ha='center', fontsize=FONT_SM, color=PALETTE[0])
ax.fill_between(annual.index, annual.values, alpha=0.15, color=PALETTE[0])
ax.set_title('Annual Revenue Trend (2021–2024)', fontsize=FONT_LG, fontweight='bold', pad=12)
ax.set_xlabel('Year');  ax.set_ylabel('Revenue (USD Millions)')
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:.0f}M'))
ax.set_xticks(annual.index)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/01_annual_revenue_trend.png')
plt.close()
print("✓  Chart 1 saved")

# ─────────────────────────────────────────────────────────────────────────────
# 2.  Revenue by Region (horizontal bar)
# ─────────────────────────────────────────────────────────────────────────────
region_rev = (df.groupby('region')['revenue'].sum() / 1e6).sort_values()

fig, ax = plt.subplots(figsize=(8, 4.5))
bars = ax.barh(region_rev.index, region_rev.values, color=PALETTE, edgecolor='white')
for bar, val in zip(bars, region_rev.values):
    ax.text(val + 0.5, bar.get_y() + bar.get_height() / 2,
            f'${val:.1f}M', va='center', fontsize=FONT_SM)
ax.set_title('Total Revenue by Region (2021–2024)', fontsize=FONT_LG, fontweight='bold', pad=12)
ax.set_xlabel('Revenue (USD Millions)')
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:.0f}M'))
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/02_revenue_by_region.png')
plt.close()
print("✓  Chart 2 saved")

# ─────────────────────────────────────────────────────────────────────────────
# 3.  Category Revenue Share (pie)
# ─────────────────────────────────────────────────────────────────────────────
cat_rev = df.groupby('category')['revenue'].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(7, 7))
wedges, texts, autotexts = ax.pie(
    cat_rev.values, labels=cat_rev.index, autopct='%1.1f%%',
    colors=PALETTE, startangle=140, pctdistance=0.75,
    wedgeprops={'edgecolor': 'white', 'linewidth': 2})
for t in autotexts: t.set_fontsize(FONT_SM); t.set_fontweight('bold')
ax.set_title('Revenue Share by Product Category', fontsize=FONT_LG, fontweight='bold', pad=16)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/03_category_revenue_share.png')
plt.close()
print("✓  Chart 3 saved")

# ─────────────────────────────────────────────────────────────────────────────
# 4.  Monthly Revenue Heatmap
# ─────────────────────────────────────────────────────────────────────────────
pivot = df.pivot_table(values='revenue', index='year', columns='month',
                        aggfunc='sum') / 1e3   # thousands

fig, ax = plt.subplots(figsize=(12, 4))
im = ax.imshow(pivot.values, cmap='YlOrRd', aspect='auto')
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Revenue (USD Thousands)', fontsize=FONT_SM)

month_labels = ['Jan','Feb','Mar','Apr','May','Jun',
                'Jul','Aug','Sep','Oct','Nov','Dec']
ax.set_xticks(range(12));  ax.set_xticklabels(month_labels, fontsize=FONT_SM)
ax.set_yticks(range(len(pivot.index)));  ax.set_yticklabels(pivot.index)
ax.set_title('Monthly Revenue Heatmap (USD Thousands)', fontsize=FONT_LG, fontweight='bold', pad=12)

for i in range(len(pivot.index)):
    for j in range(12):
        val = pivot.values[i, j]
        ax.text(j, i, f'${val:.0f}K', ha='center', va='center',
                fontsize=7, color='black' if val < pivot.values.max() * 0.6 else 'white')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/04_monthly_revenue_heatmap.png')
plt.close()
print("✓  Chart 4 saved")

# ─────────────────────────────────────────────────────────────────────────────
# 5.  Profit Margin Distribution by Category (box plot)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
data_by_cat = [df[df['category'] == c]['profit_margin'].values
               for c in cat_rev.index]
bp = ax.boxplot(data_by_cat, patch_artist=True, notch=True,
                medianprops={'color': 'white', 'linewidth': 2})
for patch, color in zip(bp['boxes'], PALETTE):
    patch.set_facecolor(color);  patch.set_alpha(0.85)
ax.set_xticklabels(cat_rev.index, fontsize=FONT_SM)
ax.set_title('Profit Margin Distribution by Category', fontsize=FONT_LG, fontweight='bold', pad=12)
ax.set_ylabel('Profit Margin')
ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/05_profit_margin_boxplot.png')
plt.close()
print("✓  Chart 5 saved")

# ─────────────────────────────────────────────────────────────────────────────
# 6.  Channel × Region Revenue (stacked bar)
# ─────────────────────────────────────────────────────────────────────────────
ch_reg = df.pivot_table(values='revenue', index='region',
                         columns='channel', aggfunc='sum') / 1e6
ch_reg = ch_reg.sort_values(ch_reg.columns[0], ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
bottom = np.zeros(len(ch_reg))
ch_colors = ['#264653', '#2a9d8f', '#e9c46a']
for col, color in zip(ch_reg.columns, ch_colors):
    ax.bar(ch_reg.index, ch_reg[col], bottom=bottom, label=col,
           color=color, edgecolor='white', width=0.6)
    bottom += ch_reg[col].values
ax.set_title('Revenue by Region & Sales Channel', fontsize=FONT_LG, fontweight='bold', pad=12)
ax.set_ylabel('Revenue (USD Millions)')
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:.0f}M'))
ax.legend(title='Channel', fontsize=FONT_SM)
plt.xticks(rotation=15, ha='right', fontsize=FONT_SM)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/06_channel_region_stacked.png')
plt.close()
print("✓  Chart 6 saved")

# ─────────────────────────────────────────────────────────────────────────────
# 7.  Discount vs Profit Scatter
# ─────────────────────────────────────────────────────────────────────────────
cat_color_map = {c: PALETTE[i] for i, c in enumerate(categories)}
sample = df.sample(800, random_state=1)

fig, ax = plt.subplots(figsize=(9, 5.5))
for cat in categories:
    sub = sample[sample['category'] == cat]
    ax.scatter(sub['discount'], sub['profit_margin'],
               c=cat_color_map[cat], alpha=0.55, s=35, label=cat, edgecolors='none')
# Trend line (all data)
z = np.polyfit(sample['discount'], sample['profit_margin'], 1)
p = np.poly1d(z)
xs = np.linspace(0, 0.25, 100)
ax.plot(xs, p(xs), color='#e63946', linewidth=2, linestyle='--', label='Trend')
ax.set_title('Discount Rate vs Profit Margin', fontsize=FONT_LG, fontweight='bold', pad=12)
ax.set_xlabel('Discount Rate');  ax.set_ylabel('Profit Margin')
ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
ax.legend(fontsize=FONT_SM, ncol=2)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/07_discount_vs_profit_scatter.png')
plt.close()
print("✓  Chart 7 saved")

# ─────────────────────────────────────────────────────────────────────────────
# 8.  Quarterly Revenue Growth YoY (grouped bar)
# ─────────────────────────────────────────────────────────────────────────────
qtr = df.groupby(['year', 'quarter'])['revenue'].sum() / 1e6
qtr = qtr.unstack('year')

x = np.arange(4)
width = 0.2
years = qtr.columns.tolist()
fig, ax = plt.subplots(figsize=(10, 5))
for i, (yr, color) in enumerate(zip(years, PALETTE)):
    offset = (i - len(years) / 2 + 0.5) * width
    bars = ax.bar(x + offset, qtr[yr], width, label=str(yr), color=color, alpha=0.9)
ax.set_title('Quarterly Revenue by Year (YoY Comparison)', fontsize=FONT_LG, fontweight='bold', pad=12)
ax.set_xticks(x);  ax.set_xticklabels([f'Q{q}' for q in range(1, 5)])
ax.set_ylabel('Revenue (USD Millions)')
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:.0f}M'))
ax.legend(title='Year', fontsize=FONT_SM)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/08_quarterly_yoy_grouped.png')
plt.close()
print("✓  Chart 8 saved")

print(f"\n All 8 charts saved to ./{OUT_DIR}/")
