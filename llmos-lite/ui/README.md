# LLMos-Lite Web UI

> Terminal-style web interface for LLMos-Lite

## Overview

A browser-based terminal-style interface with three panels:
1. **Volumes Navigator**: System/Team/User hierarchy, sessions, cron updates, git status
2. **Session/Chat Viewer**: Interactive chat with LLM, cron evolution logs
3. **Artifact Map**: Workflow graph visualization, node detail editor

## Quick Start

### Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

### Production

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
ui/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout
│   └── page.tsx                  # Main page
│
├── components/
│   ├── layout/
│   │   ├── TerminalLayout.tsx    # Main 3-panel layout
│   │   └── Header.tsx            # Top bar
│   │
│   ├── panel1-volumes/           # Panel 1 components
│   │   ├── VolumesPanel.tsx
│   │   ├── VolumeTree.tsx
│   │   ├── SessionList.tsx
│   │   ├── CronList.tsx
│   │   └── GitStatus.tsx
│   │
│   ├── panel2-session/           # Panel 2 components
│   │   ├── SessionPanel.tsx
│   │   ├── SessionView.tsx
│   │   ├── ChatInterface.tsx
│   │   └── CronView.tsx
│   │
│   └── panel3-artifacts/         # Panel 3 components
│       ├── ArtifactPanel.tsx
│       ├── WorkflowGraphPlaceholder.tsx
│       └── NodeEditor.tsx
│
├── lib/                          # Utilities
│   ├── pyodide-runner.ts
│   └── workflow-executor.ts
│
├── styles/
│   └── globals.css               # Terminal theme styles
│
├── hooks/                        # React hooks (future)
├── stores/                       # Zustand stores (future)
│
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

## Design System

### Terminal Color Palette

```css
Background:   #0a0e14 (primary), #131721 (secondary), #1c212b (tertiary)
Foreground:   #e6e6e6 (primary), #8a8a8a (secondary), #4a4a4a (tertiary)
Accents:      #00ff88 (green), #00d4ff (blue), #ffcc00 (yellow), #ff4444 (red)
Borders:      #2a2e3a
Cursor:       #00ff88
Selection:    rgba(0, 255, 136, 0.3)
```

### Typography

- Font: JetBrains Mono (monospace)
- Size: 14px base
- Line height: 1.5

### Components

- `.terminal-panel`: Panel container with border
- `.btn-terminal`: Green outlined button
- `.btn-terminal-secondary`: Gray outlined button
- `.terminal-input`: Input with focus glow
- `.terminal-heading`: Uppercase green heading
- `.status-*`: Status indicators (active, success, error, warning, pending)
- `.git-badge`: Git status badge
- `.code-block`: Code block with border

## Features (Phase 1)

✅ **Implemented**:
- 3-panel terminal layout
- Dark terminal theme
- Volume navigator (System/Team/User)
- Session list with status
- Cron updates viewer
- Git status widget
- Chat interface (static data)
- Cron log viewer
- Workflow graph placeholder
- Node detail editor

❌ **Next Phase**:
- WebSocket real-time updates
- API integration with FastAPI backend
- React Flow workflow graph
- Monaco code editor
- Actual chat with LLM
- Git operations

## Development Status

**Phase 1: Foundation** ✅ Complete
- ✅ Next.js setup
- ✅ Terminal theme
- ✅ 3-panel layout
- ✅ All panels with static data

**Phase 2: Backend Integration** (Next)
- [ ] API client
- [ ] WebSocket connection
- [ ] Real data from FastAPI
- [ ] Chat with LLM

**Phase 3: Advanced Features** (Future)
- [ ] React Flow graph
- [ ] Monaco editor
- [ ] Node drag & drop
- [ ] Live workflow execution

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **UI Library**: React 18
- **Styling**: Tailwind CSS + custom terminal theme
- **State**: Zustand (future)
- **Workflow**: React Flow (future)
- **Editor**: Monaco Editor (future)
- **Terminal**: xterm.js (future)
- **Charts**: Recharts (future)

## API Integration (Coming Soon)

The UI will connect to the FastAPI backend at `http://localhost:8000`:

```typescript
// Example API calls (future)
const sessions = await fetch('http://localhost:8000/sessions?user_id=alice');
const chat = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  body: JSON.stringify({ message: 'Help me...' })
});
```

## Contributing

See the main [WEB_UI_DESIGN.md](../WEB_UI_DESIGN.md) for the complete design specification.

## License

Apache 2.0
