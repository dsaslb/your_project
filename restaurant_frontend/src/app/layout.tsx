import Sidebar, { SidebarMenuItem } from "@/components/Sidebar";
import { UserProvider } from "@/components/UserContext";
import AuthGuard from "@/components/AuthGuard";
import { Toaster } from "@/components/ui/sonner";
import "@/styles/globals.css";
import { Home, Users, Calendar, ClipboardList, Boxes, Bell, Settings, Sparkles, BarChart3 } from "lucide-react";

const menu: SidebarMenuItem[] = [
  { label: "대시보드", href: "/dashboard", icon: <Home size={18} /> },
  { label: "직원 관리", href: "/staff", icon: <Users size={18} /> },
  { label: "스케줄", href: "/schedule", icon: <Calendar size={18} /> },
  { label: "주문 관리", href: "/orders", icon: <ClipboardList size={18} /> },
  { label: "발주 관리", href: "/purchase", icon: <Boxes size={18} /> },
  { label: "재고 관리", href: "/inventory", icon: <Boxes size={18} /> },
  { label: "청소 관리", href: "/cleaning", icon: <Sparkles size={18} /> },
  { label: "매장 종합 평가", href: "/evaluation", icon: <BarChart3 size={18} /> },
  { label: "알림/공지", href: "/notifications", icon: <Bell size={18} /> },
  { label: "설정", href: "/settings", icon: <Settings size={18} /> },
];

export const metadata = {
  title: "매장 관리 시스템",
  description: "레스토랑 매장 관리 시스템",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <UserProvider>
          <AuthGuard>
            <div className="flex min-h-screen w-full">
              <Sidebar menu={menu} />
              <main className="flex-1 bg-background p-6 overflow-y-auto transition-all duration-300">
                {children}
              </main>
            </div>
          </AuthGuard>
        </UserProvider>
        <Toaster />
      </body>
    </html>
  );
}
