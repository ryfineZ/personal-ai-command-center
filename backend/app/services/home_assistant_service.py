"""
Personal AI Command Center - Home Assistant Integration Service
"""
import httpx
from typing import List, Optional, Dict
from datetime import datetime
import asyncio

from app.core.config import settings


class HomeAssistantService:
    """Home Assistant integration service"""
    
    def __init__(self):
        self.base_url = settings.HOME_ASSISTANT_URL
        self.token = settings.HOME_ASSISTANT_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.client = None
    
    async def connect(self) -> bool:
        """Connect to Home Assistant"""
        if not self.base_url or not self.token:
            print("Home Assistant credentials not configured")
            return False
        
        try:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=30.0
            )
            
            # Test connection
            response = await self.client.get("/api/")
            if response.status_code == 200:
                return True
            else:
                print(f"Home Assistant connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Home Assistant connection error: {e}")
            return False
    
    async def get_states(self) -> List[Dict]:
        """Get all entity states"""
        if not self.client:
            if not await self.connect():
                return []
        
        try:
            response = await self.client.get("/api/states")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting states: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error getting states: {e}")
            return []
    
    async def get_entity(self, entity_id: str) -> Optional[Dict]:
        """Get state of a specific entity"""
        if not self.client:
            if not await self.connect():
                return None
        
        try:
            response = await self.client.get(f"/api/states/{entity_id}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting entity {entity_id}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error getting entity {entity_id}: {e}")
            return None
    
    async def call_service(
        self,
        domain: str,
        service: str,
        entity_id: str,
        data: Optional[Dict] = None
    ) -> bool:
        """Call a Home Assistant service"""
        if not self.client:
            if not await self.connect():
                return False
        
        try:
            payload = {
                "entity_id": entity_id
            }
            if data:
                payload.update(data)
            
            response = await self.client.post(
                f"/api/services/{domain}/{service}",
                json=payload
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"Error calling service: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error calling service: {e}")
            return False
    
    async def turn_on(self, entity_id: str) -> bool:
        """Turn on an entity"""
        domain = entity_id.split(".")[0]
        return await self.call_service(domain, "turn_on", entity_id)
    
    async def turn_off(self, entity_id: str) -> bool:
        """Turn off an entity"""
        domain = entity_id.split(".")[0]
        return await self.call_service(domain, "turn_off", entity_id)
    
    async def toggle(self, entity_id: str) -> bool:
        """Toggle an entity"""
        domain = entity_id.split(".")[0]
        return await self.call_service(domain, "toggle", entity_id)
    
    async def set_value(
        self,
        entity_id: str,
        value: float,
        attribute: str = "brightness"
    ) -> bool:
        """Set a value for an entity (e.g., brightness, temperature)"""
        domain = entity_id.split(".")[0]
        
        if domain == "light":
            return await self.call_service(
                domain,
                "turn_on",
                entity_id,
                {attribute: value}
            )
        elif domain == "climate":
            return await self.call_service(
                domain,
                "set_temperature",
                entity_id,
                {"temperature": value}
            )
        else:
            print(f"Cannot set value for domain: {domain}")
            return False
    
    async def get_entities_by_domain(self, domain: str) -> List[Dict]:
        """Get all entities of a specific domain"""
        states = await self.get_states()
        return [s for s in states if s["entity_id"].startswith(f"{domain}.")]
    
    async def get_lights(self) -> List[Dict]:
        """Get all lights"""
        return await self.get_entities_by_domain("light")
    
    async def get_switches(self) -> List[Dict]:
        """Get all switches"""
        return await self.get_entities_by_domain("switch")
    
    async def get_sensors(self) -> List[Dict]:
        """Get all sensors"""
        return await self.get_entities_by_domain("sensor")
    
    async def get_climate(self) -> List[Dict]:
        """Get all climate entities"""
        return await self.get_entities_by_domain("climate")
    
    async def execute_scene(self, scene_id: str) -> bool:
        """Execute a scene"""
        return await self.call_service("scene", "turn_on", scene_id)
    
    async def get_automations(self) -> List[Dict]:
        """Get all automations"""
        return await self.get_entities_by_domain("automation")
    
    async def trigger_automation(self, automation_id: str) -> bool:
        """Trigger an automation"""
        return await self.call_service(
            "automation",
            "trigger",
            automation_id
        )
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()


# Create instance
home_assistant_service = HomeAssistantService()
