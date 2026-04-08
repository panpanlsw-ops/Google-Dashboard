# data.py
# ─────────────────────────────────────────────────────────────────────────────
# Data layer — swap mock data with real DB queries when ready.
# get_data()     → today's KPI cards (used by top section)
# get_roi_data() → MTD data 1st of month → yesterday (used by ROI charts)
# ─────────────────────────────────────────────────────────────────────────────
from datetime import date

CAMPAIGNS = {
    "all":     "All campaigns",
    "brand":   "Brand awareness",
    "search":  "Search — HVAC",
    "display": "Display retargeting",
    "local":   "Local services ads",
}

# ── Mock data: today's KPI numbers ────────────────────────────────────────────
MOCK_TODAY = {
    "all":     dict(conversions=184, invoca=112, form=72,  cost=4820, leads=201, crm_invoca=118, crm_form=83, appointments=47, customers=19),
    "brand":   dict(conversions=42,  invoca=28,  form=14,  cost=980,  leads=46,  crm_invoca=30,  crm_form=16, appointments=11, customers=4),
    "search":  dict(conversions=76,  invoca=44,  form=32,  cost=2210, leads=83,  crm_invoca=48,  crm_form=35, appointments=20, customers=8),
    "display": dict(conversions=38,  invoca=22,  form=16,  cost=890,  leads=41,  crm_invoca=24,  crm_form=17, appointments=10, customers=4),
    "local":   dict(conversions=28,  invoca=18,  form=10,  cost=740,  leads=31,  crm_invoca=16,  crm_form=15, appointments=6,  customers=3),
}

# ── Mock data: ROI section (MTD, this year vs last year) ─────────────────────
# ty = this year, ly = last year
# ty_trend / ly_trend = monthly list Jan→current month
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


def get_data(campaign: str) -> dict:
    """
    Returns today's KPI numbers for the given campaign.
    TO CONNECT REAL DATA: replace the return below with your DB query.
    Return a dict with keys: conversions, invoca, form, cost,
                             leads, crm_invoca, crm_form, appointments, customers
    """
    # ── Replace with real DB query ─────────────────────────────────────────
    return MOCK_TODAY.get(campaign, MOCK_TODAY["all"])
    # ──────────────────────────────────────────────────────────────────────


def get_roi_data(campaign: str, start_date: date, end_date: date) -> dict:
    """
    Returns MTD ROI data (1st of month → yesterday) for the ROI charts.
    TO CONNECT REAL DATA: replace the return below with your DB query.
    Return a dict with:
      ty        → this year totals dict
      ly        → last year totals dict
      ty_trend  → this year monthly list (Jan → current month)
      ly_trend  → last year monthly list (Jan → current month)
    Each dict needs keys: conversions, cost, leads, appointments,
                          customers, cost_per_lead, cost_per_appointment, roi
    """
    # ── Replace with real DB query ─────────────────────────────────────────
    return MOCK_ROI.get(campaign, MOCK_ROI["all"])
    # ──────────────────────────────────────────────────────────────────────
