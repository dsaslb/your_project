"use client";
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/hooks/useUser';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ChefHat, Eye, EyeOff, Building2, Users, Clock, TrendingUp, Shield, Zap } from 'lucide-react';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentFeature, setCurrentFeature] = useState(0);
  
  const { login } = useUser();
  const router = useRouter();

  // 자동 슬라이드 기능
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % features.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const features = [
    {
      icon: Building2,
      title: "매장 관리",
      description: "다중 매장을 효율적으로 관리하고 모니터링하세요"
    },
    {
      icon: Users,
      title: "직원 관리",
      description: "스케줄링, 출근 관리, 성과 평가를 한 곳에서"
    },
    {
      icon: Clock,
      title: "실시간 모니터링",
      description: "매장 현황을 실시간으로 확인하고 대응하세요"
    },
    {
      icon: TrendingUp,
      title: "데이터 분석",
      description: "AI 기반 예측과 고급 분석으로 의사결정을 지원"
    },
    {
      icon: Shield,
      title: "보안 관리",
      description: "역할 기반 접근 제어로 안전한 시스템 운영"
    }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const success = await login(username, password);
      if (success) {
        // 권한별 라우팅
        const user = JSON.parse(localStorage.getItem('user') || 'null') || null;
        if (user) {
          if (user.role === 'super_admin' || user.role === 'admin') {
            router.push('/super-admin');
          } else if (user.role === 'manager') {
            router.push('/manager-dashboard');
          } else {
            router.push('/dashboard');
          }
        } else {
          router.push('/dashboard');
        }
      } else {
        setError('로그인에 실패했습니다. 사용자명과 비밀번호를 확인해주세요.');
      }
    } catch (err) {
      setError('로그인 중 오류가 발생했습니다. 다시 시도해주세요.');
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 빠른 로그인 버튼들 (개발용)
  const quickLogin = async (role: string) => {
    setUsername(role);
    setPassword('password');
    setIsLoading(true);
    
    try {
      const success = await login(role, 'password');
      if (success) {
        router.push('/dashboard');
      }
    } catch (err) {
      setError('빠른 로그인에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* 왼쪽 - 기능 소개 섹션 */}
      <div className="flex w-full md:w-1/2 min-h-screen items-center justify-center bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800">
        <div className="w-full max-w-lg px-6 py-12 flex flex-col justify-center items-center">
          {/* 로고 */}
          <div className="mb-8">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-xl">
                <ChefHat className="h-8 w-8 text-blue-600 dark:text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-blue-900 dark:text-white">Restaurant Manager</h1>
                <p className="text-blue-600 dark:text-blue-200">AI 기반 레스토랑 관리 시스템</p>
              </div>
            </div>
          </div>
          {/* 선명한 SVG 일러스트 */}
          <div className="flex justify-center mb-8">
            <svg width="220" height="140" viewBox="0 0 220 140" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="10" y="60" width="200" height="60" rx="12" fill="#fff" stroke="#6366f1" strokeWidth="2"/>
              <rect x="30" y="80" width="40" height="30" rx="6" fill="#6366f1" />
              <rect x="80" y="80" width="40" height="30" rx="6" fill="#fbbf24" />
              <rect x="130" y="80" width="40" height="30" rx="6" fill="#34d399" />
              <circle cx="60" cy="70" r="10" fill="#6366f1" />
              <circle cx="110" cy="70" r="10" fill="#fbbf24" />
              <circle cx="160" cy="70" r="10" fill="#34d399" />
              <rect x="60" y="40" width="100" height="20" rx="6" fill="#6366f1" fillOpacity="0.2" />
              <text x="110" y="55" textAnchor="middle" fontSize="14" fill="#6366f1">스마트 매장</text>
            </svg>
          </div>
          {/* 기능 소개 */}
          <div className="space-y-8">
            <h2 className="text-2xl font-semibold text-white mb-6">
              스마트한 레스토랑 관리의 시작
            </h2>
            
            <div className="space-y-6">
              {features.map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <div
                    key={index}
                    className={`flex items-start space-x-4 transition-all duration-500 ${
                      currentFeature === index 
                        ? 'opacity-100 transform translate-x-0' 
                        : 'opacity-60 transform translate-x-4'
                    }`}
                  >
                    <div className="p-3 bg-white/20 backdrop-blur-sm rounded-lg">
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-1">
                        {feature.title}
                      </h3>
                      <p className="text-blue-100 text-sm leading-relaxed">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 통계 */}
          <div className="mt-12 grid grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-white">500+</div>
              <div className="text-blue-100 text-sm">활성 매장</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">10K+</div>
              <div className="text-blue-100 text-sm">관리 직원</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">99.9%</div>
              <div className="text-blue-100 text-sm">시스템 가동률</div>
            </div>
          </div>
        </div>
      </div>

      {/* 오른쪽 - 로그인 폼 */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          {/* 모바일 로고 */}
          <div className="lg:hidden text-center">
            <div className="mx-auto h-16 w-16 flex items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 mb-4">
              <ChefHat className="h-8 w-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Restaurant Manager
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              AI 기반 레스토랑 관리 시스템
            </p>
          </div>

          {/* 로그인 카드 */}
          <Card className="border-0 shadow-2xl bg-white/80 backdrop-blur-sm dark:bg-gray-800/80">
            <CardHeader className="text-center pb-6">
              <CardTitle className="text-2xl font-bold text-gray-900 dark:text-white">
                로그인
              </CardTitle>
              <CardDescription className="text-gray-600 dark:text-gray-400">
                계정 정보를 입력하여 시스템에 접속하세요
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    사용자명
                  </Label>
                  <Input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="사용자명을 입력하세요"
                    required
                    disabled={isLoading}
                    className="h-12 border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    비밀번호
                  </Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="비밀번호를 입력하세요"
                      required
                      disabled={isLoading}
                      className="h-12 border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-12"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      disabled={isLoading}
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5" />
                      ) : (
                        <Eye className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </div>

                {error && (
                  <Alert variant="destructive" className="border-red-200 bg-red-50 dark:bg-red-900/20">
                    <AlertDescription className="text-red-800 dark:text-red-200">
                      {error}
                    </AlertDescription>
                  </Alert>
                )}

                <Button
                  type="submit"
                  className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-200 transform hover:scale-[1.02]"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>로그인 중...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <Zap className="h-4 w-4" />
                      <span>로그인</span>
                    </div>
                  )}
                </Button>
              </form>

              {/* 개발용 빠른 로그인 */}
              <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 text-center">
                  개발용 빠른 로그인
                </p>
                <div className="grid grid-cols-2 gap-3">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => quickLogin('admin')}
                    disabled={isLoading}
                    className="h-10 text-xs"
                  >
                    관리자
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => quickLogin('manager')}
                    disabled={isLoading}
                    className="h-10 text-xs"
                  >
                    매니저
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => quickLogin('employee')}
                    disabled={isLoading}
                    className="h-10 text-xs"
                  >
                    직원
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => quickLogin('super_admin')}
                    disabled={isLoading}
                    className="h-10 text-xs"
                  >
                    최고관리자
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 추가 정보 */}
          <div className="text-center space-y-2">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              © 2024 Restaurant Management System. All rights reserved.
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500">
              AI 기반 스마트 레스토랑 관리 솔루션
            </p>
          </div>
        </div>
      </div>
    </div>
  );
} 