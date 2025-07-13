"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { 
  Clock, 
  ChefHat, 
  Plus, 
  Edit, 
  Trash2,
  Eye,
  BarChart3,
  Calendar,
  User,
  Building2,
  Timer,
  TrendingUp
} from "lucide-react"

interface CookTime {
  id: number
  store_id: number
  menu_name: string
  category: string
  estimated_time: number
  actual_time: number
  complexity: 'low' | 'medium' | 'high'
  notes: string
  created_at: string
  updated_at: string
  store_name?: string
}

interface AuthState {
  isAuthenticated: boolean
  username: string
  selectedRole: string | null
  user_id: number
}

export default function CookTimePage() {
  const router = useRouter()
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    username: "",
    selectedRole: null,
    user_id: 0
  })
  
  const [cookTimes, setCookTimes] = useState<CookTime[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingCookTime, setEditingCookTime] = useState<CookTime | null>(null)
  const [formData, setFormData] = useState({
    store_id: "",
    menu_name: "",
    category: "",
    estimated_time: "",
    actual_time: "",
    complexity: "medium",
    notes: ""
  })

  useEffect(() => {
    // 인증 상태 확인
    const storedAuth = localStorage.getItem("authState")
    if (storedAuth) {
      try {
        const parsedAuth = JSON.parse(storedAuth)
        setAuthState(parsedAuth)
        fetchCookTimes()
      } catch (error) {
        console.error("인증 상태 파싱 오류:", error)
        router.push("/login")
      }
    } else {
      router.push("/login")
    }
  }, [router])

  const fetchCookTimes = async () => {
    try {
      const token = localStorage.getItem('jwt_token')
      const response = await fetch('/api/cooktime/times', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setCookTimes(data.cook_times || [])
      } else {
        console.error('조리시간 데이터 로드 실패')
      }
    } catch (error) {
      console.error('조리시간 데이터 로드 오류:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      const token = localStorage.getItem('jwt_token')
      const url = editingCookTime 
        ? `/api/cooktime/times/${editingCookTime.id}`
        : '/api/cooktime/times'
      
      const method = editingCookTime ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          store_id: parseInt(formData.store_id),
          estimated_time: parseInt(formData.estimated_time),
          actual_time: parseInt(formData.actual_time)
        })
      })
      
      if (response.ok) {
        setShowForm(false)
        setEditingCookTime(null)
        setFormData({
          store_id: "",
          menu_name: "",
          category: "",
          estimated_time: "",
          actual_time: "",
          complexity: "medium",
          notes: ""
        })
        fetchCookTimes()
      } else {
        console.error('조리시간 저장 실패')
      }
    } catch (error) {
      console.error('조리시간 저장 오류:', error)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('정말 삭제하시겠습니까?')) return
    
    try {
      const token = localStorage.getItem('jwt_token')
      const response = await fetch(`/api/cooktime/times/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        fetchCookTimes()
      } else {
        console.error('조리시간 삭제 실패')
      }
    } catch (error) {
      console.error('조리시간 삭제 오류:', error)
    }
  }

  const handleEdit = (cookTime: CookTime) => {
    setEditingCookTime(cookTime)
    setFormData({
      store_id: cookTime.store_id.toString(),
      menu_name: cookTime.menu_name,
      category: cookTime.category,
      estimated_time: cookTime.estimated_time.toString(),
      actual_time: cookTime.actual_time.toString(),
      complexity: cookTime.complexity,
      notes: cookTime.notes
    })
    setShowForm(true)
  }

  const getComplexityBadge = (complexity: string) => {
    switch (complexity) {
      case 'high': return <Badge className="bg-red-500/20 text-red-300 border-red-500/30">복잡</Badge>
      case 'medium': return <Badge className="bg-yellow-500/20 text-yellow-300 border-yellow-500/30">보통</Badge>
      case 'low': return <Badge className="bg-green-500/20 text-green-300 border-green-500/30">간단</Badge>
      default: return null
    }
  }

  const getTimeAccuracy = (estimated: number, actual: number) => {
    const diff = Math.abs(estimated - actual)
    const percentage = (diff / estimated) * 100
    
    if (percentage <= 10) return { status: 'excellent', text: '정확', color: 'text-green-400' }
    if (percentage <= 20) return { status: 'good', text: '양호', color: 'text-yellow-400' }
    return { status: 'poor', text: '부정확', color: 'text-red-400' }
  }

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return hours > 0 ? `${hours}시간 ${mins}분` : `${mins}분`
  }

  if (!authState.isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white mx-auto"></div>
          <p className="mt-4">인증 확인 중...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* 헤더 */}
      <header className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <ChefHat className="h-8 w-8 text-orange-400" />
              <div>
                <h1 className="text-xl font-bold text-white">조리 예상시간 관리</h1>
                <p className="text-sm text-slate-400">
                  메뉴별 조리시간 예측 및 실제 시간 비교
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-orange-500/20 text-orange-300 border-orange-500/30">
                {authState.selectedRole === 'manager' ? '매니저' : 
                 authState.selectedRole === 'supervisor' ? '슈퍼바이저' : '직원'}
              </Badge>
              <Button 
                onClick={() => setShowForm(true)}
                className="bg-orange-600 hover:bg-orange-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                새 메뉴
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">총 메뉴 수</CardTitle>
              <ChefHat className="h-4 w-4 text-orange-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{cookTimes.length}</div>
              <p className="text-xs text-slate-400">등록된 메뉴</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">평균 예상시간</CardTitle>
              <Clock className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {cookTimes.length > 0 ? 
                  Math.round(cookTimes.reduce((sum, ct) => sum + ct.estimated_time, 0) / cookTimes.length) : 0}분
              </div>
              <p className="text-xs text-slate-400">전체 메뉴</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">평균 실제시간</CardTitle>
              <Timer className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {cookTimes.length > 0 ? 
                  Math.round(cookTimes.reduce((sum, ct) => sum + ct.actual_time, 0) / cookTimes.length) : 0}분
              </div>
              <p className="text-xs text-slate-400">실제 조리</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">정확도</CardTitle>
              <TrendingUp className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {cookTimes.length > 0 ? 
                  Math.round((cookTimes.filter(ct => {
                    const accuracy = getTimeAccuracy(ct.estimated_time, ct.actual_time)
                    return accuracy.status === 'excellent'
                  }).length / cookTimes.length) * 100) : 0}%
              </div>
              <p className="text-xs text-slate-400">±10분 이내</p>
            </CardContent>
          </Card>
        </div>

        {/* 조리시간 목록 */}
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Clock className="h-5 w-5 mr-2 text-orange-400" />
              조리시간 목록
            </CardTitle>
            <CardDescription className="text-slate-400">
              메뉴별 예상 조리시간과 실제 조리시간 비교
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto"></div>
                <p className="text-slate-400 mt-2">데이터 로딩 중...</p>
              </div>
            ) : (
              <div className="space-y-4">
                {cookTimes.map((cookTime) => {
                  const accuracy = getTimeAccuracy(cookTime.estimated_time, cookTime.actual_time)
                  return (
                    <div key={cookTime.id} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div>
                          <h4 className="font-medium text-white">{cookTime.menu_name}</h4>
                          <p className="text-sm text-slate-400">
                            {cookTime.category} • {cookTime.store_name || `매장 ${cookTime.store_id}`}
                          </p>
                          <p className="text-xs text-slate-500">
                            {new Date(cookTime.created_at).toLocaleDateString('ko-KR')}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="text-sm text-slate-300">예상:</span>
                            <span className="text-sm text-blue-400">{formatTime(cookTime.estimated_time)}</span>
                          </div>
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="text-sm text-slate-300">실제:</span>
                            <span className="text-sm text-green-400">{formatTime(cookTime.actual_time)}</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className={`text-xs ${accuracy.color}`}>{accuracy.text}</span>
                            {getComplexityBadge(cookTime.complexity)}
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEdit(cookTime)}
                            className="text-blue-400 hover:bg-blue-500/20"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(cookTime.id)}
                            className="text-red-400 hover:bg-red-500/20"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </main>

      {/* 조리시간 폼 모달 */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">
              {editingCookTime ? '조리시간 수정' : '새 메뉴 추가'}
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">매장 ID</label>
                <Input
                  type="number"
                  value={formData.store_id}
                  onChange={(e) => setFormData({...formData, store_id: e.target.value})}
                  className="bg-slate-700 border-slate-600 text-white"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">메뉴명</label>
                <Input
                  value={formData.menu_name}
                  onChange={(e) => setFormData({...formData, menu_name: e.target.value})}
                  className="bg-slate-700 border-slate-600 text-white"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">카테고리</label>
                <Select value={formData.category} onValueChange={(value) => setFormData({...formData, category: value})}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                    <SelectValue placeholder="카테고리 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="main">메인 요리</SelectItem>
                    <SelectItem value="side">사이드</SelectItem>
                    <SelectItem value="dessert">디저트</SelectItem>
                    <SelectItem value="beverage">음료</SelectItem>
                    <SelectItem value="appetizer">전채</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">예상 조리시간 (분)</label>
                <Input
                  type="number"
                  min="1"
                  value={formData.estimated_time}
                  onChange={(e) => setFormData({...formData, estimated_time: e.target.value})}
                  className="bg-slate-700 border-slate-600 text-white"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">실제 조리시간 (분)</label>
                <Input
                  type="number"
                  min="1"
                  value={formData.actual_time}
                  onChange={(e) => setFormData({...formData, actual_time: e.target.value})}
                  className="bg-slate-700 border-slate-600 text-white"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">복잡도</label>
                <Select value={formData.complexity} onValueChange={(value) => setFormData({...formData, complexity: value as any})}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">간단</SelectItem>
                    <SelectItem value="medium">보통</SelectItem>
                    <SelectItem value="high">복잡</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">비고</label>
                <Textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({...formData, notes: e.target.value})}
                  className="bg-slate-700 border-slate-600 text-white"
                  rows={3}
                />
              </div>
              
              <div className="flex space-x-2 pt-4">
                <Button type="submit" className="bg-orange-600 hover:bg-orange-700 flex-1">
                  {editingCookTime ? '수정' : '추가'}
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setShowForm(false)
                    setEditingCookTime(null)
                    setFormData({
                      store_id: "",
                      menu_name: "",
                      category: "",
                      estimated_time: "",
                      actual_time: "",
                      complexity: "medium",
                      notes: ""
                    })
                  }}
                  className="flex-1"
                >
                  취소
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
} 