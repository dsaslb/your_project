"use client";
import { useUser } from "./UserContext";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  // 인증 우회: 항상 children 렌더
  return <>{children}</>;
} 