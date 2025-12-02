"""
Token Economy - Manages the cost of intelligence (the "battery")
"""

from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime


class LowBatteryError(Exception):
    """Raised when token budget is insufficient"""
    pass


@dataclass
class SpendLog:
    """Log entry for token spending"""
    timestamp: datetime
    operation: str
    cost: float
    balance_after: float


class TokenEconomy:
    """
    Manages the token budget (the "battery" of the OS)
    Every cognitive cycle consumes resources
    """

    def __init__(self, budget_usd: float):
        """
        Initialize token economy

        Args:
            budget_usd: Initial budget in USD
        """
        self.balance = budget_usd
        self.initial_budget = budget_usd
        self.spend_log: List[SpendLog] = []

    def check_budget(self, estimated_cost: float) -> bool:
        """
        Check if budget is sufficient

        Args:
            estimated_cost: Estimated cost in USD

        Returns:
            True if budget is sufficient

        Raises:
            LowBatteryError if insufficient funds
        """
        if self.balance < estimated_cost:
            raise LowBatteryError(
                f"Insufficient funds for Learner Mode. "
                f"Required: ${estimated_cost:.4f}, Available: ${self.balance:.4f}"
            )
        return True

    def deduct(self, actual_cost: float, operation: str = "unknown"):
        """
        Deduct cost from budget

        Args:
            actual_cost: Actual cost in USD
            operation: Description of the operation
        """
        self.balance -= actual_cost

        log_entry = SpendLog(
            timestamp=datetime.now(),
            operation=operation,
            cost=actual_cost,
            balance_after=self.balance
        )
        self.spend_log.append(log_entry)

    def get_usage_report(self) -> Dict:
        """Get usage report"""
        total_spent = sum(log.cost for log in self.spend_log)

        return {
            "initial_budget": self.initial_budget,
            "current_balance": self.balance,
            "total_spent": total_spent,
            "num_operations": len(self.spend_log),
            "average_cost": total_spent / len(self.spend_log) if self.spend_log else 0
        }
