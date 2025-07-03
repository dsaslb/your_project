import * as React from "react";

export function ScrollArea({ children, className = "", ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`overflow-auto max-h-96 ${className}`} {...props}>
      {children}
    </div>
  );
} 