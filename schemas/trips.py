from datetime import datetime

from fastapi import Form
from pydantic import BaseModel, field_serializer, ConfigDict

from schemas.calendars import CalendarOut
from schemas.participants import ParticipantOut


class TripOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    slug: str
    is_active: bool
    calendars: list[CalendarOut]
    participants: list[ParticipantOut]
    created_at: datetime
    updated_at: datetime | None = None

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, v: datetime | None, info) -> str | None:
        if v is None:
            return None
        return v.astimezone().strftime("%Y-%m-%d %H:%M")


class TripCreate(BaseModel):
    title: str
    is_active: bool = False

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),  # type: ignore[name-defined]
        is_active: bool | None = Form(False)
    ) -> "TripCreate":
        return cls(
            title=title,
            is_active=is_active if is_active is not None else False
        )


class TripUpdate(BaseModel):
    title: str
    is_active: bool = False

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),  # type: ignore[name-defined]
        is_active: bool | None = Form(False)
    ) -> "TripUpdate":
        return cls(
            title=title,
            is_active=is_active if is_active is not None else False
        )
