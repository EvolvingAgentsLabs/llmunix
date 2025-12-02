"""
RoboOS - Robot Controller Plugin

Provides tools for controlling the robotic arm, including:
- Movement commands (absolute and relative)
- Tool activation/deactivation
- Camera/sensor feeds
- Emergency controls

All tools are designed to work with the safety hook to prevent
dangerous operations.
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from robot_state import get_robot_state, Position


async def move_to(x: float, y: float, z: float, theta: float = None) -> str:
    """
    Move the robot arm to an absolute position in the workspace.

    Args:
        x: X coordinate in meters (-2.0 to 2.0)
        y: Y coordinate in meters (-2.0 to 2.0)
        z: Z coordinate in meters (0.0 to 3.0)
        theta: Optional rotation in degrees (0-360). If not provided, keeps current rotation.

    Returns:
        JSON string with status and new position

    Safety:
        This command is validated by the SafetyProtocolHook before execution.
        If the target position is outside workspace bounds or in a prohibited zone,
        the hook will block the command.

    Example:
        move_to(1.0, 0.5, 1.5, 90.0)  # Move to (1.0, 0.5, 1.5) facing 90 degrees
    """
    robot_state = get_robot_state()

    # Store previous position for logging
    previous_position = robot_state.position.to_dict()

    # Update position
    new_position = Position(
        x=x,
        y=y,
        z=z,
        theta=theta if theta is not None else robot_state.position.theta
    )

    # Verify safety (redundant check, hook should have caught this)
    is_safe, reason = robot_state.safety_limits.is_position_safe(new_position)
    if not is_safe:
        # This should have been blocked by the hook, but double-check
        return json.dumps({
            'success': False,
            'error': f'Unsafe position: {reason}',
            'current_position': previous_position
        })

    # Execute move
    robot_state.position = new_position

    # Record action
    robot_state.record_action('move_to', {
        'from': previous_position,
        'to': new_position.to_dict()
    })

    return json.dumps({
        'success': True,
        'message': f'Moved to ({x:.2f}, {y:.2f}, {z:.2f}) at {new_position.theta:.1f}°',
        'previous_position': previous_position,
        'new_position': new_position.to_dict()
    })


async def move_relative(dx: float = 0.0, dy: float = 0.0, dz: float = 0.0, dtheta: float = 0.0) -> str:
    """
    Move the robot arm relative to its current position.

    Args:
        dx: Change in X coordinate (meters)
        dy: Change in Y coordinate (meters)
        dz: Change in Z coordinate (meters)
        dtheta: Change in rotation (degrees)

    Returns:
        JSON string with status and new position

    Safety:
        This command is validated by the SafetyProtocolHook to ensure the
        resulting position is safe.

    Example:
        move_relative(dx=0.1, dz=-0.2)  # Move 0.1m right, 0.2m down
    """
    robot_state = get_robot_state()

    # Calculate target position
    target_x = robot_state.position.x + dx
    target_y = robot_state.position.y + dy
    target_z = robot_state.position.z + dz
    target_theta = (robot_state.position.theta + dtheta) % 360

    # Use move_to for the actual movement (reuses safety checks)
    return await move_to(target_x, target_y, target_z, target_theta)


async def toggle_tool(activate: bool) -> str:
    """
    Activate or deactivate the robot's tool (gripper/actuator).

    Args:
        activate: True to activate, False to deactivate

    Returns:
        JSON string with status

    Safety:
        The tool can only be activated if the robot is in a safe position.
        The SafetyProtocolHook verifies this before activation.

    Example:
        toggle_tool(True)   # Activate gripper
        toggle_tool(False)  # Deactivate gripper
    """
    robot_state = get_robot_state()

    previous_state = robot_state.tool_active
    robot_state.tool_active = activate

    # Record action
    robot_state.record_action('toggle_tool', {
        'from': previous_state,
        'to': activate
    })

    return json.dumps({
        'success': True,
        'message': f'Tool {"activated" if activate else "deactivated"}',
        'tool_active': activate,
        'position': robot_state.position.to_dict()
    })


async def get_camera_feed(view_type: str = "cockpit") -> str:
    """
    Get the current camera/sensor feed from the robot.

    This provides a "visual" representation of the robot's environment,
    similar to a flight simulator's cockpit view or overhead map.

    Args:
        view_type: Type of view to retrieve
            - "cockpit": Heads-up display with instrument panel
            - "operator": Overhead map showing robot and obstacles

    Returns:
        Formatted text view of the robot's environment

    Example:
        get_camera_feed("cockpit")   # Get HUD view
        get_camera_feed("operator")  # Get overhead map
    """
    robot_state = get_robot_state()
    return robot_state.get_camera_feed(view_type)


async def get_status() -> str:
    """
    Get comprehensive status information about the robot.

    Returns:
        JSON string with complete robot state, safety limits, and history

    Example:
        get_status()  # Get full system status
    """
    robot_state = get_robot_state()

    return json.dumps({
        'current_state': robot_state.get_state(),
        'safety_limits': robot_state.safety_limits.to_dict(),
        'emergency_stop': robot_state.emergency_stop,
        'recent_actions': robot_state.history[-5:] if robot_state.history else []
    }, indent=2)


async def emergency_stop() -> str:
    """
    EMERGENCY: Immediately halt all robot operations.

    This activates the emergency stop, which blocks ALL future commands
    until manually reset. Use only in dangerous situations.

    Returns:
        JSON string confirming emergency stop activation

    WARNING:
        After calling this, the robot will not respond to any commands
        until the emergency stop is manually cleared by resetting the system.
    """
    robot_state = get_robot_state()
    robot_state.emergency_stop = True

    robot_state.record_action('emergency_stop', {
        'position': robot_state.position.to_dict()
    })

    return json.dumps({
        'success': True,
        'message': 'EMERGENCY STOP ACTIVATED - All operations halted',
        'position': robot_state.position.to_dict()
    })


async def go_home() -> str:
    """
    Return the robot to its home position.

    Home position is a safe, neutral position:
    - X: 0.0m, Y: 0.0m, Z: 1.0m (center, elevated)
    - Theta: 0.0° (facing forward)
    - Tool: deactivated

    Returns:
        JSON string with status

    Example:
        go_home()  # Return to safe home position
    """
    robot_state = get_robot_state()

    # Deactivate tool first
    await toggle_tool(False)

    # Move to home position
    result = await move_to(0.0, 0.0, 1.0, 0.0)

    robot_state.record_action('go_home', {})

    return json.dumps({
        'success': True,
        'message': 'Returned to home position',
        'position': robot_state.position.to_dict()
    })


# Tool registry for LLM OS
ROBOT_CONTROLLER_TOOLS = [
    {
        'name': 'move_to',
        'function': move_to,
        'description': 'Move robot arm to absolute position (x, y, z, theta)',
    },
    {
        'name': 'move_relative',
        'function': move_relative,
        'description': 'Move robot arm relative to current position',
    },
    {
        'name': 'toggle_tool',
        'function': toggle_tool,
        'description': 'Activate or deactivate the robot tool/gripper',
    },
    {
        'name': 'get_camera_feed',
        'function': get_camera_feed,
        'description': 'Get visual feed from robot cameras (cockpit or operator view)',
    },
    {
        'name': 'get_status',
        'function': get_status,
        'description': 'Get comprehensive robot status and state information',
    },
    {
        'name': 'emergency_stop',
        'function': emergency_stop,
        'description': 'EMERGENCY: Halt all robot operations immediately',
    },
    {
        'name': 'go_home',
        'function': go_home,
        'description': 'Return robot to safe home position',
    },
]
