"""
Personal AI Command Center - Smart Home API
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import SmartHomeDevice

router = APIRouter()


# Schemas
class DeviceCreate(BaseModel):
    device_id: str
    name: str
    device_type: str  # light, thermostat, camera, sensor, switch, etc.
    room: Optional[str] = None
    state: dict = {}


class DeviceResponse(BaseModel):
    id: int
    device_id: str
    name: str
    device_type: str
    room: Optional[str]
    state: dict
    last_updated: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class DeviceState(BaseModel):
    state: dict


class DeviceControl(BaseModel):
    action: str  # on, off, toggle, set
    value: Optional[dict] = None


class SceneCreate(BaseModel):
    name: str
    actions: List[dict]  # List of device actions


# Endpoints
@router.get("/", response_model=List[DeviceResponse])
async def list_devices(
    skip: int = 0,
    limit: int = 50,
    room: Optional[str] = None,
    device_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List smart home devices with filters"""
    query = db.query(SmartHomeDevice)
    
    if room:
        query = query.filter(SmartHomeDevice.room == room)
    
    if device_type:
        query = query.filter(SmartHomeDevice.device_type == device_type)
    
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=DeviceResponse)
async def register_device(device: DeviceCreate, db: Session = Depends(get_db)):
    """Register a new smart home device"""
    # Check if device already exists
    existing = db.query(SmartHomeDevice).filter(
        SmartHomeDevice.device_id == device.device_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Device already registered")
    
    db_device = SmartHomeDevice(
        device_id=device.device_id,
        name=device.name,
        device_type=device.device_type,
        room=device.room,
        state=device.state
    )
    
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    return db_device


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: int, db: Session = Depends(get_db)):
    """Get device details"""
    device = db.query(SmartHomeDevice).filter(SmartHomeDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.post("/{device_id}/control")
async def control_device(
    device_id: int,
    control: DeviceControl,
    db: Session = Depends(get_db)
):
    """
    Control a smart home device
    
    Requires HITL approval if HITL_ENABLED for certain actions.
    """
    device = db.query(SmartHomeDevice).filter(SmartHomeDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # TODO: Implement actual Home Assistant control
    # TODO: Create HITL request if HITL_ENABLED
    
    # Update device state based on action
    new_state = device.state.copy() if device.state else {}
    
    if control.action == "on":
        new_state["power"] = True
    elif control.action == "off":
        new_state["power"] = False
    elif control.action == "toggle":
        new_state["power"] = not new_state.get("power", False)
    elif control.action == "set" and control.value:
        new_state.update(control.value)
    
    device.state = new_state
    device.last_updated = datetime.utcnow()
    db.commit()
    
    return {
        "status": "controlled",
        "device_id": device_id,
        "action": control.action,
        "new_state": new_state
    }


@router.put("/{device_id}/state", response_model=DeviceResponse)
async def update_device_state(
    device_id: int,
    state: DeviceState,
    db: Session = Depends(get_db)
):
    """Update device state manually"""
    device = db.query(SmartHomeDevice).filter(SmartHomeDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device.state = state.state
    device.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(device)
    
    return device


@router.delete("/{device_id}")
async def unregister_device(device_id: int, db: Session = Depends(get_db)):
    """Unregister a device"""
    device = db.query(SmartHomeDevice).filter(SmartHomeDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db.delete(device)
    db.commit()
    
    return {"status": "unregistered", "device_id": device_id}


@router.get("/rooms/list")
async def list_rooms(db: Session = Depends(get_db)):
    """List all rooms with devices"""
    rooms = db.query(SmartHomeDevice.room).distinct().all()
    return {"rooms": [room[0] for room in rooms if room[0]]}


@router.get("/types/list")
async def list_device_types():
    """List supported device types"""
    return {
        "device_types": [
            {
                "name": "light",
                "display_name": "Light",
                "actions": ["on", "off", "toggle", "set_brightness", "set_color"]
            },
            {
                "name": "thermostat",
                "display_name": "Thermostat",
                "actions": ["set_temperature", "set_mode", "set_fan"]
            },
            {
                "name": "camera",
                "display_name": "Camera",
                "actions": ["on", "off", "record", "snapshot"]
            },
            {
                "name": "sensor",
                "display_name": "Sensor",
                "actions": ["read"]
            },
            {
                "name": "switch",
                "display_name": "Switch",
                "actions": ["on", "off", "toggle"]
            },
            {
                "name": "lock",
                "display_name": "Lock",
                "actions": ["lock", "unlock"]
            }
        ]
    }


@router.post("/scenes/execute")
async def execute_scene(
    scene: SceneCreate,
    db: Session = Depends(get_db)
):
    """
    Execute a scene (group of device actions)
    
    Requires HITL approval if HITL_ENABLED.
    """
    # TODO: Implement scene execution
    # TODO: Create HITL request if HITL_ENABLED
    
    results = []
    for action in scene.actions:
        device_id = action.get("device_id")
        control = action.get("control")
        
        device = db.query(SmartHomeDevice).filter(
            SmartHomeDevice.id == device_id
        ).first()
        
        if device:
            results.append({
                "device_id": device_id,
                "device_name": device.name,
                "action": control,
                "status": "executed"
            })
    
    return {
        "scene_name": scene.name,
        "executed_at": datetime.utcnow(),
        "results": results
    }


@router.post("/sync")
async def sync_devices(db: Session = Depends(get_db)):
    """
    Sync devices from Home Assistant
    
    This endpoint triggers device synchronization from configured Home Assistant instance.
    """
    # TODO: Implement Home Assistant sync
    # TODO: Use background task for sync
    
    return {
        "status": "sync_started",
        "message": "Device synchronization started"
    }
