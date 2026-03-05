"""
Personal AI Command Center - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api import email, social, home, browser, hitl, audit, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    init_db()
    yield
    # Shutdown


app = FastAPI(
    title=settings.APP_NAME,
    description="A unified AI agent to control your entire digital life",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(email.router, prefix="/api/email", tags=["email"])
app.include_router(social.router, prefix="/api/social", tags=["social"])
app.include_router(home.router, prefix="/api/home", tags=["home"])
app.include_router(browser.router, prefix="/api/browser", tags=["browser"])
app.include_router(hitl.router, prefix="/api/hitl", tags=["hitl"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
