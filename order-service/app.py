
from flask import Flask, request, jsonify
import pika
import json
import uuid
import os

app = Flask(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    order_id = str(uuid.uuid4())
    correlation_id = str(uuid.uuid4())

    order = {
        "order_id": order_id,
        "product": data.get("product"),
        "status": "confirmed",
        "correlation_id": correlation_id
    }

    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        channel = connection.channel()

        channel.queue_declare(queue="order_events", durable=True)

        event = {
            "event": "order_created",
            "order": order,
            "correlation_id": correlation_id
        }

        channel.basic_publish(
            exchange="",
            routing_key="order_events",
            body=json.dumps(event),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        connection.close()

        print(f"Order event published. Correlation ID: {correlation_id}")

    except pika.exceptions.AMQPError as error:
        print(f"RabbitMQ error: {error}")
        return jsonify({"error": "Could not publish order event"}), 503

    return jsonify(order), 201


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
