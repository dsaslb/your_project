'use client';

import { useState } from 'react';
import Sidebar, { SidebarToggle } from './Sidebar';

interface LayoutWrapperProps {
  children: React.ReactNode;
}

export function LayoutWrapper({ children }: LayoutWrapperProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-black text-white relative overflow-hidden">
      {/* 배경 효과 */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(120,119,198,0.3),transparent_50%)]"></div>
      <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(68,68,68,0.2)_50%,transparent_75%)] bg-[length:20px_20px]"></div>
      
      {/* 상단 네온 라인 */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-60"></div>
      
      {/* 사이드바 */}
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      
      {/* 모바일 토글 버튼 */}
      <SidebarToggle onToggle={() => setSidebarOpen(!sidebarOpen)} />
      
      {/* 메인 콘텐츠 */}
      <div className="flex-1 lg:ml-64">
        {children}
      </div>
      
      {/* 하단 네온 라인 */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-400 to-transparent opacity-60"></div>
    </div>
  );
} 