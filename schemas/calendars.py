from datetime import datetime

from fastapi import Form
from pydantic import BaseModel, field_serializer

from schemas.activities import ActivityOut


class CalendarOut(BaseModel):
    id: int
    dt: datetime
    activities: list[ActivityOut]
    created_at: datetime
    updated_at: datetime | None = None

    @field_serializer("dt")
    def serialize_dt(self, v: datetime | None, info) -> str | None:
        if v is None:
            return None
        return v.astimezone().strftime("%Y-%m-%d")

    class Config:
        from_attributes = True


class CalendarCreate(BaseModel):
    dt: datetime

    @classmethod
    def as_form(
        cls,
        dt: datetime = Form(...),  # type: ignore[name-defined]
    ) -> "CalendarCreate":
        return cls(dt=dt)


class CalendarUpdate(BaseModel):
    dt: datetime

    @classmethod
    def as_form(
        cls,
        dt: datetime = Form(...),  # type: ignore[name-defined]
    ) -> "CalendarUpdate":
        return cls(dt=dt)
