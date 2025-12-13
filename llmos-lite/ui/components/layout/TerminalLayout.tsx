'use client';

import { useState } from 'react';
import Header from './Header';
import VolumesPanel from '../panel1-volumes/VolumesPanel';
import SessionPanel from '../panel2-session/SessionPanel';
import ArtifactPanel from '../panel3-artifacts/ArtifactPanel';

export default function TerminalLayout() {
  const [activeVolume, setActiveVolume] = useState<'system' | 'team' | 'user'>('user');
  const [activeSession, setActiveSession] = useState<string | null>('quantum-research');
  const [viewMode, setViewMode] = useState<'session' | 'cron'>('session');

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden">
      {/* Header */}
      <Header />

      {/* Main 3-Panel Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Panel 1: Volumes Navigator */}
        <div className="w-80 flex-shrink-0 border-r border-terminal-border overflow-hidden">
          <VolumesPanel
            activeVolume={activeVolume}
            onVolumeChange={setActiveVolume}
            activeSession={activeSession}
            onSessionChange={(sessionId) => {
              setActiveSession(sessionId);
              setViewMode('session');
            }}
            onCronClick={() => setViewMode('cron')}
          />
        </div>

        {/* Panel 2: Session/Chat Viewer */}
        <div className="flex-1 border-r border-terminal-border overflow-hidden">
          <SessionPanel
            viewMode={viewMode}
            activeSession={activeSession}
            activeVolume={activeVolume}
          />
        </div>

        {/* Panel 3: Artifact Map & Node Editor */}
        <div className="w-1/3 flex-shrink-0 overflow-hidden">
          <ArtifactPanel
            activeSession={activeSession}
            activeVolume={activeVolume}
          />
        </div>
      </div>
    </div>
  );
}
