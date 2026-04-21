# Daily Report Dashboard

Live marketing dashboard built with Streamlit.

## Files

| File | Purpose |
|---|---|
| `app.py` | Dashboard UI — 3 tabs |
| `data.py` | Data layer — reads from Excel |
| `dashboard_data.xlsx` | Your daily data — update this file |
| `requirements.txt` | Python packages |

## How to update daily

1. Open `dashboard_data.xlsx`
2. Update these sheets with your notebook results:
   - **Tab1_KPI** → All campaigns KPI numbers
   - **Tab1_Brand / Tab1_Search / Tab1_Display / Tab1_Local** → Per campaign KPIs
   - **Tab1_MTD** → MTD comparison per campaign
   - **Tab2_Regional** → Regional office data
   - **Tab3_Campaign** → Campaign monthly data
3. Delete old `dashboard_data.xlsx` from GitHub
4. Upload new file → dashboard updates in ~1 min

## Excel color guide

| Color | Meaning |
|---|---|
| 🟡 Yellow | This Year (TY) — update daily |
| 🔵 Blue | Last Year MTD — update daily |
| 🟢 Green | Last Year Full Month — update monthly |
| 🟣 Purple | Budget — update monthly |

## Tabs

- **Tab 1 — Today**: KPI cards + MTD & Comparison charts
- **Tab 2 — Regional Offices**: Office performance table + pie charts
- **Tab 3 — Campaign Performance**: Campaign table + monthly trend chart
