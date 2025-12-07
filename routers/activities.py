from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.db import get_db
from schemas.activities import ActivityCreate, ActivityOut, ActivityUpdate
from services.activity_service import (
    add_activity_to_calendar,
    delete_activity_by_slug,
    get_activity_by_slug,
    update_activity_by_slug,
    add_participant_to_activity,
    remove_participant_from_activity,
)

router = APIRouter(
    tags=["activities"],
)

DBSession = Annotated[Session, Depends(get_db)]


@router.get("/{activity_slug}", response_model=ActivityOut)
async def read_activity(calendar_id: int, activity_slug: str, db: DBSession):
    activity = get_activity_by_slug(calendar_id, activity_slug, db)
    return activity


@router.post("/", response_model=ActivityOut)
async def create_activity(
    trip_slug: str,
    calendar_id: int,
    data: Annotated[ActivityCreate, Depends(ActivityCreate.as_form)],
    db: DBSession,
):
    activity = add_activity_to_calendar(trip_slug, calendar_id, data, db)
    return activity


@router.post("/{activity_slug}/add_participant/{participant_id}", response_model=ActivityOut)
async def create_participant_in_activity(
    trip_slug: str,
    calendar_id: int,
    activity_slug: str,
    participant_id: int,
    db: DBSession,
):
    activity = add_participant_to_activity(trip_slug, calendar_id, activity_slug, participant_id, db)
    return activity

@router.post("/{activity_slug}/remove_participant/{participant_id}", response_model=ActivityOut)
async def delete_participant_in_activity(
    trip_slug: str,
    calendar_id: int,
    activity_slug: str,
    participant_id: int,
    db: DBSession,
):
    activity = remove_participant_from_activity(trip_slug, calendar_id, activity_slug, participant_id, db)
    return activity


@router.put("/{activity_slug}", response_model=ActivityOut)
async def update_activity(
    calendar_id: int,
    activity_slug: str,
    data: Annotated[ActivityUpdate, Depends(ActivityUpdate.as_form)],
    db: DBSession,
):
    activity = update_activity_by_slug(calendar_id, activity_slug, data, db)
    return activity


@router.delete("/{activity_slug}", status_code=204)
async def delete_activity(calendar_id: int, activity_slug: str, db: DBSession):
    delete_activity_by_slug(calendar_id, activity_slug, db)
