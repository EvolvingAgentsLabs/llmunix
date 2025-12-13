'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  traces?: number[];
  artifact?: string;
  pattern?: {
    name: string;
    confidence: number;
  };
}

interface ChatInterfaceProps {
  messages: Message[];
}

export default function ChatInterface({ messages }: ChatInterfaceProps) {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (!inputValue.trim()) return;
    // TODO: Send message to backend
    console.log('Sending:', inputValue);
    setInputValue('');
  };

  return (
    <div className="h-full flex flex-col">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className="space-y-1">
            {/* Message header */}
            <div className="text-xs text-terminal-fg-tertiary">
              [{message.timestamp}] {message.role === 'user' ? 'You' : 'Assistant'}:
            </div>

            {/* Message content */}
            <div className={`
              p-3 rounded
              ${message.role === 'user'
                ? 'bg-terminal-bg-tertiary text-terminal-fg-primary'
                : 'bg-terminal-bg-primary text-terminal-fg-secondary border border-terminal-border'
              }
            `}>
              {message.content}
            </div>

            {/* Metadata */}
            {message.traces && (
              <div className="text-xs text-terminal-fg-tertiary ml-3">
                ✓ Trace #{message.traces[0]}-{message.traces[message.traces.length - 1]} executed
              </div>
            )}
            {message.artifact && (
              <div className="text-xs text-terminal-accent-blue ml-3">
                ✓ Artifact {message.traces && message.traces.length > 0 ? 'created' : 'updated'}: {message.artifact}
              </div>
            )}
            {message.pattern && (
              <div className="text-xs text-terminal-accent-yellow ml-3">
                ✓ Pattern: {message.pattern.name} ({(message.pattern.confidence * 100).toFixed(0)}%)
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-terminal-border">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            className="flex-1 terminal-input"
          />
          <button onClick={handleSend} className="btn-terminal px-4">
            Send
          </button>
        </div>
        <div className="flex gap-2 mt-2">
          <button className="btn-terminal-secondary text-xs py-1 px-2">
            Attach Workflow
          </button>
          <button className="btn-terminal-secondary text-xs py-1 px-2">
            Settings
          </button>
        </div>
      </div>
    </div>
  );
}
