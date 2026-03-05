import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import io

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FraudGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background-color: #0a0d14; color: #e2e8f0; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1117 0%, #0a0d14 100%); border-right: 1px solid #1e2533; }
    [data-testid="stSidebar"] .block-container { padding-top: 2rem; }
    .main-header { font-family: 'Space Mono', monospace; font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #ef4444, #f97316, #ef4444); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shimmer 3s linear infinite; letter-spacing: -1px; margin-bottom: 0; }
    @keyframes shimmer { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }
    .sub-header { font-size: 0.85rem; color: #64748b; font-family: 'Space Mono', monospace; letter-spacing: 0.15em; text-transform: uppercase; margin-top: 0.2rem; }
    .metric-card { background: linear-gradient(135deg, #111827 0%, #0d1117 100%); border: 1px solid #1e2533; border-radius: 12px; padding: 1.25rem 1.5rem; position: relative; overflow: hidden; }
    .metric-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #ef4444, #f97316); }
    .metric-label { font-size: 0.7rem; font-family: 'Space Mono', monospace; color: #64748b; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.4rem; }
    .metric-value { font-size: 1.8rem; font-weight: 600; font-family: 'Space Mono', monospace; color: #f1f5f9; line-height: 1; }
    .metric-delta { font-size: 0.75rem; color: #22c55e; margin-top: 0.3rem; }
    .verdict-fraud { background: linear-gradient(135deg, rgba(239,68,68,0.15) 0%, rgba(185,28,28,0.1) 100%); border: 1px solid rgba(239,68,68,0.4); border-left: 4px solid #ef4444; border-radius: 12px; padding: 1.5rem 2rem; text-align: center; }
    .verdict-legit { background: linear-gradient(135deg, rgba(34,197,94,0.15) 0%, rgba(21,128,61,0.1) 100%); border: 1px solid rgba(34,197,94,0.4); border-left: 4px solid #22c55e; border-radius: 12px; padding: 1.5rem 2rem; text-align: center; }
    .verdict-title { font-family: 'Space Mono', monospace; font-size: 1.6rem; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 0.3rem; }
    .verdict-fraud .verdict-title { color: #ef4444; }
    .verdict-legit .verdict-title { color: #22c55e; }
    .verdict-conf { font-size: 0.85rem; color: #94a3b8; font-family: 'Space Mono', monospace; }
    .section-label { font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #475569; letter-spacing: 0.2em; text-transform: uppercase; border-bottom: 1px solid #1e2533; padding-bottom: 0.5rem; margin-bottom: 1.2rem; }
    .stSlider > div > div { background: #1e2533 !important; }
    .stSelectbox > div > div { background: #111827 !important; border-color: #1e2533 !important; }
    .stNumberInput > div > div > input { background: #111827 !important; border-color: #1e2533 !important; color: #e2e8f0 !important; }
    .stButton > button { background: linear-gradient(135deg, #ef4444, #dc2626); color: white; border: none; border-radius: 8px; font-family: 'Space Mono', monospace; font-size: 0.85rem; letter-spacing: 0.08em; padding: 0.6rem 2rem; width: 100%; transition: all 0.2s; box-shadow: 0 4px 20px rgba(239,68,68,0.3); }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 6px 25px rgba(239,68,68,0.45); }
    .stTabs [data-baseweb="tab-list"] { background: #0d1117; border-bottom: 1px solid #1e2533; gap: 0; }
    .stTabs [data-baseweb="tab"] { font-family: 'Space Mono', monospace; font-size: 0.78rem; letter-spacing: 0.1em; color: #64748b; background: transparent; border: none; padding: 0.75rem 1.5rem; }
    .stTabs [aria-selected="true"] { color: #ef4444 !important; border-bottom: 2px solid #ef4444 !important; background: transparent !important; }
    .stat-row { display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0; border-bottom: 1px solid #1a2030; }
    .stat-name { font-size: 0.78rem; color: #64748b; font-family: 'Space Mono', monospace; }
    .stat-val { font-size: 0.9rem; font-weight: 600; font-family: 'Space Mono', monospace; color: #22c55e; }
    hr { border-color: #1e2533 !important; }
    .fraud-row { background-color: rgba(239,68,68,0.08) !important; }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #22c55e; display: inline-block; margin-right: 6px; animation: pulse 2s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
    [data-testid="stFileUploader"] { border: 1px dashed #1e2533 !important; border-radius: 12px !important; background: #0d1117 !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2rem; max-width: 1400px; }
</style>
""", unsafe_allow_html=True)


# ─── Load Model Artifacts ─────────────────────────────────────────────────────
@st.cache_resource
def load_artifacts():
    """Load model, scaler, and label encoder. Searches common locations."""
    search_dirs = [Path("."), Path("/home/claude"), Path("/mnt/user-data/uploads")]
    artifacts = {}
    files = {
        "model":   "fraud_model.pkl",
        "scaler":  "scaler.pkl",
        "encoder": "label_encoder.pkl",
    }
    for key, fname in files.items():
        for d in search_dirs:
            p = d / fname
            if p.exists():
                with open(p, "rb") as f:
                    artifacts[key] = pickle.load(f)
                break
    return artifacts

artifacts = load_artifacts()
model_loaded = "model" in artifacts and "scaler" in artifacts


# ─── Feature Metadata ─────────────────────────────────────────────────────────
FEATURE_COLS  = ["amount", "transaction_hour", "merchant_category",
                 "foreign_transaction", "location_mismatch",
                 "device_trust_score", "velocity_last_24h", "cardholder_age"]
MERCHANT_CATS = ["Clothing", "Electronics", "Food", "Grocery", "Travel"]

# Hardcoded label-encoding map — mirrors exactly what LabelEncoder produces
# (alphabetical order: Clothing=0, Electronics=1, Food=2, Grocery=3, Travel=4).
# Used only when label_encoder.pkl cannot be found.
MERCHANT_LABEL_MAP = {cat: i for i, cat in enumerate(sorted(MERCHANT_CATS))}

MODEL_STATS = {
    "Precision": 1.00,
    "Recall":    0.60,
    "F1-Score":  0.75,
    "ROC-AUC":   1.00,
}


# ─── Helper Functions ─────────────────────────────────────────────────────────
def encode_merchant(series):
    """
    Encode merchant_category strings to integer codes.

    Priority:
      1. Saved LabelEncoder from label_encoder.pkl  — exact match to training.
      2. Hardcoded alphabetical map                 — safe fallback, same result
         because sklearn LabelEncoder sorts classes alphabetically.

    Raises ValueError with a clear message if any value is not recognised,
    so the Streamlit error block shows a human-readable explanation rather
    than a cryptic numpy traceback.
    """
    # Validate values before encoding regardless of which path we take
    known = set(MERCHANT_CATS)
    found = set(series.dropna().unique())
    unknown = found - known
    if unknown:
        raise ValueError(
            f"merchant_category contains unrecognised values: {sorted(unknown)}.\n"
            f"Accepted values are: {sorted(known)}"
        )

    if "encoder" in artifacts:
        # Primary path: use the fitted LabelEncoder saved during training
        return artifacts["encoder"].transform(series)
    else:
        # Fallback: alphabetical integer map — identical output to LabelEncoder
        return series.map(MERCHANT_LABEL_MAP)


def preprocess_single(amount, hour, merchant, foreign, location, device, velocity, age):
    """
    Build and preprocess a single-transaction DataFrame for inference.
    merchant_category is encoded to an integer; amount is scaled.
    Returns a DataFrame with exactly FEATURE_COLS columns.
    """
    df = pd.DataFrame([{
        "amount":              amount,
        "transaction_hour":    hour,
        "merchant_category":   merchant,
        "foreign_transaction": foreign,
        "location_mismatch":   location,
        "device_trust_score":  device,
        "velocity_last_24h":   velocity,
        "cardholder_age":      age,
    }])
    df["merchant_category"] = encode_merchant(df["merchant_category"])
    df[["amount"]] = artifacts["scaler"].transform(df[["amount"]])
    return df[FEATURE_COLS]


def preprocess_batch(df_raw):
    """
    Preprocess an uploaded CSV for batch inference.

    Steps:
      1. Drop non-feature columns (transaction_id, is_fraud) if present.
      2. Validate merchant_category column exists.
      3. Encode merchant_category as a single integer column via encode_merchant()
         — this always produces exactly 1 column, keeping the feature count at 8.
         Using pd.get_dummies() here would expand to 5+ columns and break the model.
      4. Scale amount with the fitted StandardScaler.
      5. Return df with exactly FEATURE_COLS in the correct order.

    Raises ValueError with readable messages for missing/invalid columns
    so the Streamlit except block can surface them cleanly.
    """
    df = df_raw.copy()

    # ── 1. Drop identifier / target columns ──────────────────────────────────
    for col in ["transaction_id", "is_fraud"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    # ── 2. Validate required columns are all present ──────────────────────────
    missing_cols = [c for c in FEATURE_COLS if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"CSV is missing required column(s): {missing_cols}\n"
            f"Columns detected in file: {df.columns.tolist()}"
        )

    # ── 3. Encode merchant_category → single integer column ───────────────────
    # IMPORTANT: must stay as one column (integer), NOT one-hot encoded.
    # The model was trained with LabelEncoder which maps each category to a
    # single integer. Using pd.get_dummies() would produce 5 columns instead
    # of 1, increasing the total feature count from 8 to 12 and causing:
    #   ValueError: X has 12 features, but model is expecting 8 features.
    df["merchant_category"] = encode_merchant(df["merchant_category"])

    # ── 4. Scale amount ───────────────────────────────────────────────────────
    df[["amount"]] = artifacts["scaler"].transform(df[["amount"]])

    # ── 5. Return exactly the 8 features the model expects, in training order ─
    return df[FEATURE_COLS]


def predict(X):
    prob  = artifacts["model"].predict_proba(X)[:, 1]
    label = (prob >= 0.5).astype(int)
    return prob, label


def gauge_chart(prob, is_fraud):
    color = "#ef4444" if is_fraud else "#22c55e"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(prob * 100, 1),
        number={"suffix": "%", "font": {"size": 36, "color": "#f1f5f9", "family": "Space Mono"}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": "#64748b", "size": 11, "family": "Space Mono"}, "ticksuffix": "%", "nticks": 6},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "#111827",
            "bordercolor": "#1e2533",
            "borderwidth": 1,
            "steps": [
                {"range": [0, 30],   "color": "rgba(34,197,94,0.12)"},
                {"range": [30, 60],  "color": "rgba(251,191,36,0.10)"},
                {"range": [60, 100], "color": "rgba(239,68,68,0.14)"},
            ],
            "threshold": {"line": {"color": "#f97316", "width": 3}, "thickness": 0.85, "value": 50},
        },
        title={"text": "FRAUD RISK SCORE", "font": {"size": 11, "color": "#64748b", "family": "Space Mono"}},
        domain={"x": [0, 1], "y": [0, 1]},
    ))
    fig.update_layout(height=260, margin=dict(t=60, b=20, l=30, r=30),
                      paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font_color="#e2e8f0")
    return fig


def batch_results_chart(df_results):
    counts = df_results["Prediction"].value_counts()
    labels = counts.index.tolist()
    values = counts.values.tolist()
    colors = ["#ef4444" if l == "FRAUD" else "#22c55e" for l in labels]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.65,
        marker=dict(colors=colors, line=dict(color="#0a0d14", width=3)),
        textfont=dict(family="Space Mono", size=12, color="#f1f5f9"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
    ))
    fraud_count = counts.get("FRAUD", 0)
    fig.add_annotation(
        text=f"<b style='font-size:24px'>{fraud_count}</b><br>"
             f"<span style='font-size:11px;color:#64748b'>FRAUD DETECTED</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(color="#ef4444", family="Space Mono"), align="center",
    )
    fig.update_layout(height=260, margin=dict(t=20, b=20, l=0, r=0),
                      paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                      legend=dict(font=dict(family="Space Mono", size=11, color="#94a3b8"),
                                  bgcolor="rgba(0,0,0,0)"), showlegend=True)
    return fig


def confidence_bar_chart(probs):
    colors = ["#ef4444" if p >= 0.5 else "#22c55e" for p in probs]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(range(1, len(probs)+1)),
        y=[round(p*100, 1) for p in probs],
        marker_color=colors, marker_line_color="#0a0d14", marker_line_width=1,
        hovertemplate="Txn #%{x}<br>Fraud prob: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=50, line_dash="dot", line_color="#f97316", line_width=1.5,
                  annotation_text="Decision threshold (50%)",
                  annotation_font=dict(color="#f97316", size=10, family="Space Mono"),
                  annotation_position="top right")
    fig.update_layout(
        height=200, margin=dict(t=20, b=40, l=40, r=20),
        paper_bgcolor="#0d1117", plot_bgcolor="#111827",
        xaxis=dict(title="Transaction #", color="#64748b", gridcolor="#1e2533",
                   tickfont=dict(family="Space Mono", size=10)),
        yaxis=dict(title="Fraud Probability (%)", color="#64748b", gridcolor="#1e2533",
                   tickfont=dict(family="Space Mono", size=10), range=[0, 105]),
        bargap=0.15,
    )
    return fig


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='margin-bottom:1.5rem'>
        <div style='font-family:Space Mono;font-size:1.15rem;font-weight:700;color:#ef4444;
                    letter-spacing:-0.5px;'>🛡️ FraudGuard<span style='color:#f97316'>AI</span></div>
        <div style='font-size:0.68rem;color:#374151;font-family:Space Mono;
                    letter-spacing:0.15em;margin-top:2px;'>DETECTION ENGINE v2.4</div>
    </div>
    """, unsafe_allow_html=True)

    status_color = "#22c55e" if model_loaded else "#ef4444"
    status_text  = "ONLINE" if model_loaded else "MODEL MISSING"
    st.markdown(f"""
    <div style='background:#0d1117;border:1px solid #1e2533;border-radius:8px;
                padding:0.75rem 1rem;margin-bottom:1.5rem;'>
        <div style='font-family:Space Mono;font-size:0.68rem;color:#475569;
                    letter-spacing:0.15em;margin-bottom:0.4rem;'>SYSTEM STATUS</div>
        <div style='display:flex;align-items:center;gap:8px;'>
            <div style='width:8px;height:8px;border-radius:50%;background:{status_color};
                        box-shadow:0 0 8px {status_color};'></div>
            <span style='font-family:Space Mono;font-size:0.82rem;color:{status_color};
                         font-weight:700;'>{status_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-label'>Model Performance</div>", unsafe_allow_html=True)
    for stat, val in MODEL_STATS.items():
        bar_w = int(val * 100)
        color = "#22c55e" if val >= 0.75 else "#f59e0b" if val >= 0.5 else "#ef4444"
        st.markdown(f"""
        <div style='margin-bottom:0.9rem;'>
            <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
                <span style='font-family:Space Mono;font-size:0.72rem;color:#64748b;
                             letter-spacing:0.08em;'>{stat}</span>
                <span style='font-family:Space Mono;font-size:0.82rem;font-weight:700;
                             color:{color};'>{val:.2f}</span>
            </div>
            <div style='background:#1e2533;border-radius:4px;height:4px;'>
                <div style='background:{color};width:{bar_w}%;height:4px;
                            border-radius:4px;transition:width 0.6s ease;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Model Details</div>", unsafe_allow_html=True)
    for k, v in {"Algorithm": "Random Forest", "Trees": "100", "Max Depth": "10",
                 "Features": "8", "Threshold": "0.50", "Training": "8,000 txns"}.items():
        st.markdown(f"""
        <div class='stat-row'>
            <span class='stat-name'>{k}</span>
            <span class='stat-val' style='color:#94a3b8;'>{v}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.65rem;color:#374151;font-family:Space Mono;
                line-height:1.6;letter-spacing:0.05em;'>
        ⚠ FOR DEMONSTRATION PURPOSES ONLY.<br>
        NOT FOR PRODUCTION FINANCIAL USE.
    </div>
    """, unsafe_allow_html=True)


# ─── Main Content ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom:2rem;'>
    <div class='main-header'>FRAUDGUARD AI</div>
    <div class='sub-header'>⬡ Real-Time Transaction Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)

if not model_loaded:
    st.error("⚠️ Model artifacts not found. Place `fraud_model.pkl`, `scaler.pkl`, "
             "and `label_encoder.pkl` in the same directory as this app.")
    st.stop()

tab_single, tab_batch = st.tabs(["  ◈  SINGLE TRANSACTION  ", "  ⊞  BATCH ANALYSIS  "])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SINGLE TRANSACTION
# ══════════════════════════════════════════════════════════════════════════════
with tab_single:
    st.markdown("<br>", unsafe_allow_html=True)
    col_form, col_result = st.columns([1.1, 1], gap="large")

    with col_form:
        st.markdown("<div class='section-label'>Transaction Details</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            amount   = st.number_input("💰 Amount ($)", min_value=0.0, max_value=10000.0,
                                       value=250.0, step=0.01, format="%.2f")
            merchant = st.selectbox("🏪 Merchant Category", options=MERCHANT_CATS, index=1)
            foreign  = st.selectbox("🌐 Foreign Transaction", options=[0, 1],
                                    format_func=lambda x: "Yes" if x else "No")
            location = st.selectbox("📍 Location Mismatch", options=[0, 1],
                                    format_func=lambda x: "Yes" if x else "No")
        with c2:
            hour     = st.slider("🕐 Transaction Hour", 0, 23, 14)
            device   = st.slider("📱 Device Trust Score", 0, 100, 72)
            velocity = st.slider("⚡ Velocity (last 24h)", 0, 20, 2)
            age      = st.slider("👤 Cardholder Age", 18, 90, 35)

        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🔍  ANALYZE TRANSACTION", use_container_width=True)

    with col_result:
        st.markdown("<div class='section-label'>Analysis Result</div>", unsafe_allow_html=True)
        if analyze_btn:
            with st.spinner("Running inference..."):
                X = preprocess_single(amount, hour, merchant, foreign,
                                      location, device, velocity, age)
                prob, label = predict(X)
                prob_val = float(prob[0])
                is_fraud = bool(label[0])

            if is_fraud:
                st.markdown(f"""
                <div class='verdict-fraud'>
                    <div class='verdict-title'>🚨 FRAUDULENT</div>
                    <div class='verdict-conf'>Confidence: {prob_val*100:.1f}% fraud probability</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='verdict-legit'>
                    <div class='verdict-title'>✅ LEGITIMATE</div>
                    <div class='verdict-conf'>Confidence: {(1-prob_val)*100:.1f}% legitimate probability</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.plotly_chart(gauge_chart(prob_val, is_fraud),
                            use_container_width=True, config={"displayModeBar": False})

            st.markdown("<div class='section-label' style='margin-top:1rem;'>Input Summary</div>",
                        unsafe_allow_html=True)
            summary_cols = st.columns(4)
            for i, (label_txt, val) in enumerate([
                ("AMOUNT", f"${amount:,.2f}"), ("HOUR", f"{hour:02d}:00"),
                ("MERCHANT", merchant),        ("FOREIGN", "YES" if foreign else "NO"),
                ("LOCATION", "MISMATCH" if location else "OK"), ("DEVICE", f"{device}/100"),
                ("VELOCITY", f"{velocity} txns"), ("AGE", f"{age} yrs"),
            ]):
                with summary_cols[i % 4]:
                    st.markdown(f"""
                    <div style='background:#0d1117;border:1px solid #1e2533;border-radius:8px;
                                padding:0.6rem 0.75rem;margin-bottom:0.5rem;text-align:center;'>
                        <div style='font-family:Space Mono;font-size:0.6rem;color:#475569;
                                    letter-spacing:0.1em;'>{label_txt}</div>
                        <div style='font-family:Space Mono;font-size:0.88rem;color:#e2e8f0;
                                    font-weight:600;margin-top:2px;'>{val}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='height:380px;display:flex;flex-direction:column;align-items:center;
                        justify-content:center;border:1px dashed #1e2533;border-radius:12px;
                        background:#0d1117;'>
                <div style='font-size:3rem;margin-bottom:1rem;opacity:0.3;'>🛡️</div>
                <div style='font-family:Space Mono;font-size:0.78rem;color:#374151;
                            letter-spacing:0.15em;text-align:center;'>
                    ENTER TRANSACTION DETAILS<br>AND CLICK ANALYZE
                </div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — BATCH ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_batch:
    st.markdown("<br>", unsafe_allow_html=True)
    col_info, col_dl = st.columns([2, 1])
    with col_info:
        st.markdown("""
        <div style='background:#0d1117;border:1px solid #1e2533;border-radius:10px;
                    padding:1rem 1.25rem;'>
            <div style='font-family:Space Mono;font-size:0.68rem;color:#475569;
                        letter-spacing:0.15em;margin-bottom:0.5rem;'>REQUIRED CSV COLUMNS</div>
            <div style='font-family:Space Mono;font-size:0.78rem;color:#64748b;line-height:1.8;'>
                amount · transaction_hour · merchant_category · foreign_transaction ·
                location_mismatch · device_trust_score · velocity_last_24h · cardholder_age
            </div>
        </div>""", unsafe_allow_html=True)

    with col_dl:
        sample_data = pd.DataFrame([
            {"amount": 150.00,  "transaction_hour": 14, "merchant_category": "Electronics",
             "foreign_transaction": 0, "location_mismatch": 0, "device_trust_score": 80,
             "velocity_last_24h": 2,  "cardholder_age": 35},
            {"amount": 1200.00, "transaction_hour": 3,  "merchant_category": "Travel",
             "foreign_transaction": 1, "location_mismatch": 1, "device_trust_score": 20,
             "velocity_last_24h": 8,  "cardholder_age": 28},
            {"amount": 45.50,   "transaction_hour": 11, "merchant_category": "Grocery",
             "foreign_transaction": 0, "location_mismatch": 0, "device_trust_score": 95,
             "velocity_last_24h": 1,  "cardholder_age": 52},
        ])
        st.download_button("⬇  Download Template CSV", data=sample_data.to_csv(index=False),
                           file_name="fraud_check_template.csv", mime="text/csv",
                           use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload transaction CSV for batch analysis", type=["csv"],
                                help="Upload a CSV with the required columns listed above")

    if uploaded:
        try:
            df_raw = pd.read_csv(uploaded)
            st.markdown(f"""
            <div style='font-family:Space Mono;font-size:0.75rem;color:#475569;
                        margin:0.5rem 0 1rem;'>
                ✓ Loaded {len(df_raw):,} transactions · {df_raw.shape[1]} columns detected
            </div>""", unsafe_allow_html=True)

            with st.spinner(f"Analyzing {len(df_raw):,} transactions..."):
                X_batch       = preprocess_batch(df_raw)
                probs, labels = predict(X_batch)

            df_results = df_raw.copy()
            for col in ["transaction_id", "is_fraud"]:
                if col in df_results.columns:
                    df_results = df_results.drop(columns=[col])
            df_results.insert(0, "Fraud Probability", [f"{p*100:.1f}%" for p in probs])
            df_results.insert(0, "Prediction", ["FRAUD" if l else "LEGITIMATE" for l in labels])
            df_results.insert(0, "Txn #", range(1, len(df_results)+1))

            n_total  = len(labels)
            n_fraud  = int(labels.sum())
            n_legit  = n_total - n_fraud
            avg_risk = float(probs.mean()) * 100
            max_risk = float(probs.max()) * 100

            st.markdown("<div class='section-label'>Batch Summary</div>", unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            for col, label_txt, val, delta_txt, delta_color in [
                (m1, "TOTAL TRANSACTIONS", f"{n_total:,}",  "batch complete",                    "#64748b"),
                (m2, "FRAUDULENT",         f"{n_fraud:,}",  f"{n_fraud/n_total*100:.1f}% of batch", "#ef4444"),
                (m3, "LEGITIMATE",         f"{n_legit:,}",  f"{n_legit/n_total*100:.1f}% of batch", "#22c55e"),
                (m4, "AVG RISK SCORE",     f"{avg_risk:.1f}%", f"max: {max_risk:.1f}%",          "#f97316"),
            ]:
                col.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>{label_txt}</div>
                    <div class='metric-value' style='color:{delta_color if label_txt != "TOTAL TRANSACTIONS" else "#f1f5f9"};'>
                        {val}</div>
                    <div class='metric-delta' style='color:{delta_color};'>{delta_txt}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            ch1, ch2 = st.columns([1, 2])
            with ch1:
                st.markdown("<div class='section-label'>Fraud Distribution</div>",
                            unsafe_allow_html=True)
                st.plotly_chart(batch_results_chart(df_results),
                                use_container_width=True, config={"displayModeBar": False})
            with ch2:
                st.markdown("<div class='section-label'>Fraud Probability by Transaction</div>",
                            unsafe_allow_html=True)
                st.plotly_chart(confidence_bar_chart(probs),
                                use_container_width=True, config={"displayModeBar": False})

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='section-label'>Transaction Results</div>",
                        unsafe_allow_html=True)
            filter_col, dl_col = st.columns([2, 1])
            with filter_col:
                show_filter = st.radio("Show",
                    ["All Transactions", "Fraud Only", "Legitimate Only"],
                    horizontal=True, label_visibility="collapsed")
            with dl_col:
                st.download_button("⬇  Export Results CSV",
                    data=df_results.to_csv(index=False),
                    file_name="fraud_analysis_results.csv", mime="text/csv",
                    use_container_width=True)

            if show_filter == "Fraud Only":
                df_display = df_results[df_results["Prediction"] == "FRAUD"]
            elif show_filter == "Legitimate Only":
                df_display = df_results[df_results["Prediction"] == "LEGITIMATE"]
            else:
                df_display = df_results

            def highlight_fraud(row):
                if row["Prediction"] == "FRAUD":
                    return ["background-color: rgba(239,68,68,0.10); color: #fca5a5"
                            if col == "Prediction" else
                            "background-color: rgba(239,68,68,0.06); color: #e2e8f0"
                            for col in row.index]
                return ["color: #86efac" if col == "Prediction" else "color: #e2e8f0"
                        for col in row.index]

            styled = (
                df_display.style
                .apply(highlight_fraud, axis=1)
                .set_properties(**{"font-family": "Space Mono, monospace",
                                   "font-size": "12px", "border": "1px solid #1e2533"})
                .set_table_styles([
                    {"selector": "thead th",
                     "props": [("background", "#0d1117"), ("color", "#64748b"),
                               ("font-family", "Space Mono, monospace"), ("font-size", "11px"),
                               ("letter-spacing", "0.1em"), ("border-bottom", "1px solid #1e2533")]},
                    {"selector": "tbody tr:hover",
                     "props": [("background", "rgba(255,255,255,0.03)")]},
                ])
            )
            st.dataframe(styled, use_container_width=True, height=380)
            st.markdown(f"""
            <div style='font-family:Space Mono;font-size:0.68rem;color:#374151;
                        text-align:right;margin-top:0.5rem;'>
                Showing {len(df_display):,} of {n_total:,} transactions
            </div>""", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.markdown("""
            <div style='font-family:Space Mono;font-size:0.78rem;color:#64748b;margin-top:0.5rem;'>
                Ensure your CSV contains all required columns with correct names and types.<br>
                merchant_category must be one of: Clothing, Electronics, Food, Grocery, Travel
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='height:280px;display:flex;flex-direction:column;align-items:center;
                    justify-content:center;border:1px dashed #1e2533;border-radius:12px;
                    background:#0d1117;'>
            <div style='font-size:2.5rem;margin-bottom:1rem;opacity:0.25;'>📊</div>
            <div style='font-family:Space Mono;font-size:0.78rem;color:#374151;
                        letter-spacing:0.15em;text-align:center;'>
                UPLOAD A CSV TO BEGIN BATCH ANALYSIS
            </div>
        </div>""", unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='border-top:1px solid #1e2533;padding-top:1rem;display:flex;
            justify-content:space-between;align-items:center;'>
    <div style='font-family:Space Mono;font-size:0.65rem;color:#374151;letter-spacing:0.1em;'>
        🛡️ FRAUDGUARD AI · DETECTION ENGINE v2.4
    </div>
    <div style='font-family:Space Mono;font-size:0.65rem;color:#374151;letter-spacing:0.1em;'>
        RANDOM FOREST · 8 FEATURES · THRESHOLD: 0.50
    </div>
</div>
""", unsafe_allow_html=True)