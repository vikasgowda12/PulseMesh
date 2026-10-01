import grpc

from app.core.config import settings
from app.grpc_service import incident_pb2
from app.grpc_service import incident_pb2_grpc


def get_incident(incident_id: int):
    address = f"{settings.GRPC_HOST}:{settings.GRPC_PORT}"

    with grpc.insecure_channel(address) as channel:
        stub = incident_pb2_grpc.IncidentServiceStub(channel)

        request = incident_pb2.GetIncidentRequest(
            incident_id=incident_id
        )

        response = stub.GetIncident(request)

        print("\nIncident retrieved through gRPC:")
        print(f"ID: {response.id}")
        print(f"Service: {response.service_name}")
        print(f"Severity: {response.severity}")
        print(f"Status: {response.status}")
        print(f"Description: {response.description}")
        print(f"Created at: {response.created_at}")
        print(f"Resolved at: {response.resolved_at or 'Not resolved'}")


if __name__ == "__main__":
    get_incident(3)
