from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.db import get_db
from schemas.participants import ParticipantCreate, ParticipantOut, ParticipantUpdate
from services.participant_service import (
    add_participant_to_trip,
    delete_participant_by_id,
    get_participant_by_id,
    update_participant_by_id,
)

router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@router.get("/{trip_slug}/participants/{participant_id}", response_model=ParticipantOut)
async def read_participant(trip_slug: str, participant_id: int, db: DBSession):
    participant = get_participant_by_id(trip_slug, participant_id, db)
    return participant


@router.post("/{trip_slug}/participants", response_model=ParticipantOut)
async def create_participant(
    trip_slug: str,
    data: Annotated[ParticipantCreate, Depends(ParticipantCreate.as_form)],
    db: DBSession,
):
    participant = add_participant_to_trip(trip_slug, data, db)
    return participant


@router.put("/{trip_slug}/participants/{participant_id}", response_model=ParticipantOut)
async def update_participant(
    trip_slug: str,
    participant_id: int,
    data: Annotated[ParticipantUpdate, Depends(ParticipantUpdate.as_form)],
    db: DBSession,
):
    participant = update_participant_by_id(trip_slug, participant_id, data, db)
    return participant


@router.delete("/{trip_slug}/participants/{participant_id}", status_code=204)
async def delete_participant(trip_slug: str, participant_id: int, db: DBSession):
    delete_participant_by_id(trip_slug, participant_id, db)
