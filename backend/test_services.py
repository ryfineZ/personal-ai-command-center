#!/usr/bin/env python3
"""
Personal AI Command Center - Service Tester

Run this script to test all integrations.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_service import email_service
from app.services.social_service import social_service
from app.services.home_assistant_service import home_assistant_service
from app.services.ollama_service import ollama_service


async def test_email():
    """Test email service"""
    print("\n=== Testing Email Service ===")
    
    # Test connection
    print("Connecting to IMAP...")
    connected = await email_service.connect_imap()
    print(f"IMAP connected: {connected}")
    
    if connected:
        # List emails
        print("\nListing last 5 emails...")
        emails = await email_service.list_emails(limit=5)
        for email in emails:
            print(f"  - {email['subject'][:50]}... from {email['sender']}")
    
    await email_service.disconnect()
    return connected


async def test_social():
    """Test social media service"""
    print("\n=== Testing Social Media Service ===")
    
    # Test Twitter
    print("Connecting to Twitter...")
    twitter_connected = await social_service.twitter.connect()
    print(f"Twitter connected: {twitter_connected}")
    
    if twitter_connected:
        print("\nGetting tweets...")
        tweets = await social_service.twitter.get_tweets(limit=5)
        for tweet in tweets:
            print(f"  - @{tweet['author']}: {tweet['text'][:50]}...")
    
    return twitter_connected


async def test_home_assistant():
    """Test Home Assistant service"""
    print("\n=== Testing Home Assistant Service ===")
    
    print("Connecting to Home Assistant...")
    connected = await home_assistant_service.connect()
    print(f"Home Assistant connected: {connected}")
    
    if connected:
        print("\nGetting lights...")
        lights = await home_assistant_service.get_lights()
        for light in lights[:5]:
            entity_id = light.get("entity_id")
            state = light.get("state")
            print(f"  - {entity_id}: {state}")
    
    await home_assistant_service.close()
    return connected


async def test_ollama():
    """Test Ollama service"""
    print("\n=== Testing Ollama Service ===")
    
    print("Connecting to Ollama...")
    connected = await ollama_service.connect()
    print(f"Ollama connected: {connected}")
    
    if connected:
        print("\nListing models...")
        models = await ollama_service.list_models()
        for model in models:
            print(f"  - {model['name']}")
        
        print("\nGenerating text...")
        response = await ollama_service.generate("Hello, how are you?")
        print(f"Response: {response[:100]}...")
    
    return connected


async def main():
    print("====================================")
    print("Personal AI Command Center")
    print("Service Integration Tester")
    print("====================================")
    
    results = {}
    
    # Test Email
    try:
        results["email"] = await test_email()
    except Exception as e:
        print(f"Email test failed: {e}")
        results["email"] = False
    
    # Test Social Media
    try:
        results["social"] = await test_social()
    except Exception as e:
        print(f"Social media test failed: {e}")
        results["social"] = False
    
    # Test Home Assistant
    try:
        results["home_assistant"] = await test_home_assistant()
    except Exception as e:
        print(f"Home Assistant test failed: {e}")
        results["home_assistant"] = False
    
    # Test Ollama
    try:
        results["ollama"] = await test_ollama()
    except Exception as e:
        print(f"Ollama test failed: {e}")
        results["ollama"] = False
    
    # Summary
    print("\n====================================")
    print("Test Results Summary")
    print("====================================")
    for service, connected in results.items():
        status = "✅ Connected" if connected else "❌ Failed"
        print(f"{service}: {status}")
    
    print("\nTo configure services, update .env file with:")
    print("  - IMAP_SERVER, SMTP_SERVER, EMAIL_ADDRESS, EMAIL_PASSWORD")
    print("  - TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET")
    print("  - HOME_ASSISTANT_URL, HOME_ASSISTANT_TOKEN")
    print("  - OLLAMA_BASE_URL, DEFAULT_MODEL")


if __name__ == "__main__":
    asyncio.run(main())
