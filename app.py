import streamlit as st
from datetime import date
import calendar
from data import get_data, CAMPAIGNS
 
st.set_page_config(
    page_title="Daily Report",
    page_icon="📊",
    layout="wide"
)
 
# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        min-height: 120px;
        background: #ffffff;
        border: 0.5px solid #e5e7eb;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 4px;
    }
    .metric-accent { height: 3px; }
    .accent-blue { background: #378ADD; }
    .accent-teal { background: #1D9E75; }
    .metric-body { padding: 10px 12px; }
    .metric-label {
        font-size: 10px;
        color: #6b7280;
        margin: 0 0 3px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 22px;
        font-weight: 600;
        color: #111827;
        margin: 0;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 10px;
        color: #9ca3af;
        margin: 3px 0 0;
    }
    .pace-row {
        font-size: 10px;
        color: #185FA5;
        margin-top: 6px;
        padding-top: 6px;
        border-top: 0.5px solid #e5e7eb;
    }
    .pace-projected { font-weight: 600; }
    div[data-testid="stHorizontalBlock"] { gap: 8px; }
</style>
""", unsafe_allow_html=True)
 
 
# ── Pace helper ───────────────────────────────────────────────────────────────
def projected(value: float, day: int, days_in_month: int) -> int:
    if day == 0:
        return 0
    return round((value / day) * days_in_month)
 
 
# ── Metric card ───────────────────────────────────────────────────────────────
def metric_card(label, value, accent="blue", sub=None, pace_val=None, days_left=None):
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    if pace_val is not None:
        pace_html = (
            f'<div class="pace-row">'
            f'&#8594; Month-end: '
            f'<span class="pace-projected">{pace_val}</span>'
            f' ({days_left}d)'
            f'</div>'
        )
    else:
        pace_html = ""
 
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-accent accent-{accent}"></div>'
        f'<div class="metric-body">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'{sub_html}'
        f'{pace_html}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )
 
 
# ── Date info ─────────────────────────────────────────────────────────────────
today = date.today()
day_of_month = today.day
days_in_month = calendar.monthrange(today.year, today.month)[1]
days_left = days_in_month - day_of_month
 
 
# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_date = st.columns([3, 1])
with col_title:
    st.markdown("# Daily Report")
    st.markdown("## Performance Overview")
with col_date:
    st.markdown(
        f"<div style='text-align:right; color:#6b7280; padding-top:16px;'>"
        f"{today.strftime('%a, %b %d %Y')}</div>",
        unsafe_allow_html=True
    )
 
# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, = st.tabs(["📈 Today"])
 
with tab1:
 
    # Campaign filter
    campaign = st.selectbox(
        "Campaign",
        options=list(CAMPAIGNS.keys()),
        format_func=lambda x: CAMPAIGNS[x]
    )
 
    d = get_data(campaign)
 
    # ── 5 cards in one row ────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
 
    with c1:
        metric_card(
            label="Conversions",
            value=f"{d['conversions']:,}",
            accent="blue",
            sub=f"Invoca {d['invoca']:,} · Form {d['form']:,}",
            pace_val=f"{projected(d['conversions'], day_of_month, days_in_month):,}",
            days_left=days_left
        )
    with c2:
        metric_card(
            label="Cost",
            value=f"${d['cost']:,}",
            accent="blue",
            pace_val=f"${projected(d['cost'], day_of_month, days_in_month):,}",
            days_left=days_left
        )
    with c3:
        metric_card(
            label="CRM Leads",
            value=f"{d['leads']:,}",
            accent="teal",
            sub=f"Invoca {d['crm_invoca']:,} · Form {d['crm_form']:,}",
            pace_val=f"{projected(d['leads'], day_of_month, days_in_month):,}",
            days_left=days_left
        )
    with c4:
        metric_card(
            label="Appointments",
            value=f"{d['appointments']:,}",
            accent="teal",
            pace_val=f"{projected(d['appointments'], day_of_month, days_in_month):,}",
            days_left=days_left
        )
    with c5:
        metric_card(
            label="Customers",
            value=f"{d['customers']:,}",
            accent="teal"
        )
 
    # ── Space for future content ───────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
