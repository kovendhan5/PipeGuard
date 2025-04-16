from flask import Flask, render_template
from google.cloud import datastore
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route("/")
def dashboard():
    try:
        logger.info("Attempting to connect to Datastore...")
        # Use datastore client instead of firestore since project is in Datastore mode
        db = datastore.Client()
        
        logger.info("Fetching runs from Datastore...")
        query = db.query(kind="runs")
        query.order = ["-timestamp"]
        runs = list(query.fetch(limit=10))
        run_data = [dict(r) for r in runs]
        logger.info(f"Retrieved {len(run_data)} runs from Datastore")
        
        logger.info("Fetching anomalies from Firestore...")
        anomalies = db.collection("anomalies").order_by("run_id", direction=firestore.Query.DESCENDING).limit(5).get()
        anomaly_data = [a.to_dict() for a in anomalies]
        logger.info(f"Retrieved {len(anomaly_data)} anomalies from Firestore")
        
        return render_template("index.html",
                            runs=run_data,
                            anomalies=anomaly_data)
    except Exception as e:
        logger.error(f"Error connecting to Firestore: {str(e)}")
        # If Firestore fails, show a demo page with sample data
        sample_runs = [
            {"id": "12345", "status": "success", "duration": 120},
            {"id": "12346", "status": "failure", "duration": 45}
        ]
        sample_anomalies = [
            {"issue": "Test failure", "fix": "Check test logs", "run_id": "12346"}
        ]
        return render_template("index.html",
                            runs=sample_runs,
                            anomalies=sample_anomalies,
                            error=str(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
