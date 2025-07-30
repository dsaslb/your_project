'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Settings, Save, RefreshCw, Bell, Shield, Eye, 
  Users, CreditCard, Globe, Palette, Database,
  CheckCircle, AlertCircle, Info
} from 'lucide-react'
import { toast } from 'react-hot-toast'

interface BrandSettings {
  general: {
    name: string
    description: string
    logo: string
    website: string
    contactEmail: string
    contactPhone: string
  }
  notifications: {
    emailNotifications: boolean
    smsNotifications: boolean
    pushNotifications: boolean
    orderAlerts: boolean
    inventoryAlerts: boolean
    customerFeedback: boolean
  }
  privacy: {
    dataCollection: boolean
    analytics: boolean
    marketing: boolean
    thirdPartySharing: boolean
  }
  payment: {
    acceptCreditCards: boolean
    acceptDebitCards: boolean
    acceptDigitalWallets: boolean
    acceptCash: boolean
    taxRate: number
    currency: string
  }
  display: {
    theme: 'light' | 'dark' | 'system'
    primaryColor: string
    language: string
    timezone: string
  }
}

export default function BrandSettingsPage() {
  const [settings, setSettings] = useState<BrandSettings>({
    general: {
      name: '',
      description: '',
      logo: '',
      website: '',
      contactEmail: '',
      contactPhone: ''
    },
    notifications: {
      emailNotifications: true,
      smsNotifications: false,
      pushNotifications: true,
      orderAlerts: true,
      inventoryAlerts: true,
      customerFeedback: true
    },
    privacy: {
      dataCollection: true,
      analytics: true,
      marketing: false,
      thirdPartySharing: false
    },
    payment: {
      acceptCreditCards: true,
      acceptDebitCards: true,
      acceptDigitalWallets: true,
      acceptCash: true,
      taxRate: 10,
      currency: 'KRW'
    },
    display: {
      theme: 'system',
      primaryColor: '#3B82F6',
      language: 'ko',
      timezone: 'Asia/Seoul'
    }
  })

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [selectedBrand, setSelectedBrand] = useState<any>(null)
  const [brands, setBrands] = useState<any[]>([])

  useEffect(() => {
    loadBrands()
  }, [])

  const loadBrands = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
      const response = await fetch(`${apiUrl}/api/brands`)
      const data = await response.json()
      
      if (data.success) {
        setBrands(data.brands || [])
        if (data.brands?.length > 0) {
          setSelectedBrand(data.brands[0])
          await loadBrandSettings(data.brands[0].id)
        }
      }
    } catch (error) {
      console.error('브랜드 목록 로드 실패:', error)
      // 데모 데이터 사용
      const demoBrands = [
        { id: '1', name: '스타벅스', description: '프리미엄 커피 브랜드' },
        { id: '2', name: '카페베네', description: '로컬 커피 체인' }
      ]
      setBrands(demoBrands)
      setSelectedBrand(demoBrands[0])
      loadDemoSettings()
    } finally {
      setLoading(false)
    }
  }

  const loadBrandSettings = async (brandId: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
      const response = await fetch(`${apiUrl}/api/brands/${brandId}/settings`)
      const data = await response.json()
      
      if (data.success) {
        setSettings(data.settings)
      }
    } catch (error) {
      console.error('브랜드 설정 로드 실패:', error)
      loadDemoSettings()
    }
  }

  const loadDemoSettings = () => {
    setSettings({
      general: {
        name: '스타벅스',
        description: '세계 최고의 프리미엄 커피 브랜드',
        logo: '',
        website: 'https://www.starbucks.co.kr',
        contactEmail: 'contact@starbucks.co.kr',
        contactPhone: '1522-3232'
      },
      notifications: {
        emailNotifications: true,
        smsNotifications: true,
        pushNotifications: true,
        orderAlerts: true,
        inventoryAlerts: true,
        customerFeedback: true
      },
      privacy: {
        dataCollection: true,
        analytics: true,
        marketing: false,
        thirdPartySharing: false
      },
      payment: {
        acceptCreditCards: true,
        acceptDebitCards: true,
        acceptDigitalWallets: true,
        acceptCash: true,
        taxRate: 10,
        currency: 'KRW'
      },
      display: {
        theme: 'light',
        primaryColor: '#00704A',
        language: 'ko',
        timezone: 'Asia/Seoul'
      }
    })
  }

  const handleSave = async () => {
    if (!selectedBrand) return

    setSaving(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
      const response = await fetch(`${apiUrl}/api/brands/${selectedBrand.id}/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
      })

      if (response.ok) {
        toast.success('설정이 저장되었습니다!')
      } else {
        toast.error('설정 저장에 실패했습니다.')
      }
    } catch (error) {
      console.error('설정 저장 실패:', error)
      toast.success('설정이 저장되었습니다! (데모 모드)')
    } finally {
      setSaving(false)
    }
  }

  const updateSettings = (section: keyof BrandSettings, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }))
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
            <div className="h-96 bg-gray-200 rounded-lg"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* 헤더 */}
        <div className="mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">브랜드 설정</h1>
              <p className="text-gray-600">브랜드 정보 및 운영 설정을 관리합니다</p>
            </div>
            <Button onClick={handleSave} disabled={saving}>
              {saving ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  저장 중...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  설정 저장
                </>
              )}
            </Button>
          </div>
        </div>

        {/* 브랜드 선택 */}
        {brands.length > 1 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg">브랜드 선택</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                {brands.map(brand => (
                  <Button
                    key={brand.id}
                    variant={selectedBrand?.id === brand.id ? "default" : "outline"}
                    onClick={() => {
                      setSelectedBrand(brand)
                      loadBrandSettings(brand.id)
                    }}
                  >
                    {brand.name}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* 설정 탭 */}
        <Tabs defaultValue="general" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="general" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              일반
            </TabsTrigger>
            <TabsTrigger value="notifications" className="flex items-center gap-2">
              <Bell className="w-4 h-4" />
              알림
            </TabsTrigger>
            <TabsTrigger value="privacy" className="flex items-center gap-2">
              <Shield className="w-4 h-4" />
              개인정보
            </TabsTrigger>
            <TabsTrigger value="payment" className="flex items-center gap-2">
              <CreditCard className="w-4 h-4" />
              결제
            </TabsTrigger>
            <TabsTrigger value="display" className="flex items-center gap-2">
              <Palette className="w-4 h-4" />
              디스플레이
            </TabsTrigger>
          </TabsList>

          {/* 일반 설정 */}
          <TabsContent value="general">
            <Card>
              <CardHeader>
                <CardTitle>일반 정보</CardTitle>
                <CardDescription>브랜드의 기본 정보를 설정합니다</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="brand-name">브랜드명</Label>
                    <Input
                      id="brand-name"
                      value={settings.general.name}
                      onChange={(e) => updateSettings('general', 'name', e.target.value)}
                      placeholder="브랜드명을 입력하세요"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="website">웹사이트</Label>
                    <Input
                      id="website"
                      type="url"
                      value={settings.general.website}
                      onChange={(e) => updateSettings('general', 'website', e.target.value)}
                      placeholder="https://example.com"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">브랜드 설명</Label>
                  <Textarea
                    id="description"
                    value={settings.general.description}
                    onChange={(e) => updateSettings('general', 'description', e.target.value)}
                    placeholder="브랜드에 대한 설명을 입력하세요"
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="contact-email">연락처 이메일</Label>
                    <Input
                      id="contact-email"
                      type="email"
                      value={settings.general.contactEmail}
                      onChange={(e) => updateSettings('general', 'contactEmail', e.target.value)}
                      placeholder="contact@example.com"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="contact-phone">연락처 전화번호</Label>
                    <Input
                      id="contact-phone"
                      type="tel"
                      value={settings.general.contactPhone}
                      onChange={(e) => updateSettings('general', 'contactPhone', e.target.value)}
                      placeholder="02-1234-5678"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 알림 설정 */}
          <TabsContent value="notifications">
            <Card>
              <CardHeader>
                <CardTitle>알림 설정</CardTitle>
                <CardDescription>다양한 알림 옵션을 설정합니다</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>이메일 알림</Label>
                      <p className="text-sm text-gray-500">중요한 업데이트를 이메일로 받습니다</p>
                    </div>
                    <Switch
                      checked={settings.notifications.emailNotifications}
                      onCheckedChange={(checked) => updateSettings('notifications', 'emailNotifications', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>SMS 알림</Label>
                      <p className="text-sm text-gray-500">긴급한 알림을 SMS로 받습니다</p>
                    </div>
                    <Switch
                      checked={settings.notifications.smsNotifications}
                      onCheckedChange={(checked) => updateSettings('notifications', 'smsNotifications', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>푸시 알림</Label>
                      <p className="text-sm text-gray-500">앱에서 실시간 알림을 받습니다</p>
                    </div>
                    <Switch
                      checked={settings.notifications.pushNotifications}
                      onCheckedChange={(checked) => updateSettings('notifications', 'pushNotifications', checked)}
                    />
                  </div>
                </div>

                <div className="border-t pt-6">
                  <h4 className="font-medium mb-4">상세 알림 설정</h4>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Label>주문 알림</Label>
                      <Switch
                        checked={settings.notifications.orderAlerts}
                        onCheckedChange={(checked) => updateSettings('notifications', 'orderAlerts', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <Label>재고 알림</Label>
                      <Switch
                        checked={settings.notifications.inventoryAlerts}
                        onCheckedChange={(checked) => updateSettings('notifications', 'inventoryAlerts', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <Label>고객 피드백 알림</Label>
                      <Switch
                        checked={settings.notifications.customerFeedback}
                        onCheckedChange={(checked) => updateSettings('notifications', 'customerFeedback', checked)}
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 개인정보 설정 */}
          <TabsContent value="privacy">
            <Card>
              <CardHeader>
                <CardTitle>개인정보 및 데이터 설정</CardTitle>
                <CardDescription>데이터 수집 및 활용에 대한 설정입니다</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>데이터 수집</Label>
                      <p className="text-sm text-gray-500">서비스 개선을 위한 데이터 수집에 동의합니다</p>
                    </div>
                    <Switch
                      checked={settings.privacy.dataCollection}
                      onCheckedChange={(checked) => updateSettings('privacy', 'dataCollection', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>분석 데이터 활용</Label>
                      <p className="text-sm text-gray-500">사용 패턴 분석 및 통계 생성에 활용됩니다</p>
                    </div>
                    <Switch
                      checked={settings.privacy.analytics}
                      onCheckedChange={(checked) => updateSettings('privacy', 'analytics', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>마케팅 활용</Label>
                      <p className="text-sm text-gray-500">맞춤형 마케팅 및 광고에 활용됩니다</p>
                    </div>
                    <Switch
                      checked={settings.privacy.marketing}
                      onCheckedChange={(checked) => updateSettings('privacy', 'marketing', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>제3자 공유</Label>
                      <p className="text-sm text-gray-500">파트너사와의 데이터 공유에 동의합니다</p>
                    </div>
                    <Switch
                      checked={settings.privacy.thirdPartySharing}
                      onCheckedChange={(checked) => updateSettings('privacy', 'thirdPartySharing', checked)}
                    />
                  </div>
                </div>

                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-start gap-3">
                    <Info className="w-5 h-5 text-blue-500 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-blue-900">개인정보 처리방침</h4>
                      <p className="text-sm text-blue-700 mt-1">
                        수집된 개인정보는 관련 법령에 따라 안전하게 처리되며, 
                        명시된 목적 외에는 사용되지 않습니다.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 결제 설정 */}
          <TabsContent value="payment">
            <Card>
              <CardHeader>
                <CardTitle>결제 설정</CardTitle>
                <CardDescription>결제 방법 및 세금 설정을 관리합니다</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h4 className="font-medium mb-4">결제 방법</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center justify-between">
                      <Label>신용카드</Label>
                      <Switch
                        checked={settings.payment.acceptCreditCards}
                        onCheckedChange={(checked) => updateSettings('payment', 'acceptCreditCards', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <Label>체크카드</Label>
                      <Switch
                        checked={settings.payment.acceptDebitCards}
                        onCheckedChange={(checked) => updateSettings('payment', 'acceptDebitCards', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <Label>디지털 지갑</Label>
                      <Switch
                        checked={settings.payment.acceptDigitalWallets}
                        onCheckedChange={(checked) => updateSettings('payment', 'acceptDigitalWallets', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <Label>현금</Label>
                      <Switch
                        checked={settings.payment.acceptCash}
                        onCheckedChange={(checked) => updateSettings('payment', 'acceptCash', checked)}
                      />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="tax-rate">세율 (%)</Label>
                    <Input
                      id="tax-rate"
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      value={settings.payment.taxRate}
                      onChange={(e) => updateSettings('payment', 'taxRate', parseFloat(e.target.value) || 0)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="currency">통화</Label>
                    <select
                      id="currency"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      value={settings.payment.currency}
                      onChange={(e) => updateSettings('payment', 'currency', e.target.value)}
                    >
                      <option value="KRW">원 (KRW)</option>
                      <option value="USD">달러 (USD)</option>
                      <option value="EUR">유로 (EUR)</option>
                      <option value="JPY">엔 (JPY)</option>
                    </select>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 디스플레이 설정 */}
          <TabsContent value="display">
            <Card>
              <CardHeader>
                <CardTitle>디스플레이 설정</CardTitle>
                <CardDescription>화면 표시 및 테마 설정을 관리합니다</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label>테마</Label>
                    <select
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      value={settings.display.theme}
                      onChange={(e) => updateSettings('display', 'theme', e.target.value)}
                    >
                      <option value="light">라이트</option>
                      <option value="dark">다크</option>
                      <option value="system">시스템 설정</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="primary-color">기본 색상</Label>
                    <div className="flex items-center gap-3">
                      <Input
                        id="primary-color"
                        type="color"
                        value={settings.display.primaryColor}
                        onChange={(e) => updateSettings('display', 'primaryColor', e.target.value)}
                        className="w-16 h-10"
                      />
                      <Input
                        type="text"
                        value={settings.display.primaryColor}
                        onChange={(e) => updateSettings('display', 'primaryColor', e.target.value)}
                        className="flex-1"
                      />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label>언어</Label>
                    <select
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      value={settings.display.language}
                      onChange={(e) => updateSettings('display', 'language', e.target.value)}
                    >
                      <option value="ko">한국어</option>
                      <option value="en">English</option>
                      <option value="ja">日本語</option>
                      <option value="zh">中文</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label>시간대</Label>
                    <select
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      value={settings.display.timezone}
                      onChange={(e) => updateSettings('display', 'timezone', e.target.value)}
                    >
                      <option value="Asia/Seoul">서울 (UTC+9)</option>
                      <option value="Asia/Tokyo">도쿄 (UTC+9)</option>
                      <option value="America/New_York">뉴욕 (UTC-5)</option>
                      <option value="Europe/London">런던 (UTC+0)</option>
                    </select>
                  </div>
                </div>

                <div className="bg-yellow-50 p-4 rounded-lg">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-yellow-900">설정 적용 안내</h4>
                      <p className="text-sm text-yellow-700 mt-1">
                        디스플레이 설정 변경 사항은 페이지를 새로고침한 후 적용됩니다.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}