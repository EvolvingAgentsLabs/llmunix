/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

"use client"

import { memo, useState } from "react"
import { Handle, Position, type NodeProps } from "reactflow"
import { Card } from "@/components/ui/card"
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

interface CircuitLibraryNodeData {
  label: string
  category: string
  pythonCode?: string
  inputCode?: string
  onInputChange?: (nodeId: string, newInput: string) => void
  onParameterChange?: (nodeId: string, parameterName: string, newValue: any) => void
  isUpdating?: boolean
}

export const CircuitLibraryNode = memo(({ id, data, isConnectable }: NodeProps<CircuitLibraryNodeData>) => {
  const [isInfoOpen, setIsInfoOpen] = useState(false)
  const [category, setCategory] = useState(data.category)

  const handleCategoryChange = (value: string) => {
    setCategory(value)
    
    const circuitLibraryCode = `circuit_library_type = "${value}"
from qiskit.circuit.library import ${value}
if circuit_library_type == "Ansatz":
    circuit = ${value}(num_qubits=2, reps=2)
elif circuit_library_type == "PauliTwoDesign":
    circuit = ${value}(num_qubits=2, reps=2)
elif circuit_library_type == "TwoLocal":
    circuit = ${value}(num_qubits=2, rotation_blocks='ry', entanglement_blocks='cz')
elif circuit_library_type == "NLocal":
    circuit = ${value}(num_qubits=2, rotation_blocks=['ry', 'rz'], entanglement_blocks='cz')
else:
    circuit = QuantumCircuit(2)`
    
    data.onInputChange?.(id || '', circuitLibraryCode)
    data.onParameterChange?.(id || '', 'circuit_library_type', value)
  }

  return (
    <Card className="w-64 border-0 shadow-md rounded-none overflow-hidden">
      <div className="bg-[#FFEFF7] h-12 flex items-center">
        <div className="w-12 h-12 bg-[#D02771] flex items-center justify-center text-white mr-2">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
          </svg>
        </div>
        <div className="text-sm font-medium text-black flex-1 flex items-center">
          {data.label}
          {data.isUpdating && (
            <Spinner size={12} className="ml-2 text-white" />
          )}
        </div>
        {data.pythonCode && (
          <Dialog open={isInfoOpen} onOpenChange={setIsInfoOpen}>
            <DialogTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 text-[#D02771] hover:bg-[#D02771]/10 mr-2"
              >
                <Info className="h-4 w-4" />
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
      <div className="bg-white">
        <div className="bg-white p-3 border-b border-[#e0e0e0]">
          <Select value={category} onValueChange={handleCategoryChange}>
            <SelectTrigger className="h-8 text-sm rounded-none bg-transparent border-0 border-b border-[#ccc] p-0 pb-1 text-[#666] font-normal focus:ring-0">
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
            <div className="mt-2 text-xs text-orange-500 flex items-center">
              <Spinner size={8} className="mr-1 text-orange-500" />
              Updating...
            </div>
          )}
        </div>
      </div>
      <Handle 
        type="target" 
        position={Position.Top} 
        isConnectable={isConnectable} 
        style={{ 
          backgroundColor: 'white', 
          border: '1px solid #D02771', 
          borderRadius: '50%', 
          width: '16px', 
          height: '16px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          top: '-20px'
        }}
      >
        <div style={{ backgroundColor: '#D02771', borderRadius: '50%', width: '6px', height: '6px' }} />
      </Handle>
      <Handle 
        type="source" 
        position={Position.Bottom} 
        isConnectable={isConnectable} 
        style={{ 
          backgroundColor: 'white', 
          border: '1px solid #D02771', 
          borderRadius: '50%', 
          width: '16px', 
          height: '16px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          bottom: '-20px'
        }}
      >
        <div style={{ backgroundColor: '#D02771', borderRadius: '50%', width: '6px', height: '6px' }} />
      </Handle>
    </Card>
  )
})

CircuitLibraryNode.displayName = "CircuitLibraryNode"
