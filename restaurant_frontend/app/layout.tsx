import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { UserProvider } from "@/components/UserContext";
import { AuthGuard } from "@/components/AuthGuard";
import { HistoryManager } from "@/components/HistoryManager";
import { NotificationProvider } from "@/components/NotificationSystem";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "맛있는집 - 매장 관리 시스템",
  description: "전문적인 레스토랑 관리 및 브랜드 홈페이지",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          disableTransitionOnChange
        >
          <UserProvider>
            <NotificationProvider>
              <AuthGuard>
                <HistoryManager />
                {children}
              </AuthGuard>
            </NotificationProvider>
          </UserProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
