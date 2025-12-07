"""
LLMOS Data Provider - Connects Terminal to Real LLMOS Data

This module bridges the Cron Terminal to actual LLMOS components:
- TraceManager: Execution traces and patterns
- MemoryStore: Facts and insights
- TokenEconomy: Spending and budget
- Dispatcher: Execution statistics

Usage:
    from kernel.terminal.llmos_data_provider import LLMOSDataProvider

    provider = LLMOSDataProvider(llmos_instance)
    terminal = CronTerminal(
        user_id="alice",
        status_callback=provider.get_system_status,
        events_callback=provider.get_events,
        suggestions_callback=provider.get_suggestions,
        cron_callback=provider.handle_user_message
    )
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


class LLMOSDataProvider:
    """
    Provides real LLMOS data to the Cron Terminal.

    Maps LLMOS internal state to the terminal's expected format.
    """

    def __init__(
        self,
        trace_manager=None,
        memory_store=None,
        token_economy=None,
        dispatcher=None,
        workspace: Optional[Path] = None
    ):
        """
        Initialize the data provider.

        Args:
            trace_manager: TraceManager instance
            memory_store: MemoryStore instance
            token_economy: TokenEconomy instance
            dispatcher: Dispatcher instance
            workspace: Workspace path
        """
        self.trace_manager = trace_manager
        self.memory_store = memory_store
        self.token_economy = token_economy
        self.dispatcher = dispatcher
        self.workspace = workspace or Path("./workspace")

        # Track activity events
        self._events: List[Dict[str, Any]] = []
        self._max_events = 50

    def log_event(self, event_type: str, title: str, metadata: Optional[Dict] = None):
        """Log an activity event"""
        self._events.insert(0, {
            "event_type": event_type,
            "title": title,
            "timestamp": datetime.now().isoformat(),
            "event_id": f"evt_{len(self._events)}",
            "metadata": metadata or {}
        })
        # Keep only recent events
        self._events = self._events[:self._max_events]

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status for the terminal.

        Returns status in the format expected by CronTerminal.
        """
        # Get trace statistics
        trace_stats = {}
        if self.trace_manager:
            trace_stats = self.trace_manager.get_statistics()

        # Get memory statistics
        memory_stats = {}
        if self.memory_store:
            memory_stats = self.memory_store.get_statistics()

        # Get token economy stats
        token_stats = {}
        if self.token_economy:
            token_stats = {
                "balance": self.token_economy.balance,
                "total_spent": sum(log.cost for log in self.token_economy.spend_log),
                "transactions": len(self.token_economy.spend_log)
            }

        # Get dispatcher stats
        dispatcher_stats = {}
        if self.dispatcher:
            try:
                dispatcher_stats = self.dispatcher.get_execution_layer_stats()
            except:
                pass

        # Determine system state based on activity
        system_state = "idle"
        system_thinking = None

        if trace_stats.get("total_traces", 0) > 0:
            system_state = "analyzing"
            system_thinking = {
                "action": f"Monitoring {trace_stats.get('total_traces', 0)} execution traces",
                "patterns": [
                    {"name": "High-confidence traces", "count": trace_stats.get("high_confidence_count", 0)},
                    {"name": "Total executions", "count": trace_stats.get("total_usage", 0)}
                ]
            }

        # Build user cron status
        user_state = "idle"
        user_thinking = None
        pending_notifications = 0

        # Count insights as pending notifications
        if memory_stats.get("insights_count", 0) > 0:
            pending_notifications = memory_stats.get("insights_count", 0)
            user_state = "analyzing"
            user_thinking = {
                "action": "Reviewing stored insights and facts",
                "considering": [
                    f"{memory_stats.get('facts_count', 0)} facts available",
                    f"{memory_stats.get('insights_count', 0)} insights generated"
                ]
            }

        return {
            "system": {
                "status": system_state,
                "last_run": datetime.now().isoformat(),
                "current_thinking": system_thinking,
                "stats": {
                    "traces": trace_stats,
                    "memory": memory_stats,
                    "tokens": token_stats,
                    "dispatcher": dispatcher_stats
                }
            },
            "teams": {
                "default": {
                    "status": "idle",
                    "last_run": datetime.now().isoformat(),
                    "pending_notifications": 0,
                    "users": {
                        "user": {
                            "status": user_state,
                            "last_run": datetime.now().isoformat(),
                            "pending_notifications": pending_notifications,
                            "current_thinking": user_thinking
                        }
                    }
                }
            }
        }

    async def get_events(self, cron_id: str) -> List[Dict[str, Any]]:
        """Get activity events for a cron"""
        events = list(self._events)

        # Add trace-based events
        if self.trace_manager:
            traces = self.trace_manager.list_traces()
            for trace in traces[:5]:  # Last 5 traces
                events.append({
                    "event_type": "artifact_created",
                    "title": f"Trace: {trace.goal_text[:40]}...",
                    "timestamp": trace.created_at.isoformat(),
                    "event_id": f"trace_{trace.goal_signature[:8]}"
                })

        # Sort by timestamp
        events.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
        return events[:10]

    async def get_suggestions(self, cron_id: str) -> List[Dict[str, Any]]:
        """Get suggestions based on LLMOS state"""
        suggestions = []

        # Suggestions based on trace statistics
        if self.trace_manager:
            stats = self.trace_manager.get_statistics()

            if stats.get("total_traces", 0) == 0:
                suggestions.append({
                    "type": "immediate",
                    "title": "Create your first execution trace",
                    "description": "Run a goal in interactive mode to start learning",
                    "confidence": 1.0,
                    "source": "No traces found"
                })
            elif stats.get("high_confidence_count", 0) > 0:
                suggestions.append({
                    "type": "recommendation",
                    "title": f"You have {stats['high_confidence_count']} reusable patterns",
                    "description": "Similar goals will execute in FOLLOWER mode (faster, cheaper)",
                    "confidence": 0.9,
                    "source": "Trace analysis"
                })

            # Check for crystallization candidates
            traces = self.trace_manager.list_traces()
            for trace in traces:
                if trace.usage_count >= 5 and trace.success_rating >= 0.95:
                    if not trace.crystallized_into_tool:
                        suggestions.append({
                            "type": "recommendation",
                            "title": f"Consider crystallizing: {trace.goal_text[:30]}...",
                            "description": f"Used {trace.usage_count} times with {trace.success_rating:.0%} success",
                            "confidence": 0.85,
                            "source": "HOPE crystallization candidate"
                        })
                        break

        # Suggestions based on memory
        if self.memory_store:
            stats = self.memory_store.get_statistics()

            if stats.get("insights_count", 0) > 0:
                suggestions.append({
                    "type": "prediction",
                    "title": f"Review {stats['insights_count']} stored insights",
                    "description": "Insights extracted from your execution patterns",
                    "confidence": 0.7,
                    "source": "Memory analysis"
                })

        # Budget suggestions
        if self.token_economy:
            remaining = self.token_economy.balance
            if remaining < 2.0:
                suggestions.append({
                    "type": "immediate",
                    "title": "Low token budget warning",
                    "description": f"${remaining:.2f} remaining - consider using FOLLOWER mode",
                    "confidence": 0.95,
                    "source": "Token economy"
                })

        return suggestions

    async def handle_user_message(self, cron_id: str, message: str) -> str:
        """
        Handle user message to their cron.

        Provides intelligent responses based on actual LLMOS state.
        """
        message_lower = message.lower()

        # Status query
        if any(word in message_lower for word in ["status", "stats", "statistics"]):
            return await self._get_status_response()

        # Trace query
        if any(word in message_lower for word in ["trace", "traces", "patterns", "learned"]):
            return await self._get_traces_response()

        # Memory query
        if any(word in message_lower for word in ["memory", "facts", "insights", "remember"]):
            return await self._get_memory_response()

        # Budget query
        if any(word in message_lower for word in ["budget", "tokens", "cost", "spent", "balance"]):
            return await self._get_budget_response()

        # Help
        if any(word in message_lower for word in ["help", "what can", "commands"]):
            return self._get_help_response()

        # Suggestions
        if any(word in message_lower for word in ["suggest", "what should", "recommend", "next"]):
            suggestions = await self.get_suggestions(cron_id)
            if suggestions:
                lines = ["🎯 Here are my suggestions:\n"]
                for i, s in enumerate(suggestions[:3], 1):
                    lines.append(f"{i}. **{s['title']}**")
                    lines.append(f"   {s['description']}")
                return "\n".join(lines)
            return "🤔 No specific suggestions at the moment. Try running some goals first!"

        # Default
        return f"""🤔 I heard: "{message[:50]}{'...' if len(message) > 50 else ''}"

Try asking me about:
• **status** - System statistics
• **traces** - Learned execution patterns
• **memory** - Stored facts and insights
• **budget** - Token spending
• **suggest** - What to do next"""

    async def _get_status_response(self) -> str:
        """Get detailed status response"""
        lines = ["📊 **LLMOS Status**\n"]

        if self.trace_manager:
            stats = self.trace_manager.get_statistics()
            lines.append(f"**Traces**: {stats.get('total_traces', 0)} total, {stats.get('high_confidence_count', 0)} high-confidence")
            lines.append(f"**Avg Success**: {stats.get('avg_success_rate', 0):.0%}")

        if self.memory_store:
            stats = self.memory_store.get_statistics()
            lines.append(f"**Memory**: {stats.get('facts_count', 0)} facts, {stats.get('insights_count', 0)} insights")

        if self.token_economy:
            lines.append(f"**Budget**: ${self.token_economy.balance:.2f} remaining")

        return "\n".join(lines)

    async def _get_traces_response(self) -> str:
        """Get traces information"""
        if not self.trace_manager:
            return "❌ Trace manager not available"

        traces = self.trace_manager.list_traces()

        if not traces:
            return "📝 No execution traces yet. Run some goals to start learning!"

        lines = [f"📚 **{len(traces)} Execution Traces**\n"]

        for trace in traces[:5]:
            status = "💎" if trace.crystallized_into_tool else "✅" if trace.success_rating >= 0.9 else "📝"
            lines.append(f"{status} **{trace.goal_text[:40]}**...")
            lines.append(f"   Mode: {trace.mode} | Used: {trace.usage_count}x | Success: {trace.success_rating:.0%}")

        if len(traces) > 5:
            lines.append(f"\n...and {len(traces) - 5} more traces")

        return "\n".join(lines)

    async def _get_memory_response(self) -> str:
        """Get memory information"""
        if not self.memory_store:
            return "❌ Memory store not available"

        stats = self.memory_store.get_statistics()
        lines = ["🧠 **Memory Store**\n"]
        lines.append(f"**Facts**: {stats.get('facts_count', 0)}")
        lines.append(f"**Insights**: {stats.get('insights_count', 0)}")
        lines.append(f"**Sessions**: {stats.get('sessions_count', 0)}")

        # Show recent facts if available
        facts = self.memory_store.search_facts("", limit=3)
        if facts:
            lines.append("\n**Recent Facts:**")
            for fact in facts:
                lines.append(f"• {fact[:60]}...")

        return "\n".join(lines)

    async def _get_budget_response(self) -> str:
        """Get budget information"""
        if not self.token_economy:
            return "❌ Token economy not available"

        balance = self.token_economy.balance
        spent = sum(log.cost for log in self.token_economy.spend_log)

        lines = ["💰 **Token Economy**\n"]
        lines.append(f"**Balance**: ${balance:.2f}")
        lines.append(f"**Spent**: ${spent:.4f}")
        lines.append(f"**Transactions**: {len(self.token_economy.spend_log)}")

        # Show recent transactions
        if self.token_economy.spend_log:
            lines.append("\n**Recent:**")
            for log in self.token_economy.spend_log[-3:]:
                lines.append(f"• ${log.cost:.4f} - {log.reason[:30]}")

        return "\n".join(lines)

    def _get_help_response(self) -> str:
        """Get help response"""
        return """🤖 **LLMOS Cron Assistant**

I can help you with:

• **status** - View system statistics
• **traces** - See learned execution patterns
• **memory** - View stored facts and insights
• **budget** - Check token spending
• **suggest** - Get recommendations

**Tips:**
- Run goals in interactive mode to create traces
- Similar goals will reuse existing patterns (FOLLOWER mode)
- High-usage patterns can be crystallized into tools (HOPE)"""
