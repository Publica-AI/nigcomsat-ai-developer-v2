"""NovaNet HR Assistant — Streamlit chat interface.

Calls the retrieval pipeline from Topics 2-4 directly via pipeline.py.
In the module demo, this switches to HTTP calls to a FastAPI backend.
"""

import streamlit as st
from pipeline import chat

# ── Page config (must be the first Streamlit call) ───────────────────

st.set_page_config(page_title="NovaNet HR Assistant", page_icon="\U0001F4BC")

# ── Sidebar: login ──────────────────────────────────────────────────

with st.sidebar:
    st.title("NovaNet HR")

    if "username" not in st.session_state:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Log in"):
            if username and password:
                st.session_state.username = username
                st.rerun()
            else:
                st.warning("Enter both username and password.")
    else:
        st.success(f"Logged in as {st.session_state.username}")
        if st.button("Log out"):
            for key in ["username", "messages", "pipeline_history"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# ── Main area ────────────────────────────────────────────────────────

st.title("NovaNet HR Assistant")
st.caption("Ask any question about HR policies, leave, benefits, or onboarding.")

# Guard: must be logged in
if "username" not in st.session_state:
    st.info("Please log in using the sidebar to start asking questions.")
    st.stop()

# Initialise session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pipeline_history" not in st.session_state:
    st.session_state.pipeline_history = []

# ── Display previous messages ────────────────────────────────────────

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Citations (assistant messages only)
        if msg.get("citations"):
            with st.expander("Sources cited"):
                for cite in msg["citations"]:
                    st.markdown(
                        f"**{cite['key']}** [{cite['doc_id']}] "
                        f"{cite['section']} — _{cite['status'].lower()}_"
                    )

        # Feedback buttons (assistant messages only)
        if msg["role"] == "assistant":
            col1, col2, _ = st.columns([1, 1, 10])
            with col1:
                if st.button("\U0001F44D", key=f"up_{i}"):
                    st.toast("Thanks for the feedback!")
            with col2:
                if st.button("\U0001F44E", key=f"down_{i}"):
                    st.toast("Thanks — we'll review this answer.")

# ── Handle new input ─────────────────────────────────────────────────

if question := st.chat_input("e.g., How many days of annual leave do I get?"):
    # Show the employee's message
    st.chat_message("user").write(question)

    with st.chat_message("assistant"):
        try:
            # Call the pipeline with a loading spinner
            with st.spinner("Searching HR documents..."):
                result = chat(question, st.session_state.pipeline_history)

            # Render the answer
            st.markdown(result["answer"])

            # Render citations if the answer was not refused
            citations = []
            if not result["refused"] and result["citations"]:
                citations = result["citations"]
                with st.expander("Sources cited"):
                    for cite in citations:
                        st.markdown(
                            f"**{cite['key']}** [{cite['doc_id']}] "
                            f"{cite['section']} — _{cite['status'].lower()}_"
                        )

            # Feedback buttons
            msg_idx = len(st.session_state.messages) + 1
            col1, col2, _ = st.columns([1, 1, 10])
            with col1:
                if st.button("\U0001F44D", key=f"up_{msg_idx}"):
                    st.toast("Thanks for the feedback!")
            with col2:
                if st.button("\U0001F44E", key=f"down_{msg_idx}"):
                    st.toast("Thanks — we'll review this answer.")

            # Store for display on re-run
            st.session_state.messages.append(
                {"role": "user", "content": question}
            )
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "citations": citations,
            })

        except Exception:
            st.error(
                "The HR assistant is temporarily unavailable. "
                "Please try again in a few minutes."
            )
