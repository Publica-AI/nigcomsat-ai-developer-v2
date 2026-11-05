# MCE Compliance Notice Intake — A Validated Extraction Pipeline

**Course:** nigcomsat_developer_track
**Module:** LLM APIs, Structured Outputs & Git
**Submission format:** python_script_with_pytest

---

You are building a small tool for the Monitoring, Compliance and Enforcement (MCE) team: given a compliance notice, it must call the model API properly, extract validated structured data from it, and prove -- with tests, not by eye -- that the extraction is actually correct, not just correctly shaped.

This brings together all three skills from Week 1: calling a model API with proper error handling, structured output with Pydantic validation, and testing for hallucination and verification habits.

---

### The Document

Your script works against `MCE-CN-2026-031_compliance_notice.txt` in the shared synthetic MCE corpus (`shared/synthetic-mce-corpus/`). Read it carefully before you start -- it is short, but it is not simple. All data in it is synthetic; no real NIGCOMSAT record is involved.

---

### What You Must Build

Two files: a script that performs the extraction, and a `pytest` file that proves it works. Both must run from the terminal.

---

#### Stage 1 -- Calling the Model Properly

Write a small, reusable function that calls the model with:
1. A system message and a user message (the notice text)
2. Error handling for transient failures (rate limits, timeouts) using exponential backoff, capped at 3 attempts
3. The API key, model name and base URL loaded from `.env` -- never hardcoded

Print the token usage (prompt, completion, total) from at least one call.

This retry loop is for *transient* failures -- the connection or the API having a bad moment. It is a different concern from Stage 2's retry loop, which is for *validation* failures. Keep them conceptually separate, even if some of the code is shared.

---

#### Stage 2 -- Structured Extraction With Validation

Define a Pydantic model for the notice with, at minimum, these fields:
- `notice_reference` (string)
- `licence_number` (string)
- `condition_breached` (string -- which licence condition was breached)
- `current_deadline` (string, ISO date -- see the trap below)
- `penalty_per_week_ngn` (integer)
- `max_penalty_ngn` (integer)

Add at least one `field_validator` enforcing a business rule the type system alone cannot express (for example: penalty amounts cannot be negative).

Use structured output mode (`response_format=YourModel`) to extract the notice, with a retry loop that feeds any validation error back to the model, capped at 3 attempts.

**The trap:** the notice contains two deadlines. Section 2 states one; a later Revision Notice supersedes it with another. `current_deadline` must be the one that is actually in force -- the revised one -- not whichever date the model happens to read first.

---

#### Stage 3 -- Testing for Correctness, Not Just Shape

A validated shape is not a correct answer -- Week 1 already taught you that. Prove your extractor is actually right, not just well-formed.

1. **Build a human-verified answer key.** Read the notice yourself and write down the correct value for `current_deadline` before you test anything. Do not ask the model what it thinks the answer is.
2. **Write a test that would catch the trap.** A test that asserts `current_deadline` equals the revised date, not the superseded one. If your extractor reports the superseded date, this test must fail -- that is the test doing its job, not a bug in the test.
3. **Write a test proving the validator works**, using `pytest.raises`, that needs no API call at all.
4. Keep these two tests independent -- neither should depend on the other, and the offline one should still pass even if the API is unreachable.
5. The deadline is the one deliberate trap you were told about. A thorough test suite checks every extracted field against the source, not only the field you were warned about.

---

### Deliverables
- One Python script performing the extraction (Stages 1 and 2)
- One `pytest` file with at least two tests (Stage 3): the deadline check and the offline validator check
- Both must run from the terminal; the test file must be runnable with `pytest <filename> -v`
- A short written note (a few sentences, in a comment or README) explaining: why the answer key was computed by hand rather than asked of the model, and why the two tests are kept independent of each other

---

## Grading Notes

Participants are building a small extraction tool, not a conversational product -- there is no single correct code structure, but there is a single correct value for current_deadline (2026-04-13, the revised date from the Revision Notice, not 2026-03-30). Getting that value wrong is the one failure that should always cost points, regardless of how clean the rest of the submission is -- it is the entire point of Stage 3. Do not penalise reasonable variation in field names, retry-count choices, or backoff timing, as long as Stage 1's error handling and Stage 2's validation retry are both genuinely present and distinct from each other. Accept any business rule in the field_validator as long as it is a real rule the type system could not express on its own -- it does not have to be the penalty-non-negative example given in the brief. The offline validator test must not call the model; if it does, Stage 3's independence requirement is not met even if the test passes. Real NIGCOMSAT documents must not be used for this project -- the synthetic corpus document is the only intended input unless NIGCOMSAT has explicitly cleared a real one. During development of the reference solution, this model was found to sometimes drop a digit when copying the long comma-grouped max_penalty_ngn figure (NGN 10,000,000 misread as 1,000,000), on roughly half of repeated runs, even after the system prompt was tightened to warn about it explicitly. This is a real, reproducible model limitation, not a hint to remove from the brief -- point 5 of Stage 3 is there so participants have a chance to discover this kind of thing themselves. A submission that independently finds and tests this (or any other field the model gets wrong) deserves credit beyond the base rubric, at grader discretion. Do not penalise a submission that reports max_penalty_ngn incorrectly if its Stage 1 and Stage 2 implementation is otherwise sound and it was not told to test that field -- the model, not the student, is the source of that specific error.

---

## Rubric (100 points total)

| Criterion | Description | Points |
|---|---|---|
| api_call_and_error_handling | Stage 1: credentials loaded from .env, never hardcoded. The model is called with a system and user message. Transient-failure handling (rate limits or timeouts) with exponential backoff is implemented and capped at a small number of attempts. Token usage is printed from at least one response. | 25 |
| structured_extraction_and_validation | Stage 2: a Pydantic model defines all required fields with correct types. Structured output mode is used to extract the notice. At least one field_validator enforces a genuine business rule. A retry loop feeds validation errors back to the model, capped at a small number of attempts, and is conceptually distinct from Stage 1's retry loop. | 30 |
| correctness_testing | Stage 3: a hand-built answer key exists with the correct, revised current_deadline (2026-04-13). A test asserts the extractor reports this value, not the superseded 2026-03-30. A separate pytest.raises test proves the validator rejects bad data without any API call. The two tests are independent -- the offline test does not depend on the live one, and a failure in one does not silently affect the other. | 30 |
| documentation_and_verification_habits | A short written note explains why the answer key was computed by hand rather than asked of the model, and why the two Stage 3 tests are kept independent. Both scripts run cleanly from the terminal as described in the brief. | 15 |
