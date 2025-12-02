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

interface PythonNodeData {
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

export const PythonNode = memo(({ id, data, isConnectable }: NodeProps<PythonNodeData>) => {
  const [inputValue, setInputValue] = useState(
    data.inputCode || 
    data.inputValue || 
    `graph.add_nodes_from(np.arange(0, n, 1))
edge_list = [
    (0, 1, 1.0),
    (0, 2, 1.0),
    (0, 4, 1.0),
    (1, 2, 1.0),
    (2, 3, 1.0),
    (3, 4, 1.0),
]
graph.add_edges_from(edge_list)`
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

    const prompt = `You are an expert Qiskit programmer.\nGiven the following Python code snippet that is part of a larger Qiskit program:\n\
\
\
python\n${data.pythonCode}\n\
\
\
\n\nThe user has provided the following input for the section between '#### INPUT PYTHON' and '#### END INPUT PYTHON':\n\
\
\
python\n${inputValue}\n\
\
\
\n\nYour task is to analyze the user's input and the surrounding code, and then generate a corrected, completed, or improved version of the code for the INPUT section.\n\n**IMPORTANT**: Respond with ONLY the Python code for the input section. Do not include the \
\
\
python markdown, explanations, or any other text.\n`;

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

      const cleanedCode = newCode.replace(/```python/g, "").replace(/```/g, "").trim()

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
    
    const inputSectionRegex = /(#{4,6}\s*INPUT PYTHON[\s\S]*?)(#{4,6}\s*END INPUT PYTHON)/g
    return data.pythonCode.replace(inputSectionRegex, (_, start, end) => {
      return start.split('\n')[0] + '\n' + inputValue.trim() + '\n' + end
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
      <Card className="w-64 border-0 shadow-md rounded-none overflow-hidden">
        <div className="bg-[#FFEFF7] h-12 flex items-center">
          <div className="w-12 h-12 bg-[#D02771] flex items-center justify-center text-white mr-2">
            <img src="/node_icons/custom-code-snippet.svg" alt="Code" width="24" height="24" className="filter brightness-0 invert" />
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
                  <pre className="bg-gray-100 text-gray-800 p-4 rounded-md text-xs overflow-x-auto">
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
                  className="h-5 w-5 p-0 text-[#D02771] hover:bg-[#D02771]/10"
                  onClick={handleUpdateWithAI}
                  title="Generate with AI"
                  disabled={isLoading}
                >
                  {isLoading ? <Loader2 className="h-3 w-3 animate-spin" /> : <Wand2 className="h-3 w-3" />}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-5 w-5 p-0 text-[#D02771] hover:bg-[#D02771]/10"
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
              className="min-h-32 max-h-64 text-[10px] font-mono border border-[#ddd] rounded-sm resize-none focus:ring-1 focus:ring-[#D02771] focus:border-[#D02771] overflow-y-auto bg-gray-900 text-white"
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
                className="flex-1 text-xs font-mono border border-[#ddd] rounded-sm resize-none focus:ring-1 focus:ring-[#D02771] focus:border-[#D02771] min-h-[400px] bg-gray-900 text-white"
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
    </>
  )
})

PythonNode.displayName = "PythonNode"
