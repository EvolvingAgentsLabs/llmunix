# RoboOS - LLM OS as the Brain of a Robot

**Using Large Language Models as the Cognitive Layer for Robotic Control**

RoboOS demonstrates how **LLM OS v3.4.0** can serve as the "brain" of a robotic arm, translating natural language commands into precise, coordinated actions. Built on the latest LLM OS with Sentience Layer and Advanced Tool Use, it showcases multi-layer architecture, safety protocols, and AI-driven control systems.

## What's New in v3.4.0

- **Sentience Layer**: Persistent internal state with valence variables (safety, curiosity, energy, self_confidence)
- **Adaptive Behavior**: Robot behavior adapts based on latent modes (PRECISION, STANDARD, CAUTIOUS, etc.)
- **Safety-First Valence**: High safety setpoint (0.8) ensures maximum caution in robot operations
- **Real-time Sentience Monitoring**: `/sentience` endpoint and WebSocket updates include behavioral state

### Previous Features (v3.3.0)

- **PTC for Repetitive Tasks**: Robot pick-and-place operations replay via Programmatic Tool Calling (99%+ savings)
- **Tool Search**: Operator agent discovers tools on-demand for novel commands
- **Five Execution Modes**: CRYSTALLIZED, FOLLOWER, MIXED, LEARNER, ORCHESTRATOR
- **Auto-Crystallization**: Repeated robot commands become zero-cost Python code

---

## Overview

Imagine controlling a robot with commands like "Pick up the object at (1, 1, 0.5)" or "Move 30cm to the right" — and having an AI that not only understands but also ensures every action is safe. That's RoboOS.

### The Vision

```
┌─────────────────────────────────────────────────────────────────┐
│  HUMAN: "Pick up the object and place it on the shelf"         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                   SENTIENCE LAYER (v3.4.0)                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Valence: safety=0.8  curiosity=0.1  energy=0.6       │    │
│  │  Latent Mode: PRECISION (focused, safe movements)      │    │
│  │  Robotics Profile: HIGH SAFETY | PRECISION MODE        │    │
│  └────────────────────────────────────────────────────────┘    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                    COGNITIVE LAYER (LLM OS)                     │
│  ┌──────────────┐        ┌──────────────────┐                  │
│  │  Operator    │        │  Safety Officer  │                  │
│  │  Agent       │◄──────►│  Agent           │                  │
│  │              │        │                  │                  │
│  │ "Navigate to │        │ "Check: Safe to  │                  │
│  │  object,     │        │  activate tool   │                  │
│  │  activate    │        │  at this         │                  │
│  │  gripper,    │        │  position?"      │                  │
│  │  move to     │        │                  │                  │
│  │  shelf"      │        │                  │                  │
│  └──────┬───────┘        └────────┬─────────┘                  │
│         │                         │                            │
│         └─────────┬───────────────┘                            │
│                   ↓                                            │
│         ┌────────────────────┐                                 │
│         │  Safety Hook       │                                 │
│         │  (Pre-validation)  │                                 │
│         └─────────┬──────────┘                                 │
└───────────────────┼────────────────────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                     SOMATIC LAYER                               │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Robot Controller Plugin                               │    │
│  │  - move_to(x, y, z, theta)                            │    │
│  │  - toggle_tool(activate)                              │    │
│  │  - get_camera_feed(view)                              │    │
│  │  - emergency_stop()                                   │    │
│  └─────────────────────┬──────────────────────────────────┘    │
└────────────────────────┼───────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PHYSICAL ROBOT                               │
│  Position: (1.5, 1.0, 0.5)   Tool: [ACTIVE]                   │
│  Within safe bounds ✓        Away from prohibited zones ✓     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Features

### For Roboticists
- **Natural Language Control**: Skip low-level programming; give high-level commands
- **Multi-Layer Safety**: PreToolUse hook prevents dangerous operations before execution
- **State Visualization**: ASCII "cockpit view" and overhead map (ready for 3D frontend)
- **PTC-Powered Replay**: Teach the robot once, replay via PTC (99%+ cost savings, 90%+ token savings)
- **Multi-Agent Coordination**: Operator and Safety Officer work together

### For AI Engineers
- **LLM OS Integration**: Demonstrates Somatic Layer (tools) + Cognitive Layer (agents)
- **SDK Hooks**: PreToolUse safety hook implementation
- **Agent Specialization**: Operator (control) vs. Safety Officer (monitoring)
- **RESTful API**: FastAPI server for frontend integration
- **WebSocket Support**: Real-time state updates

### For Safety Engineers
- **Prohibited Zones**: Define no-go areas (e.g., human workspaces)
- **Workspace Bounds**: Hard limits on X, Y, Z movement
- **Speed Limits**: Prevent dangerous rapid movements
- **Emergency Stop**: Instant halt with lock-out
- **Violation Logging**: Track and analyze safety events

---

## Architecture

### Layers

**0. Sentience Layer (v3.4.0)**
- **Valence Variables**: safety, curiosity, energy, self_confidence
- **Homeostatic Dynamics**: Setpoints drive behavior back to equilibrium
- **Latent Modes**: PRECISION, STANDARD, CAUTIOUS, RECOVERY, ADAPTIVE
- **Robotics Profile**: High safety (0.8), low curiosity (0.1) for precise operations

**1. Cognitive Layer (LLM OS)**
- **Operator Agent**: Translates natural language → tool calls
- **Safety Officer Agent**: Monitors operations, issues warnings
- **Memory (L4)**: Learns patterns for Learner → Follower optimization

**2. Somatic Layer (Robot Controller Plugin)**
- **Tools**: `move_to`, `move_relative`, `toggle_tool`, `get_camera_feed`, `go_home`, `emergency_stop`
- **Safety Hook**: Validates all commands pre-execution
- **State Manager**: Tracks position, tool status, history

**3. Physical Layer (Simulated Robot)**
- **Position**: (x, y, z, theta) in 3D workspace
- **Tool**: Gripper/actuator (active/inactive)
- **Sensors**: "Camera feeds" (cockpit/operator views)

### Safety Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  USER COMMAND: "Move to (5, 0, 1)" [OUTSIDE BOUNDS!]           │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│  OPERATOR AGENT: Interprets command, prepares move_to() call   │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│  SAFETY HOOK (Pre-Tool-Use): Validates position                │
│  ❌ BLOCKED: "X position 5.00m outside workspace [-2, 2]"      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│  AGENT RECEIVES ERROR: Explains to user why it was blocked     │
│  "I cannot move to (5, 0, 1) - it's outside the safe workspace"│
└─────────────────────────────────────────────────────────────────┘
```

**Critical Insight**: The safety hook acts as "Parental Control" — dangerous commands are intercepted and blocked BEFORE execution, not after.

---

## Quick Start

### Prerequisites
- Python 3.10+
- LLM OS installed (from parent directory)
- Anthropic API key

### Installation

```bash
# 1. Navigate to robo-os directory
cd examples/robo-os

# 2. Run automated setup
./run.sh

# The script will:
#   - Create virtual environment
#   - Install dependencies
#   - Start interactive demo
```

### Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API key
export ANTHROPIC_API_KEY="your-key-here"

# 4. Run interactive demo
python3 demo.py
```

### Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Get robot state
curl http://localhost:8000/state

# Send natural language command
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{"command": "Show me the cockpit view"}'
```

---

## Demos

Run `python3 demo.py` to access the interactive demo menu:

### Demo 1: Basic Robot Operation
See the Operator Agent translate natural language into robot actions.

**Commands Demonstrated:**
- "Show me the cockpit view"
- "Move 0.5 meters to the right"
- "Show me the operator view"

**What You'll See:**
- ASCII cockpit HUD with instrument panel
- Overhead map showing robot position
- Real-time state updates

### Demo 2: Safety Hook Protection
Watch the safety hook block dangerous commands.

**Dangerous Commands:**
- Move outside workspace bounds (X > 2.0m)
- Move into prohibited zone (collision risk)
- Move below ground (Z < 0)

**What You'll See:**
- Safety violations logged
- Commands blocked before execution
- Detailed error messages explaining WHY

### Demo 3: Multi-Agent Operation
Operator and Safety Officer work together.

**Workflow:**
1. **Safety Officer**: Performs initial safety check
2. **Operator**: Executes multi-step task (move → activate → return)
3. **Safety Officer**: Reviews operations and provides assessment

**What You'll See:**
- Collaborative multi-agent workflow
- Safety Officer's proactive monitoring
- Operator's precise execution

### Demo 4: Learner → Follower Cost Optimization
See how LLM OS saves costs on repetitive tasks.

**Scenario:**
- Task: "Pick up object at (1.5, 1.0, 0.5) and place at (-1.0, -1.0, 0.7)"
- First time: LEARNER mode plans and executes (~2,500 tokens)
- Future times: FOLLOWER mode replays trace (0 tokens - FREE!)

**Token Comparison:**
- 1000 executions without caching: **~2,500,000 tokens**
- 1000 executions with Learner/Follower: **~2,500 tokens** (99.9% savings!)

### Demo 5: Interactive Mode
Send your own commands to the robot!

**Example Commands:**
```
> Show me the cockpit view
> Move 20cm to the right
> Go to position (1, 1, 1.5)
> Activate the gripper
> Return home
> What's the current position?
```

---

## API Reference

### Base URL
```
http://localhost:8000
```

### Endpoints

#### `GET /`
Service information and available endpoints.

#### `GET /health`
Health check with emergency stop status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-21T10:30:00",
  "emergency_stop": false,
  "llmos_ready": true
}
```

#### `GET /state`
Get current robot state and recent actions.

**Response:**
```json
{
  "state": {
    "position": {"x": 0.0, "y": 0.0, "z": 1.0, "theta": 0.0},
    "tool_active": false,
    "emergency_stop": false,
    "timestamp": "2025-11-21T10:30:00"
  },
  "safety_limits": {
    "workspace": {"x": [-2.0, 2.0], "y": [-2.0, 2.0], "z": [0.0, 3.0]},
    "max_speed": 0.5,
    "prohibited_zones": [...]
  },
  "recent_actions": [...]
}
```

#### `POST /command`
Execute natural language command via agent.

**Request:**
```json
{
  "command": "Move the arm 30cm to the right",
  "agent": "operator"
}
```

**Response:**
```json
{
  "success": true,
  "command": "Move the arm 30cm to the right",
  "agent": "operator",
  "response": "Successfully moved 30cm to the right. Robot is now at (0.3, 0, 1).",
  "timestamp": "2025-11-21T10:30:00"
}
```

#### `POST /move`
Direct movement (bypasses NL, still validated by safety hook).

**Request:**
```json
{
  "x": 1.0,
  "y": 0.5,
  "z": 1.5,
  "theta": 90.0
}
```

#### `POST /tool`
Activate or deactivate tool.

**Request:**
```json
{
  "activate": true
}
```

#### `POST /view`
Get camera feed view.

**Request:**
```json
{
  "view_type": "cockpit"
}
```

**Response:**
```
╔═══════════════════════════════════════════════════════════════╗
║                        ROBO-OS COCKPIT                        ║
╠═══════════════════════════════════════════════════════════════╣
║  POSITION:                                                    ║
║    X:   0.00 m  [-2.0 to 2.0]                                ║
║    Y:   0.00 m  [-2.0 to 2.0]                                ║
║    Z:   1.00 m  [0.0 to 3.0]                                 ║
║    θ:    0.0°   [0.0 to 360.0]                               ║
║  TOOL STATUS: [INACTIVE]                                      ║
║  SAFETY STATUS: [OK]                                          ║
╚═══════════════════════════════════════════════════════════════╝
```

#### `GET /safety`
Get safety status and violation history.

**Response:**
```json
{
  "current_position_safe": true,
  "reason": null,
  "emergency_stop": false,
  "violations": {
    "total_violations": 3,
    "violations": [...]
  },
  "sentience_safety": {
    "safety_valence": 0.8,
    "level": "critical"
  }
}
```

#### `GET /sentience` (v3.4.0)
Get current Sentience Layer state and behavioral profile.

**Response:**
```json
{
  "enabled": true,
  "valence": {
    "safety": 0.8,
    "curiosity": 0.1,
    "energy": 0.6,
    "self_confidence": 0.5
  },
  "latent_mode": "auto_contained",
  "mode_description": "PRECISION mode - Focused on exact, controlled movements",
  "policy": {
    "exploration_rate": 0.05,
    "verbosity": "normal",
    "self_improvement_enabled": false
  },
  "robotics_profile": {
    "safety_priority": "HIGH",
    "precision_mode": true,
    "operational_readiness": true
  },
  "timestamp": "2025-11-27T10:30:00"
}
```

#### `POST /reset`
Reset robot to home position and clear state.

#### `POST /emergency`
Trigger emergency stop (LOCKS SYSTEM).

#### `WebSocket /ws`
Real-time state updates (1Hz).

---

## Robot State

### Position
- **X**: -2.0 to 2.0 meters (left-right)
- **Y**: -2.0 to 2.0 meters (forward-backward)
- **Z**: 0.0 to 3.0 meters (up-down, 0 = ground)
- **θ (theta)**: 0 to 360 degrees (rotation)

### Home Position
- **(0, 0, 1, 0)**: Center of workspace, 1m above ground, facing forward

### Prohibited Zones
- **Default**: Sphere at (0, 0, 1) with 0.5m radius (human safety zone)
- Robot must stay >0.5m away

### Speed Limits
- **Max movement per command**: 0.5 meters
- **Max rotation per command**: 45 degrees per second

---

## Sentience Layer (v3.4.0)

RoboOS uses the LLM OS Sentience Layer to provide adaptive, context-aware robot behavior.

### Valence Variables

The system maintains four internal state variables optimized for robotics:

| Variable | Setpoint | Purpose |
|----------|----------|---------|
| **Safety** | 0.8 (HIGH) | Maximum caution for physical operations |
| **Curiosity** | 0.1 (LOW) | Focus on precision, not exploration |
| **Energy** | 0.6 (MODERATE) | Sustained operational capacity |
| **Self-Confidence** | 0.5 (BALANCED) | Reliable but not overconfident |

### Latent Modes for Robotics

| Mode | Description | When Active |
|------|-------------|-------------|
| **PRECISION** | Focused, exact movements | Low curiosity (normal for robotics) |
| **STANDARD** | Normal safe operation | Balanced valence |
| **CAUTIOUS** | Extra validation, minimal movements | Low safety valence |
| **RECOVERY** | Conservative operations | Low energy |
| **ADAPTIVE** | Exploring alternatives | High curiosity (unusual) |

### How Sentience Affects Robot Behavior

```
┌─────────────────────────────────────────────────────────────────┐
│  Command: "Move to position (1.5, 0.5, 1.0)"                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│  SENTIENCE LAYER checks internal state:                         │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  safety=0.8 → HIGH SAFETY PRIORITY                     │    │
│  │  curiosity=0.1 → PRECISION MODE (no exploration)       │    │
│  │  energy=0.6 → OPERATIONAL READY                        │    │
│  └────────────────────────────────────────────────────────┘    │
│  Latent Mode: PRECISION → Agent uses exact coordinates         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│  COGNITIVE LAYER (Operator Agent):                              │
│  Receives sentience context → Executes with precision focus     │
└─────────────────────────────────────────────────────────────────┘
```

### Why Robotics Needs Sentience

1. **Consistent Safety**: High safety setpoint ensures the robot always prioritizes safe operations
2. **Precision Focus**: Low curiosity prevents unnecessary exploration during critical tasks
3. **Operational Awareness**: Energy tracking helps manage sustained operation cycles
4. **Adaptive Recovery**: When issues occur, the system can enter recovery mode automatically

### Configuration

The sentience profile is configured in `server.py`:

```python
config = LLMOSConfig(
    sentience=SentienceConfig(
        enable_sentience=True,
        safety_setpoint=0.8,      # Very high for robot control
        curiosity_setpoint=0.1,   # Low - focus on precision
        energy_setpoint=0.6,      # Moderate for sustained ops
        self_confidence_setpoint=0.5,
        boredom_threshold=-0.4    # Higher - routine is good
    )
)
```

---

## Safety Features

### 1. Pre-Tool-Use Hook
Every command is validated BEFORE execution:
- Position within workspace? ✓
- Clear of prohibited zones? ✓
- Movement speed safe? ✓
- Emergency stop active? ✗

### 2. Multi-Layer Validation
```
User Command → Agent Planning → Safety Hook → Tool Execution
                                     ↑
                              BLOCKS IF UNSAFE
```

### 3. Violation Logging
All blocked commands are logged:
```python
{
  'tool': 'move_to',
  'target': {'x': 5.0, 'y': 0, 'z': 1.0},
  'reason': 'X position 5.00m outside workspace [-2, 2]'
}
```

### 4. Emergency Stop
- **Trigger**: `/emergency` endpoint or `emergency_stop()` tool
- **Effect**: ALL operations blocked until manual reset
- **Use Case**: Collision detection, human intervention

### 5. Safety Officer Agent
- **Role**: Advisory and oversight (can't control robot)
- **Actions**: Issue warnings, recommend alternatives, educate users
- **Access**: Read-only tools (status, camera) + emergency_stop

---

## PTC-Powered Robot Control (v3.3.0)

### How It Works with Programmatic Tool Calling

**Learner Mode (First Time):**
```
User: "Pick up object at (1.5, 1.0, 0.5)"
  ↓
Agent plans:
  1. move_to(1.5, 1.0, 0.5)
  2. toggle_tool(True)
  ↓
Executes and stores trace with full tool_calls for PTC
Tokens: ~2,500
```

**Follower Mode + PTC (Subsequent Times):**
```
User: "Pick up object at (1.5, 1.0, 0.5)"  [Same input!]
  ↓
Learning Layer finds matching trace
  ↓
Execution Layer uses PTC to replay tool sequence
  - Tool calls execute OUTSIDE context window
  - 90%+ token savings
Tokens: ~0
```

**Crystallized Mode (After 5+ repetitions):**
```
User: "Pick up object at (1.5, 1.0, 0.5)"  [Frequent command!]
  ↓
Pattern crystallized into pure Python function
  ↓
Direct execution, no LLM at all
Tokens: 0 (truly FREE!)
```

### Use Cases
- **Repetitive tasks**: Pick-and-place, inspection, assembly (PTC replay)
- **Batch operations**: Process 1000 items with near-zero cost
- **Training workflows**: Human teaches once, robot replays via PTC forever
- **Factory lines**: Crystallized patterns for maximum throughput

### Token Savings Example

**Scenario**: Robot performs quality inspection 100 times per day

| Approach | Daily Tokens | Monthly Tokens | Yearly Tokens |
|----------|------------|--------------|-------------|
| No LLM OS | ~250,000 | ~7,500,000 | ~91,250,000 |
| FOLLOWER + PTC | ~2,500 | ~75,000 | ~912,500 |
| CRYSTALLIZED | 0 | 0 | 0 |
| **Savings** | **99%+** | **99%+** | **99%+** |

---

## Frontend Integration

RoboOS backend is frontend-agnostic. Here's how to build a UI:

### Recommended Stack
- **3D Rendering**: Three.js / React Three Fiber
- **UI Framework**: React / Vue / Svelte
- **Real-Time**: WebSocket connection to `/ws`
- **API Client**: Axios / Fetch

### Example: React + Three.js

```javascript
import { Canvas } from '@react-three/fiber';
import { useEffect, useState } from 'react';

function RobotVisualization() {
  const [robotState, setRobotState] = useState(null);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'state_update') {
        setRobotState(data.state);
      }
    };

    return () => ws.close();
  }, []);

  return (
    <Canvas>
      <RobotArm position={robotState?.position} />
      <Workspace bounds={{x: [-2, 2], y: [-2, 2], z: [0, 3]}} />
      <ProhibitedZone center={[0, 0, 1]} radius={0.5} />
    </Canvas>
  );
}

// Send command
async function sendCommand(command) {
  const response = await fetch('http://localhost:8000/command', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({command, agent: 'operator'})
  });
  return await response.json();
}
```

### UI/UX Recommendations

1. **Cockpit View**: Show real-time instrument panel (position, tool status, safety)
2. **3D Visualization**: Render robot arm, workspace bounds, prohibited zones
3. **Command Input**: Natural language text box or voice input
4. **Safety Indicators**: Color-coded status (green/yellow/red)
5. **Action History**: List recent commands and results
6. **Emergency Button**: Large, obvious emergency stop button

---

## Use Cases

### Manufacturing
- **Task**: "Inspect widget at position (1.2, 0.8, 0.6) and report defects"
- **Benefit**: Natural language quality control; Learner/Follower for repeated inspections

### Warehouse Automation
- **Task**: "Pick item from shelf A3 and place in bin B7"
- **Benefit**: Flexible picking logic; agents adapt to new items

### Research Labs
- **Task**: "Move sample to microscope stage at (0.5, 0.5, 1.0)"
- **Benefit**: Researchers give high-level commands without programming

### Education
- **Task**: Students command robot: "Draw a square" or "Stack the blocks"
- **Benefit**: Learn robotics through natural interaction

### Teleoperation
- **Task**: Remote operator: "Move slightly left" (agent interprets "slightly")
- **Benefit**: Less precise commands still work; safety hook prevents accidents

---

## Advanced Topics

### Custom Prohibited Zones

Edit `robot_state.py`:

```python
self.prohibited_zones = [
    (Position(0.0, 0.0, 1.0, 0.0), 0.5),  # Human zone
    (Position(1.5, 1.5, 0.5, 0.0), 0.3),  # Machine zone
    (Position(-1.0, -1.0, 2.0, 0.0), 0.4) # Fragile equipment
]
```

### Custom Tools

Add new tools to `plugins/robot_controller.py`:

```python
async def calibrate_sensors() -> str:
    """Run sensor calibration routine."""
    # Implementation
    return json.dumps({'success': True, 'calibration': 'complete'})

ROBOT_CONTROLLER_TOOLS.append({
    'name': 'calibrate_sensors',
    'function': calibrate_sensors,
    'description': 'Run sensor calibration routine'
})
```

### Custom Agents

Create specialized agents for specific tasks:

```python
ASSEMBLY_AGENT_CONFIG = {
    'name': 'assembly_specialist',
    'mode': 'learner',
    'system_prompt': """You specialize in assembly tasks.
    You know optimal sequences for common assembly operations..."""
}
```

### Physics Simulation Integration

Replace simulated state with real physics:

```python
# Use PyBullet, MuJoCo, or Isaac Sim
import pybullet as p

def update_robot_position(x, y, z, theta):
    # Set position in physics sim
    p.resetBasePositionAndOrientation(
        robot_id,
        [x, y, z],
        p.getQuaternionFromEuler([0, 0, theta])
    )
```

---

## Deployment

### Development
```bash
python3 demo.py  # Interactive demo
python3 server.py  # API server
```

### Production

**Option 1: Docker**
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["python3", "server.py"]
```

```bash
docker build -t robo-os .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY robo-os
```

**Option 2: Systemd Service**
```ini
[Unit]
Description=RoboOS Server
After=network.target

[Service]
Type=simple
User=robot
WorkingDirectory=/opt/robo-os
Environment="ANTHROPIC_API_KEY=your-key"
ExecStart=/opt/robo-os/venv/bin/python server.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Production Checklist
- [ ] Set secure CORS origins in `server.py`
- [ ] Enable HTTPS (use nginx reverse proxy)
- [ ] Add authentication/authorization
- [ ] Configure rate limiting
- [ ] Set up logging (Sentry, CloudWatch)
- [ ] Add performance monitoring
- [ ] Test emergency stop procedures
- [ ] Document safety protocols

---

## Troubleshooting

### Server won't start
**Error:** `ModuleNotFoundError: No module named 'boot'`
```bash
# Ensure you're in the correct directory
cd examples/robo-os
python3 -c "import sys; sys.path.insert(0, '../..'); from boot.llm_os import LLMOS"
```

### Safety hook not blocking
**Symptom:** Dangerous moves succeed
```python
# Verify hook is registered
llmos.register_hook('pre_tool_use', get_safety_hook())
```

### Agent not responding
**Error:** `Agent not initialized`
```bash
# Check API key
echo $ANTHROPIC_API_KEY

# Restart server
python3 server.py
```

### WebSocket connection fails
**Error:** `WebSocket connection closed`
- Check firewall settings (port 8000)
- Verify server is running
- Check CORS configuration

---

## Contributing

Want to improve RoboOS? Great!

### Areas for Enhancement
1. **Physics Integration**: PyBullet, MuJoCo, Isaac Sim
2. **Computer Vision**: Object detection, pose estimation
3. **Advanced Planning**: Path planning, obstacle avoidance
4. **Multi-Robot**: Coordinate multiple arms
5. **Voice Control**: Speech-to-text integration
6. **AR/VR Interface**: Immersive control interface

### Development Guidelines
- **Safety First**: All PRs must maintain safety guarantees
- **Test Coverage**: Include tests for new tools/agents
- **Documentation**: Update README and docstrings
- **Type Hints**: Use Python type annotations

---

## Resources

### Robotics
- [Robot Operating System (ROS)](https://www.ros.org/)
- [MoveIt Motion Planning](https://moveit.ros.org/)
- [PyBullet Physics](https://pybullet.org/)

### LLM OS
- [LLM OS Documentation](../../README.md)
- [Phase 2.5 Features](../../docs/phase_2.5.md)

### Related Examples
- [Qiskit Studio](../qiskit_studio_backend/README.md) - Similar architecture
- [Q-Kids Studio](../q-kids-studio/README.md) - Safety-first design

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

- **LLM OS Team**: For the innovative OS architecture
- **Robotics Community**: For inspiration on safety-first design
- **Industrial Safety Standards**: ISO 10218 (Robot Safety)

---

**Built to demonstrate the future of human-robot collaboration!**

*Where natural language meets precise control, and AI ensures safety.*
