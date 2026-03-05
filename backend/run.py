#!/usr/bin/env python3
"""
Personal AI Command Center - Run Server
"""
import sys
import os
import uvicorn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("🚀 Starting Personal AI Command Center...")
    print()
    print("📍 API: http://localhost:8001")
    print("📖 Docs: http://localhost:8001/docs")
    print("❤️  Health: http://localhost:8001/health")
    print()
    print("Press Ctrl+C to stop")
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
