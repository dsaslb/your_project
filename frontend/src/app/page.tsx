"use client"

import React from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Building2, 
  Store, 
  Users, 
  TrendingUp, 
  DollarSign, 
  ShoppingCart,
  ArrowRight,
  Home,
  BarChart3
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">🏢</div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">멀티테넌시 관리 시스템</h1>
                <p className="text-sm text-gray-500">레스토랑 업종 계층별 관리 시스템</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/login">
                <Button variant="outline" size="sm">
                  로그인
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto py-12 sm:px-6 lg:px-8">
        {/* 환영 메시지 */}
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            레스토랑 업종 관리 시스템에 오신 것을 환영합니다
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            업종, 브랜드, 매장, 직원의 계층적 구조를 효율적으로 관리할 수 있는 
            종합적인 관리 시스템입니다.
          </p>
        </div>

        {/* 계층 구조 설명 */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-12">
          <h3 className="text-xl font-semibold text-gray-900 mb-6 text-center">시스템 구조</h3>
          <div className="flex items-center justify-center space-x-8">
            <div className="text-center">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Building2 className="h-10 w-10 text-blue-600" />
              </div>
              <div className="text-lg font-medium">업종</div>
              <div className="text-sm text-gray-500">레스토랑 업종 전체</div>
            </div>
            
            <ArrowRight className="h-8 w-8 text-gray-400" />
            
            <div className="text-center">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Store className="h-10 w-10 text-green-600" />
              </div>
              <div className="text-lg font-medium">브랜드</div>
              <div className="text-sm text-gray-500">스타벅스, 맥도날드 등</div>
            </div>
            
            <ArrowRight className="h-8 w-8 text-gray-400" />
            
            <div className="text-center">
              <div className="w-20 h-20 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Home className="h-10 w-10 text-orange-600" />
              </div>
              <div className="text-lg font-medium">매장</div>
              <div className="text-sm text-gray-500">강남점, 홍대점 등</div>
            </div>
            
            <ArrowRight className="h-8 w-8 text-gray-400" />
            
            <div className="text-center">
              <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Users className="h-10 w-10 text-purple-600" />
              </div>
              <div className="text-lg font-medium">직원</div>
              <div className="text-sm text-gray-500">매니저, 서버 등</div>
            </div>
          </div>
        </div>

        {/* 관리자 페이지 카드들 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5 text-blue-600" />
                업종 관리자
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                업종 전체를 관리하고 모든 브랜드의 통계를 확인할 수 있습니다.
              </p>
              <Link href="/industry-admin">
                <Button className="w-full">
                  접속하기
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Store className="h-5 w-5 text-green-600" />
                브랜드 관리자
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                특정 브랜드의 매장과 직원을 관리할 수 있습니다.
              </p>
              <Link href="/brand-admin?brandId=1">
                <Button className="w-full">
                  접속하기
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Home className="h-5 w-5 text-orange-600" />
                매장 관리자
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                특정 매장의 직원과 운영을 관리할 수 있습니다.
              </p>
              <Link href="/branch-admin?branchId=1">
                <Button className="w-full">
                  접속하기
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-purple-600" />
                직원 대시보드
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                개별 직원이 자신의 업무와 성과를 확인할 수 있습니다.
              </p>
              <Link href="/staff?staffId=1">
                <Button className="w-full">
                  접속하기
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* 추가 기능들 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-blue-600" />
                계층 관리
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                브랜드, 매장, 직원의 계층적 구조를 한눈에 확인하고 관리할 수 있습니다.
              </p>
              <Link href="/restaurant/hierarchy">
                <Button variant="outline" className="w-full">
                  계층 관리 보기
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-600" />
                실시간 모니터링
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                매출, 주문, 직원 성과를 실시간으로 모니터링할 수 있습니다.
              </p>
              <Button variant="outline" className="w-full">
                모니터링 보기
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
