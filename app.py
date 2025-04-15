from flask import Flask, render_template
from google.cloud import firestore
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route("/")
def dashboard():
    try:
        db = firestore.Client()
        runs = db.collection("runs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).get()
        anomalies = db.collection("anomalies").order_by("run_id", direction=firestore.Query.DESCENDING).limit(5).get()
        return render_template("index.html",
                            runs=[r.to_dict() for r in runs],
                            anomalies=[a.to_dict() for a in anomalies])
    except Exception as e:
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
