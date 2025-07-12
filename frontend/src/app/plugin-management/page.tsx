'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { 
  Package, 
  Settings, 
  Play, 
  Pause, 
  RotateCcw, 
  Plus, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Menu,
  Route,
  Code,
  History,
  UploadCloud,
  CornerUpLeft,
  Star,
  Download,
  Search,
  Filter,
  SortAsc,
  SortDesc,
  MessageSquare,
  ThumbsUp,
  Eye,
  Workflow,
  TestTube,
  Activity,
  FileText,
  Square
} from 'lucide-react'

interface Plugin {
  name: string
  version: string
  description: string
  author: string
  category: string
  enabled: boolean
  loaded: boolean
  menus: MenuItem[]
  routes: RouteItem[]
}

interface MenuItem {
  title: string
  path: string
  icon?: string
  parent?: string
  roles?: string[]
  order?: number
  badge?: string
}

interface RouteItem {
  path: string
  methods: string[]
  handler: string
  auth_required?: boolean
  roles?: string[]
  description?: string
}

export default function PluginManagementPage() {
  const [plugins, setPlugins] = useState<Record<string, Plugin>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('installed')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [createForm, setCreateForm] = useState({
    name: '',
    display_name: '',
    version: '1.0.0',
    description: '',
    author: '',
    category: 'general'
  })
  const [releaseHistory, setReleaseHistory] = useState<any[]>([])
  const [showHistoryModal, setShowHistoryModal] = useState(false)
  const [historyPlugin, setHistoryPlugin] = useState<string | null>(null)
  const [showReleaseModal, setShowReleaseModal] = useState(false)
  const [releaseVersion, setReleaseVersion] = useState('')
  const [releasePlugin, setReleasePlugin] = useState<string | null>(null)
  const [showRollbackModal, setShowRollbackModal] = useState(false)
  const [rollbackVersion, setRollbackVersion] = useState('')
  const [rollbackPlugin, setRollbackPlugin] = useState<string | null>(null)
  const [releases, setReleases] = useState<any[]>([])
  const [marketplacePlugins, setMarketplacePlugins] = useState<any[]>([])
  const [marketplaceCategories, setMarketplaceCategories] = useState<any[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [sortBy, setSortBy] = useState<string>('rating')
  const [sortOrder, setSortOrder] = useState<string>('desc')
  const [showPluginDetails, setShowPluginDetails] = useState(false)
  const [selectedPlugin, setSelectedPlugin] = useState<any>(null)
  const [pluginReviews, setPluginReviews] = useState<any[]>([])
  const [showReviewModal, setShowReviewModal] = useState(false)
  const [reviewForm, setReviewForm] = useState({
    rating: 5,
    comment: ''
  })

  // 피드백 관련 상태
  const [feedbacks, setFeedbacks] = useState<any[]>([])
  const [feedbackTemplates, setFeedbackTemplates] = useState<any>({})
  const [showFeedbackModal, setShowFeedbackModal] = useState(false)
  const [showFeedbackDetails, setShowFeedbackDetails] = useState(false)
  const [selectedFeedback, setSelectedFeedback] = useState<any>(null)
  const [feedbackForm, setFeedbackForm] = useState<any>({})
  const [feedbackStatus, setFeedbackStatus] = useState<string>('')
  const [feedbackType, setFeedbackType] = useState<string>('')
  const [feedbackSortBy, setFeedbackSortBy] = useState<string>('created_at')
  const [feedbackSortOrder, setFeedbackSortOrder] = useState<string>('desc')

  // 테스트/모니터링 관련 상태
  const [testResults, setTestResults] = useState<any[]>([])
  const [performanceMetrics, setPerformanceMetrics] = useState<any[]>([])
  const [monitoringActive, setMonitoringActive] = useState(false)
  const [selectedPluginForTest, setSelectedPluginForTest] = useState<string>('')
  const [testType, setTestType] = useState<string>('all')
  const [showTestResults, setShowTestResults] = useState(false)
  const [selectedTestResult, setSelectedTestResult] = useState<any>(null)
  const [documentation, setDocumentation] = useState<any>(null)
  const [showDocumentation, setShowDocumentation] = useState(false)

  // 플러그인 목록 로드
  const loadPlugins = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/plugins/list')
      const data = await response.json()
      
      if (data.status === 'success') {
        setPlugins(data.data)
      } else {
        setError('플러그인 목록을 불러오는데 실패했습니다')
      }
    } catch (err) {
      setError('플러그인 목록을 불러오는데 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  // 플러그인 활성화/비활성화
  const togglePlugin = async (pluginName: string, enabled: boolean) => {
    try {
      const endpoint = enabled ? 'enable' : 'disable'
      const response = await fetch(`/api/plugins/${pluginName}/${endpoint}`, {
        method: 'POST'
      })
      
      if (response.ok) {
        await loadPlugins() // 목록 새로고침
      } else {
        setError(`플러그인 ${enabled ? '활성화' : '비활성화'}에 실패했습니다`)
      }
    } catch (err) {
      setError(`플러그인 ${enabled ? '활성화' : '비활성화'}에 실패했습니다`)
    }
  }

  // 플러그인 재로드
  const reloadPlugin = async (pluginName: string) => {
    try {
      const response = await fetch(`/api/plugins/${pluginName}/reload`, {
        method: 'POST'
      })
      
      if (response.ok) {
        await loadPlugins() // 목록 새로고침
      } else {
        setError('플러그인 재로드에 실패했습니다')
      }
    } catch (err) {
      setError('플러그인 재로드에 실패했습니다')
    }
  }

  // 새 플러그인 생성
  const createPlugin = async () => {
    try {
      const response = await fetch('/api/plugins/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(createForm)
      })
      
      const data = await response.json()
      
      if (data.status === 'success') {
        setShowCreateForm(false)
        setCreateForm({
          name: '',
          display_name: '',
          version: '1.0.0',
          description: '',
          author: '',
          category: 'general'
        })
        await loadPlugins() // 목록 새로고침
      } else {
        setError(data.error || '플러그인 생성에 실패했습니다')
      }
    } catch (err) {
      setError('플러그인 생성에 실패했습니다')
    }
  }

  // 플러그인 배포본(버전) 목록 조회
  const loadReleases = async (pluginName: string) => {
    try {
      const response = await fetch(`/api/plugins/${pluginName}/releases`)
      const data = await response.json()
      if (data.status === 'success') {
        setReleases(data.data)
      } else {
        setReleases([])
      }
    } catch {
      setReleases([])
    }
  }

  // 배포(스냅샷) 실행
  const handleRelease = async () => {
    if (!releasePlugin || !releaseVersion) return
    const res = await fetch(`/api/plugins/${releasePlugin}/release`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ version: releaseVersion, user: 'admin' })
    })
    setShowReleaseModal(false)
    setReleaseVersion('')
    setReleasePlugin(null)
    await loadPlugins()
    await loadReleases(releasePlugin)
  }

  // 롤백 실행
  const handleRollback = async () => {
    if (!rollbackPlugin || !rollbackVersion) return
    const res = await fetch(`/api/plugins/${rollbackPlugin}/rollback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ version: rollbackVersion, user: 'admin' })
    })
    setShowRollbackModal(false)
    setRollbackVersion('')
    setRollbackPlugin(null)
    await loadPlugins()
    await loadReleases(rollbackPlugin)
  }

  // 배포/업데이트/롤백 이력 조회
  const openHistoryModal = async (pluginName: string) => {
    setHistoryPlugin(pluginName)
    setShowHistoryModal(true)
    const res = await fetch(`/api/plugins/${pluginName}/release-history`)
    const data = await res.json()
    if (data.status === 'success') {
      setReleaseHistory(data.data.reverse())
    } else {
      setReleaseHistory([])
    }
  }

  // 마켓플레이스 플러그인 목록 로드
  const loadMarketplacePlugins = async () => {
    try {
      const params = new URLSearchParams()
      if (selectedCategory) params.append('category', selectedCategory)
      if (searchQuery) params.append('search', searchQuery)
      params.append('sort_by', sortBy)
      params.append('sort_order', sortOrder)
      
      const response = await fetch(`/api/marketplace/plugins?${params}`)
      const data = await response.json()
      
      if (data.status === 'success') {
        setMarketplacePlugins(data.data)
      } else {
        setMarketplacePlugins([])
      }
    } catch (err) {
      setMarketplacePlugins([])
    }
  }

  // 마켓플레이스 카테고리 로드
  const loadMarketplaceCategories = async () => {
    try {
      const response = await fetch('/api/marketplace/categories')
      const data = await response.json()
      
      if (data.status === 'success') {
        setMarketplaceCategories(data.data)
      } else {
        setMarketplaceCategories([])
      }
    } catch (err) {
      setMarketplaceCategories([])
    }
  }

  // 플러그인 설치
  const installPlugin = async (pluginId: string) => {
    try {
      const response = await fetch(`/api/marketplace/plugins/${pluginId}/install`, {
        method: 'POST'
      })
      
      if (response.ok) {
        await loadPlugins() // 설치된 플러그인 목록 새로고침
        await loadMarketplacePlugins() // 마켓플레이스 목록 새로고침
      } else {
        setError('플러그인 설치에 실패했습니다')
      }
    } catch (err) {
      setError('플러그인 설치에 실패했습니다')
    }
  }

  // 플러그인 상세 정보 및 리뷰 로드
  const openPluginDetails = async (pluginId: string) => {
    try {
      // 플러그인 상세 정보
      const pluginResponse = await fetch(`/api/marketplace/plugins/${pluginId}`)
      const pluginData = await pluginResponse.json()
      
      if (pluginData.status === 'success') {
        setSelectedPlugin(pluginData.data)
        
        // 리뷰 목록
        const reviewsResponse = await fetch(`/api/marketplace/plugins/${pluginId}/reviews`)
        const reviewsData = await reviewsResponse.json()
        
        if (reviewsData.status === 'success') {
          setPluginReviews(reviewsData.data)
        } else {
          setPluginReviews([])
        }
        
        setShowPluginDetails(true)
      }
    } catch (err) {
      setError('플러그인 상세 정보를 불러오는데 실패했습니다')
    }
  }

  // 리뷰 추가
  const addReview = async () => {
    if (!selectedPlugin) return
    
    try {
      const response = await fetch(`/api/marketplace/plugins/${selectedPlugin.id}/reviews`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'admin',
          user_name: 'Admin',
          rating: reviewForm.rating,
          comment: reviewForm.comment
        })
      })
      
      if (response.ok) {
        setShowReviewModal(false)
        setReviewForm({ rating: 5, comment: '' })
        await openPluginDetails(selectedPlugin.id) // 리뷰 목록 새로고침
        await loadMarketplacePlugins() // 평점 업데이트 반영
      } else {
        setError('리뷰 추가에 실패했습니다')
      }
    } catch (err) {
      setError('리뷰 추가에 실패했습니다')
    }
  }

  // 피드백 목록 로드
  const loadFeedbacks = async () => {
    try {
      const params = new URLSearchParams()
      if (feedbackStatus) params.append('status', feedbackStatus)
      if (feedbackType) params.append('type', feedbackType)
      params.append('sort_by', feedbackSortBy)
      params.append('sort_order', feedbackSortOrder)
      
      const response = await fetch(`/api/feedback?${params}`)
      const data = await response.json()
      
      if (data.status === 'success') {
        setFeedbacks(data.data)
      } else {
        setFeedbacks([])
      }
    } catch (err) {
      setFeedbacks([])
    }
  }

  // 피드백 템플릿 로드
  const loadFeedbackTemplates = async () => {
    try {
      const response = await fetch('/api/feedback/templates')
      const data = await response.json()
      
      if (data.status === 'success') {
        setFeedbackTemplates(data.data)
      } else {
        setFeedbackTemplates({})
      }
    } catch (err) {
      setFeedbackTemplates({})
    }
  }

  // 피드백 생성
  const createFeedback = async () => {
    try {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...feedbackForm,
          user_id: 'admin',
          user_name: 'Admin'
        })
      })
      
      if (response.ok) {
        setShowFeedbackModal(false)
        setFeedbackForm({})
        await loadFeedbacks()
      } else {
        setError('피드백 생성에 실패했습니다')
      }
    } catch (err) {
      setError('피드백 생성에 실패했습니다')
    }
  }

  // 피드백 상태 업데이트
  const updateFeedbackStatus = async (feedbackId: string, status: string, comment: string = '') => {
    try {
      const response = await fetch(`/api/feedback/${feedbackId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status,
          user_id: 'admin',
          comment
        })
      })
      
      if (response.ok) {
        await loadFeedbacks()
        if (selectedFeedback?.id === feedbackId) {
          await openFeedbackDetails(feedbackId)
        }
      } else {
        setError('피드백 상태 업데이트에 실패했습니다')
      }
    } catch (err) {
      setError('피드백 상태 업데이트에 실패했습니다')
    }
  }

  // 피드백 할당
  const assignFeedback = async (feedbackId: string, assignedTo: string, estimatedCompletion: string = '') => {
    try {
      const response = await fetch(`/api/feedback/${feedbackId}/assign`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          assigned_to: assignedTo,
          estimated_completion: estimatedCompletion
        })
      })
      
      if (response.ok) {
        await loadFeedbacks()
        if (selectedFeedback?.id === feedbackId) {
          await openFeedbackDetails(feedbackId)
        }
      } else {
        setError('피드백 할당에 실패했습니다')
      }
    } catch (err) {
      setError('피드백 할당에 실패했습니다')
    }
  }

  // 피드백 상세 정보 열기
  const openFeedbackDetails = async (feedbackId: string) => {
    try {
      const response = await fetch(`/api/feedback/${feedbackId}`)
      const data = await response.json()
      
      if (data.status === 'success') {
        setSelectedFeedback(data.data)
        setShowFeedbackDetails(true)
      }
    } catch (err) {
      setError('피드백 상세 정보를 불러오는데 실패했습니다')
    }
  }

  // 피드백 댓글 추가
  const addFeedbackComment = async (feedbackId: string, content: string, isInternal: boolean = false) => {
    try {
      const response = await fetch(`/api/feedback/${feedbackId}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'admin',
          user_name: 'Admin',
          user_role: 'admin',
          content,
          is_internal: isInternal
        })
      })
      
      if (response.ok) {
        await openFeedbackDetails(feedbackId)
      } else {
        setError('댓글 추가에 실패했습니다')
      }
    } catch (err) {
      setError('댓글 추가에 실패했습니다')
    }
  }

  // 피드백 투표
  const voteFeedback = async (feedbackId: string, vote: boolean) => {
    try {
      const response = await fetch(`/api/feedback/${feedbackId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'admin',
          vote
        })
      })
      
      if (response.ok) {
        await loadFeedbacks()
      }
    } catch (err) {
      // 투표 실패는 조용히 처리
    }
  }

  // 피드백 팔로우
  const followFeedback = async (feedbackId: string, follow: boolean) => {
    try {
      const response = await fetch(`/api/feedback/${feedbackId}/follow`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'admin',
          follow
        })
      })
      
      if (response.ok) {
        await loadFeedbacks()
      }
    } catch (err) {
      // 팔로우 실패는 조용히 처리
    }
  }

  // 테스트 실행
  const runPluginTests = async (pluginId: string, testType: string = 'all') => {
    try {
      const response = await fetch(`/api/plugins/${pluginId}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ test_type: testType })
      })
      
      if (response.ok) {
        const data = await response.json()
        await loadTestResults()
        setError('테스트가 실행되었습니다')
      } else {
        setError('테스트 실행에 실패했습니다')
      }
    } catch (err) {
      setError('테스트 실행에 실패했습니다')
    }
  }

  // 테스트 결과 로드
  const loadTestResults = async () => {
    try {
      const response = await fetch('/api/plugins/test-results?limit=100')
      const data = await response.json()
      
      if (data.status === 'success') {
        setTestResults(data.data)
      } else {
        setTestResults([])
      }
    } catch (err) {
      setTestResults([])
    }
  }

  // 성능 모니터링 시작
  const startMonitoring = async (pluginId?: string) => {
    try {
      const response = await fetch('/api/plugins/monitoring/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plugin_id: pluginId })
      })
      
      if (response.ok) {
        setMonitoringActive(true)
        await loadPerformanceMetrics()
      } else {
        setError('모니터링 시작에 실패했습니다')
      }
    } catch (err) {
      setError('모니터링 시작에 실패했습니다')
    }
  }

  // 성능 모니터링 중지
  const stopMonitoring = async () => {
    try {
      const response = await fetch('/api/plugins/monitoring/stop', {
        method: 'POST'
      })
      
      if (response.ok) {
        setMonitoringActive(false)
      } else {
        setError('모니터링 중지에 실패했습니다')
      }
    } catch (err) {
      setError('모니터링 중지에 실패했습니다')
    }
  }

  // 성능 메트릭 로드
  const loadPerformanceMetrics = async () => {
    try {
      const response = await fetch('/api/plugins/performance?hours=24')
      const data = await response.json()
      
      if (data.status === 'success') {
        setPerformanceMetrics(data.data)
      } else {
        setPerformanceMetrics([])
      }
    } catch (err) {
      setPerformanceMetrics([])
    }
  }

  // 문서 생성
  const generateDocumentation = async (pluginId: string) => {
    try {
      const response = await fetch(`/api/plugins/${pluginId}/documentation`, {
        method: 'POST'
      })
      
      if (response.ok) {
        const data = await response.json()
        setDocumentation(data.data)
        setShowDocumentation(true)
      } else {
        setError('문서 생성에 실패했습니다')
      }
    } catch (err) {
      setError('문서 생성에 실패했습니다')
    }
  }

  // 문서 조회
  const loadDocumentation = async (pluginId: string) => {
    try {
      const response = await fetch(`/api/plugins/${pluginId}/documentation`)
      const data = await response.json()
      
      if (data.status === 'success') {
        setDocumentation(data.data)
        setShowDocumentation(true)
      } else {
        setError('문서를 찾을 수 없습니다')
      }
    } catch (err) {
      setError('문서 조회에 실패했습니다')
    }
  }

  useEffect(() => {
    loadPlugins()
    loadMarketplaceCategories()
    loadFeedbackTemplates()
    loadTestResults()
    loadPerformanceMetrics()
  }, [])

  useEffect(() => {
    if (activeTab === 'marketplace') {
      loadMarketplacePlugins()
    } else if (activeTab === 'feedback') {
      loadFeedbacks()
    } else if (activeTab === 'testing') {
      loadTestResults()
      loadPerformanceMetrics()
    }
  }, [activeTab, selectedCategory, searchQuery, sortBy, sortOrder, feedbackStatus, feedbackType, feedbackSortBy, feedbackSortOrder])

  const getCategoryColor = (category: string) => {
    const colors = {
      restaurant: 'bg-orange-100 text-orange-800',
      retail: 'bg-blue-100 text-blue-800',
      service: 'bg-green-100 text-green-800',
      manufacturing: 'bg-purple-100 text-purple-800',
      general: 'bg-gray-100 text-gray-800'
    }
    return colors[category as keyof typeof colors] || colors.general
  }

  const getStatusIcon = (enabled: boolean, loaded: boolean) => {
    if (!enabled) return <Pause className="h-4 w-4 text-gray-400" />
    if (loaded) return <CheckCircle className="h-4 w-4 text-green-500" />
    return <AlertCircle className="h-4 w-4 text-yellow-500" />
  }

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ))
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'in_review': 'bg-blue-100 text-blue-800',
      'approved': 'bg-green-100 text-green-800',
      'rejected': 'bg-red-100 text-red-800',
      'in_development': 'bg-purple-100 text-purple-800',
      'completed': 'bg-gray-100 text-gray-800',
      'cancelled': 'bg-gray-100 text-gray-600'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      'pending': '대기중',
      'in_review': '검토중',
      'approved': '승인됨',
      'rejected': '거부됨',
      'in_development': '개발중',
      'completed': '완료됨',
      'cancelled': '취소됨'
    }
    return texts[status] || status
  }

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      'low': 'bg-green-100 text-green-800',
      'medium': 'bg-yellow-100 text-yellow-800',
      'high': 'bg-orange-100 text-orange-800',
      'critical': 'bg-red-100 text-red-800'
    }
    return colors[priority] || 'bg-gray-100 text-gray-800'
  }

  const getTestStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'passed': 'bg-green-100 text-green-800',
      'failed': 'bg-red-100 text-red-800',
      'error': 'bg-orange-100 text-orange-800',
      'skipped': 'bg-gray-100 text-gray-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getTestStatusText = (status: string) => {
    const texts: Record<string, string> = {
      'passed': '통과',
      'failed': '실패',
      'error': '오류',
      'skipped': '건너뜀'
    }
    return texts[status] || status
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">플러그인 관리</h1>
          <p className="text-gray-600">시스템 플러그인을 관리하고 설정합니다</p>
        </div>
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          새 플러그인
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="installed">설치된 플러그인</TabsTrigger>
          <TabsTrigger value="marketplace">마켓플레이스</TabsTrigger>
          <TabsTrigger value="feedback">피드백 관리</TabsTrigger>
          <TabsTrigger value="testing">테스트/모니터링</TabsTrigger>
          <TabsTrigger value="settings">설정</TabsTrigger>
        </TabsList>

        <TabsContent value="installed" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Object.entries(plugins).map(([name, plugin]) => (
              <Card key={name} className="relative">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(plugin.enabled, plugin.loaded)}
                      <div>
                        <CardTitle className="text-lg">{plugin.name}</CardTitle>
                        <CardDescription>v{plugin.version}</CardDescription>
                      </div>
                    </div>
                    <Badge className={getCategoryColor(plugin.category)}>
                      {plugin.category}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-gray-600">{plugin.description}</p>
                  <p className="text-xs text-gray-500">저자: {plugin.author}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Switch
                        checked={plugin.enabled}
                        onCheckedChange={(enabled) => togglePlugin(name, enabled)}
                      />
                      <Label className="text-sm">
                        {plugin.enabled ? '활성화' : '비활성화'}
                      </Label>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => reloadPlugin(name)}
                    >
                      <RotateCcw className="h-4 w-4" />
                    </Button>
                  </div>

                  <Separator />

                  <div className="space-y-2">
                    <div className="flex items-center space-x-2 text-sm">
                      <Menu className="h-4 w-4" />
                      <span>메뉴: {plugin.menus.length}개</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm">
                      <Route className="h-4 w-4" />
                      <span>API: {plugin.routes.length}개</span>
                    </div>
                  </div>
                  <Separator />
                  <div className="flex items-center space-x-2 mt-2">
                    <Button size="sm" variant="secondary" onClick={() => { setShowReleaseModal(true); setReleasePlugin(name); }}>
                      <UploadCloud className="h-4 w-4 mr-1" /> 배포(스냅샷)
                    </Button>
                    <Button size="sm" variant="secondary" onClick={async () => { await loadReleases(name); setShowRollbackModal(true); setRollbackPlugin(name); }}>
                      <CornerUpLeft className="h-4 w-4 mr-1" /> 롤백
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => openHistoryModal(name)}>
                      <History className="h-4 w-4 mr-1" /> 이력
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="marketplace" className="space-y-4">
          {/* 검색 및 필터 */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      placeholder="플러그인 검색..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="카테고리 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">모든 카테고리</SelectItem>
                    {marketplaceCategories.map(cat => (
                      <SelectItem key={cat.id} value={cat.id}>{cat.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger className="w-full md:w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="rating">평점</SelectItem>
                    <SelectItem value="downloads">다운로드</SelectItem>
                    <SelectItem value="created_at">최신</SelectItem>
                    <SelectItem value="price">가격</SelectItem>
                  </SelectContent>
                </Select>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')}
                >
                  {sortOrder === 'desc' ? <SortDesc className="h-4 w-4" /> : <SortAsc className="h-4 w-4" />}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* 플러그인 목록 */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {marketplacePlugins.map((plugin) => (
              <Card key={plugin.id} className="relative">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{plugin.name}</CardTitle>
                      <CardDescription>v{plugin.version}</CardDescription>
                    </div>
                    <Badge className={getCategoryColor(plugin.category)}>
                      {plugin.category}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-gray-600">{plugin.description}</p>
                  <p className="text-xs text-gray-500">저자: {plugin.author}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {renderStars(plugin.rating)}
                      <span className="text-sm text-gray-600">({plugin.rating})</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <Download className="h-4 w-4" />
                      <span>{plugin.downloads}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-medium">
                      {plugin.price === 0 ? '무료' : `${plugin.price} ${plugin.currency}`}
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => openPluginDetails(plugin.id)}
                      >
                        상세보기
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => installPlugin(plugin.id)}
                      >
                        설치
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          
          {marketplacePlugins.length === 0 && (
            <Card>
              <CardContent className="p-8 text-center">
                <p className="text-gray-500">플러그인이 없습니다.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="feedback" className="space-y-4">
          {/* 피드백 필터 및 검색 */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col md:flex-row gap-4">
                <Select value={feedbackStatus} onValueChange={setFeedbackStatus}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="상태 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">모든 상태</SelectItem>
                    <SelectItem value="pending">대기중</SelectItem>
                    <SelectItem value="in_review">검토중</SelectItem>
                    <SelectItem value="approved">승인됨</SelectItem>
                    <SelectItem value="rejected">거부됨</SelectItem>
                    <SelectItem value="in_development">개발중</SelectItem>
                    <SelectItem value="completed">완료됨</SelectItem>
                    <SelectItem value="cancelled">취소됨</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={feedbackType} onValueChange={setFeedbackType}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="유형 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">모든 유형</SelectItem>
                    <SelectItem value="plugin_request">플러그인 요청</SelectItem>
                    <SelectItem value="feature_request">기능 요청</SelectItem>
                    <SelectItem value="bug_report">버그 신고</SelectItem>
                    <SelectItem value="improvement">개선 제안</SelectItem>
                    <SelectItem value="feedback">일반 피드백</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={feedbackSortBy} onValueChange={setFeedbackSortBy}>
                  <SelectTrigger className="w-full md:w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="created_at">생성일</SelectItem>
                    <SelectItem value="updated_at">수정일</SelectItem>
                    <SelectItem value="votes">투표</SelectItem>
                    <SelectItem value="priority">우선순위</SelectItem>
                  </SelectContent>
                </Select>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setFeedbackSortOrder(feedbackSortOrder === 'desc' ? 'asc' : 'desc')}
                >
                  {feedbackSortOrder === 'desc' ? <SortDesc className="h-4 w-4" /> : <SortAsc className="h-4 w-4" />}
                </Button>
                <Button onClick={() => setShowFeedbackModal(true)} className="ml-auto">
                  <Plus className="h-4 w-4 mr-2" />
                  피드백 작성
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* 피드백 목록 */}
          <div className="space-y-4">
            {feedbacks.map((feedback) => (
              <Card key={feedback.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <CardTitle className="text-lg">{feedback.title}</CardTitle>
                        <Badge className={getStatusColor(feedback.status)}>
                          {getStatusText(feedback.status)}
                        </Badge>
                        <Badge className={getPriorityColor(feedback.priority)}>
                          {feedback.priority}
                        </Badge>
                      </div>
                      <CardDescription>
                        {feedback.type} • {feedback.user_name} • {new Date(feedback.created_at).toLocaleDateString()}
                      </CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => voteFeedback(feedback.id, true)}
                      >
                        <ThumbsUp className="h-4 w-4 mr-1" />
                        {feedback.votes}
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => openFeedbackDetails(feedback.id)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-4">{feedback.description}</p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>댓글 {feedback.comments?.length || 0}</span>
                      <span>팔로워 {feedback.followers?.length || 0}</span>
                    </div>
                    <div className="flex space-x-2">
                      {feedback.assigned_to && (
                        <Badge variant="secondary">담당: {feedback.assigned_to}</Badge>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => openFeedbackDetails(feedback.id)}
                      >
                        상세보기
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            
            {feedbacks.length === 0 && (
              <Card>
                <CardContent className="p-8 text-center">
                  <p className="text-gray-500">피드백이 없습니다.</p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="testing" className="space-y-6">
          {/* 테스트 실행 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TestTube className="h-5 w-5" />
                플러그인 테스트
              </CardTitle>
              <CardDescription>플러그인 테스트를 실행하고 결과를 확인하세요</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col md:flex-row gap-4">
                <Select value={selectedPluginForTest} onValueChange={setSelectedPluginForTest}>
                  <SelectTrigger className="w-full md:w-64">
                    <SelectValue placeholder="플러그인 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(plugins).map(([id, plugin]) => (
                      <SelectItem key={id} value={id}>{plugin.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select value={testType} onValueChange={setTestType}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">모든 테스트</SelectItem>
                    <SelectItem value="unit">단위 테스트</SelectItem>
                    <SelectItem value="integration">통합 테스트</SelectItem>
                    <SelectItem value="performance">성능 테스트</SelectItem>
                    <SelectItem value="security">보안 테스트</SelectItem>
                  </SelectContent>
                </Select>
                <Button 
                  onClick={() => runPluginTests(selectedPluginForTest, testType)}
                  disabled={!selectedPluginForTest}
                >
                  <Play className="h-4 w-4 mr-2" />
                  테스트 실행
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* 성능 모니터링 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                성능 모니터링
              </CardTitle>
              <CardDescription>플러그인 성능을 실시간으로 모니터링하세요</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-600">
                    모니터링 상태: {monitoringActive ? '실행 중' : '중지됨'}
                  </span>
                  {monitoringActive && (
                    <Badge className="bg-green-100 text-green-800">활성</Badge>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={() => startMonitoring()}
                    disabled={monitoringActive}
                    size="sm"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    시작
                  </Button>
                  <Button
                    onClick={stopMonitoring}
                    disabled={!monitoringActive}
                    variant="outline"
                    size="sm"
                  >
                    <Square className="h-4 w-4 mr-2" />
                    중지
                  </Button>
                </div>
              </div>
              
              {/* 성능 메트릭 차트 */}
              {performanceMetrics.length > 0 && (
                <div className="space-y-4">
                  <h4 className="font-medium">최근 성능 메트릭</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {performanceMetrics.slice(-3).map((metric, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="text-sm font-medium">{metric.plugin_id}</div>
                        <div className="text-xs text-gray-500 mt-1">
                          CPU: {metric.cpu_usage.toFixed(1)}% | 
                          메모리: {metric.memory_usage.toFixed(1)}% | 
                          응답시간: {metric.response_time.toFixed(0)}ms
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* 테스트 결과 */}
          <Card>
            <CardHeader>
              <CardTitle>테스트 결과</CardTitle>
              <CardDescription>최근 실행된 테스트 결과를 확인하세요</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {testResults.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">테스트 결과가 없습니다.</p>
                ) : (
                  testResults.map((result) => (
                    <div key={result.started_at} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{result.plugin_id}</span>
                          <Badge className={getTestStatusColor(result.status || 'unknown')}>
                            {getTestStatusText(result.status || 'unknown')}
                          </Badge>
                        </div>
                        <span className="text-sm text-gray-500">
                          {new Date(result.started_at).toLocaleString()}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">
                        테스트 유형: {result.test_type} | 
                        총 테스트: {result.total_tests} | 
                        통과: {result.passed_tests} | 
                        실패: {result.failed_tests}
                      </div>
                      <div className="mt-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setSelectedTestResult(result)
                            setShowTestResults(true)
                          }}
                        >
                          상세보기
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* 문서화 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                문서화
              </CardTitle>
              <CardDescription>플러그인 문서를 생성하고 관리하세요</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex flex-col md:flex-row gap-4">
                  <Select value={selectedPluginForTest} onValueChange={setSelectedPluginForTest}>
                    <SelectTrigger className="w-full md:w-64">
                      <SelectValue placeholder="플러그인 선택" />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(plugins).map(([id, plugin]) => (
                        <SelectItem key={id} value={id}>{plugin.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <div className="flex gap-2">
                    <Button
                      onClick={() => generateDocumentation(selectedPluginForTest)}
                      disabled={!selectedPluginForTest}
                    >
                      <FileText className="h-4 w-4 mr-2" />
                      문서 생성
                    </Button>
                    <Button
                      onClick={() => loadDocumentation(selectedPluginForTest)}
                      disabled={!selectedPluginForTest}
                      variant="outline"
                    >
                      <Eye className="h-4 w-4 mr-2" />
                      문서 보기
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>플러그인 설정</CardTitle>
              <CardDescription>
                전역 플러그인 설정을 관리합니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>자동 플러그인 로드</Label>
                  <p className="text-sm text-gray-600">
                    서버 시작 시 플러그인을 자동으로 로드합니다
                  </p>
                </div>
                <Switch defaultChecked />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <Label>플러그인 검증</Label>
                  <p className="text-sm text-gray-600">
                    플러그인 로드 시 스키마 검증을 수행합니다
                  </p>
                </div>
                <Switch defaultChecked />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 새 플러그인 생성 모달 */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>새 플러그인 생성</CardTitle>
              <CardDescription>
                새로운 플러그인을 생성합니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="name">플러그인 이름</Label>
                <Input
                  id="name"
                  value={createForm.name}
                  onChange={(e) => setCreateForm({...createForm, name: e.target.value})}
                  placeholder="my_plugin"
                />
              </div>
              
              <div>
                <Label htmlFor="display_name">표시 이름</Label>
                <Input
                  id="display_name"
                  value={createForm.display_name}
                  onChange={(e) => setCreateForm({...createForm, display_name: e.target.value})}
                  placeholder="내 플러그인"
                />
              </div>
              
              <div>
                <Label htmlFor="version">버전</Label>
                <Input
                  id="version"
                  value={createForm.version}
                  onChange={(e) => setCreateForm({...createForm, version: e.target.value})}
                  placeholder="1.0.0"
                />
              </div>
              
              <div>
                <Label htmlFor="description">설명</Label>
                <Textarea
                  id="description"
                  value={createForm.description}
                  onChange={(e) => setCreateForm({...createForm, description: e.target.value})}
                  placeholder="플러그인 설명을 입력하세요"
                />
              </div>
              
              <div>
                <Label htmlFor="author">저자</Label>
                <Input
                  id="author"
                  value={createForm.author}
                  onChange={(e) => setCreateForm({...createForm, author: e.target.value})}
                  placeholder="Your Name"
                />
              </div>
              
              <div>
                <Label htmlFor="category">카테고리</Label>
                <Select
                  value={createForm.category}
                  onValueChange={(value) => setCreateForm({...createForm, category: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="general">일반</SelectItem>
                    <SelectItem value="restaurant">레스토랑</SelectItem>
                    <SelectItem value="retail">소매</SelectItem>
                    <SelectItem value="service">서비스</SelectItem>
                    <SelectItem value="manufacturing">제조</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex space-x-2">
                <Button onClick={createPlugin} className="flex-1">
                  생성
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setShowCreateForm(false)}
                  className="flex-1"
                >
                  취소
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      {/* 배포(스냅샷) 모달 */}
      {showReleaseModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-sm">
            <CardHeader>
              <CardTitle>플러그인 배포(스냅샷)</CardTitle>
              <CardDescription>새 버전으로 현재 상태를 저장합니다.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Label>버전</Label>
              <Input value={releaseVersion} onChange={e => setReleaseVersion(e.target.value)} placeholder="예: 1.0.1" />
              <div className="flex space-x-2">
                <Button onClick={handleRelease} className="flex-1">배포</Button>
                <Button variant="outline" onClick={() => { setShowReleaseModal(false); setReleaseVersion(''); setReleasePlugin(null); }} className="flex-1">취소</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      {/* 롤백 모달 */}
      {showRollbackModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-sm">
            <CardHeader>
              <CardTitle>플러그인 롤백</CardTitle>
              <CardDescription>이전 배포본으로 복구합니다.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Label>롤백할 버전</Label>
              <select className="w-full border rounded p-2" value={rollbackVersion} onChange={e => setRollbackVersion(e.target.value)}>
                <option value="">버전 선택</option>
                {releases.map(r => <option key={r.version} value={r.version}>{r.version}</option>)}
              </select>
              <div className="flex space-x-2">
                <Button onClick={handleRollback} className="flex-1">롤백</Button>
                <Button variant="outline" onClick={() => { setShowRollbackModal(false); setRollbackVersion(''); setRollbackPlugin(null); }} className="flex-1">취소</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      {/* 이력 모달 */}
      {showHistoryModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-lg">
            <CardHeader>
              <CardTitle>배포/업데이트/롤백 이력</CardTitle>
              <CardDescription>{historyPlugin}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 max-h-96 overflow-y-auto">
              {releaseHistory.length === 0 && <div className="text-gray-500">이력이 없습니다.</div>}
              {releaseHistory.map((h, i) => (
                <div key={i} className="border-b py-2 text-sm">
                  <div><b>{h.action}</b> <span className="text-xs text-gray-400">({h.version})</span></div>
                  <div className="text-xs text-gray-500">{h.timestamp}</div>
                  <div className="text-xs">{h.user} {h.detail}</div>
                </div>
              ))}
            </CardContent>
            <div className="p-4 flex justify-end">
              <Button variant="outline" onClick={() => setShowHistoryModal(false)}>닫기</Button>
            </div>
          </Card>
        </div>
      )}

      {/* 플러그인 상세 정보 모달 */}
      {showPluginDetails && selectedPlugin && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-2xl">{selectedPlugin.name}</CardTitle>
                  <CardDescription>v{selectedPlugin.version} • {selectedPlugin.author}</CardDescription>
                </div>
                <Button variant="outline" onClick={() => setShowPluginDetails(false)}>
                  닫기
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-2">설명</h3>
                <p className="text-gray-600">{selectedPlugin.description}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="text-lg font-semibold mb-2">정보</h3>
                  <div className="space-y-2 text-sm">
                    <div>카테고리: {selectedPlugin.category}</div>
                    <div>가격: {selectedPlugin.price === 0 ? '무료' : `${selectedPlugin.price} ${selectedPlugin.currency}`}</div>
                    <div>평점: {selectedPlugin.rating}/5</div>
                    <div>다운로드: {selectedPlugin.downloads}</div>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-2">태그</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedPlugin.tags.map((tag: string, index: number) => (
                      <Badge key={index} variant="secondary">{tag}</Badge>
                    ))}
                  </div>
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold">리뷰</h3>
                  <Button size="sm" onClick={() => setShowReviewModal(true)}>
                    리뷰 작성
                  </Button>
                </div>
                <div className="space-y-4 max-h-64 overflow-y-auto">
                  {pluginReviews.length === 0 ? (
                    <p className="text-gray-500">리뷰가 없습니다.</p>
                  ) : (
                    pluginReviews.map((review) => (
                      <div key={review.id} className="border-b pb-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <span className="font-medium">{review.user_name}</span>
                            <div className="flex">{renderStars(review.rating)}</div>
                          </div>
                          <span className="text-xs text-gray-500">{review.created_at}</span>
                        </div>
                        <p className="text-sm text-gray-600">{review.comment}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>
              
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowPluginDetails(false)}>
                  취소
                </Button>
                <Button onClick={() => installPlugin(selectedPlugin.id)}>
                  설치
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 리뷰 작성 모달 */}
      {showReviewModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>리뷰 작성</CardTitle>
              <CardDescription>{selectedPlugin?.name}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>평점</Label>
                <div className="flex space-x-1 mt-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      onClick={() => setReviewForm({...reviewForm, rating: star})}
                    >
                      <Star
                        className={`h-6 w-6 ${star <= reviewForm.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
                      />
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <Label>리뷰</Label>
                <Textarea
                  value={reviewForm.comment}
                  onChange={(e) => setReviewForm({...reviewForm, comment: e.target.value})}
                  placeholder="플러그인에 대한 리뷰를 작성해주세요"
                  rows={4}
                />
              </div>
              <div className="flex space-x-2">
                <Button onClick={addReview} className="flex-1">작성</Button>
                <Button variant="outline" onClick={() => setShowReviewModal(false)} className="flex-1">취소</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 피드백 작성 모달 */}
      {showFeedbackModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle>피드백 작성</CardTitle>
              <CardDescription>새로운 피드백을 작성해주세요</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>피드백 유형</Label>
                <Select value={feedbackForm.type || ''} onValueChange={(value) => setFeedbackForm({...feedbackForm, type: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="피드백 유형 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="plugin_request">플러그인 요청</SelectItem>
                    <SelectItem value="feature_request">기능 요청</SelectItem>
                    <SelectItem value="bug_report">버그 신고</SelectItem>
                    <SelectItem value="improvement">개선 제안</SelectItem>
                    <SelectItem value="feedback">일반 피드백</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>제목</Label>
                <Input
                  value={feedbackForm.title || ''}
                  onChange={(e) => setFeedbackForm({...feedbackForm, title: e.target.value})}
                  placeholder="피드백 제목을 입력하세요"
                />
              </div>
              <div>
                <Label>설명</Label>
                <Textarea
                  value={feedbackForm.description || ''}
                  onChange={(e) => setFeedbackForm({...feedbackForm, description: e.target.value})}
                  placeholder="피드백에 대한 상세한 설명을 입력하세요"
                  rows={4}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>우선순위</Label>
                  <Select value={feedbackForm.priority || 'medium'} onValueChange={(value) => setFeedbackForm({...feedbackForm, priority: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">낮음</SelectItem>
                      <SelectItem value="medium">보통</SelectItem>
                      <SelectItem value="high">높음</SelectItem>
                      <SelectItem value="critical">긴급</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>카테고리</Label>
                  <Select value={feedbackForm.category || 'general'} onValueChange={(value) => setFeedbackForm({...feedbackForm, category: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="general">일반</SelectItem>
                      <SelectItem value="restaurant">레스토랑</SelectItem>
                      <SelectItem value="retail">소매</SelectItem>
                      <SelectItem value="service">서비스</SelectItem>
                      <SelectItem value="manufacturing">제조</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="flex space-x-2">
                <Button onClick={createFeedback} className="flex-1">작성</Button>
                <Button variant="outline" onClick={() => setShowFeedbackModal(false)} className="flex-1">취소</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 피드백 상세 정보 모달 */}
      {showFeedbackDetails && selectedFeedback && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-2xl">{selectedFeedback.title}</CardTitle>
                  <CardDescription>
                    {selectedFeedback.type} • {selectedFeedback.user_name} • {new Date(selectedFeedback.created_at).toLocaleDateString()}
                  </CardDescription>
                </div>
                <Button variant="outline" onClick={() => setShowFeedbackDetails(false)}>
                  닫기
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-2">설명</h3>
                <p className="text-gray-600">{selectedFeedback.description}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="text-lg font-semibold mb-2">정보</h3>
                  <div className="space-y-2 text-sm">
                    <div>상태: <Badge className={getStatusColor(selectedFeedback.status)}>{getStatusText(selectedFeedback.status)}</Badge></div>
                    <div>우선순위: <Badge className={getPriorityColor(selectedFeedback.priority)}>{selectedFeedback.priority}</Badge></div>
                    <div>카테고리: {selectedFeedback.category}</div>
                    <div>투표: {selectedFeedback.votes}</div>
                    <div>팔로워: {selectedFeedback.followers?.length || 0}</div>
                    {selectedFeedback.assigned_to && <div>담당자: {selectedFeedback.assigned_to}</div>}
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-2">태그</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedFeedback.tags?.map((tag: string, index: number) => (
                      <Badge key={index} variant="secondary">{tag}</Badge>
                    ))}
                  </div>
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold">댓글</h3>
                </div>
                <div className="space-y-4 max-h-64 overflow-y-auto">
                  {selectedFeedback.comments?.length === 0 ? (
                    <p className="text-gray-500">댓글이 없습니다.</p>
                  ) : (
                    selectedFeedback.comments?.map((comment: any) => (
                      <div key={comment.id} className="border-b pb-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <span className="font-medium">{comment.user_name}</span>
                            <Badge variant="outline">{comment.user_role}</Badge>
                            {comment.is_internal && <Badge variant="destructive">내부</Badge>}
                          </div>
                          <span className="text-xs text-gray-500">{comment.created_at}</span>
                        </div>
                        <p className="text-sm text-gray-600">{comment.content}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>
              
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowFeedbackDetails(false)}>
                  취소
                </Button>
                <Button onClick={() => updateFeedbackStatus(selectedFeedback.id, 'approved')}>
                  승인
                </Button>
                <Button variant="destructive" onClick={() => updateFeedbackStatus(selectedFeedback.id, 'rejected')}>
                  거부
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 테스트 결과 상세 모달 */}
      {showTestResults && selectedTestResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-2xl">테스트 결과 상세</CardTitle>
                  <CardDescription>
                    {selectedTestResult.plugin_id} • {selectedTestResult.test_type} • {new Date(selectedTestResult.started_at).toLocaleString()}
                  </CardDescription>
                </div>
                <Button variant="outline" onClick={() => setShowTestResults(false)}>
                  닫기
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="text-lg font-semibold mb-2">요약</h3>
                  <div className="space-y-2 text-sm">
                    <div>플러그인: {selectedTestResult.plugin_id}</div>
                    <div>테스트 유형: {selectedTestResult.test_type}</div>
                    <div>시작 시간: {new Date(selectedTestResult.started_at).toLocaleString()}</div>
                    <div>완료 시간: {new Date(selectedTestResult.completed_at).toLocaleString()}</div>
                    <div>총 테스트: {selectedTestResult.total_tests}</div>
                    <div>통과: {selectedTestResult.passed_tests}</div>
                    <div>실패: {selectedTestResult.failed_tests}</div>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-2">상태</h3>
                  <Badge className={getTestStatusColor(selectedTestResult.status)}>
                    {getTestStatusText(selectedTestResult.status)}
                  </Badge>
                </div>
              </div>
              
              {selectedTestResult.results && (
                <div>
                  <h3 className="text-lg font-semibold mb-2">개별 테스트 결과</h3>
                  <div className="space-y-4 max-h-64 overflow-y-auto">
                    {selectedTestResult.results.map((test: any, index: number) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{test.test_type}</span>
                            <Badge className={getTestStatusColor(test.status)}>
                              {getTestStatusText(test.status)}
                            </Badge>
                          </div>
                          <span className="text-sm text-gray-500">
                            {test.duration.toFixed(2)}초
                          </span>
                        </div>
                        <p className="text-sm text-gray-600">{test.message}</p>
                        {test.details && test.details.stderr && (
                          <details className="mt-2">
                            <summary className="text-sm font-medium cursor-pointer">오류 상세</summary>
                            <pre className="text-xs bg-gray-100 p-2 mt-2 rounded overflow-x-auto">
                              {test.details.stderr}
                            </pre>
                          </details>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* 문서 상세 모달 */}
      {showDocumentation && documentation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-2xl">{documentation.plugin_id} 문서</CardTitle>
                  <CardDescription>
                    마지막 업데이트: {new Date(documentation.last_updated).toLocaleString()}
                  </CardDescription>
                </div>
                <Button variant="outline" onClick={() => setShowDocumentation(false)}>
                  닫기
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-2">사용자 가이드</h3>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <pre className="whitespace-pre-wrap text-sm">{documentation.user_guide}</pre>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold mb-2">개발자 가이드</h3>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <pre className="whitespace-pre-wrap text-sm">{documentation.developer_guide}</pre>
                </div>
              </div>
              
              {documentation.api_docs && documentation.api_docs.endpoints && (
                <div>
                  <h3 className="text-lg font-semibold mb-2">API 문서</h3>
                  <div className="space-y-2">
                    {documentation.api_docs.endpoints.map((endpoint: any, index: number) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="font-medium">{endpoint.file}</div>
                        <div className="text-sm text-gray-600 mt-1">
                          라우트 수: {endpoint.routes?.length || 0}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {documentation.changelog && (
                <div>
                  <h3 className="text-lg font-semibold mb-2">변경 이력</h3>
                  <div className="space-y-2">
                    {documentation.changelog.map((change: any, index: number) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="font-medium">v{change.version}</div>
                        <div className="text-sm text-gray-500">{change.date}</div>
                        <ul className="text-sm mt-2">
                          {change.changes.map((c: string, i: number) => (
                            <li key={i}>• {c}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
} 