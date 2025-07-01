import React from "react";

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  color?: string; // tailwind 색상 클래스
  badge?: React.ReactNode;
  description?: string;
  className?: string;
}

export function StatCard({
  title,
  value,
  icon,
  color = "text-primary",
  badge,
  description,
  className = "",
}: StatCardProps) {
  return (
    <div className={`rounded-lg border bg-card p-6 flex flex-col items-start shadow-sm ${className}`}>
      <div className="flex items-center gap-2 mb-1">
        {icon && <span className="text-xl">{icon}</span>}
        <span className="text-muted-foreground text-xs">{title}</span>
        {badge && <span className="ml-2">{badge}</span>}
      </div>
      <span className={`text-3xl font-bold ${color}`}>{value}</span>
      {description && <span className="text-xs text-muted-foreground mt-2">{description}</span>}
    </div>
  );
} 