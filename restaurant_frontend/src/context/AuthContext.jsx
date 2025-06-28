import { createContext, useContext } from "react";

const AuthContext = createContext({ user: null });

export function AuthProvider({ children }) {
  // 실제로는 로그인 후 세션/쿠키에서 유저 데이터 fetch
  const user = { id: 1, name: "슈퍼관리자", role: "admin" };
  return <AuthContext.Provider value={{ user }}>{children}</AuthContext.Provider>;
}
export function useAuth() {
  return useContext(AuthContext);
} 