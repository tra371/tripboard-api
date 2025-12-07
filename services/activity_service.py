from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.models import Activity, Calendar, Participant
from core.slugs import slugify_activity
from schemas.activities import ActivityCreate, ActivityUpdate
from services.calendar_service import get_calendar_or_404
from services.participant_service import get_participant_or_404


def get_activity_or_404(calendar_id: int, activity_slug: str, db: Session) -> Activity:
    activity = (
        db.query(Activity)
        .filter(
            Activity.slug == activity_slug,
            Activity.calendar.has(Calendar.id == calendar_id),
        )
        .first()
    )
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )
    return activity


def get_activity_by_slug(calendar_id: int, activity_slug: str, db: Session):
    return get_activity_or_404(calendar_id, activity_slug, db)


def add_activity_to_calendar(
    trip_slug: str, calendar_id: int, data: ActivityCreate, db: Session
) -> Activity:
    calendar = get_calendar_or_404(trip_slug, calendar_id, db)
    slug = slugify_activity(data.title)

    # For now non-english/latin titles are not checked for uniqueness
    existing = (
        db.query(Activity)
        .filter(
            Activity.calendar_id == calendar.id,
            func.lower(func.trim(Activity.title)) == data.title.lower().strip(),
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activity with this title already exists",
        )

    activity = Activity(title=data.title, slug=slug, calendar_id=calendar.id)

    db.add(activity)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activity with this slug already exists",
        )
    db.refresh(activity)
    return activity


def add_participant_to_activity(
    trip_slug: str, calendar_id: int, activity_slug: str, participant_id: int, db: Session
) -> Activity:
    calendar = get_calendar_or_404(trip_slug, calendar_id, db)
    participant = get_participant_or_404(trip_slug, participant_id, db)

    activity = (
        db.query(Activity)
        .filter(
            Activity.slug == activity_slug,
            Activity.calendar_id == calendar.id,
        )
        .first()
    )
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )

    if any(p.id == participant.id for p in activity.participants):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participant already exists in the activity",
        )
    activity.participants.append(participant)
    activity.updated_at = datetime.now(tz=timezone.utc)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participant already exists in the activity",
        )
    db.refresh(activity)
    return activity


def remove_participant_from_activity(
    trip_slug: str, calendar_id: int, activity_slug: str, participant_id: int, db: Session
) -> Activity:
    calendar = get_calendar_or_404(trip_slug, calendar_id, db)
    participant = get_participant_or_404(trip_slug, participant_id, db)
    activity = (
        db.query(Activity)
        .filter(
            Activity.slug == activity_slug,
            Activity.calendar_id == calendar.id,
            Activity.participants.any(Participant.id == participant_id)
        )
        .first()
    )
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participant is already not in the activity",
        )

    activity.participants.remove(participant)
    activity.updated_at = datetime.now(tz=timezone.utc)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong while trying to remove the participant from the activity",
        )
    db.refresh(activity)
    return activity


def update_activity_by_slug(
    calendar_id: int, slug: str, data: ActivityUpdate, db: Session
) -> Activity:
    activity = get_activity_or_404(calendar_id, slug, db)
    activity.title = data.title
    activity.slug = slugify_activity(data.title)
    activity.updated_at = datetime.now(tz=timezone.utc)
    db.commit()
    db.refresh(activity)
    return activity


def delete_activity_by_slug(calendar_id: int, slug: str, db: Session) -> None:
    activity = get_activity_or_404(calendar_id, slug, db)

    db.delete(activity)
    db.commit()
