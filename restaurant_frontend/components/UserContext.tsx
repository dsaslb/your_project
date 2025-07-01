'use client';
import React, { createContext, useContext, useState, ReactNode } from 'react';

// User 타입 정의
export type User = {
  id: string;
  name: string;
  role: 'admin' | 'manager' | 'employee';
  permissions: {
    dashboard: boolean;
    schedule: boolean;
    orders: boolean;
    inventory: boolean;
    reports: boolean;
    settings: boolean;
    [key: string]: boolean;
  };
  storeId?: string; // 최고관리자는 전체 매장 접근 가능, 나머지는 본인 매장만
};

// 더미 유저 정보(테스트용)
const defaultUser: User = {
  id: '1',
  name: '최고관리자',
  role: 'admin',
  permissions: {
    dashboard: true,
    schedule: true,
    orders: true,
    inventory: true,
    reports: true,
    settings: true,
  },
};

// Context 생성
const UserContext = createContext<{
  user: User;
  setUser: (user: User) => void;
}>({
  user: defaultUser,
  setUser: () => {},
});

// Provider 컴포넌트
export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User>(defaultUser);
  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
}

// useUser 커스텀 훅
export function useUser() {
  return useContext(UserContext);
} 