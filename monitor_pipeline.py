# filepath: k:\Devops\PipeGuard\monitor_pipeline.py
import os
import requests
import logging
from google.cloud import firestore
from datetime import datetime
from dotenv import load_dotenv

# Configure secure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def monitor_pipeline(request):
    try:
        # Get GitHub token from environment variables (properly sanitized)
        GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
        if not GITHUB_TOKEN:
            logger.error("GitHub token not found in environment variables")
            return "Error: GitHub token not found in environment variables"
        
        # Convert to string and remove any whitespace or invisible characters that might cause API issues
        GITHUB_TOKEN = str(GITHUB_TOKEN).strip()
        # Security: Never log the actual token, only confirm it exists
        logger.info("GitHub token found and configured")
        
        GITHUB_USER = os.environ.get("GITHUB_USER", "kovendhan5")
        GITHUB_REPO = os.environ.get("GITHUB_REPO", "PipeGuard")
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
                
                anomaly = detect_anomaly(run, duration, db)
                if anomaly:
                    db.collection("anomalies").add(anomaly)
                    workflow_data.append({"anomaly": anomaly})
            except Exception as e:
                print(f"Firestore error: {e}")
                # Continue processing even if Firestore fails
        
        return f"Processed {len(workflow_data)} runs"
    
    except Exception as e:
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
