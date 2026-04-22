# v2.0
import streamlit as st
from datetime import date, timedelta
import calendar
from data import get_data, get_roi_data, get_regional_data, get_campaign_data, CAMPAIGNS

st.set_page_config(page_title="Daily Report", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .metric-card { background:#ffffff; border:0.5px solid #e5e7eb; border-radius:10px; overflow:hidden; min-height:160px; margin-bottom:4px; }
    .metric-accent { height:3px; }
    .accent-blue { background:#378ADD; }
    .accent-teal { background:#1D9E75; }
    .metric-body { padding:10px 12px; }
    .metric-label { font-size:10px; color:#6b7280; margin:0 0 3px; text-transform:uppercase; letter-spacing:0.05em; }
    .metric-value { font-size:22px; font-weight:600; color:#111827; margin:0; line-height:1.1; }
    .metric-sub { font-size:10px; color:#9ca3af; margin:3px 0 0; }
    .pace-row { font-size:10px; color:#185FA5; margin-top:6px; padding-top:6px; border-top:0.5px solid #e5e7eb; }
    .pace-projected { font-weight:600; }
    .badge-row { display:flex; gap:6px; margin-top:6px; flex-wrap:wrap; }
    .badge { font-size:10px; padding:2px 7px; border-radius:20px; font-weight:500; white-space:nowrap; }
    .badge-mtd { background:#EFF6FF; color:#1e40af; }
    .badge-full { background:#F0FDF4; color:#166534; }
    .badge-budget { background:#FDF4FF; color:#6b21a8; }
    div[data-testid="stHorizontalBlock"] { gap:8px; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def projected(value, day, days_in_month):
    if day == 0: return 0
    return round((value / day) * days_in_month)

def metric_card(label, value, accent="blue", sub=None, pace_val=None,
                days_left=None, ly_mtd=None, ly_full=None, budget=None):
    sub_html  = f'<div class="metric-sub">{sub}</div>' if sub else ""
    pace_html = (
        f'<div class="pace-row">&#8594; Month-end: <span class="pace-projected">{pace_val}</span> ({days_left}d)</div>'
    ) if pace_val is not None else ""
    badges = ""
    has_badge = ly_mtd is not None or ly_full is not None or budget is not None
    if has_badge:
        badges = '<div class="badge-row">'
        if ly_mtd is not None:
            badges += f'<span class="badge badge-mtd">LY MTD: {ly_mtd}</span>'
        if ly_full is not None:
            badges += f'<span class="badge badge-full">LY Full: {ly_full}</span>'
        if budget is not None:
            badges += f'<span class="badge badge-budget">Budget: {budget}</span>'
        badges += '</div>'
    st.markdown(
        f'<div class="metric-card"><div class="metric-accent accent-{accent}"></div>'
        f'<div class="metric-body"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>{sub_html}{badges}{pace_html}</div></div>',
        unsafe_allow_html=True
    )


# ── Dates ─────────────────────────────────────────────────────────────────────
today         = date.today()
yesterday     = today - timedelta(days=1)
day_of_month  = today.day
days_in_month = calendar.monthrange(today.year, today.month)[1]
days_left     = days_in_month - day_of_month
month_name    = today.strftime("%b")
year          = today.year
last_year     = year - 1
roi_start     = today.replace(day=1)
roi_end       = yesterday


# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_date = st.columns([3, 1])
with col_title:
    st.markdown("# Daily Report")
    st.markdown("## Performance Overview")
with col_date:
    st.markdown(
        f"<div style='text-align:right;color:#6b7280;padding-top:16px;'>{today.strftime('%a, %b %d %Y')}</div>",
        unsafe_allow_html=True
    )


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈 Today", "🏢 Regional Offices", "📊 Campaign Performance"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Daily KPIs + ROI Charts
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    campaign = st.selectbox("Campaign", options=list(CAMPAIGNS.keys()), format_func=lambda x: CAMPAIGNS[x])

    try:
        d = get_data(campaign)

    except Exception as e:
        import traceback
        st.error(f"❌ Could not load data: {e}")
        st.code(traceback.format_exc())
        empty_ly = dict(conversions=0,cost=0,leads=0,appointments=0,customers=0,
                        cost_per_lead=0,cost_per_apt=0,roi=0)
        d = dict(conversions=0,invoca=0,form=0,cost=0,budget=0,
                 leads=0,crm_invoca=0,crm_form=0,appointments=0,customers=0,
                 cost_per_lead=0,cost_per_apt=0,roi=0,
                 ly_mtd=empty_ly, ly_full=empty_ly)

    ly  = d.get("ly_mtd",  {})
    lyf = d.get("ly_full", {})

    # Row 1: Conversions, Cost, CRM Leads, Appointments, Customers
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_card("Conversions", f"{d['conversions']:,}", "blue",
            f"Invoca {d['crm_invoca']:,} · Form {d['crm_form']:,}",
            f"{projected(d['conversions'], day_of_month, days_in_month):,}", days_left,
            ly_mtd=f"{ly.get('conversions',0):,}", ly_full=f"{lyf.get('conversions',0):,}")
    with c2:
        metric_card("Cost", f"${d['cost']:,.0f}", "blue", None,
            f"${projected(d['cost'], day_of_month, days_in_month):,.0f}", days_left,
            ly_mtd=None, ly_full=None,
            budget=f"${d.get('budget',0):,.0f}")
    with c3:
        metric_card("CRM Leads", f"{d['leads']:,}", "teal",
            f"Invoca {d['crm_invoca']:,} · Form {d['crm_form']:,}",
            f"{projected(d['leads'], day_of_month, days_in_month):,}", days_left,
            ly_mtd=f"{ly.get('leads',0):,}", ly_full=f"{lyf.get('leads',0):,}")
    with c4:
        metric_card("Appointments", f"{d['appointments']:,}", "teal", None,
            f"{projected(d['appointments'], day_of_month, days_in_month):,}", days_left,
            ly_mtd=f"{ly.get('appointments',0):,}", ly_full=f"{lyf.get('appointments',0):,}")
    with c5:
        metric_card("Customers", f"{d['customers']:,}", "teal", None, None, None,
            ly_mtd=f"{ly.get('customers',0):,}", ly_full=f"{lyf.get('customers',0):,}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    roi_col1, roi_col2 = st.columns([3, 1])
    with roi_col1:
        st.markdown("### MTD & Comparison")
    with roi_col2:
        st.markdown(
            f"<div style='text-align:right;color:#6b7280;padding-top:8px;font-size:12px;'>"
            f"{month_name} 1–{yesterday.day}, {year} vs {last_year}</div>",
            unsafe_allow_html=True
        )

    is_all = (campaign == "all")
    hint = "Showing all campaigns MTD — select a specific campaign to see monthly comparison" if is_all \
           else f"MTD & monthly comparison for {CAMPAIGNS[campaign]}"
    st.caption(hint)

    roi = get_roi_data(campaign, roi_start, roi_end)
    chart_type = "bar" if is_all else "line"

    if is_all:
        labels    = list(CAMPAIGNS.values())
        camp_keys = list(CAMPAIGNS.keys())
        def series(field):
            ty = [get_roi_data(k, roi_start, roi_end)["ty"][field] for k in camp_keys]
            ly = [get_roi_data(k, roi_start, roi_end)["ly"][field] for k in camp_keys]
            return ty, ly
    else:
        # Daily labels: Apr 1, Apr 2 ... Apr (yesterday)
        labels = [f"{month_name} {d}" for d in range(1, yesterday.day + 1)]
        def series(field):
            return roi["ty_daily"][field], roi["ly_daily"][field]

    conv_ty,  conv_ly  = series("conversions")
    cost_ty,  cost_ly  = series("cost")
    leads_ty, leads_ly = series("leads")
    appts_ty, appts_ly = series("appointments")
    cust_ty,  cust_ly  = series("customers")
    cpl_ty,   cpl_ly   = series("cost_per_lead")
    cpa_ty,   cpa_ly   = series("cost_per_appointment")
    roi_ty,   roi_ly   = series("roi")

    # ── MTD Charts ────────────────────────────────────────────────────────────
    is_all = (campaign == "all")
    camp_keys  = list(CAMPAIGNS.keys())
    camp_names = list(CAMPAIGNS.values())

    if is_all:
        # Bar charts: all campaigns side by side
        def get_series(field_ty, field_ly):
            ty_vals, ly_vals = [], []
            for k in camp_keys:
                r = get_roi_data(k, roi_start, roi_end)
                ty_vals.append(r["ty"].get(field_ty, 0))
                ly_vals.append(r["ly"].get(field_ly, 0))
            return ty_vals, ly_vals
        labels = camp_names
    else:
        # Single campaign: show TY vs LY as 2 bars only
        def get_series(field_ty, field_ly):
            r = get_roi_data(campaign, roi_start, roi_end)
            return [r["ty"].get(field_ty, 0)], [r["ly"].get(field_ly, 0)]
        labels = [CAMPAIGNS[campaign]]

    conv_ty,  conv_ly  = get_series("conversions",         "conversions")
    cost_ty,  cost_ly  = get_series("cost",                "cost")
    leads_ty, leads_ly = get_series("leads",               "leads")
    apt_ty,   apt_ly   = get_series("appointments",        "appointments")
    cust_ty,  cust_ly  = get_series("customers",           "customers")
    cpl_ty,   cpl_ly   = get_series("cost_per_lead",       "cost_per_lead")
    cpa_ty,   cpa_ly   = get_series("cost_per_appointment","cost_per_appointment")
    roi_ty,   roi_ly   = get_series("roi",                 "roi")

    # ── Gauge data for Leads and Appointments ────────────────────────────────
    g_leads_ty   = d.get("leads", 0)
    g_apt_ty     = d.get("appointments", 0)
    lm_d         = d.get("lm_full", {})
    g_leads_lm   = int(lm_d.get("leads", 0))        # Last month full
    g_apt_lm     = int(lm_d.get("appointments", 0)) # Last month full
    ly_d         = d.get("ly_mtd", {})
    g_leads_ly   = int(ly_d.get("leads", 0))         # Last year MTD
    g_apt_ly     = int(ly_d.get("appointments", 0))  # Last year MTD
    g_leads_pace = projected(g_leads_ty, day_of_month, days_in_month)
    g_apt_pace   = projected(g_apt_ty,   day_of_month, days_in_month)
    # Use LM Full as gauge target
    g_leads_lyf  = g_leads_lm
    g_apt_lyf    = g_apt_lm

    # Gauge arc calculation (semicircle = 251.3 total length)
    ARC = 251.3
    def arc_offset(val, total):
        if total == 0: return ARC
        pct = min(val / total, 1.0)
        return round(ARC - pct * ARC, 1)

    # Leads gauge
    l_total   = max(g_leads_lyf, g_leads_pace, 1)
    l_ty_off  = arc_offset(g_leads_ty,   l_total)
    l_pace_off= arc_offset(g_leads_pace, l_total)
    l_ly_off  = arc_offset(g_leads_ly,   l_total)
    l_pct     = round(g_leads_ty / g_leads_lyf * 100) if g_leads_lyf else 0
    l_pace_pct= round(g_leads_pace / g_leads_lyf * 100) if g_leads_lyf else 0

    # Appointments gauge
    a_total   = max(g_apt_lyf, g_apt_pace, 1)
    a_ty_off  = arc_offset(g_apt_ty,   a_total)
    a_pace_off= arc_offset(g_apt_pace, a_total)
    a_ly_off  = arc_offset(g_apt_ly,   a_total)
    a_pct     = round(g_apt_ty / g_apt_lyf * 100) if g_apt_lyf else 0
    a_pace_pct= round(g_apt_pace / g_apt_lyf * 100) if g_apt_lyf else 0

    gauge_html = f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:20px;">

      <div style="background:#fff;border:0.5px solid #e5e7eb;border-radius:10px;padding:16px;">
        <div style="font-size:11px;font-weight:500;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:2px;">Leads — MTD Pace</div>
        <div style="font-size:10px;color:#9ca3af;margin-bottom:10px;">Comparing with Last Month Full: <strong style="color:#BA7517;">{g_leads_lm:,}</strong></div>
        <svg viewBox="0 0 200 115" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:240px;display:block;margin:0 auto;">
          <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#f3f4f6" stroke-width="18" stroke-linecap="round"/>
          <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#9FE1CB" stroke-width="18" stroke-linecap="round" stroke-dasharray="{ARC}" stroke-dashoffset="{l_pace_off}" opacity="0.5"/>
          <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#1D9E75" stroke-width="18" stroke-linecap="round" stroke-dasharray="{ARC}" stroke-dashoffset="{l_ty_off}"/>
          <text x="100" y="83" text-anchor="middle" font-size="22" font-weight="600" fill="#111827">{l_pct}%</text>
          <text x="100" y="98" text-anchor="middle" font-size="9" fill="#9ca3af">of last month</text>
          <text x="20" y="113" text-anchor="middle" font-size="9" fill="#9ca3af">0</text>
          <text x="180" y="113" text-anchor="middle" font-size="9" fill="#BA7517">{g_leads_lm:,}</text>
        </svg>
        <div style="display:flex;justify-content:space-around;margin-top:10px;padding-top:8px;border-top:0.5px solid #e5e7eb;">
          <div style="text-align:center;">
            <div style="font-size:16px;font-weight:600;color:#1D9E75;">{g_leads_ty:,}</div>
            <div style="font-size:10px;color:#9ca3af;margin-top:2px;">TY MTD</div>
          </div>
          <div style="text-align:center;">
            <div style="font-size:16px;font-weight:600;color:#9FE1CB;">{g_leads_pace:,}</div>
            <div style="font-size:10px;color:#9ca3af;margin-top:2px;">TY Pace</div>
          </div>
          <div style="text-align:center;">
            <div style="font-size:16px;font-weight:600;color:#BA7517;">{g_leads_lm:,}</div>
            <div style="font-size:10px;color:#9ca3af;margin-top:2px;">LM Full</div>
          </div>
        </div>
      </div>

      <div style="background:#fff;border:0.5px solid #e5e7eb;border-radius:10px;padding:16px;">
        <div style="font-size:11px;font-weight:500;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:2px;">Appointments — MTD Pace</div>
        <div style="font-size:10px;color:#9ca3af;margin-bottom:10px;">Comparing with Last Month Full: <strong style="color:#BA7517;">{g_apt_lm:,}</strong></div>
        <svg viewBox="0 0 200 115" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:240px;display:block;margin:0 auto;">
          <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#f3f4f6" stroke-width="18" stroke-linecap="round"/>
          <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#9FE1CB" stroke-width="18" stroke-linecap="round" stroke-dasharray="{ARC}" stroke-dashoffset="{a_pace_off}" opacity="0.5"/>
          <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#1D9E75" stroke-width="18" stroke-linecap="round" stroke-dasharray="{ARC}" stroke-dashoffset="{a_ty_off}"/>
          <text x="100" y="83" text-anchor="middle" font-size="22" font-weight="600" fill="#111827">{a_pct}%</text>
          <text x="100" y="98" text-anchor="middle" font-size="9" fill="#9ca3af">of last month</text>
          <text x="20" y="113" text-anchor="middle" font-size="9" fill="#9ca3af">0</text>
          <text x="180" y="113" text-anchor="middle" font-size="9" fill="#BA7517">{g_apt_lm:,}</text>
        </svg>
        <div style="display:flex;justify-content:space-around;margin-top:10px;padding-top:8px;border-top:0.5px solid #e5e7eb;">
          <div style="text-align:center;">
            <div style="font-size:16px;font-weight:600;color:#1D9E75;">{g_apt_ty:,}</div>
            <div style="font-size:10px;color:#9ca3af;margin-top:2px;">TY MTD</div>
          </div>
          <div style="text-align:center;">
            <div style="font-size:16px;font-weight:600;color:#9FE1CB;">{g_apt_pace:,}</div>
            <div style="font-size:10px;color:#9ca3af;margin-top:2px;">TY Pace</div>
          </div>
          <div style="text-align:center;">
            <div style="font-size:16px;font-weight:600;color:#BA7517;">{g_apt_lm:,}</div>
            <div style="font-size:10px;color:#9ca3af;margin-top:2px;">LM Full</div>
          </div>
        </div>
      </div>

    </div>
    <div style="display:flex;gap:16px;margin-bottom:16px;justify-content:center;">
      <span style="display:flex;align-items:center;gap:5px;font-size:11px;color:#6b7280;"><span style="width:12px;height:4px;background:#1D9E75;border-radius:2px;display:inline-block;"></span>TY MTD (actual)</span>
      <span style="display:flex;align-items:center;gap:5px;font-size:11px;color:#6b7280;"><span style="width:12px;height:4px;background:#9FE1CB;border-radius:2px;display:inline-block;"></span>TY Pace (projected month-end)</span>
      <span style="display:flex;align-items:center;gap:5px;font-size:11px;color:#6b7280;"><span style="width:12px;height:4px;background:#BA7517;border-radius:2px;display:inline-block;"></span>Last Month Full (target)</span>
    </div>
    """
    st.components.v1.html(gauge_html, height=320, scrolling=False)

