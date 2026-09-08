from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Patient(Base):
    __tablename__ = "patients"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), index=True)
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    billings = relationship("Billing", back_populates="patient", cascade="all, delete-orphan")
    insurances = relationship("Insurance", back_populates="patient", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="patient", cascade="all, delete-orphan")
    followups = relationship("FollowUp", back_populates="patient", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="patient", cascade="all, delete-orphan")

class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    scheduled_for: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(30), default="APPROACHING")
    provider: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    patient = relationship("Patient", back_populates="appointments")

class Billing(Base):
    __tablename__ = "billing"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="WAITING")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    patient = relationship("Patient", back_populates="billings")

class Insurance(Base):
    __tablename__ = "insurance"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    provider: Mapped[str] = mapped_column(String(200))
    policy_number: Mapped[str | None] = mapped_column(String(200), nullable=True)
    group_number: Mapped[str | None] = mapped_column(String(200), nullable=True)
    eligibility: Mapped[str | None] = mapped_column(String(100), nullable=True)
    verification_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="WAITING FOR VERIFICATION")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    patient = relationship("Patient", back_populates="insurances")

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int | None] = mapped_column(ForeignKey("patients.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="OPEN")
    patient = relationship("Patient", back_populates="tasks")

class FollowUp(Base):
    __tablename__ = "followups"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    reason: Mapped[str] = mapped_column(String(250))
    followup_date: Mapped[datetime] = mapped_column(DateTime)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="Upcoming")
    patient = relationship("Patient", back_populates="followups")

class Note(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int | None] = mapped_column(ForeignKey("patients.id"), nullable=True)
    author_role: Mapped[str] = mapped_column(String(30))
    note_type: Mapped[str] = mapped_column(String(30))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    patient = relationship("Patient", back_populates="notes")

class Activity(Base):
    __tablename__ = "activity"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_role: Mapped[str] = mapped_column(String(30))
    action: Mapped[str] = mapped_column(String(200))
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
