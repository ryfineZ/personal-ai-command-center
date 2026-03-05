"""
Personal AI Command Center - Data Models
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100))
    hashed_password = Column(String(255))  # Added for authentication
    preferences = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    credentials = relationship("Credential", back_populates="user")
    emails = relationship("Email", back_populates="user")
    posts = relationship("SocialPost", back_populates="user")
    devices = relationship("SmartHomeDevice", back_populates="user")
    tasks = relationship("BrowserTask", back_populates="user")
    hitl_requests = relationship("HITLRequest", back_populates="user")


class Credential(Base):
    """Encrypted credential storage"""
    __tablename__ = "credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service = Column(String(50), nullable=False)  # email, twitter, linkedin, home_assistant
    encrypted_data = Column(Text, nullable=False)  # AES-256 encrypted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="credentials")


class Email(Base):
    """Email message storage"""
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message_id = Column(String(255), unique=True)
    sender = Column(String(255))
    recipient = Column(String(255))
    subject = Column(String(500))
    body = Column(Text)
    category = Column(String(50))  # important, notification, promotion, etc.
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="emails")


class SocialPost(Base):
    """Social media post"""
    __tablename__ = "social_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    platform = Column(String(50), nullable=False)  # twitter, linkedin, bluesky
    content = Column(Text, nullable=False)
    scheduled_at = Column(DateTime)
    posted_at = Column(DateTime)
    status = Column(String(20), default="draft")  # draft, scheduled, posted, failed
    post_id = Column(String(255))  # Platform-specific post ID
    metrics = Column(JSON)  # likes, shares, comments
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="posts")


class SmartHomeDevice(Base):
    """Smart home device"""
    __tablename__ = "smart_home_devices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    device_type = Column(String(50))  # light, thermostat, camera, etc.
    room = Column(String(50))
    state = Column(JSON)  # Current device state
    last_updated = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="devices")


class BrowserTask(Base):
    """Browser automation task"""
    __tablename__ = "browser_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100), nullable=False)
    task_type = Column(String(50))  # form_fill, price_monitor, scheduled_check
    config = Column(JSON)  # Task configuration
    schedule = Column(String(50))  # cron expression
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    status = Column(String(20), default="active")  # active, paused, completed
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="tasks")


class HITLRequest(Base):
    """Human-in-the-Loop approval request"""
    __tablename__ = "hitl_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    request_type = Column(String(50), nullable=False)  # email_send, post_publish, device_control
    description = Column(Text)
    data = Column(JSON)  # Request data
    status = Column(String(20), default="pending")  # pending, approved, rejected, expired
    approved_at = Column(DateTime)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="hitl_requests")


class AuditLog(Base):
    """Audit log for all actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource = Column(String(50))  # email, social, device, browser
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
