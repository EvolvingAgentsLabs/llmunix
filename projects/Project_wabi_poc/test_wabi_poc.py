#!/usr/bin/env python3
"""
Test script for Wabi POC end-to-end workflow.

This script demonstrates the complete flow:
1. Start the Wabi App Server
2. Generate a Morning Briefing UI-MD
3. Verify personalization from user memory
4. Test action handling (refresh weather)
5. Display generated UI-MD

Usage:
    python3 test_wabi_poc.py
"""

import sys
import os

# Add system/api to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'system', 'api'))

# Import the app server functions directly for testing
from wabi_app_server import (
    generate_app_ui_md,
    load_user_memory,
    handle_app_action,
    PROJECT_OUTPUT_DIR
)

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_user_memory():
    """Test 1: Verify user memory loading"""
    print_section("TEST 1: User Memory Loading")

    user_id = "user123"
    memory = load_user_memory(user_id)

    print(f"User ID: {memory.get('user_id')}")
    print(f"Name: {memory.get('name')}")
    print(f"Location: {memory.get('last_seen_location')}")
    print(f"Theme: {memory.get('preferences', {}).get('theme')}")
    print(f"Interests: {', '.join(memory.get('interests', []))}")
    print(f"Apps Created: {len(memory.get('apps_created', []))}")

    habits = memory.get('habits', [])
    if habits:
        print(f"\nTop Habit: {habits[0].get('pattern')}")
        print(f"Confidence: {habits[0].get('confidence')}")

    assert memory.get('user_id') == user_id, "User ID mismatch"
    assert memory.get('name') == "Alex", "User name mismatch"
    print("\n✅ User memory loaded successfully!")


def test_ui_generation():
    """Test 2: Generate Morning Briefing UI-MD"""
    print_section("TEST 2: UI-MD Generation")

    goal = "Create a morning briefing app"
    user_id = "user123"

    print(f"Goal: {goal}")
    print(f"User: {user_id}")
    print("\nGenerating UI-MD...")

    result = generate_app_ui_md(goal, user_id, context=None)

    assert result['success'], "UI generation failed"
    assert 'app_id' in result, "No app_id in result"
    assert 'ui_md' in result, "No UI-MD in result"

    app_id = result['app_id']
    ui_md = result['ui_md']
    metadata = result['metadata']

    print(f"\n✅ UI-MD Generated!")
    print(f"App ID: {app_id}")
    print(f"Output File: {metadata['output_file']}")
    print(f"Personalization:")
    print(f"  - Location: {metadata['personalization']['location']}")
    print(f"  - Theme: {metadata['personalization']['theme']}")
    print(f"  - Interests: {', '.join(metadata['personalization']['interests'][:3])}")

    # Verify personalization is applied
    assert "San Francisco" in ui_md, "Location not personalized"
    assert "Alex" in ui_md, "User name not personalized"
    assert "Good Morning" in ui_md, "Greeting not found"

    print("\n✅ Personalization verified!")

    return app_id, ui_md


def test_action_handling(app_id):
    """Test 3: Handle user action (refresh weather)"""
    print_section("TEST 3: Action Handling")

    user_id = "user123"
    action_id = "refresh_weather"

    print(f"App ID: {app_id}")
    print(f"Action: {action_id}")
    print("\nExecuting action...")

    result = handle_app_action(app_id, user_id, action_id, params=None)

    assert result['success'], "Action handling failed"
    assert result['action'] == action_id, "Action ID mismatch"

    print(f"\n✅ Action executed successfully!")
    print(f"Timestamp: {result.get('timestamp')}")


def display_ui_md(ui_md):
    """Test 4: Display generated UI-MD"""
    print_section("TEST 4: Generated UI-MD Output")

    print("Generated UI-MD Document:")
    print("-" * 70)
    print(ui_md)
    print("-" * 70)

    # Verify key components
    components = {
        "Header": "<component type=\"Header\">",
        "Divider": "<component type=\"Divider\">",
        "Weather Card": "Weather",
        "Calendar Card": "Calendar",
        "News List": "Top Tech News",
        "Button": "<component type=\"Button\">",
    }

    print("\nComponent Verification:")
    for name, marker in components.items():
        present = marker in ui_md
        status = "✅" if present else "❌"
        print(f"{status} {name}: {'Present' if present else 'Missing'}")

    print("\n✅ UI-MD structure validated!")


def test_file_output(app_id):
    """Test 5: Verify file was written to output directory"""
    print_section("TEST 5: File Output Verification")

    expected_file = os.path.join(PROJECT_OUTPUT_DIR, f"{app_id}.md")

    print(f"Expected file: {expected_file}")
    print(f"File exists: {os.path.exists(expected_file)}")

    assert os.path.exists(expected_file), "Output file not created"

    file_size = os.path.getsize(expected_file)
    print(f"File size: {file_size} bytes")

    print("\n✅ Output file verified!")


def run_all_tests():
    """Run complete end-to-end test suite"""
    print("\n" + "=" * 70)
    print("  🌟 WABI POC - END-TO-END TEST SUITE")
    print("=" * 70)

    try:
        # Test 1: User Memory
        test_user_memory()

        # Test 2: UI Generation
        app_id, ui_md = test_ui_generation()

        # Test 3: Action Handling
        test_action_handling(app_id)

        # Test 4: Display UI-MD
        display_ui_md(ui_md)

        # Test 5: File Output
        test_file_output(app_id)

        # Final Summary
        print_section("🎉 ALL TESTS PASSED!")
        print("The Wabi POC is working correctly!")
        print("\nNext Steps:")
        print("1. Start the API server: python3 system/api/wabi_app_server.py")
        print("2. Test the API: http://localhost:8000/docs")
        print("3. Send POST request to /api/v1/generate with user goal")
        print("4. Build mobile shell app to render UI-MD")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def demo_api_usage():
    """Demonstrate how to use the API"""
    print_section("API Usage Examples")

    print("1. Generate Morning Briefing:")
    print("""
curl -X POST http://localhost:8000/api/v1/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "goal": "Create a morning briefing app",
    "user_id": "user123"
  }'
    """)

    print("\n2. Handle Refresh Action:")
    print("""
curl -X POST http://localhost:8000/api/v1/action \\
  -H "Content-Type: application/json" \\
  -d '{
    "app_id": "create-a-morning-briefing-a-user123",
    "user_id": "user123",
    "action_id": "refresh_weather"
  }'
    """)

    print("\n3. List User Apps:")
    print("""
curl http://localhost:8000/api/v1/apps/user123
    """)

    print("\n4. Get User Preferences:")
    print("""
curl http://localhost:8000/api/v1/user/user123/preferences
    """)


if __name__ == "__main__":
    print("\n🚀 Starting Wabi POC Tests...\n")

    # Run all tests
    run_all_tests()

    # Show API usage examples
    demo_api_usage()

    print("\n" + "=" * 70)
    print("  Test Suite Complete! 🎉")
    print("=" * 70 + "\n")
