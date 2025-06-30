"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface ResizableTableProps {
  children: React.ReactNode
  className?: string
  minWidth?: number
  maxWidth?: number
}

export function ResizableTable({
  children,
  className,
  minWidth = 600,
  maxWidth = 1200,
}: ResizableTableProps) {
  const [width, setWidth] = React.useState(800)
  const [isResizing, setIsResizing] = React.useState(false)
  const startX = React.useRef(0)
  const startWidth = React.useRef(0)

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsResizing(true)
    startX.current = e.clientX
    startWidth.current = width
    document.body.style.cursor = "col-resize"
    document.body.style.userSelect = "none"
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isResizing) return

    const deltaX = e.clientX - startX.current
    const newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth.current + deltaX))
    setWidth(newWidth)
  }

  const handleMouseUp = () => {
    setIsResizing(false)
    document.body.style.cursor = ""
    document.body.style.userSelect = ""
  }

  React.useEffect(() => {
    if (isResizing) {
      document.addEventListener("mousemove", handleMouseMove)
      document.addEventListener("mouseup", handleMouseUp)
      return () => {
        document.removeEventListener("mousemove", handleMouseMove)
        document.removeEventListener("mouseup", handleMouseUp)
      }
    }
  }, [isResizing])

  return (
    <div
      className={cn("relative overflow-x-auto rounded-lg border", className)}
      style={{ width: `${width}px` }}
    >
      {children}
      <div
        className="absolute right-0 top-0 h-full w-1 cursor-col-resize bg-border hover:bg-primary/50 transition-colors"
        onMouseDown={handleMouseDown}
      />
    </div>
  )
} 