# v2.0
import streamlit as st
from datetime import date, timedelta
import calendar
from data import get_data, get_roi_data, get_regional_data, get_campaign_data, get_campaigns, get_regional_detail

st.set_page_config(page_title="Google Daily Report", page_icon="📊", layout="wide")

# Cache clear - shown in sidebar
with st.sidebar:
    st.markdown("### Settings")
    if st.button("🔄 Refresh Data", help="Clear cache and reload Excel data"):
        st.cache_data.clear()
        st.rerun()
    st.caption("Click after uploading new Excel to GitHub")
    # Show last modified time of Excel
    import os
    excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard_data.xlsx")
    if os.path.exists(excel_path):
        import datetime
        mtime = os.path.getmtime(excel_path)
        st.caption(f"Excel last updated: {datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')}")

# Load campaigns dynamically from Excel
try:
    CAMPAIGNS = get_campaigns()
except:
    CAMPAIGNS = {"all": "All campaigns"}

# Short display names for charts
CAMP_SHORT = {
    "(TWC) LifeSource Brand":               "Brand",
    "AZ - Tucson Single Form":              "Tucson",
    "Arizona Single Form":                  "Arizona",
    "Bay Area Single Form":                 "Bay Area",
    "Competitors - USA":                    "Competitors",
    "Competitors - USA New":                "Competitors New",
    "Demand Gen -Prospecting and Retargeting": "Demand Gen",
    "Fresno Single Form":                   "Fresno",
    "IE - Palm Springs Single Form":        "Palm Springs",
    "Inland Empire Single Form":            "Inland Empire",
    "Las Vegas Single Form":                "Las Vegas",
    "Orange County Single Form":            "Orange County",
    "PMAX 1 - LA":                          "Pmax1",
    "PMAX 2 - NoCal":                       "Pmax2",
    "Pasadena Single Form":                 "Pasadena",
    "RLSA - All":                           "RLSA",
    "Sacramento Single Form":               "Sacramento",
    "San Antonio Single Form":              "San Antonio",
    "San Diego Single Form":                "San Diego",
    "Ventura County Single Form":           "Ventura",
}
def short(name): return CAMP_SHORT.get(name, name)

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
    .badge { font-size:12px; padding:3px 9px; border-radius:20px; font-weight:600; white-space:nowrap; }
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
    col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.markdown('<img src="data:image/png;base64,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" style="width:120px;margin-top:6px;">', unsafe_allow_html=True)
with col_title:
    st.markdown("# Google Daily Report")
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
    camp_options = list(CAMPAIGNS.values())
    selected_camp = st.selectbox("Campaign", options=camp_options)
    campaign = selected_camp  # use full name directly

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
            f"Invoca {d['invoca']:,} · Form {d['form']:,}",
            f"{projected(d['conversions'], day_of_month, days_in_month):,}", days_left,
            ly_mtd=f"{ly.get('conversions',0):,}", ly_full=f"{lyf.get('conversions',0):,}")
    with c2:
        cost_val   = d.get("cost", 0)
        budget_val = d.get("budget", 0)
        pct_used   = round(cost_val / budget_val * 100) if budget_val > 0 else 0
        pace_cost  = projected(cost_val, day_of_month, days_in_month)
        pct_pace   = round(pace_cost / budget_val * 100) if budget_val > 0 else 0
        bar_color  = "#991b1b" if pct_pace > 100 else "#BA7517" if pct_pace > 85 else "#1D9E75"
        budget_html = (
            f'<div class="badge-row" style="margin-top:6px;">' +
            f'<span class="badge badge-budget">Budget: ${budget_val:,.0f}</span>' +
            f'</div>' +
            f'<div style="margin-top:6px;">' +
            f'<div style="display:flex;justify-content:space-between;font-size:11px;color:#6b7280;margin-bottom:3px;">' +
            f'<span>Spent {pct_used}% of budget</span>' +
            f'<span style="color:{bar_color};font-weight:600;">Pace: {pct_pace}%</span>' +
            f'</div>' +
            f'<div style="height:6px;background:#f3f4f6;border-radius:3px;overflow:hidden;">' +
            f'<div style="width:{min(pct_pace,100)}%;height:100%;background:{bar_color};border-radius:3px;transition:width 0.3s;"></div>' +
            f'</div>' +
            f'</div>'
        ) if budget_val > 0 else ""
        st.markdown(
            f'<div class="metric-card"><div class="metric-accent accent-blue"></div>' +
            f'<div class="metric-body"><div class="metric-label">Cost</div>' +
            f'<div class="metric-value">${cost_val:,.0f}</div>' +
            f'<div class="pace-row">&#8594; Month-end: <span class="pace-projected">${pace_cost:,.0f}</span> ({days_left}d)</div>' +
            budget_html +
            f'</div></div>',
            unsafe_allow_html=True
        )
    with c3:
        metric_card("CRM Leads", f"{d['leads']:,}", "teal",
            f"Invoca {d['crm_invoca']:,} · Form {d['crm_form']:,}",
            f"{projected(d['leads'], day_of_month, days_in_month):,}", days_left,
            ly_mtd=f"{ly.get('leads',0):,}", ly_full=f"{lyf.get('leads',0):,}")
    with c4:
        metric_card("Appointments", f"{d['appointments']:,}", "teal", None,
            f"{projected(d['appointments'], day_of_month, days_in_month):,}", days_left,
            ly_mtd=f"{ly.get('appointments',0):,}", ly_full=None)
    with c5:
        metric_card("Customers", f"{d['customers']:,}", "teal", None, None, None,
            ly_mtd=f"{ly.get('customers',0):,}", ly_full=None)

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

    st.markdown("### 📈 Monthly Pace vs Last Month")
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
            <div style="font-size:10px;color:#9ca3af;margin-top:2px;">This Month MTD</div>
          </div>
          <div style="text-align:center;">
            <div style="font-size:16px;font-weight:600;color:#9FE1CB;">{g_leads_pace:,}</div>
            <div style="font-size:10px;color:#9ca3af;margin-top:2px;">Month-end Pace</div>
          </div>
          <div style="text-align:center;">
            <div style="font-size:16px;font-weight:600;color:#BA7517;">{g_leads_lm:,}</div>
            <div style="font-size:10px;color:#9ca3af;margin-top:2px;">Last Month Full</div>
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
            <div style="font-size:10px;color:#9ca3af;margin-top:2px;">This Month MTD</div>
          </div>
          <div style="text-align:center;">
            <div style="font-size:16px;font-weight:600;color:#9FE1CB;">{g_apt_pace:,}</div>
            <div style="font-size:10px;color:#9ca3af;margin-top:2px;">Month-end Pace</div>
          </div>
          <div style="text-align:center;">
            <div style="font-size:16px;font-weight:600;color:#BA7517;">{g_apt_lm:,}</div>
            <div style="font-size:10px;color:#9ca3af;margin-top:2px;">Last Month Full</div>
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

    st.markdown("### 📊 MTD & Comparison with Last Year")
    # ── Alert Lists: campaigns with fewer leads or appointments than LY ─────
    all_camps = get_campaigns()
    leads_down = []
    leads_up   = []
    apts_down  = []
    apts_up    = []
    for camp_name in all_camps.values():
        try:
            cd = get_data(camp_name)
            if cd.get("cost", 0) == 0:
                continue  # skip inactive campaigns
            ty_leads = cd.get("leads", 0)
            ly_leads = cd.get("ly_mtd", {}).get("leads", 0)
            ty_apt   = cd.get("appointments", 0)
            ly_apt   = cd.get("ly_mtd", {}).get("appointments", 0)
            if camp_name == "All campaigns":
                continue
            if ly_leads > 0:
                diff = abs(ty_leads - ly_leads)
                pct  = round(diff / ly_leads * 100)
                if ty_leads < ly_leads:
                    leads_down.append((camp_name, ty_leads, ly_leads, diff, pct))
                elif ty_leads > ly_leads:
                    leads_up.append((camp_name, ty_leads, ly_leads, diff, pct))
            if ly_apt > 0:
                diff = abs(ty_apt - ly_apt)
                pct  = round(diff / ly_apt * 100)
                if ty_apt < ly_apt:
                    apts_down.append((camp_name, ty_apt, ly_apt, diff, pct))
                elif ty_apt > ly_apt:
                    apts_up.append((camp_name, ty_apt, ly_apt, diff, pct))
        except:
            continue

    leads_down.sort(key=lambda x: x[4], reverse=True)
    leads_up.sort(key=lambda x: x[4], reverse=True)
    apts_down.sort(key=lambda x: x[4], reverse=True)
    apts_up.sort(key=lambda x: x[4], reverse=True)

    if leads_down or apts_down:
        al1, al2 = st.columns(2)
        with al1:
            if leads_up:
                items_up = "".join([
                    f'<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:0.5px solid #f3f4f6;">' +
                    f'<span style="font-size:14px;color:#111827;font-weight:600;">{name}</span>' +
                    f'<span style="font-size:13px;"><span style="color:#1D9E75;font-weight:700;">{ty}</span>' +
                    f'<span style="color:#9ca3af;"> vs </span><span style="color:#6b7280;font-weight:600;">{ly}</span>' +
                    f'<span style="background:#d1fae5;color:#065f46;font-size:12px;padding:2px 8px;border-radius:10px;margin-left:8px;font-weight:600;">▲{pct}%</span></span></div>'
                    for name, ty, ly, diff, pct in leads_up
                ])
                st.markdown(
                    f'<div style="background:#fff;border:0.5px solid #86efac;border-radius:10px;padding:14px;margin-bottom:12px;">' +
                    f'<div style="font-size:11px;font-weight:600;color:#065f46;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px;">✅ Leads Above Last Year MTD</div>' +
                    items_up + '</div>', unsafe_allow_html=True
                )
            if leads_down:
                items = "".join([
                    f'<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:0.5px solid #f3f4f6;">' +
                    f'<span style="font-size:14px;color:#111827;font-weight:600;">{name}</span>' +
                    f'<span style="font-size:13px;"><span style="color:#1D9E75;font-weight:700;">{ty}</span>' +
                    f'<span style="color:#9ca3af;"> vs </span><span style="color:#6b7280;font-weight:600;">{ly}</span>' +
                    f'<span style="background:#fee2e2;color:#991b1b;font-size:12px;padding:2px 8px;border-radius:10px;margin-left:8px;font-weight:600;">▼{pct}%</span></span></div>'
                    for name, ty, ly, diff, pct in leads_down
                ])
                st.markdown(
                    f'<div style="background:#fff;border:0.5px solid #fca5a5;border-radius:10px;padding:14px;">' +
                    f'<div style="font-size:11px;font-weight:600;color:#991b1b;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px;">⚠ Leads Below Last Year MTD</div>' +
                    items + '</div>', unsafe_allow_html=True
                )
            else:
                st.markdown('<div style="background:#f0fdf4;border:0.5px solid #86efac;border-radius:10px;padding:14px;font-size:12px;color:#166534;">✓ All campaigns leads are above last year</div>', unsafe_allow_html=True)

        with al2:
            if apts_up:
                items_up2 = "".join([
                    f'<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:0.5px solid #f3f4f6;">' +
                    f'<span style="font-size:14px;color:#111827;font-weight:600;">{name}</span>' +
                    f'<span style="font-size:13px;"><span style="color:#1D9E75;font-weight:700;">{ty}</span>' +
                    f'<span style="color:#9ca3af;"> vs </span><span style="color:#6b7280;font-weight:600;">{ly}</span>' +
                    f'<span style="background:#d1fae5;color:#065f46;font-size:12px;padding:2px 8px;border-radius:10px;margin-left:8px;font-weight:600;">▲{pct}%</span></span></div>'
                    for name, ty, ly, diff, pct in apts_up
                ])
                st.markdown(
                    f'<div style="background:#fff;border:0.5px solid #86efac;border-radius:10px;padding:14px;margin-bottom:12px;">' +
                    f'<div style="font-size:11px;font-weight:600;color:#065f46;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px;">✅ Appointments Above Last Year MTD</div>' +
                    items_up2 + '</div>', unsafe_allow_html=True
                )
            if apts_down:
                items = "".join([
                    f'<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:0.5px solid #f3f4f6;">' +
                    f'<span style="font-size:14px;color:#111827;font-weight:600;">{name}</span>' +
                    f'<span style="font-size:13px;"><span style="color:#1D9E75;font-weight:700;">{ty}</span>' +
                    f'<span style="color:#9ca3af;"> vs </span><span style="color:#6b7280;font-weight:600;">{ly}</span>' +
                    f'<span style="background:#fee2e2;color:#991b1b;font-size:12px;padding:2px 8px;border-radius:10px;margin-left:8px;font-weight:600;">▼{pct}%</span></span></div>'
                    for name, ty, ly, diff, pct in apts_down
                ])
                st.markdown(
                    f'<div style="background:#fff;border:0.5px solid #fca5a5;border-radius:10px;padding:14px;">' +
                    f'<div style="font-size:11px;font-weight:600;color:#991b1b;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px;">⚠ Appointments Below Last Year MTD</div>' +
                    items + '</div>', unsafe_allow_html=True
                )
            else:
                st.markdown('<div style="background:#f0fdf4;border:0.5px solid #86efac;border-radius:10px;padding:14px;font-size:12px;color:#166534;">✓ All campaigns appointments are above last year</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # ── MTD & Comparison Charts ─────────────────────────────────────────────
    is_all = (campaign == "All campaigns")
    hint = "Showing all campaigns MTD — select a specific campaign to see monthly comparison" if is_all \
           else f"MTD & monthly comparison for {campaign}"
    st.caption(hint)

    roi = get_roi_data(campaign, roi_start, roi_end)
    chart_type = "bar" if is_all else "line"

    if is_all:
        labels     = list(CAMPAIGNS.values())
        camp_names = list(CAMPAIGNS.values())
        def series(field):
            ty = [get_roi_data(name, roi_start, roi_end)["ty"].get(field, 0) for name in camp_names]
            ly = [get_roi_data(name, roi_start, roi_end)["ly"].get(field, 0) for name in camp_names]
            return ty, ly
    else:
        # Single campaign: TY vs LY as 2 bars
        labels = [campaign]
        def series(field):
            ty = [roi["ty"].get(field, 0)]
            ly = [roi["ly"].get(field, 0)]
            return ty, ly

    conv_ty,  conv_ly  = series("conversions")
    cost_ty,  cost_ly  = series("cost")
    leads_ty, leads_ly = series("leads")
    appts_ty, appts_ly = series("appointments")
    cust_ty,  cust_ly  = series("customers")
    cpl_ty,   cpl_ly   = series("cost_per_lead")
    cpa_ty,   cpa_ly   = series("cost_per_appointment")
    # (roi not used in charts)
    all_camp_names = list(CAMPAIGNS.values())
    apt_ty,  apt_ly  = appts_ty, appts_ly


    st.markdown("---")

    # ── Bar Charts ─────────────────────────────────────────────────────────────
    is_all = (campaign == "All campaigns")
    camp_keys  = list(CAMPAIGNS.values())
    camp_names = list(CAMPAIGNS.values())

    all_camp_names = list(CAMPAIGNS.values())
    if is_all:
        def get_series(field_ty, field_ly):
            ty_vals, ly_vals = [], []
            for name in all_camp_names:
                r = get_roi_data(name, roi_start, roi_end)
                ty_vals.append(r["ty"].get(field_ty, 0))
                ly_vals.append(r["ly"].get(field_ly, 0))
            return ty_vals, ly_vals
        labels = [short(n) for n in all_camp_names]
    else:
        def get_series(field_ty, field_ly):
            r = get_roi_data(campaign, roi_start, roi_end)
            return [r["ty"].get(field_ty, 0)], [r["ly"].get(field_ly, 0)]
        labels = [campaign]

    conv_ty,  conv_ly  = get_series("conversions",         "conversions")
    cost_ty,  cost_ly  = get_series("cost",                "cost")
    leads_ty, leads_ly = get_series("leads",               "leads")
    apt_ty,   apt_ly   = get_series("appointments",        "appointments")
    cust_ty,  cust_ly  = get_series("customers",           "customers")
    cpl_ty,   cpl_ly   = get_series("cost_per_lead",       "cost_per_lead")
    cpa_ty,   cpa_ly   = get_series("cost_per_appointment","cost_per_appointment")

    chart_html = f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
      {"".join([
        f'<div style="background:#fff;border:0.5px solid #e5e7eb;border-radius:10px;padding:14px;{span}">'
        f'<div style="font-size:13px;font-weight:500;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">{title}</div>'
        f'<div style="display:flex;gap:12px;margin-bottom:8px;">'
        f'<span style="display:flex;align-items:center;gap:4px;font-size:12px;color:#6b7280;"><span style="width:10px;height:10px;border-radius:2px;background:{cy};display:inline-block;"></span>This year MTD</span>'
        f'<span style="display:flex;align-items:center;gap:4px;font-size:11px;color:#6b7280;"><span style="width:10px;height:10px;border-radius:2px;background:{lc};display:inline-block;"></span>Last year MTD</span>'
        f'</div><div style="position:relative;height:190px;"><canvas id="{cid}"></canvas></div></div>'
        for title,cid,cy,lc,span in [
            ("Conversions","c1","#378ADD","#B5D4F4",""),
            ("Cost","c2","#378ADD","#B5D4F4",""),
            ("CRM Leads","c3","#1D9E75","#9FE1CB",""),
            ("Appointments","c4","#1D9E75","#9FE1CB",""),
            ("Customers","c5","#1D9E75","#9FE1CB",""),
            ("Cost per Lead","c6","#534AB7","#AFA9EC",""),
            ("Cost per Appointment","c7","#534AB7","#AFA9EC","grid-column:span 2;"),
        ]
      ])}
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    const LABELS={labels};
    const CHARTS=[
      ["c1",{conv_ty},{conv_ly},"#378ADD","#B5D4F4"],
      ["c2",{cost_ty},{cost_ly},"#378ADD","#B5D4F4"],
      ["c3",{leads_ty},{leads_ly},"#1D9E75","#9FE1CB"],
      ["c4",{apt_ty},{apt_ly},"#1D9E75","#9FE1CB"],
      ["c5",{cust_ty},{cust_ly},"#1D9E75","#9FE1CB"],
      ["c6",{cpl_ty},{cpl_ly},"#534AB7","#AFA9EC"],
      ["c7",{cpa_ty},{cpa_ly},"#534AB7","#AFA9EC"],
    ];
    CHARTS.forEach(([cid,tyD,lyD,tyC,lyC])=>{{
      const opts={{responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:ctx=>' '+ctx.parsed.y.toLocaleString()}}}}}},
        scales:{{
          x:{{ticks:{{font:{{size:10}},autoSkip:false,maxRotation:30}},grid:{{display:false}}}},
          y:{{min:0,ticks:{{font:{{size:10}},callback:v=>v.toLocaleString()}},grid:{{color:"#f3f4f6"}}}}
        }}
      }};
      new Chart(document.getElementById(cid),{{type:'bar',data:{{labels:LABELS,datasets:[
        {{data:tyD,backgroundColor:tyC,borderRadius:4}},
        {{data:lyD,backgroundColor:lyC,borderRadius:4}},
      ]}},options:opts}});
    }});
    </script>
    """
    st.components.v1.html(chart_html, height=1150, scrolling=False)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Regional Offices
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    offices     = get_regional_data(roi_start, roi_end)
    total_ul    = sum(o["ul"]    for o in offices)
    total_nl    = sum(o["nl"]    for o in offices)
    total_apt   = sum(o["apt"]   for o in offices)
    total_quote = sum(o["quote"] for o in offices)
    total_cust  = sum(o["cust"]  for o in offices)
    total_sales = sum(o["sales"] for o in offices)
    total_nlc   = sum(o["nlc"]   for o in offices)
    total_nls   = sum(o["nl_sales"] for o in offices)

    r1, r2, r3, r4, r5 = st.columns(5)
    tab2_kpi_style = "style='min-height:80px !important;'"
    def small_card(label, value, accent):
        color = "#378ADD" if accent == "blue" else "#1D9E75"
        st.markdown(
            f'<div style="background:#fff;border:0.5px solid #e5e7eb;border-radius:10px;overflow:hidden;min-height:80px;display:flex;flex-direction:column;justify-content:center;">' +
            f'<div style="height:3px;background:{color};"></div>' +
            f'<div style="padding:10px 14px;text-align:center;">' +
            f'<div style="font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:0.06em;font-weight:500;margin-bottom:4px;">{label}</div>' +
            f'<div style="font-size:24px;font-weight:700;color:#111827;">{value}</div>' +
            f'</div></div>',
            unsafe_allow_html=True
        )
    with r1: small_card("Total Leads",  f"{total_ul:,}",                    "blue")
    with r2: small_card("Appointments", f"{total_apt:,}",                   "blue")
    with r3: small_card("Customers",    f"{total_cust:,}",                  "teal")
    with r4: small_card("Total Sales",  f"${float(total_sales or 0):,.0f}", "teal")
    with r5: small_card("Apt / Leads",  f"{round(total_apt/total_ul*100) if total_ul else 0}%", "teal")

    st.markdown("<br>", unsafe_allow_html=True)

    def money(n):
        try:
            v = float(n)
            return f"${v:,.2f}" if v == v else "$0.00"
        except:
            return "$0.00"

    COLORS = ["#378ADD","#1D9E75","#534AB7","#D85A30","#BA7517","#D4537E",
              "#639922","#888780","#E24B4A","#7F77DD","#5DCAA5","#F0997B",
              "#97C459","#EF9F27","#ED93B1","#B4B2A9"]

    detail_data = get_regional_detail()
    rows_html = ""
    pie_names = []
    pie_leads = []
    pie_sales = []

    # Calculate avg apt/leads and order/leads for color coding
    def to_float(s):
        try: return float(str(s).replace("%","").strip())
        except: return 0.0

    valid_al = [to_float(o.get("apt_leads","0")) for o in offices if to_float(o.get("apt_leads","0")) > 0]
    valid_ol = [to_float(o.get("order_leads","0")) for o in offices if to_float(o.get("order_leads","0")) > 0]
    avg_al = sum(valid_al)/len(valid_al) if valid_al else 0
    avg_ol = sum(valid_ol)/len(valid_ol) if valid_ol else 0

    # Sort by leads_pct descending
    offices_sorted = sorted(offices, key=lambda o: to_float(o.get("leads_pct","0")), reverse=True)

    for i, o in enumerate(offices_sorted):
        # Read % values directly from Excel — no calculation
        lp_str = str(o.get("leads_pct","0%"))
        sp_str = str(o.get("sales_pct","0%"))
        al_str = str(o.get("apt_leads","0%"))
        oa_str = str(o.get("order_apt","0%"))
        ol_str = str(o.get("order_leads","0%"))
        office_key = o["name"].replace(" ","_").replace("/","_")

        # For pie chart use numeric value
        try: lp_num = float(lp_str.replace("%",""))
        except: lp_num = 0
        try: sp_num = float(sp_str.replace("%",""))
        except: sp_num = 0

        pie_names.append(o["name"])
        pie_leads.append(round(lp_num, 1))
        pie_sales.append(round(sp_num, 1))

        # Color badges based on value
        def pct_badge(val_str, threshold, color):
            try:
                v = float(val_str.replace("%",""))
                if v >= threshold:
                    return f'<span style="font-size:10px;font-weight:500;padding:2px 6px;border-radius:4px;background:{color[0]};color:{color[1]};">{val_str}</span>'
            except: pass
            return f'<span style="font-size:11px;color:#374151;">{val_str}</span>'

        lp_badge = pct_badge(lp_str, 10, ("#d1fae5","#065f46"))
        sp_badge = pct_badge(sp_str, 10, ("#d1fae5","#065f46"))
        al_val = to_float(al_str)
        al_badge = pct_badge(al_str, avg_al, ("#d1fae5","#065f46")) if al_val >= avg_al and al_val > 0                    else f'<span style="font-size:11px;color:#374151;">{al_str}</span>'
        ol_val = to_float(ol_str)
        ol_badge = pct_badge(ol_str, avg_ol, ("#d1fae5","#065f46")) if ol_val >= avg_ol and ol_val > 0                    else f'<span style="font-size:11px;color:#374151;">{ol_str}</span>' 

        td = "text-align:right;padding:9px 12px;border-bottom:0.5px solid #f3f4f6;color:#374151;font-size:14px;"

        # Color bars for % columns
        try: lp_num = float(lp_str.replace("%","").strip())
        except: lp_num = 0
        try: sp_num = float(sp_str.replace("%","").strip())
        except: sp_num = 0
        bar_w_l = min(int(lp_num / 20 * 100), 100)
        bar_w_s = min(int(sp_num / 25 * 100), 100)
        bar_l = f'<div style="display:flex;align-items:center;gap:5px;justify-content:flex-end;"><div style="width:50px;height:5px;background:#f3f4f6;border-radius:3px;overflow:hidden;"><div style="width:{bar_w_l}%;height:100%;background:#378ADD;border-radius:3px;"></div></div>{lp_badge}</div>'
        bar_s = f'<div style="display:flex;align-items:center;gap:5px;justify-content:flex-end;"><div style="width:50px;height:5px;background:#f3f4f6;border-radius:3px;overflow:hidden;"><div style="width:{bar_w_s}%;height:100%;background:#1D9E75;border-radius:3px;"></div></div>{sp_badge}</div>'

        # Build detail rows for this office
        detail_rows = ""
        if o["name"] in detail_data:
            detail_rows = f'<tr id="detail_{office_key}" style="display:none;"><td colspan="14" style="padding:0;"><table style="width:100%;border-collapse:collapse;background:#f8fafc;font-size:11px;">'
            detail_rows += '<tr style="background:#e2e8f0;"><th style="text-align:left;padding:8px 16px;color:#475569;font-size:13px;">Campaign</th><th style="text-align:right;padding:8px 10px;color:#475569;font-size:13px;">Unique Leads</th><th style="text-align:right;padding:8px 10px;color:#475569;font-size:13px;">New Leads</th><th style="text-align:right;padding:8px 10px;color:#475569;font-size:13px;">Apt</th><th style="text-align:right;padding:8px 10px;color:#475569;font-size:13px;">Quote</th><th style="text-align:right;padding:8px 10px;color:#475569;font-size:13px;">Customers</th><th style="text-align:right;padding:8px 10px;color:#475569;font-size:13px;">Sales</th></tr>'
            sorted_detail = sorted(detail_data[o["name"]], key=lambda x: (-x["ul"], -x["sales"]))
            for d in sorted_detail:
                detail_rows += (
                    f'<tr style="border-bottom:0.5px solid #e2e8f0;font-size:13px;">' +
                    f'<td style="padding:7px 16px;color:#374151;font-size:13px;font-weight:500;">{d["campaign"]}</td>' +
                    f'<td style="text-align:right;padding:7px 10px;font-size:13px;">{d["ul"]}</td>' +
                    f'<td style="text-align:right;padding:7px 10px;font-size:13px;">{d["nl"]}</td>' +
                    f'<td style="text-align:right;padding:7px 10px;font-size:13px;">{d["apt"]}</td>' +
                    f'<td style="text-align:right;padding:7px 10px;font-size:13px;">{d["quote"]}</td>' +
                    f'<td style="text-align:right;padding:7px 10px;font-size:13px;">{d["cust"]}</td>' +
                    f'<td style="text-align:right;padding:7px 10px;font-size:13px;">${d["sales"]:,.0f}</td>' +
                    f'</tr>'
                )
            detail_rows += '</table></td></tr>'

        has_detail = o["name"] in detail_data
        expand_btn = f'<span onclick="toggleDetail(\'{office_key}\')" style="cursor:pointer;margin-left:6px;font-size:11px;color:#6b7280;" id="btn_{office_key}">{"▶" if has_detail else ""}</span>' if has_detail else ""

        rows_html += f"""<tr onclick="{'toggleDetail(\''+office_key+'\')' if has_detail else ''}" style="cursor:{'pointer' if has_detail else 'default'};">
          <td style="text-align:left;font-weight:500;padding:9px 12px;border-bottom:0.5px solid #f3f4f6;color:#111827;font-size:14px;">{o["name"]}{expand_btn}</td>
          <td style="{td}">{o["ul"]}</td>
          <td style="{td}">{o["nl"]}</td>
          <td style="{td}">{o["apt"]}</td>
          <td style="{td}">{o["quote"]}</td>
          <td style="{td}">{o["cust"]}</td>
          <td style="{td}">{money(o["sales"])}</td>
          <td style="{td}">{o["nlc"]}</td>
          <td style="{td}">{money(o["nl_sales"])}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;">{bar_l}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;">{bar_s}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;">{al_badge}</td>
          <td style="{td}">{oa_str}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;">{ol_badge}</td>
        </tr>""" + detail_rows

    th = "padding:10px 12px;font-size:12px;font-weight:500;letter-spacing:0.04em;text-transform:uppercase;white-space:nowrap;"
    date_label = f"{month_name} 1–{yesterday.day}, {year}"

    tab2_html = f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
      <span style="font-size:15px;font-weight:500;color:#111827;">Regional Office Performance</span>
      <span style="font-size:12px;color:#6b7280;background:#f9fafb;border:0.5px solid #e5e7eb;border-radius:8px;padding:5px 12px;">{date_label}</span>
    </div>
    <div style="width:100%;overflow-x:auto;margin-bottom:28px;">
    <table style="width:100%;border-collapse:collapse;font-size:12px;white-space:nowrap;">
      <thead><tr style="background:#111827;">
        <th style="{th}text-align:left;color:#ffffff;">Regional Office</th>
        <th style="{th}text-align:right;color:#9ca3af;">Unique Leads</th>
        <th style="{th}text-align:right;color:#9ca3af;">New Leads</th>
        <th style="{th}text-align:right;color:#9ca3af;">Apt</th>
        <th style="{th}text-align:right;color:#9ca3af;">Quote</th>
        <th style="{th}text-align:right;color:#9ca3af;">Customers</th>
        <th style="{th}text-align:right;color:#9ca3af;">Sales Amount</th>
        <th style="{th}text-align:right;color:#9ca3af;">NL Customers</th>
        <th style="{th}text-align:right;color:#9ca3af;">NL Sales</th>
        <th style="{th}text-align:right;color:#9ca3af;">Leads %</th>
        <th style="{th}text-align:right;color:#9ca3af;">Sales %</th>
        <th style="{th}text-align:right;color:#9ca3af;">Apt/Leads</th>
        <th style="{th}text-align:right;color:#9ca3af;">Order/Apt</th>
        <th style="{th}text-align:right;color:#9ca3af;">Order/Leads</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
      <tfoot><tr style="background:#f8f9fa;font-weight:600;border-top:0.5px solid #e5e7eb;">
        <td style="padding:10px 12px;text-align:left;color:#111827;font-size:14px;font-weight:700;">Total</td>
        <td style="padding:10px 12px;text-align:right;color:#111827;font-size:14px;font-weight:700;">{total_ul}</td>
        <td style="padding:10px 12px;text-align:right;color:#111827;font-size:14px;font-weight:700;">{total_nl}</td>
        <td style="padding:10px 12px;text-align:right;color:#111827;font-size:14px;font-weight:700;">{total_apt}</td>
        <td style="padding:10px 12px;text-align:right;color:#111827;font-size:14px;font-weight:700;">{total_quote}</td>
        <td style="padding:10px 12px;text-align:right;color:#111827;font-size:14px;font-weight:700;">{total_cust}</td>
        <td style="padding:10px 12px;text-align:right;color:#111827;font-size:14px;font-weight:700;">{money(total_sales)}</td>
        <td style="padding:10px 12px;text-align:right;color:#111827;font-size:14px;font-weight:700;">{total_nlc}</td>
        <td style="padding:10px 12px;text-align:right;color:#111827;font-size:14px;font-weight:700;">{money(total_nls)}</td>
        <td colspan="5"></td>
      </tr></tfoot>
    </table></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
      <div style="background:#fff;border:0.5px solid #e5e7eb;border-radius:10px;padding:16px;">
        <div style="font-size:11px;font-weight:500;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:10px;">Leads % of Total</div>
        <div style="position:relative;height:300px;"><canvas id="pie-leads"></canvas></div>
      </div>
      <div style="background:#fff;border:0.5px solid #e5e7eb;border-radius:10px;padding:16px;">
        <div style="font-size:11px;font-weight:500;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:10px;">Sales Amount % of Total</div>
        <div style="position:relative;height:300px;"><canvas id="pie-sales"></canvas></div>
      </div>
    </div>
    <script>
    function toggleDetail(key){{
      var row=document.getElementById('detail_'+key);
      var btn=document.getElementById('btn_'+key);
      if(row){{
        var showing=row.style.display!=='none';
        row.style.display=showing?'none':'table-row';
        if(btn)btn.textContent=showing?'▶':'▼';
      }}
    }}
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    const COLORS={COLORS};const NAMES={pie_names};const LEADS={pie_leads};const SALES={pie_sales};
    const pieOpts={{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'right',labels:{{font:{{size:10}},boxWidth:10,padding:8}}}},tooltip:{{callbacks:{{label:ctx=>' '+ctx.label+': '+ctx.parsed.toFixed(1)+'%'}}}}}}}};
    new Chart(document.getElementById('pie-leads'),{{type:'doughnut',data:{{labels:NAMES,datasets:[{{data:LEADS,backgroundColor:COLORS,borderWidth:1,borderColor:'#fff'}}]}},options:pieOpts}});
    new Chart(document.getElementById('pie-sales'),{{type:'doughnut',data:{{labels:NAMES,datasets:[{{data:SALES,backgroundColor:COLORS,borderWidth:1,borderColor:'#fff'}}]}},options:pieOpts}});
    </script>"""
    st.components.v1.html(tab2_html, height=len(offices_sorted)*40+820, scrolling=False)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Campaign Performance
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    import json
    MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    # Date selectors
    c1,c2,c3,c4,c5 = st.columns([1,1,0.3,1,1])
    with c1: t3_fm = st.selectbox("From Month", MONTHS, index=0, key="t3fm")
    with c2: t3_fy = st.selectbox("From Year", [2025,2026], index=0, key="t3fy")
    with c3: st.markdown("<div style='padding-top:28px;text-align:center;'>to</div>", unsafe_allow_html=True)
    with c4: t3_tm = st.selectbox("To Month", MONTHS, index=MONTHS.index(today.strftime("%b")), key="t3tm")
    with c5: t3_ty = st.selectbox("To Year", [2025,2026], index=1, key="t3ty")

    fm_idx = MONTHS.index(t3_fm)
    tm_idx = MONTHS.index(t3_tm)
    st.caption(f"{t3_fm} {t3_fy} – {t3_tm} {t3_ty}")

    # Build selected months
    sel_months = []
    y, m = t3_fy, fm_idx
    while y < t3_ty or (y == t3_ty and m <= tm_idx):
        sel_months.append((y, m))
        m += 1
        if m > 11: m = 0; y += 1

    camp_data = get_campaign_data()

    def gv(c, yr, mo, f):
        s = str(yr)
        if s in c["trend"]:
            return c["trend"][s].get(f, [0]*12)[mo]
        return 0

    def isPmax(n): return "performance max" in n.lower() or "pmax" in n.lower()
    def isBrand(n): return "brand" in n.lower()

    # Aggregate each campaign
    rows = []
    for c in camp_data:
        t = {f: sum(gv(c,yr,mo,f) for yr,mo in sel_months)
             for f in ["clicks","cost","conv","leads","apt","cust","sales"]}
        if t["cost"] <= 0 and t["clicks"] <= 0 and t["leads"] <= 0:
            continue
        t["roi"] = (t["sales"]-t["cost"])/t["cost"]*100 if t["cost"]>0 else 0
        t["cpc"] = t["cost"]/t["conv"] if t["conv"]>0 else 0
        t["al"]  = t["apt"]/t["leads"]*100 if t["leads"]>0 else 0
        t["oa"]  = t["cust"]/t["apt"]*100  if t["apt"]>0  else 0
        t["name"] = c["name"]
        rows.append(t)

    rows.sort(key=lambda x: (-x["sales"], -x["roi"]))

    active = [r["name"] for r in rows]
    avg_al = sum(r["al"] for r in rows if r["al"]>0) / max(sum(1 for r in rows if r["al"]>0),1)
    avg_oa = sum(r["oa"] for r in rows if r["oa"]>0) / max(sum(1 for r in rows if r["oa"]>0),1)

    def sg(names):
        t = {f: sum(r[f] for r in rows if r["name"] in names)
             for f in ["clicks","cost","conv","leads","apt","cust","sales"]}
        t["roi"] = (t["sales"]-t["cost"])/t["cost"]*100 if t["cost"]>0 else 0
        t["cpc"] = t["cost"]/t["conv"] if t["conv"]>0 else 0
        t["al"]  = t["apt"]/t["leads"]*100 if t["leads"]>0 else 0
        t["oa"]  = t["cust"]/t["apt"]*100  if t["apt"]>0  else 0
        return t

    pmax_n = [r["name"] for r in rows if isPmax(r["name"])]
    srch_n = [r["name"] for r in rows if not isPmax(r["name"])]
    snb_n  = [r["name"] for r in rows if not isPmax(r["name"]) and not isBrand(r["name"])]
    tot = sg(active); pmax = sg(pmax_n); srch = sg(srch_n); snb = sg(snb_n)

    # Build trend data for chart
    def trend(names_or_name, field):
        ty_v, ly_v = [], []
        for yr, mo in sel_months:
            if isinstance(names_or_name, list):
                ty = sum(gv(c,yr,mo,field)   for c in camp_data if c["name"] in names_or_name)
                ly = sum(gv(c,yr-1,mo,field) for c in camp_data if c["name"] in names_or_name)
            else:
                c = next((c for c in camp_data if c["name"]==names_or_name), None)
                ty = gv(c,yr,mo,field)   if c else 0
                ly = gv(c,yr-1,mo,field) if c else 0
            ty_v.append(ty); ly_v.append(ly)
        return ty_v, ly_v

    def roi_trend(names_or_name):
        cost_ty, cost_ly   = trend(names_or_name, "cost")
        sales_ty, sales_ly = trend(names_or_name, "sales")
        roi_ty = [(s-c)/c*100 if c>0 else 0 for c,s in zip(cost_ty, sales_ty)]
        roi_ly = [(s-c)/c*100 if c>0 else 0 for c,s in zip(cost_ly, sales_ly)]
        return roi_ty, roi_ly

    def build(names_or_name):
        d = {}
        for f in ["clicks","cost","conv","leads","apt","cust","sales"]:
            ty, ly = trend(names_or_name, f)
            d[f] = ty; d[f+"_ly"] = ly
        d["roi"], d["roi_ly"] = roi_trend(names_or_name)
        return d

    all_trends = {"__total__": build(active), "__srch__": build(srch_n), "__snb__": build(snb_n)}
    if pmax_n: all_trends["__pmax__"] = build(pmax_n)
    for c in camp_data:
        if c["name"] in active:
            all_trends[c["name"]] = build(c["name"])

    chart_data = json.dumps({"labels": [f"{MONTHS[mo]} {yr}" for yr,mo in sel_months], "trends": all_trends})

    # Table
    def money(n): return f"${float(n):,.0f}"
    def f2(n):
        try:
            v = float(n)
            return "0" if v==0 else f"{v:,.2f}".rstrip("0").rstrip(".")
        except: return "0"
    def badge(v, avg, s="%"):
        c = "#065f46" if v>=avg else "#991b1b"
        b = "#d1fae5" if v>=avg else "#fee2e2"
        return f'<span style="background:{b};color:{c};padding:1px 5px;border-radius:3px;font-size:10px;font-weight:600;">{f2(v)}{s}</span>'

    ts = "text-align:right;padding:6px 8px;border-bottom:0.5px solid #f3f4f6;font-size:12px;color:#374151;"

    def dr(r, bg=""):
        nm = r["name"].replace("'","\\'")
        return (f'<tr style="background:{bg};cursor:pointer;" onclick="sel(this,\'{nm}\')">'
            f'<td style="text-align:left;padding:6px 8px;border-bottom:0.5px solid #f3f4f6;font-weight:500;font-size:12px;">{r["name"]}</td>'
            f'<td style="{ts}">{f2(r["clicks"])}</td>'
            f'<td style="{ts}">{money(r["cost"])}</td>'
            f'<td style="{ts}">{f2(r["conv"])}</td>'
            f'<td style="{ts}">{"$"+f2(r["cpc"]) if r["cpc"]>0 else "—"}</td>'
            f'<td style="{ts}">{f2(r["leads"])}</td>'
            f'<td style="{ts}">{f2(r["apt"])}</td>'
            f'<td style="{ts}">{f2(r["cust"])}</td>'
            f'<td style="{ts}">{money(r["sales"])}</td>'
            f'<td style="{ts}">{badge(r["roi"],0)}</td>'
            f'<td style="{ts}">{badge(r["al"],avg_al)}</td>'
            f'<td style="{ts}">{badge(r["oa"],avg_oa)}</td>'
            f'</tr>')

    def sr(label, r, bg, key):
        k = key.replace("'","\\'")
        lb = label.replace("'","\\'")
        return (f'<tr style="background:{bg};font-weight:700;cursor:pointer;" onclick="sel(this,\'{k}\')">'
            f'<td style="text-align:left;padding:7px 8px;font-size:12px;">{label}</td>'
            f'<td style="{ts}">{f2(r["clicks"])}</td>'
            f'<td style="{ts}">{money(r["cost"])}</td>'
            f'<td style="{ts}">{f2(r["conv"])}</td>'
            f'<td style="{ts}">{"$"+f2(r["cpc"]) if r["cpc"]>0 else "—"}</td>'
            f'<td style="{ts}">{f2(r["leads"])}</td>'
            f'<td style="{ts}">{f2(r["apt"])}</td>'
            f'<td style="{ts}">{f2(r["cust"])}</td>'
            f'<td style="{ts}">{money(r["sales"])}</td>'
            f'<td style="{ts}">{f2(r["roi"])}%</td>'
            f'<td style="{ts}">{f2(r["al"])}%</td>'
            f'<td style="{ts}">{f2(r["oa"])}%</td>'
            f'</tr>')

    tbody = sr("📊 Total",tot,"#1f2937;color:#fff","__total__")
    tbody += "".join(dr(r,"#fefce8" if i%5==1 else "") for i,r in enumerate(rows))
    tfoot = ""
    if pmax_n: tfoot += sr("🔵 PMax Total",pmax,"#EFF6FF","__pmax__")
    tfoot += sr("🟢 All Search",srch,"#F0FDF4","__srch__")
    tfoot += sr("🟡 Search without Brand",snb,"#FEFCE8","__snb__")

    html_part1 = """
<style>
body{margin:0;font-family:sans-serif;}
table{width:100%;border-collapse:collapse;white-space:nowrap;font-size:12px;}
thead tr{background:#111827;}
th{padding:8px;font-size:10px;color:#9ca3af;text-transform:uppercase;text-align:right;}
th:first-child{text-align:left;color:#fff;}
tr.sel td{background:#dbeafe!important;}
.cb{background:#fff;border:0.5px solid #e5e7eb;border-radius:10px;padding:14px;margin-top:12px;}
.mt{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px;}
.mb{font-size:11px;padding:3px 9px;border-radius:6px;border:0.5px solid #e5e7eb;cursor:pointer;background:#fff;color:#6b7280;}
.mb.on{background:#111827;color:#fff;}
</style>
<div style="overflow-x:auto;">
<table>
<thead><tr>
<th style="text-align:left;color:#fff;min-width:160px;">Campaign</th>
<th>Clicks</th><th>Cost</th><th>Conv.</th><th>Cost/Conv</th>
<th>Leads</th><th>Apt</th><th>Customers</th><th>Sales</th>
<th>ROI</th><th>Apt/Lead</th><th>Order/Apt</th>
</tr></thead>
<tbody id="tb">""" + tbody + """</tbody>
<tfoot>""" + tfoot + """</tfoot>
</table></div>
<div class="cb">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
<b id="ctitle" style="font-size:13px;">📊 Total — Trend</b>
<div style="font-size:11px;color:#6b7280;">
<span style="display:inline-block;width:10px;height:3px;background:#378ADD;margin-right:4px;vertical-align:middle;"></span>This period
<span style="display:inline-block;width:10px;height:3px;background:#B5D4F4;margin-left:8px;margin-right:4px;vertical-align:middle;border-top:2px dashed #B5D4F4;"></span>Last year
</div>
</div>
<div class="mt">
<button class="mb on" onclick="sm('clicks',this)">Clicks</button>
<button class="mb" onclick="sm('cost',this)">Cost</button>
<button class="mb" onclick="sm('conv',this)">Conversions</button>
<button class="mb" onclick="sm('leads',this)">Leads</button>
<button class="mb" onclick="sm('apt',this)">Appointments</button>
<button class="mb" onclick="sm('cust',this)">Customers</button>
<button class="mb" onclick="sm('sales',this)">Sales</button>
<button class="mb" onclick="sm('roi',this)">ROI %</button>
</div>
<div style="position:relative;height:250px;"><canvas id="cc"></canvas></div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script>
var D="""

    html_part2 = """;
var sk='__total__',cm='clicks',ch=null;
function sel(row,key){
  if(sk===key){sk='__total__';document.querySelectorAll('tr').forEach(function(r){r.classList.remove('sel');});}
  else{document.querySelectorAll('tr').forEach(function(r){r.classList.remove('sel');});row.classList.add('sel');sk=key;}
  document.getElementById('ctitle').textContent=(sk==='__total__'?'📊 Total':key)+' — Trend';
  draw();
}
function sm(m,btn){cm=m;document.querySelectorAll('.mb').forEach(function(b){b.classList.remove('on');});btn.classList.add('on');draw();}
function draw(){
  var t=D.trends[sk]||D.trends['__total__'];
  var isR=cm==='roi';
  if(ch){ch.destroy();ch=null;}
  ch=new Chart(document.getElementById('cc'),{type:'line',data:{labels:D.labels,datasets:[
    {data:t[cm]||[],borderColor:'#378ADD',backgroundColor:'rgba(55,138,221,0.08)',fill:true,tension:0.3,pointRadius:3},
    {data:t[cm+'_ly']||[],borderColor:'#B5D4F4',backgroundColor:'rgba(181,212,244,0.08)',fill:true,tension:0.3,pointRadius:3,borderDash:[5,4]}
  ]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:function(c){return isR?' '+c.parsed.y.toFixed(1)+'%':' '+c.parsed.y.toLocaleString(undefined,{maximumFractionDigits:2});}}}},scales:{x:{ticks:{font:{size:10},maxRotation:45,autoSkip:true},grid:{display:false}},y:{min:0,ticks:{font:{size:10},callback:function(v){return isR?v.toFixed(0)+'%':v.toLocaleString();}},grid:{color:'#f3f4f6'}}}}});
}
draw();
</script>"""

    st.components.v1.html(html_part1 + chart_data + html_part2, height=len(rows)*34+600, scrolling=False)
