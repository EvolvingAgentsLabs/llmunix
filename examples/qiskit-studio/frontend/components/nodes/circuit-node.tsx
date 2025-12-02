/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

"use client"

import { memo, useState } from "react"
import { Handle, Position, type NodeProps } from "reactflow"
import { Card, CardContent } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Info } from "lucide-react"
import { Spinner } from "@/components/ui/spinner"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

interface CircuitNodeData {
  label: string
  category: string
  pythonCode?: string
  inputCode?: string
  onInputChange?: (nodeId: string, newInput: string) => void
  onParameterChange?: (nodeId: string, parameterName: string, newValue: any) => void
  isUpdating?: boolean
}

export const CircuitNode = memo(({ id, data, isConnectable }: NodeProps<CircuitNodeData>) => {
  const [isInfoOpen, setIsInfoOpen] = useState(false)
  const [category, setCategory] = useState(data.category)

  const handleCategoryChange = (value: string) => {
    setCategory(value)
    
    // Generate Python code string for the circuit category
    const circuitCode = `circuit_type = "${value}"
# Configure ${value} circuit
if circuit_type == "Ansatz":
    circuit = AnsatzCircuit(num_qubits=2, reps=2)
elif circuit_type == "PauliTwoDesign":
    circuit = PauliTwoDesign(num_qubits=2, reps=2)
elif circuit_type == "TwoLocal":
    circuit = TwoLocal(num_qubits=2, rotation_blocks='ry', entanglement_blocks='cz')
elif circuit_type == "NLocal":
    circuit = NLocal(num_qubits=2, rotation_blocks=['ry', 'rz'], entanglement_blocks='cz')
else:
    circuit = QuantumCircuit(2)`
    
    data.onInputChange?.(id || '', circuitCode)
    data.onParameterChange?.(id || '', 'circuit_type', value)
  }

  return (
    <Card className="w-48 border-2 border-blue-200">
      <CardContent className="p-2">
        <div className="flex items-center mb-2">
          <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold mr-2">
            C
          </div>
          <div className="text-xs font-medium flex-1 flex items-center">
            {data.label}
            {data.isUpdating && (
              <Spinner size={12} className="ml-2 text-blue-500" />
            )}
          </div>
          {data.pythonCode && (
            <Dialog open={isInfoOpen} onOpenChange={setIsInfoOpen}>
              <DialogTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-4 w-4 p-0 text-blue-500 hover:bg-blue-50"
                >
                  <Info className="h-3 w-3" />
                </Button>
              </DialogTrigger>
              <DialogContent className="overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>{data.label} - Python Code</DialogTitle>
                </DialogHeader>
                <div className="mt-4">
                  <pre className="bg-gray-900 text-green-400 p-4 rounded-md text-xs overflow-x-auto">
                    <code>{data.pythonCode}</code>
                  </pre>
                </div>
              </DialogContent>
            </Dialog>
          )}
        </div>
        <Select value={category} onValueChange={handleCategoryChange}>
          <SelectTrigger className="h-7 text-xs">
            <SelectValue placeholder="Select category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Ansatz">Ansatz</SelectItem>
            <SelectItem value="PauliTwoDesign">PauliTwoDesign</SelectItem>
            <SelectItem value="TwoLocal">TwoLocal</SelectItem>
            <SelectItem value="NLocal">NLocal</SelectItem>
          </SelectContent>
        </Select>
        {data.isUpdating && (
          <div className="mt-1 text-xs text-orange-500 flex items-center">
            <Spinner size={8} className="mr-1 text-orange-500" />
            Updating...
          </div>
        )}
      </CardContent>
      <Handle type="target" position={Position.Top} isConnectable={isConnectable} />
      <Handle type="source" position={Position.Bottom} isConnectable={isConnectable} />
    </Card>
  )
})

CircuitNode.displayName = "CircuitNode"
