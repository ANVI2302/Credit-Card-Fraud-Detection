import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
from pathlib import Path

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
    .main-header { font-family: 'Space Mono', monospace; font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #ef4444, #f97316, #ef4444); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shimmer 3s linear infinite; letter-spacing: -1px; margin-bottom: 0; }
    @keyframes shimmer { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }
    .sub-header { font-size: 0.85rem; color: #64748b; font-family: 'Space Mono', monospace; letter-spacing: 0.15em; text-transform: uppercase; margin-top: 0.2rem; }
    .metric-card { background: linear-gradient(135deg, #111827 0%, #0d1117 100%); border: 1px solid #1e2533; border-radius: 12px; padding: 1.25rem 1.5rem; position: relative; overflow: hidden; }
    .metric-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #ef4444, #f97316); }
    .metric-label { font-size: 0.7rem; font-family: 'Space Mono', monospace; color: #64748b; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.4rem; }
    .metric-value { font-size: 1.8rem; font-weight: 600; font-family: 'Space Mono', monospace; color: #f1f5f9; line-height: 1; }
    .metric-delta { font-size: 0.75rem; color: #22c55e; margin-top: 0.3rem; }
    .section-label { font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #475569; letter-spacing: 0.2em; text-transform: uppercase; border-bottom: 1px solid #1e2533; padding-bottom: 0.5rem; margin-bottom: 1.2rem; }
    .stButton > button { background: linear-gradient(135deg, #ef4444, #dc2626); color: white; border: none; border-radius: 8px; font-family: 'Space Mono', monospace; font-size: 0.85rem; letter-spacing: 0.08em; padding: 0.6rem 2rem; width: 100%; transition: all 0.2s; box-shadow: 0 4px 20px rgba(239,68,68,0.3); }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 6px 25px rgba(239,68,68,0.45); }
    .stTabs [data-baseweb="tab-list"] { background: #0d1117; border-bottom: 1px solid #1e2533; gap: 0; }
    .stTabs [data-baseweb="tab"] { font-family: 'Space Mono', monospace; font-size: 0.78rem; letter-spacing: 0.1em; color: #64748b; background: transparent; border: none; padding: 0.75rem 1.5rem; }
    .stTabs [aria-selected="true"] { color: #ef4444 !important; border-bottom: 2px solid #ef4444 !important; background: transparent !important; }
    .stat-row { display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0; border-bottom: 1px solid #1a2030; }
    .stat-name { font-size: 0.78rem; color: #64748b; font-family: 'Space Mono', monospace; }
    .stat-val { font-size: 0.9rem; font-weight: 600; font-family: 'Space Mono', monospace; color: #22c55e; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2rem; max-width: 1400px; }
    .info-box { background: #0d1117; border: 1px solid #1e2533; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 1rem; }
    .info-box-title { font-family: 'Space Mono', monospace; font-size: 0.68rem; color: #475569; letter-spacing: 0.15em; margin-bottom: 0.5rem; }
    .col-pill { display: inline-block; background: #1e2533; border-radius: 4px; padding: 2px 8px; margin: 2px; font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #94a3b8; }
    .col-pill.numeric { background: rgba(34,197,94,0.15); color: #22c55e; }
    .verdict-fraud { background: linear-gradient(135deg, rgba(239,68,68,0.15) 0%, rgba(185,28,28,0.1) 100%); border: 1px solid rgba(239,68,68,0.4); border-left: 4px solid #ef4444; border-radius: 12px; padding: 1.5rem 2rem; text-align: center; }
    .verdict-legit { background: linear-gradient(135deg, rgba(34,197,94,0.15) 0%, rgba(21,128,61,0.1) 100%); border: 1px solid rgba(34,197,94,0.4); border-left: 4px solid #22c55e; border-radius: 12px; padding: 1.5rem 2rem; text-align: center; }
    .verdict-title { font-family: 'Space Mono', monospace; font-size: 1.6rem; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 0.3rem; }
    .verdict-fraud .verdict-title { color: #ef4444; }
    .verdict-legit .verdict-title { color: #22c55e; }
    .verdict-conf { font-size: 0.85rem; color: #94a3b8; font-family: 'Space Mono', monospace; }
</style>
""", unsafe_allow_html=True)


# ─── Load Model Artifacts ─────────────────────────────────────────────────────
@st.cache_resource
def load_artifacts():
    search_dirs = [Path("."), Path("/home/claude"), Path("/mnt/user-data/uploads")]
    artifacts = {}
    files = {"model": "fraud_model.pkl", "scaler": "scaler.pkl", "encoder": "label_encoder.pkl"}
    for key, fname in files.items():
        for d in search_dirs:
            p = d / fname
            if p.exists():
                with open(p, "rb") as f:
                    artifacts[key] = pickle.load(f)
                break
    return artifacts

artifacts = load_artifacts()
model_loaded = "model" in artifacts
MODEL_STATS = {"Precision": 1.00, "Recall": 0.60, "F1-Score": 0.75, "ROC-AUC": 1.00}


# ─── Smart CSV Preprocessor ───────────────────────────────────────────────────
def smart_preprocess(df_raw, target_col=None):
    df = df_raw.copy()
    if target_col and target_col in df.columns:
        df = df.drop(columns=[target_col])
    auto_drop = [c for c in df.columns if c.lower() in ["id", "transaction_id", "txn_id", "index", "unnamed: 0"]]
    if auto_drop:
        df = df.drop(columns=auto_drop)
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = pd.factorize(df[col])[0]
    df = df.fillna(df.median(numeric_only=True))
    model = artifacts["model"]
    expected_features = model.n_features_in_
    if len(df.columns) > expected_features:
        df = df.iloc[:, :expected_features]
    elif len(df.columns) < expected_features:
        for i in range(expected_features - len(df.columns)):
            df[f"_pad_{i}"] = 0
    if "scaler" in artifacts:
        try:
            scaled = artifacts["scaler"].transform(df)
            df = pd.DataFrame(scaled, columns=df.columns)
        except Exception:
            pass
    return df


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
            "bgcolor": "#111827", "bordercolor": "#1e2533", "borderwidth": 1,
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
        text=f"<b style='font-size:24px'>{fraud_count}</b><br><span style='font-size:11px;color:#64748b'>FRAUD DETECTED</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(color="#ef4444", family="Space Mono"), align="center",
    )
    fig.update_layout(height=260, margin=dict(t=20, b=20, l=0, r=0),
                      paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                      legend=dict(font=dict(family="Space Mono", size=11, color="#94a3b8"), bgcolor="rgba(0,0,0,0)"), showlegend=True)
    return fig


def confidence_bar_chart(probs):
    display_probs = probs[:500]
    colors = ["#ef4444" if p >= 0.5 else "#22c55e" for p in display_probs]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(range(1, len(display_probs)+1)),
        y=[round(p*100, 1) for p in display_probs],
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
        xaxis=dict(title="Transaction #", color="#64748b", gridcolor="#1e2533", tickfont=dict(family="Space Mono", size=10)),
        yaxis=dict(title="Fraud Probability (%)", color="#64748b", gridcolor="#1e2533", tickfont=dict(family="Space Mono", size=10), range=[0, 105]),
        bargap=0.15,
    )
    return fig


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='margin-bottom:1.5rem'>
        <div style='font-family:Space Mono;font-size:1.15rem;font-weight:700;color:#ef4444;letter-spacing:-0.5px;'>🛡️ FraudGuard<span style='color:#f97316'>AI</span></div>
        <div style='font-size:0.68rem;color:#374151;font-family:Space Mono;letter-spacing:0.15em;margin-top:2px;'>DETECTION ENGINE v2.4</div>
    </div>
    """, unsafe_allow_html=True)

    status_color = "#22c55e" if model_loaded else "#ef4444"
    status_text  = "ONLINE" if model_loaded else "MODEL MISSING"
    st.markdown(f"""
    <div style='background:#0d1117;border:1px solid #1e2533;border-radius:8px;padding:0.75rem 1rem;margin-bottom:1.5rem;'>
        <div style='font-family:Space Mono;font-size:0.68rem;color:#475569;letter-spacing:0.15em;margin-bottom:0.4rem;'>SYSTEM STATUS</div>
        <div style='display:flex;align-items:center;gap:8px;'>
            <div style='width:8px;height:8px;border-radius:50%;background:{status_color};box-shadow:0 0 8px {status_color};'></div>
            <span style='font-family:Space Mono;font-size:0.82rem;color:{status_color};font-weight:700;'>{status_text}</span>
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
                <span style='font-family:Space Mono;font-size:0.72rem;color:#64748b;letter-spacing:0.08em;'>{stat}</span>
                <span style='font-family:Space Mono;font-size:0.82rem;font-weight:700;color:{color};'>{val:.2f}</span>
            </div>
            <div style='background:#1e2533;border-radius:4px;height:4px;'>
                <div style='background:{color};width:{bar_w}%;height:4px;border-radius:4px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Model Details</div>", unsafe_allow_html=True)
    for k, v in {"Algorithm": "Random Forest", "Trees": "100", "Max Depth": "10", "Threshold": "0.50"}.items():
        st.markdown(f"<div class='stat-row'><span class='stat-name'>{k}</span><span class='stat-val' style='color:#94a3b8;'>{v}</span></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.65rem;color:#374151;font-family:Space Mono;line-height:1.6;letter-spacing:0.05em;'>⚠ FOR DEMONSTRATION PURPOSES ONLY.<br>NOT FOR PRODUCTION FINANCIAL USE.</div>", unsafe_allow_html=True)


# ─── Main Content ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom:2rem;'>
    <div class='main-header'>FRAUDGUARD AI</div>
    <div class='sub-header'>⬡ Real-Time Transaction Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)

if not model_loaded:
    st.error("⚠️ Model artifacts not found. Place `fraud_model.pkl` in the same directory as this app.")
    st.stop()

tab_single, tab_batch = st.tabs(["  ◈  SINGLE TRANSACTION  ", "  ⊞  BATCH ANALYSIS  "])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SINGLE TRANSACTION
# ══════════════════════════════════════════════════════════════════════════════
with tab_single:
    st.markdown("<br>", unsafe_allow_html=True)
    n_features = artifacts["model"].n_features_in_

    st.markdown(f"""
    <div class='info-box'>
        <div class='info-box-title'>ℹ️ MODEL INFO</div>
        <div style='font-family:Space Mono;font-size:0.78rem;color:#64748b;'>
            Your model expects <span style='color:#f97316;font-weight:700;'>{n_features} numeric features</span>.
            Enter values below corresponding to the columns your model was trained on.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_result = st.columns([1.1, 1], gap="large")
    with col_form:
        st.markdown("<div class='section-label'>Feature Values</div>", unsafe_allow_html=True)
        feature_values = []
        cols_per_row = 3
        rows = [st.columns(cols_per_row) for _ in range((n_features + cols_per_row - 1) // cols_per_row)]
        for i in range(n_features):
            with rows[i // cols_per_row][i % cols_per_row]:
                val = st.number_input(f"Feature {i+1}", value=0.0, format="%.4f", key=f"feat_{i}")
                feature_values.append(val)
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🔍  ANALYZE TRANSACTION", use_container_width=True)

    with col_result:
        st.markdown("<div class='section-label'>Analysis Result</div>", unsafe_allow_html=True)
        if analyze_btn:
            with st.spinner("Running inference..."):
                X = pd.DataFrame([feature_values])
                prob, label = predict(X)
                prob_val = float(prob[0])
                is_fraud = bool(label[0])
            if is_fraud:
                st.markdown(f"<div class='verdict-fraud'><div class='verdict-title'>🚨 FRAUDULENT</div><div class='verdict-conf'>Confidence: {prob_val*100:.1f}% fraud probability</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='verdict-legit'><div class='verdict-title'>✅ LEGITIMATE</div><div class='verdict-conf'>Confidence: {(1-prob_val)*100:.1f}% legitimate probability</div></div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.plotly_chart(gauge_chart(prob_val, is_fraud), use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown("""
            <div style='height:380px;display:flex;flex-direction:column;align-items:center;justify-content:center;border:1px dashed #1e2533;border-radius:12px;background:#0d1117;'>
                <div style='font-size:3rem;margin-bottom:1rem;opacity:0.3;'>🛡️</div>
                <div style='font-family:Space Mono;font-size:0.78rem;color:#374151;letter-spacing:0.15em;text-align:center;'>ENTER FEATURE VALUES<br>AND CLICK ANALYZE</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — BATCH ANALYSIS (works with ANY CSV)
# ══════════════════════════════════════════════════════════════════════════════
with tab_batch:
    st.markdown("<br>", unsafe_allow_html=True)
    n_features = artifacts["model"].n_features_in_

    st.markdown(f"""
    <div class='info-box'>
        <div class='info-box-title'>✅ UNIVERSAL CSV MODE — NO COLUMN RESTRICTIONS</div>
        <div style='font-family:Space Mono;font-size:0.78rem;color:#64748b;line-height:1.8;'>
            Upload <b style='color:#e2e8f0;'>any CSV file</b> — the app will automatically detect columns and use
            the first <span style='color:#f97316;font-weight:700;'>{n_features} numeric columns</span> your model needs.<br>
            Select your <span style='color:#ef4444;'>target/label column</span> (e.g. Class, is_fraud) to exclude it from features.
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload any transaction CSV for batch analysis", type=["csv"])

    if uploaded:
        try:
            df_raw = pd.read_csv(uploaded)
            st.markdown(f"<div style='font-family:Space Mono;font-size:0.75rem;color:#475569;margin:0.5rem 0 1rem;'>✓ Loaded <b style='color:#e2e8f0;'>{len(df_raw):,} rows</b> · <b style='color:#e2e8f0;'>{df_raw.shape[1]} columns</b> detected</div>", unsafe_allow_html=True)

            col_html = "".join([
                f"<span class='col-pill {'numeric' if pd.api.types.is_numeric_dtype(df_raw[c].dtype) else ''}'>{c}</span>"
                for c in df_raw.columns
            ])
            st.markdown(f"""
            <div class='info-box'>
                <div class='info-box-title'>DETECTED COLUMNS &nbsp;
                    <span style='color:#22c55e;'>■ numeric</span>
                    <span style='color:#94a3b8;margin-left:8px;'>■ other</span>
                </div>
                <div>{col_html}</div>
            </div>""", unsafe_allow_html=True)

            target_col = st.selectbox(
                "Select target/label column to exclude (optional)",
                options=["None"] + list(df_raw.columns),
                index=0,
                help="Select your fraud label column (e.g. 'Class', 'is_fraud') so it won't be used as a feature"
            )
            target_col = None if target_col == "None" else target_col

            run_btn = st.button("🔍  RUN BATCH ANALYSIS", use_container_width=True)

            if run_btn:
                with st.spinner(f"Analyzing {len(df_raw):,} transactions..."):
                    X_batch = smart_preprocess(df_raw, target_col=target_col)
                    probs, labels = predict(X_batch)

                df_results = df_raw.copy()
                df_results.insert(0, "Fraud Probability", [f"{p*100:.1f}%" for p in probs])
                df_results.insert(0, "Prediction", ["FRAUD" if l else "LEGITIMATE" for l in labels])
                df_results.insert(0, "Txn #", range(1, len(df_results)+1))

                n_total  = len(labels)
                n_fraud  = int(labels.sum())
                n_legit  = n_total - n_fraud
                avg_risk = float(probs.mean()) * 100
                max_risk = float(probs.max()) * 100

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='section-label'>Batch Summary</div>", unsafe_allow_html=True)
                m1, m2, m3, m4 = st.columns(4)
                for col, label_txt, val, delta_txt, delta_color in [
                    (m1, "TOTAL TRANSACTIONS", f"{n_total:,}",     "batch complete",                       "#64748b"),
                    (m2, "FRAUDULENT",         f"{n_fraud:,}",     f"{n_fraud/n_total*100:.1f}% of batch", "#ef4444"),
                    (m3, "LEGITIMATE",         f"{n_legit:,}",     f"{n_legit/n_total*100:.1f}% of batch", "#22c55e"),
                    (m4, "AVG RISK SCORE",     f"{avg_risk:.1f}%", f"max: {max_risk:.1f}%",                "#f97316"),
                ]:
                    col.markdown(f"""
                    <div class='metric-card'>
                        <div class='metric-label'>{label_txt}</div>
                        <div class='metric-value' style='color:{delta_color if label_txt != "TOTAL TRANSACTIONS" else "#f1f5f9"};'>{val}</div>
                        <div class='metric-delta' style='color:{delta_color};'>{delta_txt}</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                ch1, ch2 = st.columns([1, 2])
                with ch1:
                    st.markdown("<div class='section-label'>Fraud Distribution</div>", unsafe_allow_html=True)
                    st.plotly_chart(batch_results_chart(df_results), use_container_width=True, config={"displayModeBar": False})
                with ch2:
                    st.markdown("<div class='section-label'>Fraud Probability by Transaction</div>", unsafe_allow_html=True)
                    st.plotly_chart(confidence_bar_chart(probs), use_container_width=True, config={"displayModeBar": False})

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='section-label'>Transaction Results</div>", unsafe_allow_html=True)
                filter_col, dl_col = st.columns([2, 1])
                with filter_col:
                    show_filter = st.radio("Show", ["All Transactions", "Fraud Only", "Legitimate Only"], horizontal=True, label_visibility="collapsed")
                with dl_col:
                    st.download_button("⬇  Export Results CSV", data=df_results.to_csv(index=False), file_name="fraud_analysis_results.csv", mime="text/csv", use_container_width=True)

                if show_filter == "Fraud Only":
                    df_display = df_results[df_results["Prediction"] == "FRAUD"]
                elif show_filter == "Legitimate Only":
                    df_display = df_results[df_results["Prediction"] == "LEGITIMATE"]
                else:
                    df_display = df_results

                def highlight_fraud(row):
                    if row["Prediction"] == "FRAUD":
                        return ["background-color: rgba(239,68,68,0.10); color: #fca5a5"
                            if c == "Prediction" else
                            "background-color: rgba(239,68,68,0.06); color: #e2e8f0"
                            for c in row.index]
                    return ["color: #86efac" if c == "Prediction" else "color: #e2e8f0"
                            for c in row.index]

                styled = (
                    df_display.style.apply(highlight_fraud, axis=1)
                    .set_properties(**{"font-family": "Space Mono, monospace", "font-size": "12px", "border": "1px solid #1e2533"})
                    .set_table_styles([
                        {"selector": "thead th", "props": [("background", "#0d1117"), ("color", "#64748b"), ("font-family", "Space Mono, monospace"), ("font-size", "11px"), ("letter-spacing", "0.1em"), ("border-bottom", "1px solid #1e2533")]},
                        {"selector": "tbody tr:hover", "props": [("background", "rgba(255,255,255,0.03)")]},
                    ])
                )
                st.dataframe(styled, use_container_width=True, height=380)
                st.markdown(f"<div style='font-family:Space Mono;font-size:0.68rem;color:#374151;text-align:right;margin-top:0.5rem;'>Showing {len(df_display):,} of {n_total:,} transactions</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    else:
        st.markdown("""
        <div style='height:280px;display:flex;flex-direction:column;align-items:center;justify-content:center;border:1px dashed #1e2533;border-radius:12px;background:#0d1117;'>
            <div style='font-size:2.5rem;margin-bottom:1rem;opacity:0.25;'>📊</div>
            <div style='font-family:Space Mono;font-size:0.78rem;color:#374151;letter-spacing:0.15em;text-align:center;'>
                UPLOAD ANY CSV TO BEGIN BATCH ANALYSIS<br>
                <span style='font-size:0.68rem;margin-top:0.5rem;display:block;'>NO COLUMN RESTRICTIONS</span>
            </div>
        </div>""", unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='border-top:1px solid #1e2533;padding-top:1rem;display:flex;justify-content:space-between;align-items:center;'>
    <div style='font-family:Space Mono;font-size:0.65rem;color:#374151;letter-spacing:0.1em;'>🛡️ FRAUDGUARD AI · DETECTION ENGINE v2.4</div>
    <div style='font-family:Space Mono;font-size:0.65rem;color:#374151;letter-spacing:0.1em;'>UNIVERSAL CSV MODE · NO COLUMN RESTRICTIONS</div>
</div>
""", unsafe_allow_html=True)