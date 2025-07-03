import * as React from "react"
import { cn } from "@/lib/utils"

export function Card({ className, role, "aria-labelledby": ariaLabelledby, ...props }: React.HTMLAttributes<HTMLDivElement> & { role?: string; "aria-labelledby"?: string }) {
  return (
    <div className={cn("rounded-xl border bg-card text-card-foreground shadow", className)} role={role} aria-labelledby={ariaLabelledby} {...props} />
  )
}

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("p-4 border-b bg-gray-50 dark:bg-gray-800 rounded-t-xl", className)} {...props} />
  )
)
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<HTMLHeadingElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3 ref={ref} className={cn("text-lg font-semibold leading-none tracking-tight", className)} {...props} />
  )
)
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p ref={ref} className={cn("text-sm text-gray-500 dark:text-gray-400", className)} {...props} />
  )
)
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("p-4", className)} {...props} />
  )
)
CardContent.displayName = "CardContent"

export { CardHeader, CardTitle, CardDescription, CardContent } 