import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go
import time

# ---------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="Energy Grid Monitor", layout="wide", page_icon="⚡")
DB_CONNECTION = 'postgresql://postgres:T4e!fsF#GY3@localhost:5432/Anomaly_db'


# ---------------------------------------------------------
# 2. DATA LOADING
# ---------------------------------------------------------
@st.cache_data(ttl=60)  # Cache clears every 60 seconds
def load_data():
    try:
        engine = create_engine(DB_CONNECTION)
        query = "SELECT * FROM energy_data ORDER BY timestamp ASC"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        return None


df = load_data()

if df is None:
    st.error("❌ Could not connect to Database. Make sure PostgreSQL is running.")
    st.stop()

# ---------------------------------------------------------
# 3. SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.header("Filter Options")
days_to_show = st.sidebar.slider("Days of History", min_value=1, max_value=30, value=7)

# Filter dataframe based on slider
cutoff_date = df['timestamp'].max() - pd.Timedelta(days=days_to_show)
df_filtered = df[df['timestamp'] > cutoff_date]

# ---------------------------------------------------------
# 4. MAIN DASHBOARD
# ---------------------------------------------------------
st.title("⚡ Energy Grid Intelligent Monitor")
st.markdown(f"**Status:** System Active | **Data Points:** {len(df)}")

# --- KPI ROW ---
col1, col2, col3, col4 = st.columns(4)

latest = df.iloc[-1]
prev = df.iloc[-2]

# KPI 1: Current Load
with col1:
    st.metric(label="Current Load (kWh)",
              value=f"{latest['load_value']:.0f} kWh",
              delta=f"{latest['load_value'] - prev['load_value']:.1f}")

# KPI 2: Predicted Load (Model Accuracy Check)
with col2:
    pred_val = latest.get('predicted_load', 0)
    # Handle NaN if prediction is missing
    if pd.isna(pred_val): pred_val = 0

    st.metric(label="Model Prediction",
              value=f"{pred_val:.0f} kWh",
              delta_color="off")

# KPI 3: Anomaly Status
with col3:
    is_anomaly = latest['is_anomaly']
    status_text = "⚠️ ANOMALY DETECTED" if is_anomaly else "✅ NORMAL"
    st.metric(label="Network Status", value=status_text)

# KPI 4: Max Load (Last 24h)
with col4:
    last_24h = df.tail(24)
    max_load = last_24h['load_value'].max()
    st.metric(label="Max Load (24h)", value=f"{max_load:.0f} kWh")

st.divider()

# --- MAIN CHART ---
st.subheader("Real-Time Load vs. Forecast & Anomalies")

fig = go.Figure()

# 1. Actual Load Line
fig.add_trace(go.Scatter(
    x=df_filtered['timestamp'],
    y=df_filtered['load_value'],
    mode='lines',
    name='Actual Consumption',
    line=dict(color='#2E86C1', width=2)
))

# 2. Predicted Load Line (if available)
if 'predicted_load' in df_filtered.columns:
    fig.add_trace(go.Scatter(
        x=df_filtered['timestamp'],
        y=df_filtered['predicted_load'],
        mode='lines',
        name='AI Forecast',
        line=dict(color='#28B463', width=2, dash='dot')
    ))

# 3. Anomalies (Red Dots)
anomalies = df_filtered[df_filtered['is_anomaly'] == True]
fig.add_trace(go.Scatter(
    x=anomalies['timestamp'],
    y=anomalies['load_value'],
    mode='markers',
    name='Anomaly Detected',
    marker=dict(color='red', size=12, symbol='x-open', line=dict(width=2))
))

fig.update_layout(
    height=500,
    xaxis_title="Time",
    yaxis_title="Energy Load (kWh)",
    hovermode="x unified",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# 5. RECENT ALERTS TABLE
# ---------------------------------------------------------
st.subheader("🚨 Recent Anomalies Log")
recent_anomalies = df[df['is_anomaly'] == True].sort_values(by='timestamp', ascending=False).head(5)

if not recent_anomalies.empty:
    st.dataframe(recent_anomalies[['timestamp', 'load_value', 'predicted_load']].style.format(
        {"load_value": "{:.2f}", "predicted_load": "{:.2f}"}))
else:
    st.info("No anomalies detected in the recorded history.")

# Button to manually trigger pipeline (Simulation)
if st.button("🔄 Trigger Manual Data Update"):
    with st.spinner('Running ETL Pipeline...'):
        # Here we would normally call the prefect flow,
        # but for the UI we just simulate a delay
        time.sleep(2)
        st.success("Pipeline triggered! Refresh page to see new data.")
