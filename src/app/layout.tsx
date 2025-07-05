import "../globals.css";
import AppLayout from "@/components/AppLayout";
import { ThemeProvider } from "next-themes";

export const metadata = {
  title: "맛있는집 - 매장 관리 시스템",
  description: "전문적인 레스토랑 관리 및 브랜드 홈페이지",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem>
          <AppLayout>{children}</AppLayout>
        </ThemeProvider>
      </body>
    </html>
  );
} 