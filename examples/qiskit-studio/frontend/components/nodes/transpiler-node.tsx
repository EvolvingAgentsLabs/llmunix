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
import { ChevronDown, ChevronUp, Info } from "lucide-react"
import { Spinner } from "@/components/ui/spinner"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

interface TranspilerNodeData {
  label: string
  optimizationLevel?: number
  layout?: string
  routing?: string
  translation?: string
  enableScheduling?: boolean
  pythonCode?: string
  inputCode?: string
  onInputChange?: (nodeId: string, newInput: string) => void
  onParameterChange?: (nodeId: string, parameterName: string, newValue: any) => void
  isUpdating?: boolean
}

export const TranspilerNode = memo(({ id, data, isConnectable }: NodeProps<TranspilerNodeData>) => {
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [isInfoOpen, setIsInfoOpen] = useState(false)
  const [options, setOptions] = useState({
    optimizationLevel: data.optimizationLevel || 1,
    layout: data.layout || "sabre",
    routing: data.routing || "stochastic", 
    translation: data.translation || "translator",
    enableScheduling: data.enableScheduling || false,
  })

  const handleOptimizationLevelChange = (value: number[]) => {
    const level = value[0]
    const newOptions = { ...options, optimizationLevel: level }
    setOptions(newOptions)
    
    const optionsString = `transpiler_options = {
    "optimization_level": ${level},
    "layout_method": "${newOptions.layout}",
    "routing_method": "${newOptions.routing}",
    "translation_method": "${newOptions.translation}",
    "scheduling_method": "${newOptions.enableScheduling ? 'asap' : 'none'}",
    "seed_transpiler": 42
}`
    
    data.onInputChange?.(id || '', optionsString)
  }

  const handleOptimizationLevelCommit = (value: number[]) => {
    const level = value[0]
    const newOptions = { ...options, optimizationLevel: level }
    
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
    "scheduling_method": "${newOptions.enableScheduling ? 'asap' : 'none'}",
    "seed_transpiler": 42
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
    "scheduling_method": "${newOptions.enableScheduling ? 'asap' : 'none'}",
    "seed_transpiler": 42
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
    "scheduling_method": "${newOptions.enableScheduling ? 'asap' : 'none'}",
    "seed_transpiler": 42
}`
    
    data.onInputChange?.(id || '', optionsString)
    data.onParameterChange?.(id || '', 'translation_method', value)
  }

  const handleSchedulingChange = (checked: boolean) => {
    const newOptions = { ...options, enableScheduling: checked }
    setOptions(newOptions)
    
    const optionsString = `transpiler_options = {
    "optimization_level": ${newOptions.optimizationLevel},
    "layout_method": "${newOptions.layout}",
    "routing_method": "${newOptions.routing}",
    "translation_method": "${newOptions.translation}",
    "scheduling_method": "${checked ? 'asap' : 'none'}",
    "seed_transpiler": 42
}`
    
    data.onInputChange?.(id || '', optionsString)
    data.onParameterChange?.(id || '', 'scheduling_method', checked ? 'asap' : 'none')
  }

  return (
    <Card className="w-64 border-0 shadow-md rounded-none overflow-hidden">
      <div className="bg-[#F1EDF9] h-12 flex items-center">
        <div className="w-12 h-12 bg-[#893FFC] flex items-center justify-center text-white mr-2">
          <img src="/node_icons/optimize.svg" alt="Optimize" width="24" height="24" className="filter brightness-0 invert" />
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
                className="h-6 w-6 p-0 text-[#893FFC] hover:bg-[#893FFC]/10 mr-2"
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
        <div className="p-0">
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

          {showAdvanced && (
            <>
              <div className="bg-white p-3 border-b border-[#e0e0e0]">
                <span className="text-sm text-[#333] font-medium mb-1 block">Layout Method</span>
                <Select value={options.layout} onValueChange={handleLayoutChange}>
                  <SelectTrigger className="h-8 text-sm rounded-none bg-transparent border-0 border-b border-[#ccc] p-0 pb-1 text-[#333] font-normal focus:ring-0">
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

              <div className="bg-white p-3 border-b border-[#e0e0e0]">
                <span className="text-sm text-[#333] font-medium mb-1 block">Routing Method</span>
                <Select value={options.routing} onValueChange={handleRoutingChange}>
                  <SelectTrigger className="h-8 text-sm rounded-none bg-transparent border-0 border-b border-[#ccc] p-0 pb-1 text-[#333] font-normal focus:ring-0">
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

              <div className="bg-white p-3 border-b border-[#e0e0e0]">
                <span className="text-sm text-[#333] font-medium mb-1 block">Translation Method</span>
                <Select value={options.translation} onValueChange={handleTranslationChange}>
                  <SelectTrigger className="h-8 text-sm rounded-none bg-transparent border-0 border-b border-[#ccc] p-0 pb-1 text-[#333] font-normal focus:ring-0">
                    <SelectValue placeholder="Select translation" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="translator">Translator</SelectItem>
                    <SelectItem value="synthesis">Synthesis</SelectItem>
                    <SelectItem value="unroller">Unroller</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="bg-white p-3 border-b border-[#e0e0e0]">
                <div className="flex items-center justify-between">
                  <Label htmlFor="scheduling" className="text-sm text-[#333] font-medium">
                    Enable Scheduling
                  </Label>
                  <button
                    type="button"
                    onClick={() => handleSchedulingChange(!options.enableScheduling)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-[#1A8038] focus:ring-offset-2 ${
                      options.enableScheduling ? 'bg-[#1A8038]' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        options.enableScheduling ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                    {options.enableScheduling && (
                      <span className="absolute left-1.5 top-1 text-white text-xs">✓</span>
                    )}
                  </button>
                </div>
              </div>
            </>
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

TranspilerNode.displayName = "TranspilerNode"
