# Marketing Dashboard

Live KPI dashboard built with Streamlit — showing Google Ads and CRM performance with month-end pace projections.

---

## Files

| File | What it does |
|------|-------------|
| `app.py` | The dashboard UI — tabs, cards, filters |
| `data.py` | Data layer — swap mock data for real API calls here |
| `requirements.txt` | Python packages needed to run |

---

## How to deploy (step by step)

### Step 1 — Upload to GitHub
1. Go to [github.com](https://github.com) and sign in
2. Click the **+** button (top right) → **New repository**
3. Name it `marketing-dashboard`, set to **Public**, click **Create repository**
4. Click **uploading an existing file**
5. Drag and drop all 3 files: `app.py`, `data.py`, `requirements.txt`
6. Click **Commit changes**

### Step 2 — Deploy on Streamlit Cloud (free)
1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
2. Click **New app**
3. Select your repository: `marketing-dashboard`
4. Main file path: `app.py`
5. Click **Deploy** — done!

You'll get a public link like: `https://yourname-marketing-dashboard.streamlit.app`

---

## How to connect real data later

Open `data.py` and replace the mock data inside `get_data()` with your real API calls.
Everything else (the UI in `app.py`) stays exactly the same.

```python
def get_data(campaign: str) -> dict:
    # Add your CRM / Google Ads / Invoca API calls here
    # Return a dict with these keys:
    return dict(
        conversions=...,
        invoca=...,
        form=...,
        cost=...,
        leads=...,
        crm_invoca=...,
        crm_form=...,
        appointments=...,
        customers=...
    )
```

---

## Adding more tabs later

In `app.py`, find this line:
```python
tab1, = st.tabs(["📈 Today"])
```
And change it to:
```python
tab1, tab2, tab3 = st.tabs(["📈 Today", "📋 Tab 2 name", "📋 Tab 3 name"])
```
