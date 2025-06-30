"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface ResizableLayoutProps {
  children: React.ReactNode
  sidebar: React.ReactNode
  defaultSidebarWidth?: number
  minSidebarWidth?: number
  maxSidebarWidth?: number
  className?: string
}

export function ResizableLayout({
  children,
  sidebar,
  defaultSidebarWidth = 20,
  minSidebarWidth = 15,
  maxSidebarWidth = 40,
  className,
}: ResizableLayoutProps) {
  const [sidebarWidth, setSidebarWidth] = React.useState(defaultSidebarWidth)
  const [isResizing, setIsResizing] = React.useState(false)
  const startX = React.useRef(0)
  const startWidth = React.useRef(0)

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsResizing(true)
    startX.current = e.clientX
    startWidth.current = sidebarWidth
    document.body.style.cursor = "col-resize"
    document.body.style.userSelect = "none"
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isResizing) return

    const deltaX = e.clientX - startX.current
    const containerWidth = window.innerWidth
    const newWidthPercent = ((startWidth.current * containerWidth / 100) + deltaX) / containerWidth * 100
    const newWidth = Math.max(minSidebarWidth, Math.min(maxSidebarWidth, newWidthPercent))
    setSidebarWidth(newWidth)
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
    <div className={cn("flex min-h-screen", className)}>
      {/* Sidebar */}
      <div 
        className="border-r bg-background"
        style={{ width: `${sidebarWidth}%`, minWidth: "200px" }}
      >
        {sidebar}
      </div>
      
      {/* Resize Handle */}
      <div
        className="w-1 cursor-col-resize bg-border hover:bg-primary/50 transition-colors"
        onMouseDown={handleMouseDown}
      />
      
      {/* Main Content */}
      <div 
        className="flex-1"
        style={{ width: `${100 - sidebarWidth}%` }}
      >
        {children}
      </div>
    </div>
  )
} 