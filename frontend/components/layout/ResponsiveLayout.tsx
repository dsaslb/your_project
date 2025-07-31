/**
 * 📱 ResponsiveLayout 컴포넌트
 * 
 * 모바일 우선 반응형 레이아웃을 제공하는 컴포넌트입니다.
 */

import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Menu, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

// 브레이크포인트 정의
const BREAKPOINTS = {
  xs: 320,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;

// 레이아웃 인터페이스
export interface ResponsiveLayoutProps {
  children: React.ReactNode;
  sidebar?: React.ReactNode;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  sidebarCollapsed?: boolean;
  onSidebarToggle?: (collapsed: boolean) => void;
  className?: string;
  sidebarClassName?: string;
  mainClassName?: string;
  headerClassName?: string;
  footerClassName?: string;
}

// ResponsiveLayout 컴포넌트
export const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({
  children,
  sidebar,
  header,
  footer,
  sidebarCollapsed = false,
  onSidebarToggle,
  className,
  sidebarClassName,
  mainClassName,
  headerClassName,
  footerClassName,
}) => {
  const [isMobile, setIsMobile] = useState(false);
  const [isTablet, setIsTablet] = useState(false);
  const [isDesktop, setIsDesktop] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(sidebarCollapsed);

  // 화면 크기 감지
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      setIsMobile(width < BREAKPOINTS.md);
      setIsTablet(width >= BREAKPOINTS.md && width < BREAKPOINTS.lg);
      setIsDesktop(width >= BREAKPOINTS.lg);
      
      // 데스크톱에서는 사이드바 자동 열기
      if (width >= BREAKPOINTS.lg) {
        setSidebarOpen(true);
      } else {
        setSidebarOpen(false);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // 사이드바 토글
  const toggleSidebar = () => {
    if (isDesktop) {
      const newCollapsed = !collapsed;
      setCollapsed(newCollapsed);
      onSidebarToggle?.(newCollapsed);
    } else {
      setSidebarOpen(!sidebarOpen);
    }
  };

  // 모바일에서 사이드바 닫기
  const closeSidebar = () => {
    if (isMobile) {
      setSidebarOpen(false);
    }
  };

  return (
    <div className={cn('flex h-screen bg-gray-50 dark:bg-gray-900', className)}>
      {/* 모바일 오버레이 */}
      {isMobile && sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={closeSidebar}
          aria-hidden="true"
        />
      )}

      {/* 사이드바 */}
      {sidebar && (
        <aside
          className={cn(
            // 기본 스타일
            'flex flex-col bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700',
            'transition-all duration-300 ease-in-out',
            
            // 데스크톱 스타일
            'lg:relative lg:translate-x-0',
            collapsed ? 'lg:w-16' : 'lg:w-64',
            
            // 모바일/태블릿 스타일
            'fixed inset-y-0 left-0 z-50 w-64 transform',
            sidebarOpen ? 'translate-x-0' : '-translate-x-full',
            
            sidebarClassName
          )}
          role="complementary"
          aria-label="사이드바 네비게이션"
        >
          {/* 사이드바 헤더 */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            {!collapsed && (
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Your Program
              </h2>
            )}
            
            {/* 토글 버튼 */}
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleSidebar}
              className="lg:flex"
              aria-label={collapsed ? '사이드바 펼치기' : '사이드바 접기'}
            >
              {isDesktop ? (
                collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />
              ) : (
                <X className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* 사이드바 콘텐츠 */}
          <div className="flex-1 overflow-y-auto">
            {sidebar}
          </div>
        </aside>
      )}

      {/* 메인 콘텐츠 */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* 헤더 */}
        {header && (
          <header
            className={cn(
              'flex items-center justify-between p-4 bg-white dark:bg-gray-800',
              'border-b border-gray-200 dark:border-gray-700',
              'sticky top-0 z-30',
              headerClassName
            )}
            role="banner"
          >
            {/* 모바일 메뉴 버튼 */}
            {sidebar && isMobile && (
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleSidebar}
                className="lg:hidden"
                aria-label="메뉴 열기"
              >
                <Menu className="h-4 w-4" />
              </Button>
            )}

            {/* 헤더 콘텐츠 */}
            <div className="flex-1">
              {header}
            </div>
          </header>
        )}

        {/* 메인 콘텐츠 영역 */}
        <main
          className={cn(
            'flex-1 overflow-y-auto p-4',
            'focus:outline-none',
            mainClassName
          )}
          role="main"
          tabIndex={-1}
        >
          {children}
        </main>

        {/* 푸터 */}
        {footer && (
          <footer
            className={cn(
              'p-4 bg-white dark:bg-gray-800',
              'border-t border-gray-200 dark:border-gray-700',
              footerClassName
            )}
            role="contentinfo"
          >
            {footer}
          </footer>
        )}
      </div>
    </div>
  );
};

// 반응형 컨테이너 컴포넌트
export interface ResponsiveContainerProps {
  children: React.ReactNode;
  maxWidth?: keyof typeof BREAKPOINTS;
  padding?: 'none' | 'sm' | 'default' | 'lg' | 'xl';
  className?: string;
}

export const ResponsiveContainer: React.FC<ResponsiveContainerProps> = ({
  children,
  maxWidth = '2xl',
  padding = 'default',
  className,
}) => {
  const maxWidthClasses = {
    xs: 'max-w-xs',
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
  };

  const paddingClasses = {
    none: '',
    sm: 'px-2 sm:px-4',
    default: 'px-4 sm:px-6 lg:px-8',
    lg: 'px-6 sm:px-8 lg:px-12',
    xl: 'px-8 sm:px-12 lg:px-16',
  };

  return (
    <div
      className={cn(
        'mx-auto w-full',
        maxWidthClasses[maxWidth],
        paddingClasses[padding],
        className
      )}
    >
      {children}
    </div>
  );
};

// 반응형 그리드 컴포넌트
export interface ResponsiveGridProps {
  children: React.ReactNode;
  cols?: {
    xs?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  gap?: 'none' | 'sm' | 'default' | 'lg' | 'xl';
  className?: string;
}

export const ResponsiveGrid: React.FC<ResponsiveGridProps> = ({
  children,
  cols = { xs: 1, sm: 2, md: 3, lg: 4, xl: 5 },
  gap = 'default',
  className,
}) => {
  const gapClasses = {
    none: '',
    sm: 'gap-2',
    default: 'gap-4',
    lg: 'gap-6',
    xl: 'gap-8',
  };

  const gridColsClasses = {
    xs: `grid-cols-${cols.xs || 1}`,
    sm: `sm:grid-cols-${cols.sm || cols.xs || 1}`,
    md: `md:grid-cols-${cols.md || cols.sm || cols.xs || 1}`,
    lg: `lg:grid-cols-${cols.lg || cols.md || cols.sm || cols.xs || 1}`,
    xl: `xl:grid-cols-${cols.xl || cols.lg || cols.md || cols.sm || cols.xs || 1}`,
  };

  return (
    <div
      className={cn(
        'grid',
        gridColsClasses.xs,
        gridColsClasses.sm,
        gridColsClasses.md,
        gridColsClasses.lg,
        gridColsClasses.xl,
        gapClasses[gap],
        className
      )}
    >
      {children}
    </div>
  );
};

// 반응형 스택 컴포넌트
export interface ResponsiveStackProps {
  children: React.ReactNode;
  direction?: 'vertical' | 'horizontal';
  spacing?: 'none' | 'sm' | 'default' | 'lg' | 'xl';
  align?: 'start' | 'center' | 'end' | 'stretch';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around';
  className?: string;
}

export const ResponsiveStack: React.FC<ResponsiveStackProps> = ({
  children,
  direction = 'vertical',
  spacing = 'default',
  align = 'start',
  justify = 'start',
  className,
}) => {
  const directionClasses = {
    vertical: 'flex-col',
    horizontal: 'flex-row',
  };

  const spacingClasses = {
    none: '',
    sm: 'space-y-2 sm:space-y-0 sm:space-x-2',
    default: 'space-y-4 sm:space-y-0 sm:space-x-4',
    lg: 'space-y-6 sm:space-y-0 sm:space-x-6',
    xl: 'space-y-8 sm:space-y-0 sm:space-x-8',
  };

  const alignClasses = {
    start: 'items-start',
    center: 'items-center',
    end: 'items-end',
    stretch: 'items-stretch',
  };

  const justifyClasses = {
    start: 'justify-start',
    center: 'justify-center',
    end: 'justify-end',
    between: 'justify-between',
    around: 'justify-around',
  };

  return (
    <div
      className={cn(
        'flex',
        directionClasses[direction],
        spacingClasses[spacing],
        alignClasses[align],
        justifyClasses[justify],
        className
      )}
    >
      {children}
    </div>
  );
};

export default ResponsiveLayout; 