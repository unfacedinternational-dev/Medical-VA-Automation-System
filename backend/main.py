from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload
from .database import Base, engine, get_db
from .models import Patient, Appointment, Billing, Insurance, Task, FollowUp, Note, Activity
from .crud import patient_detail, patient_summary, appointment_status, task_status, followup_status, log

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Medical VA Automation System")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

class PatientCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    age: int = Field(ge=0, le=130)
    gender: str = Field(min_length=1, max_length=50)
class AppointmentCreate(BaseModel):
    scheduled_for: datetime
    provider: str | None = None
    notes: str | None = None
class BillingCreate(BaseModel):
    amount: int = Field(ge=0)
    status: str = "WAITING"
    description: str | None = None
class InsuranceCreate(BaseModel):
    provider: str
    policy_number: str | None = None
    group_number: str | None = None
    eligibility: str | None = None
    verification_date: datetime | None = None
    status: str = "WAITING FOR VERIFICATION"
    notes: str | None = None
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    due_date: datetime | None = None
    status: str = "OPEN"
class FollowUpCreate(BaseModel):
    reason: str = Field(min_length=1, max_length=250)
    followup_date: datetime
    notes: str | None = None
class NoteCreate(BaseModel):
    author_role: str
    note_type: str
    content: str = Field(min_length=1)

@app.get("/health")
def health(): return {"status":"ok"}

@app.post("/patients")
def create_patient(data: PatientCreate, db: Session = Depends(get_db)):
    patient=Patient(**data.model_dump()); db.add(patient); db.flush(); log(db,"va","Added patient","patient",patient.id); db.commit(); db.refresh(patient); return patient_summary(patient)

@app.get("/patients")
def list_patients(db: Session = Depends(get_db)):
    patients=db.query(Patient).options(joinedload(Patient.appointments),joinedload(Patient.billings),joinedload(Patient.insurances)).all()
    return [patient_summary(p) for p in patients]

@app.get("/patients/{patient_id}")
def patient_record(patient_id:int, db:Session=Depends(get_db)):
    p=db.query(Patient).options(joinedload(Patient.appointments),joinedload(Patient.billings),joinedload(Patient.insurances),joinedload(Patient.tasks),joinedload(Patient.followups),joinedload(Patient.notes)).filter(Patient.id==patient_id).first()
    if not p: raise HTTPException(404,"Patient not found")
    return patient_detail(p)

@app.post("/patients/{patient_id}/appointments")
def add_appointment(patient_id:int,data:AppointmentCreate,db:Session=Depends(get_db)):
    if not db.get(Patient,patient_id): raise HTTPException(404,"Patient not found")
    item=Appointment(patient_id=patient_id,**data.model_dump()); db.add(item); db.flush(); log(db,"va","Created appointment","appointment",item.id); db.commit(); db.refresh(item); return {"id":item.id,"scheduled_for":item.scheduled_for,"status":appointment_status(item)}

@app.post("/patients/{patient_id}/appointments/{appointment_id}/complete")
def complete_appointment(patient_id:int,appointment_id:int,db:Session=Depends(get_db)):
    item=db.query(Appointment).filter(Appointment.id==appointment_id,Appointment.patient_id==patient_id).first()
    if not item: raise HTTPException(404,"Appointment not found")
    item.status="COMPLETED"; log(db,"va","Marked appointment completed","appointment",item.id); db.commit(); return {"status":"COMPLETED","next_step":"Review billing and insurance"}

@app.post("/patients/{patient_id}/billing")
def add_billing(patient_id:int,data:BillingCreate,db:Session=Depends(get_db)):
    if not db.get(Patient,patient_id): raise HTTPException(404,"Patient not found")
    item=Billing(patient_id=patient_id,**data.model_dump()); db.add(item); db.flush(); log(db,"va","Created billing record","billing",item.id); db.commit(); db.refresh(item); return item

@app.patch("/patients/{patient_id}/billing/{billing_id}")
def update_billing(patient_id:int,billing_id:int,status:str,db:Session=Depends(get_db)):
    item=db.query(Billing).filter(Billing.id==billing_id,Billing.patient_id==patient_id).first()
    if not item: raise HTTPException(404,"Billing record not found")
    if status not in {"PAID","WAITING","NOT PAID","Pending","Claim Submitted","Partially Paid","Denied","Cancelled"}: raise HTTPException(400,"Invalid billing status")
    item.status=status; log(db,"va",f"Billing changed to {status}","billing",item.id); db.commit(); return item

@app.post("/patients/{patient_id}/insurance")
def add_insurance(patient_id:int,data:InsuranceCreate,db:Session=Depends(get_db)):
    if not db.get(Patient,patient_id): raise HTTPException(404,"Patient not found")
    item=Insurance(patient_id=patient_id,**data.model_dump()); db.add(item); db.flush(); log(db,"va","Added insurance record","insurance",item.id); db.commit(); db.refresh(item); return item

@app.post("/patients/{patient_id}/tasks")
def add_task(patient_id:int,data:TaskCreate,db:Session=Depends(get_db)):
    if not db.get(Patient,patient_id): raise HTTPException(404,"Patient not found")
    item=Task(patient_id=patient_id,**data.model_dump()); db.add(item); db.flush(); log(db,"va","Created task","task",item.id); db.commit(); db.refresh(item); return {"id":item.id,"title":item.title,"status":task_status(item)}

@app.post("/patients/{patient_id}/followups")
def add_followup(patient_id:int,data:FollowUpCreate,db:Session=Depends(get_db)):
    if not db.get(Patient,patient_id): raise HTTPException(404,"Patient not found")
    item=FollowUp(patient_id=patient_id,**data.model_dump()); db.add(item); db.flush(); log(db,"va","Created follow-up","followup",item.id); db.commit(); db.refresh(item); return {"id":item.id,"reason":item.reason,"status":followup_status(item)}

@app.post("/patients/{patient_id}/notes")
def add_note(patient_id:int,data:NoteCreate,db:Session=Depends(get_db)):
    if not db.get(Patient,patient_id): raise HTTPException(404,"Patient not found")
    if data.note_type not in {"MY NOTES","EMPLOYER NOTES","SHARED NOTES"}: raise HTTPException(400,"Invalid note type")
    item=Note(patient_id=patient_id,**data.model_dump()); db.add(item); db.flush(); log(db,data.author_role,"Added note","note",item.id); db.commit(); db.refresh(item); return item

@app.get("/activity")
def activity(db:Session=Depends(get_db)):
    return db.query(Activity).order_by(Activity.created_at.desc()).limit(200).all()
