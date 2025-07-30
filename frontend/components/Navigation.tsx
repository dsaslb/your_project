'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Building2, 
  Store, 
  Users, 
  User, 
  Settings, 
  Activity, 
  Home,
  BarChart3,
  Package,
  FileText,
  Bell,
  HelpCircle,
  ChevronDown,
  Zap,
  DollarSign,
  AlertTriangle,
  ShoppingCart,
  Calendar,
  UserCheck,
  TrendingUp
} from 'lucide-react';

interface SidebarItem {
  title: string;
  icon?: React.ReactNode;
  href?: string;
  children?: SidebarItem[];
  badge?: string | number;
}

export default function Navigation() {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const pathname = usePathname();

  const menuItems: SidebarItem[] = [
    {
      title: '퀀텀 대시보드',
      icon: <Home className="w-4 h-4" />,
      href: '/dashboard'
    },
    {
      title: '계층별 대시보드',
      icon: <Building2 className="w-4 h-4" />,
      children: [
        { title: 'Admin 대시보드', href: '/dashboard' },
        { title: '브랜드 대시보드', href: '/brand-dashboard/1' },
        { title: '매장 대시보드', href: '/store-dashboard' },
        { title: '직원 대시보드', href: '/employee-dashboard' }
      ]
    },
    {
      title: '브랜드 관리',
      icon: <Building2 className="w-4 h-4" />,
      children: [
        { title: '브랜드 목록', href: '/brands' },
        { title: '브랜드 분석', href: '/brands/analytics' },
        { title: '브랜드별 매출', href: '/brand-dashboard/1/sales' },
        { title: '브랜드별 개선요청', href: '/brand-dashboard/1/improvements' },
        { title: '브랜드 설정', href: '/brands/settings' }
      ]
    },
    {
      title: '업종 관리',
      icon: <BarChart3 className="w-4 h-4" />,
      children: [
        { title: '업종 목록', href: '/industries' },
        { title: '업종 분석', href: '/industries/analytics' }
      ]
    },
    {
      title: '매장 운영',
      icon: <Store className="w-4 h-4" />,
      children: [
        { title: '매장 관리자 대시보드', href: '/manager-dashboard' },
        { title: '주문 관리', href: '/orders', badge: 'New' },
        { title: '재고 관리', href: '/inventory' },
        { title: '직원 관리', href: '/staff' },
        { title: '근무표 관리', href: '/schedule' }
      ]
    },
    {
      title: '업무 관리',
      icon: <Calendar className="w-4 h-4" />,
      children: [
        { title: '출근 관리', href: '/attendance' },
        { title: '청소 관리', href: '/cleaning' },
        { title: '발주 관리', href: '/purchase' }
      ]
    },
    {
      title: '직원 기능',
      icon: <Users className="w-4 h-4" />,
      children: [
        { title: '내 근무표', href: '/schedule' },
        { title: '출근 기록', href: '/attendance' }
      ]
    },
    {
      title: '시스템 관리',
      icon: <Settings className="w-4 h-4" />,
      children: [
        { title: '관리자 대시보드', href: '/dashboard' },
        { title: '브랜드 관리', href: '/admin/brand-management' },
        { title: '매장 관리', href: '/admin/store-management' },
        { title: '직원 관리', href: '/admin/employee-management' }
      ]
    },
    {
      title: '고급 기능',
      icon: <BarChart3 className="w-4 h-4" />,
      children: [
        { title: '모듈 마켓플레이스', href: '/admin/module-marketplace' },
        { title: '플러그인 관리', href: '/admin/plugin-management' },
        { title: '피드백 관리', href: '/admin/feedback-management' }
      ]
    },
    {
      title: '시스템 모니터링',
      icon: <Activity className="w-4 h-4" />,
      children: [
        { title: '실시간 상태', href: '/monitoring/status' },
        { title: '성능 지표', href: '/monitoring/performance' },
        { title: '알림 관리', href: '/monitoring/alerts' },
        { title: '운영 리포트/경고', href: '/enhanced-alerts' },
        { title: '연동 상태 확인', href: '/industry-admin/integration-status' }
      ]
    },
    {
      title: '퀀텀 플러그인',
      icon: <Package className="w-4 h-4" />,
      children: [
        { title: '플러그인 마켓', href: '/plugins/marketplace' },
        { title: '설치된 플러그인', href: '/plugins/installed' },
        { title: '모듈/플러그인 관리', href: '/admin/module-management' }
      ]
    },
    {
      title: '보고서',
      icon: <FileText className="w-4 h-4" />,
      children: [
        { title: '매출 보고서', href: '/reports/sales' },
        { title: '성과 보고서', href: '/reports/performance' },
        { title: '전체 통계', href: '/admin/reports' }
      ]
    },
    {
      title: '공통 기능',
      icon: <Settings className="w-4 h-4" />,
      children: [
        { title: '알림', href: '/notifications' },
        { title: '설정', href: '/settings' },
        { title: '도움말', href: '/help' }
      ]
    }
  ];

  const toggleItem = (title: string) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(title)) {
        newSet.delete(title);
      } else {
        newSet.add(title);
      }
      return newSet;
    });
  };

  const renderMenuItem = (item: SidebarItem, level: number = 0) => {
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems.has(item.title);
    const isActive = item.href ? pathname === item.href : false;

    if (hasChildren) {
      return (
        <div key={item.title}>
          <div
            className={`flex items-center justify-between px-4 py-3 text-sm font-medium rounded-lg cursor-pointer transition-all duration-300 border border-transparent hover:bg-cyan-500/10 hover:text-cyan-400 hover:border-cyan-500/30 ${
              level > 0 ? 'ml-4' : ''
            }`}
            onClick={() => toggleItem(item.title)}
          >
            <div className="flex items-center space-x-3">
              <div className="text-cyan-400">{item.icon}</div>
              <span className="text-white">{item.title}</span>
              {item.badge && (
                <span className="px-2 py-1 text-xs bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-full animate-pulse">
                  {item.badge}
                </span>
              )}
            </div>
            <ChevronDown
              className={`w-4 h-4 transition-transform duration-300 text-cyan-400 ${
                isExpanded ? 'rotate-180' : ''
              }`}
            />
          </div>
          
          {isExpanded && (
            <div className="mt-2 space-y-1 ml-4 border-l border-cyan-500/30 pl-4">
              {item.children!.map(child => renderMenuItem(child, level + 1))}
            </div>
          )}
        </div>
      );
    }

    return (
      <Link key={item.title} href={item.href || '#'} className="block">
        <div
          className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg cursor-pointer transition-all duration-300 border border-transparent hover:bg-cyan-500/10 hover:text-cyan-400 hover:border-cyan-500/30 ${
            level > 0 ? 'ml-4' : ''
          } ${isActive ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-400 border-cyan-500/50 shadow-lg shadow-cyan-500/25' : ''}`}
        >
          <div className="flex items-center space-x-3">
            <div className={`transition-colors duration-300 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`}>
              {item.icon}
            </div>
            <span className="text-white">{item.title}</span>
            {item.badge && (
              <span className="px-2 py-1 text-xs bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-full animate-pulse">
                {item.badge}
              </span>
            )}
          </div>
        </div>
      </Link>
    );
  };

  return (
    <div className="w-80 bg-black/90 backdrop-blur-xl border-r border-cyan-500/20 min-h-screen">
      {/* 사이드바 헤더 */}
      <div className="p-6 border-b border-cyan-500/20">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 to-purple-600 shadow-lg shadow-cyan-500/25 animate-pulse">
            <Zap className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">
              멀티테넌시<br/>관리 시스템
            </h2>
            <p className="text-xs text-slate-400">퀀텀 네비게이터</p>
          </div>
        </div>
      </div>

      {/* 사이드바 메뉴 */}
      <div className="p-4 overflow-y-auto h-[calc(100vh-200px)]">
        <nav className="space-y-2">
          {menuItems.map(item => renderMenuItem(item))}
        </nav>
      </div>

      {/* 사이드바 푸터 */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-cyan-500/20">
        <div className="text-xs text-slate-500 text-center">
          © 2024 퀀텀 시스템 v2.0
        </div>
      </div>
    </div>
  );
} 