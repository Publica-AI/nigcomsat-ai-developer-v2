# Demo Guide — CI/CD with GitHub Actions
**Module 5B, Topic 4 | Terminal + VS Code + GitHub Browser | 25-30 min**

## What Participants Will Do

Create a `.github/workflows/test.yml` that installs dependencies and runs pytest on every push, push it to GitHub, watch it run in the Actions tab, break a test to see the pipeline fail, fix it, and set up a branch protection rule to block merges when tests fail. Everything happens in VS Code, the terminal, and the GitHub web interface.

## Pre-requisites

- A GitHub repository for the capstone (can be created during the demo)
- The capstone code with working pytest tests (from Topics 2-3)
- `requirements.txt` listing all dependencies (including `pytest`)
- Git configured with push access to the repository

---

## Part 1 — Set Up the Repository (3 min)

**If participants already have a GitHub repo for their capstone, skip to Part 2.**

**Instructor action:** Create a repo and push the capstone code.

```bash
cd capstone-demo
git init
git add .
git commit -m "Initial commit: capstone code and tests"
```

Then on GitHub:
1. Create a new repository (private is fine)
2. Follow the "push an existing repository" instructions:

```bash
git remote add origin https://github.com/USERNAME/capstone-demo.git
git branch -M main
git push -u origin main
```

**Talk through:** "Your capstone code is now on GitHub. Every file we created in Topics 2 and 3 — the validation, the digest, the tests, the Dockerfile — is in the repo. Now we add the pipeline."

---

## Part 2 — Create the Workflow File (5 min)

**Instructor action:** Create the workflow directory and file.

```bash
mkdir -p .github/workflows
```

**Create `.github/workflows/test.yml` in VS Code:**

```yaml
name: Run Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: pip install -r requirements.txt
      - run: pytest test_validate.py test_digest.py -v
```

**Talk through each section:**
- `name:` — the label shown in the Actions tab.
- `on: push` — run this workflow when code is pushed to main.
- `on: pull_request` — also run it on PRs targeting main.
- `runs-on: ubuntu-latest` — GitHub provides a fresh Ubuntu machine.
- `steps:` — checkout the code, install Python 3.10, install packages, run tests.

**Important:** "The pytest command runs only mocked tests — `test_validate.py` and `test_digest.py`. It does NOT run `test_live.py`. Live tests cost money and depend on an API key that CI does not have (unless you add it as a secret). Mocked tests are fast, free, and deterministic."

---

## Part 3 — Push and Watch (5 min)

**Instructor action:** Commit and push the workflow.

```bash
git add .github/workflows/test.yml
git commit -m "Add CI pipeline: run pytest on every push"
git push
```

**In the browser:**
1. Go to the repository on GitHub
2. Click the **Actions** tab
3. Find the workflow run (named after the commit message)
4. Click it → click the `test` job → expand each step

**Show:**
- The checkout step (fast — just clones the repo)
- The Python setup step (installs 3.10)
- The pip install step (installs from `requirements.txt`)
- The pytest step (shows the test output — same as running locally)

**Expected result:** Green checkmark — all tests pass.

**Talk through:** "This is the same output as running `pytest -v` on your machine. The difference is: this machine started from nothing. It had no Python, no packages, no code. It installed everything from scratch and ran the tests. If it passes here, it will pass on any machine."

---

## Part 4 — Break a Test (5 min)

**Instructor action:** Intentionally break a test to show a pipeline failure.

**In `test_validate.py`, change one assertion:**

```python
def test_valid_alert_passes():
    result = validate_alert("CRITICAL: Link down on VSAT-OP-0341")
    assert result["valid"] is False  # <- wrong on purpose
```

```bash
git add test_validate.py
git commit -m "Break a test to demo pipeline failure"
git push
```

**In the browser:**
1. Go to Actions tab
2. Watch the workflow run
3. See the red X

**Click the failed step:**
- Show the pytest output — it shows the failing assertion
- Show the exact line and the comparison: `True is not False`

**Talk through:** "The pipeline caught it. If branch protection were on, this change could not merge to main. The error message is the same as running `pytest` locally — pytest shows you the line, the expected value, and the actual value."

**Fix it and push again:**

```python
def test_valid_alert_passes():
    result = validate_alert("CRITICAL: Link down on VSAT-OP-0341")
    assert result["valid"] is True  # <- fixed
```

```bash
git add test_validate.py
git commit -m "Fix broken test"
git push
```

**Show the pipeline go green again.**

---

## Part 5 — Add Branch Protection (5 min)

**Instructor action:** Set up a branch protection rule in the browser.

1. Go to the repo → **Settings** → **Branches**
2. Click **Add branch protection rule** (or **Add classic branch protection rule**)
3. Branch name pattern: `main`
4. Check: **Require status checks to pass before merging**
5. Search for and select the `test` status check
6. Save changes

**Talk through:** "Now the pipeline is not just informational — it is a gate. If anyone opens a pull request to main and the tests fail, the merge button is greyed out. They must fix the tests before merging. This is the safety net: broken code cannot reach the main branch."

**If the `test` check does not appear in the search:** "You need at least one successful workflow run before the check appears. We have one from Part 3, so it should be there. If not, push a change and wait for the run to complete."

---

## Part 6 — Add Secrets (Optional, 3 min)

**Instructor action:** Show how to add a secret — only needed if participants want to run live tests in CI.

1. Go to the repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `OPENAI_API_KEY`, Value: (the key)
4. Save

**Update the workflow to use the secret (optional step for live tests):**

```yaml
      - run: pytest -v
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          MODEL_NAME: ${{ secrets.MODEL_NAME }}
          OPENAI_BASE_URL: ${{ secrets.OPENAI_BASE_URL }}
```

**Talk through:** "Secrets are encrypted and never printed in logs. For most capstones, you do not need this — mocked tests run without secrets. But if you want to run your live smoke tests in CI as well, this is how you make the API key available."

---

## Part 7 — Stretch: Docker Build in CI (3 min)

**Instructor action:** Show the extended workflow with a Docker job (do not require participants to implement this).

```yaml
  docker:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t noc-digest .
      - run: docker run --rm noc-digest pytest test_validate.py test_digest.py -v
```

**Talk through:** "This adds a second job that builds the Docker image and runs the tests inside the container. `needs: test` means it only runs if the first job passes. This is stretch credit — it proves the tests pass both natively and inside the container. If you have time and your Dockerfile is working, add this."

---

## Wrap-Up (2 min)

**Participant task:** "Set up CI for your capstone:
1. Create `.github/workflows/test.yml` (copy the template)
2. Adjust the pytest command to run your mocked test files
3. Commit and push
4. Check the Actions tab — it should go green
5. Add a branch protection rule on `main`

By end of day, your capstone has a pipeline that runs tests on every push and blocks merges on failure. Tomorrow (Topic 5) we cover the final mile: security review, monitoring, and handover."

**Files created in this demo:**
- `.github/workflows/test.yml` — the CI pipeline
