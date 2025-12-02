/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

"use client"

import type React from "react"

import { useState, useEffect, useCallback, useRef } from "react"
import ReactFlow, {
  Background,
  Controls,
  type Node,
  type Edge,
  type Connection,
  addEdge,
  useNodesState,
  useEdgesState,
  useReactFlow,
  ReactFlowProvider,
} from "reactflow"
import "reactflow/dist/style.css"
import { Sidebar } from "./sidebar"
import { CodePanel } from "./code-panel"
import { QuantumInfoNode } from "./nodes/quantum-info-node"
import { CircuitLibraryNode } from "./nodes/circuit-library-node"
import { TranspilerNode } from "./nodes/transpiler-node"
import { TranspilerPassNode } from "./nodes/transpiler-pass-node"
import { ExecutionNode } from "./nodes/execution-node"
import { RuntimeNode } from "./nodes/runtime-node"
import { VisualizationNode } from "./nodes/visualization-node"
import { ChemistryMapNode } from "./nodes/chemistry-map-node"
import { ChemistryNode } from "./nodes/chemistry-node"
import { PythonNode } from "./nodes/python-node"
import { PostProcessNode } from "./nodes/post-process-node"
import { generateQiskitCode } from "@/lib/code-generator"
import { getDemoById } from "@/lib/demo-circuits"
import { loadDemoPythonCode, hasDemoPythonCode } from "@/lib/demo-python-loader"
import { getHighlightedCodeForNode } from "@/lib/code-section-parser"
import { parseDemoNodes } from "@/lib/demo-node-parser"
import { useAICodeGeneration } from "@/hooks/useAICodeGeneration"

// Register custom node types
const nodeTypes = {
  quantumInfoNode: QuantumInfoNode,
  circuitLibraryNode: CircuitLibraryNode,
  transpilerNode: TranspilerNode,
  transpilerPassNode: TranspilerPassNode,
  executionNode: ExecutionNode,
  runtimeNode: RuntimeNode,
  visualizationNode: VisualizationNode,
  chemistryMapNode: ChemistryMapNode,
  chemistryNode: ChemistryNode,
  pythonNode: PythonNode,
  postProcessNode: PostProcessNode,
}

// Initial nodes for the circuit based on the image
const initialNodes: Node[] = [
  {
    id: "quantum-info-1",
    type: "quantumInfoNode",
    data: { label: "Quantum info library", category: "Hamiltonian" },
    position: { x: 250, y: 100 },
  },
  {
    id: "circuit-library-1",
    type: "circuitLibraryNode",
    data: { label: "Circuit Library", category: "Ansatz" },
    position: { x: 250, y: 250 },
  },
  {
    id: "transpiler-1",
    type: "transpilerNode",
    data: { label: "Transpiler" },
    position: { x: 250, y: 400 },
  },
  {
    id: "execution-1",
    type: "executionNode",
    data: { label: "Execution modes" },
    position: { x: 550, y: 300 },
  },
  {
    id: "runtime-1",
    type: "runtimeNode",
    data: {
      label: "Runtime primitives",
      category: "Estimator",
      loopCount: 10,
    },
    position: { x: 550, y: 450 },
  },
  {
    id: "runtime-2",
    type: "runtimeNode",
    data: {
      label: "Runtime primitives",
      category: "Sampler",
    },
    position: { x: 550, y: 650 },
  },
  {
    id: "visualization-1",
    type: "visualizationNode",
    data: {
      label: "Visualization module",
      category: "Undirected Graph",
    },
    position: { x: 850, y: 700 },
  },
]

// Initial edges for the circuit based on the image
const initialEdges: Edge[] = [
  {
    id: "e-quantum-circuit",
    source: "quantum-info-1",
    target: "circuit-library-1",
    animated: true,
    type: "smoothstep",
    style: { stroke: "#8a3ffc" },
  },
  {
    id: "e-circuit-transpiler",
    source: "circuit-library-1",
    target: "transpiler-1",
    animated: true,
    type: "smoothstep",
    style: { stroke: "#8a3ffc" },
  },
  {
    id: "e-transpiler-execution",
    source: "transpiler-1",
    target: "execution-1",
    animated: true,
    type: "smoothstep",
    style: { stroke: "#e83e8c" },
  },
  {
    id: "e-execution-runtime",
    source: "execution-1",
    target: "runtime-1",
    animated: true,
    type: "smoothstep",
    style: { stroke: "#2563EB" },
  },
  {
    id: "e-runtime1-runtime2",
    source: "runtime-1",
    target: "runtime-2",
    animated: true,
    type: "smoothstep",
    style: { stroke: "#2563EB" },
  },
  {
    id: "e-runtime2-visualization",
    source: "runtime-2",
    target: "visualization-1",
    animated: true,
    type: "smoothstep",
    style: { stroke: "#2563EB" },
  },
]

function QuantumComposerInner() {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const { fitView } = useReactFlow()
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [currentDemoId, setCurrentDemoId] = useState<string | null>("chemistry-simulation")
  const [demoPythonCode, setDemoPythonCode] = useState<string | null>(null)
  const [highlightSection, setHighlightSection] = useState<{
    startLine: number
    endLine: number
    step: number
  } | null>(null)
  const [backendConfig, setBackendConfig] = useState<{
    type: 'specific' | 'auto'
    backend?: string
    apiToken?: string
  } | null>(null)
  const [nodeInputs, setNodeInputs] = useState<{ [nodeId: string]: string }>({})
  const [parsedNodeData, setParsedNodeData] = useState<{ [nodeId: string]: { pythonCode: string, inputCode?: string } }>({})
  const [nodeParameters, setNodeParameters] = useState<{ [nodeId: string]: any }>({})
  const [fullCode, setFullCode] = useState('');
  const [initialParsedNodeData, setInitialParsedNodeData] = useState<{ [key: string]: { pythonCode: string, inputCode?: string } }>({});
  
  
  // Initialize AI code generation hook first
  const {
    isGenerating: isUpdatingCode,
    generatingNodeIds: updatingNodeIds,
    lastError,
    generateCodeForParameter,
    generateCodeImprovement,
    setNodeUpdating,
    clearError,
    isNodeUpdating
  } = useAICodeGeneration()

  // Define callback functions that depend on the AI hook
  const handleNodeInputChange = useCallback((nodeId: string, newInput: string) => {
    setNodeInputs(prev => ({
      ...prev,
      [nodeId]: newInput
    }));
  }, []);

  const handleUpdatePostProcessingNode = useCallback((resultJson: { type: 'text' | 'graph' | 'plot', content: string }) => {
    setNodes(currentNodes => {
      return currentNodes.map(node => {
        // Target the specific node with ID "Output"
        if (node.id === "Output") {
          // Create the appropriate output code based on type
          let outputCode = '';
          switch (resultJson.type) {
            case 'text':
              outputCode = `# Text output\nprint("${resultJson.content.replace(/"/g, '\\"')}")`;
              break;
            case 'graph':
              outputCode = `# Graph visualization\nimport matplotlib.pyplot as plt\nimport json\n\n# Parse graph data\ndata = json.loads('${JSON.stringify(resultJson.content)}')\nprint("Graph data loaded successfully")`;
              break;
            case 'plot':
              outputCode = `# Plot visualization\nimport matplotlib.pyplot as plt\nimport json\n\n# Parse plot data\ndata = json.loads('${JSON.stringify(resultJson.content)}')\nprint("Plot data loaded successfully")`;
              break;
          }
          
          // Handle content based on type
          let processedContent = resultJson.content;
          if (resultJson.type === 'text' && typeof resultJson.content === 'string') {
            // Only apply string replacement for text content
            processedContent = resultJson.content.replace(/\\n/g, '\n');
          } else if (resultJson.type === 'graph' || resultJson.type === 'plot') {
            // For graph/plot data, ensure it's a JSON string for the VisualizationNode
            processedContent = typeof resultJson.content === 'string' 
              ? resultJson.content 
              : JSON.stringify(resultJson.content);
          }

          return {
            ...node,
            data: {
              ...node.data,
              inputValue: outputCode,
              inputCode: outputCode,
              defaultText: processedContent,
              resultType: resultJson.type,
              resultContent: resultJson.content,
              category: resultJson.type === 'text' ? 'Raw' : resultJson.type === 'graph' ? 'Graph' : 'Plot'
            }
          };
        }
        return node;
      });
    });
  }, [setNodes]);

  // Add a ref to track ongoing API calls to prevent duplicates
  const ongoingAPICalls = useRef<Set<string>>(new Set());
  
  // Track chemistry node updates that are waiting for code generation
  const [pendingChemistryUpdates, setPendingChemistryUpdates] = useState<Set<string>>(new Set());
  
  // Track the expected molecular changes to verify when they're actually applied
  const [expectedMolecularChanges, setExpectedMolecularChanges] = useState<Map<string, string>>(new Map());

  // Custom function to check if a node is updating (AI call + pending code generation)
  const isNodeCurrentlyUpdating = useCallback((nodeId: string) => {
    return isNodeUpdating(nodeId) || pendingChemistryUpdates.has(nodeId);
  }, [isNodeUpdating, pendingChemistryUpdates]);

  const handleParameterChange = useCallback(async (nodeId: string, parameterName: string, newValue: any) => {
    setNodeParameters(prev => ({
      ...prev,
      [nodeId]: {
        ...prev[nodeId],
        [parameterName]: newValue
      }
    }));

    // Handle inputCode parameter specially - don't call AI, just update node data and nodeInputs
    if (parameterName === 'inputCode') {
      // Update both nodeInputs and node data atomically
      setNodeInputs(prev => ({
        ...prev,
        [nodeId]: newValue
      }));
      setNodes(currentNodes => {
        return currentNodes.map(node => {
          if (node.id === nodeId) {
            return {
              ...node,
              data: {
                ...node.data,
                inputCode: newValue
              }
            };
          }
          return node;
        });
      });
      return;
    }

    // Prevent duplicate API calls for the same parameter change
    const callKey = `${nodeId}-${parameterName}-${JSON.stringify(newValue)}`;
    if (ongoingAPICalls.current.has(callKey)) {
      return;
    }

    setTimeout(async () => {
      setNodes(currentNodes => {
        const node = currentNodes.find(n => n.id === nodeId);
        if (!node) {
          return currentNodes;
        }

        (async () => {
          // Track this API call
          ongoingAPICalls.current.add(callKey);
          
          try {
            const response = await generateCodeForParameter({
              nodeId,
              nodeType: node.type || 'unknown',
              currentCode: node.data.pythonCode || node.data.inputCode || '',
              parameterName,
              newValue,
              nodeLabel: node.data.label,
              sessionId: `param-update-${nodeId}`
            });

            if (response.success && response.code) {
              // For chemistry nodes with molecule parameter, update inputCode instead of pythonCode
              const isChemistryMoleculeUpdate = (node.type === 'chemistryNode' || node.type === 'chemistryMapNode') && parameterName === 'molecule';
              
              // Track chemistry updates that need to wait for code generation
              if (isChemistryMoleculeUpdate) {
                setPendingChemistryUpdates(prev => new Set(prev).add(nodeId));
                // Track the expected molecular code to verify when it's actually applied
                setExpectedMolecularChanges(prev => {
                  const newMap = new Map(prev);
                  newMap.set(nodeId, response.code!);
                  return newMap;
                });
              }
              
              setNodes(currentNodes => {
                const updatedNodes = currentNodes.map(n => {
                  if (n.id === nodeId) {
                    return { 
                      ...n, 
                      data: { 
                        ...n.data, 
                        ...(isChemistryMoleculeUpdate 
                          ? { inputCode: response.code } 
                          : { pythonCode: response.code }
                        ),
                        lastUpdated: Date.now()
                      } 
                    };
                  }
                  return n;
                });
                
                return updatedNodes;
              });

              // Update nodeInputs for chemistry nodes to trigger code replacement
              if (isChemistryMoleculeUpdate) {
                setNodeInputs(prev => ({
                  ...prev,
                  [nodeId]: response.code!
                }));
              } else {
                setParsedNodeData(prev => ({
                  ...prev,
                  [node.data.label]: {
                    ...prev[node.data.label],
                    pythonCode: response.code!
                  }
                }));
              }
              
            } else {
              if (response.error) {
                alert(`Failed to update code: ${response.error}`);
              }
            }
          } catch (error) {
            alert(`Error during code update: ${error instanceof Error ? error.message : 'Unknown error'}`);
          } finally {
            // Clear the API call tracking
            ongoingAPICalls.current.delete(callKey);
          }
        })();

        return currentNodes;
      });
    }, 0);
  }, [generateCodeForParameter, setNodes, setParsedNodeData]);


  useEffect(() => {
    const demo = getDemoById("chemistry-simulation")
    if (demo) {
      const enhancedNodes = demo.nodes.map(node => ({
        ...node,
        data: {
          ...node.data,
          onInputChange: handleNodeInputChange,
          onParameterChange: handleParameterChange,
          isUpdating: isNodeCurrentlyUpdating(node.id)
        }
      }));
      
      setNodes(enhancedNodes)
      setEdges(demo.edges)
      setTimeout(() => fitView({ padding: 0.1 }), 100)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (currentDemoId && hasDemoPythonCode(currentDemoId)) {
      loadDemoPythonCode(currentDemoId).then((code) => {
        setDemoPythonCode(code);
        
        const parsed = parseDemoNodes(code, currentDemoId || '');
        const nodeDataMap: { [key: string]: { pythonCode: string, inputCode?: string } } = {};
        
        parsed.nodes.forEach(node => {
          nodeDataMap[node.title] = {
            pythonCode: node.pythonCode,
            inputCode: node.inputCode
          };
        });
        
        setParsedNodeData(nodeDataMap);
        setInitialParsedNodeData(nodeDataMap);
        
        setNodes(currentNodes => {
          const updatedNodes = currentNodes.map(node => {
            const demoPythonCode = findNodePythonCode(node.data.label, nodeDataMap);
            const demoInputCode = findNodeInputCode(node.data.label, nodeDataMap);
            
            const shouldUseExistingCode = node.data.lastUpdated && node.data.pythonCode;
            
            return {
              ...node,
              data: {
                ...node.data,
                pythonCode: shouldUseExistingCode ? node.data.pythonCode : (demoPythonCode || node.data.pythonCode),
                inputCode: demoInputCode || node.data.inputCode,
                onInputChange: handleNodeInputChange,
                onParameterChange: handleParameterChange,
                isUpdating: isNodeCurrentlyUpdating(node.id)
              }
            };
          });
          
          return updatedNodes;
        });
      });
    } else {
      setDemoPythonCode(null);
      setParsedNodeData({});
    }
  }, [currentDemoId, handleNodeInputChange, handleParameterChange, isNodeCurrentlyUpdating, setNodes]);

  const generateBackendConfig = useCallback(() => {
    if (!backendConfig) return ''
    
    let configCode = '## STEP 0 : IBM Quantum Config\n'
    configCode += 'from qiskit_ibm_runtime import QiskitRuntimeService\n\n'
    configCode += 'service = QiskitRuntimeService()\n'
    
    if (backendConfig.type === 'specific' && backendConfig.backend) {
      configCode += `backend = service.backend("${backendConfig.backend}")\n`
    } else {
      configCode += 'backend = service.least_busy(operational=True, simulator=False)\n'
    }
    
    return configCode + '\n'
  }, [backendConfig])

  const getBackendConfigOffset = () => {
    if (!backendConfig || !demoPythonCode) return 0
    return 0
  }


  useEffect(() => {
    if (currentDemoId && demoPythonCode) {
      let reconstructedCode = demoPythonCode;

      // Replace pythonCode changes
      nodes.forEach(node => {
        const initialNodeData = initialParsedNodeData[node.data.label];
        if (initialNodeData && node.data.pythonCode && initialNodeData.pythonCode !== node.data.pythonCode) {
          reconstructedCode = reconstructedCode.replace(initialNodeData.pythonCode, node.data.pythonCode);
        }
      });

      // Handle INPUT PYTHON section replacements for chemistry nodes and others
      Object.entries(nodeInputs).forEach(([nodeId, inputCode]) => {
        if (inputCode.trim()) {
          const node = nodes.find(n => n.id === nodeId);
          if (node && node.data.inputCode) {
            const inputSectionRegex = /(####?\s*INPUT PYTHON[\s\S]*?)(####?\s*END INPUT PYTHON|######\s*END INPUT PYTHON)/g;
            reconstructedCode = reconstructedCode.replace(inputSectionRegex, (match, start, end) => {
              return start.split('\n')[0] + '\n' + inputCode.trim() + '\n' + end;
            });
          }
        }
      });

      // Handle backend configuration
      const backendConfigCode = generateBackendConfig();
      const hasOriginalStep0 = reconstructedCode.includes('## STEP 0 : IBM Quantum Config');
      
      if (backendConfigCode && hasOriginalStep0) {
        const lines = reconstructedCode.split('\n');
        const cleanedLines = [];
        let skipIBMConfig = false;
        
        for (let i = 0; i < lines.length; i++) {
          const line = lines[i];
          
          if (line.includes('## STEP 0 : IBM Quantum Config')) {
            skipIBMConfig = true;
            continue;
          }
          
          if (skipIBMConfig) {
            if (line.includes('from qiskit_ibm_runtime import QiskitRuntimeService') ||
                line.includes('service = QiskitRuntimeService()') ||
                line.includes('backend = service.backend') ||
                line.includes('backend = service.least_busy') ||
                line.trim() === '') {
              continue;
            }
            
            if (line.startsWith('##') || (line.trim() !== '' && !line.includes('from qiskit_ibm_runtime'))) {
              skipIBMConfig = false;
            }
          }
          
          if (!skipIBMConfig) {
            cleanedLines.push(line);
          }
        }
        
        setFullCode(backendConfigCode + cleanedLines.join('\n'));
      } else if (backendConfigCode && !hasOriginalStep0) {
        setFullCode(backendConfigCode + reconstructedCode);
      } else {
        setFullCode(reconstructedCode);
      }
      
      // Clear pending chemistry updates only when the expected molecular code is actually in fullCode
      if (pendingChemistryUpdates.size > 0) {
        const updatesStillPending = new Set<string>();
        const changesStillPending = new Map<string, string>();
        
        pendingChemistryUpdates.forEach(nodeId => {
          const expectedCode = expectedMolecularChanges.get(nodeId);
          if (expectedCode && reconstructedCode.includes(expectedCode)) {
            // The expected molecular code is now in the full code, remove from pending
          } else {
            // Still waiting for this update to be reflected
            updatesStillPending.add(nodeId);
            if (expectedCode) {
              changesStillPending.set(nodeId, expectedCode);
            }
          }
        });
        
        setPendingChemistryUpdates(updatesStillPending);
        setExpectedMolecularChanges(changesStillPending);
      }

    } else if (!currentDemoId) {
      // Handle non-demo cases
      const baseCode = selectedNode
        ? generateQiskitCode(
            [selectedNode],
            edges.filter((e) => e.source === selectedNode.id || e.target === selectedNode.id),
          )
        : generateQiskitCode(nodes, edges);
      setFullCode(baseCode);
      
      // Clear any pending updates since we're not in demo mode
      if (pendingChemistryUpdates.size > 0) {
        setPendingChemistryUpdates(new Set());
        setExpectedMolecularChanges(new Map());
      }
    }

  }, [nodes, edges, selectedNode, currentDemoId, demoPythonCode, initialParsedNodeData, nodeInputs, pendingChemistryUpdates, expectedMolecularChanges, backendConfig, generateBackendConfig]);

  const onConnect = (params: Edge | Connection) => {
    let edgeStyle = { stroke: "#2563EB" }

    const sourceNode = nodes.find((node) => node.id === params.source)
    if (sourceNode) {
      if (sourceNode.type === "quantumInfoNode" || sourceNode.type === "circuitLibraryNode") {
        edgeStyle = { stroke: "#8a3ffc" }
      } else if (sourceNode.type === "transpilerNode") {
        edgeStyle = { stroke: "#e83e8c" }
      } else if (sourceNode.type === "visualizationNode") {
        edgeStyle = { stroke: "#28a745" }
      }
    }

    setEdges((eds) => addEdge({ ...params, animated: true, style: edgeStyle }, eds))
    setCurrentDemoId(null)
    setDemoPythonCode(null)
    setHighlightSection(null)
  }

  const onNodeClick = (_: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
    
    if (currentDemoId && demoPythonCode) {
      const highlighted = getHighlightedCodeForNode(
        demoPythonCode,
        node.type || '',
        node.data?.category,
        node.data?.label
      )
      
      if (highlighted.highlightSection) {
        const offset = getBackendConfigOffset()
        const adjustedHighlightSection = {
          ...highlighted.highlightSection,
          startLine: highlighted.highlightSection.startLine + offset,
          endLine: highlighted.highlightSection.endLine + offset
        }
        setHighlightSection(adjustedHighlightSection)
      } else {
        setHighlightSection(null)
      }
    } else {
      setHighlightSection(null)
    }
  }

  const onAddNode = useCallback((nodeType: string, nodeData: any) => {
    const newNode = {
      id: `${nodeType}-${Date.now()}`,
      type: nodeType,
      data: nodeData,
      position: {
        x: Math.random() * 300 + 50,
        y: Math.random() * 300 + 50,
      },
    }

    const enhancedNode = {
      ...newNode,
      data: {
        ...newNode.data,
        onInputChange: handleNodeInputChange,
        onParameterChange: handleParameterChange,
        isUpdating: isNodeUpdating(newNode.id)
      }
    };

    setNodes((nds) => [...nds, enhancedNode])
    // Don't clear demo state when adding a new node - keep the full code intact
    // setCurrentDemoId(null)
    // setDemoPythonCode(null)
    setHighlightSection(null)
  }, [handleNodeInputChange, handleParameterChange, isNodeUpdating, setNodes])

  const findNodePythonCode = (nodeLabel: string, nodeDataMap: any) => {
    if (nodeDataMap[nodeLabel]) {
      return nodeDataMap[nodeLabel].pythonCode;
    }
    
    for (const [key, value] of Object.entries(nodeDataMap)) {
      if (key.toLowerCase().includes(nodeLabel.toLowerCase()) || 
          nodeLabel.toLowerCase().includes(key.toLowerCase())) {
        return (value as any).pythonCode;
      }
    }
    
    return undefined;
  };
  
  const findNodeInputCode = (nodeLabel: string, nodeDataMap: any) => {
    if (nodeDataMap[nodeLabel]) {
      return nodeDataMap[nodeLabel].inputCode;
    }
    
    for (const [key, value] of Object.entries(nodeDataMap)) {
      if (key.toLowerCase().includes(nodeLabel.toLowerCase()) || 
          nodeLabel.toLowerCase().includes(key.toLowerCase())) {
        return (value as any).inputCode;
      }
    }
    
    return undefined;
  };
  
  const onLoadDemo = useCallback((demoId: string) => {
    const demo = getDemoById(demoId)
    if (demo) {
      const enhancedDemoNodes = demo.nodes.map(node => ({
        ...node,
        data: {
          ...node.data,
          onInputChange: handleNodeInputChange,
          onParameterChange: handleParameterChange,
          isUpdating: false
        }
      }));
      
      setNodes(enhancedDemoNodes)
      setEdges(demo.edges)
      setSelectedNode(null)
      setCurrentDemoId(demoId)
      setHighlightSection(null)
      setNodeInputs({})
      setTimeout(() => fitView({ padding: 0.1 }), 100)
    }
  }, [handleNodeInputChange, handleParameterChange, setNodes, setEdges, fitView])

  return (
    <div className="flex h-screen">
      <Sidebar 
        onAddNode={onAddNode} 
        onLoadDemo={onLoadDemo} 
      />
      <div className="flex flex-1">
        <div className="flex-1 h-full">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
            defaultViewport={{ x: 0, y: 0, zoom: 0.6 }}
          >
            <Controls position="bottom-right" />
            <Background variant={'dots' as any} gap={12} size={1} />
          </ReactFlow>
        </div>
        <CodePanel
          code={fullCode}
          selectedNode={selectedNode?.data?.label || "Full Circuit"}
          onSelectDemo={onLoadDemo}
          highlightSection={highlightSection}
          onBackendConfigChange={setBackendConfig}
          isUpdatingCode={isUpdatingCode}
          onUpdatePostProcessingNode={handleUpdatePostProcessingNode}
        />
      </div>
    </div>
  )
}

export function QuantumComposer() {
  return (
    <ReactFlowProvider>
      <QuantumComposerInner />
    </ReactFlowProvider>
  )
}
