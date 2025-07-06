"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useUser } from "./UserContext";
import { ChevronLeft, ChevronRight, Users, Calendar, Package, ShoppingCart, BarChart3, Settings, Clock, FileText, Bell } from "lucide-react";

export interface SidebarMenuItem {
  label: string;
  href: string;
  icon?: React.ReactNode;
  group?: string;
}

export default function Sidebar({ menu }: { menu: SidebarMenuItem[] }) {
  const pathname = usePathname();
  const { user, logout } = useUser();
  const [isCollapsed, setIsCollapsed] = useState(false);

  // 관리 메뉴 그룹
  const managementMenu = [
    { label: "직원 관리", href: "/staff", icon: <Users className="h-5 w-5" /> },
    { label: "스케줄 관리", href: "/schedule", icon: <Calendar className="h-5 w-5" /> },
    { label: "근태 관리", href: "/attendance", icon: <Clock className="h-5 w-5" /> },
    { label: "발주 관리", href: "/purchase", icon: <Package className="h-5 w-5" /> },
    { label: "재고 관리", href: "/inventory", icon: <ShoppingCart className="h-5 w-5" /> },
    { label: "주문 관리", href: "/orders", icon: <FileText className="h-5 w-5" /> },
    { label: "청소 관리", href: "/cleaning", icon: <Settings className="h-5 w-5" /> },
  ];

  // 대시보드 메뉴
  const dashboardMenu = [
    { label: "대시보드", href: "/dashboard", icon: <BarChart3 className="h-5 w-5" /> },
  ];

  // 기타 메뉴
  const otherMenu = [
    { label: "매장 종합 평가", href: "/evaluation", icon: <BarChart3 className="h-5 w-5" /> },
    { label: "알림/공지", href: "/notifications", icon: <Bell className="h-5 w-5" /> },
    { label: "설정", href: "/settings", icon: <Settings className="h-5 w-5" /> },
  ];

  return (
    <aside className={`min-h-screen bg-zinc-900 text-white flex flex-col border-r border-zinc-800 transition-all duration-300 ${
      isCollapsed ? "w-16" : "w-64"
    }`}>
      <div className={`h-16 flex items-center justify-between border-b border-zinc-800 px-4 ${
        isCollapsed ? "justify-center" : "px-6"
      }`}>
        {!isCollapsed && (
          <div className="font-bold text-xl">매장관리</div>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1 hover:bg-zinc-800 rounded transition-colors"
        >
          {isCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </button>
      </div>
      
      <nav className="flex-1 py-4">
        {/* 대시보드 메뉴 */}
        <div className="mb-6">
          {!isCollapsed && (
            <div className="px-6 py-2 text-xs font-semibold text-zinc-400 uppercase tracking-wider">
              대시보드
            </div>
          )}
          {dashboardMenu.map(item => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 px-6 py-3 hover:bg-zinc-800 transition ${
                pathname === item.href ? "bg-zinc-800 font-bold" : ""
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

        {/* 관리 메뉴 그룹 */}
        <div className="mb-6">
          {!isCollapsed && (
            <div className="px-6 py-2 text-xs font-semibold text-zinc-400 uppercase tracking-wider">
              관리 메뉴
            </div>
          )}
          {managementMenu.map(item => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 px-6 py-3 hover:bg-zinc-800 transition ${
                pathname === item.href ? "bg-zinc-800 font-bold" : ""
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

        {/* 기타 메뉴 */}
        <div className="mb-6">
          {!isCollapsed && (
            <div className="px-6 py-2 text-xs font-semibold text-zinc-400 uppercase tracking-wider">
              기타
            </div>
          )}
          {otherMenu.map(item => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 px-6 py-3 hover:bg-zinc-800 transition ${
                pathname === item.href ? "bg-zinc-800 font-bold" : ""
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
      </nav>
      
      <div className={`p-4 border-t border-zinc-800 ${isCollapsed ? "px-2" : ""}`}>
        {user ? (
          <button 
            onClick={logout} 
            className={`w-full bg-zinc-700 hover:bg-zinc-600 text-white py-2 rounded transition-colors ${
              isCollapsed ? "px-2" : ""
            }`}
            title={isCollapsed ? "로그아웃" : ""}
          >
            {!isCollapsed && "로그아웃"}
          </button>
        ) : null}
      </div>
    </aside>
  );
}
