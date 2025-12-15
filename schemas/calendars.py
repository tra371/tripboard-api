from datetime import date, datetime

from fastapi import Form
from pydantic import BaseModel, ConfigDict, field_serializer

from schemas.activities import ActivityOut


class CalendarOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dt: date
    activities: list[ActivityOut]
    created_at: datetime
    updated_at: datetime | None = None

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, v: datetime | None, info) -> str | None:
        if v is None:
            return None
        return v.astimezone().strftime("%Y-%m-%d %H:%M")


class CalendarCreate(BaseModel):
    dt: date

    @classmethod
    def as_form(
        cls,
        dt: date = Form(...),  # type: ignore[name-defined]
    ) -> "CalendarCreate":
        return cls(dt=dt)


class CalendarUpdate(BaseModel):
    dt: date

    @classmethod
    def as_form(
        cls,
        dt: date = Form(...),  # type: ignore[name-defined]
    ) -> "CalendarUpdate":
        return cls(dt=dt)
