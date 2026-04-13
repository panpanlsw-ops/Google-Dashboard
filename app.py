import streamlit as st
from datetime import date, timedelta
import calendar
from data import get_data, get_roi_data, get_regional_data, get_campaign_data, CAMPAIGNS

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
        labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][:today.month]
        def series(field):
            return roi["ty_trend"][field], roi["ly_trend"][field]

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
        f'<div style="background:#fff;border:0.5px solid #e5e7eb;border-radius:10px;padding:14px;{span}">'
        f'<div style="font-size:11px;font-weight:500;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">{title}</div>'
        f'<div style="display:flex;gap:12px;margin-bottom:8px;">'
        f'<span style="display:flex;align-items:center;gap:4px;font-size:11px;color:#6b7280;"><span style="width:10px;height:10px;border-radius:2px;background:{cy};display:inline-block;"></span>This year</span>'
        f'<span style="display:flex;align-items:center;gap:4px;font-size:11px;color:#6b7280;"><span style="width:10px;height:10px;border-radius:2px;background:{lc};display:inline-block;"></span>Last year</span>'
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
    const TYPE="{chart_type}",LABELS={labels},isRoi=[false,false,false,false,false,false,false,true];
    const CHARTS=[["c1",{conv_ty},{conv_ly},"#378ADD","#B5D4F4"],["c2",{cost_ty},{cost_ly},"#378ADD","#B5D4F4"],
      ["c3",{leads_ty},{leads_ly},"#1D9E75","#9FE1CB"],["c4",{appts_ty},{appts_ly},"#1D9E75","#9FE1CB"],
      ["c5",{cust_ty},{cust_ly},"#1D9E75","#9FE1CB"],["c6",{cpl_ty},{cpl_ly},"#534AB7","#AFA9EC"],
      ["c7",{cpa_ty},{cpa_ly},"#534AB7","#AFA9EC"],["c8",{roi_ty},{roi_ly},"#BA7517","#FAC775"]];
    CHARTS.forEach(([cid,tyD,lyD,tyC,lyC],i)=>{{
      const r=isRoi[i];
      const opts={{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}},
        tooltip:{{callbacks:{{label:ctx=>r?' '+ctx.parsed.y+'%':' '+ctx.parsed.y.toLocaleString()}}}}}},
        scales:{{x:{{ticks:{{font:{{size:10}},autoSkip:false,maxRotation:30}},grid:{{display:false}}}},
        y:{{ticks:{{font:{{size:10}},callback:r?(v=>v+'%'):(v=>v.toLocaleString())}},grid:{{color:"#f3f4f6"}}}}}}}};
      const tyDs=TYPE==="bar"?{{data:tyD,backgroundColor:tyC,borderRadius:4}}:{{data:tyD,borderColor:tyC,backgroundColor:tyC+"33",fill:true,tension:0.3,pointRadius:3}};
      const lyDs=TYPE==="bar"?{{data:lyD,backgroundColor:lyC,borderRadius:4}}:{{data:lyD,borderColor:lyC,backgroundColor:lyC+"33",fill:true,tension:0.3,pointRadius:3,borderDash:[4,3]}};
      new Chart(document.getElementById(cid),{{type:TYPE,data:{{labels:LABELS,datasets:[tyDs,lyDs]}},options:opts}});
    }});
    </script>"""
    st.components.v1.html(chart_html, height=980, scrolling=False)


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
    with r1: metric_card("Total Leads",  f"{total_nl:,}",          "blue")
    with r2: metric_card("Appointments", f"{total_apt:,}",         "blue")
    with r3: metric_card("Customers",    f"{total_cust:,}",        "teal")
    with r4: metric_card("Total Sales",  f"${total_sales:,.0f}",   "teal")
    with r5: metric_card("Apt / Leads",  f"{round(total_apt/total_nl*100) if total_nl else 0}%", "teal")

    st.markdown("<br>", unsafe_allow_html=True)

    def money(n): return f"${n:,.2f}" if n else "$0.00"

    COLORS = ["#378ADD","#1D9E75","#534AB7","#D85A30","#BA7517","#D4537E",
              "#639922","#888780","#E24B4A","#7F77DD","#5DCAA5","#F0997B",
              "#97C459","#EF9F27","#ED93B1","#B4B2A9"]

    rows_html = ""
    pie_names = []
    pie_leads = []
    pie_sales = []

    for i, o in enumerate(offices):
        lp  = o["nl"]    / total_nl    * 100 if total_nl    else 0
        sp  = o["sales"] / total_sales * 100 if total_sales else 0
        al  = o["apt"]   / o["nl"]     * 100 if o["nl"]     else 0
        oa  = o["cust"]  / o["apt"]    * 100 if o["apt"]    else None
        ol  = o["cust"]  / o["nl"]     * 100 if o["nl"]     else 0
        pie_names.append(o["name"])
        pie_leads.append(round(lp, 1))
        pie_sales.append(round(sp, 1))
        bar_w_l = min(int(lp / 20 * 100), 100)
        bar_w_s = min(int(sp / 25 * 100), 100)
        lp_badge = f'<span style="font-size:10px;font-weight:500;padding:2px 6px;border-radius:4px;background:#d1fae5;color:#065f46;">{lp:.2f}%</span>' if lp >= 10 else f'<span style="font-size:11px;color:#374151;">{lp:.2f}%</span>'
        sp_badge = f'<span style="font-size:10px;font-weight:500;padding:2px 6px;border-radius:4px;background:#d1fae5;color:#065f46;">{sp:.2f}%</span>' if sp >= 10 else f'<span style="font-size:11px;color:#374151;">{sp:.2f}%</span>'
        al_badge = f'<span style="font-size:10px;font-weight:500;padding:2px 6px;border-radius:4px;background:#dbeafe;color:#1e40af;">{al:.2f}%</span>' if al >= 50 else f'<span style="font-size:11px;color:#374151;">{al:.2f}%</span>'
        bar_l = f'<div style="display:flex;align-items:center;gap:6px;justify-content:flex-end;"><div style="width:60px;height:6px;background:#f3f4f6;border-radius:3px;overflow:hidden;"><div style="width:{bar_w_l}%;height:100%;background:#378ADD;border-radius:3px;"></div></div>{lp_badge}</div>'
        bar_s = f'<div style="display:flex;align-items:center;gap:6px;justify-content:flex-end;"><div style="width:60px;height:6px;background:#f3f4f6;border-radius:3px;overflow:hidden;"><div style="width:{bar_w_s}%;height:100%;background:#1D9E75;border-radius:3px;"></div></div>{sp_badge}</div>'
        rows_html += f"""<tr>
          <td style="text-align:left;font-weight:500;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;color:#111827;">{o['name']}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;color:#374151;">{o['ul']}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;color:#374151;">{o['nl']}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;color:#374151;">{o['apt']}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;color:#374151;">{o['quote']}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;color:#374151;">{o['cust']}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;color:#374151;">{money(o['sales'])}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;color:#374151;">{o['nlc']}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;color:#374151;">{money(o['nl_sales'])}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;">{bar_l}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;">{bar_s}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;">{al_badge}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;color:#374151;">{f"{oa:.2f}%" if oa is not None else "#DIV/0!"}</td>
          <td style="text-align:right;padding:7px 10px;border-bottom:0.5px solid #f3f4f6;color:#374151;">{ol:.2f}%</td>
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
    camp_names = [c["name"] for c in camp_data]
    MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    tab3_html = f"""
    <style>
    .t3-wrap {{ padding: 0.5rem 0; font-family: sans-serif; }}
    .t3-header {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; flex-wrap:wrap; gap:8px; }}
    .t3-title {{ font-size:15px; font-weight:500; color:#111827; }}
    .t3-controls {{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; }}
    .t3-controls select {{ font-size:12px; padding:5px 10px; border-radius:8px; border:0.5px solid #d1d5db; background:#fff; color:#374151; }}
    .t3-controls label {{ font-size:12px; color:#6b7280; }}
    .t3-apply {{ font-size:12px; padding:5px 14px; border-radius:8px; border:0.5px solid #111827; background:#111827; color:#fff; cursor:pointer; }}
    .t3-badge {{ font-size:12px; color:#6b7280; background:#f9fafb; border:0.5px solid #e5e7eb; border-radius:8px; padding:5px 12px; display:inline-block; margin-bottom:12px; }}
    .t3-tbl {{ width:100%; border-collapse:collapse; font-size:11px; white-space:nowrap; }}
    .t3-tbl thead tr {{ background:#111827; }}
    .t3-tbl th {{ padding:8px 8px; font-size:10px; font-weight:500; color:#9ca3af; text-transform:uppercase; letter-spacing:0.04em; text-align:right; }}
    .t3-tbl th:first-child {{ text-align:left; color:#fff; }}
    .t3-tbl td {{ padding:6px 8px; border-bottom:0.5px solid #f3f4f6; text-align:right; color:#374151; cursor:pointer; }}
    .t3-tbl td:first-child {{ text-align:left; font-weight:500; color:#111827; }}
    .t3-tbl tfoot td {{ font-weight:600; background:#f8f9fa; border-top:0.5px solid #e5e7eb; color:#111827; padding:7px 8px; }}
    .t3-tbl tr.data-row:hover td {{ background:#f0f9ff; }}
    .t3-tbl tr.sel td {{ background:#dbeafe !important; }}
    .rp {{ background:#d1fae5; color:#065f46; padding:2px 5px; border-radius:4px; font-size:10px; font-weight:500; }}
    .rn {{ background:#fee2e2; color:#991b1b; padding:2px 5px; border-radius:4px; font-size:10px; font-weight:500; }}
    .pg {{ background:#d1fae5; color:#065f46; padding:2px 5px; border-radius:4px; font-size:10px; font-weight:500; }}
    .pr {{ background:#fee2e2; color:#991b1b; padding:2px 5px; border-radius:4px; font-size:10px; font-weight:500; }}
    .row-hl {{ background:#fefce8; }}
    .chart-box {{ background:#fff; border:0.5px solid #e5e7eb; border-radius:10px; padding:14px; margin-top:14px; }}
    .chart-top {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:6px; flex-wrap:wrap; gap:8px; }}
    .chart-name {{ font-size:13px; font-weight:500; color:#111827; }}
    .chart-hint {{ font-size:11px; color:#6b7280; margin-top:2px; }}
    .leg {{ display:flex; gap:14px; }}
    .leg-i {{ display:flex; align-items:center; gap:4px; font-size:11px; color:#6b7280; }}
    .leg-d {{ width:10px; height:10px; border-radius:2px; flex-shrink:0; }}
    .m-tabs {{ display:flex; gap:6px; flex-wrap:wrap; margin-bottom:10px; }}
    .m-tab {{ font-size:11px; padding:4px 10px; border-radius:6px; border:0.5px solid #e5e7eb; background:#fff; color:#6b7280; cursor:pointer; }}
    .m-tab.active {{ background:#111827; color:#fff; border-color:#111827; }}
    </style>

    <div class="t3-wrap">
      <div class="t3-header">
        <span class="t3-title">Campaign Performance</span>
        <div class="t3-controls">
          <label>From</label>
          <select id="t3-fm"><option value="0">Jan</option><option value="1">Feb</option><option value="2">Mar</option><option value="3">Apr</option><option value="4">May</option><option value="5">Jun</option><option value="6">Jul</option><option value="7">Aug</option><option value="8">Sep</option><option value="9">Oct</option><option value="10">Nov</option><option value="11">Dec</option></select>
          <select id="t3-fy"><option>2024</option><option>2025</option><option selected>2026</option></select>
          <label>To</label>
          <select id="t3-tm"><option value="0">Jan</option><option value="1">Feb</option><option value="2">Mar</option><option value="3" selected>Apr</option><option value="4">May</option><option value="5">Jun</option><option value="6">Jul</option><option value="7">Aug</option><option value="8">Sep</option><option value="9">Oct</option><option value="10">Nov</option><option value="11">Dec</option></select>
          <select id="t3-ty"><option>2024</option><option>2025</option><option selected>2026</option></select>
          <button class="t3-apply" onclick="t3Apply()">Apply</button>
        </div>
      </div>
      <div id="t3-badge" class="t3-badge"></div>
      <div style="overflow-x:auto;margin-bottom:4px;">
      <table class="t3-tbl">
        <thead><tr>
          <th>Campaign</th><th>Clicks</th><th>Cost</th><th>Conv.</th><th>Cost/Conv.</th>
          <th>Leads</th><th>Apt</th><th>Customers</th><th>Sales</th><th>ROI</th><th>Apt/Lead</th><th>Order/Apt</th>
        </tr></thead>
        <tbody id="t3-tbody">
          {"".join([f'<tr class="data-row{" row-hl" if i%5==1 else ""}" onclick="t3Select(this,{i})"><td>{c["name"]}</td>'+
            "".join([f'<td id="t3-r{i}-{f}">—</td>' for f in ["clicks","cost","conv","cpc","leads","apt","cust","sales","roi","al","oa"]])+
            "</tr>" for i,c in enumerate(camp_data)])}
          <tr style="font-style:italic;"><td colspan="12" style="text-align:center;color:#9ca3af;padding:6px;">Click any row to see monthly trend</td></tr>
        </tbody>
        <tfoot id="t3-tfoot"></tfoot>
      </table>
      </div>

      <div class="chart-box">
        <div class="chart-top">
          <div>
            <div class="chart-name" id="t3-cname">{camp_data[0]["name"] if camp_data else "Campaign"} — Monthly Trend</div>
            <div class="chart-hint" id="t3-chint"></div>
          </div>
          <div class="leg">
            <span class="leg-i"><span class="leg-d" style="background:#378ADD"></span><span id="t3-lty">Selected period</span></span>
            <span class="leg-i"><span class="leg-d" style="background:#B5D4F4"></span><span id="t3-lly">Same period last year</span></span>
          </div>
        </div>
        <div class="m-tabs" id="t3-mtabs">
          <button class="m-tab active" onclick="t3Metric('clicks',this)">Clicks</button>
          <button class="m-tab" onclick="t3Metric('cost',this)">Cost</button>
          <button class="m-tab" onclick="t3Metric('conv',this)">Conversions</button>
          <button class="m-tab" onclick="t3Metric('leads',this)">Leads</button>
          <button class="m-tab" onclick="t3Metric('apt',this)">Appointments</button>
          <button class="m-tab" onclick="t3Metric('sales',this)">Sales</button>
          <button class="m-tab" onclick="t3Metric('roi',this)">ROI %</button>
        </div>
        <div style="position:relative;height:240px;"><canvas id="t3-chart"></canvas></div>
      </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    const T3_MONTHS = {MONTH_NAMES};
    const T3_DATA   = {[dict(name=c["name"], trend=c["trend"]) for c in camp_data]};

    let t3FM=0,t3FY=2026,t3TM=3,t3TY=2026;
    let t3Camp=0, t3Metric='clicks', t3Chart=null;

    function t3GetMonths(fm,fy,tm,ty){{
      const r=[];let m=fm,y=fy;
      while(y<ty||(y===ty&&m<=tm)){{r.push({{m,y}});m++;if(m>11){{m=0;y++;}}}}
      return r;
    }}
    function t3Sum(campIdx,months,field){{
      return months.reduce((s,{{m,y}})=>s+(T3_DATA[campIdx]?.trend?.[y]?.[field]?.[m]||0),0);
    }}
    function t3AvgRoi(campIdx,months){{
      const valid=months.filter(({m,y})=>(T3_DATA[campIdx]?.trend?.[y]?.clicks?.[m]||0)>0);
      return valid.length?valid.reduce((s,{{m,y}})=>s+(T3_DATA[campIdx]?.trend?.[y]?.roi?.[m]||0),0)/valid.length:0;
    }}
    function roiBadge(v){{return v>=0?`<span class="rp">${{v.toFixed(1)}}%</span>`:`<span class="rn">${{v.toFixed(1)}}%</span>`;}}
    function pctBadge(v,t){{if(!isFinite(v))return'—';return v>=t?`<span class="pg">${{v.toFixed(1)}}%</span>`:`<span class="pr">${{v.toFixed(1)}}%</span>`;}}
    function money(n){{return n>0?'$'+Math.round(n).toLocaleString():'$0';}}

    function t3Apply(){{
      t3FM=parseInt(document.getElementById('t3-fm').value);
      t3FY=parseInt(document.getElementById('t3-fy').value);
      t3TM=parseInt(document.getElementById('t3-tm').value);
      t3TY=parseInt(document.getElementById('t3-ty').value);
      const months=t3GetMonths(t3FM,t3FY,t3TM,t3TY);
      document.getElementById('t3-badge').textContent=
        T3_MONTHS[t3FM]+' '+t3FY+' → '+T3_MONTHS[t3TM]+' '+t3TY+'  |  vs same period '+(t3FY-1)+'–'+(t3TY-1);

      T3_DATA.forEach((c,i)=>{{
        const clicks=t3Sum(i,months,'clicks'),cost=t3Sum(i,months,'cost'),
              conv=t3Sum(i,months,'conv'),leads=t3Sum(i,months,'leads'),
              apt=t3Sum(i,months,'apt'),cust=t3Sum(i,months,'cust'),
              sales=t3Sum(i,months,'sales'),roi=t3AvgRoi(i,months),
              cpc=conv>0?cost/conv:0,al=leads>0?apt/leads*100:0,oa=apt>0?cust/apt*100:null;
        const set=(f,v)=>{{const el=document.getElementById(`t3-r${{i}}-${{f}}`);if(el)el.innerHTML=v;}};
        set('clicks',clicks.toLocaleString()); set('cost',money(cost));
        set('conv',conv.toLocaleString()); set('cpc',cpc>0?'$'+Math.round(cpc):'—');
        set('leads',leads.toLocaleString()); set('apt',apt.toLocaleString());
        set('cust',cust.toLocaleString()); set('sales',money(sales));
        set('roi',roiBadge(roi)); set('al',pctBadge(al,30));
        set('oa',oa!==null?pctBadge(oa,20):'#DIV/0!');
      }});

      const fields=['clicks','cost','conv','leads','apt','cust','sales'];
      const tots={{}};fields.forEach(f=>{{tots[f]=T3_DATA.reduce((s,_,i)=>s+t3Sum(i,months,f),0);}});
      const avgRoi=T3_DATA.reduce((s,_,i)=>s+t3AvgRoi(i,months),0)/T3_DATA.length;
      document.getElementById('t3-tfoot').innerHTML=`
        <tr><td>Total</td><td>${{tots.clicks.toLocaleString()}}</td><td>${{money(tots.cost)}}</td><td>${{tots.conv}}</td><td>—</td>
        <td>${{tots.leads}}</td><td>${{tots.apt}}</td><td>${{tots.cust}}</td><td>${{money(tots.sales)}}</td>
        <td>${{roiBadge(avgRoi)}}</td><td>${{pctBadge(tots.leads>0?tots.apt/tots.leads*100:0,30)}}</td>
        <td>${{pctBadge(tots.apt>0?tots.cust/tots.apt*100:0,15)}}</td></tr>`;
      t3UpdateChart();
    }}

    function t3Select(row,idx){{
      document.querySelectorAll('#t3-tbody tr.data-row').forEach(r=>r.classList.remove('sel'));
      row.classList.add('sel');
      t3Camp=idx;
      document.getElementById('t3-cname').textContent=T3_DATA[idx].name+' — Monthly Trend';
      t3UpdateChart();
    }}

    function t3Metric(m,btn){{
      t3Metric=m;
      document.querySelectorAll('.m-tab').forEach(b=>b.classList.remove('active'));
      btn.classList.add('active');
      t3UpdateChart();
    }}

    function t3UpdateChart(){{
      const isRoi=t3Metric==='roi';
      const months=t3GetMonths(t3FM,t3FY,t3TM,t3TY);
      const lyMonths=months.map(({m,y})=>({m,y:y-1}));
      const labels=months.map(({m,y})=>T3_MONTHS[m]+' '+y);
      const tyData=months.map(({m,y})=>T3_DATA[t3Camp]?.trend?.[y]?.[t3Metric]?.[m]||0);
      const lyData=lyMonths.map(({m,y})=>T3_DATA[t3Camp]?.trend?.[y]?.[t3Metric]?.[m]||0);
      const tyYr=[...new Set(months.map(x=>x.y))].join('–');
      const lyYr=[...new Set(lyMonths.map(x=>x.y))].join('–');
      document.getElementById('t3-lty').textContent=tyYr;
      document.getElementById('t3-lly').textContent=lyYr;
      document.getElementById('t3-chint').textContent=
        T3_MONTHS[t3FM]+' '+t3FY+' → '+T3_MONTHS[t3TM]+' '+t3TY+'  |  vs same period last year';
      if(t3Chart)t3Chart.destroy();
      t3Chart=new Chart(document.getElementById('t3-chart'),{{
        type:'line',
        data:{{labels,datasets:[
          {{data:tyData,borderColor:'#378ADD',backgroundColor:'#378ADD22',fill:true,tension:0.3,pointRadius:4}},
          {{data:lyData,borderColor:'#B5D4F4',backgroundColor:'#B5D4F422',fill:true,tension:0.3,pointRadius:4,borderDash:[5,4]}},
        ]}},
        options:{{responsive:true,maintainAspectRatio:false,
          plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:ctx=>isRoi?' '+ctx.parsed.y+'%':' '+ctx.parsed.y.toLocaleString()}}}}}},
          scales:{{
            x:{{ticks:{{font:{{size:10}},maxRotation:45,autoSkip:true,maxTicksLimit:16}},grid:{{display:false}}}},
            y:{{ticks:{{font:{{size:10}},callback:isRoi?(v=>v+'%'):(v=>v.toLocaleString())}},grid:{{color:'#f3f4f6'}}}}
          }}
        }}
      }});
    }}
    t3Apply();
    </script>
    """
    st.components.v1.html(tab3_html, height=len(camp_data)*36+720, scrolling=False)
