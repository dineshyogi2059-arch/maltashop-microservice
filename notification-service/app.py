
from flask import Flask, jsonify
import pika
import json
import os
import threading
import sqlite3
app = Flask(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
DB_PATH = "/app/data/notifications.db"
os.makedirs("/app/data", exist_ok=True)

def init_db():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            product TEXT,
            correlation_id TEXT
        )
    """)

    connection.commit()
    connection.close()

init_db()

def receive_messages():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            channel = connection.channel()

            channel.queue_declare(queue="order_events", durable=True)

            def callback(ch, method, properties, body):
                event = json.loads(body)
                correlation_id = event["correlation_id"]
                order = event["order"]

                connection = sqlite3.connect(DB_PATH)
                cursor = connection.cursor()

                cursor.execute(
                    """
                    INSERT INTO notifications (order_id, product, correlation_id)
                    VALUES (?, ?, ?)
                    """,
                    (order["order_id"], order["product"], correlation_id)
                )

                connection.commit()
                connection.close()

                print("New order notification received!")
                print(f"Order: {order['order_id']}")
                print(f"Product: {order['product']}")
                print(f"Correlation ID: {correlation_id}")

                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue="order_events",
                on_message_callback=callback
            )

            print("Waiting for order events...")
            channel.start_consuming()

        except pika.exceptions.AMQPError as error:
            print(f"RabbitMQ connection error: {error}")
            import time
            time.sleep(5)




@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    consumer_thread = threading.Thread(
        target=receive_messages,
        daemon=True
    )
    consumer_thread.start()

    app.run(host="0.0.0.0", port=5001)
