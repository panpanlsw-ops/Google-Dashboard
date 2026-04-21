# data.py
# ─────────────────────────────────────────────────────────────────────────────
# All data is read from dashboard_data.xlsx
# Upload a new Excel file to GitHub daily to update the dashboard
# Sheets: Tab1_KPI, Tab2_Regional, Tab3_Campaign
# ─────────────────────────────────────────────────────────────────────────────
from datetime import date
import os
import pandas as pd

CAMPAIGNS = {
    "all":     "All campaigns",
    "brand":   "Brand awareness",
    "search":  "Search — HVAC",
    "display": "Display retargeting",
    "local":   "Local services ads",
}

def _excel_path():
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "dashboard_data.xlsx")


# ── Tab 1: KPI Cards ──────────────────────────────────────────────────────────
def get_data(campaign: str) -> dict:
    """Reads today's KPI numbers from Tab1_KPI sheet."""
    df = pd.read_excel(_excel_path(), sheet_name="Tab1_KPI", header=None)
    # Rows 5-10 (0-indexed 4-9): Invoca, Form, CRM Leads, Appointments, Customers, Date
    invoca = int(df.iloc[4, 1])
    form   = int(df.iloc[5, 1])
    leads  = int(df.iloc[6, 1])
    apt    = int(df.iloc[7, 1])
    cust   = int(df.iloc[8, 1])
    return dict(
        conversions=0, invoca=invoca, form=form, cost=0,
        leads=leads, crm_invoca=invoca, crm_form=form,
        appointments=apt, customers=cust,
    )


# ── Tab 1: ROI Charts (MTD & Comparison) ─────────────────────────────────────
def get_roi_data(campaign: str, start_date: date, end_date: date) -> dict:
    """
    Reads campaign monthly trend from Tab3_Campaign sheet.
    Returns this year vs last year data for MTD charts.
    """
    df = pd.read_excel(_excel_path(), sheet_name="Tab3_Campaign", header=0)
    df.columns = ["campaign","year","month","clicks","cost","conv",
                  "leads","apt","cust","sales","roi"]

    today = date.today()
    cur_month = today.strftime("%b")
    cur_year  = today.year
    last_year = cur_year - 1

    def get_row(camp_filter, yr, mo):
        rows = df
        if camp_filter != "all":
            # map campaign key to partial name match
            camp_map = {
                "brand":   "LifeSource Brand",
                "search":  "Pasadena Single Form",
                "display": "Orange County",
                "local":   "Las Vegas",
            }
            keyword = camp_map.get(camp_filter, "")
            rows = df[df["campaign"].str.contains(keyword, case=False, na=False)]
        rows = rows[(rows["year"] == yr) & (rows["month"] == mo)]
        if rows.empty:
            return dict(conversions=0, cost=0, leads=0, appointments=0,
                       customers=0, cost_per_lead=0, cost_per_appointment=0, roi=0)
        r = rows.iloc[0]
        leads = int(r.get("leads", 0))
        apt   = int(r.get("apt", 0))
        cost  = float(r.get("cost", 0))
        return dict(
            conversions=int(r.get("conv", 0)),
            cost=int(cost),
            leads=leads,
            appointments=apt,
            customers=int(r.get("cust", 0)),
            cost_per_lead=round(cost/leads) if leads > 0 else 0,
            cost_per_appointment=round(cost/apt) if apt > 0 else 0,
            roi=float(r.get("roi", 0)),
        )

    ty = get_row(campaign, cur_year,  cur_month)
    ly = get_row(campaign, last_year, cur_month)

    # Build monthly trend arrays Jan → current month
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    months_so_far = months[:today.month]

    def build_trend(yr):
        result = {f: [] for f in ["conversions","cost","leads","appointments",
                                   "customers","cost_per_lead","cost_per_appointment","roi"]}
        for mo in months_so_far:
            row = get_row(campaign, yr, mo)
            for f in result:
                result[f].append(row[f])
        return result

    # Build daily arrays for single campaign view (approximate from monthly total)
    days = (end_date - start_date).days + 1
    def daily_from_total(total, n):
        import math
        if n == 0: return []
        base = total / n
        return [max(0, round(base * (0.7 + 0.6 * math.sin(i/max(n,1) * math.pi)))) for i in range(n)]

    ty_daily = {f: daily_from_total(ty[f], days) for f in ty}
    ly_daily = {f: daily_from_total(ly[f], days) for f in ly}

    return dict(
        ty=ty, ly=ly,
        ty_trend=build_trend(cur_year),
        ly_trend=build_trend(last_year),
        ty_daily=ty_daily,
        ly_daily=ly_daily,
    )


# ── Tab 2: Regional Offices ───────────────────────────────────────────────────
def get_regional_data(start_date: date, end_date: date) -> list:
    """Reads regional office data from Tab2_Regional sheet."""
    df = pd.read_excel(_excel_path(), sheet_name="Tab2_Regional", header=0)
    df.columns = ["name","ul","nl","apt","quote","cust","sales","nlc","nl_sales"]
    df = df.dropna(subset=["name"])
    result = []
    def safe_int(val):
        try:
            return int(float(val)) if val is not None and str(val).strip() != "" else 0
        except:
            return 0

    def safe_float(val):
        try:
            return float(val) if val is not None and str(val).strip() != "" else 0.0
        except:
            return 0.0

    for _, row in df.iterrows():
        result.append(dict(
            name=str(row["name"]),
            ul=safe_int(row.get("ul", 0)),
            nl=safe_int(row.get("nl", 0)),
            apt=safe_int(row.get("apt", 0)),
            quote=safe_int(row.get("quote", 0)),
            cust=safe_int(row.get("cust", 0)),
            sales=safe_float(row.get("sales", 0)),
            nlc=safe_int(row.get("nlc", 0)),
            nl_sales=safe_float(row.get("nl_sales", 0)),
        ))
    return result


# ── Tab 3: Campaign Performance ───────────────────────────────────────────────
def get_campaign_data() -> list:
    """Reads campaign data from Tab3_Campaign sheet and builds monthly trend."""
    df = pd.read_excel(_excel_path(), sheet_name="Tab3_Campaign", header=0)
    df.columns = ["campaign","year","month","clicks","cost","conv",
                  "leads","apt","cust","sales","roi"]

    MONTH_MAP = {"Jan":0,"Feb":1,"Mar":2,"Apr":3,"May":4,"Jun":5,
                 "Jul":6,"Aug":7,"Sep":8,"Oct":9,"Nov":10,"Dec":11}

    campaigns = df["campaign"].dropna().unique().tolist()
    result = []

    def sv(val):
        try:
            v = float(val)
            return 0.0 if pd.isna(v) else v
        except:
            return 0.0

    for camp in campaigns:
        rows = df[df["campaign"] == camp]
        trend = {}
        for _, row in rows.iterrows():
            try:
                yr = int(float(row["year"]))
            except:
                continue
            mo  = str(row["month"]).strip()
            idx = MONTH_MAP.get(mo, 0)
            if yr not in trend:
                trend[yr] = {f: [0]*12 for f in
                             ["clicks","cost","conv","leads","apt","cust","sales","roi"]}
            for f in ["clicks","cost","conv","leads","apt","cust","sales","roi"]:
                trend[yr][f][idx] = sv(row.get(f, 0))
        result.append(dict(name=camp, trend=trend))

    return result
