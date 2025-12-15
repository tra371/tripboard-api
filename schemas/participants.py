from datetime import datetime

from fastapi import Form
from pydantic import BaseModel, field_serializer, ConfigDict


class ParticipantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
    updated_at: datetime | None = None

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, v: datetime | None, info) -> str | None:
        if v is None:
            return None
        return v.astimezone().strftime("%Y-%m-%d %H:%M")


class ParticipantCreate(BaseModel):
    name: str

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),  # type: ignore[name-defined]
    ) -> "ParticipantCreate":
        return cls(name=name)


class ParticipantUpdate(BaseModel):
    name: str

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),  # type: ignore[name-defined]
    ) -> "ParticipantUpdate":
        return cls(name=name)
