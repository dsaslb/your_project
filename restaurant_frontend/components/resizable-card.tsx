"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface ResizableCardProps {
  children: React.ReactNode
  className?: string
  defaultSize?: number
  minSize?: number
  maxSize?: number
  direction?: "horizontal" | "vertical"
}

export function ResizableCard({
  children,
  className,
  defaultSize = 50,
  minSize = 20,
  maxSize = 80,
  direction = "horizontal",
}: ResizableCardProps) {
  return (
    <div className={cn(
      "rounded-lg border bg-card p-6",
      direction === "vertical" ? "min-h-[200px]" : "min-w-[300px]",
      className
    )}>
      {children}
    </div>
  )
} 