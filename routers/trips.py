from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.db import get_db
from schemas.trips import TripCreate, TripOut, TripUpdate
from services.trip_service import (
    delete_trip_by_slug,
    get_all_trips,
    get_trip_by_slug,
    insert_trip,
    update_trip_by_slug,
)

router = APIRouter(
    prefix="/trips",
    tags=["trips"],
)

DBSession = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=list[TripOut])
async def read_trips(db: DBSession):
    trips = get_all_trips(db)
    return trips


@router.get("/{slug}", response_model=TripOut)
async def read_trip(slug: str, db: DBSession):
    trip = get_trip_by_slug(slug, db)
    return trip


@router.post("/", response_model=TripOut)
async def create_trip(
    data: Annotated[TripCreate, Depends(TripCreate.as_form)], db: DBSession
):
    trip = insert_trip(data, db)
    return trip


@router.put("/{slug}", response_model=TripOut)
async def update_trip(
    slug: str, data: Annotated[TripUpdate, Depends(TripUpdate.as_form)], db: DBSession
):
    trip = update_trip_by_slug(slug, data, db)
    return trip


@router.delete("/{slug}", status_code=204)
async def delete_trip(slug: str, db: DBSession):
    delete_trip_by_slug(slug, db)
