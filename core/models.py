from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


activity_participant = Table(
    "activity_participant",
    Base.metadata,
    Column(
        "activity_id",
        PG_UUID(as_uuid=True),
        ForeignKey("activities.id"),
        primary_key=True,
    ),
    Column(
        "participant_id",
        Integer,
        ForeignKey("participants.id"),
        primary_key=True,
    ),
)


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    slug: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)

    calendars: Mapped[list[Calendar]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class Calendar(Base):
    __tablename__ = "calendars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dt: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    trip_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("trips.id"),
        nullable=False,
    )
    trip: Mapped[Trip] = relationship(back_populates="calendars")

    activities: Mapped[list[Activity]] = relationship(
        back_populates="calendar",
        cascade="all, delete-orphan",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    slug: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)

    calendar_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("calendars.id"),
        nullable=False,
    )
    calendar: Mapped[Calendar] = relationship(back_populates="activities")

    expense: Mapped[Expense | None] = relationship(
        back_populates="activity",
        uselist=False,
    )

    participants: Mapped[list[Participant]] = relationship(
        secondary=activity_participant,
        back_populates="activities",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    activities: Mapped[list[Activity]] = relationship(
        secondary=activity_participant,
        back_populates="participants",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    slug: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)

    activity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("activities.id"),
        nullable=False,
    )
    activity: Mapped[Activity] = relationship(
        back_populates="expense",
        uselist=False,
    )

    payments: Mapped[list[ExpensePayment]] = relationship(
        back_populates="expense",
        cascade="all, delete-orphan",
    )
    splits: Mapped[list[ExpenseSplit]] = relationship(
        back_populates="expense",
        cascade="all, delete-orphan",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class ExpensePayment(Base):
    __tablename__ = "expense_payments"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    slug: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    expense_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("expenses.id"),
        nullable=False,
    )
    participant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("participants.id"),
        nullable=False,
    )

    amount_paid: Mapped[float] = mapped_column(Float, nullable=False)

    expense: Mapped[Expense] = relationship(back_populates="payments")
    participant: Mapped[Participant] = relationship()

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    slug: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    expense_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("expenses.id"),
        nullable=False,
    )
    participant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("participants.id"),
        nullable=False,
    )

    amount_owed: Mapped[float] = mapped_column(Float, nullable=False)

    expense: Mapped[Expense] = relationship(back_populates="splits")
    participant: Mapped[Participant] = relationship()

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
