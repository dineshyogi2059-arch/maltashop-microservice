from flask import Flask, request, jsonify
import requests
import uuid

app = Flask(__name__)

NOTIFICATION_URL = "http://notification-service:5001/notify"

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    order_id = str(uuid.uuid4())

    order = {
        "order_id": order_id,
        "product": data.get("product"),
        "status": "confirmed"
    }

    try:
        requests.post(
            NOTIFICATION_URL,
            json={"event": "order_created", "order": order},
            timeout=3
        )
    except requests.RequestException as error:
        print(f"Notification service unavailable: {error}")

    return jsonify(order), 201

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)