/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

"use client"

import { Toast, ToastClose, ToastDescription, ToastProvider, ToastTitle, ToastViewport } from "@/components/ui/toast"
import { useToast } from "@/components/ui/use-toast"

export function Toaster() {
  const { toasts } = useToast()

  return (
    <ToastProvider>
      {toasts.map(({ id, title, description, action, ...props }) => (
        <Toast key={id} {...props}>
          <div className="grid gap-1">
            {title && <ToastTitle>{title}</ToastTitle>}
            {description && <ToastDescription>{description}</ToastDescription>}
          </div>
          {action}
          <ToastClose />
        </Toast>
      ))}
      <ToastViewport className="fixed bottom-0 left-1/2 transform -translate-x-1/2 flex flex-col p-4 gap-2 w-full max-w-md z-[100] items-center" />
    </ToastProvider>
  )
}
