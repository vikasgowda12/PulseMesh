import json

from confluent_kafka import Producer

from app.core.config import settings


producer = Producer({
    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
})


def publish_incident_created(incident):
    event = {
        "event_type": "incident.created",
        "incident_id": incident.id,
        "service_name": incident.service_name,
        "severity": incident.severity,
        "status": incident.status,
        "description": incident.description,
        "created_at": incident.created_at.isoformat(),
    }

    producer.produce(
        topic=settings.KAFKA_TOPIC,
        key=str(incident.id),
        value=json.dumps(event),
    )

    producer.flush(timeout=10)

    print(f"Published incident.created event for incident {incident.id}")
