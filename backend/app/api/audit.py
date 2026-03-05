"""
Personal AI Command Center - Audit Log API
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import AuditLog

router = APIRouter()


# Schemas
class AuditLogCreate(BaseModel):
    action: str
    resource: str
    resource_id: Optional[int] = None
    details: dict = {}
    ip_address: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    resource: str
    resource_id: Optional[int]
    details: dict
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Endpoints
@router.get("/", response_model=List[AuditLogResponse])
async def list_logs(
    skip: int = 0,
    limit: int = 100,
    resource: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """List audit logs with filters"""
    query = db.query(AuditLog)
    
    if resource:
        query = query.filter(AuditLog.resource == resource)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=AuditLogResponse)
async def create_log(log: AuditLogCreate, db: Session = Depends(get_db)):
    """Create an audit log entry"""
    db_log = AuditLog(
        user_id=1,  # TODO: Get from auth
        action=log.action,
        resource=log.resource,
        resource_id=log.resource_id,
        details=log.details,
        ip_address=log.ip_address
    )
    
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    return db_log


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_log(log_id: int, db: Session = Depends(get_db)):
    """Get audit log details"""
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log


@router.get("/resources/list")
async def list_resources(db: Session = Depends(get_db)):
    """List all audited resources"""
    resources = db.query(AuditLog.resource).distinct().all()
    return {"resources": [r[0] for r in resources]}


@router.get("/actions/list")
async def list_actions(db: Session = Depends(get_db)):
    """List all audited actions"""
    actions = db.query(AuditLog.action).distinct().all()
    return {"actions": [a[0] for a in actions]}


@router.get("/stats")
async def get_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get audit statistics"""
    query = db.query(AuditLog)
    
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    total = query.count()
    
    # Group by resource
    from sqlalchemy import func
    by_resource = db.query(
        AuditLog.resource,
        func.count(AuditLog.id).label('count')
    ).group_by(AuditLog.resource).all()
    
    # Group by action
    by_action = db.query(
        AuditLog.action,
        func.count(AuditLog.id).label('count')
    ).group_by(AuditLog.action).all()
    
    return {
        "total": total,
        "by_resource": {r: c for r, c in by_resource},
        "by_action": {a: c for a, c in by_action}
    }


@router.get("/export")
async def export_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Export audit logs as JSON"""
    query = db.query(AuditLog)
    
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    logs = query.order_by(AuditLog.created_at).all()
    
    return {
        "exported_at": datetime.utcnow(),
        "count": len(logs),
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource": log.resource,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ]
    }


@router.delete("/cleanup")
async def cleanup_old_logs(
    days: int = 90,
    db: Session = Depends(get_db)
):
    """Delete logs older than specified days"""
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    deleted = db.query(AuditLog).filter(
        AuditLog.created_at < cutoff
    ).delete()
    
    db.commit()
    
    return {
        "status": "cleaned",
        "deleted_count": deleted,
        "cutoff_date": cutoff
    }


from datetime import timedelta
