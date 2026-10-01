from concurrent import futures

import grpc

from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import Incident
from app.grpc_service import incident_pb2
from app.grpc_service import incident_pb2_grpc


class IncidentService(incident_pb2_grpc.IncidentServiceServicer):
    def GetIncident(self, request, context):
        db = SessionLocal()

        try:
            incident = db.get(Incident, request.incident_id)

            if incident is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    f"Incident {request.incident_id} not found",
                )

            return incident_pb2.GetIncidentResponse(
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
        finally:
            db.close()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    incident_pb2_grpc.add_IncidentServiceServicer_to_server(
        IncidentService(), server
    )

    address = f"{settings.GRPC_HOST}:{settings.GRPC_PORT}"
    server.add_insecure_port(address)
    server.start()

    print(f"PulseMesh gRPC server listening on {address}")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Stopping PulseMesh gRPC server...")
        server.stop(grace=5).wait()


if __name__ == "__main__":
    serve()
