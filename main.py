from flask import Flask, render_template
from google.cloud import firestore

app = Flask(__name__)

@app.route("/")
def dashboard():
    db = firestore.Client()
    runs = db.collection("runs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).get()
    anomalies = db.collection("anomalies").order_by("run_id", direction=firestore.Query.DESCENDING).limit(5).get()
    return render_template("index.html",
                          runs=[r.to_dict() for r in runs],
                          anomalies=[a.to_dict() for a in anomalies])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
