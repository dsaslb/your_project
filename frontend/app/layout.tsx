import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "레스토랑 관리 시스템",
  description: "4단계 계층별 통합 관리 플랫폼",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-background antialiased font-sans w-full block">
        {children}
      </body>
    </html>
  );
} 