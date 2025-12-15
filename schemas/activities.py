from datetime import datetime

from fastapi import Form
from pydantic import BaseModel, ConfigDict, field_serializer

from schemas.participants import ParticipantOut


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    slug: str
    participants: list[ParticipantOut]
    created_at: datetime
    updated_at: datetime | None = None

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, v: datetime | None, info) -> str | None:
        if v is None:
            return None
        return v.astimezone().strftime("%Y-%m-%d %H:%M")


class ActivityCreate(BaseModel):
    title: str

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),  # type: ignore[name-defined]
    ) -> "ActivityCreate":
        return cls(title=title)


class ActivityUpdate(BaseModel):
    title: str

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),  # type: ignore[name-defined]
    ) -> "ActivityUpdate":
        return cls(title=title)
