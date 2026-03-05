"""
Personal AI Command Center - Human-in-the-Loop (HITL) API
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.models.models import HITLRequest

router = APIRouter()


# Schemas
class HITLRequestCreate(BaseModel):
    request_type: str  # email_send, post_publish, device_control, browser_action
    description: str
    data: dict


class HITLRequestResponse(BaseModel):
    id: int
    request_type: str
    description: str
    data: dict
    status: str
    approved_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class HITLApproval(BaseModel):
    approved: bool
    notes: Optional[str] = None


# Endpoints
@router.get("/", response_model=List[HITLRequestResponse])
async def list_requests(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    request_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List HITL requests with filters"""
    query = db.query(HITLRequest)
    
    if status:
        query = query.filter(HITLRequest.status == status)
    
    if request_type:
        query = query.filter(HITLRequest.request_type == request_type)
    
    return query.order_by(HITLRequest.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=HITLRequestResponse)
async def create_request(request: HITLRequestCreate, db: Session = Depends(get_db)):
    """
    Create a new HITL request
    
    This endpoint is called by other modules when they need human approval.
    """
    # Check if HITL is enabled
    if not settings.HITL_ENABLED:
        # Auto-approve if HITL is disabled
        return HITLRequestResponse(
            id=0,
            request_type=request.request_type,
            description=request.description,
            data=request.data,
            status="approved",
            approved_at=datetime.utcnow(),
            expires_at=None,
            created_at=datetime.utcnow()
        )
    
    db_request = HITLRequest(
        request_type=request.request_type,
        description=request.description,
        data=request.data,
        status="pending",
        expires_at=datetime.utcnow() + timedelta(seconds=settings.HITL_TIMEOUT)
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    return db_request


@router.get("/pending", response_model=List[HITLRequestResponse])
async def get_pending_requests(db: Session = Depends(get_db)):
    """Get all pending HITL requests"""
    requests = db.query(HITLRequest).filter(
        HITLRequest.status == "pending",
        HITLRequest.expires_at > datetime.utcnow()
    ).order_by(HITLRequest.created_at).all()
    
    return requests


@router.get("/{request_id}", response_model=HITLRequestResponse)
async def get_request(request_id: int, db: Session = Depends(get_db)):
    """Get HITL request details"""
    request = db.query(HITLRequest).filter(HITLRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@router.post("/{request_id}/approve")
async def approve_request(
    request_id: int,
    approval: HITLApproval,
    db: Session = Depends(get_db)
):
    """
    Approve or reject a HITL request
    
    This is the endpoint that users call to approve/reject requests.
    """
    request = db.query(HITLRequest).filter(HITLRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if request.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request already {request.status}")
    
    if request.expires_at and request.expires_at < datetime.utcnow():
        request.status = "expired"
        db.commit()
        raise HTTPException(status_code=400, detail="Request has expired")
    
    # Update request status
    request.status = "approved" if approval.approved else "rejected"
    request.approved_at = datetime.utcnow()
    db.commit()
    
    # TODO: Trigger the action if approved
    # TODO: Notify the requesting service
    
    return {
        "status": request.status,
        "request_id": request_id,
        "approved_at": request.approved_at,
        "notes": approval.notes
    }


@router.post("/{request_id}/expire")
async def expire_request(request_id: int, db: Session = Depends(get_db)):
    """Manually expire a request"""
    request = db.query(HITLRequest).filter(HITLRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    request.status = "expired"
    db.commit()
    
    return {"status": "expired", "request_id": request_id}


@router.post("/cleanup")
async def cleanup_expired(db: Session = Depends(get_db)):
    """Clean up expired requests"""
    expired = db.query(HITLRequest).filter(
        HITLRequest.status == "pending",
        HITLRequest.expires_at < datetime.utcnow()
    ).all()
    
    for request in expired:
        request.status = "expired"
    
    db.commit()
    
    return {
        "status": "cleaned",
        "expired_count": len(expired)
    }


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get HITL statistics"""
    total = db.query(HITLRequest).count()
    pending = db.query(HITLRequest).filter(HITLRequest.status == "pending").count()
    approved = db.query(HITLRequest).filter(HITLRequest.status == "approved").count()
    rejected = db.query(HITLRequest).filter(HITLRequest.status == "rejected").count()
    expired = db.query(HITLRequest).filter(HITLRequest.status == "expired").count()
    
    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "expired": expired
    }


@router.get("/types/list")
async def list_request_types():
    """List HITL request types"""
    return {
        "request_types": [
            {
                "name": "email_send",
                "display_name": "Send Email",
                "description": "Approval required before sending emails",
                "auto_expire": True
            },
            {
                "name": "post_publish",
                "display_name": "Publish Post",
                "description": "Approval required before publishing to social media",
                "auto_expire": True
            },
            {
                "name": "device_control",
                "display_name": "Control Device",
                "description": "Approval required for certain device actions",
                "auto_expire": True
            },
            {
                "name": "browser_action",
                "display_name": "Browser Action",
                "description": "Approval required for sensitive browser actions",
                "auto_expire": True
            },
            {
                "name": "payment",
                "display_name": "Payment",
                "description": "Approval required for payments",
                "auto_expire": False
            },
            {
                "name": "delete_data",
                "display_name": "Delete Data",
                "description": "Approval required for data deletion",
                "auto_expire": False
            }
        ]
    }
