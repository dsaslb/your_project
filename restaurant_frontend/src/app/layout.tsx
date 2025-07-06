import Sidebar from "@/components/Sidebar";
import { UserProvider } from "@/components/UserContext";
import AuthGuard from "@/components/AuthGuard";
import { Toaster } from "@/components/ui/sonner";
import "@/styles/globals.css";

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
              <Sidebar menu={[]} />
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
