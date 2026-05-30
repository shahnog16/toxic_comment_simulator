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
    page_title="CivicGuard",
    layout="wide"
)

DB_PATH = Path(__file__).resolve().parent / "database" / "civicguard.db"

# Initialize SQLite database table
create_table()

# Load model and tokenizer (cached so it loads only once)
MODEL_PATH = Path(__file__).resolve().parent / "data" / "civicguard_distilbert"

@st.cache_resource
def load_model_and_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
    model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_PATH))
    model.eval()
    return tokenizer, model

try:
    tokenizer, model = load_model_and_tokenizer()
except Exception as e:
    st.error(f"Error loading AI Model: {e}")
    st.stop()

label_mapping = {
    "LABEL_0": "toxic",
    "LABEL_1": "severe_toxic",
    "LABEL_2": "obscene",
    "LABEL_3": "threat",
    "LABEL_4": "insult",
    "LABEL_5": "identity_hate"
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
        scores[label_mapping[f"LABEL_{i}"]] = round(float(score), 4)
    return scores

# Title and header
st.title("CivicGuard")
st.caption("AI-Powered Content Moderation & Civility Analysis Engine")

# Fetch database metrics
try:
    conn = sqlite3.connect(str(DB_PATH))
    total_comments = pd.read_sql("SELECT COUNT(*) as count FROM moderation_logs", conn).iloc[0]["count"]
    blocked_comments = pd.read_sql("SELECT COUNT(*) as count FROM moderation_logs WHERE decision='BLOCKED'", conn).iloc[0]["count"]
    approved_comments = pd.read_sql("SELECT COUNT(*) as count FROM moderation_logs WHERE decision='APPROVED'", conn).iloc[0]["count"]
except Exception as e:
    st.error(f"Database Error: {e}")
    st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Moderated", int(total_comments))
with col2:
    st.metric("Blocked", int(blocked_comments))
with col3:
    st.metric("Approved", int(approved_comments))

# Input section
st.subheader("Content Analysis")
text_input = st.text_area("Enter text to moderate", height=120)
analyze_clicked = st.button("Analyze Content", use_container_width=True)

if analyze_clicked:
    if not text_input.strip():
        st.warning("Please enter text.")
    else:
        # Run local classification directly
        with st.spinner("Analyzing text..."):
            scores = predict_text(text_input)

        if scores["toxic"] > 0.5:
            decision = "BLOCKED"
            st.error("Decision: BLOCKED")
        else:
            decision = "APPROVED"
            st.success("Decision: APPROVED")

        # Log directly to local database
        log_result(text_input, scores, decision)

        score_df = pd.DataFrame({
            "Category": list(scores.keys()),
            "Confidence (%)": [round(v * 100, 2) for v in scores.values()]
        })

        st.subheader("Prediction Scores")
        st.dataframe(score_df, use_container_width=True, hide_index=True)
        st.bar_chart(score_df.set_index("Category"))

        # Force metric refresh
        st.rerun()

st.subheader("Recent Moderation Logs")
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
    conn.close()
    st.dataframe(logs_df, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"Error loading logs: {e}")
