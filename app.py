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

    # Build chart data — bar charts showing MTD totals per campaign
    camp_keys  = list(CAMPAIGNS.keys())
    camp_names = list(CAMPAIGNS.values())

    def get_series(field_ty, field_ly):
        ty_vals, ly_vals = [], []
        for k in camp_keys:
            r = get_roi_data(k, roi_start, roi_end)
            ty_vals.append(r["ty"].get(field_ty, 0))
            ly_vals.append(r["ly"].get(field_ly, 0))
        return ty_vals, ly_vals

    conv_ty,  conv_ly  = get_series("conversions",        "conversions")
    cost_ty,  cost_ly  = get_series("cost",               "cost")
    leads_ty, leads_ly = get_series("leads",              "leads")
    apt_ty,   apt_ly   = get_series("appointments",       "appointments")
    cust_ty,  cust_ly  = get_series("customers",          "customers")
    cpl_ty,   cpl_ly   = get_series("cost_per_lead",      "cost_per_lead")
    cpa_ty,   cpa_ly   = get_series("cost_per_appointment","cost_per_appointment")
    roi_ty,   roi_ly   = get_series("roi",                "roi")

    # Pace data: projected month-end for leads and appointments
    leads_pace_ty = [round(v / day_of_month * days_in_month) if day_of_month else 0 for v in leads_ty]
    leads_pace_ly = [round(v / day_of_month * days_in_month) if day_of_month else 0 for v in leads_ly]
    apt_pace_ty   = [round(v / day_of_month * days_in_month) if day_of_month else 0 for v in apt_ty]
    apt_pace_ly   = [round(v / day_of_month * days_in_month) if day_of_month else 0 for v in apt_ly]

    chart_html = f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
      {"".join([
        f'<div style="background:#fff;border:0.5px solid #e5e7eb;border-radius:10px;padding:14px;{span}">'
        f'<div style="font-size:11px;font-weight:500;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">{title}</div>'
        f'<div style="display:flex;gap:12px;margin-bottom:8px;">'
        f'<span style="display:flex;align-items:center;gap:4px;font-size:11px;color:#6b7280;"><span style="width:10px;height:10px;border-radius:2px;background:{cy};display:inline-block;"></span>This year MTD</span>'
        f'<span style="display:flex;align-items:center;gap:4px;font-size:11px;color:#6b7280;"><span style="width:10px;height:10px;border-radius:2px;background:{lc};display:inline-block;"></span>Last year MTD</span>'
        f'{"<span style=\'display:flex;align-items:center;gap:4px;font-size:11px;color:#6b7280;\'><span style=\'width:10px;height:10px;border-radius:2px;background:#9ca3af;display:inline-block;\'></span>Pace</span>" if pace else ""}'
        f'</div><div style="position:relative;height:190px;"><canvas id="{cid}"></canvas></div></div>'
        for title,cid,cy,lc,span,pace in [
            ("Conversions","c1","#378ADD","#B5D4F4","",False),
            ("Cost","c2","#378ADD","#B5D4F4","",False),
            ("CRM Leads","c3","#1D9E75","#9FE1CB","",False),
            ("Appointments","c4","#1D9E75","#9FE1CB","",False),
            ("Customers","c5","#1D9E75","#9FE1CB","",False),
            ("Cost per Lead","c6","#534AB7","#AFA9EC","",False),
            ("Cost per Appointment","c7","#534AB7","#AFA9EC","",False),
            ("ROI %","c8","#BA7517","#FAC775","grid-column:span 2;",False),
            ("Leads — MTD vs Pace","c9","#1D9E75","#9FE1CB","",True),
            ("Appointments — MTD vs Pace","c10","#1D9E75","#9FE1CB","",True),
        ]
      ])}
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    const LABELS={camp_names};
    const isRoi=[false,false,false,false,false,false,false,true,false,false];
    const CHARTS=[
      ["c1",{conv_ty},{conv_ly},null,null,"#378ADD","#B5D4F4"],
      ["c2",{cost_ty},{cost_ly},null,null,"#378ADD","#B5D4F4"],
      ["c3",{leads_ty},{leads_ly},null,null,"#1D9E75","#9FE1CB"],
      ["c4",{apt_ty},{apt_ly},null,null,"#1D9E75","#9FE1CB"],
      ["c5",{cust_ty},{cust_ly},null,null,"#1D9E75","#9FE1CB"],
      ["c6",{cpl_ty},{cpl_ly},null,null,"#534AB7","#AFA9EC"],
      ["c7",{cpa_ty},{cpa_ly},null,null,"#534AB7","#AFA9EC"],
      ["c8",{roi_ty},{roi_ly},null,null,"#BA7517","#FAC775"],
      ["c9",{leads_ty},{leads_ly},{leads_pace_ty},{leads_pace_ly},"#1D9E75","#9FE1CB"],
      ["c10",{apt_ty},{apt_ly},{apt_pace_ty},{apt_pace_ly},"#1D9E75","#9FE1CB"],
    ];
    CHARTS.forEach(([cid,tyD,lyD,pTy,pLy,tyC,lyC],i)=>{{
      const r=isRoi[i];
      const opts={{responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:ctx=>r?' '+ctx.parsed.y+'%':' '+ctx.parsed.y.toLocaleString()}}}}}},
        scales:{{
          x:{{ticks:{{font:{{size:10}},autoSkip:false,maxRotation:30}},grid:{{display:false}}}},
          y:{{ticks:{{font:{{size:10}},callback:r?(v=>v+'%'):(v=>v.toLocaleString())}},grid:{{color:"#f3f4f6"}}}}
        }}
      }};
      const datasets=[
        {{data:tyD,backgroundColor:tyC,borderRadius:4}},
        {{data:lyD,backgroundColor:lyC,borderRadius:4}},
      ];
      if(pTy) datasets.push({{data:pTy,backgroundColor:"#9ca3af",borderRadius:4,borderDash:[4,3]}});
      if(pLy) datasets.push({{data:pLy,backgroundColor:"#d1d5db",borderRadius:4}});
      new Chart(document.getElementById(cid),{{type:'bar',data:{{labels:LABELS,datasets}},options:opts}});
    }});
    </script>
    """
    st.components.v1.html(chart_html, height=1280, scrolling=False)
