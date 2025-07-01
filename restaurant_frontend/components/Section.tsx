import React from "react";

interface SectionProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
  headerRight?: React.ReactNode;
}

export function Section({ title, children, className = "", headerRight }: SectionProps) {
  return (
    <section className={`mb-8 rounded-lg border bg-card ${className}`}>
      {(title || headerRight) && (
        <div className="flex items-center justify-between px-6 pt-6 pb-2 border-b">
          {title && <h2 className="text-lg font-semibold">{title}</h2>}
          {headerRight}
        </div>
      )}
      <div className="p-6">{children}</div>
    </section>
  );
} 