'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Building2, 
  Store, 
  Users, 
  User, 
  Menu,
  X,
  Home,
  BarChart3,
  Settings
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const menuItems = [
  {
    title: '대시보드',
    href: '/dashboard',
    icon: <Home className="w-5 h-5" />,
    description: '시스템 현황 및 통계'
  },
  {
    title: '업종 관리',
    href: '/industry-management',
    icon: <Building2 className="w-5 h-5" />,
    description: '업종별 관리'
  },
  {
    title: '브랜드 관리',
    href: '/brand-management',
    icon: <Store className="w-5 h-5" />,
    description: '브랜드별 관리'
  },
  {
    title: '매장 관리',
    href: '/store-management',
    icon: <Store className="w-5 h-5" />,
    description: '매장별 관리'
  },
  {
    title: '직원 관리',
    href: '/staff',
    icon: <Users className="w-5 h-5" />,
    description: '직원별 관리'
  },
  {
    title: '분석',
    href: '/analytics',
    icon: <BarChart3 className="w-5 h-5" />,
    description: '데이터 분석'
  },
  {
    title: '설정',
    href: '/settings',
    icon: <Settings className="w-5 h-5" />,
    description: '시스템 설정'
  }
];

export default function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* 모바일 오버레이 */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* 사이드바 */}
      <div className={cn(
        "fixed left-0 top-0 z-50 h-full w-64 bg-gradient-to-b from-slate-900/95 to-slate-800/95 backdrop-blur-xl border-r border-slate-700/50 transition-transform duration-300 ease-in-out",
        isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      )}>
        {/* 헤더 */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Building2 className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-white">퀀텀 관리</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="lg:hidden text-slate-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* 네비게이션 메뉴 */}
        <nav className="p-4 space-y-2">
          {menuItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 group",
                  isActive 
                    ? "bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-400 border border-cyan-500/30" 
                    : "text-slate-300 hover:bg-slate-700/50 hover:text-white"
                )}
                onClick={() => {
                  // 모바일에서 메뉴 클릭 시 사이드바 닫기
                  if (window.innerWidth < 1024) {
                    onToggle();
                  }
                }}
              >
                <div className={cn(
                  "transition-colors duration-200",
                  isActive ? "text-cyan-400" : "text-slate-400 group-hover:text-white"
                )}>
                  {item.icon}
                </div>
                <div className="flex-1">
                  <div className="font-medium text-sm">{item.title}</div>
                  <div className="text-xs text-slate-500 group-hover:text-slate-300">
                    {item.description}
                  </div>
                </div>
              </Link>
            );
          })}
        </nav>

        {/* 하단 정보 */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-700/50">
          <div className="text-center">
            <div className="text-xs text-slate-500 mb-1">퀀텀 멀티테넌시</div>
            <div className="text-xs text-slate-600">v1.0.0</div>
          </div>
        </div>
      </div>
    </>
  );
}

// 모바일 토글 버튼 컴포넌트
export function SidebarToggle({ onToggle }: { onToggle: () => void }) {
  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={onToggle}
      className="lg:hidden fixed top-4 left-4 z-50 bg-slate-800/80 backdrop-blur-sm border border-slate-700/50 text-slate-300 hover:text-white hover:bg-slate-700/80"
    >
      <Menu className="w-5 h-5" />
    </Button>
  );
}
