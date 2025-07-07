"use client";

import Sidebar from "@/components/Sidebar";
import { UserProvider } from "@/components/UserContext";
import AuthGuard from "@/components/AuthGuard";
import { Toaster } from "@/components/ui/sonner";
import { usePathname } from "next/navigation";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider } from '@/components/theme-provider';
import { AuthProvider } from '@/components/auth/AuthProvider';
import { PermissionProvider } from '@/components/auth/PermissionProvider';

// React Query 클라이언트 생성
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5분
      gcTime: 10 * 60 * 1000, // 10분
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      retry: 1,
      retryDelay: 1000,
    },
  },
});

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLoginPage = pathname === "/login";

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        <AuthProvider>
          <PermissionProvider>
            <UserProvider>
              <AuthGuard>
                {isLoginPage ? (
                  // 로그인 페이지일 때는 전체 화면으로 로그인 폼만 표시
                  <div className="min-h-screen">
                    {children}
                  </div>
                ) : (
                  // 로그인 페이지가 아닐 때는 Sidebar와 main 레이아웃 사용
                  <div className="flex min-h-screen w-full">
                    <Sidebar menu={[]} />
                    <main className="flex-1 bg-background p-6 overflow-y-auto transition-all duration-300">
                      {children}
                    </main>
                  </div>
                )}
              </AuthGuard>
            </UserProvider>
            <Toaster />
            <ReactQueryDevtools initialIsOpen={false} />
          </PermissionProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
} 