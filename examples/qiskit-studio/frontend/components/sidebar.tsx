/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  MapIcon,
  Settings,
  Play,
  BarChart,
  ChevronDown,
  ChevronUp,
  Plus,
  Beaker,
  Network,
  LineChart,
} from "lucide-react"

interface SidebarProps {
  onAddNode: (nodeType: string, nodeData: any) => void
  onLoadDemo: (demoId: string) => void
}

export function Sidebar({ onAddNode, onLoadDemo }: SidebarProps) {
  const [activeSection, setActiveSection] = useState<string | null>(null)
  const [isDemosCollapsed, setIsDemosCollapsed] = useState(true)

  const sections = [
    {
      id: "map",
      name: "Map",
      icon: <MapIcon className="h-4 w-4" />,
      nodes: [
        {
          id: "quantumInfoNode",
          name: "Quantum Info Library",
          data: { label: "Quantum info library", category: "Hamiltonian" },
        },
        {
          id: "circuitLibraryNode",
          name: "Circuit Library",
          data: { label: "Circuit Library", category: "Ansatz" },
        },
        {
          id: "chemistryNode",
          name: "Chemistry",
          data: { 
            label: "Chemistry", 
            category: "Molecular System",
            pythonCode: `# H₂ - testbed molecule
# Basis set options: Adaptive minimal (~2 qubits), STO-3G (~2 qubits)
mol = pyscf.gto.Mole()
mol.build(
    atom=[["H", (0.0, 0.0, 0.0)], ["H", (0.74, 0.0, 0.0)]],  # bond length ~0.74 Å
    basis="sto-3g",
    spin=0,
    charge=0
)`
          },
        },
        {
          id: "chemistryMapNode",
          name: "Chemistry Map",
          data: { 
            label: "Chemistry Map", 
            category: "Molecular System",
            inputValue: `atom=[["N", (0, 0, 0)], ["N", (1.0, 0, 0)]],\nbasis="6-31g",\nsymmetry="Dooh"`,
            placeholder: "Define molecular parameters",
            details: "Maps chemical problem to quantum computation"
          },
        },
        {
          id: "pythonNode",
          name: "Python Code",
          data: { 
            label: "Python Code", 
            category: "Python",
            placeholder: "Enter Python code...",
            details: "Custom Python code block"
          },
        },
      ],
    },
    {
      id: "optimize",
      name: "Optimize",
      icon: <Settings className="h-4 w-4" />,
      nodes: [
        {
          id: "transpilerNode",
          name: "Transpiler",
          data: { label: "Transpiler" },
        },
        {
          id: "transpilerPassNode",
          name: "Transpiler Pass",
          data: { label: "Transpiler Pass" },
        },
      ],
    },
    {
      id: "execute",
      name: "Execute",
      icon: <Play className="h-4 w-4" />,
      nodes: [
        {
          id: "executionNode",
          name: "Execution Modes",
          data: { label: "Execution modes" },
        },
        {
          id: "runtimeNode",
          name: "Runtime Primitives",
          data: { label: "Runtime primitives", category: "Estimator", loopCount: 10 },
        },
      ],
    },
    {
      id: "post-process",
      name: "Post-process",
      icon: <BarChart className="h-4 w-4" />,
      nodes: [
        {
          id: "visualizationNode",
          name: "Visualization Module",
          data: { label: "Visualization module", category: "Undirected Graph" },
        },
        {
          id: "postProcessNode",
          name: "Post Process Code",
          data: { 
            label: "Post Process Code", 
            category: "Python",
            placeholder: "Enter Python code for post-processing...",
            details: "Custom Python code for post-processing results"
          },
        },
      ],
    },
  ]

  return (
    <>
      {/* Main category buttons - top left */}
      <div className="absolute left-4 top-4 z-50 space-y-2 w-64">
        {sections.map((section) => (
          <div key={section.id} className="space-y-1">
            <Button
              variant={activeSection === section.id ? "secondary" : "ghost"}
              className={`w-full justify-start text-xs font-medium rounded-lg backdrop-blur-sm ${
                activeSection === section.id
                  ? "bg-[#e6e6ff]/90 text-[#5a5ad9] hover:bg-[#d9d9ff]/90 shadow-md"
                  : "text-[#444] hover:bg-[#e9e9e9]/90 hover:text-[#222] bg-white/80 shadow-sm"
              }`}
              onClick={() => setActiveSection(activeSection === section.id ? null : section.id)}
            >
              {section.icon}
              <span className="ml-2">{section.name}</span>
              {activeSection === section.id ? (
                <ChevronUp className="ml-auto h-4 w-4" />
              ) : (
                <ChevronDown className="ml-auto h-4 w-4" />
              )}
            </Button>

            {activeSection === section.id && (
              <div className="ml-6 space-y-1">
                {section.nodes.map((node, index) => (
                  <Button
                    key={`${node.id}-${index}`}
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start text-xs text-[#333] font-medium hover:bg-[#f0f0ff]/90 hover:text-[#3a3a99] transition-colors rounded-lg bg-white/70 backdrop-blur-sm shadow-sm"
                    onClick={() => {
                      onAddNode(node.id, node.data)
                      setActiveSection(null) // Collapse all sections after adding a node
                    }}
                  >
                    <Plus className={`mr-2 h-3 w-3 ${
                      ['quantumInfoNode', 'circuitLibraryNode', 'chemistryNode', 'chemistryMapNode', 'pythonNode'].includes(node.id)
                        ? "text-[#D02771]"
                        : ['transpilerNode', 'transpilerPassNode'].includes(node.id)
                          ? "text-[#893FFC]"
                          : ['executionNode', 'runtimeNode'].includes(node.id)
                            ? "text-[#0E62FE]"
                            : ['postProcessNode', 'visualizationNode'].includes(node.id)
                              ? "text-[#1A8038]"
                              : "text-[#666]"
                    }`} />
                    <span className="text-[#333] hover:text-[#3a3a99]">{node.name}</span>
                  </Button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
      
      {/* Demos section - bottom left */}
      <div className="absolute left-4 bottom-4 z-50 w-64">
        <div className="bg-[#2563EB]/90 text-white p-2 rounded-lg backdrop-blur-sm shadow-md">
          <div 
            className="flex items-center justify-between cursor-pointer hover:bg-white/10 rounded p-1 transition-colors w-full"
            onClick={() => setIsDemosCollapsed(!isDemosCollapsed)}
          >
            <div className="flex items-center">
              {isDemosCollapsed ? (
                <ChevronDown className="h-4 w-4 mr-2" />
              ) : (
                <ChevronUp className="h-4 w-4 mr-2" />
              )}
              <span className="text-xs font-medium">Custom Qiskit Functions</span>
            </div>
          </div>
          {!isDemosCollapsed && (
            <div className="space-y-1 mt-2">
              {[
                { id: "chemistry-simulation", name: "Chemistry Simulation", icon: Beaker },
                { id: "max-cut", name: "Max Cut", icon: Network },
                { id: "chsh-inequality", name: "CHSH Inequality", icon: LineChart },
              ].map((demo) => (
                <Button
                  key={demo.id}
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start text-xs text-white hover:bg-[#3b74f3] transition-colors rounded-lg"
                  onClick={() => onLoadDemo(demo.id)}
                >
                  <demo.icon className="mr-2 h-3 w-3" />
                  <span>{demo.name}</span>
                </Button>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  )
}
