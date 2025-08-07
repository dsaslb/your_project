'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Building2, 
  Store, 
  Users, 
  Menu,
  X,
  Home,
  Settings,
  Package,
  ShoppingCart,
  Calendar,
  UserCheck,
  BarChart3,
  Truck,
  Megaphone,
  Shield,
  FileText,
  Bell,
  Activity,
  Save,
  Key,
  Route,
  Network,
  Inbox,
  Database,
  BookOpen,
  ChevronUp,
  ChevronDown
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const menuItems = [
  {
    title: '관리자 대시보드',
    href: '/admin-dashboard',
    icon: <Settings className="w-5 h-5" />,
    description: '전체 시스템 관리'
  },
  {
    title: '대시보드',
    href: '/dashboard',
    icon: <Home className="w-5 h-5" />,
    description: '시스템 현황 및 통계'
  },
  {
    title: '업종 관리자',
    href: '/industry-admin',
    icon: <Building2 className="w-5 h-5" />,
    description: '업종별 관리'
  },
  {
    title: '브랜드 관리자',
    href: '/brand-admin',
    icon: <Store className="w-5 h-5" />,
    description: '브랜드별 관리'
  },
  {
    title: '매장 관리자',
    href: '/branch-admin',
    icon: <Store className="w-5 h-5" />,
    description: '매장별 관리'
  },
  {
    title: '직원 대시보드',
    href: '/staff',
    icon: <Users className="w-5 h-5" />,
    description: '직원별 관리'
  },
  {
    title: '재고 관리',
    href: '/inventory-management',
    icon: <Package className="w-5 h-5" />,
    description: '재고 및 발주 관리'
  },
  {
    title: '주문 관리',
    href: '/order-management',
    icon: <ShoppingCart className="w-5 h-5" />,
    description: '주문 및 고객 관리'
  },
  {
    title: '스케줄 관리',
    href: '/schedule',
    icon: <Calendar className="w-5 h-5" />,
    description: '스케줄 관리'
  },
  {
    title: '고객 관리',
    href: '/customer-management',
    icon: <UserCheck className="w-5 h-5" />,
    description: '고객 정보 관리'
  },
  {
    title: '매출 분석',
    href: '/sales-analytics',
    icon: <BarChart3 className="w-5 h-5" />,
    description: '매출 데이터 분석'
  },
  {
    title: '공급업체 관리',
    href: '/supplier-management',
    icon: <Truck className="w-5 h-5" />,
    description: '공급업체 및 계약 관리'
  },
  {
    title: '마케팅 관리',
    href: '/marketing-management',
    icon: <Megaphone className="w-5 h-5" />,
    description: '프로모션 및 캠페인 관리'
  },
  {
    title: '품질 관리',
    href: '/quality-management',
    icon: <Shield className="w-5 h-5" />,
    description: '품질 이슈 및 만족도 관리'
  },
  {
    title: '보고서',
    href: '/reports',
    icon: <FileText className="w-5 h-5" />,
    description: '비즈니스 리포트 생성'
  },
  {
    title: '알림',
    href: '/notifications',
    icon: <Bell className="w-5 h-5" />,
    description: '실시간 알림 관리'
  },
  {
    title: '보안',
    href: '/security',
    icon: <Shield className="w-5 h-5" />,
    description: '보안 관리 및 모니터링'
  },
  {
    title: '백업',
    href: '/backup',
    icon: <Save className="w-5 h-5" />,
    description: '데이터 백업 및 복구'
  },
  {
    title: '모니터링',
    href: '/monitoring',
    icon: <Activity className="w-5 h-5" />,
    description: '시스템 모니터링'
  },
  {
    title: '인증 관리',
    href: '/auth',
    icon: <Key className="w-5 h-5" />,
    description: '사용자 인증 및 권한 관리'
  },
  {
    title: '데이터 분석',
    href: '/analytics',
    icon: <BarChart3 className="w-5 h-5" />,
    description: '고급 데이터 분석 및 인사이트'
  },
  {
    title: 'API 게이트웨이',
    href: '/gateway',
    icon: <Route className="w-5 h-5" />,
    description: 'API 라우팅 및 관리'
  },
  {
    title: '로드 밸런서',
    href: '/load-balancer',
    icon: <Network className="w-5 h-5" />,
    description: '서버 부하 분산 관리'
  },
  {
    title: '시스템 설정',
    href: '/system-settings',
    icon: <Settings className="w-5 h-5" />,
    description: '애플리케이션 설정 관리'
  },
  {
    title: '설정',
    href: '/settings',
    icon: <Settings className="w-5 h-5" />,
    description: '사용자 설정'
  },
  {
    title: '메시지 큐',
    href: '/message-queue',
    icon: <Inbox className="w-5 h-5" />,
    description: '비동기 작업 및 이벤트 큐 관리'
  },
  {
    title: '캐시 관리',
    href: '/cache',
    icon: <Database className="w-5 h-5" />,
    description: '메모리 및 디스크 캐시 관리'
  },
  {
    title: 'API 문서',
    href: '/api-docs',
    icon: <BookOpen className="w-5 h-5" />,
    description: 'OpenAPI 스펙 및 문서 관리'
  }
];

export default function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const pathname = usePathname();
  const [showScrollIndicator, setShowScrollIndicator] = useState(false);
  const [canScrollUp, setCanScrollUp] = useState(false);
  const [canScrollDown, setCanScrollDown] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    setShowScrollIndicator(scrollHeight > clientHeight);
    setCanScrollUp(scrollTop > 0);
    setCanScrollDown(scrollTop < scrollHeight - clientHeight - 1);
    
    // 스크롤 진행률 계산
    const maxScroll = scrollHeight - clientHeight;
    const progress = maxScroll > 0 ? (scrollTop / maxScroll) * 100 : 0;
    setScrollProgress(progress);
  };

  const scrollToTop = () => {
    const navElement = document.querySelector('.sidebar-nav');
    if (navElement) {
      navElement.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const scrollToBottom = () => {
    const navElement = document.querySelector('.sidebar-nav');
    if (navElement) {
      navElement.scrollTo({ top: navElement.scrollHeight, behavior: 'smooth' });
    }
  };

  // 컴포넌트 마운트 시 스크롤 상태 확인
  useEffect(() => {
    const checkScrollable = () => {
      const navElement = document.querySelector('.sidebar-nav');
      if (navElement) {
        const { scrollHeight, clientHeight } = navElement as HTMLElement;
        setShowScrollIndicator(scrollHeight > clientHeight);
      }
    };

    // 약간의 지연 후 체크 (DOM이 완전히 렌더링된 후)
    const timer = setTimeout(checkScrollable, 100);
    return () => clearTimeout(timer);
  }, []);

  // 키보드 네비게이션
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      
      const navElement = document.querySelector('.sidebar-nav');
      if (!navElement) return;

      switch (e.key) {
        case 'Home':
          e.preventDefault();
          navElement.scrollTo({ top: 0, behavior: 'smooth' });
          break;
        case 'End':
          e.preventDefault();
          navElement.scrollTo({ top: navElement.scrollHeight, behavior: 'smooth' });
          break;
        case 'PageUp':
          e.preventDefault();
          navElement.scrollBy({ top: -navElement.clientHeight, behavior: 'smooth' });
          break;
        case 'PageDown':
          e.preventDefault();
          navElement.scrollBy({ top: navElement.clientHeight, behavior: 'smooth' });
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

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
        "fixed left-0 top-0 z-50 h-full w-64 bg-gradient-to-b from-slate-900/95 to-slate-800/95 backdrop-blur-xl border-r border-slate-700/50 transition-transform duration-300 ease-in-out flex flex-col",
        isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      )}>
        {/* 헤더 */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700/50 flex-shrink-0">
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

        {/* 네비게이션 메뉴 - 스크롤 가능 */}
        <div 
          className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-slate-800 relative sidebar-nav"
          onScroll={handleScroll}
          title={showScrollIndicator ? "스크롤하여 더 많은 메뉴를 확인하세요" : ""}
        >
          {/* 스크롤 버튼 - 상단 */}
          {showScrollIndicator && canScrollUp && (
            <div className="absolute top-2 right-2 z-20">
              <Button
                variant="ghost"
                size="sm"
                onClick={scrollToTop}
                className="w-6 h-6 p-0 bg-slate-800/80 backdrop-blur-sm border border-slate-700/50 text-slate-300 hover:text-white hover:bg-slate-700/80"
              >
                <ChevronUp className="w-3 h-3" />
              </Button>
            </div>
          )}
          
          {/* 스크롤 버튼 - 하단 */}
          {showScrollIndicator && canScrollDown && (
            <div className="absolute bottom-2 right-2 z-20">
              <Button
                variant="ghost"
                size="sm"
                onClick={scrollToBottom}
                className="w-6 h-6 p-0 bg-slate-800/80 backdrop-blur-sm border border-slate-700/50 text-slate-300 hover:text-white hover:bg-slate-700/80"
              >
                <ChevronDown className="w-3 h-3" />
              </Button>
            </div>
          )}
          
          {/* 스크롤 인디케이터 - 상단 */}
          {showScrollIndicator && (
            <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-b from-slate-800/50 to-transparent pointer-events-none z-10">
              {canScrollUp && (
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-cyan-400 rounded-full animate-pulse"></div>
              )}
            </div>
          )}
          
          {/* 스크롤 인디케이터 - 하단 */}
          {showScrollIndicator && (
            <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-t from-slate-800/50 to-transparent pointer-events-none z-10">
              {canScrollDown && (
                <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-cyan-400 rounded-full animate-pulse"></div>
              )}
            </div>
          )}
          
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
        </div>

        {/* 하단 정보 */}
        <div className="p-4 border-t border-slate-700/50 flex-shrink-0">
          <div className="text-center">
            <div className="text-xs text-slate-500 mb-1">퀀텀 멀티테넌시</div>
            <div className="text-xs text-slate-600 mb-2">v1.0.0</div>
            {showScrollIndicator && (
              <div className="text-xs text-slate-500">
                {menuItems.length}개 메뉴 항목
                <div className="mt-1 w-full bg-slate-700/50 rounded-full h-1">
                  <div 
                    className="bg-gradient-to-r from-cyan-500 to-purple-600 h-1 rounded-full transition-all duration-200"
                    style={{ width: `${scrollProgress}%` }}
                  ></div>
                </div>
              </div>
            )}
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
