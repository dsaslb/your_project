"use client";
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, Lock, User } from "lucide-react";
import useUserStore from '@/store/useUserStore';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  
  const { 
    login, 
    error, 
    clearError, 
    isAuthenticated, 
    checkAuth 
  } = useUserStore();

  // 이미 인증된 사용자는 적절한 대시보드로 리다이렉트
  useEffect(() => {
    const checkAuthentication = async () => {
      const isAuth = await checkAuth();
      if (isAuth) {
        const { user } = useUserStore.getState();
        if (user) {
          const redirectMap = {
            'super_admin': '/admin-dashboard',
            'brand_manager': '/brand-dashboard',
            'store_manager': '/store-dashboard',
            'employee': '/dashboard'
          };
          const redirectTo = redirectMap[user.role] || '/dashboard';
          router.push(redirectTo);
        }
      }
    };

    checkAuthentication();
  }, [router, checkAuth]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    clearError();

    try {
      const result = await login(username, password);
      
      if (result.success && result.redirectTo) {
        router.push(result.redirectTo);
      } else if (result.success) {
        // 기본 리다이렉트
        router.push('/dashboard');
      }
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async (role: string) => {
    setIsLoading(true);
    clearError();

    // 데모 계정 정보
    const demoAccounts = {
      'super_admin': { username: 'admin', password: 'admin123' },
      'brand_manager': { username: 'brand', password: 'brand123' },
      'store_manager': { username: 'store', password: 'store123' },
      'employee': { username: 'employee', password: 'emp123' }
    };

    const account = demoAccounts[role as keyof typeof demoAccounts];
    if (account) {
      try {
        const result = await login(account.username, account.password);
        if (result.success && result.redirectTo) {
          router.push(result.redirectTo);
        }
      } catch (error) {
        console.error('Demo login error:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            레스토랑 관리 시스템
          </h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            계정에 로그인하여 시작하세요
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-center">로그인</CardTitle>
            <CardDescription className="text-center">
              사용자명과 비밀번호를 입력하세요
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Label htmlFor="username">사용자명</Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="사용자명을 입력하세요"
                    className="pl-10"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">비밀번호</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="비밀번호를 입력하세요"
                    className="pl-10"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full" 
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    로그인 중...
                  </>
                ) : (
                  '로그인'
                )}
              </Button>
            </form>

            {/* 데모 로그인 버튼들 */}
            <div className="mt-6 space-y-2">
              <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
                데모 계정으로 로그인:
              </p>
              <div className="grid grid-cols-2 gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDemoLogin('super_admin')}
                  disabled={isLoading}
                >
                  슈퍼 관리자
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDemoLogin('brand_manager')}
                  disabled={isLoading}
                >
                  브랜드 관리자
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDemoLogin('store_manager')}
                  disabled={isLoading}
                >
                  매장 관리자
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDemoLogin('employee')}
                  disabled={isLoading}
                >
                  직원
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            © 2024 레스토랑 관리 시스템. 모든 권리 보유.
          </p>
        </div>
      </div>
    </div>
  );
} 