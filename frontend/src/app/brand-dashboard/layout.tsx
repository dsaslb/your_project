"use client";
import { useUser } from "@/components/UserContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Building2, Users, Calendar, Package, ShoppingCart, BarChart3, Settings, Clock, FileText, Bell, ChevronLeft, Activity, Shield } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function BrandDashboardLayout({ children }: { children: React.ReactNode }) {
  const { user } = useUser();
  const router = useRouter();
  const pathname = usePathname();

  // 브랜드 관리자 메뉴
  const brandMenu = [
    { label: "브랜드 대시보드", href: "/brand-dashboard", icon: <BarChart3 className="h-5 w-5" /> },
    { label: "매장 관리", href: "/brand-dashboard/branches", icon: <Building2 className="h-5 w-5" /> },
    { label: "통계 리포트", href: "/brand-dashboard/reports", icon: <BarChart3 className="h-5 w-5" /> },
    { label: "매장 비교", href: "/brand-dashboard/compare", icon: <BarChart3 className="h-5 w-5" /> },
    { label: "실시간 모니터링", href: "/brand-dashboard/monitoring", icon: <Activity className="h-5 w-5" /> },
    { label: "권한 관리", href: "/brand-dashboard/permissions", icon: <Shield className="h-5 w-5" /> },
    { label: "직원 관리", href: "/staff", icon: <Users className="h-5 w-5" /> },
    { label: "스케줄 관리", href: "/schedule", icon: <Calendar className="h-5 w-5" /> },
    { label: "근태 관리", href: "/attendance", icon: <Clock className="h-5 w-5" /> },
    { label: "발주 관리", href: "/purchase", icon: <Package className="h-5 w-5" /> },
    { label: "재고 관리", href: "/inventory", icon: <ShoppingCart className="h-5 w-5" /> },
    { label: "주문 관리", href: "/orders", icon: <FileText className="h-5 w-5" /> },
    { label: "청소 관리", href: "/cleaning", icon: <Settings className="h-5 w-5" /> },
    { label: "알림/공지", href: "/notifications", icon: <Bell className="h-5 w-5" /> },
    { label: "설정", href: "/settings", icon: <Settings className="h-5 w-5" /> },
  ];

  useEffect(() => {
    // 브랜드 관리자가 아닌 경우 접근 제한
    if (user && user.role !== "brand_admin") {
      router.push("/dashboard");
    }
  }, [user, router]);

  if (!user || user.role !== "brand_admin") {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">권한 확인 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* 브랜드 관리자 사이드바 */}
      <aside className="w-64 bg-white shadow-sm border-r border-gray-200">
        <div className="h-16 flex items-center justify-between border-b border-gray-200 px-6">
          <div className="flex items-center space-x-3">
            <Building2 className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-lg font-semibold text-gray-900">브랜드 관리</h1>
              <p className="text-xs text-gray-500">Brand Admin</p>
            </div>
          </div>
        </div>
        
        <nav className="py-4">
          {brandMenu.map(item => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-6 py-3 hover:bg-gray-50 transition-colors ${
                pathname === item.href ? "bg-blue-50 text-blue-600 border-r-2 border-blue-600" : "text-gray-700"
              }`}
            >
              <div className="flex-shrink-0">
                {item.icon}
              </div>
              <span className="truncate">{item.label}</span>
            </Link>
          ))}
        </nav>
        
        <div className="absolute bottom-0 w-64 p-4 border-t border-gray-200">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-blue-600">
                {user.username?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">{user.username}</p>
              <p className="text-xs text-gray-500">브랜드 관리자</p>
            </div>
          </div>
          <button
            onClick={() => router.push("/dashboard")}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChevronLeft className="h-4 w-4" />
            매장 대시보드로
          </button>
        </div>
      </aside>

      {/* 메인 콘텐츠 */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
} 