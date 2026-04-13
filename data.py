# data.py
# ─────────────────────────────────────────────────────────────────────────────
# Data layer — swap mock data with real DB queries when ready.
# get_data()          → today's KPI cards
# get_roi_data()      → MTD ROI charts (1st of month → yesterday)
# get_regional_data() → MTD regional office table + pie charts
# ─────────────────────────────────────────────────────────────────────────────
from datetime import date

CAMPAIGNS = {
    "all":     "All campaigns",
    "brand":   "Brand awareness",
    "search":  "Search — HVAC",
    "display": "Display retargeting",
    "local":   "Local services ads",
}

# ── Mock: today's KPI numbers ─────────────────────────────────────────────────
MOCK_TODAY = {
    "all":     dict(conversions=184, invoca=112, form=72,  cost=4820, leads=201, crm_invoca=118, crm_form=83, appointments=47, customers=19),
    "brand":   dict(conversions=42,  invoca=28,  form=14,  cost=980,  leads=46,  crm_invoca=30,  crm_form=16, appointments=11, customers=4),
    "search":  dict(conversions=76,  invoca=44,  form=32,  cost=2210, leads=83,  crm_invoca=48,  crm_form=35, appointments=20, customers=8),
    "display": dict(conversions=38,  invoca=22,  form=16,  cost=890,  leads=41,  crm_invoca=24,  crm_form=17, appointments=10, customers=4),
    "local":   dict(conversions=28,  invoca=18,  form=10,  cost=740,  leads=31,  crm_invoca=16,  crm_form=15, appointments=6,  customers=3),
}

# ── Mock: ROI charts (MTD, this year vs last year) ────────────────────────────
MOCK_ROI = {
    "all": {
        "ty":  dict(conversions=184, cost=4820, leads=201, appointments=47, customers=19, cost_per_lead=24, cost_per_appointment=103, roi=688),
        "ly":  dict(conversions=160, cost=4200, leads=175, appointments=40, customers=15, cost_per_lead=24, cost_per_appointment=105, roi=638),
        "ty_trend": dict(conversions=[520,610,720,184], cost=[13800,16200,19100,4820], leads=[560,660,780,201], appointments=[132,155,183,47], customers=[52,62,73,19], cost_per_lead=[25,25,24,24], cost_per_appointment=[105,105,104,103], roi=[620,640,665,688]),
        "ly_trend": dict(conversions=[450,530,620,160], cost=[11900,14000,16500,4200], leads=[490,575,680,175], appointments=[113,133,158,40], customers=[43,51,62,15], cost_per_lead=[24,24,24,24], cost_per_appointment=[105,105,104,105], roi=[595,612,628,638]),
    },
    "brand": {
        "ty":  dict(conversions=42,  cost=980,  leads=46,  appointments=11, customers=4,  cost_per_lead=21, cost_per_appointment=89,  roi=736),
        "ly":  dict(conversions=35,  cost=850,  leads=38,  appointments=9,  customers=3,  cost_per_lead=22, cost_per_appointment=94,  roi=665),
        "ty_trend": dict(conversions=[28,32,38,42], cost=[620,720,840,980], leads=[28,33,40,46], appointments=[6,8,9,11], customers=[2,3,3,4], cost_per_lead=[22,22,21,21], cost_per_appointment=[103,90,93,89], roi=[690,710,720,736]),
        "ly_trend": dict(conversions=[22,26,30,35], cost=[510,600,720,850], leads=[22,27,32,38], appointments=[5,6,7,9],  customers=[1,2,2,3], cost_per_lead=[23,22,23,22], cost_per_appointment=[102,100,103,94], roi=[637,648,658,665]),
    },
    "search": {
        "ty":  dict(conversions=76,  cost=2210, leads=83,  appointments=20, customers=8,  cost_per_lead=27, cost_per_appointment=111, roi=669),
        "ly":  dict(conversions=68,  cost=1980, leads=72,  appointments=17, customers=7,  cost_per_lead=28, cost_per_appointment=116, roi=632),
        "ty_trend": dict(conversions=[48,55,65,76], cost=[1400,1650,1900,2210], leads=[50,60,72,83], appointments=[11,14,17,20], customers=[4,5,7,8], cost_per_lead=[28,28,26,27], cost_per_appointment=[127,118,112,111], roi=[636,648,658,669]),
        "ly_trend": dict(conversions=[40,47,57,68], cost=[1200,1400,1700,1980], leads=[42,52,62,72], appointments=[9,12,14,17],  customers=[3,4,6,7], cost_per_lead=[29,27,27,28], cost_per_appointment=[133,117,121,116], roi=[608,617,626,632]),
    },
    "display": {
        "ty":  dict(conversions=38,  cost=890,  leads=41,  appointments=10, customers=4,  cost_per_lead=22, cost_per_appointment=89,  roi=777),
        "ly":  dict(conversions=32,  cost=780,  leads=35,  appointments=8,  customers=3,  cost_per_lead=22, cost_per_appointment=98,  roi=695),
        "ty_trend": dict(conversions=[22,27,32,38], cost=[540,650,760,890], leads=[24,29,35,41], appointments=[5,7,8,10], customers=[2,3,3,4], cost_per_lead=[23,22,22,22], cost_per_appointment=[108,93,95,89], roi=[730,748,762,777]),
        "ly_trend": dict(conversions=[18,23,27,32], cost=[460,560,660,780], leads=[20,25,30,35], appointments=[4,6,7,8],  customers=[1,2,2,3], cost_per_lead=[23,22,22,22], cost_per_appointment=[115,93,94,98], roi=[648,661,673,695]),
    },
    "local": {
        "ty":  dict(conversions=28,  cost=740,  leads=31,  appointments=6,  customers=3,  cost_per_lead=24, cost_per_appointment=123, roi=576),
        "ly":  dict(conversions=25,  cost=590,  leads=30,  appointments=6,  customers=2,  cost_per_lead=20, cost_per_appointment=98,  roi=544),
        "ty_trend": dict(conversions=[16,19,23,28], cost=[440,530,630,740], leads=[18,22,26,31], appointments=[3,4,5,6], customers=[1,2,2,3], cost_per_lead=[24,24,24,24], cost_per_appointment=[147,133,126,123], roi=[545,554,563,576]),
        "ly_trend": dict(conversions=[14,17,20,25], cost=[340,420,510,590], leads=[16,20,25,30], appointments=[3,4,5,6], customers=[1,1,2,2], cost_per_lead=[21,21,20,20], cost_per_appointment=[113,105,102,98],  roi=[518,527,535,544]),
    },
}

# ── Mock: regional office data ────────────────────────────────────────────────
MOCK_REGIONAL = [
    dict(name="Arizona",           ul=32, nl=30, apt=12, quote=6,  cust=3,  sales=23304.00, nlc=3,  nl_sales=23304.00),
    dict(name="Austin",            ul=2,  nl=2,  apt=0,  quote=0,  cust=0,  sales=0,        nlc=0,  nl_sales=0),
    dict(name="Bay Area",          ul=49, nl=46, apt=18, quote=6,  cust=3,  sales=13794.00, nlc=2,  nl_sales=13644.00),
    dict(name="CDR",               ul=7,  nl=1,  apt=0,  quote=6,  cust=0,  sales=0,        nlc=0,  nl_sales=0),
    dict(name="Central Coast",     ul=5,  nl=5,  apt=3,  quote=0,  cust=0,  sales=0,        nlc=0,  nl_sales=0),
    dict(name="Corporate",         ul=1,  nl=0,  apt=0,  quote=0,  cust=0,  sales=0,        nlc=0,  nl_sales=0),
    dict(name="Fresno",            ul=6,  nl=6,  apt=1,  quote=1,  cust=0,  sales=0,        nlc=0,  nl_sales=0),
    dict(name="Inland Empire",     ul=36, nl=32, apt=15, quote=7,  cust=2,  sales=12797.16, nlc=2,  nl_sales=12797.16),
    dict(name="Las Vegas",         ul=19, nl=15, apt=3,  quote=1,  cust=1,  sales=7953.68,  nlc=1,  nl_sales=7953.68),
    dict(name="National Sales",    ul=37, nl=36, apt=0,  quote=13, cust=2,  sales=7684.00,  nlc=2,  nl_sales=7684.00),
    dict(name="Orange County",     ul=26, nl=21, apt=17, quote=2,  cust=2,  sales=16352.00, nlc=1,  nl_sales=7794.00),
    dict(name="Pasadena",          ul=44, nl=36, apt=14, quote=10, cust=3,  sales=23993.00, nlc=3,  nl_sales=23993.00),
    dict(name="Sacramento",        ul=19, nl=18, apt=8,  quote=2,  cust=0,  sales=0,        nlc=0,  nl_sales=0),
    dict(name="San Antonio",       ul=12, nl=12, apt=7,  quote=2,  cust=1,  sales=8641.00,  nlc=1,  nl_sales=8641.00),
    dict(name="San Diego",         ul=22, nl=21, apt=6,  quote=4,  cust=0,  sales=0,        nlc=0,  nl_sales=0),
    dict(name="Ventura/SB County", ul=9,  nl=8,  apt=5,  quote=2,  cust=2,  sales=16532.00, nlc=2,  nl_sales=16532.00),
]


def get_data(campaign: str) -> dict:
    """
    Returns today's KPI numbers.
    TO CONNECT REAL DATA: replace return with your DB query.
    """
    return MOCK_TODAY.get(campaign, MOCK_TODAY["all"])


def get_roi_data(campaign: str, start_date: date, end_date: date) -> dict:
    """
    Returns MTD ROI data for charts.
    TO CONNECT REAL DATA: replace return with your DB query.
    """
    return MOCK_ROI.get(campaign, MOCK_ROI["all"])


def get_regional_data(start_date: date, end_date: date) -> list:
    """
    Returns list of regional office dicts.
    TO CONNECT REAL DATA: replace return with your DB query.
    Each dict needs: name, ul, nl, apt, quote, cust, sales, nlc, nl_sales
    """
    return MOCK_REGIONAL
