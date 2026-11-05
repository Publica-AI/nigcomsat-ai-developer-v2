"""Conversation history management and query rewriting.

Teaches: follow-up rewriting, history windowing, token budgets.
Topic 4 of the module.
"""

import re

from citations import llm_client, MODEL, get_cited_answer

# ── Query rewriting ─────────────────────────────────────────────────

REWRITE_PROMPT = """Given a conversation between an employee and an HR assistant,
rewrite the employee's latest message as a standalone search query.

Rules:
1. Replace pronouns (it, that, those, they) with the specific nouns they refer to.
2. Include key details from the conversation (amounts, dates, document names).
3. Output ONLY the rewritten query — no explanation, no quotation marks.
4. If the message is already a standalone question, return it unchanged."""


def format_rewrite_input(history, latest_message):
    """Format conversation history + latest message for the rewriter."""
    lines = ["Conversation so far:"]
    for msg in history:
        role = "Employee" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content']}")
    lines.append(f"\nLatest message to rewrite:\n{latest_message}")
    return "\n".join(lines)


def rewrite_query(history, follow_up):
    """Rewrite a follow-up into a standalone search query using the LLM."""
    rewrite_input = format_rewrite_input(history, follow_up)
    response = llm_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": REWRITE_PROMPT},
            {"role": "user", "content": rewrite_input},
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content.strip()


# ── History utilities ───────────────────────────────────────────────


def get_history_window(history, max_pairs=5):
    """Return the last N user-assistant pairs from history."""
    max_messages = max_pairs * 2
    return history[-max_messages:]


def strip_citations(answer_text):
    """Remove [Source N] markers and the Sources block from an answer."""
    text = re.sub(r"\[Source\s*\d*\]", "", answer_text)
    text = re.split(r"\n\s*Sources?:", text)[0]
    text = re.sub(r"  +", " ", text).strip()
    return text


def estimate_tokens(text):
    """Rough estimate: 1 token ~ 4 characters."""
    return len(text) // 4


def trim_history(history, max_tokens=5000):
    """Remove oldest messages until history fits the token budget."""
    trimmed = list(history)
    while trimmed and estimate_tokens(str(trimmed)) > max_tokens:
        trimmed.pop(0)
    return trimmed


# ── Full multi-turn pipeline ───────────────────────────────────────


def chat(message, history, max_pairs=5, max_history_tokens=5000):
    """Rewrite follow-ups, retrieve cited answer, update history."""
    if history:
        window = get_history_window(history, max_pairs=max_pairs)
        window = trim_history(window, max_tokens=max_history_tokens)
        search_query = rewrite_query(window, message)
    else:
        search_query = message

    result = get_cited_answer(search_query)

    history.append({"role": "user", "content": message})
    clean_answer = strip_citations(result["answer"])
    history.append({"role": "assistant", "content": clean_answer})

    result["original_message"] = message
    result["search_query"] = search_query
    result["was_rewritten"] = (search_query != message)
    return result
