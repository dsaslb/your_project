'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { 
  Plus, Edit, Trash2, Search, Filter, MoreHorizontal,
  Building2, Users, MapPin, Phone, Mail, Globe,
  CheckCircle, AlertCircle, Clock, Star, TrendingUp
} from 'lucide-react'
import { toast } from 'react-hot-toast'

interface Brand {
  id: string
  name: string
  description: string
  logo?: string
  website?: string
  contactEmail: string
  contactPhone: string
  status: 'active' | 'inactive' | 'pending'
  createdAt: string
  updatedAt: string
  stores: number
  revenue: number
  customers: number
  rating: number
  manager: {
    name: string
    email: string
    phone: string
  }
  address: {
    street: string
    city: string
    state: string
    zipCode: string
    country: string
  }
  settings: {
    timezone: string
    currency: string
    language: string
  }
}

export default function BrandManagementPage() {
  const [brands, setBrands] = useState<Brand[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState<Partial<Brand>>({})
  const [isEditing, setIsEditing] = useState(false)

  useEffect(() => {
    loadBrands()
  }, [])

  const loadBrands = async () => {
    try {
      setLoading(true)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
      const response = await fetch(`${apiUrl}/api/brands/management`)
      const data = await response.json()
      
      if (data.success) {
        setBrands(data.brands || [])
      }
    } catch (error) {
      console.error('브랜드 목록 로드 실패:', error)
      // 데모 데이터 사용
      setBrands(generateDemoBrands())
    } finally {
      setLoading(false)
    }
  }

  const generateDemoBrands = (): Brand[] => {
    return [
      {
        id: '1',
        name: '스타벅스',
        description: '세계 최고의 프리미엄 커피 브랜드로, 고품질 커피와 독특한 매장 경험을 제공합니다.',
        logo: '',
        website: 'https://www.starbucks.co.kr',
        contactEmail: 'contact@starbucks.co.kr',
        contactPhone: '1522-3232',
        status: 'active',
        createdAt: '2020-01-15T00:00:00Z',
        updatedAt: '2024-06-01T10:30:00Z',
        stores: 1580,
        revenue: 2850000000,
        customers: 89000,
        rating: 4.5,
        manager: {
          name: '김매니저',
          email: 'manager@starbucks.co.kr',
          phone: '010-1234-5678'
        },
        address: {
          street: '을지로 100',
          city: '서울',
          state: '서울특별시',
          zipCode: '04533',
          country: '대한민국'
        },
        settings: {
          timezone: 'Asia/Seoul',
          currency: 'KRW',
          language: 'ko'
        }
      },
      {
        id: '2',
        name: '카페베네',
        description: '한국의 대표적인 커피 전문점으로, 다양한 메뉴와 편안한 분위기를 제공합니다.',
        logo: '',
        website: 'https://www.caffebene.co.kr',
        contactEmail: 'info@caffebene.co.kr',
        contactPhone: '1588-7070',
        status: 'active',
        createdAt: '2019-05-20T00:00:00Z',
        updatedAt: '2024-05-28T15:45:00Z',
        stores: 980,
        revenue: 1850000000,
        customers: 62000,
        rating: 4.2,
        manager: {
          name: '박총괄',
          email: 'manager@caffebene.co.kr',
          phone: '010-9876-5432'
        },
        address: {
          street: '강남대로 123',
          city: '서울',
          state: '서울특별시',
          zipCode: '06028',
          country: '대한민국'
        },
        settings: {
          timezone: 'Asia/Seoul',
          currency: 'KRW',
          language: 'ko'
        }
      },
      {
        id: '3',
        name: '투썸플레이스',
        description: '프리미엄 디저트 카페로 유명한 브랜드입니다.',
        logo: '',
        website: 'https://www.twosome.co.kr',
        contactEmail: 'contact@twosome.co.kr',
        contactPhone: '1577-6662',
        status: 'pending',
        createdAt: '2024-06-01T00:00:00Z',
        updatedAt: '2024-06-01T00:00:00Z',
        stores: 450,
        revenue: 950000000,
        customers: 35000,
        rating: 4.3,
        manager: {
          name: '이관리자',
          email: 'manager@twosome.co.kr',
          phone: '010-5555-1234'
        },
        address: {
          street: '테헤란로 456',
          city: '서울',
          state: '서울특별시',
          zipCode: '06155',
          country: '대한민국'
        },
        settings: {
          timezone: 'Asia/Seoul',
          currency: 'KRW',
          language: 'ko'
        }
      }
    ]
  }

  const filteredBrands = brands.filter(brand => {
    const matchesSearch = brand.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         brand.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || brand.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const handleCreateBrand = () => {
    setFormData({
      name: '',
      description: '',
      contactEmail: '',
      contactPhone: '',
      website: '',
      status: 'pending',
      manager: { name: '', email: '', phone: '' },
      address: { street: '', city: '', state: '', zipCode: '', country: '대한민국' },
      settings: { timezone: 'Asia/Seoul', currency: 'KRW', language: 'ko' }
    })
    setIsEditing(false)
    setShowModal(true)
  }

  const handleEditBrand = (brand: Brand) => {
    setFormData(brand)
    setIsEditing(true)
    setShowModal(true)
  }

  const handleDeleteBrand = async (brandId: string) => {
    if (!confirm('정말로 이 브랜드를 삭제하시겠습니까?')) return

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
      const response = await fetch(`${apiUrl}/api/brands/${brandId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        setBrands(brands.filter(brand => brand.id !== brandId))
        toast.success('브랜드가 삭제되었습니다!')
      }
    } catch (error) {
      console.error('브랜드 삭제 실패:', error)
      setBrands(brands.filter(brand => brand.id !== brandId))
      toast.success('브랜드가 삭제되었습니다! (데모 모드)')
    }
  }

  const handleSaveBrand = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
      const method = isEditing ? 'PUT' : 'POST'
      const url = isEditing ? `${apiUrl}/api/brands/${formData.id}` : `${apiUrl}/api/brands`

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        const result = await response.json()
        if (isEditing) {
          setBrands(brands.map(brand => brand.id === formData.id ? result.brand : brand))
          toast.success('브랜드가 수정되었습니다!')
        } else {
          setBrands([...brands, { ...formData, id: Date.now().toString(), createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() } as Brand])
          toast.success('브랜드가 생성되었습니다!')
        }
        setShowModal(false)
      }
    } catch (error) {
      console.error('브랜드 저장 실패:', error)
      // 데모 모드에서는 성공으로 처리
      if (isEditing) {
        setBrands(brands.map(brand => brand.id === formData.id ? { ...brand, ...formData } : brand))
        toast.success('브랜드가 수정되었습니다! (데모 모드)')
      } else {
        setBrands([...brands, { ...formData, id: Date.now().toString(), createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() } as Brand])
        toast.success('브랜드가 생성되었습니다! (데모 모드)')
      }
      setShowModal(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'inactive': return <AlertCircle className="w-4 h-4 text-red-500" />
      case 'pending': return <Clock className="w-4 h-4 text-yellow-500" />
      default: return null
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '활성'
      case 'inactive': return '비활성'
      case 'pending': return '대기'
      default: return status
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'inactive': return 'bg-red-100 text-red-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0
    }).format(value)
  }

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('ko-KR').format(value)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="h-96 bg-gray-200 rounded-lg"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">브랜드 관리</h1>
              <p className="text-gray-600">브랜드 생성, 수정, 삭제 및 상태 관리</p>
            </div>
            <Button onClick={handleCreateBrand}>
              <Plus className="w-4 h-4 mr-2" />
              새 브랜드 추가
            </Button>
          </div>
        </div>

        {/* 필터 및 검색 */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    placeholder="브랜드명 또는 설명으로 검색..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <div className="flex gap-3">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">모든 상태</option>
                  <option value="active">활성</option>
                  <option value="inactive">비활성</option>
                  <option value="pending">대기</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 브랜드 목록 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
          {filteredBrands.map(brand => (
            <Card key={brand.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Building2 className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{brand.name}</CardTitle>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(brand.status)}
                        <Badge className={getStatusColor(brand.status)}>
                          {getStatusText(brand.status)}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="sm" onClick={() => handleEditBrand(brand)}>
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => handleDeleteBrand(brand.id)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-sm text-gray-600 line-clamp-3">{brand.description}</p>
                  
                  {/* 통계 */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">매장 수</p>
                      <p className="font-semibold">{formatNumber(brand.stores)}개</p>
                    </div>
                    <div>
                      <p className="text-gray-500">고객 수</p>
                      <p className="font-semibold">{formatNumber(brand.customers)}명</p>
                    </div>
                    <div>
                      <p className="text-gray-500">매출</p>
                      <p className="font-semibold">{formatCurrency(brand.revenue)}</p>
                    </div>
                    <div className="flex items-center gap-1">
                      <Star className="w-3 h-3 text-yellow-500" />
                      <span className="font-semibold">{brand.rating.toFixed(1)}</span>
                    </div>
                  </div>

                  {/* 연락처 정보 */}
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <Mail className="w-3 h-3 text-gray-400" />
                      <span className="text-gray-600">{brand.contactEmail}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Phone className="w-3 h-3 text-gray-400" />
                      <span className="text-gray-600">{brand.contactPhone}</span>
                    </div>
                    {brand.website && (
                      <div className="flex items-center gap-2">
                        <Globe className="w-3 h-3 text-gray-400" />
                        <a href={brand.website} target="_blank" rel="noopener noreferrer" 
                           className="text-blue-600 hover:underline truncate">
                          {brand.website}
                        </a>
                      </div>
                    )}
                  </div>

                  {/* 관리자 정보 */}
                  <div className="border-t pt-3">
                    <div className="flex items-center gap-2 text-sm">
                      <Users className="w-3 h-3 text-gray-400" />
                      <span className="text-gray-600">관리자: {brand.manager.name}</span>
                    </div>
                  </div>

                  {/* 업데이트 일자 */}
                  <div className="text-xs text-gray-500">
                    최종 업데이트: {new Date(brand.updatedAt).toLocaleDateString('ko-KR')}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredBrands.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <Building2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">브랜드가 없습니다</h3>
              <p className="text-gray-500 mb-4">검색 조건에 맞는 브랜드가 없습니다.</p>
              <Button onClick={handleCreateBrand}>
                <Plus className="w-4 h-4 mr-2" />
                첫 번째 브랜드 추가
              </Button>
            </CardContent>
          </Card>
        )}

        {/* 브랜드 생성/수정 모달 */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold">
                    {isEditing ? '브랜드 수정' : '새 브랜드 추가'}
                  </h2>
                  <Button variant="ghost" onClick={() => setShowModal(false)}>
                    ✕
                  </Button>
                </div>

                <div className="space-y-6">
                  {/* 기본 정보 */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">기본 정보</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="name">브랜드명 *</Label>
                        <Input
                          id="name"
                          value={formData.name || ''}
                          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                          placeholder="브랜드명을 입력하세요"
                        />
                      </div>
                      <div>
                        <Label htmlFor="website">웹사이트</Label>
                        <Input
                          id="website"
                          type="url"
                          value={formData.website || ''}
                          onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                          placeholder="https://example.com"
                        />
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="description">설명 *</Label>
                      <Textarea
                        id="description"
                        value={formData.description || ''}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        placeholder="브랜드에 대한 설명을 입력하세요"
                        rows={3}
                      />
                    </div>
                  </div>

                  {/* 연락처 정보 */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">연락처 정보</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="contactEmail">이메일 *</Label>
                        <Input
                          id="contactEmail"
                          type="email"
                          value={formData.contactEmail || ''}
                          onChange={(e) => setFormData({ ...formData, contactEmail: e.target.value })}
                          placeholder="contact@example.com"
                        />
                      </div>
                      <div>
                        <Label htmlFor="contactPhone">전화번호 *</Label>
                        <Input
                          id="contactPhone"
                          type="tel"
                          value={formData.contactPhone || ''}
                          onChange={(e) => setFormData({ ...formData, contactPhone: e.target.value })}
                          placeholder="02-1234-5678"
                        />
                      </div>
                    </div>
                  </div>

                  {/* 관리자 정보 */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">관리자 정보</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <Label htmlFor="managerName">이름</Label>
                        <Input
                          id="managerName"
                          value={formData.manager?.name || ''}
                          onChange={(e) => setFormData({ 
                            ...formData, 
                            manager: { ...formData.manager!, name: e.target.value }
                          })}
                          placeholder="관리자 이름"
                        />
                      </div>
                      <div>
                        <Label htmlFor="managerEmail">이메일</Label>
                        <Input
                          id="managerEmail"
                          type="email"
                          value={formData.manager?.email || ''}
                          onChange={(e) => setFormData({ 
                            ...formData, 
                            manager: { ...formData.manager!, email: e.target.value }
                          })}
                          placeholder="manager@example.com"
                        />
                      </div>
                      <div>
                        <Label htmlFor="managerPhone">전화번호</Label>
                        <Input
                          id="managerPhone"
                          type="tel"
                          value={formData.manager?.phone || ''}
                          onChange={(e) => setFormData({ 
                            ...formData, 
                            manager: { ...formData.manager!, phone: e.target.value }
                          })}
                          placeholder="010-1234-5678"
                        />
                      </div>
                    </div>
                  </div>

                  {/* 상태 */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">상태</h3>
                    <div>
                      <Label htmlFor="status">브랜드 상태</Label>
                      <select
                        id="status"
                        value={formData.status || 'pending'}
                        onChange={(e) => setFormData({ ...formData, status: e.target.value as Brand['status'] })}
                        className="w-full px-3 py-2 mt-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="pending">대기</option>
                        <option value="active">활성</option>
                        <option value="inactive">비활성</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end gap-3 mt-8">
                  <Button variant="outline" onClick={() => setShowModal(false)}>
                    취소
                  </Button>
                  <Button onClick={handleSaveBrand}>
                    {isEditing ? '수정' : '생성'}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}