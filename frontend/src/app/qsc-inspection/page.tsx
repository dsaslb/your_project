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
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Plus, 
  Edit, 
  Trash2,
  Eye,
  BarChart3,
  Calendar,
  Clock,
  User,
  Building2
} from "lucide-react"

interface QSCInspection {
  id: number
  store_id: number
  inspector_id: number
  inspection_date: string
  category: string
  item: string
  status: 'pass' | 'fail' | 'warning'
  score: number
  notes: string
  created_at: string
  updated_at: string
  inspector_name?: string
  store_name?: string
}

interface AuthState {
  isAuthenticated: boolean
  username: string
  selectedRole: string | null
  user_id: number
}

export default function QSCInspectionPage() {
  const router = useRouter()
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    username: "",
    selectedRole: null,
    user_id: 0
  })
  
  const [inspections, setInspections] = useState<QSCInspection[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingInspection, setEditingInspection] = useState<QSCInspection | null>(null)
  const [formData, setFormData] = useState({
    store_id: "",
    category: "",
    item: "",
    status: "pass",
    score: "",
    notes: ""
  })

  useEffect(() => {
    // 인증 상태 확인
    const storedAuth = localStorage.getItem("authState")
    if (storedAuth) {
      try {
        const parsedAuth = JSON.parse(storedAuth)
        setAuthState(parsedAuth)
        fetchInspections()
      } catch (error) {
        console.error("인증 상태 파싱 오류:", error)
        router.push("/login")
      }
    } else {
      router.push("/login")
    }
  }, [router])

  const fetchInspections = async () => {
    try {
      const token = localStorage.getItem('jwt_token')
      const response = await fetch('/api/qsc/inspections', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setInspections(data.inspections || [])
      } else {
        console.error('QSC 점검 데이터 로드 실패')
      }
    } catch (error) {
      console.error('QSC 점검 데이터 로드 오류:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      const token = localStorage.getItem('jwt_token')
      const url = editingInspection 
        ? `/api/qsc/inspections/${editingInspection.id}`
        : '/api/qsc/inspections'
      
      const method = editingInspection ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          store_id: parseInt(formData.store_id),
          score: parseInt(formData.score)
        })
      })
      
      if (response.ok) {
        setShowForm(false)
        setEditingInspection(null)
        setFormData({
          store_id: "",
          category: "",
          item: "",
          status: "pass",
          score: "",
          notes: ""
        })
        fetchInspections()
      } else {
        console.error('QSC 점검 저장 실패')
      }
    } catch (error) {
      console.error('QSC 점검 저장 오류:', error)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('정말 삭제하시겠습니까?')) return
    
    try {
      const token = localStorage.getItem('jwt_token')
      const response = await fetch(`/api/qsc/inspections/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        fetchInspections()
      } else {
        console.error('QSC 점검 삭제 실패')
      }
    } catch (error) {
      console.error('QSC 점검 삭제 오류:', error)
    }
  }

  const handleEdit = (inspection: QSCInspection) => {
    setEditingInspection(inspection)
    setFormData({
      store_id: inspection.store_id.toString(),
      category: inspection.category,
      item: inspection.item,
      status: inspection.status,
      score: inspection.score.toString(),
      notes: inspection.notes
    })
    setShowForm(true)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass': return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'fail': return <XCircle className="h-4 w-4 text-red-500" />
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      default: return null
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pass': return <Badge className="bg-green-500/20 text-green-300 border-green-500/30">통과</Badge>
      case 'fail': return <Badge className="bg-red-500/20 text-red-300 border-red-500/30">실패</Badge>
      case 'warning': return <Badge className="bg-yellow-500/20 text-yellow-300 border-yellow-500/30">경고</Badge>
      default: return null
    }
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
              <CheckCircle className="h-8 w-8 text-green-400" />
              <div>
                <h1 className="text-xl font-bold text-white">QSC 점검 관리</h1>
                <p className="text-sm text-slate-400">
                  품질(Quality), 서비스(Service), 청결(Cleanliness) 점검 시스템
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-green-500/20 text-green-300 border-green-500/30">
                {authState.selectedRole === 'manager' ? '매니저' : 
                 authState.selectedRole === 'supervisor' ? '슈퍼바이저' : '직원'}
              </Badge>
              <Button 
                onClick={() => setShowForm(true)}
                className="bg-green-600 hover:bg-green-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                새 점검
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
              <CardTitle className="text-sm font-medium text-slate-300">총 점검 수</CardTitle>
              <BarChart3 className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{inspections.length}</div>
              <p className="text-xs text-slate-400">이번 달</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">통과</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {inspections.filter(i => i.status === 'pass').length}
              </div>
              <p className="text-xs text-slate-400">
                {inspections.length > 0 ? 
                  Math.round((inspections.filter(i => i.status === 'pass').length / inspections.length) * 100) : 0}%
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">실패</CardTitle>
              <XCircle className="h-4 w-4 text-red-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {inspections.filter(i => i.status === 'fail').length}
              </div>
              <p className="text-xs text-slate-400">
                {inspections.length > 0 ? 
                  Math.round((inspections.filter(i => i.status === 'fail').length / inspections.length) * 100) : 0}%
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">평균 점수</CardTitle>
              <BarChart3 className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {inspections.length > 0 ? 
                  Math.round(inspections.reduce((sum, i) => sum + i.score, 0) / inspections.length) : 0}
              </div>
              <p className="text-xs text-slate-400">/ 100점</p>
            </CardContent>
          </Card>
        </div>

        {/* 점검 목록 */}
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Calendar className="h-5 w-5 mr-2 text-blue-400" />
              점검 목록
            </CardTitle>
            <CardDescription className="text-slate-400">
              전체 QSC 점검 기록 및 관리
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
                {inspections.map((inspection) => (
                  <div key={inspection.id} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                    <div className="flex items-center space-x-4">
                      {getStatusIcon(inspection.status)}
                      <div>
                        <h4 className="font-medium text-white">{inspection.item}</h4>
                        <p className="text-sm text-slate-400">
                          {inspection.category} • {inspection.store_name || `매장 ${inspection.store_id}`}
                        </p>
                        <p className="text-xs text-slate-500">
                          {new Date(inspection.inspection_date).toLocaleDateString('ko-KR')}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <p className="text-sm text-white">{inspection.score}점</p>
                        {getStatusBadge(inspection.status)}
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(inspection)}
                          className="text-blue-400 hover:bg-blue-500/20"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(inspection.id)}
                          className="text-red-400 hover:bg-red-500/20"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </main>

      {/* 점검 폼 모달 */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">
              {editingInspection ? '점검 수정' : '새 점검 추가'}
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
                <label className="block text-sm font-medium text-slate-300 mb-1">카테고리</label>
                <Select value={formData.category} onValueChange={(value) => setFormData({...formData, category: value})}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                    <SelectValue placeholder="카테고리 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="quality">품질</SelectItem>
                    <SelectItem value="service">서비스</SelectItem>
                    <SelectItem value="cleanliness">청결</SelectItem>
                    <SelectItem value="safety">안전</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">점검 항목</label>
                <Input
                  value={formData.item}
                  onChange={(e) => setFormData({...formData, item: e.target.value})}
                  className="bg-slate-700 border-slate-600 text-white"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">상태</label>
                <Select value={formData.status} onValueChange={(value) => setFormData({...formData, status: value as any})}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pass">통과</SelectItem>
                    <SelectItem value="fail">실패</SelectItem>
                    <SelectItem value="warning">경고</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">점수</label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  value={formData.score}
                  onChange={(e) => setFormData({...formData, score: e.target.value})}
                  className="bg-slate-700 border-slate-600 text-white"
                  required
                />
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
                <Button type="submit" className="bg-green-600 hover:bg-green-700 flex-1">
                  {editingInspection ? '수정' : '추가'}
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setShowForm(false)
                    setEditingInspection(null)
                    setFormData({
                      store_id: "",
                      category: "",
                      item: "",
                      status: "pass",
                      score: "",
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