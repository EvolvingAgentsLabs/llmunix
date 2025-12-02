/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

"use client"

import { useState, useEffect } from "react"
import { Handle, Position, type NodeProps } from "reactflow"
import { Card } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ChevronDown, ChevronUp, Info } from "lucide-react"
import { Spinner } from "@/components/ui/spinner"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

interface RuntimeNodeData {
  label: string
  category: string
  loopCount?: number
  pythonCode?: string
  inputCode?: string
  onInputChange?: (nodeId: string, newInput: string) => void
  onParameterChange?: (nodeId: string, parameterName: string, newValue: any) => void
  isUpdating?: boolean
}

export const RuntimeNode = ({ id, data, isConnectable }: NodeProps<RuntimeNodeData>) => {

  const [options, setOptions] = useState({
    resilience_level: 1,
    custom_error_settings: {
      trex: true,  // Level 1+
      zne: false,  // Level 2+
      pec: false,  // Custom only
      pea: false,  // Custom only
      dynamical_decoupling: false,  // Custom only
      gate_twirling: false,  // Level 2+
      m3: false,
      gate_folding: false,
    },
  });
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [isInfoOpen, setIsInfoOpen] = useState(false);
  const [shotsValue, setShotsValue] = useState(10);

  const handleShotsChange = (newShots: number) => {
    const shotsString = `shots = ${newShots}`;
    data.onInputChange?.(id || '', shotsString);
  };

  useEffect(() => {
    // Track python code changes
  }, [data.pythonCode, id, data.label, data]);

  const sendResilienceConfig = (newOptions: typeof options) => {
    const resilienceConfig = {
      resilience_level: newOptions.resilience_level,
      trex: newOptions.custom_error_settings.trex,
      zne: newOptions.custom_error_settings.zne,
      pec: newOptions.custom_error_settings.pec,
      pea: newOptions.custom_error_settings.pea,
      dynamical_decoupling: newOptions.custom_error_settings.dynamical_decoupling,
      gate_twirling: newOptions.custom_error_settings.gate_twirling,
      m3: newOptions.custom_error_settings.m3,
      gate_folding: newOptions.custom_error_settings.gate_folding
    };
    data.onParameterChange?.(id || '', 'resilience_config', resilienceConfig);
  };

  const handleResilienceChange = (value: number[]) => {
    const level = value[0];
    
    const newOptions = {
      resilience_level: level,
      custom_error_settings: {
        trex: level >= 1,
        measurement_mitigation: level >= 1,
        zne: level >= 2,
        gate_twirling: level >= 2,
        pec: false,
        pea: false,
        dynamical_decoupling: false,
      }
    };
    setOptions(newOptions);

    const optionsString = `options = {
    "resilience_level": ${newOptions.resilience_level},
    "optimization_level": 3,
    "dynamical_decoupling": {
        "enable": ${newOptions.custom_error_settings.dynamical_decoupling},
        "sequence_type": "XY4pm",
        "extra_slack_distribution": "middle",
        "scheduling_method": "alap"
    },
    "resilience": {
        "measure_mitigation": ${newOptions.custom_error_settings.measurement_mitigation},
        "zne_mitigation": ${newOptions.custom_error_settings.zne},
        "pec_mitigation": ${newOptions.custom_error_settings.pec}
    },
    "execution": {
        "init_qubits": True,
        "rep_delay": 250e-6
    },
    "experimental": {
        "custom_backend": None
    }
}`;

    try {
      data.onInputChange?.(id || '', optionsString);
    } catch (error) {
      console.error('Error calling onInputChange', error);
    }
  };

  const handleResilienceCommit = (value: number[]) => {
    const level = value[0];
    
    const newOptions = {
      resilience_level: level,
      custom_error_settings: {
        trex: level >= 1,
        measurement_mitigation: level >= 1,
        zne: level >= 2,
        gate_twirling: level >= 2,
        pec: false,
        pea: false,
        dynamical_decoupling: false,
      }
    };

    try {
      sendResilienceConfig(newOptions);
    } catch (error) {
      console.error('Error calling sendResilienceConfig', error);
    }
  };

  return (
    <Card className="w-64 border-0 shadow-md rounded-none overflow-hidden">
      <div className="bg-[#E4EDF7] h-12 flex items-center">
        <div className="w-12 h-12 bg-[#0E62FE] flex items-center justify-center text-white mr-2">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
            <path d="M3 3v5h5" />
            <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
            <path d="M16 16h5v5" />
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
                className="h-7 w-7 p-0 text-[#0E62FE] hover:bg-[#0E62FE]/10 mr-2"
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
            <Select defaultValue={data.category}>
              <SelectTrigger className="h-8 text-sm rounded-none bg-transparent border-0 border-b border-[#ccc] p-0 pb-1 text-[#666] font-normal focus:ring-0">
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Estimator">Estimator</SelectItem>
                <SelectItem value="Sampler">Sampler</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {data.category === "Estimator" && (
            <div className="bg-white p-3 border-b border-[#e0e0e0]">
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#333] font-medium">Loop</span>
                <div className="flex items-center justify-end">
                  <Input
                    type="number"
                    value={data.loopCount || 10}
                    onChange={(e) => {
                      const newValue = parseInt(e.target.value, 10) || 1;
                      data.onParameterChange?.(id || '', 'loopCount', newValue);
                    }}
                    className="w-20 h-7 border-0 border-b border-[#999] rounded-none bg-transparent text-black font-medium focus:ring-0 focus:border-black focus:outline-none mr-2 text-right [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none [-moz-appearance:textfield]"
                    min={1}
                    max={100}
                  />
                  <div className="flex items-center">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 rounded-none border-0 bg-transparent hover:bg-gray-100 text-[#333] font-medium"
                      onClick={() => {
                        const currentCount = data.loopCount || 10;
                        const newCount = Math.max(1, currentCount - 1);
                        data.onParameterChange?.(id || '', 'loopCount', newCount);
                      }}
                    >
                      −
                    </Button>
                    <span className="mx-1 text-[#ccc]">|</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 rounded-none border-0 bg-transparent hover:bg-gray-100 text-[#333] font-medium"
                      onClick={() => {
                        const currentCount = data.loopCount || 10;
                        const newCount = Math.min(100, currentCount + 1);
                        data.onParameterChange?.(id || '', 'loopCount', newCount);
                      }}
                    >
                      +
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Resilience Level - Conditionally visible */}
          {data.category === "Estimator" && (
            <div className="bg-white p-3 border-b border-[#e0e0e0]">
              <div className="flex flex-col">
                <span className="text-sm text-[#333] font-medium mb-2">Resilience Level</span>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-[#333]">0</span>
                  <Slider 
                    value={[options.resilience_level]} 
                    onValueChange={handleResilienceChange}
                    onValueCommit={handleResilienceCommit}
                    min={0}
                    max={2} 
                    step={1} 
                    className="w-24 mx-2" 
                  />
                  <span className="text-xs text-[#333]">2</span>
                </div>
                <div className="mt-1 text-xs text-[#666] flex items-center justify-between">
                  <span>
                    {options.resilience_level === 0 && "No mitigation"}
                    {options.resilience_level === 1 && "TREX (Default)"}
                    {options.resilience_level === 2 && "TREX + ZNE + Gate Twirling"}
                  </span>
                  {data.isUpdating && (
                    <span className="text-[#ff6b35] text-xs flex items-center">
                      <Spinner size={8} className="mr-1 text-[#ff6b35]" />
                      Updating...
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}

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

          {/* Error Mitigation Settings (Advanced) - Conditionally rendered */}
          {showAdvanced && (
            <>
              {/* # shots */}
              <div className="bg-white p-3 border-b border-[#e0e0e0]">
                <div className="flex items-center justify-between">
                  <Label className="text-sm text-[#333] font-medium">
                    # shots
                  </Label>
                  <div className="flex items-center justify-end">
                    <Input
                      type="number"
                      value={shotsValue}
                      onChange={(e) => {
                        const newValue = parseInt(e.target.value, 10) || 1;
                        setShotsValue(newValue);
                        handleShotsChange(newValue);
                      }}
                      className="w-20 h-7 border-0 border-b border-[#999] rounded-none bg-transparent text-black font-medium focus:ring-0 focus:border-black focus:outline-none mr-2 text-right [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none [-moz-appearance:textfield]"
                      min={1}
                      max={10000}
                    />
                    <div className="flex items-center">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 w-7 p-0 rounded-none border-0 bg-transparent hover:bg-gray-100 text-[#333] font-medium"
                        onClick={() => {
                          const newShots = Math.max(1, shotsValue - 1);
                          setShotsValue(newShots);
                          handleShotsChange(newShots);
                        }}
                      >
                        −
                      </Button>
                      <span className="mx-1 text-[#ccc]">|</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 w-7 p-0 rounded-none border-0 bg-transparent hover:bg-gray-100 text-[#333] font-medium"
                        onClick={() => {
                          const newShots = Math.min(10000, shotsValue + 1);
                          setShotsValue(newShots);
                          handleShotsChange(newShots);
                        }}
                      >
                        +
                      </Button>
                    </div>
                  </div>
                </div>
              </div>

              {data.category === "Sampler" && (
                <>
                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <h4 className="font-bold text-sm text-[#333]">Error Suppression</h4>
                  </div>

                  {/* Dynamical Dec. */}
                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <div className="flex items-center justify-between">
                      <Label className="text-sm text-[#333] font-medium">
                        Dynamical Dec.
                      </Label>
                      <button
                        type="button"
                        onClick={() => {
                          const checked = !options.custom_error_settings.dynamical_decoupling;
                          const newOptions = {
                            ...options,
                            custom_error_settings: { ...options.custom_error_settings, dynamical_decoupling: checked }
                          };
                          setOptions(newOptions);
                          sendResilienceConfig(newOptions);
                        }}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-[#1A8038] focus:ring-offset-2 ${
                          options.custom_error_settings.dynamical_decoupling ? 'bg-[#1A8038]' : 'bg-gray-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            options.custom_error_settings.dynamical_decoupling ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                        {options.custom_error_settings.dynamical_decoupling && (
                          <span className="absolute left-1.5 top-1 text-white text-xs">✓</span>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Pauli Twirling */}
                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="gate_twirling" className="text-sm text-[#333] font-medium">
                        Pauli Twirling
                      </Label>
                      <button
                        type="button"
                        onClick={() => {
                          const checked = !options.custom_error_settings.gate_twirling;
                          const newOptions = {
                            ...options,
                            custom_error_settings: { ...options.custom_error_settings, gate_twirling: checked }
                          };
                          setOptions(newOptions);
                          sendResilienceConfig(newOptions);
                        }}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-[#1A8038] focus:ring-offset-2 ${
                          options.custom_error_settings.gate_twirling ? 'bg-[#1A8038]' : 'bg-gray-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            options.custom_error_settings.gate_twirling ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                        {options.custom_error_settings.gate_twirling && (
                          <span className="absolute left-1.5 top-1 text-white text-xs">✓</span>
                        )}
                      </button>
                    </div>
                  </div>

                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <h4 className="font-bold text-sm text-[#333]">Readout Error Mitigation</h4>
                  </div>

                  {/* M3 */}
                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="m3" className="text-sm text-[#333] font-medium">
                        M3
                      </Label>
                      <button
                        type="button"
                        onClick={() => {
                          const checked = !options.custom_error_settings.m3;
                          const newOptions = {
                            ...options,
                            custom_error_settings: { ...options.custom_error_settings, m3: checked }
                          };
                          setOptions(newOptions);
                          sendResilienceConfig(newOptions);
                        }}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-[#1A8038] focus:ring-offset-2 ${
                          options.custom_error_settings.m3 ? 'bg-[#1A8038]' : 'bg-gray-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            options.custom_error_settings.m3 ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                        {options.custom_error_settings.m3 && (
                          <span className="absolute left-1.5 top-1 text-white text-xs">✓</span>
                        )}
                      </button>
                    </div>
                  </div>
                </>
              )}
              {data.category === "Estimator" && (
                <>
                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <h4 className="font-bold text-sm text-[#333]">Error Suppression</h4>
                  </div>

                  {/* Dynamic Decoupling */}
                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="dynamical_decoupling" className="text-sm text-[#333] font-medium">
                        Dynamic Decoupling
                      </Label>
                      <button
                        type="button"
                        onClick={() => {
                          const checked = !options.custom_error_settings.dynamical_decoupling;
                          const newOptions = {
                            ...options,
                            custom_error_settings: { ...options.custom_error_settings, dynamical_decoupling: checked }
                          };
                          setOptions(newOptions);
                          sendResilienceConfig(newOptions);
                        }}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-[#1A8038] focus:ring-offset-2 ${
                          options.custom_error_settings.dynamical_decoupling ? 'bg-[#1A8038]' : 'bg-gray-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            options.custom_error_settings.dynamical_decoupling ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                        {options.custom_error_settings.dynamical_decoupling && (
                          <span className="absolute left-1.5 top-1 text-white text-xs">✓</span>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Pauli Twirling */}
                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="gate_twirling" className="text-sm text-[#333] font-medium">
                        Pauli Twirling
                      </Label>
                      <button
                        type="button"
                        onClick={() => {
                          const checked = !options.custom_error_settings.gate_twirling;
                          const newOptions = {
                            ...options,
                            custom_error_settings: { ...options.custom_error_settings, gate_twirling: checked }
                          };
                          setOptions(newOptions);
                          sendResilienceConfig(newOptions);
                        }}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-[#1A8038] focus:ring-offset-2 ${
                          options.custom_error_settings.gate_twirling ? 'bg-[#1A8038]' : 'bg-gray-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            options.custom_error_settings.gate_twirling ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                        {options.custom_error_settings.gate_twirling && (
                          <span className="absolute left-1.5 top-1 text-white text-xs">✓</span>
                        )}
                      </button>
                    </div>
                  </div>

                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <h4 className="font-bold text-sm text-[#333]">Readout Mitigation</h4>
                  </div>

                  {/* TREX */}
                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="trex" className="text-sm text-[#333] font-medium">
                        TREX
                      </Label>
                      <button
                        type="button"
                        onClick={() => {
                          const checked = !options.custom_error_settings.trex;
                          const newOptions = { 
                            ...options, 
                            custom_error_settings: { ...options.custom_error_settings, trex: checked } 
                          };
                          setOptions(newOptions);
                          sendResilienceConfig(newOptions);
                        }}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-[#1A8038] focus:ring-offset-2 ${
                          options.custom_error_settings.trex ? 'bg-[#1A8038]' : 'bg-gray-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            options.custom_error_settings.trex ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                        {options.custom_error_settings.trex && (
                          <span className="absolute left-1.5 top-1 text-white text-xs">✓</span>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* M3 */}
                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="m3" className="text-sm text-[#333] font-medium">
                        M3
                      </Label>
                      <button
                        type="button"
                        onClick={() => {
                          const checked = !options.custom_error_settings.m3;
                          const newOptions = {
                            ...options,
                            custom_error_settings: { ...options.custom_error_settings, m3: checked }
                          };
                          setOptions(newOptions);
                          sendResilienceConfig(newOptions);
                        }}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-[#1A8038] focus:ring-offset-2 ${
                          options.custom_error_settings.m3 ? 'bg-[#1A8038]' : 'bg-gray-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            options.custom_error_settings.m3 ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                        {options.custom_error_settings.m3 && (
                          <span className="absolute left-1.5 top-1 text-white text-xs">✓</span>
                        )}
                      </button>
                    </div>
                  </div>

                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <h4 className="font-bold text-sm text-[#333]">Error Mitigation</h4>
                  </div>

                  {/* ZNE */}
                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="zne" className="text-sm text-[#333] font-medium">
                        ZNE
                      </Label>
                      <button
                        type="button"
                        onClick={() => {
                          const checked = !options.custom_error_settings.zne;
                          const newOptions = { 
                            ...options, 
                            custom_error_settings: { ...options.custom_error_settings, zne: checked } 
                          };
                          setOptions(newOptions);
                          sendResilienceConfig(newOptions);
                        }}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-[#1A8038] focus:ring-offset-2 ${
                          options.custom_error_settings.zne ? 'bg-[#1A8038]' : 'bg-gray-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            options.custom_error_settings.zne ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                        {options.custom_error_settings.zne && (
                          <span className="absolute left-1.5 top-1 text-white text-xs">✓</span>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Gate Folding */}
                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="gate_folding" className="text-sm text-[#333] font-medium">
                        Gate Folding
                      </Label>
                      <button
                        type="button"
                        onClick={() => {
                          const checked = !options.custom_error_settings.gate_folding;
                          const newOptions = {
                            ...options,
                            custom_error_settings: { ...options.custom_error_settings, gate_folding: checked }
                          };
                          setOptions(newOptions);
                          sendResilienceConfig(newOptions);
                        }}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-[#1A8038] focus:ring-offset-2 ${
                          options.custom_error_settings.gate_folding ? 'bg-[#1A8038]' : 'bg-gray-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            options.custom_error_settings.gate_folding ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                        {options.custom_error_settings.gate_folding && (
                          <span className="absolute left-1.5 top-1 text-white text-xs">✓</span>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* PEA */}
                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="pea" className="text-sm text-[#333] font-medium">
                        PEA
                      </Label>
                      <button
                        type="button"
                        onClick={() => {
                          const checked = !options.custom_error_settings.pea;
                          const newOptions = { 
                            ...options, 
                            custom_error_settings: { ...options.custom_error_settings, pea: checked } 
                          };
                          setOptions(newOptions);
                          sendResilienceConfig(newOptions);
                        }}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-[#1A8038] focus:ring-offset-2 ${
                          options.custom_error_settings.pea ? 'bg-[#1A8038]' : 'bg-gray-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            options.custom_error_settings.pea ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                        {options.custom_error_settings.pea && (
                          <span className="absolute left-1.5 top-1 text-white text-xs">✓</span>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* PEC */}
                  <div className="bg-white p-3 border-b border-[#e0e0e0]">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="pec" className="text-sm text-[#333] font-medium">
                        PEC
                      </Label>
                      <button
                        type="button"
                        onClick={() => {
                          const checked = !options.custom_error_settings.pec;
                          const newOptions = { 
                            ...options, 
                            custom_error_settings: { ...options.custom_error_settings, pec: checked } 
                          };
                          setOptions(newOptions);
                          sendResilienceConfig(newOptions);
                        }}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-[#1A8038] focus:ring-offset-2 ${
                          options.custom_error_settings.pec ? 'bg-[#1A8038]' : 'bg-gray-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            options.custom_error_settings.pec ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                        {options.custom_error_settings.pec && (
                          <span className="absolute left-1.5 top-1 text-white text-xs">✓</span>
                        )}
                      </button>
                    </div>
                  </div>
                </>
              )}


              

              

              

              

              

              

              
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
}