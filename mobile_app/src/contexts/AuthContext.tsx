import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Alert } from 'react-native';
import { API_BASE_URL } from '../utils/config';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  avatar?: string;
  unreadNotifications: number;
  lastLogin: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<boolean>;
  updateProfile: (data: Partial<User>) => Promise<boolean>;
  refreshToken: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [token, setToken] = useState<string | null>(null);

  // 토큰 저장
  const storeToken = async (newToken: string) => {
    try {
      await AsyncStorage.setItem('auth_token', newToken);
      setToken(newToken);
    } catch (error) {
      console.error('토큰 저장 오류:', error);
    }
  };

  // 토큰 로드
  const loadToken = async () => {
    try {
      const storedToken = await AsyncStorage.getItem('auth_token');
      if (storedToken) {
        setToken(storedToken);
        return storedToken;
      }
    } catch (error) {
      console.error('토큰 로드 오류:', error);
    }
    return null;
  };

  // 토큰 제거
  const removeToken = async () => {
    try {
      await AsyncStorage.removeItem('auth_token');
      setToken(null);
    } catch (error) {
      console.error('토큰 제거 오류:', error);
    }
  };

  // 사용자 정보 가져오기
  const fetchUserInfo = async (authToken: string): Promise<User | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const userData = await response.json();
        return userData;
      } else {
        throw new Error('사용자 정보를 가져올 수 없습니다');
      }
    } catch (error) {
      console.error('사용자 정보 가져오기 오류:', error);
      return null;
    }
  };

  // 로그인
  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true);

      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        await storeToken(data.token);
        
        const userInfo = await fetchUserInfo(data.token);
        if (userInfo) {
          setUser(userInfo);
          return true;
        }
      } else {
        const errorData = await response.json();
        Alert.alert('로그인 실패', errorData.message || '로그인에 실패했습니다.');
      }
    } catch (error) {
      console.error('로그인 오류:', error);
      Alert.alert('로그인 오류', '네트워크 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
    return false;
  };

  // 로그아웃
  const logout = async (): Promise<void> => {
    try {
      if (token) {
        // 서버에 로그아웃 요청
        await fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (error) {
      console.error('로그아웃 오류:', error);
    } finally {
      setUser(null);
      await removeToken();
    }
  };

  // 회원가입
  const register = async (email: string, password: string, name: string): Promise<boolean> => {
    try {
      setIsLoading(true);

      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, name }),
      });

      if (response.ok) {
        const data = await response.json();
        await storeToken(data.token);
        
        const userInfo = await fetchUserInfo(data.token);
        if (userInfo) {
          setUser(userInfo);
          return true;
        }
      } else {
        const errorData = await response.json();
        Alert.alert('회원가입 실패', errorData.message || '회원가입에 실패했습니다.');
      }
    } catch (error) {
      console.error('회원가입 오류:', error);
      Alert.alert('회원가입 오류', '네트워크 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
    return false;
  };

  // 프로필 업데이트
  const updateProfile = async (data: Partial<User>): Promise<boolean> => {
    try {
      if (!token) return false;

      const response = await fetch(`${API_BASE_URL}/api/auth/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        const updatedUser = await response.json();
        setUser(updatedUser);
        return true;
      } else {
        const errorData = await response.json();
        Alert.alert('프로필 업데이트 실패', errorData.message || '프로필 업데이트에 실패했습니다.');
      }
    } catch (error) {
      console.error('프로필 업데이트 오류:', error);
      Alert.alert('프로필 업데이트 오류', '네트워크 오류가 발생했습니다.');
    }
    return false;
  };

  // 토큰 갱신
  const refreshToken = async (): Promise<boolean> => {
    try {
      if (!token) return false;

      const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        await storeToken(data.token);
        return true;
      } else {
        // 토큰이 만료된 경우 로그아웃
        await logout();
        return false;
      }
    } catch (error) {
      console.error('토큰 갱신 오류:', error);
      await logout();
      return false;
    }
  };

  // 초기화
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedToken = await loadToken();
        if (storedToken) {
          const userInfo = await fetchUserInfo(storedToken);
          if (userInfo) {
            setUser(userInfo);
          } else {
            // 토큰이 유효하지 않은 경우 제거
            await removeToken();
          }
        }
      } catch (error) {
        console.error('인증 초기화 오류:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // 토큰 자동 갱신
  useEffect(() => {
    if (!token) return;

    const refreshInterval = setInterval(async () => {
      const success = await refreshToken();
      if (!success) {
        clearInterval(refreshInterval);
      }
    }, 14 * 60 * 1000); // 14분마다 갱신

    return () => clearInterval(refreshInterval);
  }, [token]);

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    logout,
    register,
    updateProfile,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 