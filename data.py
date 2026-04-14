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
    For single campaign view, return daily arrays in ty_daily / ly_daily.
    Each array has one value per day from the 1st of the month to yesterday.
    """
    import random, math
    data = MOCK_ROI.get(campaign, MOCK_ROI["all"])

    # Generate daily mock data for the current MTD period
    days = (end_date - start_date).days + 1
    def daily(total, n):
        base = total / max(n, 1)
        vals = [max(0, round(base * (0.7 + 0.6 * math.sin(i/n * math.pi)))) for i in range(n)]
        # adjust last val to make total match
        diff = total - sum(vals[:-1])
        vals[-1] = max(0, diff)
        return vals

    ty = data["ty"]
    ly = data["ly"]
    data["ty_daily"] = {
        "conversions":        daily(ty["conversions"], days),
        "cost":               daily(ty["cost"], days),
        "leads":              daily(ty["leads"], days),
        "appointments":       daily(ty["appointments"], days),
        "customers":          daily(ty["customers"], days),
        "cost_per_lead":      [ty["cost_per_lead"]] * days,
        "cost_per_appointment": [ty["cost_per_appointment"]] * days,
        "roi":                [round(ty["roi"] * (0.9 + 0.2*i/days), 1) for i in range(days)],
    }
    data["ly_daily"] = {
        "conversions":        daily(ly["conversions"], days),
        "cost":               daily(ly["cost"], days),
        "leads":              daily(ly["leads"], days),
        "appointments":       daily(ly["appointments"], days),
        "customers":          daily(ly["customers"], days),
        "cost_per_lead":      [ly["cost_per_lead"]] * days,
        "cost_per_appointment": [ly["cost_per_appointment"]] * days,
        "roi":                [round(ly["roi"] * (0.9 + 0.2*i/days), 1) for i in range(days)],
    }
    return data


def get_regional_data(start_date: date, end_date: date) -> list:
    """
    Returns list of regional office dicts.
    TO CONNECT REAL DATA: replace return with your DB query.
    Each dict needs: name, ul, nl, apt, quote, cust, sales, nlc, nl_sales
    """
    return MOCK_REGIONAL


# ── Campaign performance mock data ────────────────────────────────────────────
MOCK_CAMPAIGNS = [
    dict(name="(TWC) LifeSource Brand",           highlight=False),
    dict(name="AZ - Tucson Single Form",           highlight=True),
    dict(name="Arizona Single Form",               highlight=False),
    dict(name="Bakersfield Single Form",           highlight=True),
    dict(name="Bay Area Single Form",              highlight=False),
    dict(name="Central Coast Single Form",         highlight=False),
    dict(name="Competitors - USA",                 highlight=False),
    dict(name="Demand Gen - Prospecting",          highlight=False),
    dict(name="Fresno Single Form",                highlight=False),
    dict(name="IE - Palm Springs Single Form",     highlight=False),
    dict(name="Inland Empire Single Form",         highlight=False),
    dict(name="Las Vegas Single Form",             highlight=False),
    dict(name="Orange County Single Form",         highlight=True),
    dict(name="PMAX 1 - LA",                       highlight=True),
    dict(name="PMAX 2 - NoCal",                    highlight=False),
    dict(name="Pasadena Single Form",              highlight=False),
    dict(name="RLSA - All",                        highlight=False),
    dict(name="Sacramento Single Form",            highlight=True),
    dict(name="San Antonio Single Form",           highlight=True),
    dict(name="San Diego Single Form",             highlight=False),
    dict(name="Ventura County Single Form",        highlight=False),
]

# Monthly data per campaign [Jan..Dec] for 2024, 2025, 2026
MOCK_CAMP_MONTHLY = {
    "(TWC) LifeSource Brand": {
        2024: dict(clicks=[290,310,330,350,370,360,380,400,390,380,360,340], cost=[430,460,490,520,550,535,565,595,580,565,535,505], conv=[20,22,23,25,26,26,27,29,28,27,26,24], leads=[10,11,12,13,13,13,14,15,14,13,13,12], apt=[4,5,5,5,6,6,6,6,6,6,5,5], cust=[1,1,1,2,2,2,2,2,2,2,1,1], sales=[8000,9000,9500,11000,11500,11000,12000,13000,12500,12000,10000,9000], roi=[1200,1350,1400,1600,1650,1600,1750,1900,1800,1750,1500,1350]),
        2025: dict(clicks=[320,340,365,385,405,395,415,440,428,415,395,370], cost=[475,505,540,572,600,588,617,650,634,617,588,555], conv=[22,24,26,27,28,28,30,32,31,30,28,26], leads=[11,12,13,14,14,14,15,16,16,15,14,13], apt=[5,5,6,6,6,6,6,7,7,6,6,5], cust=[1,2,2,2,2,2,2,2,2,2,2,1], sales=[9000,10500,11000,12500,13000,12500,14000,15000,14500,14000,12000,10500], roi=[1520,1700,1780,1900,1950,1900,2000,2100,2050,2000,1800,1700]),
        2026: dict(clicks=[355,378,410,1431,0,0,0,0,0,0,0,0], cost=[525,558,600,2209,0,0,0,0,0,0,0,0], conv=[24,27,29,110,0,0,0,0,0,0,0,0], leads=[12,14,15,58,0,0,0,0,0,0,0,0], apt=[5,6,6,25,0,0,0,0,0,0,0,0], cust=[2,2,2,6,0,0,0,0,0,0,0,0], sales=[10000,11500,12500,47427,0,0,0,0,0,0,0,0], roi=[1700,1850,1950,2046,0,0,0,0,0,0,0,0]),
    },
    "PMAX 1 - LA": {
        2024: dict(clicks=[420,452,493,524,545,534,561,596,575,554,522,480], cost=[3200,3445,3758,3995,4152,4068,4274,4543,4381,4223,3980,3660], conv=[10,11,12,13,13,13,14,15,14,13,13,12], leads=[5,6,6,7,7,7,7,7,7,7,6,5], apt=[3,3,3,4,4,4,4,4,4,4,3,3], cust=[1,1,1,1,1,1,1,2,1,1,1,1], sales=[12000,13500,14000,15500,16000,15500,16500,18000,17500,16500,15000,13000], roi=[52,60,65,72,74,72,78,88,85,78,70,62]),
        2025: dict(clicks=[466,502,547,582,605,593,623,662,639,616,580,533], cost=[3552,3824,4172,4435,4609,4515,4744,5043,4863,4688,4418,4062], conv=[11,12,13,14,14,14,15,16,15,14,14,13], leads=[6,6,7,7,8,8,8,8,8,8,7,6], apt=[3,3,4,4,4,4,4,5,4,4,4,3], cust=[1,1,1,1,2,1,2,2,2,1,1,1], sales=[13500,15000,15500,17000,18000,17000,18500,20000,19500,18000,16500,14500], roi=[58,67,72,80,82,80,86,97,94,86,78,69]),
        2026: dict(clicks=[518,558,608,1673,0,0,0,0,0,0,0,0], cost=[3944,4248,4631,12122,0,0,0,0,0,0,0,0], conv=[12,13,14,34,0,0,0,0,0,0,0,0], leads=[7,7,8,23,0,0,0,0,0,0,0,0], apt=[3,4,4,9,0,0,0,0,0,0,0,0], cust=[1,1,2,3,0,0,0,0,0,0,0,0], sales=[15000,16500,17500,22277,0,0,0,0,0,0,0,0], roi=[64,74,80,84,0,0,0,0,0,0,0,0]),
    },
}

def _default_monthly():
    return dict(clicks=[0]*12, cost=[0]*12, conv=[0]*12, leads=[0]*12,
                apt=[0]*12, cust=[0]*12, sales=[0]*12, roi=[0]*12)

def get_campaign_data() -> list:
    """
    Returns list of campaigns.
    TO CONNECT REAL DATA: replace with your DB query.
    Each dict needs: name, highlight (bool)
    """
    return MOCK_CAMPAIGNS


def get_campaign_trend(campaign: str, from_month: int, from_year: int,
                        to_month: int, to_year: int) -> dict:
    """
    Returns aggregated totals + monthly arrays for the selected range.
    TO CONNECT REAL DATA: replace with your DB query.
    Returns dict with: clicks, cost, conv, leads, apt, cust, sales, roi,
                       and *_monthly / *_monthly_ly lists for the trend chart.
    """
    def get_months(fm, fy, tm, ty):
        r = []
        m, y = fm, fy
        while y < ty or (y == ty and m <= tm):
            r.append((m, y))
            m += 1
            if m > 11: m = 0; y += 1
        return r

    months    = get_months(from_month, from_year, to_month, to_year)
    ly_months = [(m, y-1) for m, y in months]

    d    = MOCK_CAMP_MONTHLY.get(campaign, {})
    def val(m, y, field): return (d.get(y) or _default_monthly()).get(field, [0]*12)[m]

    result = dict(clicks=0, cost=0, conv=0, leads=0, apt=0, cust=0, sales=0, roi=0)
    for field in result:
        result[field] = sum(val(m, y, field) for m, y in months)

    for field in ["clicks","cost","conv","leads","apt","sales","roi"]:
        result[f"{field}_monthly"]    = [val(m, y, field) for m, y in months]
        result[f"{field}_monthly_ly"] = [val(m, y, field) for m, y in ly_months]

    cpc = result["cost"] / result["conv"] if result["conv"] else 0
    result["cpc"] = round(cpc)
    return result


# ── Campaign performance mock data ────────────────────────────────────────────
def _mk_trend(base_clicks, base_cost, base_conv, base_leads, base_apt, base_cust, base_sales, base_roi):
    import random
    trend = {}
    for yr in [2024, 2025, 2026]:
        f = 0.85 if yr == 2024 else (1.0 if yr == 2025 else 1.12)
        months_count = 4 if yr == 2026 else 12
        trend[yr] = {
            "clicks": [max(0, int(base_clicks * f * (0.8 + 0.4*(m/11)))) if m < months_count else 0 for m in range(12)],
            "cost":   [max(0, int(base_cost   * f * (0.8 + 0.4*(m/11)))) if m < months_count else 0 for m in range(12)],
            "conv":   [max(0, int(base_conv   * f * (0.8 + 0.4*(m/11)))) if m < months_count else 0 for m in range(12)],
            "leads":  [max(0, int(base_leads  * f * (0.8 + 0.4*(m/11)))) if m < months_count else 0 for m in range(12)],
            "apt":    [max(0, int(base_apt    * f * (0.8 + 0.4*(m/11)))) if m < months_count else 0 for m in range(12)],
            "cust":   [max(0, int(base_cust   * f * (0.8 + 0.4*(m/11)))) if m < months_count else 0 for m in range(12)],
            "sales":  [max(0, int(base_sales  * f * (0.8 + 0.4*(m/11)))) if m < months_count else 0 for m in range(12)],
            "roi":    [round(base_roi * f * (0.9 + 0.2*(m/11)), 1) if m < months_count else 0 for m in range(12)],
        }
    return trend

MOCK_CAMPAIGNS = [
    dict(name="(TWC) LifeSource Brand",         trend=_mk_trend(1431,2209,110,58,25,6,47427,2046)),
    dict(name="AZ - Tucson Single Form",         trend=_mk_trend(224,3164,15,8,3,0,0,-100)),
    dict(name="Arizona Single Form",             trend=_mk_trend(1430,16157,52,22,5,0,0,-100)),
    dict(name="Bay Area Single Form",            trend=_mk_trend(794,9648,33,25,5,1,7072,-27)),
    dict(name="Central Coast Single Form",       trend=_mk_trend(137,2668,8,1,1,0,0,-100)),
    dict(name="Competitors - USA",               trend=_mk_trend(964,9205,28,25,9,0,0,-100)),
    dict(name="Demand Gen - Prospecting",        trend=_mk_trend(24650,15524,56,6,2,1,150,-99)),
    dict(name="Fresno Single Form",              trend=_mk_trend(193,2392,5,4,0,0,0,-100)),
    dict(name="IE - Palm Springs Single Form",   trend=_mk_trend(100,1723,6,1,1,0,0,-100)),
    dict(name="Inland Empire Single Form",       trend=_mk_trend(441,4998,24,14,2,0,0,-100)),
    dict(name="Las Vegas Single Form",           trend=_mk_trend(414,5436,25,11,2,1,6453,19)),
    dict(name="Orange County Single Form",       trend=_mk_trend(910,11060,37,11,9,0,0,-100)),
    dict(name="PMAX 1 - LA",                    trend=_mk_trend(1673,12121,34,23,9,3,22277,84)),
    dict(name="PMAX 2 - NoCal",                 trend=_mk_trend(3049,13006,65,36,10,1,6572,-49)),
    dict(name="Pasadena Single Form",            trend=_mk_trend(1152,13657,65,25,5,2,8133,-40)),
    dict(name="RLSA - All",                      trend=_mk_trend(273,3055,14,6,2,1,7794,155)),
    dict(name="Sacramento Single Form",          trend=_mk_trend(598,8104,32,12,6,0,0,-100)),
    dict(name="San Antonio Single Form",         trend=_mk_trend(521,6678,34,15,6,0,0,-100)),
    dict(name="San Diego Single Form",           trend=_mk_trend(722,9407,35,15,3,0,0,-100)),
    dict(name="Ventura County Single Form",      trend=_mk_trend(264,4112,19,7,3,2,16532,302)),
]


def get_campaign_data() -> list:
    """
    Returns list of campaign dicts with monthly trend data.
    TO CONNECT REAL DATA: replace return with your DB query.
    Each dict needs: name, trend (dict of year -> dict of field -> list of 12 monthly values)
    Fields: clicks, cost, conv, leads, apt, cust, sales, roi
    """
    # ── Replace with real DB query ─────────────────────────────────────────
    return MOCK_CAMPAIGNS
    # ──────────────────────────────────────────────────────────────────────
