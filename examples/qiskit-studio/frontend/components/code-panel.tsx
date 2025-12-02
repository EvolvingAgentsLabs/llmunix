/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { CopyIcon, PlayIcon, ChevronUp, ChevronDown, Send, Loader2, Maximize2, Minimize2, Sliders } from "lucide-react"
import { toast } from "@/components/ui/use-toast"
import { ScrollArea } from "@/components/ui/scroll-area"
import ReactMarkdown from "react-markdown"
import { generateAIChatResponse, generateStreamingChatResponse, runQuantumProgramCode } from "@/lib/api-service"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"

// Token obfuscation utility functions
function obfuscateToken(text: string): string {
  if (!text) return '';
  
  const key = "quantum_computing_rocks"; // Secret key
  let result = '';
  for (let i = 0; i < text.length; i++) {
    const charCode = text.charCodeAt(i) ^ key.charCodeAt(i % key.length);
    result += String.fromCharCode(charCode);
  }
  return btoa(result); // Base64 encode for safe storage
}

// When retrieving the token
function deobfuscateToken(obfuscated: string): string {
  if (!obfuscated) return '';
  
  try {
    const key = "quantum_computing_rocks"; // Same secret key
    const text = atob(obfuscated); // Base64 decode
    let result = '';
    for (let i = 0; i < text.length; i++) {
      const charCode = text.charCodeAt(i) ^ key.charCodeAt(i % key.length);
      result += String.fromCharCode(charCode);
    }
    return result;
  } catch (e) {
    console.error("Error deobfuscating token:", e);
    return '';
  }
}

interface Message {
  role: "user" | "assistant"
  content: string
  id?: string
  streaming?: boolean
}

interface CodePanelProps {
  code: string
  selectedNode: string
  onSelectDemo: (demoId: string) => void
  highlightSection?: {
    startLine: number
    endLine: number
    step: number
  } | null
  onBackendConfigChange?: (config: { type: 'specific' | 'auto', backend?: string, apiToken?: string }) => void
  isUpdatingCode?: boolean
  onUpdatePostProcessingNode?: (resultJson: { type: 'text' | 'graph' | 'plot', content: string }) => void
}

export function CodePanel({ code, selectedNode, onSelectDemo, highlightSection, onBackendConfigChange, isUpdatingCode, onUpdatePostProcessingNode }: CodePanelProps) {
  const [expanded, setExpanded] = useState(true)
  const [maximized, setMaximized] = useState(false)
  const [backendConfig, setBackendConfig] = useState<'specific' | 'auto'>('auto')
  const [specificBackend, setSpecificBackend] = useState('')
  const [apiToken, setApiToken] = useState(() => {
    // Initialize from localStorage if available (client-side only)
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem('ibm_quantum_api_token');
      return storedToken ? deobfuscateToken(storedToken) : '';
    }
    return ''
  })
  const [channel, setChannel] = useState(() => {
    return 'ibm_cloud'
  })
  const [instance, setInstance] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('ibm_quantum_instance') || ''
    }
    return ''
  })
  const [region, setRegion] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('ibm_quantum_region') || ''
    }
    return ''
  })
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [outputExpanded, setOutputExpanded] = useState(false)
  const [outputContent, setOutputContent] = useState<string[]>([])
  const [outputHeight, setOutputHeight] = useState(128) // Default 128px (h-32)
  const [isResizing, setIsResizing] = useState(false)
  const [startY, setStartY] = useState(0)
  const [startHeight, setStartHeight] = useState(0)
  const [chatHeight, setChatHeight] = useState(160) // Default 160px (h-40)
  const [isChatResizing, setIsChatResizing] = useState(false)
  const [chatStartY, setChatStartY] = useState(0)
  const [chatStartHeight, setChatStartHeight] = useState(0)
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I can help you with quantum computing. Ask me about circuits or select a demo.",
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [useStreaming] = useState(true) // Always use streaming
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Clear output panel when a new demo/node is selected or code changes
  useEffect(() => {
    setOutputContent([])
    setOutputExpanded(false)
  }, [selectedNode, code])

  // Resize handlers for Output section
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault() // Prevent default text selection
    setIsResizing(true)
    setStartY(e.clientY)
    setStartHeight(outputHeight)
    // Disable text selection immediately
    document.body.style.userSelect = 'none'
    document.body.style.webkitUserSelect = 'none'
    document.body.style.cursor = 'ns-resize'
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isResizing) return
    
    const deltaY = e.clientY - startY
    const newHeight = Math.max(60, Math.min(400, startHeight - deltaY)) // Min 60px, Max 400px - inverted
    setOutputHeight(newHeight)
  }

  const handleMouseUp = () => {
    setIsResizing(false)
    // Re-enable text selection
    document.body.style.userSelect = ''
    document.body.style.webkitUserSelect = ''
    document.body.style.cursor = ''
  }

  // Chat resize handlers
  const handleChatMouseDown = (e: React.MouseEvent) => {
    e.preventDefault()
    setIsChatResizing(true)
    setChatStartY(e.clientY)
    setChatStartHeight(chatHeight)
    // Disable text selection immediately
    document.body.style.userSelect = 'none'
    document.body.style.webkitUserSelect = 'none'
    document.body.style.cursor = 'ns-resize'
  }

  const handleChatMouseMove = (e: MouseEvent) => {
    if (!isChatResizing) return
    
    const deltaY = e.clientY - chatStartY
    const newHeight = Math.max(80, Math.min(400, chatStartHeight - deltaY)) // Min 80px, Max 400px - inverted
    setChatHeight(newHeight)
  }

  const handleChatMouseUp = () => {
    setIsChatResizing(false)
    // Re-enable text selection
    document.body.style.userSelect = ''
    document.body.style.webkitUserSelect = ''
    document.body.style.cursor = ''
  }

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      // Ensure text selection is restored if component unmounts during drag
      document.body.style.userSelect = ''
      document.body.style.webkitUserSelect = ''
      document.body.style.cursor = ''
    }
  }, [isResizing, startY, startHeight, outputHeight])

  useEffect(() => {
    if (isChatResizing) {
      document.addEventListener('mousemove', handleChatMouseMove)
      document.addEventListener('mouseup', handleChatMouseUp)
    }

    return () => {
      document.removeEventListener('mousemove', handleChatMouseMove)
      document.removeEventListener('mouseup', handleChatMouseUp)
      // Ensure text selection is restored if component unmounts during drag
      document.body.style.userSelect = ''
      document.body.style.webkitUserSelect = ''
      document.body.style.cursor = ''
    }
  }, [isChatResizing, chatStartY, chatStartHeight, chatHeight])

  const handleBackendConfigSave = () => {
    const trimmedToken = apiToken.trim()
    const trimmedInstance = instance.trim()
    const trimmedRegion = region.trim()
    
    // Save all IBM Quantum parameters to localStorage for persistence
    if (typeof window !== 'undefined') {
      if (trimmedToken) {
        localStorage.setItem('ibm_quantum_api_token', obfuscateToken(trimmedToken))
        localStorage.setItem('ibm_quantum_channel', channel)
        localStorage.setItem('ibm_quantum_instance', trimmedInstance)
        localStorage.setItem('ibm_quantum_region', trimmedRegion)
      } else {
        localStorage.removeItem('ibm_quantum_api_token')
        localStorage.removeItem('ibm_quantum_channel')
        localStorage.removeItem('ibm_quantum_instance')
        localStorage.removeItem('ibm_quantum_region')
      }
    }
    
    const config = {
      type: backendConfig,
      backend: backendConfig === 'specific' ? specificBackend : undefined,
      apiToken: trimmedToken || undefined,
      channel: channel || undefined,
      instance: trimmedInstance || undefined,
      region: trimmedRegion || undefined
    }
    onBackendConfigChange?.(config)
    setIsDialogOpen(false)
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(code)
    toast({
      title: "Copied to clipboard",
      description: "The Qiskit code has been copied to your clipboard.",
    })
  }

  const runCode = async () => {

    setIsLoading(true)
    setOutputExpanded(true)
    setOutputContent(["Running your Quantum Program..."])
    
    try {
      const requestPayload: any = {
        input_value: code
      }
      
      // Include IBM Quantum configuration if provided
      if (apiToken.trim()) {
        requestPayload.ibm_token = apiToken.trim()
        requestPayload.channel = channel
        if (instance.trim()) {
          requestPayload.instance = instance.trim()
        }
        if (region.trim()) {
          requestPayload.region = region.trim()
        }
        
      } else {
        console.log("🔑 Frontend: No IBM token provided")
      }
      

      // Use environment variable for agent URL or fallback to runQuantumProgramCode
      const agentUrl = process.env.NEXT_PUBLIC_RUNCODE_URL
      
      
      if (agentUrl) {
        
        // Call agent.py service directly
        const response = await fetch(`${agentUrl}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestPayload),
        })
        
        const result = await response.json()

        if (response.ok && result.output) {
          const linesArray = result.output.split('\n');
          const filteredLines = linesArray.filter(line => line.trim() !== '')
          setOutputContent(filteredLines)
          
          // Extract RESULT JSON from output
          const resultLine = filteredLines.find(line => line.includes('RESULT:'))
          
          if (resultLine && onUpdatePostProcessingNode) {
            try {
              const jsonStart = resultLine.indexOf('RESULT:') + 7
              let jsonString = resultLine.substring(jsonStart).trim()
              
              // If the JSON spans multiple lines, try to find the complete JSON
              if (!jsonString.endsWith('}')) {
                const resultIndex = filteredLines.findIndex(line => line.includes('RESULT:'))
                let completeJson = jsonString
                for (let i = resultIndex + 1; i < filteredLines.length; i++) {
                  completeJson += ' ' + filteredLines[i].trim()
                  if (completeJson.endsWith('}')) break
                }
                jsonString = completeJson
              }
              
              const resultJson = JSON.parse(jsonString)
              
              // Validate the JSON structure
              if (resultJson.type && resultJson.content && 
                  ['text', 'graph', 'plot'].includes(resultJson.type)) {
                onUpdatePostProcessingNode(resultJson)
              }
            } catch (jsonError) {
              console.error("Error parsing RESULT JSON:", jsonError)
            }
          }
        } else {
          setOutputContent([result.output || "Sorry, I couldn't process that request."])
        }
      } else {
        // Fallback to original runQuantumProgramCode if no agent URL configured
        console.warn("⚠️ Frontend: NEXT_PUBLIC_RUNCODE_URL not configured, falling back to runQuantumProgramCode")
        console.warn("⚠️ Frontend: IBM Quantum token will be lost in fallback - please configure NEXT_PUBLIC_RUNCODE_URL")
        const response = await runQuantumProgramCode({
          message: code,
          sessionId: "user_1"
        })

        if (response.success && response.message) {
          const linesArray = response.message.split('\n');
          const filteredLines = linesArray.filter(line => line.trim() !== '')
          setOutputContent(filteredLines)
          
          // Extract RESULT JSON from output
          const resultLine = filteredLines.find(line => line.includes('RESULT:'))
          
          if (resultLine && onUpdatePostProcessingNode) {
            try {
              const jsonStart = resultLine.indexOf('RESULT:') + 7
              let jsonString = resultLine.substring(jsonStart).trim()
              
              // If the JSON spans multiple lines, try to find the complete JSON
              if (!jsonString.endsWith('}')) {
                const resultIndex = filteredLines.findIndex(line => line.includes('RESULT:'))
                let completeJson = jsonString
                for (let i = resultIndex + 1; i < filteredLines.length; i++) {
                  completeJson += ' ' + filteredLines[i].trim()
                  if (completeJson.endsWith('}')) break
                }
                jsonString = completeJson
              }
              
              const resultJson = JSON.parse(jsonString)
              
              // Validate the JSON structure
              if (resultJson.type && resultJson.content && 
                  ['text', 'graph', 'plot'].includes(resultJson.type)) {
                onUpdatePostProcessingNode(resultJson)
              }
            } catch (jsonError) {
              console.error("Error parsing RESULT JSON:", jsonError)
            }
          }
        } else {
          setOutputContent([response.error || "Sorry, I couldn't process that request."])
        }
      }
    } catch (error) {
      console.error("Error running code:", error)
      setOutputContent(["Sorry, I encountered an error."])
    } finally {
      setIsLoading(false)
    }
    return
  }

  const highlightPythonSyntax = (line: string) => {
    if (!line) return [];

    const patterns = [
      { pattern: /(#.*$)/, className: 'text-gray-400 italic' },
      { pattern: /(f?"[^"]*"|f?'[^']*')/, className: 'text-yellow-300' },
      { pattern: /(def\s+\w+)/, className: 'text-green-300 font-semibold' },
      { pattern: /\b(def|class|if|elif|else|for|while|try|except|finally|with|as|import|from|return|yield|break|continue|pass|lambda|and|or|not|in|is|None|True|False)\b/, className: 'text-purple-400 font-semibold' },
      { pattern: /\b(print|len|range|enumerate|zip|map|filter|sorted|max|min|sum|abs|round|int|float|str|list|dict|set|tuple|bool|type)\b/, className: 'text-blue-300' },
      { pattern: /\b(\d+\.?\d*|\.\d+)\b/, className: 'text-orange-300' },
    ];

    let segments: Array<{text: string, className?: string}> = [];
    const matches: Array<{match: RegExpMatchArray, className: string}> = [];

    patterns.forEach(({pattern, className}) => {
      let match;
      const regex = new RegExp(pattern.source, pattern.flags + 'g');
      while ((match = regex.exec(line)) !== null) {
        matches.push({match, className});
      }
    });

    matches.sort((a, b) => a.match.index! - b.match.index!);

    const filteredMatches: Array<{match: RegExpMatchArray, className: string}> = [];
    let lastEndIndex = -1;

    matches.forEach(({match, className}) => {
      if (match.index! >= lastEndIndex) {
        filteredMatches.push({match, className});
        lastEndIndex = match.index! + match[0].length;
      }
    });

    let lastIndex = 0;
    filteredMatches.forEach(({match, className}) => {
      if (match.index! > lastIndex) {
        const beforeText = line.slice(lastIndex, match.index!);
        if (beforeText) {
          segments.push({text: beforeText});
        }
      }
      segments.push({text: match[0], className});
      lastIndex = match.index! + match[0].length;
    });

    if (lastIndex < line.length) {
      segments.push({text: line.slice(lastIndex)});
    }

    if (segments.length === 0) {
      segments.push({text: line});
    }

    return segments;
  };

  const renderCodeWithHighlighting = () => {
    const lines = code.split('\n')

    return (
      <pre className="whitespace-pre w-max">
        {lines.map((line, index) => {
          const lineNumber = index + 1
          const isHighlighted = highlightSection &&
            index >= highlightSection.startLine &&
            index <= highlightSection.endLine

          const syntaxSegments = highlightPythonSyntax(line);

          return (
            <div
              key={index}
              className={`whitespace-nowrap ${isHighlighted ? 'bg-blue-600/30' : ''}`}
            >
              <span className="select-none text-gray-500 mr-3 text-[10px]">
                {lineNumber.toString().padStart(3, ' ')}
              </span>
              <span>
                {syntaxSegments.map((segment, segIndex) => (
                  <span
                    key={segIndex}
                    className={segment.className || (isHighlighted ? 'text-blue-100' : 'text-green-400')}
                    style={{ whiteSpace: 'pre' }}
                  >
                    {segment.text}
                  </span>
                ))}
              </span>
            </div>
          )
        })}
      </pre>
    )
  }

  useEffect(() => {
    if (highlightSection) {
      // Wait a bit for the DOM to update with highlighting
      setTimeout(() => {
        const highlightedElements = document.querySelectorAll('[class*="bg-blue-600"]')
        
        if (highlightedElements.length > 0) {
          // Use scrollIntoView with scrolling constrained to nearest scrollable ancestor
          highlightedElements[0].scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center',
            inline: 'nearest'
          })
        }
      }, 100)
    }
  }, [highlightSection])

  // Optimized SSE parser for the specific server format
  const parseSSEData = (chunk: string): string | null => {
    if (!chunk.startsWith('data: ')) return null
    
    const data = chunk.slice(6).trim()
    if (data === '[DONE]') return null
    
    try {
      const parsed = JSON.parse(data)
      
      // Only extract content from the llm_step field, ignore all other steps
      if (parsed.step_name === 'llm_step' && parsed.step_result) {
        return parsed.step_result
      }
      
      // Return null for all other steps to ignore them
      return null
    } catch {
      return data !== '[DONE]' ? data : null
    }
  }

  // Helper functions for cleaner error handling
  const addErrorMessage = (content: string) => {
    setMessages((prev) => [...prev, { role: "assistant", content }])
  }

  const updateStreamingMessage = (messageId: string, content: string, streaming = false) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId
          ? { ...msg, content, streaming }
          : msg
      )
    )
  }

  const handleStreamingRequest = async (input: string) => {
    const messageId = `msg-${Date.now()}`
    const streamingMessage = {
      role: "assistant" as const,
      content: "",
      id: messageId,
      streaming: true
    }
    
    setMessages((prev) => [...prev, streamingMessage])
    setStreamingMessageId(messageId)
    
    const response = await generateStreamingChatResponse({
      message: input,
      sessionId: "user_1"
    })

    if (response.success && response.stream) {
      await handleStreamingResponse(response.stream, messageId)
    } else {
      updateStreamingMessage(messageId, response.error || "Sorry, I couldn't process that request.")
      setStreamingMessageId(null)
      setIsLoading(false)
    }
  }

  const handleNonStreamingRequest = async (input: string) => {
    const response = await generateAIChatResponse({
      message: input,
      sessionId: "user_1"
    })

    const content = response.success && response.message
      ? response.message
      : response.error || "Sorry, I couldn't process that request."
    
    setMessages((prev) => [...prev, { role: "assistant", content }])
    setIsLoading(false)
  }

  const simulateTypingEffect = async (messageId: string, content: string) => {
    const words = content.split(' ')
    let displayedContent = ''
    
    for (let i = 0; i < words.length; i++) {
      displayedContent += (i > 0 ? ' ' : '') + words[i]
      // Remove "Thinking..." indicator once we start showing content
      updateStreamingMessage(messageId, displayedContent, false)
      
      // Much faster delay - only 15-30ms per word
      const delay = Math.min(Math.max(words[i].length * 2, 15), 30)
      await new Promise(resolve => setTimeout(resolve, delay))
    }
    
    // Final update to mark as not streaming
    updateStreamingMessage(messageId, content, false)
  }

  const handleStreamingResponse = async (stream: ReadableStream<Uint8Array>, messageId: string) => {
    const reader = stream.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let hasStartedStreaming = false
    
    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value, { stream: true })
        buffer += chunk
        
        // Process complete lines immediately as they arrive
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // Keep incomplete line in buffer
        
        for (const line of lines) {
          if (line.trim()) {
            const content = parseSSEData(line)
            if (content && !hasStartedStreaming) {
              // Start streaming effect immediately when first content arrives
              hasStartedStreaming = true
              await simulateTypingEffect(messageId, content)
              return // Exit after processing the content
            }
          }
        }
      }
      
      // Handle remaining buffer if no content was streamed yet
      if (buffer.trim() && !hasStartedStreaming) {
        const content = parseSSEData(buffer)
        if (content) {
          await simulateTypingEffect(messageId, content)
        } else {
          updateStreamingMessage(messageId, 'No content received', false)
        }
      }
    } catch (error) {
      console.error('Streaming error:', error)
      updateStreamingMessage(messageId, 'Error processing streaming response', false)
    } finally {
      setStreamingMessageId(null)
      setIsLoading(false)
    }
  }

  const handleSendMessage = async () => {
    if (!input.trim()) return

    const userMessage = { role: "user" as const, content: input }
    const currentInput = input
    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    const demoMappings = [
      { keywords: ["chemistry", "molecule"], demo: "chemistry-simulation" },
      { keywords: ["max cut", "graph"], demo: "max-cut" },
      { keywords: ["risk", "finance"], demo: "risk-analysis" }
    ]

    for (const { keywords, demo } of demoMappings) {
      if (keywords.some(keyword => currentInput.toLowerCase().includes(keyword))) {
        setTimeout(() => {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: `Loading the ${demo.replace('-', ' ')} demo for you...`,
            },
          ])
          onSelectDemo(demo)
          setIsLoading(false)
        }, 500)
        return
      }
    }

    try {
      if (useStreaming) {
        await handleStreamingRequest(currentInput)
      } else {
        await handleNonStreamingRequest(currentInput)
      }
    } catch (error) {
      console.error("Error calling chatbot API:", error)
      addErrorMessage("Sorry, I encountered an error. You can try asking about quantum computing or selecting a demo.")
      setIsLoading(false)
      setStreamingMessageId(null)
    }
  }

  const customComponents = {
    pre: ({ children }) => (
      <pre className="whitespace-pre-wrap">
        {children}
      </pre>
    ),
  };

  return (
    <div
      className={`${
        maximized
          ? "w-[40vw]"
          : expanded
            ? "w-[422px]"
            : "w-10"
      } border-l bg-[#1e1e1e] transition-all duration-300 flex flex-col`}
    >
      {expanded ? (
        <>
          {/* Code Panel Header */}
          <div className="flex justify-between items-center px-4 py-2 bg-[#171717] text-white border-b border-[#333]">
            <div className="flex items-center">
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 text-white hover:bg-zinc-800 rounded-none"
                onClick={() => setExpanded(false)}
              >
                <ChevronDown className="h-4 w-4" />
              </Button>
              <span className="text-sm font-medium ml-2 flex items-center">
                Code
                {highlightSection && (
                  <span className="ml-2 bg-yellow-600 text-black px-2 py-1 rounded text-xs">
                    STEP {highlightSection.step}
                  </span>
                )}
                {isUpdatingCode && (
                  <span className="ml-2 text-yellow-400 text-xs flex items-center">
                    <span className="inline-block w-3 h-3 border border-yellow-400 border-t-transparent rounded-full animate-spin mr-1"></span>
                    Updating...
                  </span>
                )}
              </span>
            </div>
            <div className="flex gap-2">
              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 text-white hover:bg-zinc-800 rounded-none"
                    title="Backend Preferences"
                  >
                    <Sliders className="h-4 w-4" />
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[425px]">
                  <DialogHeader>
                    <DialogTitle>IBM Quantum Backend Configuration</DialogTitle>
                  </DialogHeader>
                  <div className="grid gap-4 py-4">
                    <RadioGroup value={backendConfig} onValueChange={(value: 'specific' | 'auto') => setBackendConfig(value)}>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="auto" id="auto" />
                        <Label htmlFor="auto">Choose less busy backend</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="specific" id="specific" />
                        <Label htmlFor="specific">Specify backend name</Label>
                      </div>
                    </RadioGroup>

                    {backendConfig === 'specific' && (
                      <div className="grid gap-2">
                        <Label htmlFor="backend-name">Backend Name</Label>
                        <input
                          id="backend-name"
                          value={specificBackend}
                          onChange={(e) => setSpecificBackend(e.target.value)}
                          placeholder="e.g., ibm_brisbane"
                          className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                        />
                      </div>
                    )}

                    <div className="grid gap-2">
                      <Label htmlFor="api-token">IBM Quantum API Token</Label>
                      <input
                        id="api-token"
                        type="password"
                        value={apiToken}
                        onChange={(e) => {
                          setApiToken(e.target.value)
                        }}
                        placeholder="Enter your IBM Quantum API token"
                        className="px-3 py-2 border border-gray-300 rounded-md text-sm text-white"
                        style={{ 
                          backgroundColor: '#2a2a2a',
                          borderColor: '#4a4a4a',
                          color: 'white'
                        }}
                      />
                      <p className="text-xs text-gray-500">
                        Get your API token from the{' '}
                        <a 
                          href="https://quantum.ibm.com/account" 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          IBM Quantum Platform
                        </a>
                      </p>
                    </div>

                    <div className="grid gap-2">
                      <Label htmlFor="instance">Instance (CRN) - Optional</Label>
                      <input
                        id="instance"
                        value={instance}
                        onChange={(e) => setInstance(e.target.value)}
                        placeholder="crn:v1:bluemix:public:quantum-computing:us-east:a/..."
                        className="px-3 py-2 border border-gray-300 rounded-md text-sm text-white"
                        style={{ 
                          backgroundColor: '#2a2a2a',
                          borderColor: '#4a4a4a',
                          color: 'white'
                        }}
                      />
                      <p className="text-xs text-gray-500">
                        Cloud Resource Name for IBM Cloud accounts. Leave empty for IBM Quantum Platform.
                      </p>
                    </div>

                    <div className="grid gap-2">
                      <Label htmlFor="region">Region - Optional</Label>
                      <select
                        id="region"
                        value={region}
                        onChange={(e) => setRegion(e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-md text-sm text-white"
                        style={{ 
                          backgroundColor: '#2a2a2a',
                          borderColor: '#4a4a4a',
                          color: 'white'
                        }}
                      >
                        <option value="">Auto (no preference)</option>
                        <option value="us-east">US East</option>
                        <option value="eu-de">Europe (Germany)</option>
                      </select>
                      <p className="text-xs text-gray-500">
                        Region preference for backend selection
                      </p>
                    </div>
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button variant="outline" onClick={() => setIsDialogOpen(false)} className="bg-[#303030] hover:bg-[#303030]/90 text-white border-[#303030] rounded-none">
                      Cancel
                    </Button>
                    <Button onClick={handleBackendConfigSave} className="bg-[#1161FE] hover:bg-[#1161FE]/90 text-white rounded-none">
                      Apply Configuration
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 text-white hover:bg-zinc-800 rounded-none"
                onClick={() => setMaximized(!maximized)}
                title={maximized ? "Restore size" : "Maximize"}
              >
                {maximized ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 text-white hover:bg-zinc-800 rounded-none"
                onClick={copyToClipboard}
              >
                <CopyIcon className="h-4 w-4" />
              </Button>
              <Button
                variant="default"
                size="sm"
                className="bg-[#0d6efd] hover:bg-[#0b5ed7] h-6 px-3 text-xs rounded-none"
                onClick={runCode}
              >
                Run
                <PlayIcon className="ml-1 h-3 w-3" />
              </Button>
            </div>
          </div>

          {/* Code Content */}
          <div className="flex-grow overflow-x-auto overflow-y-auto relative">
            {isUpdatingCode && (
              <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-10">
                <div className="text-white text-center">
                  <div className="inline-block w-8 h-8 border-4 border-white border-t-transparent rounded-full animate-spin mb-2"></div>
                  <div className="text-sm">Updating code with AI...</div>
                </div>
              </div>
            )}
            <div className="p-4 text-green-400 font-mono text-[10px] min-w-max">
              {renderCodeWithHighlighting()}
            </div>
          </div>

          {/* Output Section */}
          <div className="border-t border-[#333] bg-[#212729]">
            {/* Output Header */}
            <div 
              className="bg-[#171717] text-white px-3 py-2 flex justify-between items-center cursor-ns-resize select-none"
              onMouseDown={handleMouseDown}
              title="Drag to resize output panel"
            >
              <h3 className="text-xs font-medium pointer-events-none">Output</h3>
              <Button
                variant="ghost"
                size="icon"
                className="h-4 w-4 text-white hover:bg-zinc-800 rounded-none pointer-events-auto"
                onClick={() => setOutputExpanded(!outputExpanded)}
              >
                {outputExpanded ? <ChevronDown className="h-3 w-3" /> : <ChevronUp className="h-3 w-3" />}
              </Button>
            </div>

            {/* Output Content */}
            {outputExpanded && (
              <ScrollArea 
                className="p-2 bg-[#212729]"
                style={{ height: `${outputHeight}px` }}
              >
                <div className="space-y-1">
                  {outputContent.map((line, index) => (
                    <div key={index} className="text-xs text-green-400 font-mono whitespace-pre-wrap">
                      {line}
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex items-center text-yellow-400 text-xs">
                      <Loader2 className="h-3 w-3 animate-spin mr-2" />
                      <span>Executing...</span>
                    </div>
                  )}
                </div>
              </ScrollArea>
            )}

          </div>

          {/* Chat Section */}
          <div className="border-t border-[#333] bg-[#212729]">
            {/* Chat Header */}
            <div 
              className="bg-[#171717] text-white px-3 py-2 flex justify-between items-center cursor-ns-resize select-none"
              onMouseDown={handleChatMouseDown}
              title="Drag to resize chat panel"
            >
              <h3 className="text-xs font-medium pointer-events-none">Qiskit Assistant</h3>
            </div>

            {/* Chat Messages */}
            <ScrollArea 
              className="p-2 bg-[#212729]"
              style={{ height: `${chatHeight}px` }}
            >
              <div className="space-y-2">
                {messages.map((message, index) => (
                  <div key={index} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div
                      className={`max-w-[80%] rounded px-2 py-1 text-xs ${
                        message.role === "user" ? "bg-[#2563EB] text-white" : "bg-[#333] text-[#eee]"
                      }`}
                    >
                      {message.role === "user" ? (
                        <p>{message.content}</p>
                      ) : (
                        <div className="markdown-content prose prose-sm prose-invert max-w-none">
                          <ReactMarkdown components={customComponents}>{message.content}</ReactMarkdown>
                          {message.streaming && (
                            <div className="flex items-center mt-1 text-gray-400">
                              <div className="inline-block w-2 h-2 bg-blue-400 rounded-full animate-pulse mr-1"></div>
                              <span className="text-xs">Thinking...</span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>

            {/* Chat Input */}
            <div className="p-2 border-t border-[#333] bg-[#212729]">
              <div className="flex items-center gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault()
                      handleSendMessage()
                    }
                  }}
                  placeholder="Ask about quantum computing..."
                  className="flex-1 rounded-none border-[#444] bg-[#252526] text-white text-xs h-8"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={isLoading || !input.trim()}
                  className="rounded-none bg-[#2563EB] hover:bg-[#1d4ed8] h-8 w-8 p-0"
                >
                  {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                </Button>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="h-full bg-zinc-900 flex flex-col items-center">
          <Button
            variant="ghost"
            size="icon"
            className="h-10 w-10 text-white hover:bg-zinc-800 mt-2"
            onClick={() => setExpanded(true)}
          >
            <ChevronUp className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  )
}
