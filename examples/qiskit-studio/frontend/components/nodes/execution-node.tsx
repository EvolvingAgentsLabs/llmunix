/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

"use client"

import { memo } from "react"
import { Handle, Position, type NodeProps } from "reactflow"
import { Card } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"

interface ExecutionNodeData {
  label: string
  pythonCode?: string
  inputCode?: string
  onInputChange?: (nodeId: string, newInput: string) => void
  onParameterChange?: (nodeId: string, parameterName: string, newValue: any) => void
  isUpdating?: boolean
}

export const ExecutionNode = memo(({ data, isConnectable }: NodeProps<ExecutionNodeData>) => {
  return (
    <Card className="w-64 border-0 shadow-md rounded-none overflow-hidden">
      <div className="bg-[#E4EDF7] h-12 flex items-center">
        <div className="w-12 h-12 bg-[#0E62FE] flex items-center justify-center text-white mr-2">
          <img src="/node_icons/execute.svg" alt="Execute" width="24" height="24" className="filter brightness-0 invert" />
        </div>
        <div className="text-sm font-medium text-black flex-1 flex items-center">
          {data.label}
          {data.isUpdating && (
            <Spinner size={12} className="ml-2 text-white" />
          )}
        </div>
      </div>
      <Handle 
        type="target" 
        position={Position.Top} 
        isConnectable={isConnectable} 
        style={{ 
          backgroundColor: 'white', 
          border: '1px solid #0E62FE', 
          borderRadius: '50%', 
          width: '16px', 
          height: '16px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          top: '-20px'
        }}
      >
        <div style={{ backgroundColor: '#0E62FE', borderRadius: '50%', width: '6px', height: '6px' }} />
      </Handle>
      <Handle 
        type="source" 
        position={Position.Bottom} 
        isConnectable={isConnectable} 
        style={{ 
          backgroundColor: 'white', 
          border: '1px solid #0E62FE', 
          borderRadius: '50%', 
          width: '16px', 
          height: '16px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          bottom: '-20px'
        }}
      >
        <div style={{ backgroundColor: '#0E62FE', borderRadius: '50%', width: '6px', height: '6px' }} />
      </Handle>
    </Card>
  )
})

ExecutionNode.displayName = "ExecutionNode"
