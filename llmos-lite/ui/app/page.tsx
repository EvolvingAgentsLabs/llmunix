'use client';

import { useState, useEffect } from 'react';
import TerminalLayout from '@/components/layout/TerminalLayout';
import APIKeySetup from '@/components/setup/APIKeySetup';
import { LLMStorage } from '@/lib/llm-client';

export default function Home() {
  const [isConfigured, setIsConfigured] = useState<boolean | null>(null);

  useEffect(() => {
    // Check if API key is configured
    setIsConfigured(LLMStorage.isConfigured());
  }, []);

  // Loading state
  if (isConfigured === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-terminal-bg-primary">
        <div className="text-terminal-accent-green animate-pulse">
          Initializing LLMos-Lite...
        </div>
      </div>
    );
  }

  // Show setup if not configured
  if (!isConfigured) {
    return <APIKeySetup onComplete={() => setIsConfigured(true)} />;
  }

  // Show main terminal interface
  return <TerminalLayout />;
}
