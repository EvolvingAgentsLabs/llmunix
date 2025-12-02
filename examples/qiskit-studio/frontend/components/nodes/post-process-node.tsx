/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

"use client"

import { memo, useState } from "react"
import { Handle, Position, type NodeProps } from "reactflow"
import { Card } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Info, Maximize2, Wand2, Loader2 } from "lucide-react"
import { Spinner } from "@/components/ui/spinner"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

interface PostProcessNodeData {
  label: string
  category: string
  inputValue?: string
  placeholder?: string
  details?: string
  pythonCode?: string
  inputCode?: string
  onInputChange?: (nodeId: string, newInput: string) => void
  isUpdating?: boolean
}

export const PostProcessNode = memo(({ id, data, isConnectable }: NodeProps<PostProcessNodeData>) => {
  const getDefaultInputValue = () => {
    // Check if this is the SQD post-process node (by label or ID)
    if (data.label === "SQD Post-process" || id === "sqd-postprocess") {
      // Return SQD Analysis code from chemistry-SQD.py
      return `from qiskit_addon_sqd.counts import counts_to_arrays

# Convert counts into bitstring and probability arrays
bitstring_matrix_full, probs_arr_full = counts_to_arrays(counts)

import numpy as np
from qiskit_addon_sqd.configuration_recovery import recover_configurations
from qiskit_addon_sqd.fermion import solve_fermion
from qiskit_addon_sqd.subsampling import postselect_and_subsample

rng = np.random.default_rng(12345)

# SQD options
iterations = 5

# Eigenstate solver options
n_batches = 3
samples_per_batch = 1000

# Self-consistent configuration recovery loop
e_hist = np.zeros((iterations, n_batches))  # energy history
s_hist = np.zeros((iterations, n_batches))  # spin history
occupancy_hist = []
avg_occupancy = None
for i in range(iterations):
    print(f"Starting configuration recovery iteration {i}")
    # On the first iteration, we have no orbital occupancy information from the
    # solver, so we just post-select from the full bitstring set based on hamming weight.
    if avg_occupancy is None:
        bs_mat_tmp = bitstring_matrix_full
        probs_arr_tmp = probs_arr_full

    # If we have average orbital occupancy information, we use it to refine the full set of noisy configurations
    else:
        bs_mat_tmp, probs_arr_tmp = recover_configurations(
            bitstring_matrix_full,
            probs_arr_full,
            avg_occupancy,
            num_elec_a,
            num_elec_b,
            rand_seed=rng,
        )

    # Throw out configurations with incorrect particle number in either the spin-up or spin-down systems
    batches = postselect_and_subsample(
        bs_mat_tmp,
        probs_arr_tmp,
        hamming_right=num_elec_a,
        hamming_left=num_elec_b,
        samples_per_batch=samples_per_batch,
        num_batches=n_batches,
        rand_seed=rng,
    )

    # Run eigenstate solvers in a loop. This loop should be parallelized for larger problems.
    e_tmp = np.zeros(n_batches)
    s_tmp = np.zeros(n_batches)
    occs_tmp = []
    coeffs = []
    for j in range(n_batches):
        energy_sci, coeffs_sci, avg_occs, spin = solve_fermion(
            batches[j],
            hcore,
            eri,
            open_shell=open_shell,
            spin_sq=spin_sq,
        )
        energy_sci += nuclear_repulsion_energy
        e_tmp[j] = energy_sci
        s_tmp[j] = spin
        occs_tmp.append(avg_occs)
        coeffs.append(coeffs_sci)

    # Combine batch results
    avg_occupancy = np.mean(occs_tmp, axis=0)

    # Track optimization history
    e_hist[i, :] = e_tmp
    s_hist[i, :] = s_tmp
    occupancy_hist.append(avg_occupancy)`
    }
    return `# Post-processing code here\n# 'results' variable is available\nprint(results)`
  }

  const [inputValue, setInputValue] = useState(
    data.inputCode || 
    data.inputValue || 
    getDefaultInputValue()
  )
  const [isInfoOpen, setIsInfoOpen] = useState(false)
  const [isMaximized, setIsMaximized] = useState(false)
  const [maximizedValue, setMaximizedValue] = useState(inputValue)
  const [isLoading, setIsLoading] = useState(false)

  const handleUpdateWithAI = async () => {
    if (!data.pythonCode) {
      console.error("No pythonCode context to send to AI.")
      return
    }
    setIsLoading(true)

    const prompt = `You are an expert Python programmer.\nGiven the following Python code snippet that is part of a larger data processing program:\n\n\npython\n${data.pythonCode}\n\n\n\n\nThe user has provided the following input for the section between '#### INPUT PYTHON' and '#### END INPUT PYTHON' for post-processing:\n\n\npython\n${inputValue}\n\n\n\n\nYour task is to analyze the user's input and the surrounding code, and then generate a corrected, completed, or improved version of the code for the INPUT section. The 'results' variable is available in this context.\n\n**IMPORTANT**: Respond with ONLY the Python code for the input section. Do not include the \n\n\npython markdown, explanations, or any other text.\n`;

    try {
      const payload = {
        input_value: prompt,
        output_type: "chat",
        input_type: "chat",
        session_id: `node-update-${id}`,
        prompt: prompt,
      }

      const response = await fetch(process.env.NEXT_PUBLIC_API_URL!, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
      
      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`)
      }
      
      const result = await response.json()

      let newCode = ""
      if (result.response) { // Handle maestro api response
        const response_json = JSON.parse(result.response)
        newCode = response_json['final_prompt']
      } else if (result.output) {
        newCode = result.output
      } else {
        throw new Error("Could not parse AI response.")
      }

      const cleanedCode = newCode.replace(/\\`\\`\\`python/g, "").replace(/\\`\\`\\`/g, "").trim()

      setInputValue(cleanedCode)
      data.onInputChange?.(id || "", cleanedCode)
    } catch (error) {
      console.error("Error updating code with AI:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (value: string) => {
    setInputValue(value)
    data.onInputChange?.(id || '', value)
  }

  const handleMaximizedChange = (value: string) => {
    setMaximizedValue(value)
  }

  const handleMaximizedSave = () => {
    setInputValue(maximizedValue)
    data.onInputChange?.(id || '', maximizedValue)
    setIsMaximized(false)
  }

  const handleMaximizedCancel = () => {
    setMaximizedValue(inputValue)
    setIsMaximized(false)
  }

  const getUpdatedPythonCode = () => {
    if (!data.pythonCode || !inputValue.trim()) {
      return data.pythonCode || ''
    }
    
    const inputSectionRegex = /(#{4,6}\\s*INPUT PYTHON[\\s\\S]*?)(#{4,6}\\s*END INPUT PYTHON)/g
    return data.pythonCode.replace(inputSectionRegex, (_, start, end) => {
      return start.split('\\n')[0] + '\\n' + inputValue.trim() + '\\n' + end
    })
  }

  return (
    <>
      <Handle 
        type="target" 
        position={Position.Top} 
        isConnectable={isConnectable} 
        style={{ 
          backgroundColor: 'white', 
          border: '1px solid #1A8038', 
          borderRadius: '50%', 
          width: '16px', 
          height: '16px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          top: '-20px'
        }}
      >
        <div style={{ backgroundColor: '#1A8038', borderRadius: '50%', width: '6px', height: '6px' }} />
      </Handle>
      <Card className="w-64 border-0 shadow-md rounded-none overflow-hidden">
        <div className="bg-[#DDFBE5] h-12 flex items-center">
          <div className="w-12 h-12 bg-[#1A8038] flex items-center justify-center text-white mr-2">
            <img src="/node_icons/post-process.svg" alt="Post Process" width="24" height="24" className="filter brightness-0 invert" />
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
                  className="h-6 w-6 p-0 text-[#1A8038] hover:bg-[#1A8038]/10 mr-2"
                >
                  <Info className="h-4 w-4" />
                </Button>
              </DialogTrigger>
              <DialogContent className="overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>{data.label} - Python Code</DialogTitle>
                </DialogHeader>
                <div className="mt-4">
                  <pre className="bg-gray-900 text-white p-4 rounded-md text-xs overflow-x-auto">
                    <code>{getUpdatedPythonCode()}</code>
                  </pre>
                </div>
              </DialogContent>
            </Dialog>
          )}
        </div>
        <div className="bg-white">
          <div className="bg-white p-3 border-b border-[#e0e0e0]">
            <div className="text-xs text-[#666] mb-2">{data.category}</div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-medium text-[#333]">
                Python Code:
              </label>
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-5 w-5 p-0 text-[#1A8038] hover:bg-[#1A8038]/10"
                  onClick={handleUpdateWithAI}
                  title="Generate with AI"
                  disabled={isLoading}
                >
                  {isLoading ? <Loader2 className="h-3 w-3 animate-spin" /> : <Wand2 className="h-3 w-3" />}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-5 w-5 p-0 text-[#1A8038] hover:bg-[#1A8038]/10"
                  onClick={() => {
                    setMaximizedValue(inputValue)
                    setIsMaximized(true)
                  }}
                  title="Maximize editor"
                >
                  <Maximize2 className="h-3 w-3" />
                </Button>
              </div>
            </div>
            <Textarea
              value={inputValue}
              onChange={(e) => handleInputChange(e.target.value)}
              placeholder={data.placeholder || "Enter Python code..."}
              className="min-h-32 max-h-64 text-[10px] font-mono border border-[#ddd] rounded-sm resize-none focus:ring-1 focus:ring-[#1A8038] focus:border-[#1A8038] overflow-y-auto"
            />
            {data.details && (
              <div className="text-xs text-[#888] mt-2">{data.details}</div>
            )}
          </div>
        </div>

        {/* Maximized Editor Modal */}
        <Dialog open={isMaximized} onOpenChange={setIsMaximized}>
          <DialogContent className="sm:max-w-[80vw] max-h-[80vh] overflow-hidden flex flex-col">
            <DialogHeader>
              <DialogTitle>{data.label} - Python Editor</DialogTitle>
            </DialogHeader>
            <div className="flex-1 flex flex-col min-h-0">
              <Textarea
                value={maximizedValue}
                onChange={(e) => handleMaximizedChange(e.target.value)}
                placeholder={data.placeholder || "Enter Python code..."}
                className="flex-1 text-xs font-mono bg-gray-900 text-white border border-[#ddd] rounded-sm resize-none focus:ring-1 focus:ring-[#1A8038] focus:border-[#1A8038] min-h-[400px]"
              />
            </div>
            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={handleMaximizedCancel} className="bg-[#303030] hover:bg-[#303030]/90 text-white border-[#303030] rounded-none">
                Cancel
              </Button>
              <Button onClick={handleMaximizedSave} className="bg-[#1161FE] hover:bg-[#1161FE]/90 text-white rounded-none">
                Save Changes
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </Card>
      <Handle 
        type="source" 
        position={Position.Bottom} 
        isConnectable={isConnectable} 
        style={{ 
          backgroundColor: 'white', 
          border: '1px solid #1A8038', 
          borderRadius: '50%', 
          width: '16px', 
          height: '16px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          bottom: '-20px'
        }}
      >
        <div style={{ backgroundColor: '#1A8038', borderRadius: '50%', width: '6px', height: '6px' }} />
      </Handle>
    </>
  )
})

PostProcessNode.displayName = "PostProcessNode"
