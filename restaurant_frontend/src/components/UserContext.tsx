"use client";
import React, { createContext, useContext, useEffect, useState } from "react";

interface User {
  id: string;
  username?: string;
  name?: string;
  role?: string;
  branch_id?: number;
}

interface UserContextType {
  user: User | null;
  login: (user: User) => void;
  logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  // localStorage에서 자동 로드 기능을 임시로 비활성화
  // useEffect(() => {
  //   const stored = localStorage.getItem("user");
  //   if (stored) setUser(JSON.parse(stored));
  // }, []);

  const login = (user: User) => {
    setUser(user);
    localStorage.setItem("user", JSON.stringify(user));
  };
  const logout = () => {
    setUser(null);
    localStorage.removeItem("user");
  };

  return (
    <UserContext.Provider value={{ user, login, logout }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error("useUser must be used within a UserProvider");
  return ctx;
} 