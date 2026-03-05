#!/usr/bin/env python3
"""
Personal AI Command Center - Database Initialization
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_db

def main():
    print("🚀 Initializing Personal AI Command Center Database...")
    print()
    
    init_db()
    
    print("✅ Database initialized successfully!")
    print()
    print("Tables created:")
    print("  - users")
    print("  - credentials")
    print("  - emails")
    print("  - social_posts")
    print("  - smart_home_devices")
    print("  - browser_tasks")
    print("  - hitl_requests")
    print("  - audit_logs")
    print()
    print("Database location: ./command_center.db")

if __name__ == "__main__":
    main()
