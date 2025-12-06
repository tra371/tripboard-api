from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

activity_participant = Table(
    'activity_participant', Base.metadata,
    Column('activity_id', Integer, ForeignKey('activities.id'), primary_key=True),
    Column('participant_id', Integer, ForeignKey('participants.id'), primary_key=True)
)


class Trip(Base):
    __tablename__ = 'trips'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    calendars = relationship('Calendar', back_populates='trip', cascade="all, delete-orphan")


class Calendar(Base):
    __tablename__ = 'calendars'
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime(timezone=True), nullable=False)
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=False)
    trip = relationship('Trip', back_populates='calendars')
    activities = relationship('Activity', back_populates='calendar', cascade="all, delete-orphan")


class Activity(Base):
    __tablename__ = 'activities'
    id = Column(Integer, primary_key=True)
    calendar_id = Column(Integer, ForeignKey('calendars.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    calendar = relationship('Calendar', back_populates='activities')
    expense = relationship('Expense', back_populates='activity', uselist=False)
    participants = relationship('Participant', secondary=activity_participant, back_populates='activities')


class Participant(Base):
    __tablename__ = 'participants'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    activities = relationship('Activity', secondary=activity_participant, back_populates='participants')


class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False)
    activity = relationship('Activity', back_populates='expense', uselist=False)
    payments = relationship('ExpensePayment', back_populates='expense', cascade="all, delete-orphan")
    splits = relationship('ExpenseSplit', back_populates='expense', cascade="all, delete-orphan")

class ExpensePayment(Base):
    __tablename__ = 'expense_payments'
    id = Column(Integer, primary_key=True)
    expense_id = Column(Integer, ForeignKey('expenses.id'), nullable=False)
    participant_id = Column(Integer, ForeignKey('participants.id'), nullable=False)
    amount_paid = Column(Float, nullable=False)
    expense = relationship('Expense', back_populates='payments')
    participant = relationship('Participant')

class ExpenseSplit(Base):
    __tablename__ = 'expense_splits'
    id = Column(Integer, primary_key=True)
    expense_id = Column(Integer, ForeignKey('expenses.id'), nullable=False)
    participant_id = Column(Integer, ForeignKey('participants.id'), nullable=False)
    amount_owed = Column(Float, nullable=False)
    expense = relationship('Expense', back_populates='splits')
    participant = relationship('Participant')