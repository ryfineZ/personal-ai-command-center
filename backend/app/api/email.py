"""
Personal AI Command Center - Email API
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.models.models import Email

router = APIRouter()


# Schemas
class EmailCreate(BaseModel):
    message_id: str
    sender: EmailStr
    recipient: EmailStr
    subject: str
    body: str


class EmailResponse(BaseModel):
    id: int
    message_id: str
    sender: str
    recipient: str
    subject: str
    body: str
    category: Optional[str]
    processed: bool
    processed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class EmailReply(BaseModel):
    to: EmailStr
    subject: str
    body: str
    in_reply_to: Optional[str] = None


class EmailCategory(BaseModel):
    category: str  # important, notification, promotion, social, spam


# Endpoints
@router.post("/", response_model=EmailResponse)
async def create_email(email: EmailCreate, db: Session = Depends(get_db)):
    """Create a new email record"""
    # Check if message_id already exists
    existing = db.query(Email).filter(Email.message_id == email.message_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email with this message_id already exists")
    
    db_email = Email(
        message_id=email.message_id,
        sender=email.sender,
        recipient=email.recipient,
        subject=email.subject,
        body=email.body,
        processed=False
    )
    
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    
    return db_email


@router.get("/", response_model=List[EmailResponse])
async def list_emails(
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None,
    processed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List emails with optional filters"""
    query = db.query(Email)
    
    if category:
        query = query.filter(Email.category == category)
    
    if processed is not None:
        query = query.filter(Email.processed == processed)
    
    return query.order_by(Email.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(email_id: int, db: Session = Depends(get_db)):
    """Get email details"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.post("/{email_id}/categorize")
async def categorize_email(
    email_id: int,
    category: EmailCategory,
    db: Session = Depends(get_db)
):
    """Categorize an email"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    email.category = category.category
    db.commit()
    
    return {"status": "categorized", "email_id": email_id, "category": category.category}


@router.post("/{email_id}/process")
async def process_email(email_id: int, db: Session = Depends(get_db)):
    """Mark email as processed"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    email.processed = True
    email.processed_at = datetime.utcnow()
    db.commit()
    
    return {"status": "processed", "email_id": email_id}


@router.post("/reply")
async def send_reply(reply: EmailReply, db: Session = Depends(get_db)):
    """
    Send email reply (requires HITL approval if enabled)
    
    This endpoint creates a HITL request for approval before sending.
    """
    from app.core.config import settings
    from app.models.models import HITLRequest
    from datetime import datetime, timedelta
    
    if settings.HITL_ENABLED:
        # Create HITL request for approval
        hitl_request = HITLRequest(
            request_type="email_send",
            description=f"Send email to {reply.to}: {reply.subject}",
            data={
                "to": reply.to,
                "subject": reply.subject,
                "body": reply.body,
                "in_reply_to": reply.in_reply_to
            },
            status="pending",
            expires_at=datetime.utcnow() + timedelta(seconds=settings.HITL_TIMEOUT)
        )
        db.add(hitl_request)
        db.commit()
        
        return {
            "status": "pending_approval",
            "message": "Email reply queued for approval",
            "hitl_request_id": hitl_request.id,
            "to": reply.to,
            "subject": reply.subject
        }
    else:
        # Send directly if HITL is disabled
        from app.services.email_service import email_service
        result = await email_service.send_email(reply.to, reply.subject, reply.body)
        return {
            "status": "sent",
            "message": "Email sent directly (HITL disabled)",
            "to": reply.to,
            "subject": reply.subject,
            "result": result
        }


@router.get("/unread/count")
async def get_unread_count(db: Session = Depends(get_db)):
    """Get count of unread/unprocessed emails"""
    count = db.query(Email).filter(Email.processed == False).count()
    return {"unread_count": count}


@router.post("/sync")
async def sync_emails(db: Session = Depends(get_db)):
    """
    Sync emails from IMAP server
    
    This endpoint triggers email synchronization from configured IMAP server.
    """
    from app.services.email_service import email_service
    from app.models.models import AuditLog
    
    try:
        # Sync emails from IMAP
        result = await email_service.sync_emails(db)
        
        # Log the sync
        audit_log = AuditLog(
            user_id=1,  # TODO: Get from auth
            action="email_sync",
            resource="email",
            resource_id=0,
            details={"emails_synced": result.get("count", 0)}
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "status": "sync_completed",
            "emails_synced": result.get("count", 0),
            "message": "Email synchronization completed"
        }
    except Exception as e:
        return {
            "status": "sync_failed",
            "error": str(e),
            "message": "Email synchronization failed"
        }


@router.delete("/{email_id}")
async def delete_email(email_id: int, db: Session = Depends(get_db)):
    """Delete email"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    db.delete(email)
    db.commit()
    
    return {"status": "deleted", "email_id": email_id}
