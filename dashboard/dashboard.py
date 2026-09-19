import streamlit as st
import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime
from collections import Counter

API_URL = st.secrets.get("API_URL", "your-api-url-here")

traffic_records = {
    "normal":  [0,1,2,0,491,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,1,0,0,150,25,0.17,0.03,0.17,0,0.05,0,0,0],
    "DoS":     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,511,511,1,1,0,0,1,0,0,255,255,1,0,1,0,1,1,0,0],
    "Probe":   [0,2,52,10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,0,1,229,229,1,0,0,0,0,0,0,0],
    "R2L":     [0,0,21,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,1,0,0,24,9,0.38,0,0.38,0,0,0,0,0],
    "U2R":     [0,0,21,0,0,0,0,0,0,1,0,1,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,0,0,1,1,1,0,1,0,0,0,0,0],
}

COLORS = {
    "normal":     "#00ff88",
    "DoS":        "#ff4444",
    "Probe":      "#ffaa00",
    "R2L":        "#ff00ff",
    "U2R":        "#ff0066",
    "Suspicious": "#ff8800",
}

st.set_page_config(
    page_title="CloudGuard IDS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #030712;
    color: #e2e8f0;
}

.stApp {
    background: radial-gradient(ellipse at 20% 20%, #0d1f3c 0%, #030712 50%, #0d0d1a 100%);
}

/* Hide streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {padding-top: 1rem; padding-bottom: 1rem;}

/* Hero header */
.hero-title {
    font-family: 'Orbitron', monospace;
    font-size: 3rem;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(135deg, #00d4ff, #0066ff, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin: 0;
    padding: 0.5rem 0;
    text-shadow: none;
}

.hero-sub {
    font-family: 'Share Tech Mono', monospace;
    text-align: center;
    color: #4a9eff;
    font-size: 0.85rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

.status-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 2rem;
    padding: 0.5rem;
    background: rgba(0, 212, 255, 0.05);
    border: 1px solid rgba(0, 212, 255, 0.15);
    border-radius: 4px;
    margin-bottom: 1rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: #4a9eff;
}

.status-dot {
    width: 8px;
    height: 8px;
    background: #00ff88;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(0,255,136,0.4); }
    70% { box-shadow: 0 0 0 8px rgba(0,255,136,0); }
    100% { box-shadow: 0 0 0 0 rgba(0,255,136,0); }
}

/* Traffic buttons */
.stButton > button {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    border-radius: 4px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    background: rgba(255,255,255,0.03) !important;
    color: #e2e8f0 !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.2s ease !important;
    letter-spacing: 1px !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: rgba(0,212,255,0.1) !important;
    border-color: #00d4ff !important;
    color: #00d4ff !important;
    transform: translateX(3px) !important;
}

/* Alert boxes */
.alert-critical {
    background: linear-gradient(135deg, rgba(255,30,30,0.15), rgba(255,0,100,0.08));
    border: 1px solid #ff4444;
    border-left: 4px solid #ff4444;
    border-radius: 6px;
    padding: 1.5rem;
    text-align: center;
    font-family: 'Orbitron', monospace;
    animation: alertpulse 1s infinite;
}

@keyframes alertpulse {
    0% { box-shadow: 0 0 0 0 rgba(255,68,68,0.3); }
    50% { box-shadow: 0 0 20px 4px rgba(255,68,68,0.15); }
    100% { box-shadow: 0 0 0 0 rgba(255,68,68,0.3); }
}

.alert-safe {
    background: linear-gradient(135deg, rgba(0,255,136,0.08), rgba(0,200,100,0.05));
    border: 1px solid #00ff88;
    border-left: 4px solid #00ff88;
    border-radius: 6px;
    padding: 1.5rem;
    text-align: center;
    font-family: 'Orbitron', monospace;
}

.alert-suspicious {
    background: linear-gradient(135deg, rgba(255,136,0,0.12), rgba(255,80,0,0.06));
    border: 1px solid #ff8800;
    border-left: 4px solid #ff8800;
    border-radius: 6px;
    padding: 1.5rem;
    text-align: center;
    font-family: 'Orbitron', monospace;
    animation: alertpulse 2s infinite;
}

.attack-type-large {
    font-size: 2.5rem;
    font-weight: 900;
    letter-spacing: 4px;
    margin: 0.3rem 0;
}

.confidence-bar-container {
    background: rgba(255,255,255,0.05);
    border-radius: 20px;
    height: 8px;
    margin: 0.5rem auto;
    max-width: 200px;
    overflow: hidden;
}

/* Metric cards */
.metric-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    font-family: 'Orbitron', monospace;
}

.metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1;
}

.metric-label {
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    opacity: 0.5;
    margin-top: 0.3rem;
    font-family: 'Share Tech Mono', monospace;
}

/* Section headers */
.section-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #4a9eff;
    border-bottom: 1px solid rgba(74,158,255,0.2);
    padding-bottom: 0.4rem;
    margin-bottom: 0.8rem;
}

/* Traffic log table */
.stDataFrame {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* Divider */
hr {
    border-color: rgba(255,255,255,0.06) !important;
    margin: 0.8rem 0 !important;
}

/* Progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg, #00d4ff, #7c3aed) !important;
}

/* Sidebar panel */
.control-panel {
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Session state init
for key, val in [('log', []), ('total', 0), ('alerts', 0), ('last_result', None), ('attack_counts', {})]:
    if key not in st.session_state:
        st.session_state[key] = val

def send_traffic(traffic_type):
    try:
        response = requests.post(API_URL, json={'features': traffic_records[traffic_type]}, timeout=10)
        result = response.json()
        result['sent'] = traffic_type
        result['time'] = datetime.now().strftime('%H:%M:%S')
        if result.get('prediction') == 'normal' and result.get('confidence', 1) < 0.60:
            result['alert'] = True
            result['prediction'] = 'Suspicious'
        st.session_state.last_result = result
        st.session_state.log.insert(0, result)
        st.session_state.total += 1
        if result.get('alert'):
            st.session_state.alerts += 1
            pred = result['prediction']
            st.session_state.attack_counts[pred] = st.session_state.attack_counts.get(pred, 0) + 1
    except Exception as e:
        st.session_state.last_result = {'error': str(e), 'sent': traffic_type, 'time': datetime.now().strftime('%H:%M:%S')}

# ── HERO SECTION ──────────────────────────────────────────────
st.markdown("<div class='hero-title'>CloudGuard</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-sub'>AI-Powered Intrusion Detection System · AWS Cloud · Real-Time</div>", unsafe_allow_html=True)

threat_level = "CRITICAL" if st.session_state.alerts > 3 else "ELEVATED" if st.session_state.alerts > 0 else "NOMINAL"
threat_color = "#ff4444" if threat_level == "CRITICAL" else "#ffaa00" if threat_level == "ELEVATED" else "#00ff88"

st.markdown(f"""
<div class='status-bar'>
    <span><span class='status-dot'></span>SYSTEM ONLINE</span>
    <span>AWS LAMBDA · ACTIVE</span>
    <span>API GATEWAY · CONNECTED</span>
    <span>SNS ALERTS · ARMED</span>
    <span style='color:{threat_color};font-weight:bold'>THREAT LEVEL: {threat_level}</span>
</div>
""", unsafe_allow_html=True)

# ── MAIN LAYOUT ───────────────────────────────────────────────
left, mid, right = st.columns([1, 1.4, 1.2])

# ── LEFT: CONTROL PANEL ──────────────────────────────────────
with left:
    st.markdown("<div class='section-header'>▸ Traffic Control</div>", unsafe_allow_html=True)

    with st.container():
        if st.button("✅  NORMAL TRAFFIC", use_container_width=True):
            send_traffic("normal")
            st.rerun()
        if st.button("💥  DoS ATTACK", use_container_width=True):
            send_traffic("DoS")
            st.rerun()
        if st.button("🔍  PROBE ATTACK", use_container_width=True):
            send_traffic("Probe")
            st.rerun()
        if st.button("🔓  R2L ATTACK", use_container_width=True):
            send_traffic("R2L")
            st.rerun()
        if st.button("☠️  U2R ATTACK", use_container_width=True):
            send_traffic("U2R")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>▸ Auto Simulation</div>", unsafe_allow_html=True)

    if st.button("⚡  SIMULATE 20 RECORDS", use_container_width=True):
        sequence = ["normal","DoS","normal","Probe","DoS","normal","R2L",
                    "DoS","normal","U2R","DoS","normal","DoS","normal",
                    "Probe","DoS","normal","R2L","normal","DoS"]
        bar = st.progress(0, text="Simulating traffic...")
        for i, t in enumerate(sequence):
            send_traffic(t)
            bar.progress((i+1)/len(sequence), text=f"Record {i+1}/20 — {t}")
            time.sleep(0.4)
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # System stats
    st.markdown("<div class='section-header'>▸ System Stats</div>", unsafe_allow_html=True)
    detection_rate = round((st.session_state.alerts / st.session_state.total * 100), 1) if st.session_state.total > 0 else 0

    st.markdown(f"""
    <div style='font-family:Share Tech Mono,monospace;font-size:0.75rem;line-height:2;color:#8892a4;'>
        <div style='display:flex;justify-content:space-between;'>
            <span>RECORDS ANALYZED</span>
            <span style='color:#e2e8f0'>{st.session_state.total}</span>
        </div>
        <div style='display:flex;justify-content:space-between;'>
            <span>THREATS DETECTED</span>
            <span style='color:#ff4444'>{st.session_state.alerts}</span>
        </div>
        <div style='display:flex;justify-content:space-between;'>
            <span>SAFE TRAFFIC</span>
            <span style='color:#00ff88'>{st.session_state.total - st.session_state.alerts}</span>
        </div>
        <div style='display:flex;justify-content:space-between;'>
            <span>DETECTION RATE</span>
            <span style='color:#ffaa00'>{detection_rate}%</span>
        </div>
        <div style='display:flex;justify-content:space-between;'>
            <span>MODEL</span>
            <span style='color:#4a9eff'>RANDOM FOREST</span>
        </div>
        <div style='display:flex;justify-content:space-between;'>
            <span>DATASET</span>
            <span style='color:#4a9eff'>NSL-KDD</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️  CLEAR ALL DATA", use_container_width=True):
        st.session_state.log = []
        st.session_state.total = 0
        st.session_state.alerts = 0
        st.session_state.last_result = None
        st.session_state.attack_counts = {}
        st.rerun()

# ── MIDDLE: DETECTION RESULT ──────────────────────────────────
with mid:
    st.markdown("<div class='section-header'>▸ Live Detection Result</div>", unsafe_allow_html=True)

    if st.session_state.last_result:
        r = st.session_state.last_result

        if 'error' in r:
            st.markdown(f"""
            <div class='alert-suspicious'>
                <div style='font-size:1rem;color:#ff8800'>⚠ CONNECTION ERROR</div>
                <div style='font-size:0.7rem;color:#888;margin-top:0.5rem;font-family:monospace'>{r['error']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            pred = r.get('prediction', 'unknown')
            conf = r.get('confidence', 0)
            alert = r.get('alert', False)
            sent = r.get('sent', '')
            color = COLORS.get(pred, '#888888')
            conf_pct = conf * 100

            if alert and pred != 'normal':
                box_class = 'alert-suspicious' if pred == 'Suspicious' else 'alert-critical'
                icon = "⚠" if pred == 'Suspicious' else "🚨"
                status_text = "SUSPICIOUS TRAFFIC FLAGGED" if pred == 'Suspicious' else "INTRUSION DETECTED"
                sub_text = "LOW CONFIDENCE — POSSIBLE EVASION ATTEMPT" if pred == 'Suspicious' else "EMAIL ALERT DISPATCHED VIA AWS SNS"
            else:
                box_class = 'alert-safe'
                icon = "✓"
                status_text = "TRAFFIC CLEARED"
                sub_text = "NO THREAT DETECTED"

            st.markdown(f"""
            <div class='{box_class}'>
                <div style='font-size:2rem;margin-bottom:0.3rem'>{icon}</div>
                <div style='font-size:0.7rem;letter-spacing:3px;color:#888;font-family:Share Tech Mono,monospace'>{status_text}</div>
                <div class='attack-type-large' style='color:{color}'>{pred.upper()}</div>
                <div style='font-size:0.7rem;letter-spacing:2px;color:#888;font-family:Share Tech Mono,monospace'>{sub_text}</div>
                <div style='margin-top:1rem;font-family:Share Tech Mono,monospace;font-size:0.75rem;color:#aaa'>
                    CONFIDENCE: <span style='color:{color}'>{conf_pct:.1f}%</span>
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    SENT: <span style='color:#4a9eff'>{sent.upper()}</span>
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    TIME: <span style='color:#4a9eff'>{r.get('time','')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='
            border: 1px dashed rgba(255,255,255,0.1);
            border-radius:8px;
            padding:3rem;
            text-align:center;
            font-family:Share Tech Mono,monospace;
        '>
            <div style='font-size:3rem;opacity:0.2'>🛡️</div>
            <div style='font-size:0.75rem;letter-spacing:3px;color:#444;margin-top:1rem'>
                AWAITING TRAFFIC INPUT
            </div>
            <div style='font-size:0.65rem;color:#333;margin-top:0.5rem'>
                SELECT TRAFFIC TYPE FROM CONTROL PANEL
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Attack distribution chart
    if st.session_state.attack_counts:
        st.markdown("<div class='section-header'>▸ Attack Distribution</div>", unsafe_allow_html=True)

        fig, ax = plt.subplots(figsize=(5, 2.5))
        fig.patch.set_facecolor('#0a0f1e')
        ax.set_facecolor('#0a0f1e')

        labels = list(st.session_state.attack_counts.keys())
        values = list(st.session_state.attack_counts.values())
        bar_colors = [COLORS.get(l, '#4a9eff') for l in labels]

        bars = ax.barh(labels, values, color=bar_colors, height=0.5, edgecolor='none')

        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                   str(val), va='center', color='#aaa',
                   fontsize=9, fontfamily='monospace')

        ax.set_xlim(0, max(values) * 1.3)
        ax.tick_params(colors='#555', labelsize=8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#1a2035')
        ax.spines['left'].set_color('#1a2035')
        for label in ax.get_yticklabels():
            label.set_color('#aaa')
            label.set_fontfamily('monospace')
        for label in ax.get_xticklabels():
            label.set_color('#555')
        ax.set_xlabel('Count', color='#444', fontsize=8)
        plt.tight_layout(pad=0.5)
        st.pyplot(fig, use_container_width=True)
        plt.close()

# ── RIGHT: TRAFFIC LOG ────────────────────────────────────────
with right:
    st.markdown("<div class='section-header'>▸ Traffic Log</div>", unsafe_allow_html=True)

    if st.session_state.log:
        for entry in st.session_state.log[:12]:
            if 'error' in entry:
                continue
            pred = entry.get('prediction', '?')
            conf = entry.get('confidence', 0)
            alert = entry.get('alert', False)
            sent = entry.get('sent', '')
            t = entry.get('time', '')
            color = COLORS.get(pred, '#888')
            icon = "🚨" if alert else "✅"

            st.markdown(f"""
            <div style='
                display:flex;
                justify-content:space-between;
                align-items:center;
                padding:0.4rem 0.6rem;
                margin-bottom:0.3rem;
                background:rgba(255,255,255,0.02);
                border-left:3px solid {color};
                border-radius:0 4px 4px 0;
                font-family:Share Tech Mono,monospace;
                font-size:0.72rem;
            '>
                <span style='color:#555'>{t}</span>
                <span style='color:#666'>{sent[:5]}</span>
                <span style='color:{color};font-weight:bold'>{pred[:10]}</span>
                <span style='color:#555'>{conf*100:.0f}%</span>
                <span>{icon}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align:center;padding:2rem;font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#333;letter-spacing:2px'>
            NO RECORDS YET
        </div>
        """, unsafe_allow_html=True)

    # Confidence timeline chart
    if len(st.session_state.log) >= 3:
        st.markdown("<br><div class='section-header'>▸ Confidence Timeline</div>", unsafe_allow_html=True)

        recent = [e for e in reversed(st.session_state.log[-15:]) if 'error' not in e]
        if recent:
            confs = [e.get('confidence', 0) * 100 for e in recent]
            colors_line = [COLORS.get(e.get('prediction','normal'), '#888') for e in recent]
            indices = list(range(len(confs)))

            fig2, ax2 = plt.subplots(figsize=(4, 1.8))
            fig2.patch.set_facecolor('#0a0f1e')
            ax2.set_facecolor('#0a0f1e')

            ax2.plot(indices, confs, color='#1a2035', linewidth=1.5, zorder=1)
            ax2.scatter(indices, confs, c=colors_line, s=40, zorder=2, edgecolors='none')
            ax2.axhline(y=60, color='#ff8800', linewidth=0.8, linestyle='--', alpha=0.5)
            ax2.fill_between(indices, confs, alpha=0.05, color='#4a9eff')

            ax2.set_ylim(0, 105)
            ax2.set_xlim(-0.5, len(indices) - 0.5)
            ax2.tick_params(colors='#333', labelsize=7)
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.spines['bottom'].set_color('#1a2035')
            ax2.spines['left'].set_color('#1a2035')
            for label in ax2.get_yticklabels():
                label.set_color('#555')
            ax2.set_xticklabels([])
            ax2.set_ylabel('%', color='#444', fontsize=7)
            plt.tight_layout(pad=0.3)
            st.pyplot(fig2, use_container_width=True)
            plt.close()

# ── FOOTER ────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style='
    text-align:center;
    font-family:Share Tech Mono,monospace;
    font-size:0.65rem;
    color:#2a3550;
    letter-spacing:2px;
    padding:0.3rem 0;
'>
    CLOUDGUARD IDS · RANDOM FOREST · NSL-KDD · AWS LAMBDA · API GATEWAY · SNS ·
    EAST POINT COLLEGE OF HIGHER EDUCATION · AI EXPO 2026
</div>
""", unsafe_allow_html=True)
