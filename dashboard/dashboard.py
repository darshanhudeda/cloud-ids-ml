import streamlit as st
import requests
import time
import pandas as pd
from datetime import datetime
import os

# Get API URL from Streamlit secrets or environment
API_URL = st.secrets.get("API_URL", "your-api-url-here")

traffic_records = {
    "normal":  [0,1,2,0,491,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,1,0,0,150,25,0.17,0.03,0.17,0,0.05,0,0,0],
    "DoS":     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,511,511,1,1,0,0,1,0,0,255,255,1,0,1,0,1,1,0,0],
    "Probe":   [0,2,52,10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,0,1,229,229,1,0,0,0,0,0,0,0],
    "R2L":     [0,0,21,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,1,0,0,24,9,0.38,0,0.38,0,0,0,0,0],
    "U2R":     [0,0,21,0,0,0,0,0,0,1,0,1,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,0,0,1,1,1,0,1,0,0,0,0,0],
}

st.set_page_config(page_title="CloudGuard IDS", page_icon="🛡️", layout="wide")

# Session state
if 'log' not in st.session_state:
    st.session_state.log = []
if 'total' not in st.session_state:
    st.session_state.total = 0
if 'alerts' not in st.session_state:
    st.session_state.alerts = 0
if 'last_result' not in st.session_state:
    st.session_state.last_result = None

def send_traffic(traffic_type):
    try:
        response = requests.post(API_URL, json={'features': traffic_records[traffic_type]})
        result = response.json()
        result['sent'] = traffic_type
        result['time'] = datetime.now().strftime('%H:%M:%S')
        # Two-layer alert
        if result.get('prediction') == 'normal' and result.get('confidence', 1) < 0.60:
            result['alert'] = True
            result['prediction'] = 'Suspicious'
        st.session_state.last_result = result
        st.session_state.log.insert(0, result)
        st.session_state.total += 1
        if result.get('alert'):
            st.session_state.alerts += 1
    except Exception as e:
        st.error(f"API Error: {e}")

# Header
st.markdown("<h1 style='text-align:center'>🛡️ CloudGuard IDS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#888'>Cloud-Based Intrusion Detection System | AWS Lambda + ML</p>", unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🎮 Send Traffic")
    if st.button("✅ Normal Traffic", use_container_width=True):
        send_traffic("normal")
    if st.button("💥 DoS Attack", use_container_width=True):
        send_traffic("DoS")
    if st.button("🔍 Probe Attack", use_container_width=True):
        send_traffic("Probe")
    if st.button("🔓 R2L Attack", use_container_width=True):
        send_traffic("R2L")
    if st.button("☠️ U2R Attack", use_container_width=True):
        send_traffic("U2R")
    if st.button("🔄 Auto Simulate 20 Records", use_container_width=True):
        sequence = ["normal","DoS","normal","Probe","DoS","normal","R2L",
                    "DoS","normal","U2R","DoS","normal","DoS","normal",
                    "Probe","DoS","normal","R2L","normal","DoS"]
        p = st.progress(0)
        for i, t in enumerate(sequence):
            send_traffic(t)
            p.progress((i+1)/len(sequence))
            time.sleep(0.5)
        st.rerun()

with col2:
    if st.session_state.last_result:
        r = st.session_state.last_result
        if r.get('alert'):
            st.error(f"🚨 ATTACK DETECTED: {r['prediction']} | Confidence: {r['confidence']*100:.1f}% | Email Alert Sent via SNS")
        else:
            st.success(f"✅ NORMAL TRAFFIC | Confidence: {r['confidence']*100:.1f}% | No threat detected")
    else:
        st.info("Click a button to send traffic to the IDS")

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Records", st.session_state.total)
    m2.metric("Attacks Detected", st.session_state.alerts)
    m3.metric("Safe Traffic", st.session_state.total - st.session_state.alerts)

    if st.session_state.log:
        st.markdown("### 📋 Traffic Log")
        df = pd.DataFrame(st.session_state.log[:15])[['time','sent','prediction','confidence','alert']]
        df.columns = ['Time','Sent','Predicted','Confidence','Alert']
        df['Alert'] = df['Alert'].map({True:'🚨 YES', False:'✅ NO'})
        df['Confidence'] = df['Confidence'].apply(lambda x: f'{x*100:.1f}%')
        st.dataframe(df, use_container_width=True, hide_index=True)

    if st.button("🗑️ Clear Log"):
        st.session_state.log = []
        st.session_state.total = 0
        st.session_state.alerts = 0
        st.session_state.last_result = None
        st.rerun()
