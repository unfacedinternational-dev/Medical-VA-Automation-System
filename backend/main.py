from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import Patient, Appointment, Billing, Insurance

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Medical VA Automation System")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

class PatientCreate(BaseModel):
    full_name: str
    age: int
    gender: str

class AppointmentCreate(BaseModel):
    scheduled_for: datetime
    provider: str | None = None
    notes: str | None = None

class BillingCreate(BaseModel):
    amount: int
    status: str = "WAITING"
    description: str | None = None

class InsuranceCreate(BaseModel):
    provider: str
    policy_number: str | None = None
    status: str = "WAITING FOR VERIFICATION"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/patients")
def create_patient(data: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(**data.model_dump())
    db.add(patient); db.commit(); db.refresh(patient)
    return patient

@app.get("/patients")
def list_patients(db: Session = Depends(get_db)):
    return db.query(Patient).order_by(Patient.full_name).all()

@app.get("/patients/{patient_id}")
def patient_record(patient_id: int, db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)
    if not patient: raise HTTPException(404, "Patient not found")
    return patient

@app.post("/patients/{patient_id}/appointments")
def add_appointment(patient_id: int, data: AppointmentCreate, db: Session = Depends(get_db)):
    if not db.get(Patient, patient_id): raise HTTPException(404, "Patient not found")
    item = Appointment(patient_id=patient_id, **data.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@app.post("/patients/{patient_id}/billing")
def add_billing(patient_id: int, data: BillingCreate, db: Session = Depends(get_db)):
    if not db.get(Patient, patient_id): raise HTTPException(404, "Patient not found")
    item = Billing(patient_id=patient_id, **data.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@app.post("/patients/{patient_id}/insurance")
def add_insurance(patient_id: int, data: InsuranceCreate, db: Session = Depends(get_db)):
    if not db.get(Patient, patient_id): raise HTTPException(404, "Patient not found")
    item = Insurance(patient_id=patient_id, **data.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item
