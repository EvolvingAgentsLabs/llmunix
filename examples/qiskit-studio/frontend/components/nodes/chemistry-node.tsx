/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

"use client"

import React, { memo, useState, useEffect, useRef } from "react"
import { Handle, Position, type NodeProps } from "reactflow"
import { Card } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Info } from "lucide-react"
import { Spinner } from "@/components/ui/spinner"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

interface ChemistryNodeData {
  label: string
  category: string
  pythonCode?: string
  inputCode?: string
  onInputChange?: (nodeId: string, newInput: string) => void
  onParameterChange?: (nodeId: string, parameterName: string, newValue: any) => void
  isUpdating?: boolean
}

// XYZ format data for 3Dmol.js visualization
const getXYZData = (moleculeKey: string): string => {
  const xyzData: { [key: string]: string } = {
    "H2": `2
H2 molecule
H 0.0 0.0 0.0
H 0.74 0.0 0.0`,
    
    "LiH": `2
LiH molecule
Li 0.0 0.0 0.0
H 1.595 0.0 0.0`,
    
    "BeH2": `3
BeH2 molecule
H -1.3264 0.0 0.0
Be 0.0 0.0 0.0
H 1.3264 0.0 0.0`,
    
    "H2O": `3
Water molecule
O 0.000000 0.000000 0.000000
H 0.757160 0.586260 0.000000
H -0.757160 0.586260 0.000000`,
    
    "N2": `2
Nitrogen molecule
N 0.0 0.0 0.0
N 1.0977 0.0 0.0`,
    
    "CO": `2
Carbon monoxide
C 0.0 0.0 0.0
O 1.1283 0.0 0.0`,
    
    "NH3": `4
Ammonia molecule
N 0.000000 0.000000 0.000000
H 0.000000 0.9377 -0.3816
H 0.8121 -0.4688 -0.3816
H -0.8121 -0.4688 -0.3816`,
    
    "CH4": `5
Methane molecule
C 0.000000 0.000000 0.000000
H 0.629118 0.629118 0.629118
H -0.629118 -0.629118 0.629118
H -0.629118 0.629118 -0.629118
H 0.629118 -0.629118 -0.629118`,
    
    "Fe2S2": `4
Iron-sulfur cluster
Fe 0.000000 0.000000 0.000000
Fe 2.7 0.000000 0.000000
S -1.35 2.34 0.000000
S -1.35 -2.34 0.000000`
  };
  
  return xyzData[moleculeKey] || xyzData["H2"];
};

// Molecule data with accurate molecular geometries and basis sets
const molecules = {
  "H2": {
    name: "H₂",
    description: "testbed molecule",
    pythonTemplate: `
# H₂ - testbed molecule
mol = pyscf.gto.Mole()
mol.build(
    atom=[["H", (0.0, 0.0, 0.0)], ["H", (0.74, 0.0, 0.0)]],  # bond length ~0.74 Å
    basis="cc-pvdz",
    symmetry="Dooh",
    spin=0,
    charge=0
)`,
    basisSets: [
      { name: "cc-pVDZ", qubits: "~2 qubits" },
      { name: "STO-3G", qubits: "~2 qubits" }
    ],
    atoms: [
      { element: "H", x: 0.0, y: 0.0, z: 0.0 },
      { element: "H", x: 0.74, y: 0.0, z: 0.0 }
    ]
  },
  "LiH": {
    name: "LiH",
    description: "classic VQE demo",
    pythonTemplate: `# LiH - classic VQE demo
# Basis set options: STO-3G (~4–8 qubits), 6-31G
mol = pyscf.gto.Mole()
mol.build(
    atom=[["Li", (0.0, 0.0, 0.0)], ["H", (1.595, 0.0, 0.0)]],  # bond length ~1.595 Å
    basis="sto-3g",
    spin=0,
    charge=0
)`,
    basisSets: [
      { name: "STO-3G (standard)", qubits: "~4–8 qubits" },
      { name: "6-31G", qubits: "~8–12 qubits" }
    ],
    atoms: [
      { element: "Li", x: 0.0, y: 0.0, z: 0.0 },
      { element: "H", x: 1.595, y: 0.0, z: 0.0 }
    ]
  },
  "BeH2": {
    name: "BeH₂",
    description: "small molecule demo",
    pythonTemplate: `# BeH₂ - small molecule demo
# Basis set options: STO-3G (~6–10 qubits), 6-31G
mol = pyscf.gto.Mole()
mol.build(
    atom=[
        ["H", (-1.3264, 0.0, 0.0)],
        ["Be", (0.0, 0.0, 0.0)],
        ["H", (1.3264, 0.0, 0.0)]
    ],  # linear geometry, Be–H ~1.3264 Å
    basis="sto-3g",
    spin=0,
    charge=0
)`,
    basisSets: [
      { name: "sto-3g", qubits: "~6–10 qubits" },
      { name: "6-31G", qubits: "~10–14 qubits" }
    ],
    atoms: [
      { element: "H", x: -1.3264, y: 0.0, z: 0.0 },
      { element: "Be", x: 0.0, y: 0.0, z: 0.0 },
      { element: "H", x: 1.3264, y: 0.0, z: 0.0 }
    ]
  },
  "H2O": {
    name: "H₂O",
    description: "water molecule",
    pythonTemplate: `# H₂O - water molecule
# Basis set options: STO-3G (~8 qubits CAS), 6-31G (~26 qubits), cc-pVDZ (~48 qubits)
mol = pyscf.gto.Mole()
mol.build(
    atom=[
        ["O", (0.000000, 0.000000, 0.000000)],
        ["H", (0.757160, 0.586260, 0.000000)],
        ["H", (-0.757160, 0.586260, 0.000000)]
    ],  # bond ~0.958 Å, angle ~104.45°
    basis="sto-3g",
    spin=0,
    charge=0
)`,
    basisSets: [
      { name: "sto-3g", qubits: "~8 qubits" },
      { name: "6-31G", qubits: "~26 qubits" },
      { name: "cc-pVDZ", qubits: "~48 qubits" }
    ],
    atoms: [
      { element: "O", x: 0.000000, y: 0.000000, z: 0.000000 },
      { element: "H", x: 0.757160, y: 0.586260, z: 0.000000 },
      { element: "H", x: -0.757160, y: 0.586260, z: 0.000000 }
    ]
  },
  "N2": {
    name: "N₂",
    description: "nitrogen molecule",
    pythonTemplate: `# N₂ - nitrogen molecule
# Basis set options: 6-31G (CAS(10,16)), cc-pVDZ (CAS(10,26))
mol = pyscf.gto.Mole()
mol.build(
    atom=[
        ["N", (0.0, 0.0, 0.0)],
        ["N", (1.0977, 0.0, 0.0)]
    ],  # bond length ~1.0977 Å
    basis="6-31g",
    spin=0,
    charge=0,
    symmetry="Dooh"
)`,
    basisSets: [
      { name: "6-31G", qubits: "~16 qubits" },
      { name: "cc-pVDZ", qubits: "~58 qubits" }
    ],
    atoms: [
      { element: "N", x: 0.0, y: 0.0, z: 0.0 },
      { element: "N", x: 1.0977, y: 0.0, z: 0.0 }
    ]
  },
  "CO": {
    name: "CO",
    description: "carbon monoxide",
    pythonTemplate: `# CO - carbon monoxide
# Basis set options: STO-3G (~10–20 qubits), 6-31G
mol = pyscf.gto.Mole()
mol.build(
    atom=[
        ["C", (0.0, 0.0, 0.0)],
        ["O", (1.1283, 0.0, 0.0)]
    ],  # bond length ~1.1283 Å
    basis="sto-3g",
    spin=0,
    charge=0
)`,
    basisSets: [
      { name: "sto-3g", qubits: "~10–20 qubits" },
      { name: "6-31G", qubits: "~15–25 qubits" }
    ],
    atoms: [
      { element: "C", x: 0.0, y: 0.0, z: 0.0 },
      { element: "O", x: 1.1283, y: 0.0, z: 0.0 }
    ]
  },
  "NH3": {
    name: "NH₃",
    description: "ammonia",
    pythonTemplate: `# NH₃ - ammonia
# Basis set options: STO-3G (~10–20 qubits), 6-31G
mol = pyscf.gto.Mole()
mol.build(
    atom=[
        ["N", (0.000000, 0.000000, 0.000000)],
        ["H", (0.000000, 0.9377, -0.3816)],
        ["H", (0.8121, -0.4688, -0.3816)],
        ["H", (-0.8121, -0.4688, -0.3816)]
    ],  # bond ~1.012 Å, angle ~107.8°
    basis="sto-3g",
    spin=0,
    charge=0
)`,
    basisSets: [
      { name: "sto-3g", qubits: "~10–20 qubits" },
      { name: "QEE optimized", qubits: "~6 qubits" }
    ],
    atoms: [
      { element: "N", x: 0.000000, y: 0.000000, z: 0.000000 },
      { element: "H", x: 0.000000, y: 0.9377, z: -0.3816 },
      { element: "H", x: 0.8121, y: -0.4688, z: -0.3816 },
      { element: "H", x: -0.8121, y: -0.4688, z: -0.3816 }
    ]
  },
  "CH4": {
    name: "CH₄",
    description: "methane",
    pythonTemplate: `# CH₄ - methane
# Basis set options: STO-3G (~10–20 qubits), 6-31G
mol = pyscf.gto.Mole()
mol.build(
    atom=[
        ["C", (0.000000, 0.000000, 0.000000)],
        ["H", (0.629118, 0.629118, 0.629118)],
        ["H", (-0.629118, -0.629118, 0.629118)],
        ["H", (-0.629118, 0.629118, -0.629118)],
        ["H", (0.629118, -0.629118, -0.629118)]
    ],  # bond ~1.09 Å, tetrahedral
    basis="sto-3g",
    spin=0,
    charge=0
)`,
    basisSets: [
      { name: "sto-3g", qubits: "~10–20 qubits" },
      { name: "6-31G", qubits: "~15–25 qubits" }
    ],
    atoms: [
      { element: "C", x: 0.000000, y: 0.000000, z: 0.000000 },
      { element: "H", x: 0.629118, y: 0.629118, z: 0.629118 },
      { element: "H", x: -0.629118, y: -0.629118, z: 0.629118 },
      { element: "H", x: -0.629118, y: 0.629118, z: -0.629118 },
      { element: "H", x: 0.629118, y: -0.629118, z: -0.629118 }
    ]
  },
  "Fe2S2": {
    name: "[2Fe–2S]",
    description: "iron-sulfur fragment",
    pythonTemplate: `# Small Fe–S fragment ([2Fe–2S] toy model, reduced active space)
# Basis set options: TZP-DKH (~45 qubits active space), can replace with minimal for demo
mol = pyscf.gto.Mole()
mol.build(
    atom=[
        ["Fe", (0.000000, 0.000000, 0.000000)],
        ["Fe", (2.7, 0.000000, 0.000000)],
        ["S", (-1.35, 2.34, 0.000000)],
        ["S", (-1.35, -2.34, 0.000000)]
    ],
    basis="tzp-dkh",
    spin=0,   # adjust depending on desired oxidation state
    charge=0
)`,
    basisSets: [
      { name: "tzp-dkh (active space)", qubits: "~45 qubits" }
    ],
    atoms: [
      { element: "Fe", x: 0.000000, y: 0.000000, z: 0.000000 },
      { element: "Fe", x: 2.7, y: 0.000000, z: 0.000000 },
      { element: "S", x: -1.35, y: 2.34, z: 0.000000 },
      { element: "S", x: -1.35, y: -2.34, z: 0.000000 }
    ]
  }
}

// Atom colors for visualization
const atomColors = {
  H: "#ffffff",
  Li: "#cc80ff",
  Be: "#c2ff00",
  C: "#909090",
  N: "#3050f8",
  O: "#ff0d0d",
  Fe: "#e06633",
  S: "#ffff30"
}

export const ChemistryNode = memo(({ id, data, isConnectable }: NodeProps<ChemistryNodeData>) => {
  const [selectedMolecule, setSelectedMolecule] = useState("H2")
  const [isInfoOpen, setIsInfoOpen] = useState(false)
  const [show3D, setShow3D] = useState(false)

  const currentMolecule = molecules[selectedMolecule as keyof typeof molecules]

  // Initialize with default H2 molecule code if no pythonCode exists
  const getDefaultPythonCode = () => {
    const molecule = molecules["H2"]
    return molecule.pythonTemplate
  }

  // Set default code immediately when component mounts
  React.useEffect(() => {
    if (data.onParameterChange && !data.pythonCode) {
      const defaultCode = `
      ${getDefaultPythonCode()}
      `
      // Set inputCode for the code generation system (this will also update nodeInputs atomically)
      data.onParameterChange(id || '', 'inputCode', defaultCode)
    }
  }, [id, data.onParameterChange, data.pythonCode])

  // Get the Python code for the currently selected molecule
  const getCurrentMoleculePythonCode = () => {
    const molecule = molecules[selectedMolecule as keyof typeof molecules]
    return molecule ? molecule.pythonTemplate : getDefaultPythonCode()
  }

  // Ensure we always have Python code available for the node
  const currentPythonCode = data.pythonCode || getDefaultPythonCode()

  const handleMoleculeChange = (value: string) => {
    setSelectedMolecule(value)
    
    const molecule = molecules[value as keyof typeof molecules]
    const moleculeCode = molecule.pythonTemplate
    
    // Trigger AI code generation by using 'molecule' parameter instead of 'inputCode'
    // This will cause the AI system to generate new code based on the selected molecule
    data.onParameterChange?.(id || '', 'molecule', value)
  }

  const renderMolecularVisualization = () => {
    if (!currentMolecule) return null

    // Calculate bounds of molecule for proper centering
    const xs = currentMolecule.atoms.map(atom => atom.x)
    const ys = currentMolecule.atoms.map(atom => atom.y)
    const minX = Math.min(...xs)
    const maxX = Math.max(...xs)
    const minY = Math.min(...ys)
    const maxY = Math.max(...ys)
    
    const width = maxX - minX
    const height = maxY - minY
    const svgWidth = 208 // Node width (256) - padding (24*2)
    const svgHeight = 120
    
    // Scale to fit in container with some padding
    const scaleX = width > 0 ? (svgWidth - 40) / width : 40
    const scaleY = height > 0 ? (svgHeight - 40) / height : 40
    const scale = Math.min(scaleX, scaleY, 40) // Max scale of 40
    
    const centerX = svgWidth / 2
    const centerY = svgHeight / 2
    const offsetX = (minX + maxX) / 2
    const offsetY = (minY + maxY) / 2
    
    return (
      <div className="bg-white">
        <div className="p-3">
          <div className="text-xs text-gray-600 mb-2 flex items-center justify-between">
            <span>Molecular Structure:</span>
            <button
              onClick={() => setShow3D(true)}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              View in 3D
            </button>
          </div>
          <div className="w-full flex justify-center">
            <svg width={svgWidth} height={svgHeight} className="border border-gray-200 rounded bg-white">
              {/* Bonds - simple lines between atoms */}
              {currentMolecule.atoms.map((atom1, i) => 
                currentMolecule.atoms.slice(i + 1).map((atom2, j) => {
                  const distance = Math.sqrt(
                    Math.pow(atom1.x - atom2.x, 2) + 
                    Math.pow(atom1.y - atom2.y, 2) + 
                    Math.pow(atom1.z - atom2.z, 2)
                  )
                  // Only draw bonds for reasonable distances (< 2.0 Å typically)
                  if (distance < 2.0) {
                    return (
                      <line
                        key={`bond-${i}-${j}`}
                        x1={centerX + (atom1.x - offsetX) * scale}
                        y1={centerY + (atom1.y - offsetY) * scale}
                        x2={centerX + (atom2.x - offsetX) * scale}
                        y2={centerY + (atom2.y - offsetY) * scale}
                        stroke="#666"
                        strokeWidth="2"
                      />
                    )
                  }
                  return null
                })
              )}
              
              {/* Atoms */}
              {currentMolecule.atoms.map((atom, index) => (
                <g key={`atom-${index}`}>
                  <circle
                    cx={centerX + (atom.x - offsetX) * scale}
                    cy={centerY + (atom.y - offsetY) * scale}
                    r="12"
                    fill={atomColors[atom.element as keyof typeof atomColors] || "#999"}
                    stroke="#333"
                    strokeWidth="1"
                  />
                  <text
                    x={centerX + (atom.x - offsetX) * scale}
                    y={centerY + (atom.y - offsetY) * scale + 4}
                    textAnchor="middle"
                    className="text-xs font-bold"
                    fill={atom.element === 'H' ? "#000" : "#fff"}
                  >
                    {atom.element}
                  </text>
                </g>
              ))}
            </svg>
          </div>
        </div>
        
        <div className="bg-white p-2 mx-3 mb-3 rounded text-xs border border-gray-200">
          <div className="font-medium mb-1 text-gray-800">Basis sets:</div>
          <div className="space-y-1 text-gray-700">
            {currentMolecule.basisSets.map((basis, index) => (
              <div key={index} className="flex justify-between items-center text-gray-700">
                <span>• {basis.name}</span>
                <span className="text-gray-600 text-xs">{basis.qubits}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // 3Dmol.js viewer reference
  const viewerRef = useRef<HTMLDivElement>(null);
  const viewerInstanceRef = useRef<any>(null);
  const rotationIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const render3DMolecularVisualization = () => {
    if (!currentMolecule) return null

    return (
      <div className="bg-white">
        <div className="p-3">
          <div className="text-xs text-gray-600 mb-2 flex items-center justify-between">
            <span>3D Molecular Structure:</span>
            <button
              onClick={() => setShow3D(false)}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              Switch to 2D
            </button>
          </div>
          <div className="w-full flex justify-center">
            <div 
              className="border border-gray-200 rounded bg-white relative"
              style={{ 
                width: 208, // Same as 2D viewer (svgWidth)
                height: 120, // Same as 2D viewer (svgHeight)
              }}
            >
              <div 
                ref={viewerRef}
                className="absolute inset-0"
                style={{ 
                  width: '100%',
                  height: '100%',
                  borderRadius: '4px'
                }}
              />
            </div>
          </div>
        </div>
        
        <div className="bg-white p-2 mx-3 mb-3 rounded text-xs border border-gray-200">
          <div className="font-medium mb-1 text-gray-800">Basis sets:</div>
          <div className="space-y-1 text-gray-700">
            {currentMolecule.basisSets.map((basis, index) => (
              <div key={index} className="flex justify-between items-center text-gray-700">
                <span>• {basis.name}</span>
                <span className="text-gray-600 text-xs">{basis.qubits}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // Initialize 3Dmol.js viewer when 3D view is shown
  useEffect(() => {
    if (show3D && viewerRef.current && !viewerInstanceRef.current) {
      const init3DMol = async () => {
        try {
          // Dynamic import only on client side
          if (typeof window === 'undefined') return
          
          const $3Dmol = await import('3dmol')
          if (!$3Dmol) return
          
          // Initialize 3Dmol viewer with maximum compatibility config
          const config = { 
            backgroundColor: 'white',
            antialias: false,
            preserveDrawingBuffer: false, // Disable to avoid OffscreenCanvas issues
            alpha: false, // Disable alpha for better compatibility
            premultipliedAlpha: false,
            depth: true,
            stencil: false
          };
          
          viewerInstanceRef.current = $3Dmol.createViewer(viewerRef.current, config);
        
          // Load molecule data
          const xyzData = getXYZData(selectedMolecule);
          viewerInstanceRef.current.addModel(xyzData, 'xyz');
          
          // Set visual style - ball and stick representation
          viewerInstanceRef.current.setStyle({}, {
            stick: { radius: 0.15 },
            sphere: { scale: 0.4 }
          });
          
          // Set background and zoom
          viewerInstanceRef.current.setBackgroundColor('white');
          viewerInstanceRef.current.zoomTo();
          viewerInstanceRef.current.zoom(3.0);
          
          // Render the molecule
          viewerInstanceRef.current.render();
          
          // Start a gentle manual rotation using safe rotate method
          let rotationAngle = 0;
          rotationIntervalRef.current = setInterval(() => {
            if (viewerInstanceRef.current) {
              try {
                rotationAngle += 1; // 1 degree per step
                viewerInstanceRef.current.rotate(1, 'y'); // Rotate 1 degree around Y axis
                viewerInstanceRef.current.render();
              } catch (error) {
                // If rotation fails, clear the interval and continue without animation
                if (rotationIntervalRef.current) {
                  clearInterval(rotationIntervalRef.current);
                  rotationIntervalRef.current = null;
                }
              }
            }
          }, 50); // Update every 50ms for smooth animation
          
        } catch (error) {
          console.error('3Dmol initialization error:', error);
          // Fallback: show error message in viewer area
          if (viewerRef.current) {
            viewerRef.current.innerHTML = `
              <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666; font-size: 12px; text-align: center; padding: 10px;">
                <div>
                  <div>3D viewer not available</div>
                  <div style="font-size: 10px; margin-top: 5px;">Please use 2D view</div>
                </div>
              </div>
            `;
          }
        }
      }
      
      init3DMol()
    } else if (!show3D && viewerInstanceRef.current) {
      // Clean up viewer when switching to 2D
      try {
        // Clear rotation interval
        if (rotationIntervalRef.current) {
          clearInterval(rotationIntervalRef.current);
          rotationIntervalRef.current = null;
        }
        // Clear viewer
        viewerInstanceRef.current.clear();
      } catch (error) {
        console.warn('3Dmol cleanup error (non-critical):', error);
      }
      viewerInstanceRef.current = null;
    }
  }, [show3D, selectedMolecule]);

  // Update molecule when selection changes in 3D mode
  useEffect(() => {
    if (show3D && viewerInstanceRef.current) {
      try {
        // Clear rotation interval first
        if (rotationIntervalRef.current) {
          clearInterval(rotationIntervalRef.current);
          rotationIntervalRef.current = null;
        }
        
        // Clear existing model
        viewerInstanceRef.current.clear();
        
        // Load new molecule
        const xyzData = getXYZData(selectedMolecule);
        viewerInstanceRef.current.addModel(xyzData, 'xyz');
        
        // Apply styling
        viewerInstanceRef.current.setStyle({}, {
          stick: { radius: 0.15 },
          sphere: { scale: 0.4 }
        });
        
        viewerInstanceRef.current.zoomTo();
        viewerInstanceRef.current.zoom(3.0);
        viewerInstanceRef.current.render();
        
        // Restart rotation animation for new molecule
        let rotationAngle = 0;
        rotationIntervalRef.current = setInterval(() => {
          if (viewerInstanceRef.current) {
            try {
              rotationAngle += 1;
              viewerInstanceRef.current.rotate(1, 'y');
              viewerInstanceRef.current.render();
            } catch (error) {
              if (rotationIntervalRef.current) {
                clearInterval(rotationIntervalRef.current);
                rotationIntervalRef.current = null;
              }
            }
          }
        }, 50);
        
      } catch (error) {
        console.error('3Dmol molecule update error:', error);
        // Don't crash, just log the error
      }
    }
  }, [selectedMolecule, show3D]);

  return (
    <Card className="w-64 border-0 shadow-md rounded-none overflow-hidden bg-white">
      <div className="bg-[#FFEFF7] h-12 flex items-center">
        <div className="w-12 h-12 bg-[#D02771] flex items-center justify-center text-white mr-2">
          <img src="/node_icons/map.svg" alt="Chemistry" width="24" height="24" className="filter brightness-0 invert" />
        </div>
        <div className="text-sm font-medium text-black flex-1 flex items-center">
          {data.label}
          {data.isUpdating && (
            <Spinner size={12} className="ml-2 text-white" />
          )}
        </div>
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
              <DialogTitle>{data.label} - {currentMolecule.name} Python Code</DialogTitle>
            </DialogHeader>
            <div className="mt-4">
              <pre className="bg-gray-900 text-green-400 p-4 rounded-md text-xs overflow-x-auto">
                <code>{getCurrentMoleculePythonCode()}</code>
              </pre>
            </div>
          </DialogContent>
        </Dialog>
      </div>
      
      <div className="bg-white">
        <div className="bg-white p-3 border-b border-[#e0e0e0]">
          <div className="text-xs text-[#666] mb-2">Molecular System</div>
          <Select value={selectedMolecule} onValueChange={handleMoleculeChange}>
            <SelectTrigger className="h-8 text-sm rounded-none bg-transparent border-0 border-b border-[#ccc] p-0 pb-1 text-[#333] font-normal focus:ring-0">
              <SelectValue placeholder="Select molecule" />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(molecules).map(([key, molecule]) => (
                <SelectItem key={key} value={key}>
                  {molecule.name} - {molecule.basisSets[0].qubits}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {data.isUpdating && (
            <div className="mt-2 text-xs text-orange-500 flex items-center">
              <Spinner size={8} className="mr-1 text-orange-500" />
              Updating...
            </div>
          )}
        </div>
        
        {selectedMolecule && (show3D ? render3DMolecularVisualization() : renderMolecularVisualization())}
      </div>

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
    </Card>
  )
})

ChemistryNode.displayName = "ChemistryNode"