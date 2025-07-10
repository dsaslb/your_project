"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import {
  Settings,
  Store,
  Bell,
  Shield,
  Database,
  Palette,
  Globe,
  Save,
  Download,
  Upload,
  Trash2,
  Users,
  Clock,
  MapPin,
  Phone,
  Mail,
  CreditCard,
  FileText,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Eye,
  EyeOff,
  Key,
  User,
  Building,
  Calendar,
  DollarSign,
  Percent,
  Package,
  Truck,
  Receipt,
  BarChart3,
  Lock,
  Unlock,
  RefreshCw,
  Archive,
  History,
} from "lucide-react";

// 설정 데이터 타입 정의
interface YourProgramSettings {
  basic: {
    name: string;
    address: string;
    phone: string;
    email: string;
    website: string;
    description: string;
    logo: string;
  };
  business: {
    timezone: string;
    language: string;
    currency: string;
    taxRate: number;
    serviceCharge: number;
    operatingHours: {
      monday: { open: string; close: string; closed: boolean };
      tuesday: { open: string; close: string; closed: boolean };
      wednesday: { open: string; close: string; closed: boolean };
      thursday: { open: string; close: string; closed: boolean };
      friday: { open: string; close: string; closed: boolean };
      saturday: { open: string; close: string; closed: boolean };
      sunday: { open: string; close: string; closed: boolean };
    };
  };
  notifications: {
    newOrder: boolean;
    lowInventory: boolean;
    staffAttendance: boolean;
    dailyReport: boolean;
    weeklyReport: boolean;
    monthlyReport: boolean;
    paymentAlerts: boolean;
    systemAlerts: boolean;
  };
  security: {
    passwordPolicy: {
      minLength: number;
      requireUppercase: boolean;
      requireLowercase: boolean;
      requireNumbers: boolean;
      requireSpecialChars: boolean;
      expiryDays: number;
    };
    sessionTimeout: number;
    twoFactorAuth: boolean;
    loginAttempts: number;
    lockoutDuration: number;
  };
  appearance: {
    theme: "light" | "dark" | "system";
    primaryColor: string;
    sidebarCollapsed: boolean;
    compactMode: boolean;
    showAnimations: boolean;
  };
  backup: {
    autoBackup: boolean;
    backupFrequency: "daily" | "weekly" | "monthly";
    backupTime: string;
    retentionDays: number;
    cloudBackup: boolean;
  };
}

// 기본 설정 데이터
const defaultSettings: YourProgramSettings = {
  basic: {
    name: "맛있는 레스토랑",
    address: "서울시 강남구 테헤란로 123",
    phone: "02-1234-5678",
    email: "info@your_program.com",
    website: "https://your_program.com",
    description: "최고의 맛과 서비스를 제공하는 레스토랑입니다.",
    logo: "",
  },
  business: {
    timezone: "Asia/Seoul",
    language: "ko",
    currency: "KRW",
    taxRate: 10,
    serviceCharge: 5,
    operatingHours: {
      monday: { open: "09:00", close: "22:00", closed: false },
      tuesday: { open: "09:00", close: "22:00", closed: false },
      wednesday: { open: "09:00", close: "22:00", closed: false },
      thursday: { open: "09:00", close: "22:00", closed: false },
      friday: { open: "09:00", close: "23:00", closed: false },
      saturday: { open: "10:00", close: "23:00", closed: false },
      sunday: { open: "10:00", close: "21:00", closed: false },
    },
  },
  notifications: {
    newOrder: true,
    lowInventory: true,
    staffAttendance: false,
    dailyReport: true,
    weeklyReport: true,
    monthlyReport: true,
    paymentAlerts: true,
    systemAlerts: true,
  },
  security: {
    passwordPolicy: {
      minLength: 8,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecialChars: true,
      expiryDays: 90,
    },
    sessionTimeout: 30,
    twoFactorAuth: false,
    loginAttempts: 5,
    lockoutDuration: 15,
  },
  appearance: {
    theme: "system",
    primaryColor: "#3b82f6",
    sidebarCollapsed: false,
    compactMode: false,
    showAnimations: true,
  },
  backup: {
    autoBackup: true,
    backupFrequency: "daily",
    backupTime: "02:00",
    retentionDays: 30,
    cloudBackup: false,
  },
};

export default function SettingsPage() {
  const [settings, setSettings] = useState<YourProgramSettings>(defaultSettings);
  const [activeTab, setActiveTab] = useState("basic");
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // 설정 저장
  const handleSave = async (section: keyof YourProgramSettings) => {
    setIsLoading(true);
    try {
      // API 호출 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast("설정이 저장되었습니다.", {
        description: `${section} 설정이 성공적으로 업데이트되었습니다.`,
      });
    } catch (error) {
      toast("저장 실패", {
        description: "설정 저장 중 오류가 발생했습니다.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 전체 설정 저장
  const handleSaveAll = async () => {
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      toast("모든 설정이 저장되었습니다.", {
        description: "모든 설정이 성공적으로 업데이트되었습니다.",
      });
    } catch (error) {
      toast("저장 실패", {
        description: "설정 저장 중 오류가 발생했습니다.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 설정 초기화
  const handleReset = () => {
    setSettings(defaultSettings);
    toast("설정이 초기화되었습니다.", {
      description: "모든 설정이 기본값으로 되돌아갔습니다.",
    });
  };

  // 백업 생성
  const handleBackup = async () => {
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast("백업이 생성되었습니다.", {
        description: "설정 백업 파일이 다운로드되었습니다.",
      });
    } catch (error) {
      toast("백업 실패", {
        description: "백업 생성 중 오류가 발생했습니다.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">설정</h1>
          <p className="text-muted-foreground">
            시스템 설정을 관리하고 환경을 구성하세요.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleReset}>
            <RefreshCw className="h-4 w-4 mr-2" />
            초기화
          </Button>
          <Button variant="outline" onClick={handleBackup} disabled={isLoading}>
            <Download className="h-4 w-4 mr-2" />
            백업
          </Button>
          <Button onClick={handleSaveAll} disabled={isLoading}>
            <Save className="h-4 w-4 mr-2" />
            {isLoading ? "저장 중..." : "모든 설정 저장"}
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="basic" className="flex items-center gap-2">
            <Store className="h-4 w-4" />
            기본 정보
          </TabsTrigger>
          <TabsTrigger value="business" className="flex items-center gap-2">
            <Building className="h-4 w-4" />
            영업 설정
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            알림 설정
          </TabsTrigger>
          <TabsTrigger value="security" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            보안 설정
          </TabsTrigger>
          <TabsTrigger value="appearance" className="flex items-center gap-2">
            <Palette className="h-4 w-4" />
            외관 설정
          </TabsTrigger>
          <TabsTrigger value="backup" className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            백업/복원
          </TabsTrigger>
        </TabsList>

        {/* 기본 정보 설정 */}
        <TabsContent value="basic" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Store className="h-5 w-5" />
                매장 기본 정보
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">매장명 *</Label>
                  <Input
                    id="name"
                    value={settings.basic.name}
                    onChange={(e) => setSettings({
                      ...settings,
                      basic: { ...settings.basic, name: e.target.value }
                    })}
                    placeholder="매장명을 입력하세요"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">연락처 *</Label>
                  <Input
                    id="phone"
                    value={settings.basic.phone}
                    onChange={(e) => setSettings({
                      ...settings,
                      basic: { ...settings.basic, phone: e.target.value }
                    })}
                    placeholder="02-1234-5678"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">이메일 *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={settings.basic.email}
                    onChange={(e) => setSettings({
                      ...settings,
                      basic: { ...settings.basic, email: e.target.value }
                    })}
                    placeholder="info@your_program.com"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="website">웹사이트</Label>
                  <Input
                    id="website"
                    value={settings.basic.website}
                    onChange={(e) => setSettings({
                      ...settings,
                      basic: { ...settings.basic, website: e.target.value }
                    })}
                    placeholder="https://your_program.com"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="address">매장 주소 *</Label>
                <Input
                  id="address"
                  value={settings.basic.address}
                  onChange={(e) => setSettings({
                    ...settings,
                    basic: { ...settings.basic, address: e.target.value }
                  })}
                  placeholder="서울시 강남구 테헤란로 123"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">매장 설명</Label>
                <Textarea
                  id="description"
                  value={settings.basic.description}
                  onChange={(e) => setSettings({
                    ...settings,
                    basic: { ...settings.basic, description: e.target.value }
                  })}
                  placeholder="매장에 대한 설명을 입력하세요"
                  rows={3}
                />
              </div>
              <Button onClick={() => handleSave("basic")} disabled={isLoading}>
                <Save className="h-4 w-4 mr-2" />
                기본 정보 저장
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 영업 설정 */}
        <TabsContent value="business" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building className="h-5 w-5" />
                영업 설정
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>시간대</Label>
                  <Select
                    value={settings.business.timezone}
                    onValueChange={(value: string) => setSettings({
                      ...settings,
                      business: { ...settings.business, timezone: value }
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Asia/Seoul">한국 표준시 (UTC+9)</SelectItem>
                      <SelectItem value="UTC">UTC</SelectItem>
                      <SelectItem value="America/New_York">미국 동부시 (UTC-5)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>언어</Label>
                  <Select
                    value={settings.business.language}
                    onValueChange={(value: string) => setSettings({
                      ...settings,
                      business: { ...settings.business, language: value }
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ko">한국어</SelectItem>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="ja">日本語</SelectItem>
                      <SelectItem value="zh">中文</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>통화</Label>
                  <Select
                    value={settings.business.currency}
                    onValueChange={(value: string) => setSettings({
                      ...settings,
                      business: { ...settings.business, currency: value }
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="KRW">원 (₩)</SelectItem>
                      <SelectItem value="USD">달러 ($)</SelectItem>
                      <SelectItem value="EUR">유로 (€)</SelectItem>
                      <SelectItem value="JPY">엔 (¥)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Separator />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="taxRate">부가세율 (%)</Label>
                  <Input
                    id="taxRate"
                    type="number"
                    value={settings.business.taxRate}
                    onChange={(e) => setSettings({
                      ...settings,
                      business: { ...settings.business, taxRate: Number(e.target.value) }
                    })}
                    min="0"
                    max="100"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="serviceCharge">봉사료 (%)</Label>
                  <Input
                    id="serviceCharge"
                    type="number"
                    value={settings.business.serviceCharge}
                    onChange={(e) => setSettings({
                      ...settings,
                      business: { ...settings.business, serviceCharge: Number(e.target.value) }
                    })}
                    min="0"
                    max="100"
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">영업 시간</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(settings.business.operatingHours).map(([day, hours]) => (
                    <div key={day} className="flex items-center gap-4 p-4 border rounded-lg">
                      <div className="w-20 font-medium">
                        {day === 'monday' && '월요일'}
                        {day === 'tuesday' && '화요일'}
                        {day === 'wednesday' && '수요일'}
                        {day === 'thursday' && '목요일'}
                        {day === 'friday' && '금요일'}
                        {day === 'saturday' && '토요일'}
                        {day === 'sunday' && '일요일'}
                      </div>
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={!hours.closed}
                          onCheckedChange={(checked) => setSettings({
                            ...settings,
                            business: {
                              ...settings.business,
                              operatingHours: {
                                ...settings.business.operatingHours,
                                [day]: { ...hours, closed: !checked }
                              }
                            }
                          })}
                        />
                        {!hours.closed && (
                          <>
                            <Input
                              type="time"
                              value={hours.open}
                              onChange={(e) => setSettings({
                                ...settings,
                                business: {
                                  ...settings.business,
                                  operatingHours: {
                                    ...settings.business.operatingHours,
                                    [day]: { ...hours, open: e.target.value }
                                  }
                                }
                              })}
                              className="w-24"
                            />
                            <span>~</span>
                            <Input
                              type="time"
                              value={hours.close}
                              onChange={(e) => setSettings({
                                ...settings,
                                business: {
                                  ...settings.business,
                                  operatingHours: {
                                    ...settings.business.operatingHours,
                                    [day]: { ...hours, close: e.target.value }
                                  }
                                }
                              })}
                              className="w-24"
                            />
                          </>
                        )}
                        {hours.closed && <span className="text-muted-foreground">휴무</span>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <Button onClick={() => handleSave("business")} disabled={isLoading}>
                <Save className="h-4 w-4 mr-2" />
                영업 설정 저장
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 알림 설정 */}
        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                알림 설정
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                {Object.entries(settings.notifications).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-medium">
                        {key === 'newOrder' && '새 주문 알림'}
                        {key === 'lowInventory' && '재고 부족 알림'}
                        {key === 'staffAttendance' && '직원 근무 알림'}
                        {key === 'dailyReport' && '일일 리포트'}
                        {key === 'weeklyReport' && '주간 리포트'}
                        {key === 'monthlyReport' && '월간 리포트'}
                        {key === 'paymentAlerts' && '결제 알림'}
                        {key === 'systemAlerts' && '시스템 알림'}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {key === 'newOrder' && '새로운 주문이 들어올 때 알림을 받습니다'}
                        {key === 'lowInventory' && '재고가 부족할 때 알림을 받습니다'}
                        {key === 'staffAttendance' && '직원 근무 상태 변경 시 알림을 받습니다'}
                        {key === 'dailyReport' && '일일 매출 리포트를 이메일로 받습니다'}
                        {key === 'weeklyReport' && '주간 매출 리포트를 이메일로 받습니다'}
                        {key === 'monthlyReport' && '월간 매출 리포트를 이메일로 받습니다'}
                        {key === 'paymentAlerts' && '결제 관련 알림을 받습니다'}
                        {key === 'systemAlerts' && '시스템 관련 알림을 받습니다'}
                      </p>
                    </div>
                    <Switch
                      checked={!!value}
                      onCheckedChange={(checked) => setSettings({
                        ...settings,
                        notifications: {
                          ...settings.notifications,
                          [key]: checked
                        }
                      })}
                    />
                  </div>
                ))}
              </div>
              <Button onClick={() => handleSave("notifications")} disabled={isLoading}>
                <Save className="h-4 w-4 mr-2" />
                알림 설정 저장
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 보안 설정 */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                보안 설정
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">비밀번호 정책</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="minLength">최소 길이</Label>
                    <Input
                      id="minLength"
                      type="number"
                      value={settings.security.passwordPolicy.minLength}
                      onChange={(e) => setSettings({
                        ...settings,
                        security: {
                          ...settings.security,
                          passwordPolicy: {
                            ...settings.security.passwordPolicy,
                            minLength: Number(e.target.value)
                          }
                        }
                      })}
                      min="6"
                      max="20"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="expiryDays">만료일수</Label>
                    <Input
                      id="expiryDays"
                      type="number"
                      value={settings.security.passwordPolicy.expiryDays}
                      onChange={(e) => setSettings({
                        ...settings,
                        security: {
                          ...settings.security,
                          passwordPolicy: {
                            ...settings.security.passwordPolicy,
                            expiryDays: Number(e.target.value)
                          }
                        }
                      })}
                      min="30"
                      max="365"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  {Object.entries(settings.security.passwordPolicy).map(([key, value]) => {
                    if (key === 'minLength' || key === 'expiryDays') return null;
                    return (
                      <div key={key} className="flex items-center space-x-2">
                        <Switch
                          checked={!!value}
                          onCheckedChange={(checked) => setSettings({
                            ...settings,
                            security: {
                              ...settings.security,
                              passwordPolicy: {
                                ...settings.security.passwordPolicy,
                                [key]: checked
                              }
                            }
                          })}
                        />
                        <Label>
                          {key === 'requireUppercase' && '대문자 포함'}
                          {key === 'requireLowercase' && '소문자 포함'}
                          {key === 'requireNumbers' && '숫자 포함'}
                          {key === 'requireSpecialChars' && '특수문자 포함'}
                        </Label>
                      </div>
                    );
                  })}
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">세션 관리</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="sessionTimeout">세션 타임아웃 (분)</Label>
                    <Input
                      id="sessionTimeout"
                      type="number"
                      value={settings.security.sessionTimeout}
                      onChange={(e) => setSettings({
                        ...settings,
                        security: {
                          ...settings.security,
                          sessionTimeout: Number(e.target.value)
                        }
                      })}
                      min="5"
                      max="480"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="loginAttempts">로그인 시도 횟수</Label>
                    <Input
                      id="loginAttempts"
                      type="number"
                      value={settings.security.loginAttempts}
                      onChange={(e) => setSettings({
                        ...settings,
                        security: {
                          ...settings.security,
                          loginAttempts: Number(e.target.value)
                        }
                      })}
                      min="3"
                      max="10"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lockoutDuration">계정 잠금 시간 (분)</Label>
                  <Input
                    id="lockoutDuration"
                    type="number"
                    value={settings.security.lockoutDuration}
                    onChange={(e) => setSettings({
                      ...settings,
                      security: {
                        ...settings.security,
                        lockoutDuration: Number(e.target.value)
                      }
                    })}
                    min="5"
                    max="1440"
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">2단계 인증</h3>
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={settings.security.twoFactorAuth}
                    onCheckedChange={(checked) => setSettings({
                      ...settings,
                      security: {
                        ...settings.security,
                        twoFactorAuth: checked
                      }
                    })}
                  />
                  <Label>2단계 인증 활성화</Label>
                </div>
              </div>

              <Button onClick={() => handleSave("security")} disabled={isLoading}>
                <Save className="h-4 w-4 mr-2" />
                보안 설정 저장
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 외관 설정 */}
        <TabsContent value="appearance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                외관 설정
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>테마</Label>
                  <Select
                    value={settings.appearance.theme}
                    onValueChange={(value: "light" | "dark" | "system") => setSettings({
                      ...settings,
                      appearance: { ...settings.appearance, theme: value }
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">라이트 모드</SelectItem>
                      <SelectItem value="dark">다크 모드</SelectItem>
                      <SelectItem value="system">시스템 설정</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>주요 색상</Label>
                  <div className="flex gap-2">
                    {['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'].map((color) => (
                      <button
                        key={color}
                        className={`w-8 h-8 rounded-full border-2 ${
                          settings.appearance.primaryColor === color ? 'border-gray-900' : 'border-gray-300'
                        }`}
                        style={{ backgroundColor: color }}
                        onClick={() => setSettings({
                          ...settings,
                          appearance: { ...settings.appearance, primaryColor: color }
                        })}
                      />
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  {Object.entries(settings.appearance).map(([key, value]) => {
                    if (key === 'theme' || key === 'primaryColor') return null;
                    return (
                      <div key={key} className="flex items-center space-x-2">
                        <Switch
                          checked={!!value}
                          onCheckedChange={(checked) => setSettings({
                            ...settings,
                            appearance: {
                              ...settings.appearance,
                              [key]: checked
                            }
                          })}
                        />
                        <Label>
                          {key === 'sidebarCollapsed' && '사이드바 축소'}
                          {key === 'compactMode' && '컴팩트 모드'}
                          {key === 'showAnimations' && '애니메이션 표시'}
                        </Label>
                      </div>
                    );
                  })}
                </div>
              </div>

              <Button onClick={() => handleSave("appearance")} disabled={isLoading}>
                <Save className="h-4 w-4 mr-2" />
                외관 설정 저장
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 백업/복원 */}
        <TabsContent value="backup" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                백업 및 복원
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">자동 백업 설정</h3>
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={settings.backup.autoBackup}
                    onCheckedChange={(checked) => setSettings({
                      ...settings,
                      backup: { ...settings.backup, autoBackup: checked }
                    })}
                  />
                  <Label>자동 백업 활성화</Label>
                </div>

                {settings.backup.autoBackup && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label>백업 빈도</Label>
                      <Select
                        value={settings.backup.backupFrequency}
                        onValueChange={(value: "daily" | "weekly" | "monthly") => setSettings({
                          ...settings,
                          backup: { ...settings.backup, backupFrequency: value }
                        })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="daily">매일</SelectItem>
                          <SelectItem value="weekly">매주</SelectItem>
                          <SelectItem value="monthly">매월</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>백업 시간</Label>
                      <Input
                        type="time"
                        value={settings.backup.backupTime}
                        onChange={(e) => setSettings({
                          ...settings,
                          backup: { ...settings.backup, backupTime: e.target.value }
                        })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>보관 기간 (일)</Label>
                      <Input
                        type="number"
                        value={settings.backup.retentionDays}
                        onChange={(e) => setSettings({
                          ...settings,
                          backup: { ...settings.backup, retentionDays: Number(e.target.value) }
                        })}
                        min="1"
                        max="365"
                      />
                    </div>
                  </div>
                )}

                <div className="flex items-center space-x-2">
                  <Switch
                    checked={settings.backup.cloudBackup}
                    onCheckedChange={(checked) => setSettings({
                      ...settings,
                      backup: { ...settings.backup, cloudBackup: checked }
                    })}
                  />
                  <Label>클라우드 백업 활성화</Label>
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">수동 백업</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Button variant="outline" onClick={handleBackup} disabled={isLoading}>
                    <Download className="h-4 w-4 mr-2" />
                    백업 생성
                  </Button>
                  <Button variant="outline" disabled={isLoading}>
                    <Upload className="h-4 w-4 mr-2" />
                    백업 복원
                  </Button>
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">최근 백업</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      <div>
                        <p className="font-medium">백업_2024_01_15_02_00.zip</p>
                        <p className="text-sm text-muted-foreground">2024년 1월 15일 02:00</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      <div>
                        <p className="font-medium">백업_2024_01_14_02_00.zip</p>
                        <p className="text-sm text-muted-foreground">2024년 1월 14일 02:00</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>

              <Button onClick={() => handleSave("backup")} disabled={isLoading}>
                <Save className="h-4 w-4 mr-2" />
                백업 설정 저장
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 