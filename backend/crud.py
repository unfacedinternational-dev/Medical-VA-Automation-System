from datetime import datetime
from sqlalchemy.orm import Session
from .models import Activity, Appointment, Patient, Task, FollowUp

def log(db: Session, actor: str, action: str, entity_type=None, entity_id=None):
    db.add(Activity(actor_role=actor, action=action, entity_type=entity_type, entity_id=entity_id))

def appointment_status(item: Appointment):
    if item.status == "COMPLETED": return "COMPLETED"
    return "PAST DUE" if item.scheduled_for < datetime.utcnow() else "APPROACHING"

def task_status(item: Task):
    if item.status == "COMPLETED": return "COMPLETED"
    return "OVERDUE" if item.due_date and item.due_date < datetime.utcnow() else item.status

def followup_status(item: FollowUp):
    if item.status == "Completed": return "Completed"
    if item.followup_date < datetime.utcnow(): return "Overdue"
    return "Due" if (item.followup_date-datetime.utcnow()).total_seconds() <= 86400 else "Upcoming"

def patient_summary(p: Patient):
    a=sorted(p.appointments,key=lambda x:x.scheduled_for,reverse=True)
    b=sorted(p.billings,key=lambda x:x.id,reverse=True)
    i=sorted(p.insurances,key=lambda x:x.id,reverse=True)
    return {"id":p.id,"full_name":p.full_name,"age":p.age,"gender":p.gender,"appointment":({"date":a[0].scheduled_for,"status":appointment_status(a[0])} if a else None),"billing":({"amount":b[0].amount,"status":b[0].status} if b else None),"insurance":({"provider":i[0].provider,"status":i[0].status} if i else None)}

def patient_detail(p: Patient):
    return {**patient_summary(p),"appointments":[{"id":x.id,"scheduled_for":x.scheduled_for,"status":appointment_status(x),"provider":x.provider,"notes":x.notes} for x in p.appointments],"billings":[{"id":x.id,"amount":x.amount,"status":x.status,"description":x.description} for x in p.billings],"insurances":[{"id":x.id,"provider":x.provider,"policy_number":x.policy_number,"group_number":x.group_number,"eligibility":x.eligibility,"verification_date":x.verification_date,"status":x.status,"notes":x.notes} for x in p.insurances],"tasks":[{"id":x.id,"title":x.title,"description":x.description,"due_date":x.due_date,"status":task_status(x)} for x in p.tasks],"followups":[{"id":x.id,"reason":x.reason,"followup_date":x.followup_date,"notes":x.notes,"status":followup_status(x)} for x in p.followups],"notes":[{"id":x.id,"author_role":x.author_role,"note_type":x.note_type,"content":x.content,"created_at":x.created_at,"updated_at":x.updated_at} for x in p.notes]}
