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
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* 환영 메시지 */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-2xl flex items-center justify-center mr-4">
              <Building2 className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-900">퀀텀 멀티테넌시</h1>
              <p className="text-lg text-gray-600">레스토랑 업종 계층별 관리 시스템</p>
            </div>
          </div>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            업종, 브랜드, 매장, 직원의 계층적 구조를 효율적으로 관리할 수 있는 
            종합적인 관리 시스템입니다.
          </p>
        </div>

        {/* 계층 구조 설명 */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-12 border border-gray-100">
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
          <Card className="hover:shadow-lg transition-all duration-300 border border-gray-100">
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
                <Button className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700">
                  접속하기
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-all duration-300 border border-gray-100">
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
                <Button className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700">
                  접속하기
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-all duration-300 border border-gray-100">
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
                <Button className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700">
                  접속하기
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-all duration-300 border border-gray-100">
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
                <Button className="w-full bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700">
                  접속하기
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* 추가 기능들 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="border border-gray-100">
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
                <Button variant="outline" className="w-full border-blue-200 text-blue-600 hover:bg-blue-50">
                  계층 관리 보기
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="border border-gray-100">
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
              <Button variant="outline" className="w-full border-green-200 text-green-600 hover:bg-green-50">
                모니터링 보기
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
