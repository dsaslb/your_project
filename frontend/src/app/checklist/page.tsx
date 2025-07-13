"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { 
  ClipboardList, 
  CheckCircle, 
  Clock, 
  Plus, 
  Edit, 
  Trash2,
  Eye,
  BarChart3,
  Calendar,
  User,
  Building2,
  AlertCircle
} from "lucide-react"

interface Checklist {
  id: number
  store_id: number
  employee_id: number
  checklist_date: string
  category: string
  title: string
  description: string
  priority: 'low' | 'medium' | 'high'
  status: 'pending' | 'in_progress' | 'completed'
  due_date: string
  completed_at?: string
  created_at: string
  updated_at: string
  employee_name?: string
  store_name?: string
}

interface ChecklistItem {
  id: number
  checklist_id: number
  item_text: string
  is_completed: boolean
  completed_at?: string
}

interface AuthState {
  isAuthenticated: boolean
  username: string
  selectedRole: string | null
  user_id: number
}

export default function ChecklistPage() {
  const router = useRouter()
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    username: "",
    selectedRole: null,
    user_id: 0
  })
  
  const [checklists, setChecklists] = useState<Checklist[]>([])
  const [checklistItems, setChecklistItems] = useState<ChecklistItem[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingChecklist, setEditingChecklist] = useState<Checklist | null>(null)
  const [formData, setFormData] = useState({
    store_id: "",
    category: "",
    title: "",
    description: "",
    priority: "medium",
    due_date: ""
  })

  useEffect(() => {
    // 인증 상태 확인
    const storedAuth = localStorage.getItem("authState")
    if (storedAuth) {
      try {
        const parsedAuth = JSON.parse(storedAuth)
        setAuthState(parsedAuth)
        fetchChecklists()
      } catch (error) {
        console.error("인증 상태 파싱 오류:", error)
        router.push("/login")
      }
    } else {
      router.push("/login")
    }
  }, [router])

  const fetchChecklists = async () => {
    try {
      const token = localStorage.getItem('jwt_token')
      const response = await fetch('/api/checklist/checklists', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setChecklists(data.checklists || [])
      } else {
        console.error('체크리스트 데이터 로드 실패')
      }
    } catch (error) {
      console.error('체크리스트 데이터 로드 오류:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchChecklistItems = async (checklistId: number) => {
    try {
      const token = localStorage.getItem('jwt_token')
      const response = await fetch(`/api/checklist/checklists/${checklistId}/items`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setChecklistItems(data.items || [])
      }
    } catch (error) {
      console.error('체크리스트 항목 로드 오류:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      const token = localStorage.getItem('jwt_token')
      const url = editingChecklist 
        ? `/api/checklist/checklists/${editingChecklist.id}`
        : '/api/checklist/checklists'
      
      const method = editingChecklist ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          store_id: parseInt(formData.store_id)
        })
      })
      
      if (response.ok) {
        setShowForm(false)
        setEditingChecklist(null)
        setFormData({
          store_id: "",
          category: "",
          title: "",
          description: "",
          priority: "medium",
          due_date: ""
        })
        fetchChecklists()
      } else {
        console.error('체크리스트 저장 실패')
      }
    } catch (error) {
      console.error('체크리스트 저장 오류:', error)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('정말 삭제하시겠습니까?')) return
    
    try {
      const token = localStorage.getItem('jwt_token')
      const response = await fetch(`/api/checklist/checklists/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        fetchChecklists()
      } else {
        console.error('체크리스트 삭제 실패')
      }
    } catch (error) {
      console.error('체크리스트 삭제 오류:', error)
    }
  }

  const handleEdit = (checklist: Checklist) => {
    setEditingChecklist(checklist)
    setFormData({
      store_id: checklist.store_id.toString(),
      category: checklist.category,
      title: checklist.title,
      description: checklist.description,
      priority: checklist.priority,
      due_date: checklist.due_date
    })
    setShowForm(true)
  }

  const handleStatusChange = async (checklistId: number, newStatus: string) => {
    try {
      const token = localStorage.getItem('jwt_token')
      const response = await fetch(`/api/checklist/checklists/${checklistId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: newStatus })
      })
      
      if (response.ok) {
        fetchChecklists()
      }
    } catch (error) {
      console.error('상태 변경 오류:', error)
    }
  }

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'high': return <Badge className="bg-red-500/20 text-red-300 border-red-500/30">높음</Badge>
      case 'medium': return <Badge className="bg-yellow-500/20 text-yellow-300 border-yellow-500/30">보통</Badge>
      case 'low': return <Badge className="bg-green-500/20 text-green-300 border-green-500/30">낮음</Badge>
      default: return null
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed': return <Badge className="bg-green-500/20 text-green-300 border-green-500/30">완료</Badge>
      case 'in_progress': return <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/30">진행중</Badge>
      case 'pending': return <Badge className="bg-yellow-500/20 text-yellow-300 border-yellow-500/30">대기</Badge>
      default: return null
    }
  }

  const isOverdue = (dueDate: string) => {
    return new Date(dueDate) < new Date() && status !== 'completed'
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
              <ClipboardList className="h-8 w-8 text-blue-400" />
              <div>
                <h1 className="text-xl font-bold text-white">업무 체크리스트</h1>
                <p className="text-sm text-slate-400">
                  일일 업무 관리 및 진행 상황 추적
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-blue-500/20 text-blue-300 border-blue-500/30">
                {authState.selectedRole === 'manager' ? '매니저' : 
                 authState.selectedRole === 'supervisor' ? '슈퍼바이저' : '직원'}
              </Badge>
              <Button 
                onClick={() => setShowForm(true)}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                새 체크리스트
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
              <CardTitle className="text-sm font-medium text-slate-300">총 체크리스트</CardTitle>
              <ClipboardList className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{checklists.length}</div>
              <p className="text-xs text-slate-400">전체</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">완료</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {checklists.filter(c => c.status === 'completed').length}
              </div>
              <p className="text-xs text-slate-400">
                {checklists.length > 0 ? 
                  Math.round((checklists.filter(c => c.status === 'completed').length / checklists.length) * 100) : 0}%
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">진행중</CardTitle>
              <Clock className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {checklists.filter(c => c.status === 'in_progress').length}
              </div>
              <p className="text-xs text-slate-400">현재 진행</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">지연</CardTitle>
              <AlertCircle className="h-4 w-4 text-red-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {checklists.filter(c => isOverdue(c.due_date)).length}
              </div>
              <p className="text-xs text-slate-400">기한 초과</p>
            </CardContent>
          </Card>
        </div>

        {/* 체크리스트 목록 */}
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Calendar className="h-5 w-5 mr-2 text-blue-400" />
              체크리스트 목록
            </CardTitle>
            <CardDescription className="text-slate-400">
              전체 업무 체크리스트 및 진행 상황
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
                {checklists.map((checklist) => (
                  <div key={checklist.id} className={`p-4 rounded-lg ${isOverdue(checklist.due_date) ? 'bg-red-500/10 border border-red-500/30' : 'bg-white/5'}`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div>
                          <h4 className="font-medium text-white">{checklist.title}</h4>
                          <p className="text-sm text-slate-400">
                            {checklist.category} • {checklist.store_name || `매장 ${checklist.store_id}`}
                          </p>
                          <p className="text-xs text-slate-500">
                            마감일: {new Date(checklist.due_date).toLocaleDateString('ko-KR')}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          {getPriorityBadge(checklist.priority)}
                          {getStatusBadge(checklist.status)}
                          {isOverdue(checklist.due_date) && (
                            <Badge className="bg-red-500/20 text-red-300 border-red-500/30 ml-2">지연</Badge>
                          )}
                        </div>
                        <div className="flex space-x-2">
                          <Select 
                            value={checklist.status} 
                            onValueChange={(value) => handleStatusChange(checklist.id, value)}
                          >
                            <SelectTrigger className="w-32 bg-slate-700 border-slate-600 text-white">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="pending">대기</SelectItem>
                              <SelectItem value="in_progress">진행중</SelectItem>
                              <SelectItem value="completed">완료</SelectItem>
                            </SelectContent>
                          </Select>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEdit(checklist)}
                            className="text-blue-400 hover:bg-blue-500/20"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(checklist.id)}
                            className="text-red-400 hover:bg-red-500/20"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </main>

      {/* 체크리스트 폼 모달 */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">
              {editingChecklist ? '체크리스트 수정' : '새 체크리스트 추가'}
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
                    <SelectItem value="opening">오픈</SelectItem>
                    <SelectItem value="closing">마감</SelectItem>
                    <SelectItem value="cleaning">청소</SelectItem>
                    <SelectItem value="inventory">재고</SelectItem>
                    <SelectItem value="maintenance">정비</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">제목</label>
                <Input
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="bg-slate-700 border-slate-600 text-white"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">설명</label>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="bg-slate-700 border-slate-600 text-white"
                  rows={3}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">우선순위</label>
                <Select value={formData.priority} onValueChange={(value) => setFormData({...formData, priority: value as any})}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">낮음</SelectItem>
                    <SelectItem value="medium">보통</SelectItem>
                    <SelectItem value="high">높음</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">마감일</label>
                <Input
                  type="datetime-local"
                  value={formData.due_date}
                  onChange={(e) => setFormData({...formData, due_date: e.target.value})}
                  className="bg-slate-700 border-slate-600 text-white"
                  required
                />
              </div>
              
              <div className="flex space-x-2 pt-4">
                <Button type="submit" className="bg-blue-600 hover:bg-blue-700 flex-1">
                  {editingChecklist ? '수정' : '추가'}
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setShowForm(false)
                    setEditingChecklist(null)
                    setFormData({
                      store_id: "",
                      category: "",
                      title: "",
                      description: "",
                      priority: "medium",
                      due_date: ""
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