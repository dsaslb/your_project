"use client";

import { usePathname } from "next/navigation";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";

interface ClientLayoutProps {
  children: React.ReactNode;
}

export default function ClientLayout({ children }: ClientLayoutProps) {
  const pathname = usePathname();
  
  // 로그인 페이지와 루트 페이지는 사이드바 없이 표시
  const isPublicPage = pathname === "/login" || pathname === "/";
  
  if (isPublicPage) {
    return <>{children}</>;
  }
  
  // 대시보드 페이지들은 사이드바와 함께 표시
  return (
    <SidebarProvider>
      <div className="flex h-screen w-screen overflow-hidden">
        <div className="h-full flex-shrink-0 w-64 border-r bg-background">
          <AppSidebar />
        </div>
        <main className="flex-1 h-full overflow-y-auto bg-background p-6">
          {children}
        </main>
      </div>
    </SidebarProvider>
  );
} 