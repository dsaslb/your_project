"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useUser } from "./UserContext";
import { 
  ChevronLeft, 
  ChevronRight, 
  Users, 
  Calendar, 
  Package, 
  ShoppingCart, 
  BarChart3, 
  Settings, 
  Clock, 
  FileText, 
  Bell,
  Crown,
  Building2,
  Store,
  Shield,
  TrendingUp,
  AlertTriangle,
  ClipboardList,
  DollarSign,
  UserCheck,
  Archive,
  MessageSquare,
  Home,
  LogOut,
  MessageCircle
} from "lucide-react";

export interface SidebarMenuItem {
  label: string;
  href: string;
  icon?: React.ReactNode;
  group?: string;
  requiredPermission?: string;
}

export default function Sidebar({ menu }: { menu: SidebarMenuItem[] }) {
  const pathname = usePathname();
  const { user, logout } = useUser();
  const [isCollapsed, setIsCollapsed] = useState(false);

  // 권한 계산 함수
  const calculatePermissions = (role?: string) => {
    return {
      canAccessSuperAdmin: role === 'super_admin' || role === 'admin',
      canAccessBrandAdmin: role === 'super_admin' || role === 'admin' || role === 'brand_admin',
      canAccessStoreAdmin: role === 'super_admin' || role === 'admin' || role === 'brand_admin' || role === 'store_admin' || role === 'manager',
      canAccessStaff: true, // 모든 로그인한 사용자는 기본 접근 가능
      canAccessManager: role === 'super_admin' || role === 'admin' || role === 'brand_admin' || role === 'manager',
    };
  };

  const permissions = calculatePermissions(user?.role);

  // 메인 대시보드 메뉴
  const mainMenu = [
    { 
      label: "홈", 
      href: "/dashboard", 
      icon: <Home className="h-5 w-5" />,
      requiredPermission: 'canAccessStaff'
    },
  ];

  // 슈퍼 관리자 메뉴
  const superAdminMenu = [
    { 
      label: "슈퍼 관리자 대시보드", 
      href: "/admin-dashboard", 
      icon: <Crown className="h-5 w-5" />,
      requiredPermission: 'canAccessSuperAdmin'
    },
    { 
      label: "시스템 모니터링", 
      href: "/admin-monitor", 
      icon: <Shield className="h-5 w-5" />,
      requiredPermission: 'canAccessSuperAdmin'
    },
    { 
      label: "전체 통계", 
      href: "/admin-analytics", 
      icon: <TrendingUp className="h-5 w-5" />,
      requiredPermission: 'canAccessSuperAdmin'
    },
    { 
      label: "사용자 관리", 
      href: "/user-management", 
      icon: <UserCheck className="h-5 w-5" />,
      requiredPermission: 'canAccessSuperAdmin'
    },
    { 
      label: "브랜치 관리", 
      href: "/branch-management", 
      icon: <Building2 className="h-5 w-5" />,
      requiredPermission: 'canAccessSuperAdmin'
    },
  ];

  // 브랜드 관리자 메뉴
  const brandAdminMenu = [
    { 
      label: "브랜드 대시보드", 
      href: "/brand-dashboard", 
      icon: <Building2 className="h-5 w-5" />,
      requiredPermission: 'canAccessBrandAdmin'
    },
    { 
      label: "매장 관리", 
      href: "/store-management", 
      icon: <Store className="h-5 w-5" />,
      requiredPermission: 'canAccessBrandAdmin'
    },
    { 
      label: "브랜드 통계", 
      href: "/brand-analytics", 
      icon: <BarChart3 className="h-5 w-5" />,
      requiredPermission: 'canAccessBrandAdmin'
    },
  ];

  // 매장 관리자 메뉴
  const storeAdminMenu = [
    { 
      label: "매장 대시보드", 
      href: "/store-dashboard", 
      icon: <Store className="h-5 w-5" />,
      requiredPermission: 'canAccessStoreAdmin'
    },
    { 
      label: "직원 관리", 
      href: "/staff", 
      icon: <Users className="h-5 w-5" />,
      requiredPermission: 'canAccessStoreAdmin'
    },
    { 
      label: "스케줄 관리", 
      href: "/schedule", 
      icon: <Calendar className="h-5 w-5" />,
      requiredPermission: 'canAccessStoreAdmin'
    },
    { 
      label: "근태 관리", 
      href: "/attendance", 
      icon: <Clock className="h-5 w-5" />,
      requiredPermission: 'canAccessStoreAdmin'
    },
    { 
      label: "발주 관리", 
      href: "/purchase", 
      icon: <Package className="h-5 w-5" />,
      requiredPermission: 'canAccessStoreAdmin'
    },
    { 
      label: "재고 관리", 
      href: "/inventory", 
      icon: <Archive className="h-5 w-5" />,
      requiredPermission: 'canAccessStoreAdmin'
    },
    { 
      label: "주문 관리", 
      href: "/orders", 
      icon: <ShoppingCart className="h-5 w-5" />,
      requiredPermission: 'canAccessStoreAdmin'
    },
  ];

  // 일반 직원 메뉴
  const staffMenu = [
    { 
      label: "내 근태", 
      href: "/my-attendance", 
      icon: <Clock className="h-5 w-5" />,
      requiredPermission: 'canAccessStaff'
    },
    { 
      label: "내 스케줄", 
      href: "/my-schedule", 
      icon: <Calendar className="h-5 w-5" />,
      requiredPermission: 'canAccessStaff'
    },
  ];

  // 공통 메뉴
  const commonMenu = [
    { 
      label: "채팅", 
      href: "/chat", 
      icon: <MessageCircle className="h-5 w-5" />,
      requiredPermission: 'canAccessStaff'
    },
    { 
      label: "고급 보고서", 
      href: "/reports", 
      icon: <BarChart3 className="h-5 w-5" />,
      requiredPermission: 'canAccessManager'
    },
    { 
      label: "데이터 시각화", 
      href: "/visualization", 
      icon: <TrendingUp className="h-5 w-5" />,
      requiredPermission: 'canAccessManager'
    },
    { 
      label: "알림/공지", 
      href: "/notifications", 
      icon: <Bell className="h-5 w-5" />,
      requiredPermission: 'canAccessStaff'
    },
    { 
      label: "설정", 
      href: "/settings", 
      icon: <Settings className="h-5 w-5" />,
      requiredPermission: 'canAccessStaff'
    },
  ];

  // 권한에 따른 메뉴 필터링
  const filterMenuByPermission = (menuItems: any[]) => {
    return menuItems.filter(item => {
      if (!item.requiredPermission) return true;
      return permissions[item.requiredPermission as keyof typeof permissions];
    });
  };

  const filteredMainMenu = filterMenuByPermission(mainMenu);
  const filteredSuperAdminMenu = filterMenuByPermission(superAdminMenu);
  const filteredBrandAdminMenu = filterMenuByPermission(brandAdminMenu);
  const filteredStoreAdminMenu = filterMenuByPermission(storeAdminMenu);
  const filteredStaffMenu = filterMenuByPermission(staffMenu);
  const filteredCommonMenu = filterMenuByPermission(commonMenu);

  const renderMenuSection = (title: string, menuItems: any[]) => {
    if (menuItems.length === 0) return null;

    return (
      <div className="mb-6">
        {!isCollapsed && (
          <div className="px-6 py-2 text-xs font-semibold text-zinc-400 uppercase tracking-wider">
            {title}
          </div>
        )}
        {menuItems.map(item => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-2 px-6 py-3 hover:bg-zinc-800 transition-colors ${
              pathname === item.href ? "bg-zinc-800 text-white font-semibold" : "text-zinc-300"
            } ${isCollapsed ? "justify-center px-2" : ""}`}
            title={isCollapsed ? item.label : ""}
          >
            <div className="flex-shrink-0">
              {item.icon}
            </div>
            {!isCollapsed && (
              <span className="truncate">{item.label}</span>
            )}
          </Link>
        ))}
      </div>
    );
  };

  return (
    <aside className={`min-h-screen bg-zinc-900 text-white flex flex-col border-r border-zinc-800 transition-all duration-300 ${
      isCollapsed ? "w-16" : "w-64"
    }`}>
      {/* 헤더 */}
      <div className={`h-16 flex items-center justify-between border-b border-zinc-800 px-4 ${
        isCollapsed ? "justify-center" : "px-6"
      }`}>
        {!isCollapsed && (
          <div className="font-bold text-xl text-white">레스토랑 관리</div>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1 hover:bg-zinc-800 rounded transition-colors text-zinc-300 hover:text-white"
        >
          {isCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </button>
      </div>
      
      {/* 네비게이션 */}
      <nav className="flex-1 py-4 overflow-y-auto">
        {/* 메인 메뉴 */}
        {renderMenuSection("메인", filteredMainMenu)}
        
        {/* 슈퍼 관리자 메뉴 */}
        {renderMenuSection("슈퍼 관리", filteredSuperAdminMenu)}
        
        {/* 브랜드 관리자 메뉴 */}
        {renderMenuSection("브랜드 관리", filteredBrandAdminMenu)}
        
        {/* 매장 관리자 메뉴 */}
        {renderMenuSection("매장 관리", filteredStoreAdminMenu)}
        
        {/* 일반 직원 메뉴 */}
        {renderMenuSection("업무", filteredStaffMenu)}
        
        {/* 공통 메뉴 */}
        {renderMenuSection("기타", filteredCommonMenu)}
      </nav>
      
      {/* 푸터 */}
      <div className={`p-4 border-t border-zinc-800 ${isCollapsed ? "px-2" : ""}`}>
        {user ? (
          <div className="space-y-2">
            {!isCollapsed && (
              <div className="text-xs text-zinc-400 px-2 mb-2">
                <div className="font-medium">{user.name || user.username}</div>
                <div className="text-zinc-500">{user.role}</div>
              </div>
            )}
            <button 
              onClick={logout} 
              className={`w-full bg-zinc-700 hover:bg-zinc-600 text-white py-2 rounded transition-colors flex items-center justify-center gap-2 ${
                isCollapsed ? "px-2" : ""
              }`}
              title={isCollapsed ? "로그아웃" : ""}
            >
              <LogOut className="h-4 w-4" />
              {!isCollapsed && "로그아웃"}
            </button>
          </div>
        ) : null}
      </div>
    </aside>
  );
}
