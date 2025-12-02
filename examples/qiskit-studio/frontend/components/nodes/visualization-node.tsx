/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

"use client"

import { memo, useState, useMemo, useEffect } from "react"
import { Handle, Position, type NodeProps } from "reactflow"
import { Card } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Info, ChevronDown, ChevronUp } from "lucide-react"
import { Spinner } from "@/components/ui/spinner"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

interface VisualizationNodeData {
  label: string
  category: string
  pythonCode?: string
  inputCode?: string
  onInputChange?: (nodeId: string, newInput: string) => void
  onParameterChange?: (nodeId: string, parameterName: string, newValue: any) => void
  isUpdating?: boolean
  defaultText?: string
}

export const VisualizationNode = memo(({ id, data, isConnectable }: NodeProps<VisualizationNodeData>) => {
  const [selectedVisualization, setSelectedVisualization] = useState(data.category)
  const [isInfoOpen, setIsInfoOpen] = useState(false)
  const [isResultCollapsed, setIsResultCollapsed] = useState(false)

  // Update selectedVisualization when data.category changes (e.g., from output updates)
  useEffect(() => {
    if (data.category && data.category !== selectedVisualization) {
      setSelectedVisualization(data.category)
    }
  }, [data.category, selectedVisualization])

  const handleVisualizationChange = (value: string) => {
    setSelectedVisualization(value)
    
    const visualizationCode = `visualization_type = "${value}"
if visualization_type == "Undirected Graph":
    from qiskit.visualization import plot_state_city
    plot_state_city(quantum_state)
elif visualization_type == "Histogram":
    from qiskit.visualization import plot_histogram
    plot_histogram(counts)
elif visualization_type == "Bloch Sphere":
    from qiskit.visualization import plot_bloch_multivector
    plot_bloch_multivector(quantum_state)
elif visualization_type == "Circuit Diagram":
    from qiskit.visualization import circuit_drawer
    circuit_drawer(circuit, output='mpl')
elif visualization_type == "Plot":
    import matplotlib.pyplot as plt
    plt.plot(data['CHSH1'], label='CHSH1')
    plt.plot(data['CHSH2'], label='CHSH2')
    plt.legend()
    plt.show()
elif visualization_type == "Graph":
    import matplotlib.pyplot as plt
    import networkx as nx
    G = nx.Graph()
    G.add_edges_from([(0,1), (0,2), (0,4), (1,2), (2,3), (3,4)])
    pos = nx.spring_layout(G)
    colors = ['red' if bit == 0 else 'blue' for bit in bitstring]
    nx.draw(G, pos, node_color=colors, with_labels=True)
    plt.show()
elif visualization_type == "Raw":
    print("Raw results:", counts)
else:
    print("Unknown visualization type")`
    
    data.onInputChange?.(id || '', visualizationCode)
    data.onParameterChange?.(id || '', 'visualization_type', value)
  }

  const plotData = useMemo(() => {
    if (selectedVisualization === "Plot" && data.defaultText) {
      try {
        const parsed = JSON.parse(data.defaultText.replace(/'/g, '"'))
        return parsed
      } catch (e) {
        return null
      }
    }
    return null
  }, [selectedVisualization, data.defaultText])

  const graphData = useMemo(() => {
    if (selectedVisualization === "Graph" && data.defaultText) {
      try {
        // Try to parse as JSON first
        const parsed = JSON.parse(data.defaultText)
        if (parsed.nodes && parsed.edges && parsed.bitstring) {
          return parsed
        }
        
        // Fallback: try to parse if it contains legacy bitstring format
        if (data.defaultText.includes('bitstring') || data.defaultText.includes('Result bitstring')) {
          const bitstringMatch = data.defaultText.match(/\[([0-9, ]+)\]/)
          if (bitstringMatch) {
            const bitstring = bitstringMatch[1].split(',').map(s => parseInt(s.trim()))
            return {
              nodes: 5,
              edges: [[0,1], [0,2], [0,4], [1,2], [2,3], [3,4]], // Fallback edges
              bitstring
            }
          }
        }
      } catch (e) {
        return null
      }
    }
    return null
  }, [selectedVisualization, data.defaultText])

  const renderPlot = () => {
    if (!plotData || !plotData.CHSH1 || !plotData.CHSH2) {
      return <div className="text-xs text-gray-500">No plot data available</div>
    }

    const maxVal = Math.max(...plotData.CHSH1, ...plotData.CHSH2)
    const minVal = Math.min(...plotData.CHSH1, ...plotData.CHSH2)
    const range = maxVal - minVal
    const padding = range * 0.1

    // Adjust dimensions to fit in container with margins for labels
    const containerWidth = 220 // Slightly less than node width to fit in container
    const containerHeight = 140
    const marginLeft = 35
    const marginBottom = 25
    const marginTop = 10
    const marginRight = 10
    
    const plotWidth = containerWidth - marginLeft - marginRight
    const plotHeight = containerHeight - marginTop - marginBottom

    const getY = (val: number) => {
      return marginTop + plotHeight - ((val - minVal + padding) / (range + 2 * padding)) * plotHeight
    }

    const getX = (index: number, length: number) => {
      return marginLeft + (index / (length - 1)) * plotWidth
    }

    const createPath = (values: number[]) => {
      return values.map((val, i) => 
        `${i === 0 ? 'M' : 'L'} ${getX(i, values.length)} ${getY(val)}`
      ).join(' ')
    }

    // Calculate nice tick values for Y-axis
    const yTicks = [
      minVal + padding,
      (minVal + maxVal) / 2,
      maxVal - padding
    ]

    // Calculate X-axis ticks (phase indices)
    const xTicks = [0, Math.floor(plotData.CHSH1.length / 2), plotData.CHSH1.length - 1]

    return (
      <div className="w-full flex flex-col items-center">
        <svg width={containerWidth} height={containerHeight} className="border border-gray-200">
          {/* Plot area background */}
          <rect x={marginLeft} y={marginTop} width={plotWidth} height={plotHeight} 
                fill="white" stroke="none"/>
          
          {/* Grid lines */}
          {yTicks.map((tick, i) => (
            <line key={`h-${i}`} 
                  x1={marginLeft} 
                  y1={getY(tick)} 
                  x2={marginLeft + plotWidth} 
                  y2={getY(tick)} 
                  stroke="#e0e0e0" 
                  strokeWidth="0.5"/>
          ))}
          {xTicks.map((tick, i) => (
            <line key={`v-${i}`} 
                  x1={getX(tick, plotData.CHSH1.length)} 
                  y1={marginTop} 
                  x2={getX(tick, plotData.CHSH1.length)} 
                  y2={marginTop + plotHeight} 
                  stroke="#e0e0e0" 
                  strokeWidth="0.5"/>
          ))}
          
          {/* Axes */}
          <line x1={marginLeft} y1={marginTop} x2={marginLeft} y2={marginTop + plotHeight} 
                stroke="#333" strokeWidth="1"/>
          <line x1={marginLeft} y1={marginTop + plotHeight} x2={marginLeft + plotWidth} y2={marginTop + plotHeight} 
                stroke="#333" strokeWidth="1"/>
          
          {/* CHSH1 line */}
          <path d={createPath(plotData.CHSH1)} 
                fill="none" 
                stroke="#2563EB" 
                strokeWidth="2"/>
          
          {/* CHSH2 line */}
          <path d={createPath(plotData.CHSH2)} 
                fill="none" 
                stroke="#DC2626" 
                strokeWidth="2"/>
          
          {/* Data points */}
          {plotData.CHSH1.map((val: number, i: number) => (
            <circle key={`chsh1-${i}`} 
                    cx={getX(i, plotData.CHSH1.length)} 
                    cy={getY(val)} 
                    r="1.5" 
                    fill="#2563EB"/>
          ))}
          {plotData.CHSH2.map((val: number, i: number) => (
            <circle key={`chsh2-${i}`} 
                    cx={getX(i, plotData.CHSH2.length)} 
                    cy={getY(val)} 
                    r="1.5" 
                    fill="#DC2626"/>
          ))}
          
          {/* Y-axis labels */}
          {yTicks.map((tick, i) => (
            <text key={`y-label-${i}`} 
                  x={marginLeft - 5} 
                  y={getY(tick) + 3} 
                  textAnchor="end" 
                  fontSize="8" 
                  fill="#666">
              {tick.toFixed(1)}
            </text>
          ))}
          
          {/* X-axis labels */}
          {xTicks.map((tick, i) => (
            <text key={`x-label-${i}`} 
                  x={getX(tick, plotData.CHSH1.length)} 
                  y={marginTop + plotHeight + 15} 
                  textAnchor="middle" 
                  fontSize="8" 
                  fill="#666">
              {tick}
            </text>
          ))}
          
          {/* Axis titles */}
          <text x={marginLeft + plotWidth / 2} 
                y={containerHeight - 5} 
                textAnchor="middle" 
                fontSize="9" 
                fill="#333">
            Phase Index
          </text>
          
          <text x={12} 
                y={marginTop + plotHeight / 2} 
                textAnchor="middle" 
                fontSize="9" 
                fill="#333" 
                transform={`rotate(-90, 12, ${marginTop + plotHeight / 2})`}>
            CHSH Value
          </text>
        </svg>
        
        {/* Legend */}
        <div className="flex gap-3 mt-1 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-0.5 bg-blue-600"></div>
            <span className="text-black">CHSH1</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-0.5 bg-red-600"></div>
            <span className="text-black">CHSH2</span>
          </div>
        </div>
      </div>
    )
  }

  const renderGraph = () => {
    if (!graphData) {
      return <div className="text-xs text-gray-500">No graph data available</div>
    }

    const containerWidth = 220
    const containerHeight = 160
    const centerX = containerWidth / 2
    const centerY = containerHeight / 2
    const radius = 60

    // Position nodes in a pentagon for 5 nodes
    const nodePositions = Array.from({ length: graphData.nodes }, (_, i) => {
      const angle = (i * 2 * Math.PI) / graphData.nodes - Math.PI / 2 // Start from top
      return {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      }
    })

    return (
      <div className="w-full flex flex-col items-center">
        <svg width={containerWidth} height={containerHeight} className="border border-gray-200">
          {/* Draw edges */}
          {graphData.edges.map((edge, i) => {
            const [node1, node2] = edge
            const pos1 = nodePositions[node1]
            const pos2 = nodePositions[node2]
            
            // All edges are gray and thick
            const edgeColor = "#6B7280" // Gray for all edges
            const edgeWidth = "3" // Thick for all edges
            
            return (
              <line key={`edge-${i}`}
                    x1={pos1.x} y1={pos1.y}
                    x2={pos2.x} y2={pos2.y}
                    stroke={edgeColor}
                    strokeWidth={edgeWidth}
                    opacity={1} />
            )
          })}
          
          {/* Draw nodes */}
          {nodePositions.map((pos, i) => {
            const partition = graphData.bitstring[i]
            const nodeColor = partition === 0 ? "#EF4444" : "#3B82F6" // Red for 0, Blue for 1
            
            return (
              <g key={`node-${i}`}>
                <circle cx={pos.x} cy={pos.y} r="15"
                        fill={nodeColor}
                        stroke="#fff"
                        strokeWidth="2" />
                <text x={pos.x} y={pos.y + 4}
                      textAnchor="middle"
                      fontSize="12"
                      fill="white"
                      fontWeight="bold">
                  {i}
                </text>
              </g>
            )
          })}
        </svg>
        
        {/* Legend */}
        <div className="flex flex-col gap-1 mt-2 text-xs">
          <div className="flex gap-4">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span className="text-black">Partition 0</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
              <span className="text-black">Partition 1</span>
            </div>
          </div>
          <div className="flex justify-center">
            <div className="flex items-center gap-1">
              <div className="w-4 h-1 bg-gray-500"></div>
              <span className="text-black">Graph edges</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const getResultContent = () => {
    // If defaultText is provided, use it regardless of visualization type
    if (data.defaultText) {
      return data.defaultText;
    }
    
    switch (selectedVisualization) {
      case "Undirected Graph":
        return "Graph visualization will appear here"
      case "Histogram":
        return "Histogram chart will appear here"
      case "Bloch Sphere":
        return "Bloch sphere visualization will appear here"
      case "Circuit Diagram":
        return "Circuit diagram will appear here"
      case "Plot":
        return "Plot visualization will appear here"
      case "Graph":
        return "Graph visualization will appear here"
      case "Raw":
        return "{'counts': {'00': 1024, '11': 976}, 'metadata': {'shots': 2000}}"
      case "Bitstring":
        return "Bitstring analysis results will appear here"
      case "ExpectationValues":
        return "Expectation values will appear here"
      default:
        return "Select a visualization type to see results"
    }
  }

  return (
    <Card className="w-64 border-0 shadow-md rounded-none overflow-hidden">
      <div className="bg-[#DDFBE5] h-12 flex items-center">
        <div className="w-12 h-12 bg-[#1A8038] flex items-center justify-center text-white mr-2">
          <img src="/node_icons/custom-output.svg" alt="Output" width="24" height="24" className="filter brightness-0 invert" />
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
          <Select value={selectedVisualization} onValueChange={handleVisualizationChange}>
            <SelectTrigger className="h-8 text-sm rounded-none bg-transparent border-0 border-b border-[#ccc] p-0 pb-1 text-[#666] font-normal focus:ring-0">
              <SelectValue placeholder="Select visualization" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Raw">Raw</SelectItem>
              <SelectItem value="Histogram">Histogram</SelectItem>
              <SelectItem value="Plot">Plot</SelectItem>
              <SelectItem value="Graph">Graph</SelectItem>
            </SelectContent>
          </Select>
          {data.isUpdating && (
            <div className="mt-2 text-xs text-orange-500 flex items-center">
              <Spinner size={8} className="mr-1 text-orange-500" />
              Updating...
            </div>
          )}
        </div>
        {selectedVisualization && (
          <div className="bg-white">
            <div 
              className="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-50"
              onClick={() => setIsResultCollapsed(!isResultCollapsed)}
            >
              <div className="text-xs text-[#666]">Result:</div>
              <Button variant="ghost" size="sm" className="h-4 w-4 p-0">
                {isResultCollapsed ? (
                  <ChevronDown className="h-3 w-3" />
                ) : (
                  <ChevronUp className="h-3 w-3" />
                )}
              </Button>
            </div>
            {!isResultCollapsed && (
              <div className="px-3 pb-3">
                <div className="bg-[#f8f9fa] border border-[#e9ecef] rounded p-2 min-h-16">
                  {selectedVisualization === "Plot" && plotData ? (
                    renderPlot()
                  ) : selectedVisualization === "Graph" && graphData ? (
                    renderGraph()
                  ) : (
                    <div className="text-xs font-mono text-[#495057] whitespace-pre-line">
                      {getResultContent()}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
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
    </Card>
  )
})

VisualizationNode.displayName = "VisualizationNode"
