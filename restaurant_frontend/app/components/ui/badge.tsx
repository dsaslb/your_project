import * as React from "react";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Badge({ className = "", ...props }: BadgeProps) {
  return (
    <div
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200 ${className}`}
      {...props}
    />
  );
} 