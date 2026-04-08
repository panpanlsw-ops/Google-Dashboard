import streamlit as st
from datetime import date
import calendar
from data import get_data, CAMPAIGNS
 
st.set_page_config(
    page_title="Marketing Dashboard",
    page_icon="📊",
    layout="wide"
)
 
# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 12px;
        color: #6b7280;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 600;
        color: #111827;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 12px;
        color: #6b7280;
        margin-top: 6px;
    }
    .pace-row {
        font-size: 12px;
        color: #185FA5;
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid #e5e7eb;
    }
    .pace-projected {
        font-weight: 600;
    }
    .section-title {
        font-size: 12px;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
        margin-top: 4px;
    }
    div[data-testid="stHorizontalBlock"] { gap: 12px; }
</style>
""", unsafe_allow_html=True)
 
 
# ── Pace helper ───────────────────────────────────────────────────────────────
def projected(value: float, day: int, days_in_month: int) -> int:
    if day == 0:
        return 0
    return round((value / day) * days_in_month)
 
 
# ── Metric card ───────────────────────────────────────────────────────────────
def metric_card(label, value, sub=None, pace_val=None, days_left=None):
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    if pace_val is not None:
        pace_html = (
            f'<div class="pace-row">'
            f'&#8594; Projected month-end: '
            f'<span class="pace-projected">{pace_val}</span>'
            f' &nbsp;({days_left}d left)'
            f'</div>'
        )
    else:
        pace_html = ""
 
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'{sub_html}'
        f'{pace_html}'
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
    st.markdown("## Performance Overview")
with col_date:
    st.markdown(
        f"<div style='text-align:right; color:#6b7280; padding-top:8px;'>"
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
 
    # ── Google section ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Google</div>', unsafe_allow_html=True)
    g1, g2 = st.columns(2)
 
    with g1:
        metric_card(
            label="Conversions",
            value=f"{d['conversions']:,}",
            sub=f"🔵 Invoca {d['invoca']:,} &nbsp;|&nbsp; 🟢 Form {d['form']:,}",
            pace_val=f"{projected(d['conversions'], day_of_month, days_in_month):,}",
            days_left=days_left
        )
    with g2:
        metric_card(
            label="Cost",
            value=f"${d['cost']:,}",
            pace_val=f"${projected(d['cost'], day_of_month, days_in_month):,}",
            days_left=days_left
        )
 
    st.markdown(
        "<hr style='border:none; border-top:0.5px solid #e5e7eb; margin: 8px 0 16px;'>",
        unsafe_allow_html=True
    )
 
    # ── CRM section ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">CRM</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
 
    with c1:
        metric_card(
            label="CRM Leads",
            value=f"{d['leads']:,}",
            sub=f"🔵 Invoca {d['crm_invoca']:,} &nbsp;|&nbsp; 🟢 Form {d['crm_form']:,}",
            pace_val=f"{projected(d['leads'], day_of_month, days_in_month):,}",
            days_left=days_left
        )
    with c2:
        metric_card(
            label="Appointments",
            value=f"{d['appointments']:,}",
            pace_val=f"{projected(d['appointments'], day_of_month, days_in_month):,}",
            days_left=days_left
        )
    with c3:
        metric_card(
            label="Customers",
            value=f"{d['customers']:,}"
        )
