import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Import database logging helpers
import sys
sys.path.append(str(Path(__file__).resolve().parent))
from database.db import create_table, log_result

# Page configuration
st.set_page_config(
    page_title="CivicGuard Console",
    page_icon="🛡️",
    layout="wide"
)

# Apply premium modern styling (Glassmorphism + custom fonts + smooth gradients)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700;800&display=swap');

    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #e2e8f0;
    }

    /* Welcome Banner Glass Effect */
    .welcome-banner {
        background: linear-gradient(135deg, rgba(31, 41, 55, 0.8) 0%, rgba(17, 24, 39, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 35px;
        margin-bottom: 30px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    .welcome-banner::before {
        content: '';
        position: absolute;
        top: -60px;
        right: -60px;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0) 70%);
        border-radius: 50%;
    }
    .welcome-banner h1 {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 2.3rem;
        margin: 0 0 10px 0;
        background: linear-gradient(90deg, #ffffff 0%, #c7d2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .welcome-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        max-width: 800px;
        line-height: 1.6;
        margin-bottom: 20px;
    }

    /* Metric Cards Redesign */
    div[data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.45) !important;
        backdrop-filter: blur(12px) saturate(180%);
        -webkit-backdrop-filter: blur(12px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 24px 20px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 15px 35px rgba(99, 102, 241, 0.15);
    }

    /* Metric Label Styling */
    div[data-testid="metric-container"] label {
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8 !important;
    }

    /* Section Cards Styling */
    .card-container {
        background: rgba(30, 41, 59, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    }

    /* Interactive Elements Styling */
    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        color: #f1f5f9 !important;
        font-size: 1.05rem !important;
        padding: 15px !important;
        transition: border-color 0.3s ease;
    }
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }

    /* Glowing Button */
    button[data-testid="baseButton-secondary"] {
        background: linear-gradient(90deg, #4f46e5 0%, #6366f1 50%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 24px !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35) !important;
    }
    button[data-testid="baseButton-secondary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

DB_PATH = Path(__file__).resolve().parent / "database" / "civicguard.db"

# Initialize SQLite database table
create_table()

# Load model and tokenizer (cached so it loads only once)
MODEL_PATH = Path(__file__).resolve().parent / "data" / "civicguard_distilbert"

@st.cache_resource
def load_model_and_tokenizer():
    local_weights = MODEL_PATH / "model.safetensors"
    if local_weights.exists():
        tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
        model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_PATH))
    else:
        fallback_model = "unitary/toxic-bert"
        tokenizer = AutoTokenizer.from_pretrained(fallback_model)
        model = AutoModelForSequenceClassification.from_pretrained(fallback_model)
    
    model.eval()
    return tokenizer, model

try:
    tokenizer, model = load_model_and_tokenizer()
    is_fallback = not (MODEL_PATH / "model.safetensors").exists()
except Exception as e:
    st.error(f"Error loading AI Model: {e}")
    st.stop()

# Helper mapping to standardize index labels to human-readable categories
label_mapping = {
    "LABEL_0": "toxic",
    "LABEL_1": "severe_toxic",
    "LABEL_2": "obscene",
    "LABEL_3": "threat",
    "LABEL_4": "insult",
    "LABEL_5": "identity_hate",
    "toxic": "toxic",
    "severe_toxic": "severe_toxic",
    "obscene": "obscene",
    "threat": "threat",
    "insult": "insult",
    "identity_hate": "identity_hate"
}

def predict_text(text):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )
    inputs.pop("token_type_ids", None)

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.sigmoid(outputs.logits)[0]
    scores = {}
    for i, score in enumerate(probabilities):
        label_name = model.config.id2label.get(i, f"LABEL_{i}")
        mapped_name = label_mapping.get(label_name, label_name)
        scores[mapped_name] = round(float(score), 4)
    return scores

# Fetch database metrics
try:
    conn = sqlite3.connect(str(DB_PATH))
    total_comments = pd.read_sql("SELECT COUNT(*) as count FROM moderation_logs", conn).iloc[0]["count"]
    blocked_comments = pd.read_sql("SELECT COUNT(*) as count FROM moderation_logs WHERE decision='BLOCKED'", conn).iloc[0]["count"]
    approved_comments = pd.read_sql("SELECT COUNT(*) as count FROM moderation_logs WHERE decision='APPROVED'", conn).iloc[0]["count"]
    
    # Calculate overall civility score
    if total_comments > 0:
        civility_score = round((approved_comments / total_comments) * 100, 1)
    else:
        civility_score = 100.0
except Exception as e:
    st.error(f"Database Error: {e}")
    st.stop()

# Welcome Banner Markup
model_badge_style = "background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.4); color: #f87171;" if is_fallback else "background: rgba(16, 185, 129, 0.2); border: 1px solid rgba(16, 185, 129, 0.4); color: #34d399;"
model_status_text = "unitary/toxic-bert (HuggingFace Hub)" if is_fallback else "DistilBERT (Local Model)"

st.markdown(
    f"""
    <div class="welcome-banner">
        <h1>🛡️ Welcome to CivicGuard Console</h1>
        <div class="welcome-subtitle">
            An advanced AI-powered content moderation console. Monitor community civility trends, run live neural inference, and audit moderation logs in real-time.
        </div>
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
            <span style="background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(99, 102, 241, 0.4); color: #a5b4fc; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; letter-spacing: 0.02em;">
                🟢 Active Session
            </span>
            <span style="{model_badge_style} padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; letter-spacing: 0.02em;">
                🧠 {model_status_text}
            </span>
            <span style="background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); color: #cbd5e1; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; letter-spacing: 0.02em;">
                📈 Civility Index: {civility_score}%
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Render main KPIs
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    st.metric("Total Moderated", f"{int(total_comments):,}")
with kpi_col2:
    st.metric("Approved Comments", f"{int(approved_comments):,}")
with kpi_col3:
    st.metric("Blocked Comments", f"{int(blocked_comments):,}")
with kpi_col4:
    st.metric("Civility Index Score", f"{civility_score}%", help="Percentage of total comments marked APPROVED.")

st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# Layout division: Column 1 for input, Column 2 for charts
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.markdown("<div class='card-container'>", unsafe_allow_html=True)
    st.subheader("💡 Content Analysis Sandbox")
    text_input = st.text_area(
        "Enter message to analyze", 
        placeholder="Type a message or review comment here to check civility metrics...", 
        height=140
    )
    analyze_clicked = st.button("Moderate Content", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if analyze_clicked:
        if not text_input.strip():
            st.warning("Please enter some text to analyze.")
        else:
            with st.spinner("Executing neural inference..."):
                scores = predict_text(text_input)

            if scores["toxic"] > 0.5:
                decision = "BLOCKED"
                st.error("Decision: 🛑 BLOCKED (Toxicity Exceeds Threshold)")
            else:
                decision = "APPROVED"
                st.success("Decision: ✅ APPROVED (Message Safe)")

            # Log directly to local database
            log_result(text_input, scores, decision)

            score_df = pd.DataFrame({
                "Category": list(scores.keys()),
                "Confidence (%)": [round(v * 100, 2) for v in scores.values()]
            })

            st.markdown("<div class='card-container'>", unsafe_allow_html=True)
            st.subheader("📊 Classifier Insights")
            st.dataframe(score_df, use_container_width=True, hide_index=True)
            st.bar_chart(score_df.set_index("Category"))
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Refresh metric values instantly
            st.rerun()

with col_right:
    st.markdown("<div class='card-container'>", unsafe_allow_html=True)
    st.subheader("📈 Toxicity Severity Trend")
    
    # Load recent logs to render analytical trend graphs
    try:
        logs_df = pd.read_sql(
            """
            SELECT 
                input_text, 
                decision, 
                toxic, 
                severe_toxic, 
                obscene, 
                threat, 
                insult, 
                identity_hate, 
                timestamp 
            FROM moderation_logs 
            ORDER BY timestamp DESC 
            LIMIT 20
            """,
            conn
        )
        
        if not logs_df.empty:
            # Chronological flip
            trend_df = logs_df.iloc[::-1].copy()
            trend_df["Sequence"] = range(1, len(trend_df) + 1)
            
            st.caption("Tracking toxicity levels across recent moderation runs (last 20 logs)")
            st.area_chart(
                trend_df.set_index("Sequence")[["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]],
                use_container_width=True
            )
        else:
            st.info("No logs available yet to render analytical trend lines. Analyze some text to build graphs!")
    except Exception as e:
        st.error(f"Error loading analytical graphs: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# Full-width section for historical audits
st.markdown("<div class='card-container'>", unsafe_allow_html=True)
st.subheader("📋 Historical Audit Logs")
if not logs_df.empty:
    # Custom format the dataframe for sleekness
    styled_logs = logs_df.copy()
    styled_logs["decision"] = styled_logs["decision"].apply(lambda x: "🛑 BLOCKED" if x == "BLOCKED" else "✅ APPROVED")
    st.dataframe(
        styled_logs, 
        use_container_width=True, 
        hide_index=True
    )
else:
    st.info("Audits will populate here once texts are analyzed.")
st.markdown("</div>", unsafe_allow_html=True)

conn.close()
