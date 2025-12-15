from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.models import Trip
from core.slugs import slugify_trip
from schemas.trips import TripCreate, TripUpdate


def get_trip_or_404(slug: str, db: Session) -> Trip:
    trip = db.query(Trip).filter(Trip.slug == slug).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )
    return trip


def get_all_trips(db: Session):
    return db.query(Trip).all()


def get_trip_by_slug(slug: str, db: Session):
    return get_trip_or_404(slug, db)


def get_active_trip(db: Session) -> Trip | None:
    print("inside service")
    active_trip = db.query(Trip).filter(Trip.is_active.is_(True)).first()
    print(active_trip)
    return active_trip


def insert_trip(data: TripCreate, db: Session) -> Trip:
    slug = slugify_trip(data.title)

    # For now non-english/latin titles are not checked for uniqueness
    existing = db.query(Trip).filter(Trip.slug == slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip with this title already exists",
        )

    if data.is_active:
        db.execute(update(Trip).values(is_active=False))

    trip = Trip(title=data.title, is_active=data.is_active, slug=slug)

    db.add(trip)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip with this slug already exists",
        )
    db.refresh(trip)
    return trip


def update_trip_by_slug(slug: str, data: TripUpdate, db: Session) -> Trip:
    trip = get_trip_or_404(slug, db)
    if data.is_active:
        db.execute(update(Trip).values(is_active=False))
    trip.title = data.title
    trip.slug = slugify_trip(data.title)
    trip.is_active = data.is_active
    trip.updated_at = datetime.now(tz=timezone.utc)
    db.commit()
    db.refresh(trip)
    return trip


def delete_trip_by_slug(slug: str, db: Session) -> None:
    trip = get_trip_or_404(slug, db)

    db.delete(trip)
    db.commit()
