from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.db import get_db
from schemas.calendars import CalendarOut, CalendarCreate, CalendarUpdate
from services.calendar_service import (
    get_calendar_by_id,
    add_calendar_to_trip,
    update_calendar_by_id,
    delete_calendar_by_id,
)
from routers import activities

router = APIRouter(
    tags=["calendars"],
)
router.include_router(
    activities.router,
    prefix="/{calendar_id}/activities"
)

DBSession = Annotated[Session, Depends(get_db)]


@router.get("/{calendar_id}", response_model=CalendarOut)
async def read_calendar(trip_slug: str, calendar_id: int, db: DBSession):
    calendar = get_calendar_by_id(trip_slug, calendar_id, db)
    return calendar


@router.post("/", response_model=CalendarOut)
async def create_calendar(
    trip_slug: str,
    data: Annotated[CalendarCreate, Depends(CalendarCreate.as_form)],
    db: DBSession,
):
    calendar = add_calendar_to_trip(trip_slug, data, db)
    return calendar


@router.put("/{calendar_id}", response_model=CalendarOut)
async def update_calendar(
    trip_slug: str,
    calendar_id: int,
    data: Annotated[CalendarUpdate, Depends(CalendarUpdate.as_form)],
    db: DBSession,
):
    calendar = update_calendar_by_id(trip_slug, calendar_id, data, db)
    return calendar


@router.delete("/{calendar_id}", status_code=204)
async def delete_calendar(trip_slug: str, calendar_id: int, db: DBSession):
    delete_calendar_by_id(trip_slug, calendar_id, db)
