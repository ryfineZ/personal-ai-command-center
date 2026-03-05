"""
Personal AI Command Center - Browser Automation API
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import BrowserTask

router = APIRouter()


# Schemas
class TaskCreate(BaseModel):
    name: str
    task_type: str  # form_fill, price_monitor, scheduled_check, screenshot
    config: dict
    schedule: Optional[str] = None  # cron expression


class TaskResponse(BaseModel):
    id: int
    name: str
    task_type: str
    config: dict
    schedule: Optional[str]
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    status: str
    result: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class TaskExecute(BaseModel):
    params: Optional[dict] = None


# Endpoints
@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 50,
    task_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List browser automation tasks with filters"""
    query = db.query(BrowserTask)
    
    if task_type:
        query = query.filter(BrowserTask.task_type == task_type)
    
    if status:
        query = query.filter(BrowserTask.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new browser automation task"""
    db_task = BrowserTask(
        name=task.name,
        task_type=task.task_type,
        config=task.config,
        schedule=task.schedule,
        status="active" if task.schedule else "manual"
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get task details"""
    task = db.query(BrowserTask).filter(BrowserTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/execute")
async def execute_task(
    task_id: int,
    execute: TaskExecute,
    db: Session = Depends(get_db)
):
    """
    Execute a browser automation task
    
    Requires HITL approval if HITL_ENABLED for certain task types.
    """
    task = db.query(BrowserTask).filter(BrowserTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != "active" and task.status != "manual":
        raise HTTPException(status_code=400, detail=f"Task is {task.status}")
    
    # TODO: Implement actual browser automation with Playwright
    # TODO: Create HITL request if HITL_ENABLED
    
    # Update task execution
    task.last_run = datetime.utcnow()
    task.result = {
        "status": "success",
        "executed_at": datetime.utcnow().isoformat(),
        "params": execute.params
    }
    db.commit()
    
    return {
        "status": "executed",
        "task_id": task_id,
        "result": task.result
    }


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    """Update task configuration"""
    db_task = db.query(BrowserTask).filter(BrowserTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.name = task.name
    db_task.task_type = task.task_type
    db_task.config = task.config
    db_task.schedule = task.schedule
    db_task.status = "active" if task.schedule else "manual"
    db.commit()
    db.refresh(db_task)
    
    return db_task


@router.post("/{task_id}/pause")
async def pause_task(task_id: int, db: Session = Depends(get_db)):
    """Pause a scheduled task"""
    task = db.query(BrowserTask).filter(BrowserTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "paused"
    db.commit()
    
    return {"status": "paused", "task_id": task_id}


@router.post("/{task_id}/resume")
async def resume_task(task_id: int, db: Session = Depends(get_db)):
    """Resume a paused task"""
    task = db.query(BrowserTask).filter(BrowserTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != "paused":
        raise HTTPException(status_code=400, detail="Task is not paused")
    
    task.status = "active"
    db.commit()
    
    return {"status": "resumed", "task_id": task_id}


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    task = db.query(BrowserTask).filter(BrowserTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"status": "deleted", "task_id": task_id}


@router.get("/types/list")
async def list_task_types():
    """List supported browser task types"""
    return {
        "task_types": [
            {
                "name": "form_fill",
                "display_name": "Form Filling",
                "description": "Automatically fill web forms",
                "requires_hitl": True
            },
            {
                "name": "price_monitor",
                "display_name": "Price Monitoring",
                "description": "Monitor product prices and notify on changes",
                "requires_hitl": False
            },
            {
                "name": "scheduled_check",
                "display_name": "Scheduled Check",
                "description": "Periodically check websites for updates",
                "requires_hitl": False
            },
            {
                "name": "screenshot",
                "display_name": "Screenshot",
                "description": "Take screenshots of web pages",
                "requires_hitl": False
            },
            {
                "name": "data_extraction",
                "display_name": "Data Extraction",
                "description": "Extract data from web pages",
                "requires_hitl": False
            },
            {
                "name": "login",
                "display_name": "Login",
                "description": "Automatically login to websites",
                "requires_hitl": True
            }
        ]
    }


@router.post("/quick/form-fill")
async def quick_form_fill(
    url: str,
    fields: dict,
    submit: bool = False,
    db: Session = Depends(get_db)
):
    """
    Quick form filling without creating a task
    
    Requires HITL approval if HITL_ENABLED.
    """
    # TODO: Implement form filling with Playwright
    # TODO: Create HITL request if HITL_ENABLED
    
    return {
        "status": "pending_approval" if True else "executed",
        "url": url,
        "fields": fields,
        "submit": submit
    }


@router.post("/quick/screenshot")
async def quick_screenshot(
    url: str,
    full_page: bool = False,
    db: Session = Depends(get_db)
):
    """Take a screenshot of a web page"""
    # TODO: Implement screenshot with Playwright
    
    return {
        "status": "success",
        "url": url,
        "full_page": full_page,
        "screenshot_url": f"/screenshots/{datetime.utcnow().timestamp()}.png"
    }
