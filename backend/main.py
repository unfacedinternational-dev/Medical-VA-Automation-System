from datetime import datetime
from pathlib import Path
from uuid import uuid4
import os
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload
from .database import Base, engine, get_db
from .models import Patient, Appointment, Billing, Insurance, Task, FollowUp, Note, Activity, PatientDocument
from .crud import patient_detail, patient_summary, appointment_status, task_status, followup_status, log
from .auth import USERS, verify_user, create_access_token, decode_access_token

BASE_DIR=Path(__file__).resolve().parent.parent
FRONTEND=BASE_DIR/"frontend"
STORAGE_ROOT=BASE_DIR/"storage"/"patients"
STORAGE_ROOT.mkdir(parents=True,exist_ok=True)
MAX_FILE_SIZE=25*1024*1024
ALLOWED_EXTENSIONS={".pdf",".png",".jpg",".jpeg",".gif",".webp",".doc",".docx",".xls",".xlsx",".txt"}
INLINE_TYPES={"application/pdf","image/png","image/jpeg","image/gif","image/webp"}
Base.metadata.create_all(bind=engine)
app=FastAPI(title="Medical VA Automation System")
app.add_middleware(CORSMiddleware,allow_origins=os.environ.get("MEDICAL_VA_ALLOWED_ORIGIN","").split(",") if os.environ.get("MEDICAL_VA_ALLOWED_ORIGIN") else [],allow_credentials=True,allow_methods=["GET","POST","PATCH","DELETE"],allow_headers=["Content-Type"])
app.mount("/static",StaticFiles(directory=str(FRONTEND/"static")),name="static")

def current_user(request:Request):
    token=request.cookies.get("medical_va_token")
    username=decode_access_token(token) if token else None
    if username not in USERS: raise HTTPException(401,"Authentication required")
    return USERS[username] | {"username":username}

def require_va(user=Depends(current_user)):
    if user["role"]!="va": raise HTTPException(403,"VA access required")
    return user

class LoginRequest(BaseModel): username:str; password:str
class PatientCreate(BaseModel): full_name:str=Field(min_length=2,max_length=200); age:int=Field(ge=0,le=130); gender:str=Field(min_length=1,max_length=50)
class AppointmentCreate(BaseModel): scheduled_for:datetime; provider:str|None=None; notes:str|None=None
class BillingCreate(BaseModel): amount:int=Field(ge=0); status:str="WAITING"; description:str|None=None
class InsuranceCreate(BaseModel): provider:str; policy_number:str|None=None; group_number:str|None=None; eligibility:str|None=None; verification_date:datetime|None=None; status:str="WAITING FOR VERIFICATION"; notes:str|None=None
class TaskCreate(BaseModel): title:str=Field(min_length=1,max_length=200); description:str|None=None; due_date:datetime|None=None; status:str="OPEN"
class FollowUpCreate(BaseModel): reason:str=Field(min_length=1,max_length=250); followup_date:datetime; notes:str|None=None
class NoteCreate(BaseModel): note_type:str; content:str=Field(min_length=1)

def document_payload(x): return {"id":x.id,"original_name":x.original_name,"content_type":x.content_type,"file_size":x.file_size,"uploaded_by":x.uploaded_by,"created_at":x.created_at,"view_url":f"/documents/{x.id}/view","download_url":f"/documents/{x.id}/download"}

@app.get("/",response_class=HTMLResponse)
def home(): return (FRONTEND/"templates"/"index.html").read_text(encoding="utf-8")
@app.get("/dashboard",response_class=HTMLResponse)
def dashboard(user=Depends(current_user)): return (FRONTEND/"static"/"dashboard.html").read_text(encoding="utf-8")
@app.post("/login")
def login(data:LoginRequest,response:Response):
    if data.username not in USERS or not verify_user(data.username,data.password): raise HTTPException(401,"Invalid username or password")
    token=create_access_token(data.username)
    response.set_cookie("medical_va_token",token,max_age=8*60*60,httponly=True,samesite="lax",secure=os.environ.get("MEDICAL_VA_SECURE_COOKIE","1")!="0",path="/")
    return {"username":data.username,"display_name":USERS[data.username]["display_name"],"role":USERS[data.username]["role"]}
@app.post("/logout")
def logout(response:Response): response.delete_cookie("medical_va_token",path="/"); return {"ok":True}
@app.get("/me")
def me(user=Depends(current_user)): return {"username":user["username"],"display_name":user["display_name"],"role":user["role"]}
@app.get("/health")
def health(): return {"status":"ok"}

@app.post("/patients")
def create_patient(data:PatientCreate,db:Session=Depends(get_db),user=Depends(require_va)):
    patient=Patient(**data.model_dump());db.add(patient);db.flush();log(db,"va","Added patient","patient",patient.id);db.commit();db.refresh(patient);return patient_summary(patient)
@app.get("/patients")
def list_patients(db:Session=Depends(get_db),user=Depends(current_user)):
    patients=db.query(Patient).options(joinedload(Patient.appointments),joinedload(Patient.billings),joinedload(Patient.insurances)).all();return [patient_summary(p) for p in patients]
@app.get("/patients/{patient_id}")
def patient_record(patient_id:int,db:Session=Depends(get_db),user=Depends(current_user)):
    p=db.query(Patient).options(joinedload(Patient.appointments),joinedload(Patient.billings),joinedload(Patient.insurances),joinedload(Patient.tasks),joinedload(Patient.followups),joinedload(Patient.notes),joinedload(Patient.documents)).filter(Patient.id==patient_id).first()
    if not p: raise HTTPException(404,"Patient not found")
    return patient_detail(p)
@app.post("/patients/{patient_id}/appointments")
def add_appointment(patient_id:int,data:AppointmentCreate,db:Session=Depends(get_db),user=Depends(require_va)):
    if not db.get(Patient,patient_id): raise HTTPException(404,"Patient not found")
    item=Appointment(patient_id=patient_id,**data.model_dump());db.add(item);db.flush();log(db,"va","Created appointment","appointment",item.id);db.commit();db.refresh(item);return {"id":item.id,"scheduled_for":item.scheduled_for,"status":appointment_status(item)}
@app.post("/patients/{patient_id}/appointments/{appointment_id}/complete")
def complete_appointment(patient_id:int,appointment_id:int,db:Session=Depends(get_db),user=Depends(require_va)):
    item=db.query(Appointment).filter(Appointment.id==appointment_id,Appointment.patient_id==patient_id).first()
    if not item: raise HTTPException(404,"Appointment not found")
    item.status="COMPLETED";log(db,"va","Marked appointment completed","appointment",item.id);db.commit();return {"status":"COMPLETED","next_step":"Review billing and insurance"}
@app.post("/patients/{patient_id}/billing")
def add_billing(patient_id:int,data:BillingCreate,db:Session=Depends(get_db),user=Depends(require_va)):
    if not db.get(Patient,patient_id): raise HTTPException(404,"Patient not found")
    item=Billing(patient_id=patient_id,**data.model_dump());db.add(item);db.flush();log(db,"va","Created billing record","billing",item.id);db.commit();db.refresh(item);return item
@app.patch("/patients/{patient_id}/billing/{billing_id}")
def update_billing(patient_id:int,billing_id:int,status:str,db:Session=Depends(get_db),user=Depends(require_va)):
    item=db.query(Billing).filter(Billing.id==billing_id,Billing.patient_id==patient_id).first()
    if not item: raise HTTPException(404,"Billing record not found")
    if status not in {"PAID","WAITING","NOT PAID","Pending","Claim Submitted","Partially Paid","Denied","Cancelled"}: raise HTTPException(400,"Invalid billing status")
    item.status=status;log(db,"va",f"Billing changed to {status}","billing",item.id);db.commit();return item
@app.post("/patients/{patient_id}/insurance")
def add_insurance(patient_id:int,data:InsuranceCreate,db:Session=Depends(get_db),user=Depends(require_va)):
    if not db.get(Patient,patient_id): raise HTTPException(404,"Patient not found")
    item=Insurance(patient_id=patient_id,**data.model_dump());db.add(item);db.flush();log(db,"va","Added insurance record","insurance",item.id);db.commit();db.refresh(item);return item
@app.post("/patients/{patient_id}/tasks")
def add_task(patient_id:int,data:TaskCreate,db:Session=Depends(get_db),user=Depends(require_va)):
    if not db.get(Patient,patient_id): raise HTTPException(404,"Patient not found")
    item=Task(patient_id=patient_id,**data.model_dump());db.add(item);db.flush();log(db,"va","Created task","task",item.id);db.commit();db.refresh(item);return {"id":item.id,"title":item.title,"status":task_status(item)}
@app.post("/patients/{patient_id}/followups")
def add_followup(patient_id:int,data:FollowUpCreate,db:Session=Depends(get_db),user=Depends(require_va)):
    if not db.get(Patient,patient_id): raise HTTPException(404,"Patient not found")
    item=FollowUp(patient_id=patient_id,**data.model_dump());db.add(item);db.flush();log(db,"va","Created follow-up","followup",item.id);db.commit();db.refresh(item);return {"id":item.id,"reason":item.reason,"status":followup_status(item)}
@app.post("/patients/{patient_id}/notes")
def add_note(patient_id:int,data:NoteCreate,db:Session=Depends(get_db),user=Depends(current_user)):
    if not db.get(Patient,patient_id): raise HTTPException(404,"Patient not found")
    allowed={"va":"MY NOTES","employer":"EMPLOYER NOTES"}
    if data.note_type not in {"MY NOTES","EMPLOYER NOTES","SHARED NOTES"}: raise HTTPException(400,"Invalid note type")
    if data.note_type!="SHARED NOTES" and data.note_type!=allowed[user["role"]]: raise HTTPException(403,"You cannot create this note type")
    item=Note(patient_id=patient_id,author_role=user["role"],note_type=data.note_type,content=data.content);db.add(item);db.flush();log(db,user["role"],"Added note","note",item.id);db.commit();db.refresh(item);return item

@app.get("/patients/{patient_id}/documents")
def list_documents(patient_id:int,db:Session=Depends(get_db),user=Depends(current_user)):
    if not db.get(Patient,patient_id): raise HTTPException(404,"Patient not found")
    return [document_payload(x) for x in db.query(PatientDocument).filter(PatientDocument.patient_id==patient_id).order_by(PatientDocument.created_at.desc()).all()]
@app.post("/patients/{patient_id}/documents")
async def upload_document(patient_id:int,file:UploadFile=File(...),db:Session=Depends(get_db),user=Depends(require_va)):
    if not db.get(Patient,patient_id): raise HTTPException(404,"Patient not found")
    original_name=Path(file.filename or "document").name;ext=Path(original_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS: raise HTTPException(400,"Unsupported file type")
    data=await file.read()
    if len(data)>MAX_FILE_SIZE: raise HTTPException(413,"File exceeds 25 MB limit")
    stored_name=f"{uuid4().hex}{ext}";patient_dir=STORAGE_ROOT/str(patient_id);patient_dir.mkdir(parents=True,exist_ok=True);(patient_dir/stored_name).write_bytes(data)
    item=PatientDocument(patient_id=patient_id,original_name=original_name,stored_name=f"{patient_id}/{stored_name}",content_type=file.content_type,file_size=len(data),uploaded_by=user["role"]);db.add(item);db.flush();log(db,user["role"],f"Uploaded document {original_name}","document",item.id);db.commit();db.refresh(item);return document_payload(item)
def get_document(document_id,db):
    item=db.get(PatientDocument,document_id)
    if not item: raise HTTPException(404,"Document not found")
    path=STORAGE_ROOT/item.stored_name
    if not path.is_file(): raise HTTPException(404,"Stored file not found")
    return item,path
@app.get("/documents/{document_id}/view")
def view_document(document_id:int,db:Session=Depends(get_db),user=Depends(current_user)):
    item,path=get_document(document_id,db);disposition="inline" if item.content_type in INLINE_TYPES else "attachment";return FileResponse(path,media_type=item.content_type or "application/octet-stream",filename=item.original_name,content_disposition_type=disposition)
@app.get("/documents/{document_id}/download")
def download_document(document_id:int,db:Session=Depends(get_db),user=Depends(current_user)):
    item,path=get_document(document_id);return FileResponse(path,media_type=item.content_type or "application/octet-stream",filename=item.original_name)
@app.delete("/documents/{document_id}")
def delete_document(document_id:int,db:Session=Depends(get_db),user=Depends(require_va)):
    item,path=get_document(document_id,db);name=item.original_name;patient_id=item.patient_id;path.unlink();db.delete(item);log(db,user["role"],f"Deleted document {name}","document",document_id);db.commit();return {"deleted":True,"patient_id":patient_id}
@app.get("/activity")
def activity(db:Session=Depends(get_db),user=Depends(current_user)): return db.query(Activity).order_by(Activity.created_at.desc()).limit(200).all()
