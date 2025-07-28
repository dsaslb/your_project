'use client';
import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Clock, Users, Store, DollarSign } from 'lucide-react';

interface Brand {
  id: number;
  name: string;
  code: string;
  description: string;
  status: 'active' | 'inactive' | 'pending';
  store_count: number;
  employee_count: number;
  total_revenue: number;
  improvement_requests: number;
  ai_diagnoses: number;
  pending_approvals: number;
  last_activity: string;
}

interface BrandCardProps {
  brand: Brand;
  onClick: () => void;
}

export default function BrandCard({ brand, onClick }: BrandCardProps) {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">활성</Badge>;
      case 'inactive':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100">비활성</Badge>;
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">대기</Badge>;
      default:
        return <Badge variant="secondary">알 수 없음</Badge>;
    }
  };

  const getRevenueTrend = () => {
    // 임시로 랜덤 트렌드 생성
    const isPositive = Math.random() > 0.5;
    return (
      <div className="flex items-center text-sm">
        {isPositive ? (
          <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
        ) : (
          <TrendingDown className="w-4 h-4 text-red-500 mr-1" />
        )}
        <span className={isPositive ? 'text-green-600' : 'text-red-600'}>
          {isPositive ? '+' : '-'}{Math.floor(Math.random() * 15) + 5}%
        </span>
      </div>
    );
  };

  return (
    <Card 
      className="cursor-pointer hover:shadow-lg transition-shadow duration-200"
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">{brand.name}</CardTitle>
            <CardDescription className="text-sm text-gray-500">{brand.code}</CardDescription>
          </div>
          {getStatusBadge(brand.status)}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* 주요 지표 */}
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="flex items-center">
            <Store className="w-4 h-4 text-blue-500 mr-2" />
            <span>{brand.store_count}개</span>
          </div>
          <div className="flex items-center">
            <Users className="w-4 h-4 text-green-500 mr-2" />
            <span>{brand.employee_count}명</span>
          </div>
          <div className="flex items-center">
            <DollarSign className="w-4 h-4 text-purple-500 mr-2" />
            <span>{(brand.total_revenue || 0).toLocaleString()}원</span>
          </div>
        </div>

        {/* 매출 트렌드 */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">이번 달 매출</span>
          {getRevenueTrend()}
        </div>

        {/* 알림 및 개선사항 */}
        {(brand.improvement_requests > 0 || brand.ai_diagnoses > 0 || brand.pending_approvals > 0) && (
          <div className="space-y-2">
            {brand.improvement_requests > 0 && (
              <div className="flex items-center text-sm text-orange-600">
                <AlertTriangle className="w-4 h-4 mr-2" />
                <span>개선 요청 {brand.improvement_requests}건</span>
              </div>
            )}
            {brand.ai_diagnoses > 0 && (
              <div className="flex items-center text-sm text-blue-600">
                <CheckCircle className="w-4 h-4 mr-2" />
                <span>AI 진단 {brand.ai_diagnoses}건</span>
              </div>
            )}
            {brand.pending_approvals > 0 && (
              <div className="flex items-center text-sm text-yellow-600">
                <Clock className="w-4 h-4 mr-2" />
                <span>승인 대기 {brand.pending_approvals}건</span>
              </div>
            )}
          </div>
        )}

        {/* 마지막 활동 */}
        <div className="text-xs text-gray-500 pt-2 border-t">
          마지막 활동: {new Date(brand.last_activity).toLocaleDateString()}
        </div>
      </CardContent>
    </Card>
  );
} 