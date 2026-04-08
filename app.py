import streamlit as st
from datetime import date
import calendar
from data import get_data, CAMPAIGNS
 
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
    .section-label { font-size:11px; font-weight:600; color:#6b7280; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:8px; margin-top:4px; }
    div[data-testid="stHorizontalBlock"] { gap:8px; }
</style>
""", unsafe_allow_html=True)
 
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
 
today = date.today()
day_of_month = today.day
days_in_month = calendar.monthrange(today.year, today.month)[1]
days_left = days_in_month - day_of_month
month_name = today.strftime("%b")
year = today.year
 
col_title, col_date = st.columns([3, 1])
with col_title:
    st.markdown("# Daily Report")
    st.markdown("## Performance Overview")
with col_date:
    st.markdown(
        f"<div style='text-align:right;color:#6b7280;padding-top:16px;'>{today.strftime('%a, %b %d %Y')}</div>",
        unsafe_allow_html=True
    )
 
tab1, = st.tabs(["📈 Today"])
 
with tab1:
    campaign = st.selectbox("Campaign", options=list(CAMPAIGNS.keys()), format_func=lambda x: CAMPAIGNS[x])
    d = get_data(campaign)
 
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
            f"{month_name} 1–{day_of_month}, {year} vs {year-1}</div>",
            unsafe_allow_html=True
        )
 
    is_all = (campaign == "all")
    hint = "Showing all campaigns — select a specific campaign to see monthly trends" if is_all else \
           f"Showing monthly trend for {CAMPAIGNS[campaign]}"
    st.caption(hint)
 
    chart_type = "bar" if is_all else "line"
 
    if is_all:
        camp_keys  = ["all", "brand", "search", "display", "local"]
        camp_names = ["All", "Brand", "Search", "Display", "Local"]
        roi = {k: get_data(k) for k in camp_keys}
        conv_ty  = [roi[k]["conversions"] for k in camp_keys]
        conv_ly  = [int(roi[k]["conversions"] * 0.87) for k in camp_keys]
        cost_ty  = [roi[k]["cost"]         for k in camp_keys]
        cost_ly  = [int(roi[k]["cost"]     * 0.88) for k in camp_keys]
        leads_ty = [roi[k]["leads"]        for k in camp_keys]
        leads_ly = [int(roi[k]["leads"]    * 0.87) for k in camp_keys]
        appts_ty = [roi[k]["appointments"] for k in camp_keys]
        appts_ly = [int(roi[k]["appointments"] * 0.85) for k in camp_keys]
        cust_ty  = [roi[k]["customers"]    for k in camp_keys]
        cust_ly  = [int(roi[k]["customers"]* 0.85) for k in camp_keys]
        labels   = camp_names
    else:
        labels   = ["Jan", "Feb", "Mar", "Apr"]
        base = d["conversions"]
        conv_ty  = [int(base*0.55), int(base*0.70), int(base*0.85), base]
        conv_ly  = [int(v*0.87) for v in conv_ty]
        base = d["cost"]
        cost_ty  = [int(base*0.55), int(base*0.70), int(base*0.85), base]
        cost_ly  = [int(v*0.88) for v in cost_ty]
        base = d["leads"]
        leads_ty = [int(base*0.55), int(base*0.70), int(base*0.85), base]
        leads_ly = [int(v*0.87) for v in leads_ty]
        base = d["appointments"]
        appts_ty = [int(base*0.55), int(base*0.70), int(base*0.85), base]
        appts_ly = [int(v*0.85) for v in appts_ty]
        base = d["customers"]
        cust_ty  = [int(base*0.55), int(base*0.70), int(base*0.85), base]
        cust_ly  = [int(v*0.85) for v in cust_ty]
 
    chart_js = f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:8px;">
      {"".join([
        f'<div style="background:#fff;border:0.5px solid #e5e7eb;border-radius:10px;padding:14px;">'
        f'<div style="font-size:11px;font-weight:500;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">{title}</div>'
        f'<div style="display:flex;gap:12px;margin-bottom:8px;">'
        f'<span style="display:flex;align-items:center;gap:4px;font-size:11px;color:#6b7280;"><span style="width:10px;height:10px;border-radius:2px;background:{cy_color};display:inline-block;"></span>This year</span>'
        f'<span style="display:flex;align-items:center;gap:4px;font-size:11px;color:#6b7280;"><span style="width:10px;height:10px;border-radius:2px;background:{ly_color};display:inline-block;"></span>Last year</span>'
        f'</div>'
        f'<div style="position:relative;height:200px;"><canvas id="{cid}"></canvas></div></div>'
        for title, cid, cy_color, ly_color in [
            ("Conversions", "c1", "#378ADD", "#B5D4F4"),
            ("Cost", "c2", "#378ADD", "#B5D4F4"),
            ("CRM Leads", "c3", "#1D9E75", "#9FE1CB"),
            ("Appointments & Customers", "c4", "#1D9E75", "#9FE1CB"),
        ]
      ])}
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    const TYPE = "{chart_type}";
    const LABELS = {labels};
    const DATASETS = [
      [{{data:{conv_ty},  ty:"#378ADD", ly:"#B5D4F4"}}, "c1"],
      [{{data:{cost_ty},  ty:"#378ADD", ly:"#B5D4F4"}}, "c2"],
      [{{data:{leads_ty}, ty:"#1D9E75", ly:"#9FE1CB"}}, "c3"],
      [{{data:{[a+b for a,b in zip(appts_ty, cust_ty)]}, ty:"#1D9E75", ly:"#9FE1CB"}}, "c4"],
    ];
    const LY = [{conv_ly}, {cost_ly}, {leads_ly}, {[a+b for a,b in zip(appts_ly, cust_ly)]}];
    const opts = {{
      responsive:true, maintainAspectRatio:false,
      plugins:{{legend:{{display:false}}}},
      scales:{{
        x:{{ticks:{{font:{{size:10}},autoSkip:false,maxRotation:30}},grid:{{display:false}}}},
        y:{{ticks:{{font:{{size:10}}}},grid:{{color:"#f3f4f6"}}}}
      }}
    }};
    DATASETS.forEach(([ds, cid], i) => {{
      const tyDs = TYPE === "bar"
        ? {{data:ds.data, backgroundColor:ds.ty, borderRadius:4}}
        : {{data:ds.data, borderColor:ds.ty, backgroundColor:ds.ty+"33", fill:true, tension:0.3, pointRadius:3}};
      const lyDs = TYPE === "bar"
        ? {{data:LY[i], backgroundColor:ds.ly, borderRadius:4}}
        : {{data:LY[i], borderColor:ds.ly, backgroundColor:ds.ly+"33", fill:true, tension:0.3, pointRadius:3, borderDash:[4,3]}};
      new Chart(document.getElementById(cid), {{
        type: TYPE,
        data: {{labels: LABELS, datasets: [tyDs, lyDs]}},
        options: JSON.parse(JSON.stringify(opts))
      }});
    }});
    </script>
    """
    st.components.v1.html(chart_js, height=520, scrolling=False)
