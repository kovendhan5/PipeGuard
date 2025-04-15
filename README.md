# PipeGuard

PipeGuard is a DevOps tool that monitors a GitHub Actions pipeline, detects anomalies (like long build times or test failures), and displays insights via a Flask dashboard on Google App Engine.

## Features
- Monitors GitHub Actions runs for this repo
- Logs run data (status, duration) in Firestore
- Flags anomalies (duration > 2x average, failures) with fix suggestions
- Dashboard with recent runs, anomalies, and duration chart
- Serverless: Cloud Functions, Firestore, App Engine, Cloud Scheduler

## Setup

### 1. Prerequisites
- Python 3.9+
- Google Cloud project (`pipeguard`) with Firestore, Cloud Functions, App Engine, and Cloud Scheduler enabled
- GitHub token with `repo:status` scope

### 2. Local Development
```bash
pip install -r requirements.txt
python app.py
```

### 3. CI/CD
- On push, GitHub Actions runs tests via `.github/workflows/ci.yml`

### 4. Cloud Function (monitor_pipeline.py)
- Deploy to Google Cloud Functions
- Set environment variable `GITHUB_TOKEN` to your GitHub token
- Schedule with Cloud Scheduler (hourly)

### 5. Dashboard (main.py)
- Deploy to App Engine:
```bash
gcloud app deploy app.yaml
```
- Access at: `https://pipeguard.ew.r.appspot.com` (or your region)

## File Structure
- `app.py` – Minimal Flask app
- `test_app.py` – Pytest suite
- `requirements.txt` – Dependencies
- `.github/workflows/ci.yml` – GitHub Actions workflow
- `monitor_pipeline.py` – Cloud Function
- `main.py` – Flask dashboard
- `templates/index.html` – Dashboard UI
- `app.yaml` – App Engine config

## Notes
- Firestore must be in Native mode
- GitHub token should be kept secret (use Secret Manager or env vars)
- For demo, use the provided sample code and update as needed

## License
MIT
