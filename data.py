# data.py v3.0
# Reads all data from dashboard_data.xlsx
# Tab1_KPI: one row per campaign (All, Brand, Search, Display, Local)
# Tab2_Regional: one row per regional office
# Tab3_Campaign: one row per campaign per month
from datetime import date
import os
import pandas as pd

# Base campaigns — will be extended dynamically from Excel
CAMPAIGNS_BASE = {
    "all": "All campaigns",
}

def get_campaigns():
    """Load all campaigns from Tab1_KPI sheet dynamically."""
    try:
        import pandas as pd
        df = pd.read_excel(_excel_path(), sheet_name="Tab1_KPI", header=4)
        campaigns = {}
        for _, row in df.iterrows():
            name = str(row.iloc[0]).strip()
            if name and name not in ["nan", "Yellow=TY"]:
                key = name.lower().replace(" ", "_").replace("-","_").replace(".","").replace("(","").replace(")","")[:30]
                campaigns[key] = name
        return campaigns if campaigns else CAMPAIGNS_BASE
    except:
        return CAMPAIGNS_BASE

CAMPAIGNS = CAMPAIGNS_BASE  # will be overridden at runtime

def _excel_path():
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "dashboard_data.xlsx")

def _sv(val):
    try:
        v = float(val)
        return 0.0 if (v != v) else v
    except:
        return 0.0


# ── Tab 1: KPI Cards ──────────────────────────────────────────────────────────
def get_data(campaign: str) -> dict:
    """
    Reads KPI numbers from Tab1_KPI sheet.
    One row per campaign. Columns:
    A=Campaign, B-K=TY, L-S=LY MTD, T-X=LY Full, Y-Z=Budget, AA=Date
    """
    df = pd.read_excel(_excel_path(), sheet_name="Tab1_KPI", header=4)
    df.columns = [
        "campaign",
        "ty_conv","ty_conv_invoca","ty_conv_form",
        "ty_cost",
        "ty_leads","ty_crm_invoca","ty_crm_form",
        "ty_apt","ty_cust","ty_cpl","ty_cpa","ty_roi",
        "ly_conv","ly_cost","ly_leads","ly_apt","ly_cust","ly_cpl","ly_cpa","ly_roi",
        "lyf_conv","lyf_cost","lyf_leads","lyf_apt","lyf_cust",
        "bud_conv","bud_cost",
        "lm_leads","lm_apt",
        "date",
    ]
    df = df.dropna(subset=["campaign"])

    # Match campaign by name directly (campaign param is the full name or key)
    rows = df[df["campaign"].astype(str).str.strip() == campaign]
    if rows.empty:
        # Try partial match
        rows = df[df["campaign"].astype(str).str.contains(campaign[:15], case=False, na=False)]
    if rows.empty:
        rows = df[df["campaign"].astype(str).str.contains("All", case=False, na=False)]
    if rows.empty:
        rows = df.head(1)

    r = rows.iloc[0]
    sv = lambda f: _sv(r.get(f, 0))

    return dict(
        conversions  = int(sv("ty_conv")),
        cost         = sv("ty_cost"),
        budget       = sv("bud_cost"),
        invoca       = int(sv("ty_conv_invoca")),
        form         = int(sv("ty_conv_form")),
        leads        = int(sv("ty_leads")),
        crm_invoca   = int(sv("ty_crm_invoca")),
        crm_form     = int(sv("ty_crm_form")),
        appointments = int(sv("ty_apt")),
        customers    = int(sv("ty_cust")),
        cost_per_lead= sv("ty_cpl"),
        cost_per_apt = sv("ty_cpa"),
        roi          = sv("ty_roi"),
        lm_full=dict(
            leads        = int(sv("lm_leads")),
            appointments = int(sv("lm_apt")),
        ),
        ly_mtd=dict(
            conversions=int(sv("ly_conv")), cost=sv("ly_cost"),
            leads=int(sv("ly_leads")),      appointments=int(sv("ly_apt")),
            customers=int(sv("ly_cust")),   cost_per_lead=sv("ly_cpl"),
            cost_per_apt=sv("ly_cpa"),      roi=sv("ly_roi"),
        ),
        ly_full=dict(
            conversions=int(sv("lyf_conv")), cost=sv("lyf_cost"),
            leads=int(sv("lyf_leads")),      appointments=int(sv("lyf_apt")),
            customers=int(sv("lyf_cust")),   cost_per_lead=0,
            cost_per_apt=0,                  roi=0,
        ),
    )


# ── Tab 1: ROI Charts ─────────────────────────────────────────────────────────
def get_roi_data(campaign: str, start_date: date, end_date: date) -> dict:
    """Reads MTD comparison from Tab1_KPI, monthly trend from Tab3_Campaign."""
    df = pd.read_excel(_excel_path(), sheet_name="Tab1_KPI", header=4)
    df.columns = [
        "campaign",
        "ty_conv","ty_conv_invoca","ty_conv_form",
        "ty_cost",
        "ty_leads","ty_crm_invoca","ty_crm_form",
        "ty_apt","ty_cust","ty_cpl","ty_cpa","ty_roi",
        "ly_conv","ly_cost","ly_leads","ly_apt","ly_cust","ly_cpl","ly_cpa","ly_roi",
        "lyf_conv","lyf_cost","lyf_leads","lyf_apt","lyf_cust",
        "bud_conv","bud_cost",
        "lm_leads","lm_apt",
        "date",
    ]
    df = df.dropna(subset=["campaign"])

    camp_keys = list(CAMPAIGNS.keys())
    camp_names = list(CAMPAIGNS.values())

    def get_row(key):
        rows = df[df["campaign"].astype(str).str.strip() == key]
        if rows.empty:
            rows = df[df["campaign"].astype(str).str.contains(key[:15] if len(key)>3 else "All", case=False, na=False)]
        if rows.empty: rows = df.head(1)
        return rows.iloc[0]

    def sv(r, f): return _sv(r.get(f, 0))

    r = get_row(campaign)
    ty = dict(conversions=int(sv(r,"ty_conv")), cost=sv(r,"ty_cost"),
              leads=int(sv(r,"ty_leads")), appointments=int(sv(r,"ty_apt")),
              customers=int(sv(r,"ty_cust")), cost_per_lead=sv(r,"ty_cpl"),
              cost_per_appointment=sv(r,"ty_cpa"), roi=sv(r,"ty_roi"))
    ly = dict(conversions=int(sv(r,"ly_conv")), cost=sv(r,"ly_cost"),
              leads=int(sv(r,"ly_leads")), appointments=int(sv(r,"ly_apt")),
              customers=int(sv(r,"ly_cust")), cost_per_lead=sv(r,"ly_cpl"),
              cost_per_appointment=sv(r,"ly_cpa"), roi=sv(r,"ly_roi"))

    # Bar chart series (all campaigns)
    def series(ty_field, ly_field):
        return ([int(_sv(get_row(k).get(ty_field,0))) for k in camp_keys],
                [int(_sv(get_row(k).get(ly_field,0))) for k in camp_keys])

    leads_ty, leads_ly   = series("ty_leads","ly_leads")
    apt_ty,   apt_ly     = series("ty_apt",  "ly_apt")
    cust_ty,  cust_ly    = series("ty_cust", "ly_cust")
    cpl_ty,   cpl_ly     = series("ty_cpl",  "ly_cpl")
    cpa_ty,   cpa_ly     = series("ty_cpa",  "ly_cpa")
    roi_ty,   roi_ly     = series("ty_roi",  "ly_roi")
    conv_ty,  conv_ly    = series("ty_conv", "ly_conv")
    cost_ty,  cost_ly    = series("ty_cost", "ly_cost")

    return dict(
        ty=ty, ly=ly,
        ty_trend=dict(conversions=conv_ty, cost=cost_ty, leads=leads_ty,
                      appointments=apt_ty, customers=cust_ty,
                      cost_per_lead=cpl_ty, cost_per_appointment=cpa_ty, roi=roi_ty),
        ly_trend=dict(conversions=conv_ly, cost=cost_ly, leads=leads_ly,
                      appointments=apt_ly, customers=cust_ly,
                      cost_per_lead=cpl_ly, cost_per_appointment=cpa_ly, roi=roi_ly),
        ty_daily={}, ly_daily={},
    )


# ── Tab 2: Regional Offices ───────────────────────────────────────────────────
def get_regional_data(start_date: date, end_date: date) -> list:
    df = pd.read_excel(_excel_path(), sheet_name="Tab2_Regional", header=3)
    # Rename using actual column names
    col_map = {
        "Regional Office":    "name",
        "Unique Leads":       "ul",
        "New Leads":          "nl",
        "Apt":                "apt",
        "Quote":              "quote",
        "Customers":          "cust",
        "Sales Amount":       "sales",
        "NL Customers":       "nlc",
        "NL Sales":           "nl_sales",
        "% of Total":         "leads_pct",
        "$ Sales % of Total": "sales_pct",
        "Apt/Leads":          "apt_leads",
        "Order/Apt":          "order_apt",
        "Order/Leads":        "order_leads",
    }
    df = df.rename(columns={c: col_map[c] for c in df.columns if c in col_map})
    df = df.dropna(subset=["name"])
    df = df[~df["name"].astype(str).str.contains("row|update|office|regional", case=False, na=False)]

    result = []
    for _, row in df.iterrows():
        result.append(dict(
            name=str(row["name"]),
            ul=int(_sv(row.get("ul",0))),       nl=int(_sv(row.get("nl",0))),
            apt=int(_sv(row.get("apt",0))),     quote=int(_sv(row.get("quote",0))),
            cust=int(_sv(row.get("cust",0))),   sales=_sv(row.get("sales",0)),
            nlc=int(_sv(row.get("nlc",0))),     nl_sales=_sv(row.get("nl_sales",0)),
            leads_pct=str(row.get("leads_pct","0%")),
            sales_pct=str(row.get("sales_pct","0%")),
            apt_leads=str(row.get("apt_leads","0%")),
            order_apt=str(row.get("order_apt","0%")),
            order_leads=str(row.get("order_leads","0%")),
        ))
    return result


# ── Tab 3: Campaign Performance ───────────────────────────────────────────────
def get_campaign_data() -> list:
    df = pd.read_excel(_excel_path(), sheet_name="Tab3_Campaign", header=3)
    col_map3 = {
        "Campaign":"campaign","Year":"year","Month":"month",
        "Clicks":"clicks","Cost":"cost","Conversions":"conv",
        "Leads":"leads","Appointments":"apt","Customers":"cust",
        "Sales":"sales","ROI %":"roi",
    }
    df = df.rename(columns={c: col_map3[c] for c in df.columns if c in col_map3})
    df = df.dropna(subset=["campaign"])
    df = df[~df["campaign"].astype(str).str.contains("campaign|row|update", case=False, na=False)]

    MONTH_MAP = {"Jan":0,"Feb":1,"Mar":2,"Apr":3,"May":4,"Jun":5,
                 "Jul":6,"Aug":7,"Sep":8,"Oct":9,"Nov":10,"Dec":11}

    campaigns = df["campaign"].unique().tolist()
    result = []
    for camp in campaigns:
        rows = df[df["campaign"] == camp]
        trend = {}
        for _, row in rows.iterrows():
            try: yr = int(float(row["year"]))
            except: continue
            mo  = str(row["month"]).strip()
            idx = MONTH_MAP.get(mo, 0)
            if yr not in trend:
                trend[yr] = {f:[0]*12 for f in ["clicks","cost","conv","leads","apt","cust","sales","roi"]}
            for f in ["clicks","cost","conv","leads","apt","cust","sales","roi"]:
                trend[yr][f][idx] = _sv(row.get(f,0))
        result.append(dict(name=camp, trend=trend))
    return result
