'use client';

export default function Header() {
  return (
    <header className="h-12 bg-terminal-bg-secondary border-b border-terminal-border flex items-center justify-between px-4">
      <div className="flex items-center gap-3">
        <div className="text-terminal-accent-green font-bold text-lg">
          LLMos-Lite
        </div>
        <div className="text-terminal-fg-tertiary text-xs">
          Web Terminal
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="text-terminal-fg-secondary text-sm">
          alice@engineering
        </div>
        <div className="w-2 h-2 rounded-full bg-terminal-accent-green animate-pulse-slow" />
      </div>
    </header>
  );
}
