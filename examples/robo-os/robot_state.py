"""
RoboOS - Robot State Management and Safety Systems

This module defines the robot state, workspace limits, and safety protocols.
"""

import json
import math
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime


@dataclass
class Position:
    """3D position with rotation."""
    x: float  # meters
    y: float  # meters
    z: float  # meters
    theta: float  # rotation in degrees (0-360)

    def distance_to(self, other: 'Position') -> float:
        """Calculate Euclidean distance to another position."""
        return math.sqrt(
            (self.x - other.x)**2 +
            (self.y - other.y)**2 +
            (self.z - other.z)**2
        )

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class SafetyLimits:
    """Workspace safety limits and constraints."""
    min_x: float = -2.0  # meters
    max_x: float = 2.0
    min_y: float = -2.0
    max_y: float = 2.0
    min_z: float = 0.0  # Never go below ground
    max_z: float = 3.0
    max_speed: float = 0.5  # meters per second
    max_rotation_speed: float = 45.0  # degrees per second

    # Prohibited zones (defined as spheres: center + radius)
    prohibited_zones: List[Tuple[Position, float]] = None

    def __post_init__(self):
        """Initialize prohibited zones if not provided."""
        if self.prohibited_zones is None:
            # Example: A sphere around origin representing a human workspace
            self.prohibited_zones = [
                (Position(0.0, 0.0, 1.0, 0.0), 0.5)  # 0.5m radius safety zone
            ]

    def is_position_safe(self, pos: Position) -> Tuple[bool, Optional[str]]:
        """
        Check if a position is within safe limits.

        Returns:
            (is_safe, reason) - True if safe, False with reason if unsafe
        """
        # Check workspace boundaries
        if not (self.min_x <= pos.x <= self.max_x):
            return False, f"X position {pos.x:.2f}m outside workspace [{self.min_x}, {self.max_x}]"
        if not (self.min_y <= pos.y <= self.max_y):
            return False, f"Y position {pos.y:.2f}m outside workspace [{self.min_y}, {self.max_y}]"
        if not (self.min_z <= pos.z <= self.max_z):
            return False, f"Z position {pos.z:.2f}m outside workspace [{self.min_z}, {self.max_z}]"

        # Check prohibited zones
        for zone_center, radius in self.prohibited_zones:
            distance = pos.distance_to(zone_center)
            if distance < radius:
                return False, f"Position within prohibited zone at ({zone_center.x:.2f}, {zone_center.y:.2f}, {zone_center.z:.2f}), distance: {distance:.2f}m < {radius}m"

        return True, None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'workspace': {
                'x': [self.min_x, self.max_x],
                'y': [self.min_y, self.max_y],
                'z': [self.min_z, self.max_z]
            },
            'max_speed': self.max_speed,
            'max_rotation_speed': self.max_rotation_speed,
            'prohibited_zones': [
                {'center': center.to_dict(), 'radius': radius}
                for center, radius in self.prohibited_zones
            ]
        }


class RobotState:
    """
    Central state manager for the robotic arm.

    Tracks position, tool status, and provides state queries.
    """

    def __init__(self, safety_limits: Optional[SafetyLimits] = None):
        """Initialize robot state."""
        self.position = Position(x=0.0, y=0.0, z=1.0, theta=0.0)  # Start at safe height
        self.tool_active = False  # Gripper/tool state
        self.safety_limits = safety_limits or SafetyLimits()
        self.history: List[Dict[str, Any]] = []
        self.emergency_stop = False

    def get_state(self) -> Dict[str, Any]:
        """Get current robot state as dictionary."""
        return {
            'position': self.position.to_dict(),
            'tool_active': self.tool_active,
            'emergency_stop': self.emergency_stop,
            'timestamp': datetime.now().isoformat()
        }

    def record_action(self, action: str, details: Dict[str, Any]):
        """Record an action in the history."""
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'state': self.get_state(),
            'details': details
        })

    def get_cockpit_view(self) -> str:
        """
        Generate a text-based "cockpit" view of the robot state.

        This is what the operator "sees" - like a flight simulator HUD.
        """
        is_safe, reason = self.safety_limits.is_position_safe(self.position)

        cockpit = f"""
╔═══════════════════════════════════════════════════════════════╗
║                        ROBO-OS COCKPIT                        ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  POSITION:                                                    ║
║    X: {self.position.x:>6.2f} m  [{self.safety_limits.min_x:.1f} to {self.safety_limits.max_x:.1f}]                         ║
║    Y: {self.position.y:>6.2f} m  [{self.safety_limits.min_y:.1f} to {self.safety_limits.max_y:.1f}]                         ║
║    Z: {self.position.z:>6.2f} m  [{self.safety_limits.min_z:.1f} to {self.safety_limits.max_z:.1f}]                         ║
║    θ: {self.position.theta:>6.1f}°   [0.0 to 360.0]                         ║
║                                                               ║
║  TOOL STATUS: {'[ACTIVE]' if self.tool_active else '[INACTIVE]':<44}  ║
║                                                               ║
║  SAFETY STATUS: {'[OK]' if is_safe and not self.emergency_stop else '[WARNING]':<42}  ║
║    {'All systems normal' if is_safe and not self.emergency_stop else (reason or 'EMERGENCY STOP ACTIVE'):<56} ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
        return cockpit

    def get_operator_view(self) -> str:
        """
        Generate an overhead map view showing robot position.

        This is a simple ASCII representation of the workspace.
        """
        # Create a 20x20 grid representing the workspace
        grid_size = 20
        grid = [['·' for _ in range(grid_size)] for _ in range(grid_size)]

        # Map robot position to grid coordinates
        x_range = self.safety_limits.max_x - self.safety_limits.min_x
        y_range = self.safety_limits.max_y - self.safety_limits.min_y

        grid_x = int(((self.position.x - self.safety_limits.min_x) / x_range) * (grid_size - 1))
        grid_y = int(((self.position.y - self.safety_limits.min_y) / y_range) * (grid_size - 1))

        # Clamp to grid bounds
        grid_x = max(0, min(grid_size - 1, grid_x))
        grid_y = max(0, min(grid_size - 1, grid_y))

        # Mark robot position
        grid[grid_y][grid_x] = 'R' if not self.tool_active else 'X'

        # Mark prohibited zones
        for zone_center, radius in self.safety_limits.prohibited_zones:
            zone_grid_x = int(((zone_center.x - self.safety_limits.min_x) / x_range) * (grid_size - 1))
            zone_grid_y = int(((zone_center.y - self.safety_limits.min_y) / y_range) * (grid_size - 1))

            # Draw zone (simple circle approximation)
            zone_radius_grid = int((radius / x_range) * grid_size)
            for dy in range(-zone_radius_grid, zone_radius_grid + 1):
                for dx in range(-zone_radius_grid, zone_radius_grid + 1):
                    if dx*dx + dy*dy <= zone_radius_grid*zone_radius_grid:
                        y = zone_grid_y + dy
                        x = zone_grid_x + dx
                        if 0 <= y < grid_size and 0 <= x < grid_size:
                            if grid[y][x] not in ['R', 'X']:
                                grid[y][x] = '█'

        # Create view
        view = "\n  OPERATOR VIEW (Overhead Map)\n"
        view += "  " + "─" * (grid_size + 2) + "\n"
        for row in reversed(grid):  # Reverse to have Y axis pointing up
            view += "  │" + "".join(row) + "│\n"
        view += "  " + "─" * (grid_size + 2) + "\n"
        view += f"  Legend: R=Robot  X=Robot(Tool Active)  █=Prohibited Zone  ·=Safe Space\n"
        view += f"  Robot at: ({self.position.x:.2f}, {self.position.y:.2f}, {self.position.z:.2f})\n"

        return view

    def get_camera_feed(self, view_type: str = "cockpit") -> str:
        """
        Get a "camera feed" view of the robot.

        Args:
            view_type: "cockpit" or "operator"

        Returns:
            Formatted text view
        """
        if view_type == "cockpit":
            return self.get_cockpit_view()
        elif view_type == "operator":
            return self.get_operator_view()
        else:
            return f"Unknown view type: {view_type}"


# Global robot state instance
_robot_state = None


def get_robot_state() -> RobotState:
    """Get the global robot state instance."""
    global _robot_state
    if _robot_state is None:
        _robot_state = RobotState()
    return _robot_state


def reset_robot_state():
    """Reset the global robot state (useful for testing)."""
    global _robot_state
    _robot_state = RobotState()
