'use client';

interface VolumeTreeProps {
  activeVolume: 'system' | 'team' | 'user';
  onVolumeChange: (volume: 'system' | 'team' | 'user') => void;
}

export default function VolumeTree({ activeVolume, onVolumeChange }: VolumeTreeProps) {
  const volumes = [
    {
      id: 'system' as const,
      label: 'System',
      icon: '📁',
      skills: 23,
      traces: 0,
      readonly: true,
    },
    {
      id: 'team' as const,
      label: 'Team: engineering',
      icon: '📁',
      skills: 15,
      traces: 234,
      readonly: false,
    },
    {
      id: 'user' as const,
      label: 'User: alice',
      icon: '📁',
      skills: 3,
      traces: 48,
      readonly: false,
    },
  ];

  return (
    <div className="space-y-2">
      {volumes.map((volume) => (
        <div
          key={volume.id}
          onClick={() => onVolumeChange(volume.id)}
          className={`
            p-2 rounded cursor-pointer transition-colors
            ${activeVolume === volume.id ? 'terminal-active' : 'terminal-hover'}
          `}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span>{volume.icon}</span>
              <span className="text-sm">{volume.label}</span>
              {activeVolume === volume.id && (
                <span className="text-terminal-accent-green">●</span>
              )}
            </div>
            {volume.readonly && (
              <span className="text-xs text-terminal-fg-tertiary">readonly</span>
            )}
          </div>
          <div className="ml-6 mt-1 text-xs text-terminal-fg-secondary">
            <div>{volume.skills} skills</div>
            <div>{volume.traces} traces</div>
          </div>
        </div>
      ))}
    </div>
  );
}
