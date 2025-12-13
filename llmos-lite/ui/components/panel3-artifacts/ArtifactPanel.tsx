'use client';

import { useState } from 'react';
import WorkflowGraphPlaceholder from './WorkflowGraphPlaceholder';
import NodeEditor from './NodeEditor';

interface ArtifactPanelProps {
  activeSession: string | null;
  activeVolume: 'system' | 'team' | 'user';
}

export default function ArtifactPanel({ activeSession, activeVolume }: ArtifactPanelProps) {
  const [selectedNode, setSelectedNode] = useState<string | null>('vqe-node');

  return (
    <div className="h-full flex flex-col bg-terminal-bg-secondary">
      {/* Workflow Graph */}
      <div className="h-1/2 border-b border-terminal-border">
        <div className="p-4 border-b border-terminal-border">
          <h2 className="terminal-heading text-xs">WORKFLOW GRAPH</h2>
        </div>
        <div className="h-[calc(100%-3rem)] p-4">
          <WorkflowGraphPlaceholder onNodeSelect={setSelectedNode} selectedNode={selectedNode} />
        </div>
      </div>

      {/* Node Detail */}
      <div className="h-1/2 overflow-auto">
        <div className="p-4 border-b border-terminal-border">
          <h2 className="terminal-heading text-xs">NODE DETAIL</h2>
        </div>
        <div className="p-4">
          <NodeEditor selectedNode={selectedNode} />
        </div>
      </div>
    </div>
  );
}
