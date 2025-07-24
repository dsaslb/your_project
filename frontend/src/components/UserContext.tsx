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
  // 인증 우회: 항상 children 렌더
  return <>{children}</>;
}

export function useUser() {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error("useUser must be used within a UserProvider");
  return ctx;
} 