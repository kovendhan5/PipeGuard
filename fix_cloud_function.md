# filepath: k:\Devops\PipeGuard\fix_cloud_function.md

# Steps to Fix Your Cloud Function

The error in your Cloud Function is that the GitHub token is being treated as a variable name rather than a string. Here's how to fix it:

## 1. Update your Cloud Function directly in Google Cloud Console

1. Go to: https://console.cloud.google.com/functions/details/us-central1/monitor_pipeline?project=pipeguard
2. Click "Edit" button
3. Go to the "Runtime, build, connections and security settings" section
4. Navigate to the "Runtime environment variables" section
5. Make sure your GITHUB_TOKEN is enclosed in quotes if you're updating it

## 2. Create a fixed version of your function and redeploy

```bash
cd ~/pipeguard

# Update main.py file to handle the token properly
cat > main.py << 'EOL'
from monitor_pipeline import monitor_pipeline

# This file imports the monitor_pipeline function so that 
# Google Cloud Functions can find it at deployment time
EOL

# Create fixed monitor_pipeline.py file
cat > monitor_pipeline.py << 'EOL'
import os
import requests
from google.cloud import firestore
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def monitor_pipeline(request):
    try:
        # Get GitHub token from environment variables (properly sanitized)
        GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
        if not GITHUB_TOKEN:
            return "Error: GitHub token not found in environment variables"
        
        # Convert token to string and strip any whitespace
        GITHUB_TOKEN = str(GITHUB_TOKEN).strip()
        
        GITHUB_USER = os.environ.get("GITHUB_USER", "kovendhan5")
        GITHUB_REPO = os.environ.get("GITHUB_REPO", "PipeGuard")
        
        print(f"Fetching data for {GITHUB_USER}/{GITHUB_REPO}")
        
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/actions/runs"
        
        # Fetch GitHub Actions data
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"Error fetching GitHub data: {response.status_code}, {response.text}"
            
        runs = response.json()
        
        # Store workflow data in memory for testing without Firestore
        workflow_data = []
        
        # Process the GitHub Actions data
        for run in runs.get("workflow_runs", []):
            created = datetime.strptime(run["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            updated = datetime.strptime(run["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
            duration = int((updated - created).total_seconds())
            
            run_data = {
                "id": run["id"],
                "status": run["conclusion"],
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            workflow_data.append(run_data)
            
            # Try to store in Firestore if available
            try:
                db = firestore.Client()
                db.collection("runs").add(run_data)
                print(f"Stored run {run['id']} in Firestore")
                
                anomaly = detect_anomaly(run, duration, db)
                if anomaly:
                    db.collection("anomalies").add(anomaly)
                    print(f"Found anomaly in run {run['id']}")
                    workflow_data.append({"anomaly": anomaly})
            except Exception as e:
                print(f"Firestore error: {e}")
                # Continue processing even if Firestore fails
        
        return f"Processed {len(workflow_data)} runs"
    
    except Exception as e:
        print(f"Error in monitor_pipeline: {str(e)}")
        return f"Error in monitor_pipeline: {str(e)}"

def detect_anomaly(run, duration, db):
    try:
        recent = db.collection("runs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).get()
        durations = [r.to_dict()["duration"] for r in recent if "duration" in r.to_dict()]
        avg_duration = sum(durations) / len(durations) if durations else 1
        if duration > 2 * avg_duration:
            return {"issue": "Long build time", "fix": "Optimize resources", "run_id": run["id"]}
    except Exception as e:
        print(f"Error calculating duration anomalies: {e}")
        # Continue to check for failure regardless of duration anomaly detection errors
    
    if run["conclusion"] == "failure":
        return {"issue": "Test failure", "fix": "Check test logs", "run_id": run["id"]}
    return None
EOL

# Redeploy your Cloud Function
gcloud functions deploy monitor_pipeline \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --source=$(pwd) \
  --set-env-vars GITHUB_USER=kovendhan5,GITHUB_REPO=PipeGuard,GITHUB_TOKEN="your_token_here"
```

Replace `"your_token_here"` with your actual GitHub token, making sure to keep the quotes.

## 3. Test your function manually

After redeploying the fixed function, test it by running:

```bash
curl https://us-central1-pipeguard.cloudfunctions.net/monitor_pipeline
```

## 4. Update your app.py to fix any issues on the dashboard side

If you're still seeing sample data on your dashboard after fixing the Cloud Function, check the dashboard logs:

```bash
gcloud app logs read
```

This should help identify any remaining issues with your Flask app's connection to Firestore.
