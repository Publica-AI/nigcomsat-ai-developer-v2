"""NovaNet HR Assistant — Streamlit chat interface (authenticated).

Calls the FastAPI backend (api.py) for login, queries, and feedback.
Upgraded from Topic 5: placeholder login replaced with real auth,
feedback buttons write to the Q&A log via /feedback.
"""

import streamlit as st
import requests

API_URL = "http://localhost:8000"

# ── Page config (must be the first Streamlit call) ───────────────────

st.set_page_config(page_title="NovaNet HR Assistant", page_icon="\U0001F4BC")

# ── Sidebar: login ──────────────────────────────────────────────────

with st.sidebar:
    st.title("NovaNet HR")
    st.caption("Your questions are logged for quality monitoring.")

    if "token" not in st.session_state:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Log in"):
            if username and password:
                try:
                    resp = requests.post(
                        f"{API_URL}/login",
                        json={"username": username, "password": password},
                    )
                    if resp.ok:
                        data = resp.json()
                        st.session_state.token = data["token"]
                        st.session_state.username = data["username"]
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                except requests.ConnectionError:
                    st.error("Cannot reach the API server. Is FastAPI running?")
            else:
                st.warning("Enter both username and password.")
    else:
        st.success(f"Logged in as {st.session_state.username}")
        if st.button("Log out"):
            for key in ["token", "username", "messages"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# ── Main area ────────────────────────────────────────────────────────

st.title("NovaNet HR Assistant")
st.caption("Ask any question about HR policies, leave, benefits, or onboarding.")

# Guard: must be logged in
if "token" not in st.session_state:
    st.info("Please log in using the sidebar to start asking questions.")
    st.stop()

# Initialise session state
if "messages" not in st.session_state:
    st.session_state.messages = []

headers = {"Authorization": f"Bearer {st.session_state.token}"}

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
        if msg["role"] == "assistant" and msg.get("log_id"):
            col1, col2, _ = st.columns([1, 1, 10])
            with col1:
                if st.button("\U0001F44D", key=f"up_{i}"):
                    requests.post(
                        f"{API_URL}/feedback",
                        json={"log_id": msg["log_id"], "feedback": "positive"},
                        headers=headers,
                    )
                    st.toast("Thanks for the feedback!")
            with col2:
                if st.button("\U0001F44E", key=f"down_{i}"):
                    requests.post(
                        f"{API_URL}/feedback",
                        json={"log_id": msg["log_id"], "feedback": "negative"},
                        headers=headers,
                    )
                    st.toast("Thanks — we'll review this answer.")

# ── Handle new input ─────────────────────────────────────────────────

if question := st.chat_input("e.g., How many days of annual leave do I get?"):
    # Show the employee's message
    st.chat_message("user").write(question)

    with st.chat_message("assistant"):
        try:
            # Call the API with a loading spinner
            with st.spinner("Searching HR documents..."):
                resp = requests.post(
                    f"{API_URL}/query",
                    json={"question": question},
                    headers=headers,
                    timeout=60,
                )

            # Handle expired token
            if resp.status_code == 401:
                st.warning("Your session has expired. Please log in again.")
                for key in ["token", "username", "messages"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

            resp.raise_for_status()
            result = resp.json()

            # Render the answer
            st.markdown(result["answer"])

            # Render citations if the answer was not refused
            citations = []
            if not result.get("refused") and result.get("citations"):
                citations = result["citations"]
                with st.expander("Sources cited"):
                    for cite in citations:
                        st.markdown(
                            f"**{cite['key']}** [{cite['doc_id']}] "
                            f"{cite['section']} — _{cite['status'].lower()}_"
                        )

            # Feedback buttons
            log_id = result.get("log_id")
            msg_idx = len(st.session_state.messages) + 1
            col1, col2, _ = st.columns([1, 1, 10])
            with col1:
                if st.button("\U0001F44D", key=f"up_{msg_idx}"):
                    if log_id:
                        requests.post(
                            f"{API_URL}/feedback",
                            json={"log_id": log_id, "feedback": "positive"},
                            headers=headers,
                        )
                    st.toast("Thanks for the feedback!")
            with col2:
                if st.button("\U0001F44E", key=f"down_{msg_idx}"):
                    if log_id:
                        requests.post(
                            f"{API_URL}/feedback",
                            json={"log_id": log_id, "feedback": "negative"},
                            headers=headers,
                        )
                    st.toast("Thanks — we'll review this answer.")

            # Store for display on re-run
            st.session_state.messages.append(
                {"role": "user", "content": question}
            )
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "citations": citations,
                "log_id": log_id,
            })

        except requests.ConnectionError:
            st.error("Cannot reach the API server. Is FastAPI running?")
        except Exception:
            st.error(
                "The HR assistant is temporarily unavailable. "
                "Please try again in a few minutes."
            )
