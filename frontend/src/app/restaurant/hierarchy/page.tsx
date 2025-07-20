"use client";

import React, { useState } from 'react';
import { RestaurantHierarchy } from '@/components/RestaurantHierarchy/RestaurantHierarchy';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Building2, 
  Store, 
  Users, 
  TrendingUp, 
  DollarSign, 
  ShoppingCart,
  ArrowLeft,
  ArrowRight,
  Home
} from 'lucide-react';
import Link from 'next/link';

export default function RestaurantHierarchyPage() {
  const [currentLevel, setCurrentLevel] = useState<'brand' | 'branch' | 'staff'>('brand');
  const [selectedId, setSelectedId] = useState<number | undefined>();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">🍽️</div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">레스토랑 계층 관리</h1>
                <p className="text-sm text-gray-500">브랜드 &gt; 매장 &gt; 직원 계층별 관리</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/">
                <Button variant="outline" size="sm">
                  <Home className="h-4 w-4 mr-2" />
                  홈으로
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* 브레드크럼 */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center space-x-2 py-3">
            <Link href="/" className="text-gray-500 hover:text-gray-700">
              홈
            </Link>
            <ArrowLeft className="h-4 w-4 text-gray-400" />
            <span className="text-gray-900 font-medium">레스토랑 계층 관리</span>
          </div>
        </div>
      </nav>

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* 계층별 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">전체 브랜드</CardTitle>
              <Store className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">12개</div>
              <p className="text-xs text-muted-foreground">
                활성 브랜드 수
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">전체 매장</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">156개</div>
              <p className="text-xs text-muted-foreground">
                운영 중인 매장
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">전체 직원</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,234명</div>
              <p className="text-xs text-muted-foreground">
                근무 중인 직원
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">오늘 매출</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">₩45,678,900</div>
              <p className="text-xs text-muted-foreground">
                +12.5% from yesterday
              </p>
            </CardContent>
          </Card>
        </div>

        {/* 계층별 네비게이션 */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold">계층별 관리</h2>
            <p className="text-sm text-gray-600">브랜드, 매장, 직원을 계층적으로 관리하세요</p>
          </div>
          <div className="p-6">
            <div className="flex space-x-4">
              <Button
                variant={currentLevel === 'brand' ? 'default' : 'outline'}
                onClick={() => setCurrentLevel('brand')}
                className="flex items-center gap-2"
              >
                <Store className="h-4 w-4" />
                브랜드 관리
              </Button>
              <Button
                variant={currentLevel === 'branch' ? 'default' : 'outline'}
                onClick={() => setCurrentLevel('branch')}
                className="flex items-center gap-2"
              >
                <Building2 className="h-4 w-4" />
                매장 관리
              </Button>
              <Button
                variant={currentLevel === 'staff' ? 'default' : 'outline'}
                onClick={() => setCurrentLevel('staff')}
                className="flex items-center gap-2"
              >
                <Users className="h-4 w-4" />
                직원 관리
              </Button>
            </div>
          </div>
        </div>

        {/* 계층 구조 설명 */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-semibold">계층 구조</h3>
          </div>
          <div className="p-6">
            <div className="flex items-center justify-center space-x-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <Store className="h-8 w-8 text-blue-600" />
                </div>
                <div className="text-sm font-medium">브랜드</div>
                <div className="text-xs text-gray-500">스타벅스, 맥도날드 등</div>
              </div>
              
              <ArrowRight className="h-6 w-6 text-gray-400" />
              
              <div className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <Building2 className="h-8 w-8 text-green-600" />
                </div>
                <div className="text-sm font-medium">매장</div>
                <div className="text-xs text-gray-500">강남점, 홍대점 등</div>
              </div>
              
              <ArrowRight className="h-6 w-6 text-gray-400" />
              
              <div className="text-center">
                <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <Users className="h-8 w-8 text-orange-600" />
                </div>
                <div className="text-sm font-medium">직원</div>
                <div className="text-xs text-gray-500">매니저, 서버 등</div>
              </div>
            </div>
          </div>
        </div>

        {/* 계층별 관리 컴포넌트 */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-semibold">
              {currentLevel === 'brand' && '브랜드별 관리'}
              {currentLevel === 'branch' && '매장별 관리'}
              {currentLevel === 'staff' && '직원별 관리'}
            </h3>
          </div>
          <div className="p-6">
            <RestaurantHierarchy 
              currentLevel={currentLevel}
              selectedId={selectedId}
            />
          </div>
        </div>

        {/* 빠른 액션 */}
        <div className="mt-6 bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-semibold">빠른 액션</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                <Store className="h-6 w-6 mb-2" />
                <span className="text-sm">새 브랜드 추가</span>
              </Button>
              <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                <Building2 className="h-6 w-6 mb-2" />
                <span className="text-sm">새 매장 등록</span>
              </Button>
              <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                <Users className="h-6 w-6 mb-2" />
                <span className="text-sm">직원 등록</span>
              </Button>
              <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                <TrendingUp className="h-6 w-6 mb-2" />
                <span className="text-sm">성과 리포트</span>
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 