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

export const ResizableCard = ({
  children,
  className,
  defaultSize = 50,
  minSize = 20,
  maxSize = 80,
  direction = "horizontal",
}: ResizableCardProps) => {
  return (
    <div className={cn(
      "rounded-lg border bg-white dark:bg-gray-900 shadow flex flex-col justify-between transition-all duration-200",
      direction === "vertical" ? "min-h-[200px]" : "min-w-[300px]",
      className
    )}>
      {children}
    </div>
  )
}

ResizableCard.Content = function Content({ children, className, ...props }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("p-6 flex flex-col gap-2", className)} {...props}>{children}</div>;
};
ResizableCard.Header = function Header({ children, className, ...props }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("mb-2 flex flex-col gap-1", className)} {...props}>{children}</div>;
};
ResizableCard.Title = function Title({ children, className, ...props }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("text-lg font-bold", className)} {...props}>{children}</div>;
};
ResizableCard.Description = function Description({ children, className, ...props }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("text-sm text-gray-500", className)} {...props}>{children}</div>;
}; 