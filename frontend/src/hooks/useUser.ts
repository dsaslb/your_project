import { UserRole, Permission } from '@/lib/auth';
import { useEffect } from 'react';

interface User {
  id: number;
  username: string;
  name: string;
  email: string;
  role: 'super_admin' | 'brand_manager' | 'store_manager' | 'employee';
  permissions: string[];
}

// 임시로 비활성화 - useAuth 문제 해결 필요
export const useUser = () => {
  // 더미 사용자 데이터 반환
  const dummyUser: User = {
    id: 1,
    username: 'admin',
    name: '관리자',
    email: 'admin@example.com',
    role: 'super_admin',
    permissions: Object.values(Permission)
  };

  const login = async (username: string, password: string): Promise<boolean> => {
    console.log('Login attempt:', username);
    return true;
  };

  const logout = () => {
    console.log('Logout');
  };

  const updateUser = (userData: Partial<User>) => {
    console.log('User update requested:', userData);
  };

  return {
    user: dummyUser,
    loading: false,
    error: null,
    login,
    logout,
    updateUser
  };
}; 
