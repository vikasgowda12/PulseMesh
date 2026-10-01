import json
import logging

from confluent_kafka import KafkaException, Producer

from app.core.config import settings


logger = logging.getLogger(__name__)
producer = None


def publish_incident_created(incident):
    global producer

    if not settings.KAFKA_BOOTSTRAP_SERVERS.strip():
        logger.warning("Kafka is not configured; incident event was not published")
        return False

    event = {
        "event_type": "incident.created",
        "incident_id": incident.id,
        "service_name": incident.service_name,
        "severity": incident.severity,
        "status": incident.status,
        "description": incident.description,
        "created_at": incident.created_at.isoformat(),
    }

    try:
        if producer is None:
            producer = Producer({
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            })

        delivery_errors = []

        def on_delivery(error, message):
            if error is not None:
                delivery_errors.append(error)

        producer.produce(
            topic=settings.KAFKA_TOPIC,
            key=str(incident.id),
            value=json.dumps(event),
            callback=on_delivery,
        )

        pending = producer.flush(timeout=2)
        if delivery_errors:
            logger.error("Kafka did not deliver incident %s: %s", incident.id, delivery_errors[0])
            return False
        if pending:
            logger.warning("Kafka delivery timed out for incident %s", incident.id)
            return False

        logger.info("Published incident.created event for incident %s", incident.id)
        return True
    except (KafkaException, BufferError, RuntimeError) as error:
        logger.warning("Could not publish incident %s to Kafka: %s", incident.id, error)
        return False
