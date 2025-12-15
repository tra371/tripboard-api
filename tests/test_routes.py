import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_docs_ok():
    r = client.get("/docs")
    assert r.status_code == 200


def test_openapi_ok():
    r = client.get("/openapi.json")
    assert r.status_code == 200
