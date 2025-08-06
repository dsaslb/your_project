"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Settings, User, Bell, Shield } from 'lucide-react';

export default function SettingsPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">설정</h1>
        <p className="text-gray-600">사용자 설정 및 시스템 설정</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border border-gray-100">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              프로필 설정
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">이름</label>
                <input 
                  type="text" 
                  className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md"
                  defaultValue="김철수"
                />
              </div>
              <div>
                <label className="text-sm font-medium">이메일</label>
                <input 
                  type="email" 
                  className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md"
                  defaultValue="kim@example.com"
                />
              </div>
              <div>
                <label className="text-sm font-medium">전화번호</label>
                <input 
                  type="tel" 
                  className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md"
                  defaultValue="010-1234-5678"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              알림 설정
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">이메일 알림</span>
                <input type="checkbox" defaultChecked className="rounded" />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">푸시 알림</span>
                <input type="checkbox" defaultChecked className="rounded" />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">SMS 알림</span>
                <input type="checkbox" className="rounded" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              보안 설정
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">현재 비밀번호</label>
                <input 
                  type="password" 
                  className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="현재 비밀번호 입력"
                />
              </div>
              <div>
                <label className="text-sm font-medium">새 비밀번호</label>
                <input 
                  type="password" 
                  className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="새 비밀번호 입력"
                />
              </div>
              <div>
                <label className="text-sm font-medium">비밀번호 확인</label>
                <input 
                  type="password" 
                  className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="새 비밀번호 재입력"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              시스템 설정
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">언어</label>
                <select className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md">
                  <option>한국어</option>
                  <option>English</option>
                  <option>日本語</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">시간대</label>
                <select className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md">
                  <option>Asia/Seoul (UTC+9)</option>
                  <option>UTC</option>
                  <option>America/New_York</option>
                </select>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">다크 모드</span>
                <input type="checkbox" className="rounded" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 