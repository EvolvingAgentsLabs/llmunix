/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

import { QuantumComposer } from "@/components/quantum-composer"
import "@/lib/debug-utils"

export default function Home() {
  return (
    <main className="min-h-screen">
      <QuantumComposer />
    </main>
  )
}
