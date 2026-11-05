# Demo Guide - Testing for Hallucination & Verification Habits
**Module 1, Topic 6 | Estimated duration: 25-30 minutes**

---

## What This Demo Teaches

- Two independent checks, not one pipeline: catching a hallucination needs no schema, and proving a validator needs no API call
- Building a human-verified answer key before writing any test code
- Being honest about a live result instead of scripting one: this model reliably gets both traps right, and that's part of the lesson, not a failed demo
- Writing a short, plain `test_extraction.py` with two independent tests and running it with `pytest` from the terminal — the test the Week 1 deliverable requires

**Before you teach this:** run the two live cells (duration question, manufacturer question) yourself first. As of this writing they consistently return the correct answer (98 minutes; "not mentioned"). If your model or gateway ever answers differently, that is not a broken demo — it's the more dramatic version of the same lesson. Either way, say what actually happened; don't narrate a failure that isn't occurring on screen.

---

## Setup

1. Open the Topic 6 demo folder and open `notebook.ipynb`
2. Confirm `openai`, `python-dotenv`, `pydantic` and `pytest` are installed
3. Confirm `.env` is present with `OPENAI_API_KEY`, `MODEL_NAME` and `OPENAI_BASE_URL`
4. Have a terminal open alongside the notebook — the last part of this demo runs `pytest` from the command line, not from a notebook cell

---

## Demo Steps

### Part 1 - Two Kinds of Hallucination, No Schema (4 min)

> "Topic 5 was about getting a guaranteed shape back. Catching a hallucination has nothing to do with shape. Two plain questions, two plain-text answers — that's the whole API surface we need."

Run the setup and `SHIFT_NOTE` cells. Point out how short the shift note is compared to Topic 5's full incident report — no severity, no customers affected, nothing this topic doesn't ask about.

### Part 2 - Asking Both Questions (6 min)

Run the duration-question cell, then the manufacturer-question cell.

> "One question has a precise correct answer hiding behind a vaguer one. The other has no answer in the document at all. Watch what comes back for each."

### Part 3 - Building the Answer Key, and Checking It (6 min)

Before running the comparison cell, do the arithmetic on the board: 03:52 minus 02:14.

> "We didn't ask the model what the right answer is — that would be asking the fox to guard the henhouse. We read the timeline ourselves. 98 minutes, decided before we looked at what the model said."

Run the `extract_minutes` / comparison cell.

### Part 4 - Reporting What Actually Happens (5 min)

Run the **We Actually Tested This** cell content live, or rerun the two question cells a few times in front of the class.

> "When this was built, the duration question came back 98 six times out of six, and the manufacturer question came back 'not mentioned' four times out of four. If you're seeing the same thing right now, that's not a failed demo — that's a well-behaved model. Let's talk about why we still wrote a test for it."

If your run genuinely does produce a wrong answer, say that plainly instead — it makes the next part even more concrete.

### Part 5 - Why the Test Still Matters (4 min)

> "This model, on this gateway, right now, gets both of these right. None of that is guaranteed to stay true — this exact course had its gateway's model swapped out from under it mid-build, with no code change on our end. The test isn't proof of a bug we found. It's insurance against one we haven't seen yet."

### Part 6 - Proving the Validator, Separately (4 min)

Run the `IncidentExtract` / `pytest.raises` cell.

> "This one has nothing to do with anything we just asked the model. No API call at all — just Pydantic checking its own rule. One test depends on infrastructure we don't control. This one doesn't. Knowing which is which is the actual skill."

### Part 7 - Writing and Running the Test File (5 min)

Run the `%%writefile test_extraction.py` cell, then switch to the terminal.

```
cd <this demo folder>
pytest test_extraction.py -v
```

> "Two tests, one command. This is the test the Week 1 deliverable asks for. If `test_duration_not_copied_from_summary` ever fails on you, don't just rerun it and move on — that's the exact scenario Slide 6 warned you about."

### Close (2 min)

> "Two small checks. Neither one needed a schema, and neither one needed to fail for the lesson to matter. You test for what's possible, not just for what you've already seen go wrong."

---

## Common Issues

- **`pytest: command not found`** — `pytest` wasn't installed in the active virtual environment; `pip install pytest` and retry
- **The live answers genuinely come back wrong** — great, tell the class exactly that; it's a real, live demonstration of the failure mode, not a script to follow
- **`extract_minutes` raises "No number found"** — the model replied in words instead of digits (e.g. "ninety-eight"); tighten the prompt's "Reply with just the number" instruction if this happens often
- **`test_duration_not_copied_from_summary` fails intermittently but `test_negative_customers_rejected` always passes** — expected and fine; only the first test depends on the live API being up and the model answering consistently, which is precisely the distinction Part 6 makes
