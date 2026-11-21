from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/notify", methods=["POST"])
def notify():
    data = request.get_json()

    print("New notification received!")
    print(data)

    return jsonify({
        "message": "Notification received successfully"
    }), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)