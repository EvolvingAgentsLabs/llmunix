/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

"use client"

import type React from "react"

import { useState } from "react"
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
  type Connection,
  addEdge,
  useNodesState,
  useEdgesState,
  Panel,
} from "reactflow"
import "reactflow/dist/style.css"
import { Sidebar } from "./sidebar"
import { CodePanel } from "./code-panel"
import { QuantumInfoNode } from "./nodes/quantum-info-node"
import { TranspilerNode } from "./nodes/transpiler-node"
import { ExecutionNode } from "./nodes/execution-node"
import { RuntimeNode } from "./nodes/runtime-node"
import { VisualizationNode } from "./nodes/visualization-node"
import { generateQiskitCode } from "@/lib/code-generator"

// Register custom node types
const nodeTypes = {
  quantumInfoNode: QuantumInfoNode,
  transpilerNode: TranspilerNode,
  executionNode: ExecutionNode,
  runtimeNode: RuntimeNode,
  visualizationNode: VisualizationNode,
}

// Initial nodes for the circuit
const initialNodes: Node[] = [
  {
    id: "quantum-info-1",
    type: "quantumInfoNode",
    data: { label: "Quantum info library", category: "Hamiltonian" },
    position: { x: 250, y: 100 },
  },
  {
    id: "transpiler-1",
    type: "transpilerNode",
    data: { label: "Transpiler" },
    position: { x: 250, y: 250 },
  },
]

// Initial edges for the circuit
const initialEdges: Edge[] = [
  {
    id: "e-quantum-transpiler",
    source: "quantum-info-1",
    target: "transpiler-1",
  },
]

export function CircuitBuilder() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)

  const qiskitCode = generateQiskitCode(nodes, edges)

  const onConnect = (params: Edge | Connection) => {
    setEdges((eds) => addEdge(params, eds))
  }

  const onNodeClick = (_: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
  }

  const onAddNode = (nodeType: string, nodeData: any) => {
    const newNode = {
      id: `${nodeType}-${Date.now()}`,
      type: nodeType,
      data: nodeData,
      position: {
        x: Math.random() * 300 + 50,
        y: Math.random() * 300 + 50,
      },
    }

    setNodes((nds) => [...nds, newNode])
  }

  return (
    <div className="flex h-screen">
      <Sidebar onAddNode={onAddNode} />
      <div className="flex flex-col flex-1">
        <div className="flex-1 h-full">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
          >
            <Controls />
            <MiniMap />
            <Background variant="dots" gap={12} size={1} />
          </ReactFlow>
        </div>
        <CodePanel code={qiskitCode} />
      </div>
    </div>
  )
}
