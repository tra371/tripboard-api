from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.models import Trip
from schemas.trips import TripOut


# Create and persist a sample trip to test participants
@pytest.fixture(scope="session")
def trip(db_session: Session) -> TripOut:
    """Create one trip in the test DB, shared across participant tests."""
    trip = Trip(
        title="Chaung Thar Trip",
        slug="chaung-thar-trip",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(trip)
    db_session.commit()
    db_session.refresh(trip)

    return TripOut.model_validate(trip)


BASE_URL = "/api/v1/trips"


def test_create_participant(client: TestClient, trip: TripOut):
    trip_slug = trip.slug
    resp = client.post(
        f"{BASE_URL}/{trip_slug}/participants",
        data={"name": "john doe"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "john doe"


def test_participant_crud_flow(client: TestClient, trip: TripOut):
    trip_slug = trip.slug
    # Create
    create = client.post(
        f"{BASE_URL}/{trip_slug}/participants",
        data={"name": "mary jane"},
    )
    assert create.status_code == 200
    participant = create.json()
    id = participant["id"]

    # Create with same name variants
    create_conflict_400 = client.post(
        f"{BASE_URL}/{trip_slug}/participants",
        data={"name": "mary jane"},
    )
    assert create_conflict_400.status_code == 400

    create_conflict_different_case_400 = client.post(
        f"{BASE_URL}/{trip_slug}/participants",
        data={"name": "MARY Jane"},
    )
    assert create_conflict_different_case_400.status_code == 400

    create_conflict_whitespace_400 = client.post(
        f"{BASE_URL}/{trip_slug}/participants",
        data={"name": " mary jane "},
    )
    assert create_conflict_whitespace_400.status_code == 400

    # Read single
    read = client.get(f"{BASE_URL}/{trip_slug}/participants/{id}")
    assert read.status_code == 200
    assert read.json()["id"] == id

    # Update
    update = client.put(
        f"{BASE_URL}/{trip_slug}/participants/{id}",
        data={"name": "anya"},
    )
    assert update.status_code == 200
    updated = update.json()
    assert updated["name"] == "anya"

    # Delete
    delete = client.delete(f"{BASE_URL}/{trip_slug}/participants/{id}")
    assert delete.status_code == 204

    # Ensure gone
    read_again = client.get(f"{BASE_URL}/{trip_slug}/participants/{id}")
    assert read_again.status_code == 404
