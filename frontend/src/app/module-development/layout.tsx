import React from 'react';
import ModuleDevelopmentNav from '@/components/navigation/ModuleDevelopmentNav';

export default function ModuleDevelopmentLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <ModuleDevelopmentNav />
      <main className="flex-1">
        {children}
      </main>
    </div>
  );
} 