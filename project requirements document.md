Smart Pipeline Health Monitor (PipeGuard) - Project Requirement Document
1. Project Overview
1.1 Purpose
PipeGuard is a DevOps tool that monitors CI/CD pipelines (e.g., GitHub Actions), detects anomalies like long build times or test failures, and displays insights via a web dashboard. It solves the real-world issue of silent pipeline failures that delay releases, targeting lean teams on Google Cloud’s free tier.
1.2 Objective
Build a serverless prototype in 48 hours to:

Monitor a sample GitHub Actions pipeline for a Python app.
Log run data (status, duration) in Firestore.
Flag anomalies (e.g., build time > 2x average) with fix suggestions.
Provide a Flask-based dashboard on App Engine.
Showcase DevOps skills (CI/CD, cloud automation, monitoring) for job applications.

1.3 Scope

In-Scope:
GitHub Actions pipeline for a Flask app.
Cloud Functions for monitoring.
Firestore for data storage.
App Engine dashboard with Chart.js.
Hourly triggers via Cloud Scheduler.
GitHub Copilot for coding efficiency.


Out-of-Scope:
Multi-pipeline monitoring.
Machine learning for anomalies.
Email/SMS alerts.




2. Functional Requirements
2.1 Pipeline Setup

FR1: Public GitHub repo with a Python Flask app.
FR2: GitHub Actions workflow for build/test on push.
FR3: Pytest suite to simulate pass/fail cases.

2.2 Monitoring

FR4: Cloud Function to fetch GitHub Actions data (ID, status, duration) hourly.
FR5: Store runs in Firestore with timestamps.

2.3 Anomaly Detection

FR6: Flag anomalies:
Duration > 2x average of last 10 runs.
Failed status.


FR7: Log anomalies with fixes (e.g., “Review test logs”) in Firestore.

2.4 Dashboard

FR8: Flask app on App Engine showing:
Last 10 runs (ID, status, duration).
Recent anomalies with fixes.
Duration chart (Chart.js).


FR9: Publicly accessible dashboard.

2.5 Automation

FR10: Hourly monitoring via Cloud Scheduler.


3. Non-Functional Requirements
3.1 Performance

Cloud Function runs in < 10 seconds.
Dashboard loads in < 3 seconds.

3.2 Scalability

Supports 100 runs/day within Firestore free tier (1 GiB).

3.3 Security

GitHub token with repo:status scope.
Firestore read-only for dashboard.

3.4 Usability

Clean, mobile-friendly dashboard.
Commented code.

3.5 Cost

Zero cost using:
Cloud Functions: < 200K invocations/month.
Firestore: < 1 GiB.
App Engine: < 28 instance hours/day.




4. Technical Requirements
4.1 Tech Stack

Backend: Cloud Functions (Python 3.9).
Pipeline: GitHub Actions, Docker.
Database: Firestore.
Frontend: App Engine, Flask, Chart.js.
APIs: GitHub API, Cloud Monitoring API.
Tools: Google Cloud SDK, Git, Copilot, VS Code.

4.2 Environment

Local: Python 3.9, VS Code with Copilot.
Cloud: Google Cloud Console, gcloud CLI.
GitHub: Public repo.

4.3 Sample Code

Cloud Function (monitor_pipeline.py):
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
        anomaly = detect_anomaly(run, duration)
        if anomaly:
            db.collection("anomalies").add(anomaly)
    return "Runs logged"

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


Flask App (main.py):
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


Dashboard (templates/index.html):
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


GitHub Actions (.github/workflows/ci.yml):
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




5. Development Plan (48 Hours)
5.1 Day 1: Pipeline + Backend (8-10 hours)

Hour 1: Set up Google Cloud, enable APIs, install SDK.
Hours 2-3: Create repo, Flask app, GitHub Actions.
Hours 4-6: Build Cloud Function for monitoring.
Hours 7-10: Add anomaly detection, test with runs.

5.2 Day 2: Frontend + Testing (8-10 hours)

Hours 1-4: Develop Flask dashboard, deploy to App Engine.
Hours 5-6: Configure Cloud Scheduler.
Hours 7-10: Test, debug, document on GitHub.


6. Deliverables

Live Demo: https://YOUR_PROJECT_ID.ew.r.appspot.com.
GitHub Repo: Public, with code, README, screenshots.
Portfolio: 1-min video demo (problem, solution, tech).


7. Constraints

Timeline: Complete by April 17, 2025, 06:59 AM PDT.
Budget: Zero cost (free tier).
Skills: Python, Git, web basics (per prior chats).
Scope: Avoid extras like alerts or complex analytics.


8. Success Criteria

Firestore logs runs within 1 hour.
Dashboard shows 5+ runs, 1+ anomaly.
App is live, bug-free.
Repo has clear README and demo link.
Project highlights CI/CD, automation, monitoring for jobs.

