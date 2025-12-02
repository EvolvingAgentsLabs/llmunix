"""
RoboOS - Safety Protocol Hook

This hook acts as a "Parental Control" system for the robot,
preventing any dangerous operations before they execute.

It implements the PreToolUse hook from LLM OS Phase 2.5.
"""

from typing import Dict, Any, Optional
from robot_state import get_robot_state, Position


class SafetyProtocolHook:
    """
    Pre-execution safety hook that validates all robot commands.

    This hook intercepts tool calls BEFORE they execute and validates:
    - Position is within workspace bounds
    - Position avoids prohibited zones
    - Movement speed is safe
    - Emergency stop is not active

    Think of this as the "Safety Officer" that has veto power over
    any command the operator or LLM wants to execute.
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize safety hook.

        Args:
            strict_mode: If True, reject any potentially unsafe action.
                        If False, allow with warnings.
        """
        self.strict_mode = strict_mode
        self.violations_log = []

    def __call__(self, tool_name: str, tool_input: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Safety check before tool execution.

        Args:
            tool_name: Name of the tool about to execute
            tool_input: Parameters being passed to the tool

        Returns:
            None if safe to proceed, or Dict with error message if unsafe
        """
        robot_state = get_robot_state()

        # Check emergency stop
        if robot_state.emergency_stop:
            return {
                'blocked': True,
                'reason': 'EMERGENCY STOP ACTIVE - All operations blocked',
                'severity': 'critical'
            }

        # Validate specific tools
        if tool_name == "move_to":
            return self._validate_move(tool_input, robot_state)
        elif tool_name == "move_relative":
            return self._validate_relative_move(tool_input, robot_state)
        elif tool_name == "toggle_tool":
            return self._validate_tool_toggle(tool_input, robot_state)

        # Unknown tools are allowed by default (could be changed in strict mode)
        return None

    def _validate_move(self, tool_input: Dict[str, Any], robot_state) -> Optional[Dict[str, Any]]:
        """Validate absolute movement command."""
        try:
            # Parse target position
            target_position = Position(
                x=float(tool_input.get('x', robot_state.position.x)),
                y=float(tool_input.get('y', robot_state.position.y)),
                z=float(tool_input.get('z', robot_state.position.z)),
                theta=float(tool_input.get('theta', robot_state.position.theta))
            )

            # Check if target position is safe
            is_safe, reason = robot_state.safety_limits.is_position_safe(target_position)

            if not is_safe:
                violation = {
                    'tool': 'move_to',
                    'target': target_position.to_dict(),
                    'reason': reason
                }
                self.violations_log.append(violation)

                return {
                    'blocked': True,
                    'reason': f'SAFETY VIOLATION: {reason}',
                    'severity': 'high',
                    'suggestion': 'Choose a position within workspace bounds and away from prohibited zones'
                }

            # Check movement speed
            distance = robot_state.position.distance_to(target_position)
            max_safe_distance = robot_state.safety_limits.max_speed  # Per command limit

            if distance > max_safe_distance and self.strict_mode:
                return {
                    'blocked': True,
                    'reason': f'Movement too large: {distance:.2f}m > {max_safe_distance:.2f}m safe limit',
                    'severity': 'medium',
                    'suggestion': f'Break movement into smaller steps (< {max_safe_distance}m each)'
                }

            return None  # Safe to proceed

        except (ValueError, KeyError) as e:
            return {
                'blocked': True,
                'reason': f'Invalid move parameters: {str(e)}',
                'severity': 'medium'
            }

    def _validate_relative_move(self, tool_input: Dict[str, Any], robot_state) -> Optional[Dict[str, Any]]:
        """Validate relative movement command."""
        try:
            # Calculate target position
            dx = float(tool_input.get('dx', 0.0))
            dy = float(tool_input.get('dy', 0.0))
            dz = float(tool_input.get('dz', 0.0))
            dtheta = float(tool_input.get('dtheta', 0.0))

            target_position = Position(
                x=robot_state.position.x + dx,
                y=robot_state.position.y + dy,
                z=robot_state.position.z + dz,
                theta=(robot_state.position.theta + dtheta) % 360
            )

            # Use same validation as absolute move
            return self._validate_move(
                {
                    'x': target_position.x,
                    'y': target_position.y,
                    'z': target_position.z,
                    'theta': target_position.theta
                },
                robot_state
            )

        except (ValueError, KeyError) as e:
            return {
                'blocked': True,
                'reason': f'Invalid relative move parameters: {str(e)}',
                'severity': 'medium'
            }

    def _validate_tool_toggle(self, tool_input: Dict[str, Any], robot_state) -> Optional[Dict[str, Any]]:
        """Validate tool activation/deactivation."""
        # Check if current position is safe for tool use
        is_safe, reason = robot_state.safety_limits.is_position_safe(robot_state.position)

        if not is_safe:
            return {
                'blocked': True,
                'reason': f'Cannot activate tool in unsafe position: {reason}',
                'severity': 'high'
            }

        return None  # Safe to proceed

    def get_violations_summary(self) -> Dict[str, Any]:
        """Get a summary of all safety violations."""
        return {
            'total_violations': len(self.violations_log),
            'violations': self.violations_log
        }

    def reset_violations(self):
        """Clear the violations log."""
        self.violations_log.clear()


# Global safety hook instance
_safety_hook = None


def get_safety_hook() -> SafetyProtocolHook:
    """Get the global safety hook instance."""
    global _safety_hook
    if _safety_hook is None:
        _safety_hook = SafetyProtocolHook(strict_mode=True)
    return _safety_hook
