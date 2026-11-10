# Demo Guide — Packaging with Docker
**Module 5B, Topic 3 | Terminal + VS Code | 30-35 min**

## What Participants Will Do

Install Docker Desktop (if not already installed), write a Dockerfile for a small NOC digest automation, build and run the image, add a `.dockerignore`, pass secrets at runtime with `--env-file`, add a `docker-compose.yml` for a FastAPI + MySQL setup, and run tests inside the container. Everything happens in the terminal and VS Code.

## Pre-requisites

- Docker Desktop installed and running (`docker --version` works)
- The capstone demo files from Topic 2 (or use the scaffold below)
- A `.env` file with `OPENAI_API_KEY`, `MODEL_NAME`, `OPENAI_BASE_URL` (for the live demo, optional)

---

## Part 1 — Verify Docker Is Running (3 min)

**Instructor action:** Confirm Docker is working.

```bash
docker --version
docker run --rm hello-world
```

**Expected output:** Docker version, then the "Hello from Docker!" message.

**If Docker Desktop is not installed**, guide participants through the install now:
1. Download from docker.com
2. Run installer (enables WSL 2 on Windows)
3. Restart
4. Open Docker Desktop, wait for "Docker Desktop is running"
5. Re-run `docker --version`

**Talk through:** "If you see the hello-world message, Docker is working. If not, pair with someone who has it running — we will debug after class."

---

## Part 2 — Write a Dockerfile (5 min)

**Instructor action:** In the `capstone-demo/` folder from Topic 2, create a `requirements.txt` and a `Dockerfile`.

**Create `requirements.txt`:**

```
openai
python-dotenv
pytest
```

**Create `Dockerfile`:**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "digest.py"]
```

**Talk through each line:**
- `FROM python:3.10-slim` — "We start from a base image with Python 3.10 already installed. The `slim` variant is about 120MB instead of 900MB — it leaves out compilers we do not need."
- `WORKDIR /app` — "Set the working directory inside the container."
- `COPY requirements.txt .` then `RUN pip install` — "Install dependencies first. Docker caches this layer, so if only our code changes, pip does not run again."
- `COPY . .` — "Copy the rest of our code into the image."
- `CMD` — "The default command when a container starts."

---

## Part 3 — Create .dockerignore (2 min)

**Instructor action:** Create `.dockerignore` in the same folder.

```
.env
.env.*
__pycache__
*.pyc
.git
.vscode
*.md
```

**Talk through:** "This keeps secrets and unnecessary files out of the image. The most important line is `.env` — even if `COPY . .` runs, the `.env` file is excluded. Your API keys never enter the image."

---

## Part 4 — Build and Run (5 min)

**Instructor action:** Build the image and run it.

```bash
# build the image
docker build -t noc-digest .
```

**Show the output:** Each `STEP` corresponds to a Dockerfile instruction. Docker caches layers — point out "Using cache" on the `pip install` step if you rebuild.

```bash
# run the container (will fail without .env — that is expected)
docker run --rm noc-digest
```

**Expected:** An error about missing API key — because we did not pass `.env`.

```bash
# run with environment variables
docker run --rm --env-file .env noc-digest
```

**Expected:** The digest script runs and produces output (if the `.env` has a valid key). If no key is available, show the error handling from Topic 2's tests.

**Talk through:** "The first run failed because there is no API key inside the container — good, that means `.dockerignore` is working. The second run passes the `.env` file at runtime with `--env-file`. The key is never in the image."

---

## Part 5 — Run Tests Inside the Container (5 min)

**Instructor action:** Run the Topic 2 tests inside the container.

```bash
# run all mocked tests inside the container
docker run --rm noc-digest pytest test_validate.py test_digest.py -v
```

**Expected output:** All mocked tests pass inside the container — same as on the laptop.

**Talk through:** "If the tests pass on your laptop but fail in the container, something is different about the environment — a missing package in `requirements.txt`, a file excluded by `.dockerignore`. Catch this now, not in CI tomorrow."

**If a test fails:** Debug together. Common causes:
- Missing package in `requirements.txt` (add it, rebuild)
- File excluded by `.dockerignore` that the tests need (adjust `.dockerignore`)
- Import path issue (check `WORKDIR`)

---

## Part 6 — Docker Compose: FastAPI + MySQL (8 min)

**Instructor action:** Show a Compose setup for participants whose capstone includes a web service and database. Create `docker-compose.yml`:

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: localdev
      MYSQL_DATABASE: capstone
    ports:
      - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:
```

**For the demo, update the Dockerfile CMD for a FastAPI app:**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**(If participants do not have a FastAPI app in this demo folder, this part is show-and-tell. The commands below work if they have a `main.py` with a FastAPI app.)**

```bash
# start both services
docker compose up --build

# in another terminal, verify it works
curl http://localhost:8000/docs

# stop both services
docker compose down
```

**Talk through:** "One command starts your app and its database. Your colleague does not need MySQL installed — Compose pulls the image and starts it. The `depends_on` ensures MySQL is running before the app starts. The volume persists the database data between restarts."

**For participants with a single-container capstone:** "If your capstone is a script or a CLI tool, you do not need Compose. `docker run --env-file .env` is enough. Do not add Compose for complexity's sake."

---

## Part 7 — Rebuild and Layer Caching (3 min)

**Instructor action:** Make a small change to `digest.py` (add a comment), then rebuild.

```bash
# change one line of code
# then rebuild
docker build -t noc-digest .
```

**Show the output:** The `pip install` layer says "Using cache" — only the `COPY . .` layer and after re-run. The rebuild takes seconds instead of minutes.

**Talk through:** "This is why we copy `requirements.txt` and install packages before copying the code. Docker caches each layer. If only the code changed, pip does not run again. This saves minutes on every rebuild."

**Now change `requirements.txt`** (add `requests`), rebuild, and show that pip runs again because the layer changed.

---

## Wrap-Up (2 min)

**Participant task:** "Containerise your capstone:
1. Write a `Dockerfile` (start from the four-line template)
2. Create `.dockerignore` (at minimum: `.env`, `__pycache__`, `.git`)
3. Build: `docker build -t my-capstone .`
4. Run: `docker run --rm --env-file .env my-capstone`
5. Run tests: `docker run --rm my-capstone pytest -v`
6. If you need a database, add `docker-compose.yml`

By end of day, your capstone runs in Docker and tests pass inside the container. Tomorrow we wire GitHub Actions to do this automatically on every push."

**Files created in this demo:**
- `Dockerfile` — the image recipe
- `.dockerignore` — keeps secrets and junk out of the image
- `requirements.txt` — Python dependencies (may already exist from Topic 2)
- `docker-compose.yml` — multi-service setup (only if needed)
