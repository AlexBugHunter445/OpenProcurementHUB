from fastapi.testclient import TestClient
from openprocurementhub_api.main import create_app


def test_health() -> None:
    client=TestClient(create_app())
    assert client.get('/api/v1/health').json() == {'status':'ok'}
