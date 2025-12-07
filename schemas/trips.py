from datetime import datetime

from fastapi import Form
from pydantic import BaseModel, field_serializer


class TripOut(BaseModel):
    title: str
    slug: str
    created_at: datetime
    updated_at: datetime | None = None

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, v: datetime | None, info) -> str | None:
        if v is None:
            return None
        return v.astimezone().strftime("%Y-%m-%d %H:%M")

    class Config:
        from_attributes = True


class TripCreate(BaseModel):
    title: str

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),  # type: ignore[name-defined]
    ) -> "TripCreate":
        return cls(title=title)


class TripUpdate(BaseModel):
    title: str

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),  # type: ignore[name-defined]
    ) -> "TripUpdate":
        return cls(title=title)
