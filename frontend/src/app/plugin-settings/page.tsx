'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Settings, 
  Search, 
  Filter, 
  SortAsc, 
  SortDesc,
  Package,
  Code,
  Database,
  Shield,
  Zap,
  Palette,
  Globe,
  Bell,
  Lock,
  Unlock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Eye,
  Edit,
  Copy,
  Download,
  Upload,
  History,
  RefreshCw,
  Plus,
  Trash2,
  Star,
  Users,
  Activity,
  BarChart3,
  FileText,
  Workflow,
  TestTube,
  Settings2,
  Cog,
  Wrench,
  Archive,
  FolderOpen,
  FileCode,
  FileJson,
  FileArchive
} from 'lucide-react'
import PluginSettingsManager from '@/components/PluginSettingsManager'

interface Plugin {
  name: string
  version: string
  description: string
  author: string
  category: string
  enabled: boolean
  loaded: boolean
  has_settings: boolean
  settings_count: number
  last_modified: string
  complexity: 'simple' | 'medium' | 'complex'
  tags: string[]
}

interface PluginSettings {
  [key: string]: any
}

export default function PluginSettingsPage() {
  const [plugins, setPlugins] = useState<Plugin[]>([])
  const [filteredPlugins, setFilteredPlugins] = useState<Plugin[]>([])
  const [selectedPlugin, setSelectedPlugin] = useState<Plugin | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [sortBy, setSortBy] = useState('name')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [activeTab, setActiveTab] = useState('plugins')
  const [showSettings, setShowSettings] = useState(false)
  const [settingsData, setSettingsData] = useState<PluginSettings>({})
  const [categories, setCategories] = useState<string[]>([])
  const [stats, setStats] = useState({
    total: 0,
    enabled: 0,
    disabled: 0,
    withSettings: 0,
    withoutSettings: 0
  })

  // 플러그인 목록 로드
  const loadPlugins = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch('/api/plugins/list')
      const data = await response.json()
      
      if (data.status === 'success') {
        const pluginList = Object.values(data.data).map((plugin: any) => ({
          name: plugin.name,
          version: plugin.version,
          description: plugin.description,
          author: plugin.author,
          category: plugin.category,
          enabled: plugin.enabled,
          loaded: plugin.loaded,
          has_settings: plugin.has_settings || false,
          settings_count: plugin.settings_count || 0,
          last_modified: plugin.last_modified || new Date().toISOString(),
          complexity: plugin.complexity || 'simple',
          tags: plugin.tags || []
        }))
        
        setPlugins(pluginList)
        setFilteredPlugins(pluginList)
        
        // 카테고리 목록 추출
        const uniqueCategories = [...new Set(pluginList.map(p => p.category))]
        setCategories(uniqueCategories)
        
        // 통계 계산
        setStats({
          total: pluginList.length,
          enabled: pluginList.filter(p => p.enabled).length,
          disabled: pluginList.filter(p => !p.enabled).length,
          withSettings: pluginList.filter(p => p.has_settings).length,
          withoutSettings: pluginList.filter(p => !p.has_settings).length
        })
      } else {
        setError('플러그인 목록을 불러오는데 실패했습니다')
      }
    } catch (err) {
      setError('플러그인 목록을 불러오는데 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  // 필터링 및 정렬 적용
  useEffect(() => {
    let filtered = [...plugins]
    
    // 검색 필터
    if (searchQuery) {
      filtered = filtered.filter(plugin =>
        plugin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        plugin.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        plugin.author.toLowerCase().includes(searchQuery.toLowerCase()) ||
        plugin.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    }
    
    // 카테고리 필터
    if (categoryFilter) {
      filtered = filtered.filter(plugin => plugin.category === categoryFilter)
    }
    
    // 상태 필터
    if (statusFilter) {
      switch (statusFilter) {
        case 'enabled':
          filtered = filtered.filter(plugin => plugin.enabled)
          break
        case 'disabled':
          filtered = filtered.filter(plugin => !plugin.enabled)
          break
        case 'with_settings':
          filtered = filtered.filter(plugin => plugin.has_settings)
          break
        case 'without_settings':
          filtered = filtered.filter(plugin => !plugin.has_settings)
          break
      }
    }
    
    // 정렬
    filtered.sort((a, b) => {
      let aValue = a[sortBy as keyof Plugin]
      let bValue = b[sortBy as keyof Plugin]
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        aValue = aValue.toLowerCase()
        bValue = bValue.toLowerCase()
      }
      
      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1
      return 0
    })
    
    setFilteredPlugins(filtered)
  }, [plugins, searchQuery, categoryFilter, statusFilter, sortBy, sortOrder])

  // 초기 로드
  useEffect(() => {
    loadPlugins()
  }, [])

  // 플러그인 선택
  const handlePluginSelect = (plugin: Plugin) => {
    setSelectedPlugin(plugin)
    setShowSettings(true)
    setActiveTab('settings')
  }

  // 설정 변경 핸들러
  const handleSettingsChange = (newSettings: PluginSettings) => {
    setSettingsData(newSettings)
    // 플러그인 목록 새로고침
    loadPlugins()
  }

  // 복잡도 색상 반환
  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'simple': return 'bg-green-100 text-green-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'complex': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  // 복잡도 텍스트 반환
  const getComplexityText = (complexity: string) => {
    switch (complexity) {
      case 'simple': return '간단'
      case 'medium': return '보통'
      case 'complex': return '복잡'
      default: return '알 수 없음'
    }
  }

  // 카테고리 아이콘 반환
  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'core': return <Cog className="h-4 w-4" />
      case 'management': return <Settings2 className="h-4 w-4" />
      case 'security': return <Shield className="h-4 w-4" />
      case 'performance': return <Zap className="h-4 w-4" />
      case 'ui': return <Palette className="h-4 w-4" />
      case 'integration': return <Globe className="h-4 w-4" />
      case 'notification': return <Bell className="h-4 w-4" />
      case 'authentication': return <Lock className="h-4 w-4" />
      case 'analytics': return <BarChart3 className="h-4 w-4" />
      case 'workflow': return <Workflow className="h-4 w-4" />
      case 'testing': return <TestTube className="h-4 w-4" />
      default: return <Package className="h-4 w-4" />
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">플러그인 설정 관리</h1>
          <p className="text-muted-foreground">
            플러그인의 설정을 중앙에서 관리하고 모니터링합니다
          </p>
        </div>
        <Button onClick={loadPlugins} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          새로고침
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Package className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">전체</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <div>
                <p className="text-sm font-medium">활성화</p>
                <p className="text-2xl font-bold">{stats.enabled}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <XCircle className="h-4 w-4 text-red-600" />
              <div>
                <p className="text-sm font-medium">비활성화</p>
                <p className="text-2xl font-bold">{stats.disabled}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Settings className="h-4 w-4 text-blue-600" />
              <div>
                <p className="text-sm font-medium">설정 있음</p>
                <p className="text-2xl font-bold">{stats.withSettings}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <FileText className="h-4 w-4 text-gray-600" />
              <div>
                <p className="text-sm font-medium">설정 없음</p>
                <p className="text-2xl font-bold">{stats.withoutSettings}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 메인 탭 */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="plugins">플러그인 목록</TabsTrigger>
          <TabsTrigger value="settings" disabled={!selectedPlugin}>
            설정 관리
          </TabsTrigger>
        </TabsList>

        {/* 플러그인 목록 */}
        <TabsContent value="plugins" className="space-y-4">
          {/* 필터 및 검색 */}
          <Card>
            <CardContent className="p-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="space-y-2">
                  <Label>검색</Label>
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="플러그인 검색..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-8"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label>카테고리</Label>
                  <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="모든 카테고리" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">모든 카테고리</SelectItem>
                      {categories.map(category => (
                        <SelectItem key={category} value={category}>
                          {category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label>상태</Label>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="모든 상태" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">모든 상태</SelectItem>
                      <SelectItem value="enabled">활성화됨</SelectItem>
                      <SelectItem value="disabled">비활성화됨</SelectItem>
                      <SelectItem value="with_settings">설정 있음</SelectItem>
                      <SelectItem value="without_settings">설정 없음</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label>정렬</Label>
                  <div className="flex space-x-2">
                    <Select value={sortBy} onValueChange={setSortBy}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="name">이름</SelectItem>
                        <SelectItem value="category">카테고리</SelectItem>
                        <SelectItem value="version">버전</SelectItem>
                        <SelectItem value="last_modified">수정일</SelectItem>
                        <SelectItem value="complexity">복잡도</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                    >
                      {sortOrder === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 플러그인 그리드 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredPlugins.map((plugin) => (
              <Card 
                key={plugin.name} 
                className={`cursor-pointer transition-all hover:shadow-md ${
                  selectedPlugin?.name === plugin.name ? 'ring-2 ring-primary' : ''
                }`}
                onClick={() => handlePluginSelect(plugin)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      {getCategoryIcon(plugin.category)}
                      <div>
                        <CardTitle className="text-lg">{plugin.name}</CardTitle>
                        <CardDescription className="text-sm">
                          v{plugin.version} • {plugin.author}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex flex-col items-end space-y-1">
                      <Badge variant={plugin.enabled ? 'default' : 'secondary'}>
                        {plugin.enabled ? '활성화' : '비활성화'}
                      </Badge>
                      <Badge variant="outline" className={getComplexityColor(plugin.complexity)}>
                        {getComplexityText(plugin.complexity)}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="pt-0">
                  <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                    {plugin.description}
                  </p>
                  
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <div className="flex items-center space-x-2">
                      {plugin.has_settings ? (
                        <Settings className="h-3 w-3" />
                      ) : (
                        <FileText className="h-3 w-3" />
                      )}
                      <span>
                        {plugin.has_settings ? `${plugin.settings_count}개 설정` : '설정 없음'}
                      </span>
                    </div>
                    <span>
                      {new Date(plugin.last_modified).toLocaleDateString()}
                    </span>
                  </div>
                  
                  {plugin.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {plugin.tags.slice(0, 3).map((tag, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                      {plugin.tags.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{plugin.tags.length - 3}
                        </Badge>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredPlugins.length === 0 && (
            <Card>
              <CardContent className="p-8 text-center">
                <Package className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">조건에 맞는 플러그인이 없습니다</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* 설정 관리 */}
        <TabsContent value="settings" className="space-y-4">
          {selectedPlugin && (
            <div className="space-y-4">
              {/* 선택된 플러그인 정보 */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {getCategoryIcon(selectedPlugin.category)}
                      <div>
                        <CardTitle>{selectedPlugin.name}</CardTitle>
                        <CardDescription>
                          v{selectedPlugin.version} • {selectedPlugin.author} • {selectedPlugin.category}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant={selectedPlugin.enabled ? 'default' : 'secondary'}>
                        {selectedPlugin.enabled ? '활성화' : '비활성화'}
                      </Badge>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedPlugin(null)
                          setShowSettings(false)
                          setActiveTab('plugins')
                        }}
                      >
                        목록으로
                      </Button>
                    </div>
                  </div>
                </CardHeader>
              </Card>

              {/* 설정 관리자 */}
              <PluginSettingsManager
                pluginName={selectedPlugin.name}
                onSettingsChange={handleSettingsChange}
              />
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
} 