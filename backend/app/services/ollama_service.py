"""
Personal AI Command Center - Ollama Local LLM Integration Service
"""
import ollama
from typing import List, Optional, Dict
import asyncio
from datetime import datetime

from app.core.config import settings


class OllamaService:
    """Ollama local LLM integration"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.DEFAULT_MODEL
        self.client = None
    
    async def connect(self) -> bool:
        """Connect to Ollama"""
        try:
            # Test connection by listing models
            models = ollama.list()
            return True
        except Exception as e:
            print(f"Ollama connection error: {e}")
            print(f"Make sure Ollama is running at {self.base_url}")
            return False
    
    async def list_models(self) -> List[Dict]:
        """List available models"""
        try:
            response = ollama.list()
            models = []
            for model in response.get("models", []):
                models.append({
                    "name": model.get("model"),
                    "size": model.get("size"),
                    "modified_at": model.get("modified_at"),
                    "digest": model.get("digest")
                })
            return models
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    async def chat(
        self,
        messages: List[Dict],
        model: Optional[str] = None,
        stream: bool = False
    ) -> Optional[str]:
        """Chat with the model"""
        try:
            model = model or self.default_model
            
            if stream:
                response = ""
                for chunk in ollama.chat(
                    model=model,
                    messages=messages,
                    stream=True
                ):
                    response += chunk.get("message", {}).get("content", "")
                return response
            else:
                response = ollama.chat(
                    model=model,
                    messages=messages
                )
                return response.get("message", {}).get("content", "")
                
        except Exception as e:
            print(f"Error in chat: {e}")
            return None
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        stream: bool = False
    ) -> Optional[str]:
        """Generate text from a prompt"""
        try:
            model = model or self.default_model
            
            options = {}
            if system:
                options["system"] = system
            
            if stream:
                response = ""
                for chunk in ollama.generate(
                    model=model,
                    prompt=prompt,
                    stream=True,
                    options=options
                ):
                    response += chunk.get("response", "")
                return response
            else:
                response = ollama.generate(
                    model=model,
                    prompt=prompt,
                    options=options
                )
                return response.get("response", "")
                
        except Exception as e:
            print(f"Error in generate: {e}")
            return None
    
    async def embeddings(
        self,
        text: str,
        model: Optional[str] = None
    ) -> Optional[List[float]]:
        """Generate embeddings for text"""
        try:
            model = model or self.default_model
            response = ollama.embeddings(
                model=model,
                prompt=text
            )
            return response.get("embedding", [])
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return None
    
    async def pull_model(self, model: str) -> bool:
        """Pull/download a model"""
        try:
            response = ollama.pull(model)
            return True
        except Exception as e:
            print(f"Error pulling model {model}: {e}")
            return False
    
    async def classify_email(self, email: Dict) -> str:
        """Classify an email into categories"""
        prompt = f"""Classify the following email into one of these categories:
- important
- notification
- promotion
- social
- spam

Email from: {email.get('sender', '')}
Subject: {email.get('subject', '')}
Body: {email.get('body', '')[:200]}

Reply with only the category name."""

        response = await self.generate(prompt)
        
        if response:
            category = response.strip().lower()
            valid_categories = ["important", "notification", "promotion", "social", "spam"]
            if category in valid_categories:
                return category
        
        return "notification"
    
    async def generate_email_reply(
        self,
        email: Dict,
        tone: str = "professional"
    ) -> str:
        """Generate a reply to an email"""
        prompt = f"""Generate a brief, {tone} reply to the following email:

From: {email.get('sender', '')}
Subject: {email.get('subject', '')}
Body: {email.get('body', '')[:500]}

Reply:"""

        response = await self.generate(prompt)
        return response or "Thank you for your email. I will get back to you soon."
    
    async def summarize_text(self, text: str, max_length: int = 100) -> str:
        """Summarize text"""
        prompt = f"""Summarize the following text in {max_length} words or less:

{text}

Summary:"""

        response = await self.generate(prompt)
        return response or text[:max_length]
    
    async def extract_action_items(self, text: str) -> List[str]:
        """Extract action items from text"""
        prompt = f"""Extract action items from the following text. Return each item on a new line:

{text}

Action items:"""

        response = await self.generate(prompt)
        
        if response:
            items = response.strip().split("\n")
            return [item.strip("- ") for item in items if item.strip()]
        
        return []
    
    async def sentiment_analysis(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        prompt = f"""Analyze the sentiment of the following text. Return only one word: positive, negative, or neutral.

{text}

Sentiment:"""

        response = await self.generate(prompt)
        sentiment = response.strip().lower() if response else "neutral"
        
        return {
            "sentiment": sentiment if sentiment in ["positive", "negative", "neutral"] else "neutral",
            "confidence": 0.8  # Placeholder
        }
    
    async def smart_home_command(self, command: str, context: Optional[Dict] = None) -> Dict:
        """Parse a natural language smart home command"""
        context_str = ""
        if context:
            context_str = f"\n\nAvailable devices: {context.get('devices', [])}"
        
        prompt = f"""Parse the following smart home command into a structured format:

Command: {command}
{context_str}

Return JSON with:
- action: turn_on, turn_off, toggle, set_value
- device_type: light, switch, climate, etc.
- device_name: name or id of the device
- value: optional value (for brightness, temperature, etc.)

JSON:"""

        response = await self.generate(prompt)
        
        if response:
            try:
                import json
                return json.loads(response)
            except:
                pass
        
        return {
            "action": "unknown",
            "device_type": "unknown",
            "device_name": "",
            "value": None
        }
    
    async def generate_social_post(
        self,
        topic: str,
        platform: str = "twitter",
        tone: str = "professional"
    ) -> str:
        """Generate a social media post"""
        length_limit = {
            "twitter": 280,
            "linkedin": 3000,
            "bluesky": 300,
            "farcaster": 320
        }.get(platform, 280)
        
        prompt = f"""Generate a {tone} social media post about: {topic}

Platform: {platform}
Max length: {length_limit} characters

Post:"""

        response = await self.generate(prompt)
        return response or topic


# Create instance
ollama_service = OllamaService()
