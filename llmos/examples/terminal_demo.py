#!/usr/bin/env python3
"""
Cron Terminal Demo - Interactive Dashboard Tutorial

This demo shows the Cron Terminal with simulated real-time cron activity.
It demonstrates how UserCrons, TeamCrons, and SystemCron work together.

Usage:
    cd llmos
    python examples/terminal_demo.py

What you'll see:
    - Live cron status updates (thinking, analyzing, idle)
    - Suggestions appearing based on "analysis"
    - Activity log with recent events
    - Interactive chat with your personal cron
"""

import asyncio
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kernel.terminal import CronTerminal, TerminalConfig


# =============================================================================
# SIMULATED CRON DATA
# =============================================================================

class SimulatedCronSystem:
    """
    Simulates a real cron system with evolving state.

    In production, this would connect to the actual Sentience Cron system.
    For this demo, it generates realistic-looking data that changes over time.
    """

    def __init__(self, user_id: str, team_id: str):
        self.user_id = user_id
        self.team_id = team_id
        self.cycle_count = 0

        # Simulated state
        self.user_pending_notifications = 5
        self.team_pending_notifications = 3

        # Activity log
        self.events: List[Dict[str, Any]] = []
        self._generate_initial_events()

        # Suggestions
        self.suggestions: List[Dict[str, Any]] = []
        self._generate_initial_suggestions()

        # Thinking states cycle
        self.thinking_states = [
            {"action": "Reviewing your recent traces", "considering": ["Suggest caching pattern"]},
            {"action": "Analyzing code patterns", "patterns": [{"name": "API optimization", "count": 12}]},
            {"action": "Cross-referencing team insights", "cross_refs": ["bob's database work"]},
            {"action": "Evaluating improvement opportunities", "considering": ["Refactor auth module"]},
            {"action": "Idle - monitoring for changes", "considering": []},
        ]

    def _generate_initial_events(self):
        """Generate some initial activity events"""
        now = datetime.now()
        events = [
            {"event_type": "cron_started", "title": "UserCron started monitoring", "minutes_ago": 45},
            {"event_type": "artifact_created", "title": "Created trace: api_endpoint_handler", "minutes_ago": 30},
            {"event_type": "insight_generated", "title": "Found pattern: repeated null checks", "minutes_ago": 22},
            {"event_type": "suggestion_created", "title": "Suggested: Add input validation", "minutes_ago": 15},
            {"event_type": "cron_cycle_end", "title": "Analysis cycle completed", "minutes_ago": 5},
        ]

        for event in events:
            timestamp = now - timedelta(minutes=event["minutes_ago"])
            self.events.append({
                "event_type": event["event_type"],
                "title": event["title"],
                "timestamp": timestamp.isoformat(),
                "event_id": f"evt_{random.randint(1000, 9999)}"
            })

    def _generate_initial_suggestions(self):
        """Generate initial suggestions"""
        self.suggestions = [
            {
                "type": "immediate",
                "title": "Review pending code changes",
                "description": "3 files modified in last session need review",
                "confidence": 0.92,
                "source": "Based on your commit patterns"
            },
            {
                "type": "recommendation",
                "title": "Consider adding error handling",
                "description": "Found 5 functions without try/catch blocks",
                "confidence": 0.78,
                "source": "Code analysis"
            },
            {
                "type": "prediction",
                "title": "You might work on auth next",
                "description": "Based on your recent file access patterns",
                "confidence": 0.65,
                "source": "Behavioral analysis"
            }
        ]

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status.

        This simulates what the real SystemCron.get_global_status() would return.
        """
        self.cycle_count += 1

        # Rotate through thinking states
        thinking_index = self.cycle_count % len(self.thinking_states)
        user_thinking = self.thinking_states[thinking_index]

        # Determine states based on cycle
        user_state = "thinking" if thinking_index < 4 else "idle"
        team_state = "analyzing" if self.cycle_count % 3 == 0 else "idle"
        system_state = "thinking" if self.cycle_count % 5 == 0 else "idle"

        # Occasionally add new events
        if self.cycle_count % 2 == 0:
            self._add_random_event()

        # Occasionally update suggestions
        if self.cycle_count % 4 == 0:
            self._rotate_suggestions()

        return {
            "system": {
                "status": system_state,
                "last_run": datetime.now().isoformat(),
                "current_thinking": {
                    "action": "Coordinating cross-team insights",
                    "patterns": [
                        {"name": "Shared utility functions", "count": 8},
                        {"name": "Common error patterns", "count": 5}
                    ]
                } if system_state == "thinking" else None
            },
            "teams": {
                self.team_id: {
                    "status": team_state,
                    "last_run": datetime.now().isoformat(),
                    "pending_notifications": self.team_pending_notifications,
                    "current_thinking": {
                        "action": f"Analyzing {self.team_id} team patterns",
                        "patterns": [{"name": "Code review bottleneck", "count": 3}]
                    } if team_state == "analyzing" else None,
                    "users": {
                        self.user_id: {
                            "status": user_state,
                            "last_run": datetime.now().isoformat(),
                            "pending_notifications": self.user_pending_notifications,
                            "current_task": "Monitoring your workspace" if user_state == "idle" else None,
                            "current_thinking": user_thinking if user_state == "thinking" else None
                        },
                        "bob": {
                            "status": "thinking" if self.cycle_count % 2 == 1 else "idle",
                            "last_run": datetime.now().isoformat(),
                            "pending_notifications": 2,
                            "current_task": "Optimizing database queries"
                        },
                        "carol": {
                            "status": "idle",
                            "last_run": datetime.now().isoformat(),
                            "pending_notifications": 0
                        }
                    }
                },
                "design": {
                    "status": "idle",
                    "last_run": datetime.now().isoformat(),
                    "pending_notifications": 1,
                    "users": {
                        "dave": {
                            "status": "idle",
                            "last_run": datetime.now().isoformat(),
                            "pending_notifications": 1
                        }
                    }
                }
            }
        }

    def _add_random_event(self):
        """Add a random event to simulate activity"""
        event_types = [
            ("artifact_created", "Created new trace"),
            ("insight_generated", "Discovered pattern"),
            ("cron_cycle_end", "Analysis cycle completed"),
            ("suggestion_created", "New suggestion available"),
        ]

        event_type, title = random.choice(event_types)
        self.events.insert(0, {
            "event_type": event_type,
            "title": f"{title}: {random.choice(['auth', 'api', 'utils', 'config'])}",
            "timestamp": datetime.now().isoformat(),
            "event_id": f"evt_{random.randint(1000, 9999)}"
        })

        # Keep only last 20 events
        self.events = self.events[:20]

    def _rotate_suggestions(self):
        """Rotate suggestions to simulate new insights"""
        new_suggestions = [
            {"type": "immediate", "title": "Run tests before commit", "confidence": 0.95},
            {"type": "recommendation", "title": "Update documentation", "confidence": 0.72},
            {"type": "creative", "title": "Try a different algorithm approach", "confidence": 0.55},
            {"type": "prediction", "title": "Likely to refactor soon", "confidence": 0.68},
        ]

        # Replace one random suggestion
        if self.suggestions:
            idx = random.randint(0, len(self.suggestions) - 1)
            self.suggestions[idx] = random.choice(new_suggestions)

    async def get_events(self, cron_id: str) -> List[Dict[str, Any]]:
        """Get events for a specific cron"""
        return self.events[:10]

    async def get_suggestions(self, cron_id: str) -> List[Dict[str, Any]]:
        """Get suggestions for a specific cron"""
        if cron_id == f"user:{self.user_id}":
            return self.suggestions
        return []

    async def send_to_cron(self, cron_id: str, message: str) -> str:
        """
        Send a message to a cron and get a response.

        This simulates the actual cron responding to user queries.
        """
        message_lower = message.lower()

        # Simulate intelligent responses
        if any(word in message_lower for word in ["status", "what are you doing", "working on"]):
            return f"🔍 I'm currently in cycle {self.cycle_count}. I've analyzed {len(self.events)} events and generated {len(self.suggestions)} suggestions for you."

        if any(word in message_lower for word in ["suggest", "what should", "next", "recommend"]):
            if self.suggestions:
                top = self.suggestions[0]
                return f"🎯 Top suggestion: {top['title']}\nConfidence: {top.get('confidence', 0.5):.0%}\n\nWant me to elaborate on this?"
            return "🤔 I'm still analyzing your patterns. Check back in a moment."

        if any(word in message_lower for word in ["analyze", "look at", "check", "review"]):
            self.cycle_count += 1  # Trigger analysis
            return "🔍 Starting analysis now. I'll update the suggestions panel when I find something interesting."

        if any(word in message_lower for word in ["help", "what can you do", "commands"]):
            return """🤖 I can help you with:

• **Suggestions**: Ask "what should I do next?"
• **Analysis**: Say "analyze my recent work"
• **Status**: Ask "what are you working on?"
• **Patterns**: Say "show me patterns"
• **Clear**: Say "clear notifications"

I'm always monitoring your workspace and learning from your patterns!"""

        if any(word in message_lower for word in ["pattern", "patterns", "found"]):
            return f"""📊 Patterns I've found in your work:

1. **API optimization** - 12 similar traces
2. **Error handling gaps** - 5 locations
3. **Code duplication** - 3 modules

Want me to create improvement suggestions for any of these?"""

        if any(word in message_lower for word in ["clear", "dismiss", "notifications"]):
            self.user_pending_notifications = 0
            return "✅ Cleared all notifications. I'll let you know when something new comes up."

        if any(word in message_lower for word in ["thank", "thanks", "great", "good"]):
            return "😊 Happy to help! Let me know if you need anything else."

        # Default response
        return f"🤔 I heard: \"{message[:50]}{'...' if len(message) > 50 else ''}\"\n\nTry asking me to 'suggest next steps' or 'analyze recent work'."


# =============================================================================
# DEMO RUNNER
# =============================================================================

async def run_demo():
    """Run the terminal demo with simulated data"""

    print("=" * 60)
    print("🖥️  CRON TERMINAL DEMO")
    print("=" * 60)
    print()
    print("This demo shows the Cron Terminal with live simulated data.")
    print()
    print("You are: alice (engineering team)")
    print()
    print("CONTROLS:")
    print("  ↑/↓     Navigate up/down in tree or scroll detail")
    print("  ←/→     Collapse/expand tree nodes")
    print("  Tab     Switch between tree and detail panels")
    print("  Enter   Select a cron / confirm in chat")
    print("  r       Manual refresh")
    print("  a       Toggle auto-refresh (5s interval)")
    print("  q       Quit")
    print()
    print("TRY THIS:")
    print("  1. Press ↓ to navigate to your cron (alice)")
    print("  2. Press Enter to see your detail panel")
    print("  3. Press Tab to switch to detail panel")
    print("  4. Type 'help' and press Enter to chat with your cron")
    print()
    print("Starting in 3 seconds...")
    print("=" * 60)

    await asyncio.sleep(3)

    # Create simulated system
    user_id = "alice"
    team_id = "engineering"
    sim = SimulatedCronSystem(user_id, team_id)

    # Create terminal with callbacks to simulated system
    terminal = CronTerminal(
        user_id=user_id,
        team_id=team_id,
        status_callback=sim.get_system_status,
        events_callback=sim.get_events,
        suggestions_callback=sim.get_suggestions,
        cron_callback=sim.send_to_cron,
        config=TerminalConfig(
            refresh_interval=5.0,  # Refresh every 5 seconds
            auto_refresh=True
        )
    )

    # Run the terminal
    await terminal.run()


async def run_quick_test():
    """Quick non-interactive test to verify everything works"""
    print("Running quick test...")

    user_id = "alice"
    team_id = "engineering"
    sim = SimulatedCronSystem(user_id, team_id)

    terminal = CronTerminal(
        user_id=user_id,
        team_id=team_id,
        status_callback=sim.get_system_status,
        events_callback=sim.get_events,
        suggestions_callback=sim.get_suggestions,
        cron_callback=sim.send_to_cron
    )

    # Refresh and render
    await terminal.refresh()

    # Select user's cron
    terminal.tree_view.select(f"user:{user_id}")
    status = await sim.get_system_status()
    await terminal._refresh_detail(f"user:{user_id}", status)

    # Render
    print(terminal.render())

    # Test chat
    print("\n" + "=" * 60)
    print("Testing chat interaction:")
    print("=" * 60)

    response = await sim.send_to_cron(f"user:{user_id}", "help")
    print(f"\nYou: help")
    print(f"Cron: {response}")

    response = await sim.send_to_cron(f"user:{user_id}", "what should I do next?")
    print(f"\nYou: what should I do next?")
    print(f"Cron: {response}")

    print("\n✅ Quick test passed!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        asyncio.run(run_quick_test())
    else:
        asyncio.run(run_demo())
