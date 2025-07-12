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

export const useUser = () => {
  const { user, isLoading, isAuthenticated, login: authLogin, logout: authLogout } = useAuth();
  const { setUser } = useAuthStore();

  // 더미 사용자 데이터 즉시 설정 (개발용)
  useEffect(() => {
    if (!user && !isLoading) {
      const dummyUser = {
        id: 1,
        username: 'admin',
        name: '관리자',
        email: 'admin@example.com',
        role: UserRole.SUPER_ADMIN,
        permissions: Object.values(Permission),
        created_at: new Date().toISOString(),
        last_login: new Date().toISOString()
      };
      setUser(dummyUser); // 즉시 세팅
    }
  }, [user, isLoading, setUser]);

  // useAuth의 사용자 정보를 useUser 형식으로 변환
  const convertedUser: User | null = user ? {
    id: user.id,
    username: user.username,
    name: user.name,
    email: user.email,
    role: user.role,
    permissions: user.permissions
  } : null;

  const login = async (username: string, password: string): Promise<boolean> => {
    return await authLogin(username, password);
  };

  const logout = () => {
    authLogout();
  };

  const updateUser = (userData: Partial<User>) => {
    // useAuth에서는 직접적인 사용자 업데이트가 제한적이므로
    // 실제로는 refreshUser를 호출하는 것이 좋습니다
    console.log('User update requested:', userData);
  };

  return {
    user: convertedUser,
    loading: isLoading || !convertedUser, // 유저가 세팅될 때까지 loading 처리
    error: null,
    login,
    logout,
    updateUser
  };
}; 
