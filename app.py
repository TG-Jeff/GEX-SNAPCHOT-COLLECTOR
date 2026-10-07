```python
from flask import Flask
import subprocess
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "OK", 200


@app.route("/collect")
def collect():
    try:
        result = subprocess.run(
            ["python", "collector.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=120
        )

        if result.returncode == 0:
            return "OK", 200
        else:
            return "ERROR", 500

    except Exception:
        return "ERROR", 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
```
