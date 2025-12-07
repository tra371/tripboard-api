from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.models import Participant, Trip
from schemas.participants import ParticipantCreate, ParticipantUpdate
from services.trip_service import get_trip_or_404


def get_participant_or_404(trip_slug: str, id: int, db: Session) -> Participant:
    participant = (
        db.query(Participant)
        .filter(Participant.id == id, Participant.trip.has(Trip.slug == trip_slug))
        .first()
    )
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found",
        )
    return participant


def get_participant_by_id(trip_slug: str, id: int, db: Session):
    return get_participant_or_404(trip_slug, id, db)


def add_participant_to_trip(
    trip_slug: str, data: ParticipantCreate, db: Session
) -> Participant:
    trip = get_trip_or_404(trip_slug, db)
    existing = (
        db.query(Participant)
        .filter(
            Participant.trip_id == trip.id,
            func.lower(func.trim(Participant.name)) == data.name.lower().strip(),
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participant with the same name already exists in this trip",
        )
    participant = Participant(name=data.name, trip_id=trip.id)
    db.add(participant)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participant with the same name already exists in this trip",
        )
    db.refresh(participant)
    return participant


def update_participant_by_id(
    trip_slug: str, id: int, data: ParticipantUpdate, db: Session
) -> Participant:
    participant = get_participant_or_404(trip_slug, id, db)

    participant.name = data.name
    participant.updated_at = datetime.now(tz=timezone.utc)
    db.commit()
    db.refresh(participant)
    return participant


def delete_participant_by_id(trip_slug: str, id: int, db: Session) -> None:
    participant = get_participant_or_404(trip_slug, id, db)

    db.delete(participant)
    db.commit()
