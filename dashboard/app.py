import streamlit as st
import requests
import sqlite3
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="CivicGuard",
    layout="wide"
)

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "civicguard.db"

st.title("CivicGuard")
st.caption("AI-Powered Content Moderation & Civility Analysis Engine")

try:
    conn = sqlite3.connect(str(DB_PATH))

    total_comments = pd.read_sql(
        "SELECT COUNT(*) as count FROM moderation_logs",
        conn
    ).iloc[0]["count"]

    blocked_comments = pd.read_sql(
        "SELECT COUNT(*) as count FROM moderation_logs WHERE decision='BLOCKED'",
        conn
    ).iloc[0]["count"]

    approved_comments = pd.read_sql(
        "SELECT COUNT(*) as count FROM moderation_logs WHERE decision='APPROVED'",
        conn
    ).iloc[0]["count"]

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

st.subheader("Content Analysis")

text_input = st.text_area(
    "Enter text to moderate",
    height=120
)

analyze_clicked = st.button(
    "Analyze Content",
    use_container_width=True
)

if analyze_clicked:

    if not text_input.strip():
        st.warning("Please enter text.")

    else:

        try:
            response = requests.post(
                "http://127.0.0.1:8000/moderate",
                json={"text": text_input},
                timeout=10
            )

            result = response.json()

        except Exception:
            st.error(
                "Unable to connect to the CivicGuard API. Make sure FastAPI is running."
            )
            st.stop()

        scores = result["scores"]

        if result["decision"] == "BLOCKED":
            st.error("Decision: BLOCKED")
        else:
            st.success("Decision: APPROVED")

        score_df = pd.DataFrame({
            "Category": list(scores.keys()),
            "Confidence (%)": [
                round(v * 100, 2)
                for v in scores.values()
            ]
        })

        st.subheader("Prediction Scores")

        st.dataframe(
            score_df,
            use_container_width=True,
            hide_index=True
        )

        st.bar_chart(
            score_df.set_index("Category")
        )

st.subheader("Recent Moderation Logs")

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

st.dataframe(
    logs_df,
    use_container_width=True,
    hide_index=True
)