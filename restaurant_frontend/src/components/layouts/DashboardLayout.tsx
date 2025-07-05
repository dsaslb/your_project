import React from "react";

export default function DashboardLayout({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="p-6">
      <h1 className="text-2xl font-bold mb-2">{title}</h1>
      {description && <p className="text-zinc-500 mb-6">{description}</p>}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {children}
      </div>
    </section>
  );
} 