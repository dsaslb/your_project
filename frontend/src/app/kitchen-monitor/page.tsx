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
  Monitor, 
  Thermometer, 
  AlertTriangle, 
  Plus, 
  Edit, 
  Trash2,
  Eye,
  BarChart3,
  Calendar,
  User,
  Building2,
  Activity,
  Zap
} from "lucide-react"

interface KitchenMonitor {
  id: number
  store_id: number
  monitor_type: string
  location: string
  current_value: number
  threshold_min: number
  threshold_max: number
  status: 'normal' | 'warning' | 'critical'
  last_updated: string
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

export default function KitchenMonitorPage() {
  const router = useRouter()
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    username: "",
    selectedRole: null,
    user_id: 0
  })
  
  const [monitors, setMonitors] = useState<KitchenMonitor[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingMonitor, setEditingMonitor] = useState<KitchenMonitor | null>(null)
  const [formData, setFormData] = useState({
    store_id: "",
    monitor_type: "",
    location: "",
    current_value: "",
    threshold_min: "",
    threshold_max: "",
    notes: ""
  })

  useEffect(() => {
    // 인증 상태 확인
    const storedAuth = localStorage.getItem("authState")
    if (storedAuth) {
      try {
        const parsedAuth = JSON.parse(storedAuth)
        setAuthState(parsedAuth)
        fetchMonitors()
      } catch (error) {
        console.error("인증 상태 파싱 오류:", error)
        router.push("/login")
      }
    } else {
      router.push("/login")
    }
  }, [router])

  const fetchMonitors = async () => {
    try {
      const token = localStorage.getItem('jwt_token')
      const response = await fetch('/api/kitchen-monitor/monitors', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setMonitors(data.monitors || [])
      } else {
        console.error('주방 모니터링 데이터 로드 실패')
      }
    } catch (error) {
      console.error('주방 모니터링 데이터 로드 오류:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      const token = localStorage.getItem('jwt_token')
      const url = editingMonitor 
        ? `/api/kitchen-monitor/monitors/${editingMonitor.id}`
        : '/api/kitchen-monitor/monitors'
      
      const method = editingMonitor ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          store_id: parseInt(formData.store_id),
          current_value: parseFloat(formData.current_value),
          threshold_min: parseFloat(formData.threshold_min),
          threshold_max: parseFloat(formData.threshold_max)
        })
      })
      
      if (response.ok) {
        setShowForm(false)
        setEditingMonitor(null)
        setFormData({
          store_id: "",
          monitor_type: "",
          location: "",
          current_value: "",
          threshold_min: "",
          threshold_max: "",
          notes: ""
        })
        fetchMonitors()
      } else {
        console.error('주방 모니터링 저장 실패')
      }
    } catch (error) {
      console.error('주방 모니터링 저장 오류:', error)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('정말 삭제하시겠습니까?')) return
    
    try {
      const token = localStorage.getItem('jwt_token')
      const response = await fetch(`/api/kitchen-monitor/monitors/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        fetchMonitors()
      } else {
        console.error('주방 모니터링 삭제 실패')
      }
    } catch (error) {
      console.error('주방 모니터링 삭제 오류:', error)
    }
  }

  const handleEdit = (monitor: KitchenMonitor) => {
    setEditingMonitor(monitor)
    setFormData({
      store_id: monitor.store_id.toString(),
      monitor_type: monitor.monitor_type,
      location: monitor.location,
      current_value: monitor.current_value.toString(),
      threshold_min: monitor.threshold_min.toString(),
      threshold_max: monitor.threshold_max.toString(),
      notes: monitor.notes
    })
    setShowForm(true)
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'normal': return <Badge className="bg-green-500/20 text-green-300 border-green-500/30">정상</Badge>
      case 'warning': return <Badge className="bg-yellow-500/20 text-yellow-300 border-yellow-500/30">경고</Badge>
      case 'critical': return <Badge className="bg-red-500/20 text-red-300 border-red-500/30">위험</Badge>
      default: return null
    }
  }

  const getMonitorIcon = (type: string) => {
    switch (type) {
      case 'temperature': return <Thermometer className="h-4 w-4 text-red-400" />
      case 'humidity': return <Activity className="h-4 w-4 text-blue-400" />
      case 'pressure': return <Zap className="h-4 w-4 text-yellow-400" />
      default: return <Monitor className="h-4 w-4 text-purple-400" />
    }
  }

  const getMonitorTypeName = (type: string) => {
    switch (type) {
      case 'temperature': return '온도'
      case 'humidity': return '습도'
      case 'pressure': return '압력'
      case 'gas': return '가스'
      default: return type
    }
  }

  const getUnit = (type: string) => {
    switch (type) {
      case 'temperature': return '°C'
      case 'humidity': return '%'
      case 'pressure': return 'Pa'
      case 'gas': return 'ppm'
      default: return ''
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
              <Monitor className="h-8 w-8 text-purple-400" />
              <div>
                <h1 className="text-xl font-bold text-white">주방 모니터링</h1>
                <p className="text-sm text-slate-400">
                  실시간 주방 환경 및 장비 상태 모니터링
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-purple-500/20 text-purple-300 border-purple-500/30">
                {authState.selectedRole === 'manager' ? '매니저' : 
                 authState.selectedRole === 'supervisor' ? '슈퍼바이저' : '직원'}
              </Badge>
              <Button 
                onClick={() => setShowForm(true)}
                className="bg-purple-600 hover:bg-purple-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                새 모니터
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
              <CardTitle className="text-sm font-medium text-slate-300">총 모니터</CardTitle>
              <Monitor className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{monitors.length}</div>
              <p className="text-xs text-slate-400">활성 모니터</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">정상</CardTitle>
              <Activity className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {monitors.filter(m => m.status === 'normal').length}
              </div>
              <p className="text-xs text-slate-400">
                {monitors.length > 0 ? 
                  Math.round((monitors.filter(m => m.status === 'normal').length / monitors.length) * 100) : 0}%
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">경고</CardTitle>
              <AlertTriangle className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {monitors.filter(m => m.status === 'warning').length}
              </div>
              <p className="text-xs text-slate-400">주의 필요</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">위험</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {monitors.filter(m => m.status === 'critical').length}
              </div>
              <p className="text-xs text-slate-400">즉시 조치 필요</p>
            </CardContent>
          </Card>
        </div>

        {/* 모니터링 목록 */}
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Monitor className="h-5 w-5 mr-2 text-purple-400" />
              모니터링 목록
            </CardTitle>
            <CardDescription className="text-slate-400">
              실시간 주방 환경 및 장비 상태
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
                {monitors.map((monitor) => (
                  <div key={monitor.id} className={`flex items-center justify-between p-4 rounded-lg ${
                    monitor.status === 'critical' ? 'bg-red-500/10 border border-red-500/30' :
                    monitor.status === 'warning' ? 'bg-yellow-500/10 border border-yellow-500/30' :
                    'bg-white/5'
                  }`}>
                    <div className="flex items-center space-x-4">
                      {getMonitorIcon(monitor.monitor_type)}
                      <div>
                        <h4 className="font-medium text-white">
                          {getMonitorTypeName(monitor.monitor_type)} - {monitor.location}
                        </h4>
                        <p className="text-sm text-slate-400">
                          {monitor.store_name || `매장 ${monitor.store_id}`}
                        </p>
                        <p className="text-xs text-slate-500">
                          마지막 업데이트: {new Date(monitor.last_updated).toLocaleString('ko-KR')}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="text-lg font-bold text-white">
                          {monitor.current_value}{getUnit(monitor.monitor_type)}
                        </div>
                        <div className="text-xs text-slate-400">
                          {monitor.threshold_min}{getUnit(monitor.monitor_type)} ~ {monitor.threshold_max}{getUnit(monitor.monitor_type)}
                        </div>
                        {getStatusBadge(monitor.status)}
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(monitor)}
                          className="text-blue-400 hover:bg-blue-500/20"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(monitor.id)}
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

      {/* 모니터링 폼 모달 */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">
              {editingMonitor ? '모니터링 수정' : '새 모니터링 추가'}
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
                <label className="block text-sm font-medium text-slate-300 mb-1">모니터링 타입</label>
                <Select value={formData.monitor_type} onValueChange={(value) => setFormData({...formData, monitor_type: value})}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                    <SelectValue placeholder="타입 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="temperature">온도</SelectItem>
                    <SelectItem value="humidity">습도</SelectItem>
                    <SelectItem value="pressure">압력</SelectItem>
                    <SelectItem value="gas">가스</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">위치</label>
                <Input
                  value={formData.location}
                  onChange={(e) => setFormData({...formData, location: e.target.value})}
                  className="bg-slate-700 border-slate-600 text-white"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">현재 값</label>
                <Input
                  type="number"
                  step="0.1"
                  value={formData.current_value}
                  onChange={(e) => setFormData({...formData, current_value: e.target.value})}
                  className="bg-slate-700 border-slate-600 text-white"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">최소 임계값</label>
                <Input
                  type="number"
                  step="0.1"
                  value={formData.threshold_min}
                  onChange={(e) => setFormData({...formData, threshold_min: e.target.value})}
                  className="bg-slate-700 border-slate-600 text-white"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">최대 임계값</label>
                <Input
                  type="number"
                  step="0.1"
                  value={formData.threshold_max}
                  onChange={(e) => setFormData({...formData, threshold_max: e.target.value})}
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
                <Button type="submit" className="bg-purple-600 hover:bg-purple-700 flex-1">
                  {editingMonitor ? '수정' : '추가'}
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setShowForm(false)
                    setEditingMonitor(null)
                    setFormData({
                      store_id: "",
                      monitor_type: "",
                      location: "",
                      current_value: "",
                      threshold_min: "",
                      threshold_max: "",
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