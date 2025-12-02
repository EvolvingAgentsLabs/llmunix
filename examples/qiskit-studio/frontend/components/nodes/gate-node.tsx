/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

"use client"

import { memo } from "react"
import { Handle, Position, type NodeProps } from "reactflow"
import { Card, CardContent } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"

interface GateNodeData {
  label: string
  gateType: string
  pythonCode?: string
  inputCode?: string
  onInputChange?: (nodeId: string, newInput: string) => void
  onParameterChange?: (nodeId: string, parameterName: string, newValue: any) => void
  isUpdating?: boolean
}

export const GateNode = memo(({ data, isConnectable }: NodeProps<GateNodeData>) => {
  const getGateColor = () => {
    switch (data.gateType) {
      case "h":
        return "bg-blue-500"
      case "x":
        return "bg-red-500"
      case "y":
        return "bg-yellow-500"
      case "z":
        return "bg-purple-500"
      case "cx":
        return "bg-green-500"
      case "ccx":
        return "bg-orange-500"
      default:
        return "bg-gray-500"
    }
  }

  return (
    <Card className="w-32 border-2">
      <CardContent className="p-2">
        <div className="flex items-center">
          <div
            className={`w-6 h-6 rounded-full ${getGateColor()} flex items-center justify-center text-white font-bold mr-2`}
          >
            {data.gateType.toUpperCase()}
          </div>
          <div className="text-xs font-medium flex-1 flex items-center">
            {data.label}
            {data.isUpdating && (
              <Spinner size={8} className="ml-2 text-gray-500" />
            )}
          </div>
        </div>
      </CardContent>
      <Handle type="target" position={Position.Top} isConnectable={isConnectable} />
      <Handle type="source" position={Position.Bottom} isConnectable={isConnectable} />
    </Card>
  )
})

GateNode.displayName = "GateNode"
