"""Kalshibot Mission Control — Streamlit adaptation, read-only and demo-safe.
Original code is JavaScript/Node; this is a Python dashboard inspired by its sections.
It does not execute Kalshi orders or use production credentials.
"""
import datetime as dt
import math
import os
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="KALSHIBOT | Mission Control", page_icon="◆", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
.stApp{background:#090c14;color:#e1e6f4}
.block-container{padding-top:1.15rem;max-width:1550px}
h1,h2,h3{color:#eaf0ff}
[data-testid="stMetric"]{background:#121725;border:1px solid #2a3247;border-radius:11px;padding:16px}
[data-testid="stMetricLabel"]{color:#94a3b8}
div[data-testid="stVerticalBlockBorderWrapper"]>div{background:#111624;border-color:#30384c}
.stButton button{background:#142b36;border:1px solid #237b8a;color:#bdf3ff}
hr{border-color:#293244}
</style>""", unsafe_allow_html=True)

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Kalshibot-Streamlit-ReadOnly/1.0"})

@st.cache_data(ttl=8, show_spinner=False)
def get_btc():
    try:
        j=SESSION.get("https://api.binance.com/api/v3/ticker/price", params={"symbol":"BTCUSDT"},timeout=6)
        j.raise_for_status()
        return float(j.json()["price"]), "Binance BTC/USDT"
    except Exception:
        try:
            j=SESSION.get("https://api.coinbase.com/v2/prices/BTC-USD/spot",timeout=6)
            j.raise_for_status()
            return float(j.json()["data"]["amount"]),"Coinbase BTC/USD (fallback)"
        except Exception:
            return None,"Unavailable"

@st.cache_data(ttl=12, show_spinner=False)
def get_markets():
    base="https://api.elections.kalshi.com/trade-api/v2/markets"
    try:
        j=SESSION.get(base,params={"series_ticker":"KXBTC15M","status":"open","limit":100},timeout=9)
        j.raise_for_status()
        return j.json().get("markets",[]),None
    except Exception as e:
        return [],str(e)

def number(m,k):
    try:
        v=m.get(k)
        if v is None: return None
        return float(v)
    except (ValueError, TypeError):return None

def cents(m,side):
    # Kalshi legacy cent values take precedence; *_dollars in newer APIs are USD.
    v=number(m,side)
    if v is not None:return v
    v=number(m,side+"_dollars")
    return None if v is None else v*100

def show_cents(n):return "—" if n is None else f"{n:.0f}¢"

now=dt.datetime.now(ZoneInfo("America/New_York"))
a,b=st.columns([3,1])
with a:
    st.markdown("# ◆ KALSHIBOT  ·  MISSION CONTROL")
with b:
    st.caption(f"Eastern Time · {now:%b %d, %Y  %I:%M:%S %p}")
    if st.button("↻ Refresh public data",use_container_width=True):
        get_btc.clear();get_markets.clear();st.rerun()
st.caption("**READ-ONLY / DEMO** · Production order placement disabled · Original Kalshibot Node.js engine is not running in Streamlit")

price,source=get_btc()
markets,error=get_markets()

m1,m2,m3,m4=st.columns(4)
m1.metric("BTC/USD",f"${price:,.2f}" if price else "Unavailable",help=source)
m2.metric("TOTAL P&L", "—", help="No original trading ledger attached; not a simulated or real result")
m3.metric("ROI", "—",help="Unavailable until a journal is connected")
m4.metric("DEMO BALANCE", "Not connected",help="The original server maintains its own balance and positions")

with st.container(border=True):
    c1,c2=st.columns([3,1])
    c1.subheader("BOT INTENT")
    c2.markdown("**STATUS: OBSERVATION ONLY**")
    st.write("Live public-market observation is enabled. The original strategy engine, trained ML scorer, and execution system are not running in this Streamlit port.")
    i1,i2,i3,i4=st.columns(4)
    i1.metric("ACTION","HOLD")
    i2.metric("MODEL P(UP)","—")
    i3.metric("MODEL EDGE","—")
    i4.metric("ACTIVE KALSHI MARKETS",str(len(markets)))

chart_col,position_col=st.columns([2,1])
with chart_col:
    with st.container(border=True):
        st.subheader("P&L HISTORY")
        st.info("No P&L values are invented. Connect an existing demo trade journal to populate this chart.")
with position_col:
    with st.container(border=True):
        st.subheader("OPEN POSITIONS")
        st.write("No positions loaded. This dashboard has no access to the original Node.js engine's position state.")

with st.container(border=True):
    st.subheader("ACTIVE KALSHI BTC 15-MINUTE MARKETS")
    if error:st.warning("Kalshi public API request failed: "+error)
    if markets:
        rows=[]
        for m in markets:
            yb,ya,nb,na=[cents(m,k) for k in ("yes_bid","yes_ask","no_bid","no_ask")]
            combined=None if ya is None or na is None else ya+na
            rows.append({"Ticker":m.get("ticker",""),"YES bid":show_cents(yb),"YES ask":show_cents(ya),
                "NO bid":show_cents(nb),"NO ask":show_cents(na),"Combined ask":show_cents(combined),
                "Status":m.get("status",""),"Close":m.get("close_time","" )})
        st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
    elif not error:st.info("No open markets returned by Kalshi at this moment.")
    st.caption("A YES+NO quoted total below $1 does not guarantee an executable profit: fees, depth, partial fills and latency matter.")

with st.container(border=True):
    st.subheader("TRADE LOG")
    st.info("No trades imported. Existing GitHub, Supabase and Kalshi account history are not modified.")

with st.container(border=True):
    st.subheader("PERFORMANCE STATISTICS")
    stats=["Total Trades","Win Rate","Wins","Losses","Volume","Trades/Hour","Open Positions","Profit Factor","Avg Win","Avg Loss","Streak","Unrealized P&L"]
    cols=st.columns(4)
    for i,k in enumerate(stats):cols[i%4].metric(k,"—")

with st.expander("Strategy modules preserved in the original ZIP (not executed here)"):
    st.markdown("""Original JavaScript source includes Binance / RedStone / Polymarket market feeds, Kalshi market data,
    directional GBM-derived probabilities, cross-exchange signal generation, dual-side pricing scans,
    Kelly sizing, ML signal scoring, risk controls, trade execution and state recording.
    This read-only Python UI does **not** claim these modules run or produce equivalent signals.""")
with st.expander("About deploying the exact original interface"):
    st.markdown("""The **exact** original Mission Control UI is in `original-node-app/public/`.
    It depends on `server.js`, Express, Socket.IO and a running Node.js trading engine; it cannot be run directly
    by Streamlit Cloud. To view that exact UI, deploy the Node.js app as a separate service. Keep trading
    endpoints locked down and do not publish production API keys. The original code is supplied for reference,
    not automatically launched by this Streamlit application.""")

st.caption("Original source retained in the accompanying project archive · No orders submitted · No private account APIs used")
