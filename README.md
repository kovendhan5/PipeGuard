# PipeGuard - GitHub Actions Pipeline Monitor

PipeGuard is a monitoring system for GitHub Actions pipelines that detects anomalies and provides suggestions for fixes. The project demonstrates DevOps skills by integrating multiple Google Cloud services with a GitHub workflow.

## Quick Start (Local Development)

### Option 1: Windows Batch Script (Easiest)
1. Double-click `setup_and_run.bat`
2. Choose option 1 to run the Flask app locally
3. Visit http://localhost:8080 to see the dashboard

### Option 2: Manual Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run locally: `python run_local.py`
3. Visit http://localhost:8080

### Option 3: Test the Application
Run tests to verify everything works:
```bash
python -m pytest test_app.py -v
```

## Configuration for Production

1. Copy `.env.example` to `.env`
2. Fill in your actual credentials:
   - `GITHUB_TOKEN`: GitHub personal access token with repo:status scope
   - `GITHUB_USER`: Your GitHub username
   - `GITHUB_REPO`: Repository name to monitor
   - `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID

## Features

- Real-time monitoring of GitHub Actions pipeline runs
- Automated detection of anomalous pipeline behavior:
  - Performance issues (runs taking longer than usual)
  - Failed pipeline runs
- Suggested fixes for identified problems
- Interactive dashboard for visualizing pipeline health
- Hourly automatic monitoring via Cloud Scheduler

## Architecture

- **GitHub Actions**: CI/CD pipeline providing the source data
- **Google Cloud Function**: Collects GitHub Actions data and detects anomalies
- **Google Firestore**: NoSQL database storing pipeline runs and detected anomalies
- **Google App Engine**: Hosts the Flask dashboard website
- **Google Cloud Scheduler**: Triggers the monitoring function hourly

## Live Demo

Visit the live dashboard: [https://pipeguard.uc.r.appspot.com/](https://pipeguard.uc.r.appspot.com/)

## Setup Instructions

### Prerequisites

- GitHub account with a repository using GitHub Actions
- Google Cloud Platform account
- Python 3.9+

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
