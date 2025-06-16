# 🚀 PipeGuard Real Environment Setup Guide

## Prerequisites Checklist

Before setting up PipeGuard with real services, ensure you have:

- [ ] GitHub account with a repository containing GitHub Actions
- [ ] Google Cloud Platform account (free tier is sufficient)
- [ ] Python 3.9+ installed
- [ ] Git installed and configured

## Step 1: GitHub Setup

### 1.1 Create GitHub Personal Access Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Set expiration (90 days recommended for testing)
4. Select these scopes:
   - [ ] `repo` (Full control of private repositories)
   - [ ] `workflow` (Update GitHub Action workflows)
   - [ ] `read:org` (Read org and team membership)
5. Click "Generate token" and **copy it immediately**

### 1.2 Update .env file
```bash
GITHUB_TOKEN=ghp_your_actual_token_here
GITHUB_USER=your_github_username
GITHUB_REPO=your_repository_name
```

## Step 2: Google Cloud Platform Setup

### 2.1 Create GCP Project
1. Go to https://console.cloud.google.com/
2. Click "New Project"
3. Name: `pipeguard-monitor` (or your preference)
4. Note the Project ID

### 2.2 Enable Required APIs
```bash
# Run these commands in Google Cloud Shell or with gcloud CLI
gcloud services enable firestore.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable appengine.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
```

### 2.3 Create Service Account
1. Go to IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Name: `pipeguard-service`
4. Grant these roles:
   - Cloud Datastore User
   - Cloud Functions Developer
   - App Engine Admin
5. Create and download JSON key
6. Save as `k:\Devops\PipeGuard-1\credentials\service-account-key.json`

### 2.4 Initialize Firestore
1. Go to Firestore in the Console
2. Click "Create database"
3. Choose "Production mode"
4. Select a region (us-central1 recommended)

### 2.5 Update .env file
```bash
GOOGLE_APPLICATION_CREDENTIALS=k:\Devops\PipeGuard-1\credentials\service-account-key.json
GOOGLE_CLOUD_PROJECT=your-actual-project-id
```

## Step 3: Secure the Environment

### 3.1 Generate Secure Secret Key
```bash
cd k:\Devops\PipeGuard-1
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```
Copy the output to your `.env` file.

### 3.2 Create Credentials Directory
```bash
mkdir credentials
# Move your service account key here
```

### 3.3 Update .gitignore
Ensure these lines are in `.gitignore`:
```
.env
credentials/
*.json
```

## Step 4: Test the Real Environment

### 4.1 Install Dependencies
```bash
pip install -r requirements.txt
```

### 4.2 Run Security Check
```bash
python security_check.py
```

### 4.3 Test GitHub Connection
```bash
python -c "
import os
from dotenv import load_dotenv
import requests

load_dotenv()
token = os.getenv('GITHUB_TOKEN')
user = os.getenv('GITHUB_USER')
repo = os.getenv('GITHUB_REPO')

if not all([token, user, repo]):
    print('❌ Missing GitHub configuration')
    exit(1)

url = f'https://api.github.com/repos/{user}/{repo}/actions/runs'
headers = {'Authorization': f'token {token}'}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    print('✅ GitHub API connection successful')
    print(f'Found {len(response.json().get(\"workflow_runs\", []))} workflow runs')
else:
    print(f'❌ GitHub API error: {response.status_code}')
"
```

### 4.4 Test Google Cloud Connection
```bash
python -c "
import os
from dotenv import load_dotenv
from google.cloud import firestore

load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

try:
    db = firestore.Client()
    collections = list(db.collections())
    print('✅ Firestore connection successful')
    print(f'Found {len(collections)} collections')
except Exception as e:
    print(f'❌ Firestore connection failed: {e}')
"
```

## Step 5: Run PipeGuard with Real Data

### 5.1 Start the Application
```bash
python run_local.py
```
Choose option 1 to start the Flask dashboard.

### 5.2 Access the Dashboard
Visit: http://localhost:8080

The dashboard will now display real data from your GitHub repository!

## Step 6: Deploy to Production (Optional)

### 6.1 Deploy to App Engine
```bash
gcloud app deploy app.yaml
```

### 6.2 Deploy Cloud Function
```bash
gcloud functions deploy monitor_pipeline \
    --runtime python39 \
    --trigger-topic pipeline-monitor \
    --entry-point main \
    --source .
```

### 6.3 Set up Cloud Scheduler
```bash
gcloud scheduler jobs create http pipeline-monitor-job \
    --schedule="*/5 * * * *" \
    --uri="https://your-project.cloudfunctions.net/monitor_pipeline" \
    --http-method=GET
```

## 🔧 Troubleshooting

### Common Issues

**GitHub API Rate Limiting**
- Solution: Use authenticated requests (token required)
- Rate limit: 5,000 requests/hour with token

**Firestore Permission Denied**
- Check service account has correct roles
- Verify GOOGLE_APPLICATION_CREDENTIALS path

**Port Already in Use**
- Change FLASK_PORT in .env file
- Or run: `python run_local.py` and choose different port

### Security Best Practices

✅ **Never commit .env files**
✅ **Rotate GitHub tokens regularly**
✅ **Use least-privilege IAM roles**
✅ **Enable 2FA on all accounts**
✅ **Monitor API usage**

## 📞 Support

If you encounter issues:
1. Check `python security_check.py` output
2. Review logs in `python run_local.py`
3. Verify credentials are correctly set
4. Test individual components with the test scripts above

---

**🎯 You're now ready to monitor real GitHub Actions pipelines with PipeGuard!**
