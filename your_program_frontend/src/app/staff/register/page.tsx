"use client";
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Smartphone, Monitor, FileText, UserPlus } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function StaffRegisterPage() {
  const router = useRouter();

  const handleMobileContract = () => {
    router.push('/staff/contract/mobile');
  };
  
  const handleDesktopContract = () => {
    router.push('/staff/contract');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="px-4 py-4">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.back()}
              className="p-2"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-lg font-bold text-gray-900 dark:text-white">새직원 등록</h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">계약서 작성 방식을 선택하세요</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <UserPlus className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              계약서 작성 방식 선택
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              새직원 등록을 위한 계약서 작성 방식을 선택해주세요.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 모바일용 계약서 */}
            <Card className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-blue-500 dark:hover:border-blue-400">
              <CardHeader className="text-center">
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Smartphone className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <CardTitle className="text-lg">모바일용 계약서</CardTitle>
                <CardDescription>
                  터치 친화적인 모바일 최적화 인터페이스
                </CardDescription>
              </CardHeader>
              <CardContent className="text-center">
                <div className="space-y-3 mb-6">
                  <div className="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    단계별 간편 입력
                  </div>
                  <div className="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    터치 사인 패드
                  </div>
                  <div className="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    빠른 설정 적용
                  </div>
                  <div className="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    직원 자동 등록
                  </div>
                </div>
                <Button 
                  onClick={handleMobileContract}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  <Smartphone className="h-4 w-4 mr-2" />
                  모바일용 선택
                </Button>
              </CardContent>
            </Card>

            {/* 컴퓨터용 계약서 */}
            <Card className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-green-500 dark:hover:border-green-400">
              <CardHeader className="text-center">
                <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Monitor className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <CardTitle className="text-lg">컴퓨터용 계약서</CardTitle>
                <CardDescription>
                  데스크톱에 최적화된 상세한 계약서 작성
                </CardDescription>
              </CardHeader>
              <CardContent className="text-center">
                <div className="space-y-3 mb-6">
                  <div className="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    상세한 정보 입력
                  </div>
                  <div className="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    마우스 사인 패드
                  </div>
                  <div className="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    고급 설정 옵션
                  </div>
                  <div className="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    계약서 미리보기
                  </div>
                </div>
                <Button 
                  onClick={handleDesktopContract}
                  className="w-full bg-green-600 hover:bg-green-700"
                >
                  <Monitor className="h-4 w-4 mr-2" />
                  컴퓨터용 선택
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* 추가 정보 */}
          <div className="mt-8 text-center">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                💡 선택 가이드
              </h3>
              <div className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                <p><strong>모바일용:</strong> 스마트폰이나 태블릿에서 사용하거나 빠른 계약서 작성 시</p>
                <p><strong>컴퓨터용:</strong> 상세한 정보 입력이나 복잡한 계약 조건 설정 시</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 