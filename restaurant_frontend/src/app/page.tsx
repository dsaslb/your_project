'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Crown, Building2, Store, User, Activity } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">
          🍽️ 레스토랑 관리 시스템
        </h1>
        <p className="text-slate-300 text-lg mb-8">
          4단계 계층별 통합 관리 플랫폼
        </p>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-800/50 p-4 rounded-lg">
            <h2 className="text-white font-semibold">업종별 관리자</h2>
            <p className="text-slate-400 text-sm">전체 업종 통합 관리</p>
          </div>
          <div className="bg-slate-800/50 p-4 rounded-lg">
            <h2 className="text-white font-semibold">브랜드별 관리자</h2>
            <p className="text-slate-400 text-sm">브랜드별 운영 관리</p>
          </div>
          <div className="bg-slate-800/50 p-4 rounded-lg">
            <h2 className="text-white font-semibold">매장별 관리자</h2>
            <p className="text-slate-400 text-sm">개별 매장 실시간 운영</p>
          </div>
          <div className="bg-slate-800/50 p-4 rounded-lg">
            <h2 className="text-white font-semibold">직원 개인</h2>
            <p className="text-slate-400 text-sm">개인 업무 현황 관리</p>
          </div>
        </div>
        <p className="text-slate-400 text-sm mt-8">
          포트 3001에서 실행 중 | Next.js 15.3.5
        </p>
      </div>
    </div>
  );
}
