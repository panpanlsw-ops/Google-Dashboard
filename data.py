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
    """
    Reads KPI numbers from Tab1_KPI sheet.
    Rows (0-indexed from row 5):
      4=Conversions, 5=Cost, 6=Invoca, 7=Form, 8=CRM Leads,
      9=Appointments, 10=Customers, 11=CPL, 12=CPA, 13=ROI
    Cols: 1=TY, 2=LY MTD, 3=LY Full, 4=Budget
    """
    df = pd.read_excel(_excel_path(), sheet_name="Tab1_KPI", header=None)

    def sv(idx, col):
        try:
            v = df.iloc[idx, col]
            if v is None or str(v).strip() in ["", "nan", "None"]: return 0
            return float(v)
        except:
            return 0

    return dict(
        conversions=int(sv(4,1)),
        cost=sv(5,1),
        budget=sv(5,4),
        invoca=int(sv(6,1)),
        form=int(sv(7,1)),
        leads=int(sv(8,1)),
        crm_invoca=int(sv(6,1)),
        crm_form=int(sv(7,1)),
        appointments=int(sv(9,1)),
        customers=int(sv(10,1)),
        cost_per_lead=sv(11,1),
        cost_per_apt=sv(12,1),
        roi=sv(13,1),
        ly_mtd=dict(
            conversions=int(sv(4,2)),
            cost=sv(5,2),
            leads=int(sv(8,2)),
            appointments=int(sv(9,2)),
            customers=int(sv(10,2)),
            cost_per_lead=sv(11,2),
            cost_per_apt=sv(12,2),
            roi=sv(13,2),
        ),
        ly_full=dict(
            conversions=int(sv(4,3)),
            cost=sv(5,3),
            leads=int(sv(8,3)),
            appointments=int(sv(9,3)),
            customers=int(sv(10,3)),
            cost_per_lead=sv(11,3),
            cost_per_apt=sv(12,3),
            roi=sv(13,3),
        ),
    )


# ── Tab 1: ROI Charts (MTD & Comparison) ─────────────────────────────────────
def get_roi_data(campaign: str, start_date: date, end_date: date) -> dict:
    """
    Reads MTD comparison data from Tab1_MTD sheet.
    Columns: Campaign, TY Leads, TY Apt, TY Cust, TY CPL, TY CPA, TY ROI,
                       LY Leads, LY Apt, LY Cust, LY CPL, LY CPA, LY ROI
    """
    df = pd.read_excel(_excel_path(), sheet_name="Tab1_MTD", header=4)
    df.columns = [
        "campaign",
        "ty_leads","ty_apt","ty_cust","ty_cpl","ty_cpa","ty_roi",
        "ly_leads","ly_apt","ly_cust","ly_cpl","ly_cpa","ly_roi",
    ]
    df = df.dropna(subset=["campaign"])
    df = df[~df["campaign"].astype(str).str.contains("yellow|blue|legend", case=False, na=False)]

    def sv(val):
        try:
            v = float(val)
            return 0.0 if (v != v) else v
        except:
            return 0.0

    def get_row(camp_key):
        if camp_key == "all":
            rows = df[df["campaign"].astype(str).str.lower().str.contains("all campaign", na=False)]
        else:
            camp_map = {
                "brand":   "LifeSource Brand",
                "search":  "Pasadena Single Form",
                "display": "Orange County",
                "local":   "Las Vegas",
            }
            keyword = camp_map.get(camp_key, "")
            rows = df[df["campaign"].astype(str).str.contains(keyword, case=False, na=False)]

        if rows.empty:
            return None
        r = rows.iloc[0]
        return r

    # Build ty/ly dicts for all campaigns (for bar charts)
    camp_keys  = list(CAMPAIGNS.keys())
    camp_names = list(CAMPAIGNS.values())

    def series_all(field_ty, field_ly):
        ty_vals, ly_vals = [], []
        for key in camp_keys:
            r = get_row(key)
            if r is not None:
                ty_vals.append(sv(r.get(field_ty, 0)))
                ly_vals.append(sv(r.get(field_ly, 0)))
            else:
                ty_vals.append(0)
                ly_vals.append(0)
        return ty_vals, ly_vals

    leads_ty,  leads_ly  = series_all("ty_leads", "ly_leads")
    apt_ty,    apt_ly    = series_all("ty_apt",   "ly_apt")
    cust_ty,   cust_ly   = series_all("ty_cust",  "ly_cust")
    cpl_ty,    cpl_ly    = series_all("ty_cpl",   "ly_cpl")
    cpa_ty,    cpa_ly    = series_all("ty_cpa",   "ly_cpa")
    roi_ty,    roi_ly    = series_all("ty_roi",   "ly_roi")

    # Single campaign row for ty/ly totals
    r = get_row(campaign)
    if r is not None:
        ty = dict(conversions=0, cost=0, leads=sv(r["ty_leads"]),
                  appointments=sv(r["ty_apt"]), customers=sv(r["ty_cust"]),
                  cost_per_lead=sv(r["ty_cpl"]), cost_per_appointment=sv(r["ty_cpa"]),
                  roi=sv(r["ty_roi"]))
        ly = dict(conversions=0, cost=0, leads=sv(r["ly_leads"]),
                  appointments=sv(r["ly_apt"]), customers=sv(r["ly_cust"]),
                  cost_per_lead=sv(r["ly_cpl"]), cost_per_appointment=sv(r["ly_cpa"]),
                  roi=sv(r["ly_roi"]))
    else:
        ty = ly = dict(conversions=0, cost=0, leads=0, appointments=0,
                       customers=0, cost_per_lead=0, cost_per_appointment=0, roi=0)

    # Daily arrays (approximate from totals)
    import math
    days = max((end_date - start_date).days + 1, 1)
    def daily(total):
        base = total / days
        return [max(0, round(base * (0.7 + 0.6 * math.sin(i/days * math.pi)))) for i in range(days)]

    ty_daily = {f: daily(ty[f]) for f in ty}
    ly_daily = {f: daily(ly[f]) for f in ly}

    return dict(
        ty=ty, ly=ly,
        ty_trend=dict(
            conversions=leads_ty, cost=[0]*len(camp_keys),
            leads=leads_ty, appointments=apt_ty, customers=cust_ty,
            cost_per_lead=cpl_ty, cost_per_appointment=cpa_ty, roi=roi_ty,
        ),
        ly_trend=dict(
            conversions=leads_ly, cost=[0]*len(camp_keys),
            leads=leads_ly, appointments=apt_ly, customers=cust_ly,
            cost_per_lead=cpl_ly, cost_per_appointment=cpa_ly, roi=roi_ly,
        ),
        ty_daily=ty_daily,
        ly_daily=ly_daily,
    )


def get_regional_data(start_date: date, end_date: date) -> list:
    """Reads regional office data from Tab2_Regional sheet."""
    # header=3 skips title rows, row 4 is the actual header
    df = pd.read_excel(_excel_path(), sheet_name="Tab2_Regional", header=3)
    # Use actual Excel column names
    df = df.rename(columns={
        "Regional Office": "name",
        "Unique Leads": "ul",
        "New Leads": "nl",
        "Apt": "apt",
        "Quote": "quote",
        "Customers": "cust",
        "Sales Amount": "sales",
        "NL Customers": "nlc",
        "NL Sales": "nl_sales",
    })
    df = df.dropna(subset=["name"])
    df = df[~df["name"].astype(str).str.contains("row|update|office|regional", case=False, na=False)]
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
    df = pd.read_excel(_excel_path(), sheet_name="Tab3_Campaign", header=3)
    df = df.rename(columns={
        "Campaign": "campaign", "Year": "year", "Month": "month",
        "Clicks": "clicks", "Cost": "cost", "Conversions": "conv",
        "Leads": "leads", "Appointments": "apt", "Customers": "cust",
        "Sales": "sales", "ROI %": "roi",
    })
    df = df.dropna(subset=["campaign"])
    df = df[~df["campaign"].astype(str).str.contains("campaign|row|update", case=False, na=False)]

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
