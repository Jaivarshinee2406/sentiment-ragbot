"""
Streamlit UI for the sentiment RAG bot. Runs entirely on your local
free models - no API key, no MySQL required.

Usage:
    streamlit run app/streamlit_app.py
"""
import csv
import sys
from pathlib import Path

import streamlit as st

# Allow running `streamlit run app/streamlit_app.py` from the project root
sys.path.append(str(Path(__file__).parent.parent))

from app.sentiment import classify_ticket
from app.embeddings import index_ticket
from app.rag import answer_question

st.set_page_config(page_title="Support Ticket Sentiment RAG Bot", layout="wide")
st.title("🎫 Support Ticket Sentiment RAG Bot")

if "analyzed_tickets" not in st.session_state:
    st.session_state.analyzed_tickets = []

tab1, tab2, tab3 = st.tabs(["Analyze a ticket", "Ask a question (RAG)", "Bulk load sample data"])

# --- Tab 1: analyze a single ticket ---
with tab1:
    st.subheader("Classify a single ticket")
    ticket_text = st.text_area("Paste a support ticket:", height=120,
                                placeholder="e.g. My order arrived damaged and nobody replied to my emails.")

    if st.button("Analyze", type="primary"):
        if ticket_text.strip():
            with st.spinner("Classifying..."):
                result = classify_ticket(ticket_text)
                ticket_id = f"ui-{len(st.session_state.analyzed_tickets)}"
                index_ticket(ticket_id, ticket_text, result)
                st.session_state.analyzed_tickets.append({"text": ticket_text, **result})

            col1, col2, col3 = st.columns(3)
            sentiment_emoji = {"positive": "😊", "neutral": "😐", "negative": "😠"}
            col1.metric("Sentiment", f"{sentiment_emoji.get(result['sentiment'], '')} {result['sentiment']}")
            col2.metric("Category", result["category"])
            col3.metric("Confidence", f"{result['confidence']:.0%}")
            st.info(f"**Summary:** {result['summary']}")
        else:
            st.warning("Please paste a ticket first.")

    if st.session_state.analyzed_tickets:
        st.subheader("Analyzed so far")
        st.dataframe(st.session_state.analyzed_tickets, use_container_width=True)

# --- Tab 2: RAG question answering ---
with tab2:
    st.subheader("Ask a question about indexed tickets")
    st.caption("Answers are generated from tickets you've analyzed or bulk-loaded (Chroma index).")

    question = st.text_input("Your question:", placeholder="e.g. What are customers unhappy about?")
    sentiment_filter = st.selectbox("Filter by sentiment (optional):",
                                     ["Any", "positive", "neutral", "negative"])
    n_results = st.slider("Number of tickets to retrieve:", 1, 10, 5)

    if st.button("Ask", type="primary"):
        if question.strip():
            with st.spinner("Retrieving relevant tickets and generating an answer..."):
                filt = None if sentiment_filter == "Any" else sentiment_filter
                result = answer_question(question, n_results=n_results, sentiment_filter=filt)
            st.success(result["answer"])
            with st.expander("Sources used"):
                for src in result["sources"]:
                    st.write(src)
        else:
            st.warning("Please type a question first.")

# --- Tab 3: bulk load sample data ---
with tab3:
    st.subheader("Bulk load and index sample tickets")
    csv_path = Path(__file__).parent.parent / "data" / "sample_tickets.csv"

    if not csv_path.exists():
        st.error(f"No sample data found at {csv_path}. Run: python data/generate_sample_data.py")
    else:
        with open(csv_path, newline="", encoding="utf-8") as f:
            all_rows = list(csv.DictReader(f))
        st.write(f"Found {len(all_rows)} sample tickets in `data/sample_tickets.csv`.")
        n_to_load = st.slider("How many to classify + index?", 5, len(all_rows), 20)

        if st.button("Load and index", type="primary"):
            progress = st.progress(0)
            status = st.empty()
            for i, row in enumerate(all_rows[:n_to_load]):
                result = classify_ticket(row["text"])
                index_ticket(row["ticket_id"], row["text"], result)
                status.text(f"Processed {i+1}/{n_to_load}: {result['sentiment']} / {result['category']}")
                progress.progress((i + 1) / n_to_load)
            st.success(f"Indexed {n_to_load} tickets. Go to the 'Ask a question' tab to query them.")
