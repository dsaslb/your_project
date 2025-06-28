import { createContext, useContext } from "react";

export type UserRole = "admin" | "manager" | "employee";
export type User = { id: number; name: string; role: UserRole } | null;

const AuthContext = createContext<{ user: User }>({ user: null });

export function AuthProvider({ children }: { children: React.ReactNode }) {
  // 실제로는 로그인 후 세션/쿠키에서 유저 데이터 fetch
  const user = { id: 1, name: "슈퍼관리자", role: "admin" as UserRole };
  return <AuthContext.Provider value={{ user }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
} 