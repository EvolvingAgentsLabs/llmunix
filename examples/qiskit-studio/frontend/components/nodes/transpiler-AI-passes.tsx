/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

"use client"

import { memo, useState } from "react"
import { Handle, Position, type NodeProps } from "reactflow"
import { Card } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { ChevronDown, ChevronUp } from "lucide-react"
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner"

interface TranspilerNodeData {
  label: string;
  optimizationLevel?: number;
  layout?: string;
  routing?: string;
  translation?: string;
  schedulingMethod?: string; // Replaces enableScheduling
  seedTranspiler?: number;  // New
  pythonCode?: string
  inputCode?: string
  onInputChange?: (nodeId: string, newInput: string) => void
  onParameterChange?: (nodeId: string, parameterName: string, newValue: any) => void
  isUpdating?: boolean
}

export const TranspilerNode = memo(({ id, data, isConnectable }: NodeProps<TranspilerNodeData>) => {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [options, setOptions] = useState({
    optimizationLevel: data.optimizationLevel || 1,
    layout: data.layout || "sabre",
    routing: data.routing || "stochastic", 
    translation: data.translation || "translator",
    schedulingMethod: data.schedulingMethod || "none",
    seedTranspiler: data.seedTranspiler || 42,
  });

  const handleOptimizationLevelChange = (value: number[]) => {
    const level = value[0]
    const newOptions = { ...options, optimizationLevel: level }
    setOptions(newOptions)
    
    const optionsString = `transpiler_options = {
    "optimization_level": ${level},
    "layout_method": "${newOptions.layout}",
    "routing_method": "${newOptions.routing}",
    "translation_method": "${newOptions.translation}",
    "scheduling_method": "${newOptions.schedulingMethod}",
    "seed_transpiler": ${newOptions.seedTranspiler}
}`
    
    data.onInputChange?.(id || '', optionsString)
  }

  const handleOptimizationLevelCommit = (value: number[]) => {
    const level = value[0]
    data.onParameterChange?.(id || '', 'optimization_level', level)
  }

  const handleLayoutChange = (value: string) => {
    const newOptions = { ...options, layout: value }
    setOptions(newOptions)
    
    const optionsString = `transpiler_options = {
    "optimization_level": ${newOptions.optimizationLevel},
    "layout_method": "${value}",
    "routing_method": "${newOptions.routing}",
    "translation_method": "${newOptions.translation}",
    "scheduling_method": "${newOptions.schedulingMethod}",
    "seed_transpiler": ${newOptions.seedTranspiler}
}`
    
    data.onInputChange?.(id || '', optionsString)
    data.onParameterChange?.(id || '', 'layout_method', value)
  }

  const handleRoutingChange = (value: string) => {
    const newOptions = { ...options, routing: value }
    setOptions(newOptions)
    
    const optionsString = `transpiler_options = {
    "optimization_level": ${newOptions.optimizationLevel},
    "layout_method": "${newOptions.layout}",
    "routing_method": "${value}",
    "translation_method": "${newOptions.translation}",
    "scheduling_method": "${newOptions.schedulingMethod}",
    "seed_transpiler": ${newOptions.seedTranspiler}
}`
    
    data.onInputChange?.(id || '', optionsString)
    data.onParameterChange?.(id || '', 'routing_method', value)
  }

  const handleTranslationChange = (value: string) => {
    const newOptions = { ...options, translation: value }
    setOptions(newOptions)
    
    const optionsString = `transpiler_options = {
    "optimization_level": ${newOptions.optimizationLevel},
    "layout_method": "${newOptions.layout}",
    "routing_method": "${newOptions.routing}",
    "translation_method": "${value}",
    "scheduling_method": "${newOptions.schedulingMethod}",
    "seed_transpiler": ${newOptions.seedTranspiler}
}`
    
    data.onInputChange?.(id || '', optionsString)
    data.onParameterChange?.(id || '', 'translation_method', value)
  }

  const handleSchedulingChange = (value: string) => {
    const newOptions = { ...options, schedulingMethod: value }
    setOptions(newOptions)
    
    const optionsString = `transpiler_options = {
    "optimization_level": ${newOptions.optimizationLevel},
    "layout_method": "${newOptions.layout}",
    "routing_method": "${newOptions.routing}",
    "translation_method": "${newOptions.translation}",
    "scheduling_method": "${value}",
    "seed_transpiler": ${newOptions.seedTranspiler}
}`
    
    data.onInputChange?.(id || '', optionsString)
    data.onParameterChange?.(id || '', 'scheduling_method', value)
  }

  const handleSeedChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const seedValue = parseInt(e.target.value, 10) || 42
    const newOptions = { ...options, seedTranspiler: seedValue }
    setOptions(newOptions)
    
    const optionsString = `transpiler_options = {
    "optimization_level": ${newOptions.optimizationLevel},
    "layout_method": "${newOptions.layout}",
    "routing_method": "${newOptions.routing}",
    "translation_method": "${newOptions.translation}",
    "scheduling_method": "${newOptions.schedulingMethod}",
    "seed_transpiler": ${seedValue}
}`
    
    data.onInputChange?.(id || '', optionsString)
    data.onParameterChange?.(id || '', 'seed_transpiler', seedValue)
  }

  return (
    <Card className="w-48 border-0 shadow-md rounded-none overflow-hidden">
      <div className="bg-[#F1EDF9] h-12 flex items-center">
        <div className="w-12 h-12 bg-[#893FFC] flex items-center justify-center text-white mr-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M8 3H7a2 2 0 0 0-2 2v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5a2 2 0 0 0 2 2h1" />
            <path d="M16 3h1a2 2 0 0 1 2 2v5a2 2 0 0 0 2 2 2 2 0 0 0-2 2v5a2 2 0 0 1-2 2h-1" />
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
          {/* Optimization Level - Always visible */}
          <div className="bg-white p-3 border-b border-[#e0e0e0]">
            <div className="flex flex-col">
              <span className="text-sm text-[#333] font-medium mb-2">Optimization Level</span>
              <div className="flex items-center justify-between">
                <span className="text-xs text-[#333]">0</span>
                <Slider 
                  value={[options.optimizationLevel]} 
                  onValueChange={handleOptimizationLevelChange}
                  onValueCommit={handleOptimizationLevelCommit}
                  max={3} 
                  step={1} 
                  className="w-24 mx-2" 
                />
                <span className="text-xs text-[#333]">3</span>
              </div>
              {data.isUpdating && (
                <div className="mt-1 text-xs text-[#ff6b35] flex items-center">
                  <Spinner size={8} className="mr-1 text-[#ff6b35]" />
                  Updating...
                </div>
              )}
            </div>
          </div>

          {/* Advanced Options Toggle Button */}
          <div className="bg-white p-2 border-b border-[#e0e0e0]">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="w-full justify-between text-xs text-[#333] font-medium hover:bg-[#e5e5e5] hover:text-[#333] rounded-none"
            >
              <span>Advanced Options</span>
              {showAdvanced ? (
                <ChevronUp className="h-4 w-4 text-[#333]" />
              ) : (
                <ChevronDown className="h-4 w-4 text-[#333]" />
              )}
            </Button>
          </div>

          {/* Advanced Options - Conditionally rendered */}
          {showAdvanced && (
            <>
              {/* Layout Method */}
              <div className="bg-white p-3 border-b border-[#e0e0e0]">
                <span className="text-sm text-[#333] font-medium mb-1 block">Layout Method</span>
                <Select value={options.layout} onValueChange={handleLayoutChange}>
                  <SelectTrigger className="h-8 text-sm rounded-none bg-transparent border-0 p-0 text-[#333] font-normal focus:ring-0">
                    <SelectValue placeholder="Select layout" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="trivial">Trivial</SelectItem>
                    <SelectItem value="dense">Dense</SelectItem>
                    <SelectItem value="sabre">Sabre</SelectItem>
                    <SelectItem value="stochastic">Stochastic</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Routing Method */}
              <div className="bg-white p-3 border-b border-[#e0e0e0]">
                <span className="text-sm text-[#333] font-medium mb-1 block">Routing Method</span>
                <Select value={options.routing} onValueChange={handleRoutingChange}>
                  <SelectTrigger className="h-8 text-sm rounded-none bg-transparent border-0 p-0 text-[#333] font-normal focus:ring-0">
                    <SelectValue placeholder="Select routing" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="basic">Basic</SelectItem>
                    <SelectItem value="stochastic">Stochastic</SelectItem>
                    <SelectItem value="lookahead">Lookahead</SelectItem>
                    <SelectItem value="sabre">Sabre</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Translation Method */}
              <div className="bg-white p-3 border-b border-[#e0e0e0]">
                <span className="text-sm text-[#333] font-medium mb-1 block">Translation Method</span>
                <Select value={options.translation} onValueChange={handleTranslationChange}>
                  <SelectTrigger className="h-8 text-sm rounded-none bg-transparent border-0 p-0 text-[#333] font-normal focus:ring-0">
                    <SelectValue placeholder="Select translation" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="translator">Translator</SelectItem>
                    <SelectItem value="synthesis">Synthesis</SelectItem>
                    <SelectItem value="unroller">Unroller</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Scheduling Method */}
              <div className="bg-white p-3 border-b border-[#e0e0e0]">
                <span className="text-sm text-[#333] font-medium mb-1 block">Scheduling Method</span>
                <Select value={options.schedulingMethod} onValueChange={handleSchedulingChange}>
                  <SelectTrigger className="h-8 text-sm rounded-none bg-transparent border-0 p-0 text-[#333] font-normal focus:ring-0">
                    <SelectValue placeholder="Select scheduling method" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">None</SelectItem>
                    <SelectItem value="asap">ASAP</SelectItem>
                    <SelectItem value="alap">ALAP</SelectItem>
                    <SelectItem value="default">Default</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Seed Transpiler */}
              <div className="bg-white p-3 border-b border-[#e0e0e0]">
                <Label htmlFor="seedTranspiler" className="text-sm text-[#333] font-medium mb-1 block">
                  Seed Transpiler
                </Label>
                <Input
                  id="seedTranspiler"
                  type="number"
                  placeholder="Enter seed (optional)"
                  value={options.seedTranspiler}
                  onChange={handleSeedChange}
                  className="h-8 text-sm rounded-none bg-transparent border p-1 text-[#333] font-normal focus:ring-0"
                />
              </div>
            </>
          )}
        </div>
      </div>
      <Handle type="target" position={Position.Top} isConnectable={isConnectable} className="w-3 h-3 bg-[#893FFC]" />
      <Handle type="source" position={Position.Bottom} isConnectable={isConnectable} className="w-3 h-3 bg-[#893FFC]" />
    </Card>
  )
})

TranspilerNode.displayName = "TranspilerNode"
