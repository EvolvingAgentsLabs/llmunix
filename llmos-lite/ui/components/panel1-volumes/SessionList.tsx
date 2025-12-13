'use client';

interface SessionListProps {
  activeVolume: 'system' | 'team' | 'user';
  activeSession: string | null;
  onSessionChange: (sessionId: string) => void;
}

export default function SessionList({
  activeVolume,
  activeSession,
  onSessionChange,
}: SessionListProps) {
  // Static data for demo
  const sessions = {
    user: [
      {
        id: 'quantum-research',
        name: 'quantum-research',
        traces: 48,
        timeAgo: '3h ago',
        status: 'uncommitted' as const,
        patterns: 1,
      },
      {
        id: 'data-pipeline',
        name: 'data-pipeline',
        traces: 12,
        timeAgo: '2d ago',
        status: 'committed' as const,
        commitHash: 'b7e9a2f',
      },
    ],
    team: [
      {
        id: 'graphql-opt',
        name: 'graphql-opt (Bob)',
        traces: 34,
        timeAgo: '1d ago',
        status: 'committed' as const,
        commitHash: 'a1b2c3d',
      },
    ],
    system: [],
  };

  const currentSessions = sessions[activeVolume];

  if (currentSessions.length === 0) {
    return (
      <div className="text-terminal-fg-tertiary text-xs italic">
        No active sessions
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {currentSessions.map((session) => (
        <div
          key={session.id}
          onClick={() => onSessionChange(session.id)}
          className={`
            p-2 rounded cursor-pointer transition-colors
            ${activeSession === session.id ? 'terminal-active' : 'terminal-hover'}
          `}
        >
          <div className="flex items-center gap-2 mb-1">
            <span className={session.status === 'uncommitted' ? 'status-active' : 'status-success'}>
              {session.status === 'uncommitted' ? '●' : '✓'}
            </span>
            <span className="text-sm font-medium">{session.name}</span>
          </div>
          <div className="ml-6 text-xs text-terminal-fg-secondary space-y-0.5">
            <div>{session.traces} traces</div>
            <div>{session.timeAgo}</div>
            {session.status === 'uncommitted' && session.patterns && (
              <div className="text-terminal-accent-yellow">
                {session.patterns} pattern{session.patterns > 1 ? 's' : ''} detected
              </div>
            )}
            {session.status === 'committed' && (
              <div className="git-badge git-badge-committed">
                {session.commitHash}
              </div>
            )}
          </div>
          {session.status === 'uncommitted' && (
            <div className="ml-6 mt-2 flex gap-2">
              <button className="btn-terminal text-xs py-0.5 px-2">
                Commit
              </button>
              <button className="btn-terminal-secondary text-xs py-0.5 px-2">
                Share
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
