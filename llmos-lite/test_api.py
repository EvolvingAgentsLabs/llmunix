#!/usr/bin/env python3
"""
Quick test script for LLMos-Lite API

Run this after starting the API server to test basic functionality.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    print()

def test_list_skills():
    """Test listing skills"""
    print("Testing skills list...")
    response = requests.get(
        f"{BASE_URL}/skills",
        params={"user_id": "alice", "team_id": "engineering"}
    )
    print(f"  Status: {response.status_code}")
    data = response.json()
    print(f"  Total skills: {data['total']}")
    for skill in data['skills']:
        print(f"    - {skill['name']} ({skill['volume']})")
    print()

def test_create_skill():
    """Test creating a skill"""
    print("Testing skill creation...")
    skill_data = {
        "user_id": "alice",
        "skill_id": "test-skill",
        "name": "Test Skill",
        "category": "testing",
        "description": "A test skill",
        "content": "## Approach\n1. Do something\n2. Do another thing",
        "keywords": ["test", "example"]
    }
    response = requests.post(
        f"{BASE_URL}/skills",
        json=skill_data
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    print()

def test_chat():
    """Test chat endpoint"""
    print("Testing chat...")
    chat_data = {
        "user_id": "alice",
        "team_id": "engineering",
        "message": "Write a Python function to calculate factorial",
        "include_skills": True,
        "max_skills": 3
    }
    response = requests.post(
        f"{BASE_URL}/chat",
        json=chat_data
    )
    print(f"  Status: {response.status_code}")
    data = response.json()
    print(f"  Skills used: {data.get('skills_used', [])}")
    print(f"  Trace ID: {data.get('trace_id', 'N/A')}")
    print(f"  Response preview: {data.get('response', '')[:200]}...")
    print()

def test_evolution():
    """Test evolution endpoint"""
    print("Testing evolution...")
    evolution_data = {
        "user_id": "alice",
        "team_id": "engineering",
        "auto_apply": True
    }
    response = requests.post(
        f"{BASE_URL}/evolve",
        json=evolution_data
    )
    print(f"  Status: {response.status_code}")
    data = response.json()
    print(f"  Status: {data.get('status')}")
    print(f"  Traces analyzed: {data.get('traces_analyzed')}")
    print(f"  Patterns detected: {data.get('patterns_detected')}")
    print(f"  Skills created: {data.get('skills_created')}")
    print()

def test_volume_stats():
    """Test volume stats"""
    print("Testing volume stats...")
    response = requests.get(
        f"{BASE_URL}/volumes/stats",
        params={"user_id": "alice", "team_id": "engineering"}
    )
    print(f"  Status: {response.status_code}")
    data = response.json()
    for volume_type, stats in data.items():
        print(f"  {volume_type.upper()} Volume:")
        print(f"    - Skills: {stats.get('skill_count', 0)}")
        print(f"    - Traces: {stats.get('trace_count', 0)}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("LLMos-Lite API Test Suite")
    print("=" * 60)
    print()

    try:
        test_health()
        test_list_skills()
        test_create_skill()
        test_chat()
        test_evolution()
        test_volume_stats()

        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server.")
        print("Make sure the server is running: python api/main.py")
    except Exception as e:
        print(f"ERROR: {e}")
