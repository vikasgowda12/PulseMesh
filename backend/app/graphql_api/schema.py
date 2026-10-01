import strawberry
from strawberry.types import Info

from app.db.database import SessionLocal
from app.db.models import Incident


@strawberry.type
class IncidentType:
    id: int
    service_name: str
    severity: str
    status: str
    description: str
    created_at: str
    resolved_at: str


def convert_incident(incident: Incident) -> IncidentType:
    return IncidentType(
        id=incident.id,
        service_name=incident.service_name,
        severity=incident.severity,
        status=incident.status,
        description=incident.description,
        created_at=incident.created_at.isoformat(),
        resolved_at=(
            incident.resolved_at.isoformat()
            if incident.resolved_at
            else ""
        ),
    )


@strawberry.type
class Query:
    @strawberry.field
    def incidents(self, info: Info) -> list[IncidentType]:
        db = SessionLocal()
        try:
            records = (
                db.query(Incident)
                .order_by(Incident.created_at.desc())
                .all()
            )
            return [convert_incident(item) for item in records]
        finally:
            db.close()

    @strawberry.field
    def incident(self, info: Info, id: int) -> IncidentType | None:
        db = SessionLocal()
        try:
            record = db.get(Incident, id)
            return convert_incident(record) if record else None
        finally:
            db.close()


schema = strawberry.Schema(query=Query)
