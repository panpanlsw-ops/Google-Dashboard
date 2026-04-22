# v2.0
import streamlit as st
from datetime import date, timedelta
import calendar
from data import get_data, get_roi_data, get_regional_data, get_campaign_data, get_campaigns

st.set_page_config(page_title="Daily Report", page_icon="📊", layout="wide")

# Load campaigns dynamically from Excel
try:
    CAMPAIGNS = get_campaigns()
except:
    CAMPAIGNS = {"all": "All campaigns"}

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
    roi_ty,   roi_ly   = series("roi")

    # ── MTD Charts ────────────────────────────────────────────────────────────
    is_all = (campaign == "All campaigns")
    camp_keys  = list(CAMPAIGNS.values())
    camp_names = list(CAMPAIGNS.values())

    if is_all:
        # Bar charts: all campaigns side by side
        def get_series(field_ty, field_ly):
            ty_vals, ly_vals = [], []
            for name in camp_keys:
                r = get_roi_data(name, roi_start, roi_end)
                ty_vals.append(r["ty"].get(field_ty, 0))
                ly_vals.append(r["ly"].get(field_ly, 0))
            return ty_vals, ly_vals
        labels = camp_names
    else:
        # Single campaign: show TY vs LY as 2 bars only
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
        labels = all_camp_names
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
    roi_ty,   roi_ly   = get_series("roi",                 "roi")

    chart_html = f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
      {"".join([
        f'<div style="background:#fff;border:0.5px solid #e5e7eb;border-radius:10px;padding:14px;{span}">'
        f'<div style="font-size:11px;font-weight:500;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">{title}</div>'
        f'<div style="display:flex;gap:12px;margin-bottom:8px;">'
        f'<span style="display:flex;align-items:center;gap:4px;font-size:11px;color:#6b7280;"><span style="width:10px;height:10px;border-radius:2px;background:{cy};display:inline-block;"></span>This year MTD</span>'
        f'<span style="display:flex;align-items:center;gap:4px;font-size:11px;color:#6b7280;"><span style="width:10px;height:10px;border-radius:2px;background:{lc};display:inline-block;"></span>Last year MTD</span>'
        f'</div><div style="position:relative;height:190px;"><canvas id="{cid}"></canvas></div></div>'
        for title,cid,cy,lc,span in [
            ("Conversions","c1","#378ADD","#B5D4F4",""),
            ("Cost","c2","#378ADD","#B5D4F4",""),
            ("CRM Leads","c3","#1D9E75","#9FE1CB",""),
            ("Appointments","c4","#1D9E75","#9FE1CB",""),
            ("Customers","c5","#1D9E75","#9FE1CB",""),
            ("Cost per Lead","c6","#534AB7","#AFA9EC",""),
            ("Cost per Appointment","c7","#534AB7","#AFA9EC",""),
            ("ROI %","c8","#BA7517","#FAC775","grid-column:span 2;"),
        ]
      ])}
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    const LABELS={labels};
    const isRoi=[false,false,false,false,false,false,false,true];
    const CHARTS=[
      ["c1",{conv_ty},{conv_ly},"#378ADD","#B5D4F4"],
      ["c2",{cost_ty},{cost_ly},"#378ADD","#B5D4F4"],
      ["c3",{leads_ty},{leads_ly},"#1D9E75","#9FE1CB"],
      ["c4",{apt_ty},{apt_ly},"#1D9E75","#9FE1CB"],
      ["c5",{cust_ty},{cust_ly},"#1D9E75","#9FE1CB"],
      ["c6",{cpl_ty},{cpl_ly},"#534AB7","#AFA9EC"],
      ["c7",{cpa_ty},{cpa_ly},"#534AB7","#AFA9EC"],
      ["c8",{roi_ty},{roi_ly},"#BA7517","#FAC775"],
    ];
    CHARTS.forEach(([cid,tyD,lyD,tyC,lyC],i)=>{{
      const r=isRoi[i];
      const opts={{responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:ctx=>r?' '+ctx.parsed.y+'%':' '+ctx.parsed.y.toLocaleString()}}}}}},
        scales:{{
          x:{{ticks:{{font:{{size:10}},autoSkip:false,maxRotation:30}},grid:{{display:false}}}},
          y:{{min:0,ticks:{{font:{{size:10}},callback:r?(v=>v+'%'):(v=>v.toLocaleString())}},grid:{{color:"#f3f4f6"}}}}
        }}
      }};
      new Chart(document.getElementById(cid),{{type:'bar',data:{{labels:LABELS,datasets:[
        {{data:tyD,backgroundColor:tyC,borderRadius:4}},
        {{data:lyD,backgroundColor:lyC,borderRadius:4}},
      ]}},options:opts}});
    }});
    </script>
    """
    st.components.v1.html(chart_html, height=1300, scrolling=True)


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
    with r1: metric_card("Total Leads",  f"{total_nl:,}",                    "blue")
    with r2: metric_card("Appointments", f"{total_apt:,}",                   "blue")
    with r3: metric_card("Customers",    f"{total_cust:,}",                  "teal")
    with r4: metric_card("Total Sales",  f"${float(total_sales or 0):,.0f}", "teal")
    with r5: metric_card("Apt / Leads",  f"{round(total_apt/total_nl*100) if total_nl else 0}%", "teal")

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

    rows_html = ""
    pie_names = []
    pie_leads = []
    pie_sales = []

    for i, o in enumerate(offices):
        # Read % values directly from Excel — no calculation
        lp_str = str(o.get("leads_pct","0%"))
        sp_str = str(o.get("sales_pct","0%"))
        al_str = str(o.get("apt_leads","0%"))
        oa_str = str(o.get("order_apt","0%"))
        ol_str = str(o.get("order_leads","0%"))

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
        al_badge = pct_badge(al_str, 50, ("#dbeafe","#1e40af"))

        td = "text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;color:#374151;"
        rows_html += f"""<tr>
          <td style="text-align:left;font-weight:500;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;color:#111827;">{o["name"]}</td>
          <td style="{td}">{o["ul"]}</td>
          <td style="{td}">{o["nl"]}</td>
          <td style="{td}">{o["apt"]}</td>
          <td style="{td}">{o["quote"]}</td>
          <td style="{td}">{o["cust"]}</td>
          <td style="{td}">{money(o["sales"])}</td>
          <td style="{td}">{o["nlc"]}</td>
          <td style="{td}">{money(o["nl_sales"])}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;">{lp_badge}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;">{sp_badge}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;">{al_badge}</td>
          <td style="{td}">{oa_str}</td>
          <td style="{td}">{ol_str}</td>
        </tr>"""

    th = "padding:9px 10px;font-size:11px;font-weight:500;letter-spacing:0.04em;text-transform:uppercase;white-space:nowrap;"
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
        <td style="padding:8px 10px;text-align:left;color:#111827;">Total</td>
        <td style="padding:8px 10px;text-align:right;color:#111827;">{total_ul}</td>
        <td style="padding:8px 10px;text-align:right;color:#111827;">{total_nl}</td>
        <td style="padding:8px 10px;text-align:right;color:#111827;">{total_apt}</td>
        <td style="padding:8px 10px;text-align:right;color:#111827;">{total_quote}</td>
        <td style="padding:8px 10px;text-align:right;color:#111827;">{total_cust}</td>
        <td style="padding:8px 10px;text-align:right;color:#111827;">{money(total_sales)}</td>
        <td style="padding:8px 10px;text-align:right;color:#111827;">{total_nlc}</td>
        <td style="padding:8px 10px;text-align:right;color:#111827;">{money(total_nls)}</td>
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
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    const COLORS={COLORS};const NAMES={pie_names};const LEADS={pie_leads};const SALES={pie_sales};
    const pieOpts={{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'right',labels:{{font:{{size:10}},boxWidth:10,padding:8}}}},tooltip:{{callbacks:{{label:ctx=>' '+ctx.label+': '+ctx.parsed.toFixed(1)+'%'}}}}}}}};
    new Chart(document.getElementById('pie-leads'),{{type:'doughnut',data:{{labels:NAMES,datasets:[{{data:LEADS,backgroundColor:COLORS,borderWidth:1,borderColor:'#fff'}}]}},options:pieOpts}});
    new Chart(document.getElementById('pie-sales'),{{type:'doughnut',data:{{labels:NAMES,datasets:[{{data:SALES,backgroundColor:COLORS,borderWidth:1,borderColor:'#fff'}}]}},options:pieOpts}});
    </script>"""
    st.components.v1.html(tab2_html, height=len(offices)*40+820, scrolling=False)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Campaign Performance
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    camp_data = get_campaign_data()
    import json
    camp_json = json.dumps([{"name": c["name"], "trend": c["trend"]} for c in camp_data])
    camp_rows = ""
    for i, c in enumerate(camp_data):
        hl = " row-hl" if i % 5 == 1 else ""
        cells = "".join([f'<td id="t3r{i}_{f}">—</td>' for f in ["clicks","cost","conv","cpc","leads","apt","cust","sales","roi","al","oa"]])
        camp_rows += f'<tr class="data-row{hl}" onclick="t3Select(this,{i})"><td>{c["name"]}</td>{cells}</tr>'

    MONTH_NAMES_T3 = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    tab3_html = """
    <style>
    .t3{padding:0.5rem 0;font-family:sans-serif}.t3h{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;flex-wrap:wrap;gap:8px}.t3h span{font-size:15px;font-weight:500;color:#111827}.t3c{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.t3c label{font-size:12px;color:#6b7280}.t3c select{font-size:12px;padding:5px 10px;border-radius:8px;border:0.5px solid #d1d5db;background:#fff;color:#374151}.t3c button{font-size:12px;padding:5px 14px;border-radius:8px;border:0.5px solid #111827;background:#111827;color:#fff;cursor:pointer}.t3badge{font-size:12px;color:#6b7280;background:#f9fafb;border:0.5px solid #e5e7eb;border-radius:8px;padding:5px 12px;display:inline-block;margin-bottom:12px}.t3tbl{width:100%;border-collapse:collapse;font-size:11px;white-space:nowrap}.t3tbl thead tr{background:#111827}.t3tbl th{padding:8px 8px;font-size:10px;font-weight:500;color:#9ca3af;text-transform:uppercase;letter-spacing:0.04em;text-align:right}.t3tbl th:first-child{text-align:left;color:#fff}.t3tbl td{padding:6px 8px;border-bottom:0.5px solid #f3f4f6;text-align:right;color:#374151;cursor:pointer}.t3tbl td:first-child{text-align:left;font-weight:500;color:#111827}.t3tbl tfoot td{font-weight:600;background:#f8f9fa;border-top:0.5px solid #e5e7eb;color:#111827;padding:7px 8px}.t3tbl tr.data-row:hover td{background:#f0f9ff}.t3tbl tr.sel td{background:#dbeafe !important}.t3tbl tr.row-hl{background:#fefce8}.rp{background:#d1fae5;color:#065f46;padding:2px 5px;border-radius:4px;font-size:10px;font-weight:500}.rn{background:#fee2e2;color:#991b1b;padding:2px 5px;border-radius:4px;font-size:10px;font-weight:500}.pg{background:#d1fae5;color:#065f46;padding:2px 5px;border-radius:4px;font-size:10px;font-weight:500}.pr{background:#fee2e2;color:#991b1b;padding:2px 5px;border-radius:4px;font-size:10px;font-weight:500}.cbox{background:#fff;border:0.5px solid #e5e7eb;border-radius:10px;padding:14px;margin-top:14px}.ctop{display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;flex-wrap:wrap;gap:8px}.cname{font-size:13px;font-weight:500;color:#111827}.chint{font-size:11px;color:#6b7280;margin-top:2px}.leg{display:flex;gap:14px}.legi{display:flex;align-items:center;gap:4px;font-size:11px;color:#6b7280}.legd{width:10px;height:10px;border-radius:2px;flex-shrink:0}.mtabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}.mtab{font-size:11px;padding:4px 10px;border-radius:6px;border:0.5px solid #e5e7eb;background:#fff;color:#6b7280;cursor:pointer}.mtab.active{background:#111827;color:#fff;border-color:#111827}
    </style>
    <div class="t3">
      <div class="t3h"><span>Campaign Performance</span>
        <div class="t3c">
          <label>From</label>
          <select id="t3fm"><option value="0">Jan</option><option value="1">Feb</option><option value="2">Mar</option><option value="3" selected>Apr</option><option value="4">May</option><option value="5">Jun</option><option value="6">Jul</option><option value="7">Aug</option><option value="8">Sep</option><option value="9">Oct</option><option value="10">Nov</option><option value="11">Dec</option></select>
          <select id="t3fy"><option>2024</option><option>2025</option><option selected>2026</option></select>
          <label>To</label>
          <select id="t3tm"><option value="0">Jan</option><option value="1">Feb</option><option value="2">Mar</option><option value="3" selected>Apr</option><option value="4">May</option><option value="5">Jun</option><option value="6">Jul</option><option value="7">Aug</option><option value="8">Sep</option><option value="9">Oct</option><option value="10">Nov</option><option value="11">Dec</option></select>
          <select id="t3ty"><option>2024</option><option>2025</option><option selected>2026</option></select>
          <button onclick="t3Apply()">Apply</button>
        </div>
      </div>
      <div id="t3badge" class="t3badge"></div>
      <div style="overflow-x:auto;margin-bottom:4px;">
      <table class="t3tbl">
        <thead><tr><th>Campaign</th><th>Clicks</th><th>Cost</th><th>Conv.</th><th>Cost/Conv.</th><th>Leads</th><th>Apt</th><th>Customers</th><th>Sales</th><th>ROI</th><th>Apt/Lead</th><th>Order/Apt</th></tr></thead>
        <tbody id="t3body">""" + camp_rows + """
          <tr><td colspan="12" style="text-align:center;color:#9ca3af;font-style:italic;padding:6px;">Click any row to see monthly trend</td></tr>
        </tbody>
        <tfoot id="t3foot"></tfoot>
      </table></div>
      <div class="cbox">
        <div class="ctop">
          <div><div class="cname" id="t3cname">Select a campaign above</div><div class="chint" id="t3chint"></div></div>
          <div class="leg">
            <span class="legi"><span class="legd" style="background:#378ADD"></span><span id="t3lty">This period</span></span>
            <span class="legi"><span class="legd" style="background:#B5D4F4"></span><span id="t3lly">Last period</span></span>
          </div>
        </div>
        <div class="mtabs">
          <button class="mtab active" onclick="t3SM('clicks',this)">Clicks</button>
          <button class="mtab" onclick="t3SM('cost',this)">Cost</button>
          <button class="mtab" onclick="t3SM('conv',this)">Conversions</button>
          <button class="mtab" onclick="t3SM('leads',this)">Leads</button>
          <button class="mtab" onclick="t3SM('apt',this)">Appointments</button>
          <button class="mtab" onclick="t3SM('sales',this)">Sales</button>
          <button class="mtab" onclick="t3SM('roi',this)">ROI %</button>
        </div>
        <div style="position:relative;height:240px;"><canvas id="t3chart"></canvas></div>
      </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    const MN=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const TD=""" + camp_json + """;
    var fm=0,fy=2026,tm=3,ty=2026,ci=0,cm='clicks',tc=null;
    function getMonths(a,b,c,d){var r=[],mo=a,yr=b;while(yr<d||(yr===d&&mo<=c)){r.push({m:mo,y:yr});mo++;if(mo>11){mo=0;yr++;}}return r;}
    function gv(i,months,f){return months.reduce(function(s,p){return s+((TD[i]&&TD[i].trend&&TD[i].trend[p.y]&&TD[i].trend[p.y][f]&&TD[i].trend[p.y][f][p.m])||0);},0);}
    function gav(i,months){var vl=months.filter(function(p){return((TD[i]&&TD[i].trend&&TD[i].trend[p.y]&&TD[i].trend[p.y].clicks&&TD[i].trend[p.y].clicks[p.m])||0)>0;});if(!vl.length)return 0;return vl.reduce(function(s,p){return s+((TD[i]&&TD[i].trend&&TD[i].trend[p.y]&&TD[i].trend[p.y].roi&&TD[i].trend[p.y].roi[p.m])||0);},0)/vl.length;}
    function rb(v){return v>=0?'<span class="rp">'+v.toFixed(1)+'%</span>':'<span class="rn">'+v.toFixed(1)+'%</span>';}
    function pb(v,t){if(!isFinite(v))return'—';return v>=t?'<span class="pg">'+v.toFixed(1)+'%</span>':'<span class="pr">'+v.toFixed(1)+'%</span>';}
    function mn(n){return n>0?'$'+Math.round(n).toLocaleString():'$0';}
    function se(id,v){var el=document.getElementById(id);if(el)el.innerHTML=v;}
    function t3Apply(){
      fm=parseInt(document.getElementById('t3fm').value);fy=parseInt(document.getElementById('t3fy').value);
      tm=parseInt(document.getElementById('t3tm').value);ty=parseInt(document.getElementById('t3ty').value);
      var months=getMonths(fm,fy,tm,ty);
      document.getElementById('t3badge').textContent=MN[fm]+' '+fy+' - '+MN[tm]+' '+ty+'  |  vs '+MN[fm]+' '+(fy-1)+' - '+MN[tm]+' '+(ty-1);
      TD.forEach(function(c,i){
        var cl=gv(i,months,'clicks'),co=gv(i,months,'cost'),cv=gv(i,months,'conv'),le=gv(i,months,'leads'),ap=gv(i,months,'apt'),cu=gv(i,months,'cust'),sa=gv(i,months,'sales'),ro=gav(i,months),cpc=cv>0?co/cv:0,al=le>0?ap/le*100:0,oa=ap>0?cu/ap*100:null;
        se('t3r'+i+'_clicks',cl.toLocaleString());se('t3r'+i+'_cost',mn(co));se('t3r'+i+'_conv',cv.toLocaleString());se('t3r'+i+'_cpc',cpc>0?'$'+Math.round(cpc):'—');
        se('t3r'+i+'_leads',le.toLocaleString());se('t3r'+i+'_apt',ap.toLocaleString());se('t3r'+i+'_cust',cu.toLocaleString());se('t3r'+i+'_sales',mn(sa));
        se('t3r'+i+'_roi',rb(ro));se('t3r'+i+'_al',pb(al,30));se('t3r'+i+'_oa',oa!==null?pb(oa,20):'#DIV/0!');
      });
      var tot={cl:0,co:0,cv:0,le:0,ap:0,cu:0,sa:0};
      TD.forEach(function(_,i){tot.cl+=gv(i,months,'clicks');tot.co+=gv(i,months,'cost');tot.cv+=gv(i,months,'conv');tot.le+=gv(i,months,'leads');tot.ap+=gv(i,months,'apt');tot.cu+=gv(i,months,'cust');tot.sa+=gv(i,months,'sales');});
      var ar=TD.reduce(function(s,_,i){return s+gav(i,months);},0)/TD.length;
      document.getElementById('t3foot').innerHTML='<tr><td>Total</td><td>'+tot.cl.toLocaleString()+'</td><td>'+mn(tot.co)+'</td><td>'+tot.cv+'</td><td>—</td><td>'+tot.le+'</td><td>'+tot.ap+'</td><td>'+tot.cu+'</td><td>'+mn(tot.sa)+'</td><td>'+rb(ar)+'</td><td>'+pb(tot.le>0?tot.ap/tot.le*100:0,30)+'</td><td>'+pb(tot.ap>0?tot.cu/tot.ap*100:0,15)+'</td></tr>';
      t3UC();
    }
    function t3Select(row,idx){document.querySelectorAll('#t3body tr.data-row').forEach(function(r){r.classList.remove('sel');});row.classList.add('sel');ci=idx;document.getElementById('t3cname').textContent=TD[idx].name+' — Monthly Trend';t3UC();}
    function t3SM(m,btn){cm=m;document.querySelectorAll('.mtab').forEach(function(b){b.classList.remove('active');});btn.classList.add('active');t3UC();}
    function t3UC(){
      var isR=cm==='roi';var months=getMonths(fm,fy,tm,ty);var ly=months.map(function(p){return{m:p.m,y:p.y-1};});
      var labels=months.map(function(p){return MN[p.m]+' '+p.y;});
      var tyd=months.map(function(p){return(TD[ci]&&TD[ci].trend&&TD[ci].trend[p.y]&&TD[ci].trend[p.y][cm]&&TD[ci].trend[p.y][cm][p.m])||0;});
      var lyd=ly.map(function(p){return(TD[ci]&&TD[ci].trend&&TD[ci].trend[p.y]&&TD[ci].trend[p.y][cm]&&TD[ci].trend[p.y][cm][p.m])||0;});
      var tyy=[...new Set(months.map(function(p){return p.y;}))].join('–');var lyy=[...new Set(ly.map(function(p){return p.y;}))].join('–');
      document.getElementById('t3lty').textContent=tyy;document.getElementById('t3lly').textContent=lyy;
      document.getElementById('t3chint').textContent=MN[fm]+' '+fy+' - '+MN[tm]+' '+ty+'  |  vs same period last year';
      if(tc)tc.destroy();
      tc=new Chart(document.getElementById('t3chart'),{type:'line',data:{labels:labels,datasets:[{data:tyd,borderColor:'#378ADD',backgroundColor:'#378ADD22',fill:true,tension:0.3,pointRadius:4},{data:lyd,borderColor:'#B5D4F4',backgroundColor:'#B5D4F422',fill:true,tension:0.3,pointRadius:4,borderDash:[5,4]}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:function(ctx){return isR?' '+ctx.parsed.y+'%':' '+ctx.parsed.y.toLocaleString();}}}},scales:{x:{ticks:{font:{size:10},maxRotation:45,autoSkip:true,maxTicksLimit:16},grid:{display:false}},y:{ticks:{font:{size:10},callback:function(v){return isR?v+'%':v.toLocaleString();}},grid:{color:'#f3f4f6'}}}}});
    }
    t3Apply();
    </script>
    """
    st.components.v1.html(tab3_html, height=len(camp_data)*36+720, scrolling=False)
