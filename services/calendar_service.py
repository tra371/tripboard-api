from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.models import Calendar, Trip
from schemas.calendars import CalendarCreate, CalendarUpdate
from services.trip_service import get_trip_or_404


def get_calendar_or_404(trip_slug: str, id: int, db: Session) -> Calendar:
    calendar = (
        db.query(Calendar)
        .filter(Calendar.id == id, Calendar.trip.has(Trip.slug == trip_slug))
        .first()
    )
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found",
        )
    return calendar


def get_calendar_by_id(trip_slug: str, id: int, db: Session):
    return get_calendar_or_404(trip_slug, id, db)


def add_calendar_to_trip(
    trip_slug: str, data: CalendarCreate, db: Session
) -> Calendar:
    trip = get_trip_or_404(trip_slug, db)
    existing = (
        db.query(Calendar)
        .filter(
            Calendar.trip_id == trip.id,
            Calendar.dt == data.dt,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Calendar with the same date already exists in this trip",
        )
    calendar = Calendar(dt=data.dt, trip_id=trip.id)
    db.add(calendar)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Calendar with the same date already exists in this trip",
        )
    db.refresh(calendar)
    return calendar


def update_calendar_by_id(
    trip_slug: str, id: int, data: CalendarUpdate, db: Session
) -> Calendar:
    calendar = get_calendar_or_404(trip_slug, id, db)

    calendar.dt = data.dt
    calendar.updated_at = datetime.now(tz=timezone.utc)
    db.commit()
    db.refresh(calendar)
    return calendar


def delete_calendar_by_id(trip_slug: str, id: int, db: Session) -> None:
    calendar = get_calendar_or_404(trip_slug, id, db)

    db.delete(calendar)
    db.commit()
