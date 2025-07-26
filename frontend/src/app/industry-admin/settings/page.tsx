'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';
import { 
  Settings, 
  Save, 
  RefreshCw, 
  Shield, 
  Bell, 
  Database,
  Users,
  Building2
} from 'lucide-react';

export default function IndustryAdminSettingsPage() {
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      // 실제 API 호출 시 수정
      // const response = await fetch('/api/industry/settings');
      // const data = await response.json();
      
      // 임시 데이터
      const data = {
        notifications: {
          email_enabled: true,
          sms_enabled: false,
          brand_creation_alerts: true,
          system_alerts: true
        },
        security: {
          two_factor_auth: false,
          session_timeout: 30,
          password_policy: 'strong'
        },
        branding: {
          company_name: '업종관리 시스템',
          logo_url: '/logo.png',
          primary_color: '#3b82f6'
        },
        limits: {
          max_brands_per_industry: 50,
          max_stores_per_brand: 100,
          max_employees_per_store: 50
        }
      };
      
      setSettings(data);
    } catch (error) {
      console.error('설정 로드 오류:', error);
      toast.error('설정을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    try {
      setSaving(true);
      // 실제 API 호출 시 수정
      // const response = await fetch('/api/industry/settings', {
      //   method: 'PUT',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(settings),
      // });
      
      // 임시 성공 처리
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success('설정이 성공적으로 저장되었습니다.');
    } catch (error) {
      console.error('설정 저장 오류:', error);
      toast.error('설정 저장 중 오류가 발생했습니다.');
    } finally {
      setSaving(false);
    }
  };

  const updateSetting = (section: string, key: string, value: any) => {
    setSettings((prev: any) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span>설정을 불러오는 중...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">업종관리자 설정</h1>
          <p className="text-gray-600 mt-2">시스템 설정 및 권한을 관리합니다.</p>
        </div>
        <Button onClick={saveSettings} disabled={saving} className="bg-blue-600 hover:bg-blue-700">
          {saving ? (
            <>
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              저장 중...
            </>
          ) : (
            <>
              <Save className="h-4 w-4 mr-2" />
              설정 저장
            </>
          )}
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 알림 설정 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Bell className="h-5 w-5 mr-2" />
              알림 설정
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="email-notifications">이메일 알림</Label>
              <Switch
                id="email-notifications"
                checked={settings?.notifications?.email_enabled}
                onCheckedChange={(checked) => updateSetting('notifications', 'email_enabled', checked)}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="sms-notifications">SMS 알림</Label>
              <Switch
                id="sms-notifications"
                checked={settings?.notifications?.sms_enabled}
                onCheckedChange={(checked) => updateSetting('notifications', 'sms_enabled', checked)}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="brand-alerts">브랜드 생성 알림</Label>
              <Switch
                id="brand-alerts"
                checked={settings?.notifications?.brand_creation_alerts}
                onCheckedChange={(checked) => updateSetting('notifications', 'brand_creation_alerts', checked)}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="system-alerts">시스템 알림</Label>
              <Switch
                id="system-alerts"
                checked={settings?.notifications?.system_alerts}
                onCheckedChange={(checked) => updateSetting('notifications', 'system_alerts', checked)}
              />
            </div>
          </CardContent>
        </Card>

        {/* 보안 설정 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="h-5 w-5 mr-2" />
              보안 설정
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="two-factor">2단계 인증</Label>
              <Switch
                id="two-factor"
                checked={settings?.security?.two_factor_auth}
                onCheckedChange={(checked) => updateSetting('security', 'two_factor_auth', checked)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="session-timeout">세션 타임아웃 (분)</Label>
              <Input
                id="session-timeout"
                type="number"
                value={settings?.security?.session_timeout}
                onChange={(e) => updateSetting('security', 'session_timeout', parseInt(e.target.value))}
                min="5"
                max="480"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password-policy">비밀번호 정책</Label>
              <select
                id="password-policy"
                value={settings?.security?.password_policy}
                onChange={(e) => updateSetting('security', 'password_policy', e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="basic">기본 (8자 이상)</option>
                <option value="strong">강력 (8자 이상, 특수문자 포함)</option>
                <option value="very-strong">매우 강력 (12자 이상, 특수문자, 숫자 포함)</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* 브랜딩 설정 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Building2 className="h-5 w-5 mr-2" />
              브랜딩 설정
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="company-name">회사명</Label>
              <Input
                id="company-name"
                value={settings?.branding?.company_name}
                onChange={(e) => updateSetting('branding', 'company_name', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="logo-url">로고 URL</Label>
              <Input
                id="logo-url"
                value={settings?.branding?.logo_url}
                onChange={(e) => updateSetting('branding', 'logo_url', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="primary-color">주요 색상</Label>
              <Input
                id="primary-color"
                type="color"
                value={settings?.branding?.primary_color}
                onChange={(e) => updateSetting('branding', 'primary_color', e.target.value)}
                className="h-10"
              />
            </div>
          </CardContent>
        </Card>

        {/* 제한 설정 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Users className="h-5 w-5 mr-2" />
              제한 설정
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="max-brands">업종당 최대 브랜드 수</Label>
              <Input
                id="max-brands"
                type="number"
                value={settings?.limits?.max_brands_per_industry}
                onChange={(e) => updateSetting('limits', 'max_brands_per_industry', parseInt(e.target.value))}
                min="1"
                max="1000"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="max-stores">브랜드당 최대 매장 수</Label>
              <Input
                id="max-stores"
                type="number"
                value={settings?.limits?.max_stores_per_brand}
                onChange={(e) => updateSetting('limits', 'max_stores_per_brand', parseInt(e.target.value))}
                min="1"
                max="1000"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="max-employees">매장당 최대 직원 수</Label>
              <Input
                id="max-employees"
                type="number"
                value={settings?.limits?.max_employees_per_store}
                onChange={(e) => updateSetting('limits', 'max_employees_per_store', parseInt(e.target.value))}
                min="1"
                max="1000"
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 시스템 정보 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Database className="h-5 w-5 mr-2" />
            시스템 정보
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium">서버 버전:</span> v1.0.0
            </div>
            <div>
              <span className="font-medium">데이터베이스:</span> SQLite
            </div>
            <div>
              <span className="font-medium">마지막 업데이트:</span> 2024-01-26
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 