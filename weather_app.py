"""
╔══════════════════════════════════════════════════════════════╗
║  WEATHER ENERGY SIGNAL — Web App Demo                        ║
║  Alternative Data Signal Framework                           ║
║  Streamlit dark-mode dashboard per SGR/SIM italiane          ║
╚══════════════════════════════════════════════════════════════╝

Installazione dipendenze:
    pip install streamlit plotly pandas numpy scipy yfinance requests openpyxl

Avvio:
    streamlit run weather_app.py

Struttura pagine (sidebar):
    1. 📡 Signal Dashboard   — segnale attuale + KPI
    2. 🌡️ Weather Analysis   — grafici meteo e WEI
    3. 📈 Backtest           — performance e metriche
    4. 📖 Metodologia        — spiegazione del modello
    5. 📤 Export             — download Excel/CSV
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats
from datetime import datetime, timedelta
import requests
import warnings
import io
import os

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# CONFIGURAZIONE PAGINA
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Weather Energy Signal",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# CSS — Dark mode Bloomberg-style
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Import font ── */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── Root variables ── */
:root {
    --bg-primary:    #0a0e17;
    --bg-secondary:  #111827;
    --bg-card:       #151d2e;
    --bg-card-hover: #1a2540;
    --border:        #1e2d47;
    --border-bright: #2a3f63;
    --text-primary:  #e8edf5;
    --text-secondary:#8a9ab5;
    --text-dim:      #4a5a75;
    --accent-blue:   #3b82f6;
    --accent-cyan:   #06b6d4;
    --accent-green:  #10b981;
    --accent-red:    #ef4444;
    --accent-amber:  #f59e0b;
    --accent-purple: #8b5cf6;
    --long-color:    #10b981;
    --short-color:   #ef4444;
    --neutral-color: #8a9ab5;
}

/* ── Base ── */
.stApp { background: var(--bg-primary); color: var(--text-primary); }
.main .block-container { padding: 1.5rem 2rem; max-width: 1600px; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stRadio label {
    color: var(--text-secondary) !important;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
}

/* ── Typography ── */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em;
}
p, div, span, label {
    font-family: 'JetBrains Mono', monospace;
}

/* ── KPI Card ── */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
}
.kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.5rem;
}
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.kpi-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-secondary);
}

/* ── Signal Badge ── */
.signal-badge {
    display: inline-block;
    padding: 0.4rem 1.2rem;
    border-radius: 4px;
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.badge-long    { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid #10b981; }
.badge-short   { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid #ef4444; }
.badge-neutral { background: rgba(138,154,181,0.1); color: #8a9ab5; border: 1px solid #4a5a75; }

/* ── Section header ── */
.section-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--accent-cyan);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    margin: 1.5rem 0 1rem 0;
}

/* ── Data table ── */
.stDataFrame { background: var(--bg-card) !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 8px; }

/* ── Selectbox / slider ── */
.stSelectbox select, .stSlider { color: var(--text-primary) !important; }

/* ── Metric override ── */
[data-testid="metric-container"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
}

/* ── Top bar ── */
.top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.8rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.top-bar-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.03em;
}
.top-bar-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-dim);
}
.dot-live {
    display: inline-block;
    width: 7px; height: 7px;
    background: var(--accent-green);
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.3; }
}

/* ── Disclaimer box ── */
.disclaimer {
    background: rgba(245,158,11,0.05);
    border: 1px solid rgba(245,158,11,0.2);
    border-left: 3px solid var(--accent-amber);
    border-radius: 4px;
    padding: 0.8rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-secondary);
    margin-top: 1rem;
}

/* ── Methodology card ── */
.method-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.4rem;
    margin-bottom: 1rem;
}
.method-card h4 {
    font-family: 'Syne', sans-serif !important;
    font-size: 1rem;
    color: var(--accent-cyan) !important;
    margin-bottom: 0.8rem;
}
.method-card p {
    font-size: 0.8rem;
    color: var(--text-secondary);
    line-height: 1.7;
}

/* ── Chain box ── */
.chain-box {
    background: var(--bg-secondary);
    border: 1px solid var(--border-bright);
    border-radius: 6px;
    padding: 1rem 1.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--accent-cyan);
    text-align: center;
    letter-spacing: 0.05em;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# COSTANTI E CONFIG
# ─────────────────────────────────────────────────────────────
STATIONS = {
    'AMS': {'name': 'Amsterdam',  'lat': 52.37, 'lon':  4.90, 'weight': 0.20},
    'FRA': {'name': 'Frankfurt',  'lat': 50.11, 'lon':  8.68, 'weight': 0.25},
    'PAR': {'name': 'Paris',      'lat': 48.85, 'lon':  2.35, 'weight': 0.20},
    'MIL': {'name': 'Milan',      'lat': 45.46, 'lon':  9.19, 'weight': 0.15},
    'LON': {'name': 'London',     'lat': 51.50, 'lon': -0.12, 'weight': 0.10},
    'WAW': {'name': 'Warsaw',     'lat': 52.23, 'lon': 21.01, 'weight': 0.10},
}
HDD_BASE   = 15.5
CDD_BASE   = 22.0
START_DATE = '2015-01-01'
END_DATE   = datetime.today().strftime('%Y-%m-%d')
ZSCORE_WIN = 365
THR_LONG   = 1.0
THR_SHORT  = -1.0

# Plotly dark theme base
PLOTLY_DARK = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(21,29,46,0.6)',
    font=dict(family='JetBrains Mono', color='#8a9ab5', size=11),
    xaxis=dict(gridcolor='#1e2d47', linecolor='#1e2d47', tickfont=dict(size=10)),
    yaxis=dict(gridcolor='#1e2d47', linecolor='#1e2d47', tickfont=dict(size=10)),
    legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='#1e2d47', borderwidth=1),
    margin=dict(l=50, r=20, t=40, b=40),
)

# ─────────────────────────────────────────────────────────────
# DATA PIPELINE — cached
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_weather(start, end):
    """Scarica dati meteo da Open-Meteo per tutte le stazioni."""
    frames = []
    for code, st_info in STATIONS.items():
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": st_info['lat'], "longitude": st_info['lon'],
            "start_date": start, "end_date": end,
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean",
            "timezone": "Europe/Amsterdam"
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        d = r.json()['daily']
        df = pd.DataFrame({
            'date':    pd.to_datetime(d['time']),
            'station': code,
            't_max':   d['temperature_2m_max'],
            't_min':   d['temperature_2m_min'],
            't_mean':  d['temperature_2m_mean'],
        })
        frames.append(df)
    return pd.concat(frames, ignore_index=True).sort_values(['date','station'])


@st.cache_data(ttl=3600, show_spinner=False)
def load_prices(start, end):
    """Scarica prezzi NG=F e XLE da yfinance — robusto per MultiIndex."""
    import yfinance as yf
    frames = []
    for ticker, name in [('NG=F', 'TTF_GAS'), ('XLE', 'ENERGY_EQ')]:
        try:
            df = yf.download(ticker, start=start, end=end,
                             auto_adjust=True, progress=False)
            if df.empty:
                continue
            # Gestisci MultiIndex (yfinance >= 0.2.x restituisce colonne multilivello)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            if 'Close' in df.columns:
                df = df[['Close']].copy()
                df.columns = ['close']
            elif 'close' in df.columns:
                df = df[['close']].copy()
            else:
                continue
            df.index.name = 'date'
            df = df.reset_index()
            df['ticker'] = name
            df['date'] = pd.to_datetime(df['date'])
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df = df.dropna(subset=['close'])
            frames.append(df)
        except Exception:
            continue
    if not frames:
        return pd.DataFrame(columns=['date','close','ticker','ret_1d'])
    prices = pd.concat(frames, ignore_index=True).sort_values(['ticker','date'])
    prices['ret_1d'] = prices.groupby('ticker')['close'].transform(
        lambda x: np.log(x / x.shift(1))
    )
    return prices


def compute_baseline(weather_df, years=20, smooth=15):
    df = weather_df.copy()
    df['day_of_year'] = df['date'].dt.dayofyear
    df['year'] = df['date'].dt.year
    cutoff = df['year'].max() - years
    base_df = df[df['year'] > cutoff].copy()
    grp = base_df.groupby(['station','day_of_year'])['t_mean']
    bl = grp.agg(t_baseline='mean', t_std='std').reset_index()
    smoothed = []
    for station in bl['station'].unique():
        sub = bl[bl['station']==station].copy().sort_values('day_of_year')
        sub['t_baseline'] = sub['t_baseline'].rolling(smooth, center=True, min_periods=5).mean().fillna(sub['t_baseline'])
        sub['t_std']      = sub['t_std'].rolling(smooth, center=True, min_periods=5).mean().fillna(sub['t_std'])
        smoothed.append(sub)
    bl = pd.concat(smoothed).reset_index(drop=True)
    bl['hdd_baseline'] = np.maximum(0, HDD_BASE - bl['t_baseline'])
    bl['cdd_baseline'] = np.maximum(0, bl['t_baseline'] - CDD_BASE)
    return bl


def compute_features(weather_df, baseline_df):
    df = weather_df.copy()
    df['day_of_year'] = df['date'].dt.dayofyear
    df['hdd_obs'] = np.maximum(0, HDD_BASE - df['t_mean'])
    df['cdd_obs'] = np.maximum(0, df['t_mean'] - CDD_BASE)
    df = df.merge(baseline_df[['station','day_of_year','t_baseline','t_std','hdd_baseline','cdd_baseline']],
                  on=['station','day_of_year'], how='left')
    df['t_anomaly']   = df['t_mean'] - df['t_baseline']
    df['hdd_anomaly'] = df['hdd_obs'] - df['hdd_baseline']
    df['cdd_anomaly'] = df['cdd_obs'] - df['cdd_baseline']
    df['weight'] = df['station'].map({k: v['weight'] for k,v in STATIONS.items()})
    composite = df.groupby('date').apply(lambda g: pd.Series({
        'hdd_composite':    (g['hdd_obs']     * g['weight']).sum(),
        'cdd_composite':    (g['cdd_obs']     * g['weight']).sum(),
        'hdd_anomaly_comp': (g['hdd_anomaly'] * g['weight']).sum(),
        'cdd_anomaly_comp': (g['cdd_anomaly'] * g['weight']).sum(),
        't_anomaly_comp':   (g['t_anomaly']   * g['weight']).sum(),
    })).reset_index()
    composite = composite.sort_values('date').reset_index(drop=True)

    def rzscore(s, w=ZSCORE_WIN):
        mu = s.rolling(w, min_periods=60).mean()
        sd = s.rolling(w, min_periods=60).std()
        return (s - mu) / sd.replace(0, np.nan)

    composite['z_hdd'] = rzscore(composite['hdd_anomaly_comp'])
    composite['z_cdd'] = rzscore(composite['cdd_anomaly_comp'])
    composite['cold_wave'] = (composite['z_hdd'].rolling(3, min_periods=3).sum().ge(6)).astype(int)
    composite['warm_wave'] = (composite['z_cdd'].rolling(3, min_periods=3).sum().ge(6)).astype(int)
    composite['season'] = np.where(composite['date'].dt.month.isin([10,11,12,1,2,3,4]), 'winter', 'summer')
    return composite


def compute_wei(feat_df):
    df = feat_df.copy()
    wei_w = df['z_hdd'] * 0.80 + df['cold_wave'] * 0.20
    wei_s = df['z_cdd'] * 0.80 + df['warm_wave'] * 0.20
    df['WEI'] = np.where(df['season']=='winter', wei_w, wei_s)
    df['WEI_smooth'] = df['WEI'].rolling(3, min_periods=2).mean()

    def classify(v):
        if v > THR_LONG  * 1.5: return 'STRONG_LONG'
        if v > THR_LONG:         return 'LONG'
        if v < THR_SHORT * 1.5: return 'STRONG_SHORT'
        if v < THR_SHORT:        return 'SHORT'
        return 'NEUTRAL'

    df['signal_class'] = df['WEI_smooth'].apply(classify)
    return df


def generate_signal(feat_df, min_dur=2):
    df = feat_df[['date','WEI_smooth','season']].dropna().copy().sort_values('date').reset_index(drop=True)
    signals, days_a, days_b, cur = [], 0, 0, 0
    for _, row in df.iterrows():
        w = row['WEI_smooth']
        if w > THR_LONG:   days_a += 1; days_b = 0
        elif w < THR_SHORT: days_b += 1; days_a = 0
        else:               days_a = 0;  days_b = 0; cur = 0
        if days_a >= min_dur: cur = 1
        elif days_b >= min_dur: cur = -1
        signals.append(cur)
    df['signal'] = signals
    return df


def run_backtest(sig_df, prices_df, ticker='TTF_GAS', horizons=[3,5,10,15]):
    price_piv = prices_df[prices_df['ticker']==ticker][['date','close']].set_index('date').sort_index()
    df = sig_df[['date','signal','WEI_smooth','season']].merge(
        price_piv.rename(columns={'close':'price_t'}), on='date', how='inner'
    ).sort_values('date').reset_index(drop=True)

    results = {}
    for H in horizons:
        df[f'fwd_{H}'] = np.log(df['price_t'].shift(-H) / df['price_t'].shift(-1))
        mask_l = (df['signal']==1)  & df[f'fwd_{H}'].notna()
        mask_s = (df['signal']==-1) & df[f'fwd_{H}'].notna()
        mask_a = (df['signal']!=0)  & df[f'fwd_{H}'].notna()
        sr = df.loc[mask_a, f'fwd_{H}'] * df.loc[mask_a, 'signal']
        lr = df.loc[mask_l, f'fwd_{H}']
        sr2= df.loc[mask_s, f'fwd_{H}']
        t, p = (stats.ttest_1samp(sr.dropna(), 0) if len(sr)>5 else (np.nan, np.nan))
        results[H] = {
            'n_long': mask_l.sum(), 'hr_long': (lr>0).mean() if len(lr) else np.nan,
            'avg_long': lr.mean() if len(lr) else np.nan,
            'n_short': mask_s.sum(), 'hr_short': (sr2<0).mean() if len(sr2) else np.nan,
            'avg_short': sr2.mean() if len(sr2) else np.nan,
            't': t, 'p': p, 'sig': p < 0.10 if not np.isnan(p) else False,
        }
    return results, df


def compute_portfolio(sig_df, prices_df, ticker='TTF_GAS', tc=0.0005):
    pdf = prices_df[prices_df['ticker']==ticker][['date','close','ret_1d']].sort_values('date')
    df  = sig_df[['date','signal']].merge(pdf, on='date', how='inner').sort_values('date').reset_index(drop=True)
    df['sig_lag']  = df['signal'].shift(1).fillna(0)
    df['trade']    = df['sig_lag'].diff().abs() > 0
    df['port_ret'] = df['sig_lag'] * df['ret_1d'] - df['trade'] * tc
    df['equity']   = 100 * np.exp(df['port_ret'].cumsum())
    df['equity_bh']= 100 * np.exp(df['ret_1d'].cumsum())
    rets = df['port_ret'].dropna()
    n_y  = len(rets)/252
    tot  = df['equity'].iloc[-1]/100-1 if len(df)>0 else 0
    ann  = (1+tot)**(1/n_y)-1 if (n_y>0 and tot>-1) else np.nan
    vol  = rets.std()*np.sqrt(252) if len(rets)>1 else np.nan
    sharpe  = ann/vol if (vol is not None and not np.isnan(vol) and vol>0 and not np.isnan(ann)) else np.nan
    dwnvol  = rets[rets<0].std()*np.sqrt(252) if len(rets[rets<0])>1 else np.nan
    sortino = ann/dwnvol if (dwnvol is not None and not np.isnan(dwnvol) and dwnvol>0 and not np.isnan(ann)) else np.nan
    rmax    = df['equity'].cummax()
    dd      = (df['equity']-rmax)/rmax
    max_dd  = dd.min()
    calmar  = ann/abs(max_dd) if max_dd!=0 else np.nan
    act_r   = df.loc[df['sig_lag']!=0,'port_ret'].dropna()
    bh_tot  = df['equity_bh'].iloc[-1]/100-1
    bh_ann  = (1+bh_tot)**(1/n_y)-1 if n_y>0 else np.nan
    bh_vol  = df['ret_1d'].std()*np.sqrt(252)
    bh_sh   = bh_ann/bh_vol if bh_vol>0 else np.nan
    return {
        'df': df, 'ann_ret': ann, 'ann_vol': vol, 'sharpe': sharpe,
        'sortino': sortino, 'max_dd': max_dd, 'calmar': calmar,
        'win_rate': (act_r>0).mean(), 'n_trades': df['trade'].sum(),
        'bh_ann': bh_ann, 'bh_sharpe': bh_sh, 'n_years': n_y,
    }


# ─────────────────────────────────────────────────────────────
# LOAD DATA — con spinner
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def build_all():
    weather  = load_weather(START_DATE, END_DATE)
    baseline = compute_baseline(weather)
    features = compute_features(weather, baseline)
    features = compute_wei(features)
    sig_df   = generate_signal(features)
    prices   = load_prices(START_DATE, END_DATE)
    bt_res, bt_df = run_backtest(sig_df, prices)
    perf     = compute_portfolio(sig_df, prices)
    return {
        'weather': weather, 'features': features,
        'sig_df': sig_df, 'prices': prices,
        'bt_res': bt_res, 'bt_df': bt_df, 'perf': perf,
    }


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 1.5rem 0;'>
        <div style='font-family:Syne,sans-serif; font-size:1.1rem; font-weight:800;
                    color:#e8edf5; letter-spacing:-0.02em;'>
            🌡️ Weather Energy
        </div>
        <div style='font-family:JetBrains Mono,monospace; font-size:0.65rem;
                    color:#4a5a75; margin-top:4px; text-transform:uppercase;
                    letter-spacing:0.1em;'>
            Alternative Data Signal
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigazione",
        ["📡  Signal Dashboard", "🌡️  Weather Analysis",
         "📈  Backtest", "📖  Metodologia", "📤  Export"],
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border-color:#1e2d47; margin:1.5rem 0;'>", unsafe_allow_html=True)

    # Controlli
    st.markdown("<div style='font-size:0.65rem; color:#4a5a75; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;'>Periodo analisi</div>", unsafe_allow_html=True)
    start_y = st.selectbox("Anno inizio", [2015,2016,2017,2018,2019,2020], index=0, label_visibility="collapsed")
    START_DATE_SEL = f"{start_y}-01-01"

    st.markdown("<div style='font-size:0.65rem; color:#4a5a75; text-transform:uppercase; letter-spacing:0.1em; margin-top:0.8rem; margin-bottom:0.5rem;'>Asset target</div>", unsafe_allow_html=True)
    asset = st.selectbox("Asset", ["TTF_GAS (NG=F proxy)", "ENERGY_EQ (XLE)"], label_visibility="collapsed")
    ticker_sel = "TTF_GAS" if "TTF" in asset else "ENERGY_EQ"

    st.markdown("<hr style='border-color:#1e2d47; margin:1.5rem 0;'>", unsafe_allow_html=True)

    if st.button("🔄 Aggiorna dati", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown(f"""
    <div style='font-family:JetBrains Mono,monospace; font-size:0.62rem; color:#4a5a75; margin-top:1rem;'>
        Ultimo aggiornamento<br>
        <span style='color:#8a9ab5;'>{datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# CARICAMENTO DATI
# ─────────────────────────────────────────────────────────────
with st.spinner("⚙️  Caricamento dati in corso..."):
    try:
        DATA = build_all()
        data_ok = True
    except Exception as e:
        data_ok = False
        err_msg = str(e)

if not data_ok:
    st.error(f"Errore nel caricamento dati: {err_msg}")
    st.info("Verifica la connessione internet e che yfinance sia installato.")
    st.stop()

feat   = DATA['features']
sig_df = DATA['sig_df']
prices = DATA['prices']
bt_res = DATA['bt_res']
bt_df  = DATA['bt_df']
perf   = DATA['perf']

latest = feat.dropna(subset=['WEI_smooth']).iloc[-1]
latest_sig = sig_df[sig_df['date'] == sig_df['date'].max()].iloc[-1] if len(sig_df) > 0 else None

def signal_color(s):
    if 'LONG' in str(s):  return '#10b981'
    if 'SHORT' in str(s): return '#ef4444'
    return '#8a9ab5'

def badge_class(s):
    if 'LONG' in str(s):  return 'badge-long'
    if 'SHORT' in str(s): return 'badge-short'
    return 'badge-neutral'

curr_signal = latest.get('signal_class', 'NEUTRAL')
curr_wei    = latest.get('WEI_smooth', 0)
curr_hdd    = latest.get('hdd_anomaly_comp', 0)
curr_season = latest.get('season', 'winter')
curr_date   = pd.to_datetime(latest.get('date')).strftime('%d %b %Y') if 'date' in latest else ''


# ═══════════════════════════════════════════════════════════════
# PAGE 1 — SIGNAL DASHBOARD
# ═══════════════════════════════════════════════════════════════
if "Signal Dashboard" in page:

    # Top bar
    st.markdown(f"""
    <div class='top-bar'>
        <div class='top-bar-title'>Weather Energy Signal</div>
        <div class='top-bar-meta'>
            <span class='dot-live'></span>LIVE &nbsp;|&nbsp;
            Ultimo dato: {curr_date} &nbsp;|&nbsp;
            Stagione: {curr_season.upper()}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Segnale principale ──────────────────────────────────────
    col_sig, col_kpi = st.columns([1, 3])

    with col_sig:
        st.markdown(f"""
        <div class='kpi-card' style='text-align:center; padding:2rem 1rem;'>
            <div class='kpi-label'>Segnale attivo</div>
            <div style='margin:1rem 0;'>
                <span class='signal-badge {badge_class(curr_signal)}'>{curr_signal.replace('_',' ')}</span>
            </div>
            <div class='kpi-label' style='margin-top:1.2rem;'>Asset target</div>
            <div style='font-family:Syne,sans-serif; font-size:1rem; font-weight:700;
                        color:#3b82f6; margin-top:0.3rem;'>
                Natural Gas (NG=F)
            </div>
            <div style='font-family:JetBrains Mono,monospace; font-size:0.68rem;
                        color:#4a5a75; margin-top:0.5rem;'>
                proxy TTF Gas Europa
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_kpi:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>Weather Energy Index</div>
                <div class='kpi-value' style='color:{signal_color(curr_signal)};'>
                    {curr_wei:+.2f}
                </div>
                <div class='kpi-sub'>z-score (soglia ±1.0)</div>
            </div>""", unsafe_allow_html=True)
        with k2:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>HDD Anomaly oggi</div>
                <div class='kpi-value' style='color:{"#10b981" if curr_hdd>0 else "#ef4444"};'>
                    {curr_hdd:+.2f}
                </div>
                <div class='kpi-sub'>vs baseline 20Y (°C·giorni)</div>
            </div>""", unsafe_allow_html=True)
        with k3:
            sr = perf['sharpe']
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>Sharpe Ratio (backtest)</div>
                <div class='kpi-value' style='color:{"#10b981" if sr>0 else "#ef4444"};'>
                    {sr:.2f}
                </div>
                <div class='kpi-sub'>vs B&H: {perf['bh_sharpe']:.2f}</div>
            </div>""", unsafe_allow_html=True)
        with k4:
            hr = bt_res[5]['hr_long'] if 5 in bt_res else np.nan
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>Hit Rate LONG a 5gg</div>
                <div class='kpi-value' style='color:{"#10b981" if hr>0.5 else "#ef4444"};'>
                    {hr:.1%}
                </div>
                <div class='kpi-sub'>p-val: {bt_res[5]['p']:.3f} {"✅" if bt_res[5]['sig'] else "⚠️"}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>WEI — ULTIMI 90 GIORNI</div>", unsafe_allow_html=True)

    # ── Mini chart WEI recente ──────────────────────────────────
    recent = feat.dropna(subset=['WEI_smooth']).tail(90)

    fig_mini = go.Figure()
    fig_mini.add_hrect(y0=THR_LONG, y1=10,  fillcolor='rgba(16,185,129,0.05)', line_width=0)
    fig_mini.add_hrect(y0=-10, y1=THR_SHORT, fillcolor='rgba(239,68,68,0.05)',  line_width=0)
    fig_mini.add_hline(y=THR_LONG,  line=dict(color='#10b981', dash='dash', width=1))
    fig_mini.add_hline(y=THR_SHORT, line=dict(color='#ef4444', dash='dash', width=1))
    fig_mini.add_hline(y=0, line=dict(color='#4a5a75', width=0.5))
    fig_mini.add_scatter(
        x=recent['date'], y=recent['WEI_smooth'],
        mode='lines', line=dict(color='#3b82f6', width=2),
        fill='tozeroy',
        fillcolor='rgba(59,130,246,0.08)',
        name='WEI'
    )
    # Evidenzia zona LONG
    long_mask = recent['WEI_smooth'] > THR_LONG
    fig_mini.add_scatter(
        x=recent.loc[long_mask,'date'], y=recent.loc[long_mask,'WEI_smooth'],
        mode='markers', marker=dict(color='#10b981', size=5, symbol='circle'),
        name='LONG zone'
    )
    fig_mini.update_layout(**PLOTLY_DARK, height=200,
        yaxis_title='WEI', showlegend=False,
        title=dict(text='', font=dict(size=11)))
    st.plotly_chart(fig_mini, use_container_width=True)

    # ── Tabella ultimi 30 giorni ────────────────────────────────
    st.markdown("<div class='section-header'>LOG SEGNALI — ULTIMI 30 GIORNI</div>", unsafe_allow_html=True)

    last30 = feat[['date','WEI_smooth','hdd_anomaly_comp','signal_class','season','cold_wave']].tail(30).copy()
    last30 = last30.merge(sig_df[['date','signal']], on='date', how='left')
    last30['date'] = last30['date'].dt.strftime('%Y-%m-%d')
    last30['WEI_smooth'] = last30['WEI_smooth'].round(3)
    last30['hdd_anomaly_comp'] = last30['hdd_anomaly_comp'].round(2)
    last30 = last30.rename(columns={
        'date':'Data', 'WEI_smooth':'WEI', 'hdd_anomaly_comp':'HDD Anomaly',
        'signal_class':'Classe segnale', 'signal':'Segnale num',
        'season':'Stagione', 'cold_wave':'Cold Wave'
    })
    st.dataframe(
        last30.iloc[::-1].reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
        height=350,
    )

    st.markdown("""
    <div class='disclaimer'>
        ⚠️ Disclaimer: questo sistema è uno strumento di supporto alla ricerca e al risk monitoring.
        Non costituisce consulenza in materia di investimenti ai sensi della normativa MiFID II.
        I segnali non garantiscono rendimenti futuri. Performance passate non sono indicative di risultati futuri.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE 2 — WEATHER ANALYSIS
# ═══════════════════════════════════════════════════════════════
elif "Weather Analysis" in page:

    st.markdown("<h2 style='margin-bottom:0.3rem;'>Weather Analysis</h2>", unsafe_allow_html=True)
    st.markdown("<div style='font-family:JetBrains Mono,monospace; font-size:0.75rem; color:#4a5a75; margin-bottom:1.5rem;'>Dati reali Open-Meteo — 6 stazioni Europa — 2015 → oggi</div>", unsafe_allow_html=True)

    # ── Grafico 1: WEI serie storica completa ──────────────────
    st.markdown("<div class='section-header'>WEATHER ENERGY INDEX — SERIE STORICA</div>", unsafe_allow_html=True)

    feat_plot = feat.dropna(subset=['WEI_smooth'])

    fig_wei = go.Figure()
    fig_wei.add_hrect(y0=THR_LONG, y1=feat_plot['WEI_smooth'].max()+1,
                      fillcolor='rgba(16,185,129,0.04)', line_width=0)
    fig_wei.add_hrect(y0=feat_plot['WEI_smooth'].min()-1, y1=THR_SHORT,
                      fillcolor='rgba(239,68,68,0.04)', line_width=0)
    fig_wei.add_hline(y=THR_LONG,  line=dict(color='#10b981', dash='dash', width=1),
                      annotation_text='Soglia LONG', annotation_font_color='#10b981',
                      annotation_font_size=10)
    fig_wei.add_hline(y=THR_SHORT, line=dict(color='#ef4444', dash='dash', width=1),
                      annotation_text='Soglia SHORT', annotation_font_color='#ef4444',
                      annotation_font_size=10)
    fig_wei.add_hline(y=0, line=dict(color='#4a5a75', width=0.5))
    fig_wei.add_scatter(x=feat_plot['date'], y=feat_plot['WEI_smooth'],
                        mode='lines', line=dict(color='#3b82f6', width=1.2),
                        name='WEI (3d smooth)', fill='tozeroy',
                        fillcolor='rgba(59,130,246,0.06)')

    # Evidenzia cold waves
    cw = feat_plot[feat_plot['cold_wave']==1]
    if len(cw):
        fig_wei.add_scatter(x=cw['date'], y=cw['WEI_smooth'],
                            mode='markers', marker=dict(color='#f59e0b', size=4),
                            name='Cold Wave', opacity=0.7)

    fig_wei.update_layout(**PLOTLY_DARK, height=320,
                          yaxis_title='WEI (z-score)',
                          title=dict(text=''))
    st.plotly_chart(fig_wei, use_container_width=True)

    # ── Grafici 2+3 in colonna ─────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("<div class='section-header'>STAGIONALITÀ HDD ANOMALY</div>", unsafe_allow_html=True)
        feat_plot2 = feat_plot.copy()
        feat_plot2['month'] = feat_plot2['date'].dt.month
        monthly = feat_plot2.groupby('month')['hdd_anomaly_comp'].agg(['mean','std'])
        months_it = ['Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic']

        fig_seas = go.Figure()
        colors = ['#10b981' if v >= 0 else '#ef4444' for v in monthly['mean']]
        fig_seas.add_bar(
            x=months_it, y=monthly['mean'],
            marker_color=colors, marker_opacity=0.8,
            error_y=dict(type='data', array=monthly['std'], color='#4a5a75', thickness=1.5),
            name='HDD Anomaly media'
        )
        fig_seas.add_hline(y=0, line=dict(color='#4a5a75', width=0.8))
        fig_seas.update_layout(**PLOTLY_DARK, height=280,
                               yaxis_title='HDD Anomaly (°C·giorni)',
                               showlegend=False,
                               title=dict(text=''))
        st.plotly_chart(fig_seas, use_container_width=True)

    with col_b:
        st.markdown("<div class='section-header'>DISTRIBUZIONE WEI</div>", unsafe_allow_html=True)
        wei_vals = feat_plot['WEI_smooth'].dropna()

        fig_dist = go.Figure()
        fig_dist.add_histogram(
            x=wei_vals, nbinsx=80,
            marker_color='#3b82f6', opacity=0.7,
            histnorm='probability density',
            name='WEI'
        )
        # Normal overlay
        x_n = np.linspace(wei_vals.min(), wei_vals.max(), 200)
        from scipy.stats import norm as sci_norm
        fig_dist.add_scatter(
            x=x_n, y=sci_norm.pdf(x_n, wei_vals.mean(), wei_vals.std()),
            mode='lines', line=dict(color='#f59e0b', width=2),
            name='Normale teorica'
        )
        fig_dist.add_vline(x=THR_LONG,  line=dict(color='#10b981', dash='dash', width=1.5))
        fig_dist.add_vline(x=THR_SHORT, line=dict(color='#ef4444', dash='dash', width=1.5))
        fig_dist.update_layout(**PLOTLY_DARK, height=280,
                               xaxis_title='WEI',
                               yaxis_title='Densità',
                               title=dict(text=''))
        st.plotly_chart(fig_dist, use_container_width=True)

    # ── Temperatura recente per stazione ───────────────────────
    st.markdown("<div class='section-header'>TEMPERATURE RECENTI PER STAZIONE — ULTIMI 30 GIORNI</div>", unsafe_allow_html=True)
    weather_rec = DATA['weather'].copy()
    weather_rec = weather_rec[weather_rec['date'] >= weather_rec['date'].max() - pd.Timedelta(days=30)]

    fig_temp = go.Figure()
    colors_st = ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6','#06b6d4']
    for i, (code, info) in enumerate(STATIONS.items()):
        sub = weather_rec[weather_rec['station']==code]
        fig_temp.add_scatter(
            x=sub['date'], y=sub['t_mean'],
            mode='lines', line=dict(color=colors_st[i], width=1.5),
            name=f"{code} – {info['name']}"
        )
    fig_temp.add_hline(y=HDD_BASE, line=dict(color='#4a5a75', dash='dot', width=1),
                       annotation_text='HDD base 15.5°C', annotation_font_size=9,
                       annotation_font_color='#4a5a75')
    fig_temp.update_layout(**PLOTLY_DARK, height=280,
                           yaxis_title='Temperatura (°C)',
                           title=dict(text=''))
    st.plotly_chart(fig_temp, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# PAGE 3 — BACKTEST
# ═══════════════════════════════════════════════════════════════
elif "Backtest" in page:

    st.markdown("<h2 style='margin-bottom:0.3rem;'>Backtest & Performance</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-family:JetBrains Mono,monospace; font-size:0.75rem; color:#4a5a75; margin-bottom:1.5rem;'>Asset: {ticker_sel} | Periodo: {START_DATE} → {END_DATE} | TC: 5 bps per trade</div>", unsafe_allow_html=True)

    # ── KPI performance ────────────────────────────────────────
    k1,k2,k3,k4,k5 = st.columns(5)
    metrics = [
        ("Return Ann.", f"{perf['ann_ret']*100:.1f}%", f"B&H: {perf['bh_ann']*100:.1f}%", perf['ann_ret']>0),
        ("Sharpe Ratio", f"{perf['sharpe']:.2f}", f"B&H: {perf['bh_sharpe']:.2f}", perf['sharpe']>0),
        ("Sortino Ratio", f"{perf['sortino']:.2f}", "", perf['sortino']>0),
        ("Max Drawdown", f"{perf['max_dd']*100:.1f}%", "", perf['max_dd']>-0.3),
        ("Win Rate", f"{perf['win_rate']*100:.1f}%", f"N trade: {int(perf['n_trades'])}", perf['win_rate']>0.5),
    ]
    for col, (label, val, sub, pos) in zip([k1,k2,k3,k4,k5], metrics):
        with col:
            color = '#10b981' if pos else '#ef4444'
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>{label}</div>
                <div class='kpi-value' style='color:{color}; font-size:1.6rem;'>{val}</div>
                <div class='kpi-sub'>{sub}</div>
            </div>""", unsafe_allow_html=True)

    # ── Equity curve ───────────────────────────────────────────
    st.markdown("<div class='section-header'>EQUITY CURVE — SEGNALE WEI vs BUY & HOLD</div>", unsafe_allow_html=True)
    perf_df = perf['df'].dropna(subset=['equity'])

    fig_eq = go.Figure()
    fig_eq.add_scatter(x=perf_df['date'], y=perf_df['equity_bh'],
                       mode='lines', line=dict(color='#4a5a75', width=1.2, dash='dash'),
                       name='Buy & Hold', opacity=0.7)
    fig_eq.add_scatter(x=perf_df['date'], y=perf_df['equity'],
                       mode='lines', line=dict(color='#3b82f6', width=2),
                       name='WEI Signal', fill='tonexty',
                       fillcolor='rgba(59,130,246,0.06)')
    fig_eq.add_hline(y=100, line=dict(color='#4a5a75', width=0.5))
    fig_eq.update_layout(**PLOTLY_DARK, height=320,
                         yaxis_title='Valore portafoglio (base 100)',
                         title=dict(text=''))
    st.plotly_chart(fig_eq, use_container_width=True)

    col_dd, col_hr = st.columns(2)

    with col_dd:
        st.markdown("<div class='section-header'>DRAWDOWN</div>", unsafe_allow_html=True)
        rmax = perf_df['equity'].cummax()
        dd   = (perf_df['equity'] - rmax) / rmax * 100
        fig_dd = go.Figure()
        fig_dd.add_scatter(x=perf_df['date'], y=dd,
                           mode='lines', line=dict(color='#ef4444', width=1),
                           fill='tozeroy', fillcolor='rgba(239,68,68,0.15)',
                           name='Drawdown')
        fig_dd.add_hline(y=0, line=dict(color='#4a5a75', width=0.5))
        fig_dd.update_layout(**PLOTLY_DARK, height=240,
                             yaxis_title='Drawdown (%)',
                             title=dict(text=f'Max DD: {perf["max_dd"]*100:.1f}%'))
        st.plotly_chart(fig_dd, use_container_width=True)

    with col_hr:
        st.markdown("<div class='section-header'>HIT RATE PER ORIZZONTE</div>", unsafe_allow_html=True)
        horizons_list = list(bt_res.keys())
        hr_l = [bt_res[h]['hr_long']  for h in horizons_list]
        hr_s = [bt_res[h]['hr_short'] for h in horizons_list]
        fig_hr = go.Figure()
        fig_hr.add_bar(x=[f'H={h}gg' for h in horizons_list], y=[v*100 for v in hr_l],
                       name='LONG', marker_color='#10b981', opacity=0.8)
        fig_hr.add_bar(x=[f'H={h}gg' for h in horizons_list], y=[v*100 for v in hr_s],
                       name='SHORT', marker_color='#ef4444', opacity=0.8)
        fig_hr.add_hline(y=50, line=dict(color='#4a5a75', dash='dash', width=1),
                         annotation_text='50% (random)', annotation_font_size=9,
                         annotation_font_color='#4a5a75')
        fig_hr.update_layout(**PLOTLY_DARK, height=240, barmode='group',
                             yaxis_title='Hit Rate (%)',
                             yaxis_range=[30,75],
                             title=dict(text=''))
        st.plotly_chart(fig_hr, use_container_width=True)

    # ── Tabella metriche per orizzonte ─────────────────────────
    st.markdown("<div class='section-header'>METRICHE DETTAGLIO PER ORIZZONTE</div>", unsafe_allow_html=True)
    rows = []
    for H, m in bt_res.items():
        rows.append({
            'H (giorni)': H,
            'N LONG': m['n_long'],
            'Hit Rate LONG': f"{m['hr_long']:.1%}",
            'Avg Return LONG': f"{m['avg_long']*100:.2f}%",
            'N SHORT': m['n_short'],
            'Hit Rate SHORT': f"{m['hr_short']:.1%}",
            'T-statistic': f"{m['t']:.2f}",
            'P-value': f"{m['p']:.3f}",
            'Significativo': '✅' if m['sig'] else '⚠️',
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("""
    <div class='disclaimer'>
        Il backtest è calcolato as-of: il segnale del giorno T usa solo dati disponibili fino a T.
        Transaction cost: 5 bps per trade. Nessuna leva. Orizzonte: long/short flat (1x).
        I risultati si riferiscono a NG=F (Natural Gas Futures NYMEX) come proxy del TTF europeo.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE 4 — METODOLOGIA
# ═══════════════════════════════════════════════════════════════
elif "Metodologia" in page:

    st.markdown("<h2 style='margin-bottom:0.3rem;'>Metodologia</h2>", unsafe_allow_html=True)
    st.markdown("<div style='font-family:JetBrains Mono,monospace; font-size:0.75rem; color:#4a5a75; margin-bottom:1.5rem;'>Documentazione tecnica del modello — versione 1.0</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='chain-box'>
        Temperatura anomala (6 stazioni Europa)
        &nbsp;→&nbsp; HDD/CDD deviation dal baseline 20Y
        &nbsp;→&nbsp; Weather Energy Index (z-score rolling)
        &nbsp;→&nbsp; Segnale LONG / SHORT / NEUTRAL
        &nbsp;→&nbsp; Posizione su Natural Gas Futures
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class='method-card'>
            <h4>📡 Fonte dati meteo</h4>
            <p>
            Open-Meteo Historical Weather API (gratuita, nessuna API key).
            Dati giornalieri: T_max, T_min, T_mean per 6 stazioni europee.
            Storico disponibile dal 1940, aggiornamento giornaliero.
            Nessun dato proprietario — tutto verificabile pubblicamente.
            </p>
        </div>
        <div class='method-card'>
            <h4>🌡️ HDD e CDD</h4>
            <p>
            <b>HDD</b> (Heating Degree Days) = max(0, 15.5°C − T_mean).
            Misura il "freddo accumulato" rispetto alla soglia di neutralità termica europea.
            Ogni HDD corrisponde a domanda riscaldamento incremetale.<br><br>
            <b>CDD</b> (Cooling Degree Days) = max(0, T_mean − 22°C).
            Driver estivo della domanda di energia elettrica per raffreddamento.
            </p>
        </div>
        <div class='method-card'>
            <h4>📐 Baseline climatologico</h4>
            <p>
            Per ogni stazione e ogni giorno dell'anno, viene calcolata la temperatura
            media degli ultimi 20 anni. Smoothing a 15 giorni per evitare discontinuità.
            L'anomalia è la deviazione rispetto a questo baseline:
            positiva = più freddo del normale, negativa = più caldo del normale.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='method-card'>
            <h4>📊 Weather Energy Index (WEI)</h4>
            <p>
            Indice composito che combina le 6 stazioni con pesi geografici
            (Germania 25%, Amsterdam 20%, Parigi 20%, Milano 15%, Londra 10%, Varsavia 10%).
            I pesi riflettono il peso di ciascun paese nel consumo gas europeo.<br><br>
            Formula (inverno): WEI = z_HDD_anomaly × 0.80 + cold_wave_flag × 0.20<br>
            Formula (estate):  WEI = z_CDD_anomaly × 0.80 + warm_wave_flag × 0.20<br><br>
            Lo z-score rolling (finestra 365 giorni) rende il WEI confrontabile
            tra stagioni diverse e anni diversi.
            </p>
        </div>
        <div class='method-card'>
            <h4>🎯 Generazione segnale</h4>
            <p>
            <b>LONG</b>: WEI > +1.0 per almeno 2 giorni consecutivi<br>
            <b>SHORT</b>: WEI < -1.0 per almeno 2 giorni consecutivi<br>
            <b>NEUTRAL</b>: altrimenti<br><br>
            Il filtro a 2 giorni consecutivi evita reazioni a spike isolati di un giorno
            che spesso sono rumore meteorologico, non anomalie strutturali.
            </p>
        </div>
        <div class='method-card'>
            <h4>⚖️ Backtest as-of</h4>
            <p>
            Il segnale del giorno T usa SOLO dati disponibili fino a T — nessun look-ahead.
            Il trade entra al close di T+1 (si vede il segnale la sera, si esegue il giorno
            dopo). Il forward return è calcolato al close di T+H per H = 3, 5, 10, 15 giorni.
            Transaction cost: 5 basis points per trade.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ── Tabella stazioni ───────────────────────────────────────
    st.markdown("<div class='section-header'>STAZIONI DI MONITORAGGIO</div>", unsafe_allow_html=True)
    st_data = pd.DataFrame([
        {'Codice': k, 'Città': v['name'], 'Lat': v['lat'],
         'Lon': v['lon'], 'Peso': f"{v['weight']*100:.0f}%"}
        for k, v in STATIONS.items()
    ])
    st.dataframe(st_data, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class='disclaimer'>
        ⚠️ Posizionamento commerciale: questo sistema è uno strumento di "economic intelligence
        interpretabile" — non un servizio di consulenza in materia di investimenti ai sensi di
        MiFID II. I segnali non costituiscono raccomandazioni personalizzate. Il sistema misura
        anomalie fisiche e le traduce in indicatori quantitativi verificabili.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE 5 — EXPORT
# ═══════════════════════════════════════════════════════════════
elif "Export" in page:

    st.markdown("<h2 style='margin-bottom:0.3rem;'>Export</h2>", unsafe_allow_html=True)
    st.markdown("<div style='font-family:JetBrains Mono,monospace; font-size:0.75rem; color:#4a5a75; margin-bottom:1.5rem;'>Esporta i dati e i risultati in formato Excel o CSV</div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("<div class='section-header'>EXPORT EXCEL — REPORT COMPLETO</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='method-card'>
            <h4>📊 Contenuto del report Excel</h4>
            <p>
            • Foglio 1: Segnali giornalieri (WEI, HDD, segnale, classe)<br>
            • Foglio 2: Performance backtest per orizzonte<br>
            • Foglio 3: Equity curve vs Buy & Hold<br>
            • Foglio 4: Dati meteo grezzi (temperature stazioni)<br>
            • Foglio 5: Riepilogo metodologia
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Costruisci Excel in memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:

            # Foglio 1: Segnali
            signals_export = feat[['date','WEI','WEI_smooth','hdd_composite',
                                   'hdd_anomaly_comp','z_hdd','signal_class',
                                   'season','cold_wave']].copy()
            signals_export = signals_export.merge(
                sig_df[['date','signal']], on='date', how='left'
            )
            signals_export['date'] = signals_export['date'].dt.strftime('%Y-%m-%d')
            signals_export.to_excel(writer, sheet_name='Segnali WEI', index=False)

            # Foglio 2: Backtest metriche
            bt_rows = []
            for H, m in bt_res.items():
                bt_rows.append({
                    'Orizzonte (giorni)': H,
                    'N LONG': m['n_long'], 'Hit Rate LONG': m['hr_long'],
                    'Avg Return LONG': m['avg_long'],
                    'N SHORT': m['n_short'], 'Hit Rate SHORT': m['hr_short'],
                    'Avg Return SHORT': m['avg_short'],
                    'T-statistic': m['t'], 'P-value': m['p'],
                    'Significativo (p<10%)': m['sig'],
                })
            pd.DataFrame(bt_rows).to_excel(writer, sheet_name='Backtest Metriche', index=False)

            # Foglio 3: Equity curve
            eq_export = perf['df'][['date','equity','equity_bh','port_ret','sig_lag']].copy()
            eq_export['date'] = eq_export['date'].dt.strftime('%Y-%m-%d')
            eq_export.to_excel(writer, sheet_name='Equity Curve', index=False)

            # Foglio 4: Prezzi
            prices_export = prices.copy()
            prices_export['date'] = prices_export['date'].dt.strftime('%Y-%m-%d')
            prices_export.to_excel(writer, sheet_name='Prezzi Asset', index=False)

            # Foglio 5: Sommario
            summary = pd.DataFrame([
                ['Sistema', 'Weather Energy Signal v1.0'],
                ['Data generazione', datetime.now().strftime('%Y-%m-%d %H:%M')],
                ['Periodo dati', f"{START_DATE} → {END_DATE}"],
                ['Asset target', 'NG=F (Natural Gas Futures NYMEX)'],
                ['Stazioni monitorate', ', '.join(STATIONS.keys())],
                ['Soglia LONG', f'WEI > {THR_LONG}'],
                ['Soglia SHORT', f'WEI < {THR_SHORT}'],
                ['Return annualizzato', f"{perf['ann_ret']*100:.1f}%"],
                ['Sharpe Ratio', f"{perf['sharpe']:.2f}"],
                ['Max Drawdown', f"{perf['max_dd']*100:.1f}%"],
                ['Hit Rate LONG a 5gg', f"{bt_res[5]['hr_long']:.1%}"],
                ['P-value a 5gg', f"{bt_res[5]['p']:.3f}"],
                ['Disclaimer', 'Strumento di supporto alla ricerca. Non costituisce consulenza MiFID II.'],
            ], columns=['Parametro', 'Valore'])
            summary.to_excel(writer, sheet_name='Sommario', index=False)

        output.seek(0)
        st.download_button(
            label="📥 Download Report Excel",
            data=output,
            file_name=f"WeatherEnergySignal_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with col_b:
        st.markdown("<div class='section-header'>EXPORT CSV — SEGNALI GIORNALIERI</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='method-card'>
            <h4>📄 Contenuto CSV</h4>
            <p>
            Tutti i segnali giornalieri in formato CSV leggero.<br>
            Utile per importare i dati in Excel, Bloomberg Terminal,
            o qualsiasi sistema di portfolio management.<br><br>
            Colonne: data, WEI, HDD_anomaly, segnale (-1/0/1),
            classe segnale, stagione.
            </p>
        </div>
        """, unsafe_allow_html=True)

        csv_export = feat[['date','WEI_smooth','hdd_anomaly_comp',
                           'signal_class','season']].copy()
        csv_export = csv_export.merge(sig_df[['date','signal']], on='date', how='left')
        csv_export['date'] = csv_export['date'].dt.strftime('%Y-%m-%d')
        csv_export.columns = ['date','WEI','HDD_anomaly','signal_class','season','signal_num']

        st.download_button(
            label="📥 Download CSV Segnali",
            data=csv_export.to_csv(index=False),
            file_name=f"WeatherSignals_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>ANTEPRIMA DATI</div>", unsafe_allow_html=True)
        st.dataframe(csv_export.tail(15).iloc[::-1].reset_index(drop=True),
                     use_container_width=True, hide_index=True, height=300)
