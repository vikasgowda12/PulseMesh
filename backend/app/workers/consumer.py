import json

from confluent_kafka import Consumer, KafkaError

from app.core.config import settings


def run_consumer():
    consumer = Consumer({
        "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "group.id": "pulsemesh-incident-workers",
        "auto.offset.reset": "earliest",
    })

    consumer.subscribe([settings.KAFKA_TOPIC])

    print("PulseMesh consumer started.")
    print(f"Listening to topic: {settings.KAFKA_TOPIC}")

    try:
        while True:
            message = consumer.poll(1.0)

            if message is None:
                continue

            if message.error():
                if message.error().code() == KafkaError._PARTITION_EOF:
                    continue

                print(f"Kafka error: {message.error()}")
                continue

            try:
                event = json.loads(message.value().decode("utf-8"))
                print("\nReceived incident event:")
                print(json.dumps(event, indent=2))

            except (json.JSONDecodeError, UnicodeDecodeError) as error:
                print(f"Could not decode event: {error}")

    except KeyboardInterrupt:
        print("\nStopping PulseMesh consumer...")

    finally:
        consumer.close()
        print("Consumer stopped.")


if __name__ == "__main__":
    run_consumer()
