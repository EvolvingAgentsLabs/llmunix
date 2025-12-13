'use client';

import VolumeTree from './VolumeTree';
import SessionList from './SessionList';
import CronList from './CronList';
import GitStatus from './GitStatus';

interface VolumesPanelProps {
  activeVolume: 'system' | 'team' | 'user';
  onVolumeChange: (volume: 'system' | 'team' | 'user') => void;
  activeSession: string | null;
  onSessionChange: (sessionId: string) => void;
  onCronClick: () => void;
}

export default function VolumesPanel({
  activeVolume,
  onVolumeChange,
  activeSession,
  onSessionChange,
  onCronClick,
}: VolumesPanelProps) {
  return (
    <div className="h-full flex flex-col bg-terminal-bg-secondary">
      {/* Volume Tree */}
      <div className="p-4 border-b border-terminal-border">
        <h2 className="terminal-heading text-xs mb-3">VOLUMES</h2>
        <VolumeTree
          activeVolume={activeVolume}
          onVolumeChange={onVolumeChange}
        />
      </div>

      {/* Sessions List */}
      <div className="flex-1 p-4 border-b border-terminal-border overflow-auto">
        <h2 className="terminal-heading text-xs mb-3">
          SESSIONS ({activeVolume})
        </h2>
        <SessionList
          activeVolume={activeVolume}
          activeSession={activeSession}
          onSessionChange={onSessionChange}
        />
      </div>

      {/* Cron Updates */}
      <div className="p-4 border-b border-terminal-border">
        <h2 className="terminal-heading text-xs mb-3">CRON UPDATES</h2>
        <CronList onCronClick={onCronClick} />
      </div>

      {/* Git Status */}
      <div className="p-4">
        <h2 className="terminal-heading text-xs mb-3">GIT STATUS</h2>
        <GitStatus activeVolume={activeVolume} />
      </div>
    </div>
  );
}
