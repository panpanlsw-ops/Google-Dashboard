import streamlit as st
from datetime import date
import calendar
from data import get_data, CAMPAIGNS

st.set_page_config(
    page_title="Marketing Dashboard",
    page_icon="📊",
    layout="wide"
)

# ── Styling ──────────────────────────────────────────────────────────────────
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
        margin-top: 4px;
    }
    .pace-row {
        font-size: 12px;
        color: #185FA5;
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid #e5e7eb;
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
def projected(value: float, day: int, days_in_month: int) -> float:
    if day == 0:
        return 0
    return round((value / day) * days_in_month)


def pace_html(value: float, day: int, days_in_month: int, is_cost: bool = False) -> str:
    p = projected(value, day, days_in_month)
    formatted = f"${p:,}" if is_cost else f"{p:,}"
    days_left = days_in_month - day
    return f'<div class="pace-row">→ Projected month-end: <strong>{formatted}</strong> &nbsp;({days_left}d left)</div>'


def metric_card(label, value, sub=None, pace=None):
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    pace_html_str = f'<div class="pace-row">{pace}</div>' if pace else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {sub_html}
        {pace_html_str}
    </div>
    """, unsafe_allow_html=True)



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
    st.markdown(f"<div style='text-align:right; color:#6b7280; padding-top:8px;'>{today.strftime('%a, %b %d %Y')}</div>", unsafe_allow_html=True)

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
            pace=f"→ Projected month-end: <strong>{projected(d['conversions'], day_of_month, days_in_month):,}</strong> ({days_left}d left)"
        )
    with g2:
        metric_card(
            label="Cost",
            value=f"${d['cost']:,}",
            pace=f"→ Projected month-end: <strong>${projected(d['cost'], day_of_month, days_in_month):,}</strong> ({days_left}d left)"
        )

    st.markdown("<hr style='border:none; border-top:0.5px solid #e5e7eb; margin: 8px 0 16px;'>", unsafe_allow_html=True)

    # ── CRM section ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">CRM</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            label="CRM Leads",
            value=f"{d['leads']:,}",
            sub=f"🔵 Invoca {d['crm_invoca']:,} &nbsp;|&nbsp; 🟢 Form {d['crm_form']:,}",
            pace=f"→ Projected month-end: <strong>{projected(d['leads'], day_of_month, days_in_month):,}</strong> ({days_left}d left)"
        )
    with c2:
        metric_card(
            label="Appointments",
            value=f"{d['appointments']:,}",
            pace=f"→ Projected month-end: <strong>{projected(d['appointments'], day_of_month, days_in_month):,}</strong> ({days_left}d left)"
        )
    with c3:
        metric_card(
            label="Customers",
            value=f"{d['customers']:,}"
        )
