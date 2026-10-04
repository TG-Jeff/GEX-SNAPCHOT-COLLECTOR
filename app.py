from flask import Flask, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "GEX Collector is alive!"

@app.route("/collect")
def collect():
    try:
        result = subprocess.run(
            ["python", "collector.py"],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return jsonify({
                "status": "success",
                "message": "Snapshot collected successfully"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Collector failed"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
