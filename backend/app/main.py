from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.events.producer import publish_incident_created
from strawberry.fastapi import GraphQLRouter
from app.graphql_api.schema import schema
from app.db.database import get_db
from app.db.models import Incident


app = FastAPI(
    title="PulseMesh API",
    description="Incident detection and management API",
    version="0.1.0",
)


graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IncidentCreate(BaseModel):
    service_name: str = Field(min_length=1, max_length=100)
    severity: str = Field(default="medium", max_length=20)
    description: str = Field(min_length=1)


class IncidentResponse(BaseModel):
    id: int
    service_name: str
    severity: str
    status: str
    description: str
    created_at: datetime
    resolved_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


@app.get("/")
def root():
    return {"message": "Welcome to PulseMesh API"}


@app.post(
    "/incidents",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db),
):
    incident = Incident(
        service_name=incident_data.service_name,
        severity=incident_data.severity,
        status="open",
        description=incident_data.description,
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    publish_incident_created(incident)

    return incident


@app.get("/incidents", response_model=list[IncidentResponse])
def list_incidents(db: Session = Depends(get_db)):
    return (
        db.query(Incident)
        .order_by(Incident.created_at.desc())
        .all()
    )


@app.get(
    "/incidents/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident


@app.patch(
    "/incidents/{incident_id}/resolve",
    response_model=IncidentResponse,
)
def resolve_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    # Resolve the incident only if it is not already resolved.
    if incident.status != "resolved":
        incident.status = "resolved"
        incident.resolved_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(incident)

    return incident