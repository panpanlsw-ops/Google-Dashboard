# data.py
# ─────────────────────────────────────────────────────────────────────────────
# This file is your data layer.
# RIGHT NOW: returns mock data so the dashboard works immediately.
# LATER: replace the mock_data dict with real API calls to your CRM,
#         Google Ads, and Invoca — without touching app.py at all.
# ─────────────────────────────────────────────────────────────────────────────

CAMPAIGNS = {
    "all":     "All campaigns",
    "brand":   "Brand awareness",
    "search":  "Search — HVAC",
    "display": "Display retargeting",
    "local":   "Local services ads",
}

# ── Mock data (replace with real API calls when ready) ────────────────────────
MOCK_DATA = {
    "all":     dict(conversions=184, invoca=112, form=72,  cost=4820, leads=201, crm_invoca=118, crm_form=83, appointments=47, customers=19),
    "brand":   dict(conversions=42,  invoca=28,  form=14,  cost=980,  leads=46,  crm_invoca=30,  crm_form=16, appointments=11, customers=4),
    "search":  dict(conversions=76,  invoca=44,  form=32,  cost=2210, leads=83,  crm_invoca=48,  crm_form=35, appointments=20, customers=8),
    "display": dict(conversions=38,  invoca=22,  form=16,  cost=890,  leads=41,  crm_invoca=24,  crm_form=17, appointments=10, customers=4),
    "local":   dict(conversions=28,  invoca=18,  form=10,  cost=740,  leads=31,  crm_invoca=16,  crm_form=15, appointments=6,  customers=3),
}


def get_data(campaign: str) -> dict:
    """
    Returns dashboard metrics for the given campaign key.

    TO CONNECT REAL DATA:
    1. Import your CRM / Google Ads / Invoca API clients here
    2. Fetch today's data
    3. Return a dict with the same keys as MOCK_DATA
    """
    # ── Swap this block with real API calls when ready ─────────────────────
    return MOCK_DATA.get(campaign, MOCK_DATA["all"])
    # ──────────────────────────────────────────────────────────────────────
