"use client";
import { useUser } from "./UserContext";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useUser();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading) {
      if (!user && pathname !== "/login") {
        router.replace("/login");
      }
      if (user && pathname === "/login") {
        router.replace("/dashboard");
      }
    }
  }, [user, pathname, router, isLoading]);

  if (isLoading) {
    return <div>로딩 중...</div>;
  }

  if (!user && pathname !== "/login") {
    return null;
  }
  
  if (user && pathname === "/login") {
    return null;
  }
  
  return <>{children}</>;
} 