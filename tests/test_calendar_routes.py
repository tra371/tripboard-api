from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.models import Trip
from schemas.trips import TripOut


# Create and persist a sample trip to test calendars
@pytest.fixture(scope="session")
def trip(db_session: Session) -> TripOut:
    """Create one trip in the test DB, shared across calendars tests."""
    trip = Trip(
        title="Ngwe Saung Trip",
        slug="ngwe-saung-trip",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(trip)
    db_session.commit()
    db_session.refresh(trip)

    return TripOut.model_validate(trip)


BASE_URL = "/api/v1/trips"


def test_create_calendar(client: TestClient, trip: TripOut):
    trip_slug = trip.slug
    today = date.today()
    today_str = today.isoformat()
    resp = client.post(
        f"{BASE_URL}/{trip_slug}/calendars",
        data={"dt": today_str},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "dt" in body
    assert body["dt"] == today_str


def test_calendar_crud_flow(client: TestClient, trip: TripOut):
    trip_slug = trip.slug
    test_date = "2024-12-31"
    # Create
    create = client.post(
        f"{BASE_URL}/{trip_slug}/calendars",
        data={"dt": test_date},
    )
    assert create.status_code == 200
    calendar = create.json()
    id = calendar["id"]

    # Create with same date
    create_conflict_400 = client.post(
        f"{BASE_URL}/{trip_slug}/calendars",
        data={"dt": test_date},
    )
    assert create_conflict_400.status_code == 400

    # Read single
    read = client.get(f"{BASE_URL}/{trip_slug}/calendars/{id}")
    assert read.status_code == 200
    assert read.json()["id"] == id

    # Update
    update = client.put(
        f"{BASE_URL}/{trip_slug}/calendars/{id}",
        data={"dt": "2026-01-31"},
    )
    assert update.status_code == 200
    updated = update.json()
    assert updated["dt"] == "2026-01-31"

    # Delete
    delete = client.delete(f"{BASE_URL}/{trip_slug}/calendars/{id}")
    assert delete.status_code == 204

    # Ensure gone
    read_again = client.get(f"{BASE_URL}/{trip_slug}/calendars/{id}")
    assert read_again.status_code == 404
