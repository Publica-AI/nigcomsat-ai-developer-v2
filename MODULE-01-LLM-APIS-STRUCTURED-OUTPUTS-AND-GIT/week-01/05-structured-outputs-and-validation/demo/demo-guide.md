# Demo Guide - Structured Outputs & Validation
**Module 1, Topic 5 | Estimated duration: 35-40 minutes**

---

## What This Demo Teaches

- Defining a data contract once with Pydantic and using it for both the API schema and the validation
- Calling the model with structured output mode (`response_format=<PydanticModel>`) instead of asking for JSON in the prompt
- Adding a business-rule validator for something the schema's types cannot express
- Building a retry loop that feeds a validation error back to the model
- Letting a genuinely absent field come back as `None` instead of forcing a guess

---

## Setup

1. Open the Topic 5 demo folder and open `notebook.ipynb`
2. Confirm `openai`, `python-dotenv` and `pydantic` are installed
3. Confirm the `.env` file (copied from the repository root `.env.example`) has `OPENAI_API_KEY`, `MODEL_NAME` and `OPENAI_BASE_URL` set — this topic does not need `EMBEDDING_API_KEY`
4. Run the import/setup cell and confirm it prints `Client ready.` with a model name
5. Keep `shared/synthetic-mce-corpus/ANSWER-KEY.md` open on your own machine — it is instructor-only and gives the confirmed field values used to sanity-check the demo live

---

## Demo Steps

### Part 1 - Why Prose Isn't a Contract (5 min)

Before opening the notebook, ask the model the same question three different ways in a scratch cell or the browser playground: "What is the severity and affected link for this incident?" Show that the three replies come back shaped differently.

> "If your code did `response.split(':')[1]` against all three of these, how many would actually work? Maybe one. This is why we don't parse chat replies by hand."

### Part 2 - The Source Document (5 min)

Run the setup cells, then the cell that defines `INCIDENT_REPORT`.

> "This is our synthetic NOC incident report — `NOC-INC-2026-0417`. Notice it has a summary, a details section, and a timeline. We're going to pull structured fields out of this, and later in Topic 6 we'll come back and check whether the summary is even telling the truth about itself."

Do not resolve the "approximately two hours" line yet if anyone notices it — flag that it is coming back in Topic 6.

### Part 3 - One Class, Two Jobs (7 min)

Run the `IncidentExtract` class cell.

> "This one class does two jobs. Its schema builds the contract we send to the API. The class itself validates whatever comes back. Watch — this print statement shows you the exact JSON Schema Pydantic generated for us, so you never have to write it by hand."

Run `IncidentExtract.model_json_schema()` and point out the `enum` on `severity` and the `required` list.

### Part 4 - The Structured Output Call (7 min)

Run the `client.chat.completions.parse(...)` cell.

> "We pass the class straight in as `response_format`. Look at what comes back — `type(incident)` is already `IncidentExtract`, not a dict, not a string. No `json.loads()`, no stripping markdown fences."

If the severity or customer count in the printed result doesn't match the answer key (P2, KU-HUB1-GW3, 3 customers), stop and investigate before moving on — this is the one live-model step in this topic and it must be checked against the answer key before class.

### Part 5 - Breaking It on Purpose (7 min)

Run the `bad_reply` / `ValidationError` cell.

> "Structured output mode guarantees the *shape*. It does not guarantee the model can't hand you a technically-valid but nonsensical number. Here I'm simulating a reply where `customers_affected` came back as -3 — still an int, still schema-legal, still wrong."

Read the printed `ValidationError` aloud, field by field.

> "This is the exact message our retry loop is going to feed back to the model in a second."

### Part 6 - The Retry Loop (6 min)

Run the `extract_with_retry` cell against the real incident report.

> "In this run it should succeed on attempt 1 — the real model output is fine. The loop exists for the day it isn't: it catches the validation error, appends it as a correction message, and tries again, capped at three attempts. After that, it raises — a human looks at it, we don't retry forever and we don't quietly accept bad data."

### Part 7 - Letting the Model Say "I Don't Know" (5 min)

Run the `SHORT_REPORT` cell.

> "This second report is still under investigation — there's genuinely no root cause stated. Watch `root_cause` come back as `null`, not an invented explanation. That's only possible because we made the field `Optional` and told the model explicitly, in the system prompt, that `null` is an acceptable answer."

The `assert incident_2.root_cause is None` line should pass silently — if it doesn't, the model is guessing, and that is worth stopping on as a real bug, not moving past quietly.

### Close (3 min)

> "Everything you just built — the `IncidentExtract` class and the `extract_with_retry` function — is not a throwaway example. Topic 6 tests this exact extractor against known answers, including that 'two hours' claim we skipped over. Keep this notebook open."

---

## Common Issues

- **`model_dump_json` not found** — the class was probably built with an older Pydantic v1 install; confirm `pydantic>=2` is installed.
- **`response_format` rejected by the API** — confirm `MODEL_NAME` points at a model that supports structured output mode; this was confirmed for the course model before the track was built, so a rejection here usually means a wrong or stale `.env` value.
- **The live call in Part 4 doesn't match the answer key** — check the exact wording of the system prompt hasn't drifted from the notebook; a small prompt change can shift which fields the model reports.
