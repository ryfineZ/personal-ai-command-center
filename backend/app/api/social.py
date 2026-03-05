"""
Personal AI Command Center - Social Media API
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import SocialPost

router = APIRouter()


# Schemas
class PostCreate(BaseModel):
    platform: str  # twitter, linkedin, bluesky, farcaster
    content: str
    scheduled_at: Optional[datetime] = None


class PostResponse(BaseModel):
    id: int
    platform: str
    content: str
    scheduled_at: Optional[datetime]
    posted_at: Optional[datetime]
    status: str
    post_id: Optional[str]
    metrics: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class PostMetrics(BaseModel):
    likes: int = 0
    shares: int = 0
    comments: int = 0
    views: int = 0


# Endpoints
@router.get("/", response_model=List[PostResponse])
async def list_posts(
    skip: int = 0,
    limit: int = 50,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List social media posts with filters"""
    query = db.query(SocialPost)
    
    if platform:
        query = query.filter(SocialPost.platform == platform)
    
    if status:
        query = query.filter(SocialPost.status == status)
    
    return query.order_by(SocialPost.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=PostResponse)
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """Create a new social media post"""
    db_post = SocialPost(
        platform=post.platform,
        content=post.content,
        scheduled_at=post.scheduled_at,
        status="scheduled" if post.scheduled_at else "draft"
    )
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    return db_post


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get post details"""
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/{post_id}/publish")
async def publish_post(post_id: int, db: Session = Depends(get_db)):
    """
    Publish post to social media platform
    
    Requires HITL approval if HITL_ENABLED.
    """
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.status not in ["draft", "scheduled"]:
        raise HTTPException(status_code=400, detail="Post cannot be published")
    
    # TODO: Implement actual posting to platform
    # TODO: Create HITL request if HITL_ENABLED
    
    post.status = "posted"
    post.posted_at = datetime.utcnow()
    post.post_id = f"{post.platform}_{post.id}_{datetime.utcnow().timestamp()}"
    db.commit()
    
    return {
        "status": "published",
        "post_id": post_id,
        "platform": post.platform,
        "posted_at": post.posted_at
    }


@router.delete("/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    """Delete post"""
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.status == "posted":
        raise HTTPException(status_code=400, detail="Cannot delete posted content")
    
    db.delete(post)
    db.commit()
    
    return {"status": "deleted", "post_id": post_id}


@router.get("/scheduled")
async def get_scheduled_posts(db: Session = Depends(get_db)):
    """Get all scheduled posts"""
    now = datetime.utcnow()
    posts = db.query(SocialPost).filter(
        SocialPost.status == "scheduled",
        SocialPost.scheduled_at > now
    ).order_by(SocialPost.scheduled_at).all()
    
    return posts


@router.post("/{post_id}/metrics")
async def update_metrics(
    post_id: int,
    metrics: PostMetrics,
    db: Session = Depends(get_db)
):
    """Update post metrics (likes, shares, etc.)"""
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post.metrics = metrics.dict()
    db.commit()
    
    return {"status": "updated", "post_id": post_id, "metrics": metrics.dict()}


@router.get("/platforms")
async def list_platforms():
    """List supported social media platforms"""
    return {
        "platforms": [
            {
                "name": "twitter",
                "display_name": "Twitter/X",
                "features": ["post", "reply", "retweet", "like"]
            },
            {
                "name": "linkedin",
                "display_name": "LinkedIn",
                "features": ["post", "article", "comment"]
            },
            {
                "name": "bluesky",
                "display_name": "Bluesky",
                "features": ["post", "reply", "repost", "like"]
            },
            {
                "name": "farcaster",
                "display_name": "Farcaster",
                "features": ["cast", "reply", "recast", "like"]
            }
        ]
    }
