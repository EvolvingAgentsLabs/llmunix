'use client';

interface CronListProps {
  onCronClick: () => void;
}

export default function CronList({ onCronClick }: CronListProps) {
  const crons = [
    {
      id: 'evolution-user',
      name: 'Evolution (User)',
      status: 'completed' as const,
      lastRun: '2h ago',
      patterns: 5,
      skillsGenerated: 2,
      nextRun: '22h',
    },
    {
      id: 'evolution-team',
      name: 'Evolution (Team)',
      status: 'scheduled' as const,
      lastRun: '12h ago',
      patterns: 3,
      skillsGenerated: 0,
      nextRun: '12h',
    },
  ];

  return (
    <div className="space-y-3">
      {crons.map((cron) => (
        <div
          key={cron.id}
          onClick={onCronClick}
          className="p-2 rounded cursor-pointer terminal-hover"
        >
          <div className="flex items-center gap-2 mb-1">
            <span className={cron.status === 'completed' ? 'status-success' : 'status-pending'}>
              {cron.status === 'completed' ? '🔄' : '⏸'}
            </span>
            <span className="text-sm">{cron.name}</span>
          </div>
          <div className="ml-6 text-xs text-terminal-fg-secondary space-y-0.5">
            <div>Last run: {cron.lastRun}</div>
            {cron.status === 'completed' && (
              <>
                <div className="text-terminal-accent-green">
                  {cron.patterns} patterns detected
                </div>
                <div className="text-terminal-accent-blue">
                  {cron.skillsGenerated} skills generated
                </div>
              </>
            )}
            <div>Next run: {cron.nextRun}</div>
          </div>
          <button
            className="btn-terminal text-xs py-0.5 px-2 ml-6 mt-2"
            onClick={(e) => {
              e.stopPropagation();
              onCronClick();
            }}
          >
            View Log
          </button>
        </div>
      ))}
    </div>
  );
}
