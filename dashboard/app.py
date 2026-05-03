import streamlit as st
import requests
import sqlite3
import pandas as pd

st.title("CivicGuard — Content Moderation Dashboard")
st.markdown("---")

# Input section
st.subheader("Analyze a Comment")

col1, col2 = st.columns([2, 1])

with col1:
    text_input = st.text_area("Enter text to moderate:")

with col2:
    st.markdown("")
    st.markdown("")
    analyze_clicked = st.button("Analyze")

result_container = st.container()

if analyze_clicked:
    if text_input:
        response = requests.post(
            "http://127.0.0.1:8000/moderate",
            json={"text": text_input}
        )
        result = response.json()

        with result_container:
            if result['decision'] == "BLOCKED":
                st.error("🚫 BLOCKED")
            else:
                st.success("✅ APPROVED")

            st.subheader("Toxicity Scores")
            scores = result['scores']
            st.bar_chart(scores)

    else:
        with result_container:
            st.warning("Please enter some text first")

st.markdown("---")

# Show recent logs from database
st.subheader("Recent Moderation Logs")
conn = sqlite3.connect('../database/civicguard.db')
df = pd.read_sql(
    "SELECT * FROM moderation_logs ORDER BY timestamp DESC LIMIT 20",
    conn
)
conn.close()
st.dataframe(df)