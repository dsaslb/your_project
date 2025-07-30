'use client';

import { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { useSystemStatus } from '@/hooks/useSystemStatus';
import { useMenuPreferences } from '@/hooks/useMenuPreferences';
import { SidebarSearch } from '@/components/SidebarSearch';
import { MenuStatusIndicator, StatusBadge } from '@/components/MenuStatusIndicator';
import { SystemStatusHeader } from '@/components/SystemStatusHeader';
import { NotificationBadge } from '@/components/NotificationCenter';
import { 
  Menu, 
  X, 
  ChevronDown, 
  ChevronRight,
  Home,
  Building2,
  Users,
  Settings,
  BarChart3,
  ShoppingCart,
  Calendar,
  UserCheck,
  Store,
  Package,
  FileText,
  Bell,
  HelpCircle,
  Zap,
  Sparkles,
  Globe,
  Shield,
  Activity,
  Cpu,
  Monitor,
  Brain,
  TrendingUp,
  Server,
  Star
} from 'lucide-react';
import useUserStore from '@/store/useUserStore';
import { useOrderStore } from '@/store/useOrderStore';
import { usePluginMenus } from '@/hooks/usePluginMenus';
import ClientOnly from './ClientOnly';

interface MenuItem {
  title: string;
  href?: string;
  icon?: React.ReactNode;
  children?: MenuItem[];
  roles?: string[];
  badge?: string | number;
  status?: 'online' | 'offline' | 'warning' | 'error';
  statusMessage?: string;
  lastUpdated?: Date;
  category?: string;
  priority?: number;
}

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [filteredMenuItems, setFilteredMenuItems] = useState<MenuItem[]>([]);
  const pathname = usePathname();
  const { user, isAuthenticated, hasRole, subscribeToChanges } = useUserStore();
  const { connectWebSocket, disconnectWebSocket } = useOrderStore();
  const { menus: pluginMenus, loading: pluginMenusLoading } = usePluginMenus();
  
  // 새로운 훅들 사용
  const { getMenuStatus, getStatusMessage, status: systemStatus } = useSystemStatus();
  const {
    toggleFavorite,
    toggleHidden,
    updateLastAccessed,
    filterHiddenMenus,
    sortMenusByPriority,
    isFavorite,
    isHidden,
  } = useMenuPreferences();

  // 실시간 동기화: 사용자 상태 변경 감지
  useEffect(() => {
    if (isAuthenticated) {
      // WebSocket 연결
      connectWebSocket();
      
      // 사용자 상태 변경 구독
      const unsubscribe = subscribeToChanges((newState) => {
        console.log('사용자 상태 변경 감지:', newState);
        // 메뉴 재렌더링을 위해 강제 업데이트
        setIsOpen(prev => prev);
      });
      
      return () => {
        if (typeof unsubscribe === 'function') {
          unsubscribe();
        }
        disconnectWebSocket();
      };
    }
  }, [isAuthenticated, subscribeToChanges, connectWebSocket, disconnectWebSocket]);

  const toggleExpanded = (title: string) => {
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

  const isActive = (href: string) => pathname === href;

  // 권한별 메뉴 구성
  const getMenuItems = (): MenuItem[] => {
    const baseItems: MenuItem[] = [
      {
        title: '퀀텀 대시보드',
        href: '/dashboard',
        icon: <Home className="w-4 h-4" />,
        roles: ['super_admin', 'brand_manager', 'store_manager', 'employee'],
        category: 'dashboard',
        status: getMenuStatus('/dashboard'),
        statusMessage: getStatusMessage('/dashboard'),
        lastUpdated: systemStatus.lastUpdated,
      }
    ];

    // 플러그인 메뉴 추가
    if (!pluginMenusLoading && pluginMenus.length > 0) {
      const userRole = user?.role || 'employee';
      const userPluginMenus = pluginMenus.filter(menu => {
        if (!menu.roles || menu.roles.length === 0) return true;
        return menu.roles.includes(userRole);
      });

              // 플러그인 메뉴를 그룹별로 구성
        const pluginGroups: Record<string, MenuItem[]> = {};
        userPluginMenus.forEach(menu => {
          const parent = menu.parent || 'plugins';
          if (!pluginGroups[parent]) {
            pluginGroups[parent] = [];
          }
          pluginGroups[parent].push({
            title: menu.title,
            href: menu.path,
            icon: <Package className="w-4 h-4" />,
            badge: menu.badge,
            roles: menu.roles,
            category: 'plugin',
            status: getMenuStatus(menu.path),
            statusMessage: getStatusMessage(menu.path),
            lastUpdated: systemStatus.lastUpdated,
          });
        });

      // 플러그인 그룹을 메뉴에 추가
      Object.entries(pluginGroups).forEach(([groupName, groupMenus]) => {
        if (groupMenus.length === 1) {
          // 단일 메뉴인 경우 직접 추가
          baseItems.push(groupMenus[0]);
        } else {
          // 여러 메뉴인 경우 그룹으로 추가
          baseItems.push({
            title: groupName === 'plugins' ? '퀀텀 플러그인' : groupName,
            icon: <Package className="w-4 h-4" />,
            children: groupMenus,
            roles: groupMenus.flatMap(menu => menu.roles || [])
          });
        }
      });
    }

    // 최고 관리자 메뉴
    if (hasRole('super_admin')) {
      baseItems.push(
        {
          title: '시스템 관리',
          icon: <Settings className="w-4 h-4" />,
          children: [
            {
              title: '관리자 대시보드',
              href: '/dashboard',
              roles: ['super_admin'],
              category: 'administration',
                      status: getMenuStatus('/dashboard'),
        statusMessage: getStatusMessage('/dashboard'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '브랜드 관리',
              href: '/admin/brand-management',
              roles: ['super_admin'],
              category: 'administration',
              status: getMenuStatus('/admin/brand-management'),
              statusMessage: getStatusMessage('/admin/brand-management'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '매장 관리',
              href: '/admin/store-management',
              roles: ['super_admin'],
              category: 'administration',
              status: getMenuStatus('/admin/store-management'),
              statusMessage: getStatusMessage('/admin/store-management'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '직원 관리',
              href: '/admin/employee-management',
              roles: ['super_admin'],
              category: 'administration',
              status: getMenuStatus('/admin/employee-management'),
              statusMessage: getStatusMessage('/admin/employee-management'),
              lastUpdated: systemStatus.lastUpdated,
            }
          ],
          roles: ['super_admin'],
          category: 'administration',
        },
        {
          title: 'AI 시스템 모니터링',
          icon: <Brain className="w-4 h-4" />,
          children: [
            {
              title: '시스템 상태',
              href: '/system-health',
              icon: <Monitor className="w-4 h-4" />,
              roles: ['super_admin'],
              category: 'monitoring',
              status: getMenuStatus('/system-health'),
              statusMessage: getStatusMessage('/system-health'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '고급 분석',
              href: '/advanced-analytics',
              icon: <TrendingUp className="w-4 h-4" />,
              roles: ['super_admin'],
              category: 'analytics',
              status: getMenuStatus('/advanced-analytics'),
              statusMessage: getStatusMessage('/advanced-analytics'),
              lastUpdated: systemStatus.lastUpdated,
            }
          ],
          roles: ['super_admin'],
          category: 'monitoring',
        },
        {
          title: '고급 기능',
          icon: <BarChart3 className="w-4 h-4" />,
          children: [
            {
              title: '모듈 마켓플레이스',
              href: '/admin/module-marketplace',
              roles: ['super_admin'],
              category: 'advanced',
              status: getMenuStatus('/admin/module-marketplace'),
              statusMessage: getStatusMessage('/admin/module-marketplace'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '플러그인 관리',
              href: '/admin/plugin-management',
              roles: ['super_admin'],
              category: 'advanced',
              status: getMenuStatus('/admin/plugin-management'),
              statusMessage: getStatusMessage('/admin/plugin-management'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '피드백 관리',
              href: '/admin/feedback-management',
              roles: ['super_admin'],
              category: 'advanced',
              status: getMenuStatus('/admin/feedback-management'),
              statusMessage: getStatusMessage('/admin/feedback-management'),
              lastUpdated: systemStatus.lastUpdated,
            }
          ],
          roles: ['super_admin'],
          category: 'advanced',
        }
      );
    }

    // 브랜드 관리자 메뉴
    if (hasRole(['super_admin', 'brand_manager'])) {
      baseItems.push(
        {
          title: '브랜드 관리',
          icon: <Building2 className="w-4 h-4" />,
          children: [
            {
              title: '브랜드 대시보드',
              href: '/brand-dashboard/1',
              roles: ['super_admin', 'brand_manager'],
              category: 'brand',
              status: getMenuStatus('/brand-dashboard/1'),
              statusMessage: getStatusMessage('/brand-dashboard/1'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '브랜드별 매출',
              href: '/brand-dashboard/1/sales',
              roles: ['super_admin', 'brand_manager'],
              category: 'brand',
              status: getMenuStatus('/brand-dashboard/1/sales'),
              statusMessage: getStatusMessage('/brand-dashboard/1/sales'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '브랜드별 개선요청',
              href: '/brand-dashboard/1/improvements',
              roles: ['super_admin', 'brand_manager'],
              category: 'brand',
              status: getMenuStatus('/brand-dashboard/1/improvements'),
              statusMessage: getStatusMessage('/brand-dashboard/1/improvements'),
              lastUpdated: systemStatus.lastUpdated,
            }
          ],
          roles: ['super_admin', 'brand_manager'],
          category: 'brand',
        },
        {
          title: 'AI 시스템 모니터링',
          icon: <Brain className="w-4 h-4" />,
          children: [
            {
              title: '시스템 상태',
              href: '/system-health',
              icon: <Monitor className="w-4 h-4" />,
              roles: ['super_admin', 'brand_manager']
            },
            {
              title: '고급 분석',
              href: '/advanced-analytics',
              icon: <TrendingUp className="w-4 h-4" />,
              roles: ['super_admin', 'brand_manager']
            }
          ],
          roles: ['super_admin', 'brand_manager']
        },
        {
          title: '모듈/플러그인 관리',
          href: '/admin/module-management',
          icon: <Package className="w-4 h-4" />,
          roles: ['super_admin', 'brand_manager']
        }
      );
    }

    // 매장 관리자 메뉴
    if (hasRole(['super_admin', 'brand_manager', 'store_manager'])) {
      baseItems.push(
        {
          title: '매장 운영',
          icon: <Store className="w-4 h-4" />,
          children: [
            {
              title: '매장 관리자 대시보드',
              href: '/manager-dashboard',
              roles: ['super_admin', 'brand_manager', 'store_manager'],
              category: 'store',
              status: getMenuStatus('/manager-dashboard'),
              statusMessage: getStatusMessage('/manager-dashboard'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '주문 관리',
              href: '/orders',
              badge: 'New',
              roles: ['super_admin', 'brand_manager', 'store_manager'],
              category: 'store',
              status: getMenuStatus('/orders'),
              statusMessage: getStatusMessage('/orders'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '재고 관리',
              href: '/inventory',
              roles: ['super_admin', 'brand_manager', 'store_manager'],
              category: 'store',
              status: getMenuStatus('/inventory'),
              statusMessage: getStatusMessage('/inventory'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '직원 관리',
              href: '/staff',
              roles: ['super_admin', 'brand_manager', 'store_manager'],
              category: 'store',
              status: getMenuStatus('/staff'),
              statusMessage: getStatusMessage('/staff'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '근무표 관리',
              href: '/schedule',
              roles: ['super_admin', 'brand_manager', 'store_manager'],
              category: 'store',
              status: getMenuStatus('/schedule'),
              statusMessage: getStatusMessage('/schedule'),
              lastUpdated: systemStatus.lastUpdated,
            }
          ],
          roles: ['super_admin', 'brand_manager', 'store_manager'],
          category: 'store',
        },
        {
          title: '업무 관리',
          icon: <Calendar className="w-4 h-4" />,
          children: [
            {
              title: '출근 관리',
              href: '/attendance',
              roles: ['super_admin', 'brand_manager', 'store_manager'],
              category: 'work',
              status: getMenuStatus('/attendance'),
              statusMessage: getStatusMessage('/attendance'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '청소 관리',
              href: '/cleaning',
              roles: ['super_admin', 'brand_manager', 'store_manager'],
              category: 'work',
              status: getMenuStatus('/cleaning'),
              statusMessage: getStatusMessage('/cleaning'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '발주 관리',
              href: '/purchase',
              roles: ['super_admin', 'brand_manager', 'store_manager'],
              category: 'work',
              status: getMenuStatus('/purchase'),
              statusMessage: getStatusMessage('/purchase'),
              lastUpdated: systemStatus.lastUpdated,
            }
          ],
          roles: ['super_admin', 'brand_manager', 'store_manager'],
          category: 'work',
        },
        {
          title: 'AI 시스템 모니터링',
          icon: <Brain className="w-4 h-4" />,
          children: [
            {
              title: '시스템 상태',
              href: '/system-health',
              icon: <Monitor className="w-4 h-4" />,
              roles: ['super_admin', 'brand_manager', 'store_manager']
            },
            {
              title: '고급 분석',
              href: '/advanced-analytics',
              icon: <TrendingUp className="w-4 h-4" />,
              roles: ['super_admin', 'brand_manager', 'store_manager']
            }
          ],
          roles: ['super_admin', 'brand_manager', 'store_manager']
        }
      );
    }

    // 직원 메뉴
    if (hasRole(['super_admin', 'brand_manager', 'store_manager', 'employee'])) {
      baseItems.push(
        {
          title: '직원 기능',
          icon: <Users className="w-4 h-4" />,
          children: [
            {
              title: '직원 대시보드',
              href: '/employee-dashboard',
              roles: ['super_admin', 'brand_manager', 'store_manager', 'employee'],
              category: 'employee',
              status: getMenuStatus('/employee-dashboard'),
              statusMessage: getStatusMessage('/employee-dashboard'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '내 근무표',
              href: '/schedule',
              roles: ['super_admin', 'brand_manager', 'store_manager', 'employee'],
              category: 'employee',
              status: getMenuStatus('/schedule'),
              statusMessage: getStatusMessage('/schedule'),
              lastUpdated: systemStatus.lastUpdated,
            },
            {
              title: '출근 기록',
              href: '/attendance',
              roles: ['super_admin', 'brand_manager', 'store_manager', 'employee'],
              category: 'employee',
              status: getMenuStatus('/attendance'),
              statusMessage: getStatusMessage('/attendance'),
              lastUpdated: systemStatus.lastUpdated,
            }
          ],
          roles: ['super_admin', 'brand_manager', 'store_manager', 'employee'],
          category: 'employee',
        }
      );
    }

    // 공통 메뉴
    baseItems.push(
      {
        title: '공통 기능',
        icon: <Settings className="w-4 h-4" />,
        children: [
          {
            title: '알림',
            href: '/notifications',
            icon: <Bell className="w-4 h-4" />,
            roles: ['super_admin', 'brand_manager', 'store_manager', 'employee'],
            category: 'common',
            status: getMenuStatus('/notifications'),
            statusMessage: getStatusMessage('/notifications'),
            lastUpdated: systemStatus.lastUpdated,
          },
          {
            title: '설정',
            href: '/settings',
            icon: <Settings className="w-4 h-4" />,
            roles: ['super_admin', 'brand_manager', 'store_manager', 'employee'],
            category: 'common',
            status: getMenuStatus('/settings'),
            statusMessage: getStatusMessage('/settings'),
            lastUpdated: systemStatus.lastUpdated,
          },
          {
            title: '도움말',
            href: '/help',
            icon: <HelpCircle className="w-4 h-4" />,
            roles: ['super_admin', 'brand_manager', 'store_manager', 'employee'],
            category: 'common',
            status: getMenuStatus('/help'),
            statusMessage: getStatusMessage('/help'),
            lastUpdated: systemStatus.lastUpdated,
          }
        ],
        roles: ['super_admin', 'brand_manager', 'store_manager', 'employee'],
        category: 'common',
      }
    );

    // 운영 리포트/경고 메뉴 추가 (관리자/운영자 권한)
    if (hasRole(['super_admin', 'brand_manager', 'store_manager', 'admin'])) {
      baseItems.push({
        title: '운영 리포트/경고',
        href: '/enhanced-alerts',
        icon: <FileText className="w-4 h-4" />,
        roles: ['super_admin', 'brand_manager', 'store_manager', 'admin'],
        category: 'reports',
        status: getMenuStatus('/enhanced-alerts'),
        statusMessage: getStatusMessage('/enhanced-alerts'),
        lastUpdated: systemStatus.lastUpdated,
      });
    }

    return baseItems;
  };

  const renderMenuItem = (item: MenuItem, level: number = 0) => {
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems.has(item.title);
    const isActiveItem = item.href ? isActive(item.href) : false;
    const isFavoriteItem = item.href ? isFavorite(item.href) : false;
    const isHiddenItem = item.href ? isHidden(item.href) : false;

    // 권한 체크
    if (item.roles && !hasRole(item.roles)) {
      return null;
    }

    // 숨김 메뉴 체크
    if (isHiddenItem) {
      return null;
    }

    if (hasChildren) {
      return (
        <div key={item.title}>
          <div
            className={cn(
              'flex items-center justify-between px-4 py-3 text-sm font-medium rounded-lg cursor-pointer transition-all duration-300',
              level === 0 ? 'hover:bg-cyan-500/10 hover:text-cyan-400 hover:border-cyan-500/30 border border-transparent' : 'hover:bg-purple-500/10 hover:text-purple-400 hover:border-purple-500/30 border border-transparent',
              level > 0 && 'ml-4'
            )}
            onClick={() => toggleExpanded(item.title)}
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
              className={cn(
                'w-4 h-4 transition-transform duration-300 text-cyan-400',
                isExpanded && 'rotate-180'
              )}
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

    // 링크가 있는 메뉴 아이템
    if (item.href) {
      return (
        <div key={item.title} className="relative group">
          <Link href={item.href} className="block" onClick={() => {
            setIsOpen(false);
            updateLastAccessed(item.href!);
          }}>
            <div
              className={cn(
                'flex items-center justify-between px-4 py-3 text-sm font-medium rounded-lg cursor-pointer transition-all duration-300 border border-transparent',
                level === 0 ? 'hover:bg-cyan-500/10 hover:text-cyan-400 hover:border-cyan-500/30' : 'hover:bg-purple-500/10 hover:text-purple-400 hover:border-purple-500/30',
                isActiveItem && 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-400 border-cyan-500/50 shadow-lg shadow-cyan-500/25',
                isFavoriteItem && 'border-yellow-500/30',
                level > 0 && 'ml-4'
              )}
            >
              <div className="flex items-center space-x-3">
                <div className={cn(
                  'transition-colors duration-300',
                  isActiveItem ? 'text-cyan-400' : 'text-slate-400'
                )}>
                  {item.icon}
                </div>
                <span className="text-white">{item.title}</span>
                {item.badge && (
                  <span className="px-2 py-1 text-xs bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-full animate-pulse">
                    {item.badge}
                  </span>
                )}
              </div>
              
              {/* 상태 표시 및 액션 버튼 */}
              <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                {/* 상태 배지 */}
                {item.status && (
                  <StatusBadge status={item.status} />
                )}
                
                {/* 즐겨찾기 버튼 */}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    toggleFavorite(item.href!);
                  }}
                  className={cn(
                    "p-1 h-auto w-auto",
                    isFavoriteItem ? "text-yellow-400" : "text-slate-400 hover:text-yellow-400"
                  )}
                >
                  <Star className="w-3 h-3" />
                </Button>
              </div>
            </div>
          </Link>
        </div>
      );
    }

    // 링크가 없는 메뉴 아이템 (그룹 헤더)
    return (
      <div key={item.title}>
        <div
          className={cn(
            'flex items-center px-4 py-3 text-sm font-medium text-slate-400',
            level > 0 && 'ml-4'
          )}
        >
          <div className="flex items-center space-x-3">
            <div className="text-cyan-400">{item.icon}</div>
            <span>{item.title}</span>
          </div>
        </div>
      </div>
    );
  };

  const menuItems = getMenuItems();
  
  // 메뉴 아이템 처리 (필터링, 정렬)
  const processedMenuItems = useMemo(() => {
    let items = [...menuItems];
    
    // 숨김 메뉴 필터링
    items = filterHiddenMenus(items);
    
    // 우선순위 기반 정렬
    items = sortMenusByPriority(items);
    
    return items;
  }, [menuItems, filterHiddenMenus, sortMenusByPriority]);

  // 검색 결과 처리
  const handleSearch = (filteredItems: MenuItem[]) => {
    setFilteredMenuItems(filteredItems);
  };

  // 표시할 메뉴 아이템 결정
  const displayMenuItems = filteredMenuItems.length > 0 ? filteredMenuItems : processedMenuItems;

  if (!isAuthenticated) {
    return null;
  }

  return (
    <ClientOnly>
      {/* 모바일 사이드바 */}
      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="md:hidden bg-slate-900/50 border border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/10 hover:border-cyan-400"
          >
            <Menu className="h-5 w-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-80 p-0 bg-black/95 backdrop-blur-xl border-r border-cyan-500/20">
          <div className="flex h-full flex-col">
            <div className="flex items-center justify-between p-6 border-b border-cyan-500/20">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 to-purple-600 shadow-lg shadow-cyan-500/25">
                  <Zap className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">
                    퀀텀 시스템
                  </h2>
                  <p className="text-xs text-slate-400">차세대 관리 플랫폼</p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsOpen(false)}
                className="text-cyan-400 hover:bg-cyan-500/10 hover:text-cyan-300"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex-1 p-4 overflow-y-auto">
              <nav className="space-y-2">
                {displayMenuItems.map(item => renderMenuItem(item))}
              </nav>
            </div>
            <div className="p-4 border-t border-cyan-500/20 space-y-2">
              <NotificationBadge />
              <div className="text-xs text-slate-500 text-center">
                © 2024 퀀텀 시스템 v2.0
              </div>
            </div>
          </div>
        </SheetContent>
      </Sheet>

      {/* 데스크톱 사이드바 */}
      <div className="hidden md:flex md:w-80 md:flex-col md:fixed md:inset-y-0 md:border-r md:border-cyan-500/20 md:bg-black/90 md:backdrop-blur-xl">
        <div className="flex flex-col flex-grow pt-6 bg-black/90 backdrop-blur-xl overflow-y-auto">
          {/* 헤더 */}
          <div className="flex items-center flex-shrink-0 px-6 mb-6">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 to-purple-600 shadow-lg shadow-cyan-500/25 animate-pulse">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">
                  퀀텀 시스템
                </h1>
                <p className="text-xs text-slate-400">차세대 관리 플랫폼</p>
              </div>
            </div>
          </div>

          {/* 시스템 상태 헤더 */}
          <SystemStatusHeader />

          {/* 검색 컴포넌트 */}
          <SidebarSearch
            menuItems={processedMenuItems}
            onSearch={handleSearch}
            onToggleFavorite={toggleFavorite}
            onToggleHidden={toggleHidden}
            isFavorite={isFavorite}
            isHidden={isHidden}
          />

          {/* 네비게이션 */}
          <div className="flex-grow flex flex-col">
            <nav className="flex-1 px-4 pb-4 space-y-2">
              {displayMenuItems.map(item => renderMenuItem(item))}
            </nav>
          </div>

          {/* 푸터 */}
          <div className="p-4 border-t border-cyan-500/20 space-y-2">
            <NotificationBadge />
            <div className="text-xs text-slate-500 text-center">
              © 2024 퀀텀 시스템 v2.0
            </div>
          </div>
        </div>
      </div>
    </ClientOnly>
  );
}
