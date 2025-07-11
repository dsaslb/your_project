'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Menu, X, ChevronDown, ChevronRight } from 'lucide-react';
import useUserStore from '@/store/useUserStore';
import { useOrderStore } from '@/store/useOrderStore';
import { usePluginMenus } from '@/hooks/usePluginMenus';

interface MenuItem {
  title: string;
  href?: string;
  icon?: React.ReactNode;
  children?: MenuItem[];
  roles?: string[];
  badge?: string | number;
}

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const pathname = usePathname();
  const { user, isAuthenticated, hasRole, subscribeToChanges } = useUserStore();
  const { connectWebSocket, disconnectWebSocket } = useOrderStore();
  const { menus: pluginMenus, loading: pluginMenusLoading } = usePluginMenus();

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
        title: '대시보드',
        href: '/dashboard',
        icon: <div className="w-4 h-4 bg-blue-500 rounded" />,
        roles: ['super_admin', 'brand_manager', 'store_manager', 'employee']
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
          icon: <div className="w-4 h-4 bg-purple-500 rounded" />,
          badge: menu.badge,
          roles: menu.roles
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
            title: groupName === 'plugins' ? '플러그인' : groupName,
            icon: <div className="w-4 h-4 bg-purple-500 rounded" />,
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
          icon: <div className="w-4 h-4 bg-red-500 rounded" />,
          children: [
            {
              title: '전체 대시보드',
              href: '/super-admin',
              roles: ['super_admin']
            },
            {
              title: '매장 관리',
              href: '/branch-management',
              roles: ['super_admin']
            },
            {
              title: '사용자 관리',
              href: '/staff',
              roles: ['super_admin']
            },
            {
              title: '권한 관리',
              href: '/admin-monitor',
              roles: ['super_admin']
            }
          ],
          roles: ['super_admin']
        },
        {
          title: '고급 기능',
          icon: <div className="w-4 h-4 bg-purple-500 rounded" />,
          children: [
            {
              title: 'AI 예측',
              href: '/ai-prediction',
              roles: ['super_admin']
            },
            {
              title: '실시간 모니터링',
              href: '/realtime-monitoring',
              roles: ['super_admin']
            },
            {
              title: '플러그인 성능',
              href: '/plugin-performance',
              roles: ['super_admin']
            },
            {
              title: '보안 감사',
              href: '/security-audit',
              roles: ['super_admin']
            }
          ],
          roles: ['super_admin']
        }
      );
    }

    // 브랜드 관리자 메뉴
    if (hasRole(['super_admin', 'brand_manager'])) {
      baseItems.push(
        {
          title: '브랜드 관리',
          icon: <div className="w-4 h-4 bg-green-500 rounded" />,
          children: [
            {
              title: '브랜드 대시보드',
              href: '/brand-dashboard',
              roles: ['super_admin', 'brand_manager']
            },
            {
              title: '매장별 통계',
              href: '/analytics',
              roles: ['super_admin', 'brand_manager']
            },
            {
              title: '성과 분석',
              href: '/performance',
              roles: ['super_admin', 'brand_manager']
            }
          ],
          roles: ['super_admin', 'brand_manager']
        }
      );
    }

    // 매장 관리자 메뉴
    if (hasRole(['super_admin', 'brand_manager', 'store_manager'])) {
      baseItems.push(
        {
          title: '매장 운영',
          icon: <div className="w-4 h-4 bg-orange-500 rounded" />,
          children: [
            {
              title: '매장 대시보드',
              href: '/store-dashboard',
              roles: ['super_admin', 'brand_manager', 'store_manager']
            },
            {
              title: '주문 관리',
              href: '/orders',
              badge: 'New',
              roles: ['super_admin', 'brand_manager', 'store_manager']
            },
            {
              title: '재고 관리',
              href: '/inventory',
              roles: ['super_admin', 'brand_manager', 'store_manager']
            },
            {
              title: '직원 관리',
              href: '/staff',
              roles: ['super_admin', 'brand_manager', 'store_manager']
            },
            {
              title: '근무표 관리',
              href: '/schedule',
              roles: ['super_admin', 'brand_manager', 'store_manager']
            }
          ],
          roles: ['super_admin', 'brand_manager', 'store_manager']
        },
        {
          title: '업무 관리',
          icon: <div className="w-4 h-4 bg-yellow-500 rounded" />,
          children: [
            {
              title: '출근 관리',
              href: '/attendance',
              roles: ['super_admin', 'brand_manager', 'store_manager']
            },
            {
              title: '청소 관리',
              href: '/cleaning',
              roles: ['super_admin', 'brand_manager', 'store_manager']
            },
            {
              title: '발주 관리',
              href: '/purchase',
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
          icon: <div className="w-4 h-4 bg-blue-500 rounded" />,
          children: [
            {
              title: '직원 대시보드',
              href: '/employee-dashboard',
              roles: ['super_admin', 'brand_manager', 'store_manager', 'employee']
            },
            {
              title: '내 근무표',
              href: '/schedule',
              roles: ['super_admin', 'brand_manager', 'store_manager', 'employee']
            },
            {
              title: '출근 기록',
              href: '/attendance',
              roles: ['super_admin', 'brand_manager', 'store_manager', 'employee']
            }
          ],
          roles: ['super_admin', 'brand_manager', 'store_manager', 'employee']
        }
      );
    }

    // 공통 메뉴
    baseItems.push(
      {
        title: '공통 기능',
        icon: <div className="w-4 h-4 bg-gray-500 rounded" />,
        children: [
          {
            title: '알림',
            href: '/notifications',
            roles: ['super_admin', 'brand_manager', 'store_manager', 'employee']
          },
          {
            title: '채팅',
            href: '/chat',
            roles: ['super_admin', 'brand_manager', 'store_manager', 'employee']
          },
          {
            title: '설정',
            href: '/settings',
            roles: ['super_admin', 'brand_manager', 'store_manager', 'employee']
          }
        ],
        roles: ['super_admin', 'brand_manager', 'store_manager', 'employee']
      }
    );

    return baseItems;
  };

  const renderMenuItem = (item: MenuItem, level: number = 0) => {
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems.has(item.title);
    const isActiveItem = item.href ? isActive(item.href) : false;

    // 권한 체크
    if (item.roles && !hasRole(item.roles)) {
      return null;
    }

    return (
      <div key={item.title}>
        <div
          className={cn(
            'flex items-center justify-between px-3 py-2 text-sm font-medium rounded-md cursor-pointer transition-colors',
            level === 0 ? 'hover:bg-gray-100 dark:hover:bg-gray-800' : 'hover:bg-gray-50 dark:hover:bg-gray-700',
            isActiveItem && 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
            level > 0 && 'ml-4'
          )}
          onClick={() => {
            if (hasChildren) {
              toggleExpanded(item.title);
            } else if (item.href) {
              setIsOpen(false);
            }
          }}
        >
          <div className="flex items-center space-x-3">
            {item.icon}
            <span>{item.title}</span>
            {item.badge && (
              <span className="px-2 py-1 text-xs bg-red-500 text-white rounded-full">
                {item.badge}
              </span>
            )}
          </div>
          {hasChildren && (
            <ChevronDown
              className={cn(
                'w-4 h-4 transition-transform',
                isExpanded && 'rotate-180'
              )}
            />
          )}
        </div>
        
        {hasChildren && isExpanded && (
          <div className="mt-1 space-y-1">
            {item.children!.map(child => renderMenuItem(child, level + 1))}
          </div>
        )}
        
        {!hasChildren && item.href && (
          <Link href={item.href} className="block">
            <div
              className={cn(
                'flex items-center px-3 py-2 text-sm font-medium rounded-md cursor-pointer transition-colors',
                level === 0 ? 'hover:bg-gray-100 dark:hover:bg-gray-800' : 'hover:bg-gray-50 dark:hover:bg-gray-700',
                isActiveItem && 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
                level > 0 && 'ml-4'
              )}
            >
              {item.icon}
              <span className="ml-3">{item.title}</span>
            </div>
          </Link>
        )}
      </div>
    );
  };

  const menuItems = getMenuItems();

  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      {/* 모바일 사이드바 */}
      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="md:hidden"
          >
            <Menu className="h-5 w-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-64 p-0">
          <div className="flex h-full flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-lg font-semibold">Your Program</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex-1 p-4 overflow-y-auto">
              <nav className="space-y-2">
                {menuItems.map(item => renderMenuItem(item))}
              </nav>
            </div>
          </div>
        </SheetContent>
      </Sheet>

      {/* 데스크톱 사이드바 */}
      <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0 md:border-r md:bg-white md:dark:bg-gray-900">
        <div className="flex flex-col flex-grow pt-5 bg-white dark:bg-gray-900 overflow-y-auto">
          <div className="flex items-center flex-shrink-0 px-4">
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              Your Program
            </h1>
          </div>
          <div className="mt-5 flex-grow flex flex-col">
            <nav className="flex-1 px-2 pb-4 space-y-1">
              {menuItems.map(item => renderMenuItem(item))}
            </nav>
          </div>
        </div>
      </div>
    </>
  );
}
