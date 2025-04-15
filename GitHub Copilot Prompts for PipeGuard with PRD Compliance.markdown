# GitHub Copilot Prompts for Smart Pipeline Health Monitor (PipeGuard)

## Overview
These prompts instruct GitHub Copilot to build PipeGuard—a DevOps tool that monitors GitHub Actions pipelines, detects anomalies (e.g., long builds, test failures), and displays insights on a Flask dashboard—strictly per the Project Requirement Document (PRD, artifact_id: fd24885d-71f1-4f21-b3fc-946d257921ab). Designed for Google Cloud’s free tier and a 48-hour timeline, they align with your Python skills and job goals. Prompts embed PRD context to mimic “requirements access” without MCP servers, using the Model Context Protocol (MCP) approach to avoid drift (e.g., non-GCP code).

## Setup Instructions
- **Environment**: VS Code, Python 3.9, GitHub Copilot extension, Google Cloud SDK.
- **Copilot Usage**:
  - Paste prompts as comments in files.
  - Accept suggestions matching PRD (e.g., `google.cloud.firestore`, Flask, Python 3.9).
  - Reject irrelevant code (e.g., AWS, Node.js, SQL).
  - Replace placeholders (e.g., `YOUR_GITHUB_TOKEN`).
- **Files**:
  - `.github/workflows/ci.yml` (pipeline)
  - `monitor_pipeline.py` (Cloud Function)
  - `main.py` (Flask app)
  - `templates/index.html` (dashboard)
  - `requirements.txt`, `app.yaml`
- **PRD Compliance**: Prompts reference PRD sections (FR1-FR10, Tech Stack: Google Cloud, Flask, Firestore, Chart.js).
- **MCP Note**: No MCP servers needed; Firestore is accessed via SDK, not external databases.

## Prompts by PRD Component

### 1. GitHub Actions Pipeline (FR1-FR3)
**File**: `.github/workflows/ci.yml`  
**Purpose**: CI pipeline for Flask app per PRD FR1 (public repo), FR2 (build/test), FR3 (pytest).  
**Prompt**:
```yaml
# PipeGuard: GitHub Actions per PRD FR1-FR3
# Public repo YOUR_USERNAME/YOUR_REPO, Python Flask app
# Trigger on push to main, use ubuntu-latest, Python 3.9
# Steps: checkout, setup-python, install requirements.txt, run pytest
# PRD: No Docker, no extra jobs
```
**Expected Output**:
```yaml
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with: { python-version: '3.9' }
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
```
**Supporting Files** (manual):
- `app.py`:
  ```python
  from flask import Flask
  app = Flask(__name__)
  @app.route('/')
  def hello():
      return 'Hello, PipeGuard!'
  ```
- `test_app.py`:
  ```python
  from app import app
  def test_hello():
      client = app.test_client()
      response = client.get('/')
      assert response.status_code == 200
      assert b'Hello, PipeGuard!' in response.data
  ```
- `requirements.txt`:
  ```
  flask==2.0.1
  pytest==7.1.2
  ```

### 2. Cloud Function for Monitoring (FR4-FR5)
**File**: `monitor_pipeline.py`  
**Purpose**: Fetch runs, store in Firestore per PRD FR4 (GitHub API), FR5 (runs collection).  
**Prompt**:
```python
# PipeGuard: Cloud Function per PRD FR4-FR5
# Fetch GitHub Actions runs for YOUR_USERNAME/YOUR_REPO
# Use requests, Bearer YOUR_GITHUB_TOKEN
# Store id, status, duration (updated_at - created_at, seconds) in Firestore 'runs'
# PRD: Use google.cloud.firestore, no SQL, no MCP server
```
**Expected Output**:
```python
import requests
from google.cloud import firestore
from datetime import datetime

def monitor_pipeline(request):
    headers = {"Authorization": "Bearer YOUR_GITHUB_TOKEN"}
    url = "https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/actions/runs"
    runs = requests.get(url, headers=headers).json()
    db = firestore.Client()
    for run in runs["workflow_runs"]:
        created = datetime.strptime(run["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        updated = datetime.strptime(run["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
        duration = int((updated - created).total_seconds())
        db.collection("runs").add({
            "id": run["id"],
            "status": run["status"],
            "duration": duration,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
    return "Runs logged"
```
**Notes**:
- Deploy: `gcloud functions deploy monitor_pipeline --runtime python39 --trigger-http`.
- `requirements.txt`: Add `requests==2.28.1, google-cloud-firestore==2.7.2`.

### 3. Anomaly Detection (FR6-FR7)
**File**: `monitor_pipeline.py` (append)  
**Purpose**: Detect and store anomalies per PRD FR6 (flag issues), FR7 (anomalies collection).  
**Prompt**:
```python
# PipeGuard: Anomaly detection per PRD FR6-FR7
# Input: run dict, duration (seconds)
# Query Firestore 'runs', last 10, average duration
# Flag: duration > 2x average ('Long build time', 'Optimize resources')
# Flag: status == 'failure' ('Test failure', 'Check test logs')
# Store in Firestore 'anomalies'
# PRD: No ML, no external DB
```
**Expected Output**:
```python
def detect_anomaly(run, duration):
    db = firestore.Client()
    recent = db.collection("runs").order_by("timestamp").limit(10).get()
    durations = [r.to_dict()["duration"] for r in recent]
    avg_duration = sum(durations) / len(durations) if durations else 1
    if duration > 2 * avg_duration:
        return {"issue": "Long build time", "fix": "Optimize resources"}
    if run["status"] == "failure":
        return {"issue": "Test failure", "fix": "Check test logs"}
    return None
```
**Update `monitor_pipeline`**:
```python
# After storing run
anomaly = detect_anomaly(run, duration)
if anomaly:
    db.collection("anomalies").add(anomaly)
```

### 4. Flask Dashboard (FR8-FR9)
**File**: `main.py`  
**Purpose**: Dashboard per PRD FR8 (runs, anomalies, chart), FR9 (public).  
**Prompt**:
```python
# PipeGuard: Flask on App Engine per PRD FR8-FR9
# Route '/' fetches Firestore: 10 runs (id, status, duration), 5 anomalies (issue, fix)
# Render index.html with runs, anomalies
# PRD: Use google.cloud.firestore, no MCP server
```
**Expected Output**:
```python
from flask import Flask, render_template
from google.cloud import firestore

app = Flask(__name__)

@app.route("/")
def dashboard():
    db = firestore.Client()
    runs = db.collection("runs").order_by("timestamp").limit(10).get()
    anomalies = db.collection("anomalies").limit(5).get()
    return render_template("index.html",
                          runs=[r.to_dict() for r in runs],
                          anomalies=[a.to_dict() for a in anomalies])
```
**Config**:
- `app.yaml`:
  ```yaml
  runtime: python39
  entrypoint: gunicorn -b :$PORT main:app
  ```
- `requirements.txt`: Add `gunicorn==20.1.0`.

### 5. Dashboard UI (FR8)
**File**: `templates/index.html`  
**Purpose**: UI per PRD FR8 (runs, anomalies, chart).  
**Prompt**:
```html
<!-- PipeGuard: Dashboard per PRD FR8 -->
<!-- List 10 runs: id, status, duration -->
<!-- List 5 anomalies: issue, fix -->
<!-- Chart.js line chart: durations, blue line -->
<!-- Arial font, 600px canvas -->
<!-- PRD: No extra frameworks -->
```
**Expected Output**:
```html
<!DOCTYPE html>
<html>
<head>
  <title>PipeGuard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { font-family: Arial; margin: 20px; }
    canvas { max-width: 600px; }
  </style>
</head>
<body>
  <h1>PipeGuard: Pipeline Health</h1>
  <h2>Recent Runs</h2>
  <ul>
    {% for run in runs %}
      <li>Run {{ run.id }}: {{ run.status }} ({{ run.duration }}s)</li>
    {% endfor %}
  </ul>
  <h2>Anomalies</h2>
  <ul>
    {% for anomaly in anomalies %}
      <li>{{ anomaly.issue }} - Fix: {{ anomaly.fix }}</li>
    {% endfor %}
  </ul>
  <canvas id="durationChart"></canvas>
  <script>
    new Chart(document.getElementById("durationChart"), {
      type: "line",
      data: {
        labels: [{% for run in runs %}"Run {{ run.id }}",{% endfor %}],
        datasets: [{
          label: "Build Duration (s)",
          data: [{% for run in runs %}{{ run.duration }},{% endfor %}],
          borderColor: "blue",
          fill: false
        }]
      }
    });
  </script>
</body>
</html>
```

### 6. Automation (FR10)
**File**: None (Cloud Scheduler)  
**Purpose**: Hourly trigger per PRD FR10.  
**Prompt** (terminal/note):
```bash
# PipeGuard: Scheduler per PRD FR10
# Hourly HTTP call to monitor_pipeline
# PRD: Use gcloud scheduler
```
**Command**:
```bash
gcloud scheduler jobs create http pipeline-monitor \
  --schedule "0 * * * *" \
  --uri "https://YOUR_REGION-YOUR_PROJECT_ID.cloudfunctions.net/monitor_pipeline"
```

## Tips for Copilot
- **PRD Compliance**:
  - Prompts cite “PRD FR#” to lock Copilot to requirements.
  - Reject non-PRD code (e.g., SQL, AWS).
  - Verify Firestore: `runs` (id, status, duration), `anomalies` (issue, fix).
- **MCP Approach**:
  - Use “Google Cloud,” “PipeGuard,” “PRD” to avoid drift.
  - No MCP servers; Firestore uses SDK.
- **Debugging**:
  - Errors? Add: `# Fix [issue] for PipeGuard per PRD`.
  - Example: `# Fix Firestore auth for PipeGuard`.

## Plan
- **Day 1**: Pipeline (Prompt 1), Monitoring/Anomalies (2-3).
- **Day 2**: Dashboard (4-5), Scheduler (6), test.
- **Test**: 5+ commits, check Firestore/dashboard.

## Deliverables
- Demo: `https://YOUR_PROJECT_ID.ew.r.appspot.com`.
- Repo with README.
- 1-min video.