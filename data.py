# data.py v3.0
# Reads all data from dashboard_data.xlsx
import streamlit as st
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

@st.cache_data(ttl=300)
def get_campaigns():
    """Load only active campaigns (non-zero TY Cost or TY Leads) from Tab1_KPI sheet."""
    try:
        import pandas as pd
        df = pd.read_excel(_excel_path(), sheet_name="Tab1_KPI", header=4)
        campaigns = {}
        for _, row in df.iterrows():
            name = _norm(str(row.iloc[0]))
            if not name or name in ["nan", "Yellow=TY"]:
                continue
            # Check if campaign has any data — TY Cost (col 2) or TY Leads (col 5)
            try:
                ty_cost  = float(row.iloc[2]) if row.iloc[2] else 0
                ty_leads = float(row.iloc[5]) if row.iloc[5] else 0
            except:
                ty_cost, ty_leads = 0, 0
            # Always include "All campaigns", skip others with no data
            if name == "All campaigns" or ty_cost > 0 or ty_leads > 0:
                campaigns[name] = name
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

def _norm(name):
    """Normalize campaign name: fix encoding issues and standardize dashes."""
    if not isinstance(name, str):
        return str(name)
    # Fix em/en dash to regular hyphen
    name = name.replace("–", "-").replace("—", "-")
    name = name.strip()
    return name


# ── Tab 1: KPI Cards ──────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
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
        "bud_cost",
        "lm_leads","lm_apt",
        "date",
    ]
    df = df.dropna(subset=["campaign"])

    # Match campaign by name directly (campaign param is the full name or key)
    df["campaign"] = df["campaign"].astype(str).apply(_norm)
    camp_norm = _norm(campaign)
    rows = df[df["campaign"] == camp_norm]
    if rows.empty:
        rows = df[df["campaign"].str.contains(camp_norm[:15], case=False, na=False)]
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
        invoca       = int(sv("ty_conv_invoca")),  # Google conv Invoca
        form         = int(sv("ty_conv_form")),     # Google conv Form
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
@st.cache_data(ttl=300)
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
        "bud_cost",
        "lm_leads","lm_apt",
        "date",
    ]
    df = df.dropna(subset=["campaign"])

    camp_keys = list(CAMPAIGNS.keys())
    camp_names = list(CAMPAIGNS.values())

    df["campaign"] = df["campaign"].astype(str).apply(_norm)
    def get_row(key):
        key_norm = _norm(key)
        rows = df[df["campaign"] == key_norm]
        if rows.empty:
            rows = df[df["campaign"].str.contains(key_norm[:15] if len(key_norm)>3 else "All", case=False, na=False)]
        if rows.empty: rows = df.head(1)
        return rows.iloc[0]

    def sv(r, f): return _sv(r.get(f, 0))

    r = get_row(campaign)
    def safe_int(v):
        try: return max(0, int(float(v))) if v==v else 0
        except: return 0
    def safe_float(v):
        try: return float(v) if v==v else 0.0
        except: return 0.0

    ty = dict(conversions=safe_int(sv(r,"ty_conv")), cost=safe_float(sv(r,"ty_cost")),
              leads=safe_int(sv(r,"ty_leads")), appointments=safe_int(sv(r,"ty_apt")),
              customers=safe_int(sv(r,"ty_cust")), cost_per_lead=safe_float(sv(r,"ty_cpl")),
              cost_per_appointment=safe_float(sv(r,"ty_cpa")), roi=safe_float(sv(r,"ty_roi")))
    ly = dict(conversions=safe_int(sv(r,"ly_conv")), cost=safe_float(sv(r,"ly_cost")),
              leads=safe_int(sv(r,"ly_leads")), appointments=safe_int(sv(r,"ly_apt")),
              customers=safe_int(sv(r,"ly_cust")), cost_per_lead=safe_float(sv(r,"ly_cpl")),
              cost_per_appointment=safe_float(sv(r,"ly_cpa")), roi=safe_float(sv(r,"ly_roi")))

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

def get_regional_detail(from_year=None, from_month=None, to_year=None, to_month=None) -> dict:
    """Reads campaign breakdown per regional office from Tab2_Regional_Detail, filtered by date range."""
    try:
        df = pd.read_excel(_excel_path(), sheet_name="Tab2_Regional_Detail", header=3)
        df.columns = [str(c).strip() for c in df.columns]

        # Rename columns by position
        col_names = ["region","year","month","campaign","ul","nl","apt","quote","cust","sales","nlc","nl_sales"]
        df = df.iloc[:, :len(col_names)]
        df.columns = col_names

        df = df.dropna(subset=["region","campaign"])
        df["region"]   = df["region"].astype(str).str.replace("–","-").str.strip()
        df["campaign"] = df["campaign"].astype(str).str.replace("–","-").str.strip()

        MONTH_MAP = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
                     "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12,
                     "January":1,"February":2,"March":3,"April":4,
                     "June":6,"July":7,"August":8,"September":9,
                     "October":10,"November":11,"December":12}

        # Filter by date range
        if from_year and to_year:
            def in_range(row):
                try:
                    yr = int(float(row["year"]))
                    mo = MONTH_MAP.get(str(row["month"]).strip(), 0)
                    return (from_year*100+from_month) <= (yr*100+mo) <= (to_year*100+to_month)
                except: return False
            df = df[df.apply(in_range, axis=1)]

        # Aggregate by region+campaign (sum numeric)
        result = {}
        agg = {}
        for _, row in df.iterrows():
            reg  = row["region"]
            camp = row["campaign"]
            key  = (reg, camp)
            if key not in agg:
                agg[key] = {f:0.0 for f in ["ul","nl","apt","quote","cust","sales","nlc","nl_sales"]}
            for f in ["ul","nl","apt","quote","cust","sales","nlc","nl_sales"]:
                agg[key][f] += _sv(row.get(f, 0))

        for (reg, camp), d in agg.items():
            if reg not in result:
                result[reg] = []
            result[reg].append(dict(
                campaign=camp,
                ul=int(d["ul"]), nl=int(d["nl"]),
                apt=int(d["apt"]), quote=int(d["quote"]),
                cust=int(d["cust"]), sales=d["sales"],
                nlc=int(d["nlc"]), nl_sales=d["nl_sales"],
            ))
        return result
    except Exception as e:
        print(f"Error reading Tab2_Regional_Detail: {e}")
        return {}

@st.cache_data(ttl=300)
def get_regional_data(from_year=None, from_month=None, to_year=None, to_month=None) -> list:
    df = pd.read_excel(_excel_path(), sheet_name="Tab2_Regional", header=3)
    col_map = {
        "Regional Office":"name","Year":"year","Month":"month",
        "Unique Leads":"ul","New Leads":"nl","Apt":"apt","Quote":"quote",
        "Customers":"cust","Sales Amount":"sales","NL Customers":"nlc","NL Sales":"nl_sales",
        "% of Total":"leads_pct","$ Sales % of Total":"sales_pct",
        "Apt/Leads":"apt_leads","Order/Apt":"order_apt","Order/Leads":"order_leads",
    }
    df = df.rename(columns={c: col_map[c] for c in df.columns if c in col_map})
    df = df.dropna(subset=["name"])
    df = df[~df["name"].astype(str).str.contains("row|update|office|regional|add new", case=False, na=False)]

    MONTH_MAP = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
                 "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12,
                 "January":1,"February":2,"March":3,"April":4,
                 "June":6,"July":7,"August":8,"September":9,
                 "October":10,"November":11,"December":12}
    has_date_cols = "year" in df.columns and "month" in df.columns
    if from_year and to_year and has_date_cols:
        def in_range(row):
            try:
                yr = int(float(row["year"]))
                mo = MONTH_MAP.get(str(row["month"]).strip(), 0)
                return (from_year*100+from_month) <= (yr*100+mo) <= (to_year*100+to_month)
            except: return False
        df = df[df.apply(in_range, axis=1)]

    # Aggregate by office
    offices = {}
    for _, row in df.iterrows():
        name = str(row["name"]).strip()
        if not name or name == "nan": continue
        if name not in offices:
            offices[name] = {f:0.0 for f in ["ul","nl","apt","quote","cust","sales","nlc","nl_sales"]}
            offices[name].update({"leads_pct":"","sales_pct":"","apt_leads":"","order_apt":"","order_leads":""})
        for f in ["ul","nl","apt","quote","cust","sales","nlc","nl_sales"]:
            offices[name][f] += _sv(row.get(f,0))
        for f in ["leads_pct","sales_pct","apt_leads","order_apt","order_leads"]:
            v = str(row.get(f,"")).strip()
            if v and v != "nan": offices[name][f] = v

    return [dict(
        name=name,
        ul=int(d["ul"]), nl=int(d["nl"]), apt=int(d["apt"]),
        quote=int(d["quote"]), cust=int(d["cust"]),
        sales=d["sales"], nlc=int(d["nlc"]), nl_sales=d["nl_sales"],
        leads_pct=d["leads_pct"] or "0%",
        sales_pct=d["sales_pct"] or "0%",
        apt_leads=d["apt_leads"] or "0%",
        order_apt=d["order_apt"] or "0%",
        order_leads=d["order_leads"] or "0%",
    ) for name, d in offices.items()]


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
    df["campaign"] = df["campaign"].astype(str).apply(_norm)
    df = df[~df["campaign"].str.contains("campaign|row|update", case=False, na=False)]

    MONTH_MAP = {"Jan":0,"Feb":1,"Mar":2,"Apr":3,"May":4,"Jun":5,
                 "Jul":6,"Aug":7,"Sep":8,"Oct":9,"Nov":10,"Dec":11}

    campaigns = df["campaign"].unique().tolist()
    result = []
    for camp in campaigns:
        rows = df[df["campaign"] == camp]
        trend = {}
        for _, row in rows.iterrows():
            try: yr = str(int(float(row["year"])))  # string key for JS
            except: continue
            mo  = str(row["month"]).strip()
            idx = MONTH_MAP.get(mo, 0)
            if yr not in trend:
                trend[yr] = {f:[0]*12 for f in ["clicks","cost","conv","leads","apt","cust","sales","roi"]}
            for f in ["clicks","cost","conv","leads","apt","cust","sales","roi"]:
                trend[yr][f][idx] = _sv(row.get(f,0))
        result.append(dict(name=camp, trend=trend))
    return result
