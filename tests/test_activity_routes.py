from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.models import Calendar, Participant, Trip
from schemas.calendars import CalendarOut
from schemas.participants import ParticipantOut
from schemas.trips import TripOut
from services.trip_service import get_trip_or_404

BASE_URL = "/api/v1/trips"


# Create and persist a sample trip and participants to test activities
@pytest.fixture(scope="session")
def trip(db_session: Session) -> TripOut:
    """Create one trip in the test DB, shared across activity tests."""
    trip = Trip(
        title="Dawei Trip",
        slug="dawei-trip",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(trip)
    db_session.commit()
    db_session.refresh(trip)

    return TripOut.model_validate(trip)


@pytest.fixture(scope="session")
def calendar(db_session: Session, trip: TripOut) -> CalendarOut:
    """Create one calendar in the test DB, shared across activity tests."""
    date_str = "2015-12-29"
    date_obj = date.fromisoformat(date_str)
    trip_ = get_trip_or_404(trip.slug, db_session)
    calendar = Calendar(
        dt=date_obj, created_at=datetime.now(timezone.utc), trip_id=trip_.id
    )
    db_session.add(calendar)
    db_session.commit()
    db_session.refresh(calendar)

    return CalendarOut.model_validate(calendar)


@pytest.fixture(scope="session")
def participant(db_session: Session, trip: TripOut) -> ParticipantOut:
    """Create one participant in the test DB, shared across activity tests."""
    trip_ = get_trip_or_404(trip.slug, db_session)
    participant = Participant(
        name="Anya Taylor Joy", created_at=datetime.now(timezone.utc), trip_id=trip_.id
    )
    db_session.add(participant)
    db_session.commit()
    db_session.refresh(participant)

    return ParticipantOut.model_validate(participant)


def test_create_activity(client: TestClient, trip: TripOut, calendar: CalendarOut):
    resp = client.post(
        f"{BASE_URL}/{trip.slug}/calendars/{calendar.id}/activities",
        data={"title": "Test Activity 0"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Test Activity 0"
    assert "slug" in body


def test_activity_crud_flow(client: TestClient, trip: TripOut, calendar: CalendarOut):
    # Create
    create = client.post(
        f"{BASE_URL}/{trip.slug}/calendars/{calendar.id}/activities",
        data={"title": "Test Activity 1"},
    )
    assert create.status_code == 200
    activity = create.json()
    slug = activity["slug"]

    # Create with same title variants
    create_conflict_400 = client.post(
        f"{BASE_URL}/{trip.slug}/calendars/{calendar.id}/activities",
        data={"title": "test activity 1"},
    )
    assert create_conflict_400.status_code == 400

    create_conflict_different_case_400 = client.post(
        f"{BASE_URL}/{trip.slug}/calendars/{calendar.id}/activities",
        data={"title": "TEST Activity 1"},
    )
    assert create_conflict_different_case_400.status_code == 400

    create_conflict_whitespace_400 = client.post(
        f"{BASE_URL}/{trip.slug}/calendars/{calendar.id}/activities",
        data={"title": " Test Activity 1 "},
    )
    assert create_conflict_whitespace_400.status_code == 400

    # Read single
    read = client.get(
        f"{BASE_URL}/{trip.slug}/calendars/{calendar.id}/activities/{slug}"
    )
    assert read.status_code == 200
    assert read.json()["slug"] == slug

    # Update
    update = client.put(
        f"{BASE_URL}/{trip.slug}/calendars/{calendar.id}/activities/{slug}",
        data={"title": "Updated Activity 1"},
    )
    assert update.status_code == 200
    updated = update.json()
    assert updated["title"] == "Updated Activity 1"
    updated_slug = updated["slug"]
    assert updated_slug != slug
    assert updated_slug == "updated-activity-1"

    # Delete
    delete = client.delete(
        f"{BASE_URL}/{trip.slug}/calendars/{calendar.id}/activities/{updated_slug}"
    )
    assert delete.status_code == 204

    # Ensure gone
    read_again = client.get(
        f"{BASE_URL}/{trip.slug}/calendars/{calendar.id}/activities/{slug}"
    )
    assert read_again.status_code == 404
    # Ensure activity with old slug also gone
    read_again = client.get(
        f"{BASE_URL}/{trip.slug}/calendars/{calendar.id}/activities/{updated_slug}"
    )
    assert read_again.status_code == 404


def test_add_and_remove_participant_in_activity(
    client: TestClient,
    trip: TripOut,
    calendar: CalendarOut,
    participant: ParticipantOut,
):
    # Create an activity
    create = client.post(
        f"{BASE_URL}/{trip.slug}/calendars/{calendar.id}/activities",
        data={"title": "Participant Activity"},
    )
    assert create.status_code == 200
    activity = create.json()
    activity_slug = activity["slug"]

    # Add participant
    add = client.post(
        f"{BASE_URL}/{trip.slug}/calendars/{calendar.id}/activities/{activity_slug}/add_participant/{participant.id}"
    )
    assert add.status_code == 200
    added = add.json()
    assert any(p["id"] == participant.id for p in added["participants"])

    # Adding same participant again
    add_again = client.post(
        f"{BASE_URL}/{trip.slug}/calendars/{calendar.id}/activities/{activity_slug}/add_participant/{participant.id}"
    )
    assert add_again.status_code == 400
    body_again = add_again.json()
    assert body_again["detail"] == "Participant already exists in the activity"

    # Remove participant
    remove = client.post(
        f"{BASE_URL}/{trip.slug}/calendars/{calendar.id}/activities/{activity_slug}/remove_participant/{participant.id}"
    )
    assert remove.status_code == 200
    removed = remove.json()
    assert all(p["id"] != participant.id for p in removed["participants"])

    # Removing again (already not in activity)
    remove_again = client.post(
        f"{BASE_URL}/{trip.slug}/calendars/{calendar.id}/activities/{activity_slug}/remove_participant/{participant.id}"
    )
    assert remove_again.status_code == 400
    body_remove_again = remove_again.json()
    assert body_remove_again["detail"] == "Participant is already not in the activity"
