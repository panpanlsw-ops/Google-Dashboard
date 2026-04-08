import streamlit as st
from datetime import date, timedelta
import calendar
from data import get_data, get_roi_data, CAMPAIGNS
 
st.set_page_config(page_title="Daily Report", page_icon="📊", layout="wide")
 
st.markdown("""
<style>
    .metric-card { background:#ffffff; border:0.5px solid #e5e7eb; border-radius:10px; overflow:hidden; min-height:120px; margin-bottom:4px; }
    .metric-accent { height:3px; }
    .accent-blue { background:#378ADD; }
    .accent-teal { background:#1D9E75; }
    .metric-body { padding:10px 12px; }
    .metric-label { font-size:10px; color:#6b7280; margin:0 0 3px; text-transform:uppercase; letter-spacing:0.05em; }
    .metric-value { font-size:22px; font-weight:600; color:#111827; margin:0; line-height:1.1; }
    .metric-sub { font-size:10px; color:#9ca3af; margin:3px 0 0; }
    .pace-row { font-size:10px; color:#185FA5; margin-top:6px; padding-top:6px; border-top:0.5px solid #e5e7eb; }
    .pace-projected { font-weight:600; }
    div[data-testid="stHorizontalBlock"] { gap:8px; }
</style>
""", unsafe_allow_html=True)
 
 
# ── Helpers ───────────────────────────────────────────────────────────────────
def projected(value, day, days_in_month):
    if day == 0: return 0
    return round((value / day) * days_in_month)
 
def metric_card(label, value, accent="blue", sub=None, pace_val=None, days_left=None):
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    pace_html = (
        f'<div class="pace-row">&#8594; Month-end: <span class="pace-projected">{pace_val}</span> ({days_left}d)</div>'
    ) if pace_val is not None else ""
    st.markdown(
        f'<div class="metric-card"><div class="metric-accent accent-{accent}"></div>'
        f'<div class="metric-body"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>{sub_html}{pace_html}</div></div>',
        unsafe_allow_html=True
    )
 
 
# ── Dates ─────────────────────────────────────────────────────────────────────
today      = date.today()
yesterday  = today - timedelta(days=1)
day_of_month   = today.day
days_in_month  = calendar.monthrange(today.year, today.month)[1]
days_left      = days_in_month - day_of_month
month_name     = today.strftime("%b")
year           = today.year
last_year      = year - 1
 
# KPI cards use today; ROI section uses 1st of month → yesterday
roi_start = today.replace(day=1)
roi_end   = yesterday
 
 
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
tab1, = st.tabs(["📈 Today"])
 
with tab1:
 
    campaign = st.selectbox("Campaign", options=list(CAMPAIGNS.keys()), format_func=lambda x: CAMPAIGNS[x])
    d = get_data(campaign)
 
    # ── KPI Cards ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_card("Conversions", f"{d['conversions']:,}", "blue",
            f"Invoca {d['invoca']:,} · Form {d['form']:,}",
            f"{projected(d['conversions'], day_of_month, days_in_month):,}", days_left)
    with c2:
        metric_card("Cost", f"${d['cost']:,}", "blue", None,
            f"${projected(d['cost'], day_of_month, days_in_month):,}", days_left)
    with c3:
        metric_card("CRM Leads", f"{d['leads']:,}", "teal",
            f"Invoca {d['crm_invoca']:,} · Form {d['crm_form']:,}",
            f"{projected(d['leads'], day_of_month, days_in_month):,}", days_left)
    with c4:
        metric_card("Appointments", f"{d['appointments']:,}", "teal", None,
            f"{projected(d['appointments'], day_of_month, days_in_month):,}", days_left)
    with c5:
        metric_card("Customers", f"{d['customers']:,}", "teal")
 
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
 
    # ── ROI Section ───────────────────────────────────────────────────────────
    roi_col1, roi_col2 = st.columns([3, 1])
    with roi_col1:
        st.markdown("### Current ROI")
    with roi_col2:
        st.markdown(
            f"<div style='text-align:right;color:#6b7280;padding-top:8px;font-size:12px;'>"
            f"{month_name} 1–{yesterday.day}, {year} vs {last_year}</div>",
            unsafe_allow_html=True
        )
 
    is_all = (campaign == "all")
    hint = "Showing all campaigns — select a specific campaign to see monthly trends" if is_all \
           else f"Monthly trend for {CAMPAIGNS[campaign]} — Jan to {month_name} {year}"
    st.caption(hint)
 
    # Get ROI data
    roi = get_roi_data(campaign, roi_start, roi_end)
 
    if is_all:
        labels   = list(CAMPAIGNS.values())
        camp_keys = list(CAMPAIGNS.keys())
        def series(field):
            ty = [get_roi_data(k, roi_start, roi_end)["ty"][field] for k in camp_keys]
            ly = [get_roi_data(k, roi_start, roi_end)["ly"][field] for k in camp_keys]
            return ty, ly
        chart_type = "bar"
    else:
        labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][:today.month]
        def series(field):
            return roi["ty_trend"][field], roi["ly_trend"][field]
        chart_type = "line"
 
    conv_ty,  conv_ly  = series("conversions")
    cost_ty,  cost_ly  = series("cost")
    leads_ty, leads_ly = series("leads")
    appts_ty, appts_ly = series("appointments")
    cust_ty,  cust_ly  = series("customers")
    cpl_ty,   cpl_ly   = series("cost_per_lead")
    cpa_ty,   cpa_ly   = series("cost_per_appointment")
    roi_ty,   roi_ly   = series("roi")
 
    chart_html = f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
      {"".join([
        f'''<div style="background:#fff;border:0.5px solid #e5e7eb;border-radius:10px;padding:14px;{span}">
          <div style="font-size:11px;font-weight:500;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">{title}</div>
          <div style="display:flex;gap:12px;margin-bottom:8px;">
            <span style="display:flex;align-items:center;gap:4px;font-size:11px;color:#6b7280;"><span style="width:10px;height:10px;border-radius:2px;background:{cy};display:inline-block;"></span>This year</span>
            <span style="display:flex;align-items:center;gap:4px;font-size:11px;color:#6b7280;"><span style="width:10px;height:10px;border-radius:2px;background:{ly};display:inline-block;"></span>Last year</span>
          </div>
          <div style="position:relative;height:190px;"><canvas id="{cid}"></canvas></div>
        </div>'''
        for title, cid, cy, ly, span in [
            ("Conversions",           "c1", "#378ADD", "#B5D4F4", ""),
            ("Cost",                  "c2", "#378ADD", "#B5D4F4", ""),
            ("CRM Leads",             "c3", "#1D9E75", "#9FE1CB", ""),
            ("Appointments",          "c4", "#1D9E75", "#9FE1CB", ""),
            ("Customers",             "c5", "#1D9E75", "#9FE1CB", ""),
            ("Cost per Lead",         "c6", "#534AB7", "#AFA9EC", ""),
            ("Cost per Appointment",  "c7", "#534AB7", "#AFA9EC", ""),
            ("ROI %",                 "c8", "#BA7517", "#FAC775", "grid-column:span 2;"),
        ]
      ])}
    </div>
 
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    const TYPE = "{chart_type}";
    const LABELS = {labels};
    const isRoi = [false,false,false,false,false,false,false,true];
    const CHARTS = [
      ["c1", {conv_ty},  {conv_ly},  "#378ADD","#B5D4F4"],
      ["c2", {cost_ty},  {cost_ly},  "#378ADD","#B5D4F4"],
      ["c3", {leads_ty}, {leads_ly}, "#1D9E75","#9FE1CB"],
      ["c4", {appts_ty}, {appts_ly}, "#1D9E75","#9FE1CB"],
      ["c5", {cust_ty},  {cust_ly},  "#1D9E75","#9FE1CB"],
      ["c6", {cpl_ty},   {cpl_ly},   "#534AB7","#AFA9EC"],
      ["c7", {cpa_ty},   {cpa_ly},   "#534AB7","#AFA9EC"],
      ["c8", {roi_ty},   {roi_ly},   "#BA7517","#FAC775"],
    ];
    CHARTS.forEach(([cid, tyD, lyD, tyC, lyC], i) => {{
      const roi = isRoi[i];
      const opts = {{
        responsive:true, maintainAspectRatio:false,
        plugins:{{ legend:{{display:false}}, tooltip:{{ callbacks:{{ label: ctx => roi ? ' '+ctx.parsed.y+'%' : ' '+ctx.parsed.y.toLocaleString() }} }} }},
        scales:{{
          x:{{ ticks:{{font:{{size:10}},autoSkip:false,maxRotation:30}}, grid:{{display:false}} }},
          y:{{ ticks:{{font:{{size:10}}, callback: roi ? (v=>v+'%') : (v=>v.toLocaleString()) }}, grid:{{color:"#f3f4f6"}} }}
        }}
      }};
      const tyDs = TYPE==="bar"
        ? {{data:tyD, backgroundColor:tyC, borderRadius:4}}
        : {{data:tyD, borderColor:tyC, backgroundColor:tyC+"33", fill:true, tension:0.3, pointRadius:3}};
      const lyDs = TYPE==="bar"
        ? {{data:lyD, backgroundColor:lyC, borderRadius:4}}
        : {{data:lyD, borderColor:lyC, backgroundColor:lyC+"33", fill:true, tension:0.3, pointRadius:3, borderDash:[4,3]}};
      new Chart(document.getElementById(cid), {{
        type: TYPE,
        data: {{ labels: LABELS, datasets: [tyDs, lyDs] }},
        options: opts
      }});
    }});
    </script>
    """
    st.components.v1.html(chart_html, height=980, scrolling=False)
