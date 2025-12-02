/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

"use client"

import { memo, useState } from "react"
import { Handle, Position, type NodeProps } from "reactflow"
import { Card } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Info } from "lucide-react"
import { Spinner } from "@/components/ui/spinner"

interface TranspilerPassNodeData {
  label: string
  selectedPass?: string
  pythonCode?: string
  inputCode?: string
  onInputChange?: (nodeId: string, newInput: string) => void
  onParameterChange?: (nodeId: string, parameterName: string, newValue: any) => void
  isUpdating?: boolean
}

const transpilerPasses = [
  { name: "Optimize1qGates", description: "Optimize chains of single-qubit u1, u2, u3 gates by combining them into a single gate." },
  { name: "Optimize1qGatesDecomposition", description: "Optimize chains of single-qubit gates by combining them into a single gate." },
  { name: "Collect1qRuns", description: "Collect one-qubit subcircuits." },
  { name: "Collect2qBlocks", description: "Collect two-qubit subcircuits." },
  { name: "CollectMultiQBlocks", description: "Collect sequences of uninterrupted gates acting on groups of qubits." },
  { name: "CollectAndCollapse", description: "A general transpiler pass to collect and to consolidate blocks of nodes in a circuit." },
  { name: "CollectLinearFunctions", description: "Collect blocks of linear gates (CXGate and SwapGate gates) and replaces them by linear functions (LinearFunction)." },
  { name: "CollectCliffords", description: "Collects blocks of Clifford gates and replaces them by a Clifford object." },
  { name: "ConsolidateBlocks", description: "Replace each block of consecutive gates by a single Unitary node." },
  { name: "InverseCancellation", description: "Cancel specific Gates which are inverses of each other when they occur back-to-back." },
  { name: "CommutationAnalysis", description: "Analysis pass to find commutation relations between DAG nodes." },
  { name: "CommutativeCancellation", description: "Cancel the redundant (self-adjoint) gates through commutation relations." },
  { name: "CommutativeInverseCancellation", description: "Cancel pairs of inverse gates exploiting commutation relations." },
  { name: "Optimize1qGatesSimpleCommutation", description: "Optimizes 1Q gate strings interrupted by 2Q gates by commuting the components and resynthesizing the results." },
  { name: "RemoveDiagonalGatesBeforeMeasure", description: "Remove diagonal gates (including diagonal 2Q gates) before a measurement." },
  { name: "RemoveResetInZeroState", description: "Remove reset gate when the qubit is in zero state." },
  { name: "RemoveFinalReset", description: "Remove reset when it is the final instruction on a qubit wire." },
  { name: "HoareOptimizer", description: "This is a transpiler pass using Hoare logic circuit optimization." },
  { name: "TemplateOptimization", description: "Class for the template optimization pass." },
  { name: "ResetAfterMeasureSimplification", description: "This pass replaces reset after measure with a conditional X gate." },
  { name: "OptimizeCliffords", description: "Combine consecutive Cliffords over the same qubits." },
  { name: "ElidePermutations", description: "Remove permutation operations from a pre-layout circuit" },
  { name: "OptimizeAnnotated", description: "Optimization pass on circuits with annotated operations." },
  { name: "Split2QUnitaries", description: "Attempt to splits two-qubit unitaries in a DAGCircuit into two single-qubit gates." },
  { name: "RemoveIdentityEquivalent", description: "Remove gates with negligible effects." },
  { name: "ContractIdleWiresInControlFlow", description: "Remove idle qubits from control-flow operations of a DAGCircuit." },
  { name: "LightCone", description: "Remove the gates that do not affect the outcome of a measurement on a circuit." },
]

export const TranspilerPassNode = memo(({ data, isConnectable }: NodeProps<TranspilerPassNodeData>) => {
  const [selectedPass, setSelectedPass] = useState<string>(data.selectedPass || transpilerPasses[0].name)
  const [showDescription, setShowDescription] = useState<boolean>(false)

  const selectedPassInfo = transpilerPasses.find((pass) => pass.name === selectedPass)
  const description = selectedPassInfo?.description || "No description available"

  return (
    <Card className="w-64 border-0 shadow-md rounded-none overflow-hidden">
      <div className="bg-[#F1EDF9] h-12 flex items-center">
        <div className="w-12 h-12 bg-[#893FFC] flex items-center justify-center text-white mr-2">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
            <path d="M13.5 9.17a3 3 0 0 0 0 5.66" />
          </svg>
        </div>
        <div className="text-sm font-medium text-black flex-1 flex items-center">
          {data.label}
          {data.isUpdating && (
            <Spinner size={12} className="ml-2 text-white" />
          )}
        </div>
      </div>
      <div className="bg-white">
        <div className="p-0">
          <div className="bg-white p-3 border-b border-[#e0e0e0] flex items-center justify-between">
            <Select
              value={selectedPass}
              onValueChange={(value) => {
                setSelectedPass(value)
                data.selectedPass = value
              }}
            >
              <SelectTrigger className="h-8 text-sm rounded-none bg-transparent border-0 border-b border-[#ccc] p-0 pb-1 text-[#333] font-normal focus:ring-0 w-36">
                <SelectValue placeholder="Select pass" />
              </SelectTrigger>
              <SelectContent className="max-h-[200px]">
                <ScrollArea className="h-[200px]">
                  {transpilerPasses.map((pass) => (
                    <SelectItem key={pass.name} value={pass.name} className="text-xs">
                      {pass.name}
                    </SelectItem>
                  ))}
                </ScrollArea>
              </SelectContent>
            </Select>
            <button
              className="text-[#666] hover:text-[#333]"
              onClick={() => setShowDescription(!showDescription)}
              title="Toggle description"
            >
              <Info size={16} />
            </button>
          </div>

          {showDescription && (
            <div className="bg-white p-3 border-b border-[#e0e0e0] text-xs text-[#333]">{description}</div>
          )}
        </div>
      </div>
      <Handle 
        type="target" 
        position={Position.Top} 
        isConnectable={isConnectable} 
        style={{ 
          backgroundColor: 'white', 
          border: '1px solid #893FFC', 
          borderRadius: '50%', 
          width: '16px', 
          height: '16px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          top: '-20px'
        }}
      >
        <div style={{ backgroundColor: '#893FFC', borderRadius: '50%', width: '6px', height: '6px' }} />
      </Handle>
      <Handle 
        type="source" 
        position={Position.Bottom} 
        isConnectable={isConnectable} 
        style={{ 
          backgroundColor: 'white', 
          border: '1px solid #893FFC', 
          borderRadius: '50%', 
          width: '16px', 
          height: '16px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          bottom: '-20px'
        }}
      >
        <div style={{ backgroundColor: '#893FFC', borderRadius: '50%', width: '6px', height: '6px' }} />
      </Handle>
    </Card>
  )
})

TranspilerPassNode.displayName = "TranspilerPassNode"
