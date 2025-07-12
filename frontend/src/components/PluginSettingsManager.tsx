'use client'

import React, { useState, useEffect, useCallback } from 'react'
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
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { 
  Settings, 
  Save, 
  RotateCcw, 
  Upload, 
  Download, 
  History, 
  FileText, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Plus,
  Trash2,
  Copy,
  Eye,
  Edit,
  Clock,
  User,
  Hash,
  Code,
  Database,
  Shield,
  Zap,
  Palette,
  Globe,
  Bell,
  Lock,
  Unlock,
  RefreshCw,
  Play,
  Pause,
  Square,
  ChevronDown,
  ChevronRight,
  Search,
  Filter,
  SortAsc,
  SortDesc
} from 'lucide-react'
import { toast } from 'sonner'

interface PluginSettings {
  [key: string]: any
}

interface SettingsMetadata {
  last_modified: string
  modified_by: string
  version: string
  checksum: string
}

interface BackupInfo {
  version: string
  created_at: string
  size: number
  filename: string
}

interface SettingsTemplate {
  name: string
  description: string
  schema: any
  default_settings: PluginSettings
  migrations?: { [key: string]: any }
}

interface PluginSettingsManagerProps {
  pluginName: string
  onSettingsChange?: (settings: PluginSettings) => void
}

export default function PluginSettingsManager({ 
  pluginName, 
  onSettingsChange 
}: PluginSettingsManagerProps) {
  const [settings, setSettings] = useState<PluginSettings>({})
  const [metadata, setMetadata] = useState<SettingsMetadata | null>(null)
  const [template, setTemplate] = useState<SettingsTemplate | null>(null)
  const [backups, setBackups] = useState<BackupInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('general')
  const [showBackupDialog, setShowBackupDialog] = useState(false)
  const [showRestoreDialog, setShowRestoreDialog] = useState(false)
  const [showExportDialog, setShowExportDialog] = useState(false)
  const [showImportDialog, setShowImportDialog] = useState(false)
  const [showTemplateDialog, setShowTemplateDialog] = useState(false)
  const [showMigrationDialog, setShowMigrationDialog] = useState(false)
  const [selectedBackup, setSelectedBackup] = useState<BackupInfo | null>(null)
  const [exportFormat, setExportFormat] = useState('json')
  const [importData, setImportData] = useState('')
  const [importFormat, setImportFormat] = useState('json')
  const [migrationFromVersion, setMigrationFromVersion] = useState('')
  const [migrationToVersion, setMigrationToVersion] = useState('')
  const [validationErrors, setValidationErrors] = useState<string[]>([])
  const [hasChanges, setHasChanges] = useState(false)
  const [originalSettings, setOriginalSettings] = useState<PluginSettings>({})

  // 설정 로드
  const loadSettings = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`/api/plugin-settings/${pluginName}`)
      const data = await response.json()
      
      if (data.status === 'success') {
        setSettings(data.data.settings)
        setMetadata(data.data.metadata)
        setOriginalSettings(data.data.settings)
        setHasChanges(false)
      } else {
        setError(data.error || '설정을 불러오는데 실패했습니다')
      }
    } catch (err) {
      setError('설정을 불러오는데 실패했습니다')
    } finally {
      setLoading(false)
    }
  }, [pluginName])

  // 템플릿 로드
  const loadTemplate = useCallback(async () => {
    try {
      const response = await fetch(`/api/plugin-settings/${pluginName}/template`)
      const data = await response.json()
      
      if (data.status === 'success') {
        setTemplate(data.data)
      }
    } catch (err) {
      console.error('템플릿 로드 실패:', err)
    }
  }, [pluginName])

  // 백업 목록 로드
  const loadBackups = useCallback(async () => {
    try {
      const response = await fetch(`/api/plugin-settings/${pluginName}/backup`)
      const data = await response.json()
      
      if (data.status === 'success') {
        setBackups(data.data)
      }
    } catch (err) {
      console.error('백업 목록 로드 실패:', err)
    }
  }, [pluginName])

  // 초기 로드
  useEffect(() => {
    loadSettings()
    loadTemplate()
    loadBackups()
  }, [loadSettings, loadTemplate, loadBackups])

  // 설정 변경 감지
  useEffect(() => {
    setHasChanges(JSON.stringify(settings) !== JSON.stringify(originalSettings))
  }, [settings, originalSettings])

  // 설정 저장
  const saveSettings = async () => {
    try {
      setSaving(true)
      
      // 설정 검증
      const validationResponse = await fetch(`/api/plugin-settings/${pluginName}/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ settings })
      })
      
      const validationData = await validationResponse.json()
      
      if (!validationData.data.is_valid) {
        setValidationErrors(['설정이 유효하지 않습니다'])
        return
      }
      
      const response = await fetch(`/api/plugin-settings/${pluginName}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ settings })
      })
      
      const data = await response.json()
      
      if (data.status === 'success') {
        toast.success('설정이 성공적으로 저장되었습니다')
        setOriginalSettings(settings)
        setHasChanges(false)
        onSettingsChange?.(settings)
        await loadSettings() // 메타데이터 새로고침
      } else {
        setError(data.error || '설정 저장에 실패했습니다')
        toast.error(data.error || '설정 저장에 실패했습니다')
      }
    } catch (err) {
      setError('설정 저장에 실패했습니다')
      toast.error('설정 저장에 실패했습니다')
    } finally {
      setSaving(false)
    }
  }

  // 설정 초기화
  const resetSettings = async () => {
    try {
      const response = await fetch(`/api/plugin-settings/${pluginName}/reset`, {
        method: 'POST'
      })
      
      const data = await response.json()
      
      if (data.status === 'success') {
        toast.success('설정이 기본값으로 초기화되었습니다')
        await loadSettings()
      } else {
        toast.error(data.error || '설정 초기화에 실패했습니다')
      }
    } catch (err) {
      toast.error('설정 초기화에 실패했습니다')
    }
  }

  // 백업 생성
  const createBackup = async () => {
    try {
      const response = await fetch(`/api/plugin-settings/${pluginName}/backup`, {
        method: 'POST'
      })
      
      const data = await response.json()
      
      if (data.status === 'success') {
        toast.success('백업이 성공적으로 생성되었습니다')
        await loadBackups()
        setShowBackupDialog(false)
      } else {
        toast.error(data.error || '백업 생성에 실패했습니다')
      }
    } catch (err) {
      toast.error('백업 생성에 실패했습니다')
    }
  }

  // 백업 복원
  const restoreBackup = async () => {
    if (!selectedBackup) return
    
    try {
      const response = await fetch(`/api/plugin-settings/${pluginName}/backup/${selectedBackup.version}`, {
        method: 'POST'
      })
      
      const data = await response.json()
      
      if (data.status === 'success') {
        toast.success('백업이 성공적으로 복원되었습니다')
        await loadSettings()
        setShowRestoreDialog(false)
        setSelectedBackup(null)
      } else {
        toast.error(data.error || '백업 복원에 실패했습니다')
      }
    } catch (err) {
      toast.error('백업 복원에 실패했습니다')
    }
  }

  // 설정 내보내기
  const exportSettings = async () => {
    try {
      const response = await fetch(`/api/plugin-settings/${pluginName}/export?format=${exportFormat}`)
      const data = await response.json()
      
      if (data.status === 'success') {
        const blob = new Blob([data.data], { 
          type: exportFormat === 'json' ? 'application/json' : 'text/yaml' 
        })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${pluginName}_settings.${exportFormat}`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        
        toast.success('설정이 성공적으로 내보내졌습니다')
        setShowExportDialog(false)
      } else {
        toast.error(data.error || '설정 내보내기에 실패했습니다')
      }
    } catch (err) {
      toast.error('설정 내보내기에 실패했습니다')
    }
  }

  // 설정 가져오기
  const importSettings = async () => {
    if (!importData.trim()) {
      toast.error('가져올 데이터를 입력해주세요')
      return
    }
    
    try {
      const response = await fetch(`/api/plugin-settings/${pluginName}/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          import_data: importData, 
          format: importFormat 
        })
      })
      
      const data = await response.json()
      
      if (data.status === 'success') {
        toast.success('설정이 성공적으로 가져와졌습니다')
        await loadSettings()
        setShowImportDialog(false)
        setImportData('')
      } else {
        toast.error(data.error || '설정 가져오기에 실패했습니다')
      }
    } catch (err) {
      toast.error('설정 가져오기에 실패했습니다')
    }
  }

  // 설정 마이그레이션
  const migrateSettings = async () => {
    if (!migrationFromVersion || !migrationToVersion) {
      toast.error('마이그레이션 버전을 입력해주세요')
      return
    }
    
    try {
      const response = await fetch(`/api/plugin-settings/${pluginName}/migrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          from_version: migrationFromVersion, 
          to_version: migrationToVersion 
        })
      })
      
      const data = await response.json()
      
      if (data.status === 'success') {
        toast.success('설정 마이그레이션이 성공적으로 완료되었습니다')
        await loadSettings()
        setShowMigrationDialog(false)
        setMigrationFromVersion('')
        setMigrationToVersion('')
      } else {
        toast.error(data.error || '설정 마이그레이션에 실패했습니다')
      }
    } catch (err) {
      toast.error('설정 마이그레이션에 실패했습니다')
    }
  }

  // 설정 필드 업데이트
  const updateSetting = (path: string, value: any) => {
    const pathArray = path.split('.')
    const newSettings = { ...settings }
    let current = newSettings
    
    for (let i = 0; i < pathArray.length - 1; i++) {
      if (!current[pathArray[i]]) {
        current[pathArray[i]] = {}
      }
      current = current[pathArray[i]]
    }
    
    current[pathArray[pathArray.length - 1]] = value
    setSettings(newSettings)
  }

  // 설정 필드 렌더링
  const renderSettingField = (key: string, value: any, path: string = '') => {
    const fullPath = path ? `${path}.${key}` : key
    
    if (typeof value === 'boolean') {
      return (
        <div key={fullPath} className="flex items-center space-x-2">
          <Switch
            checked={value}
            onCheckedChange={(checked) => updateSetting(fullPath, checked)}
          />
          <Label className="text-sm font-medium">{key}</Label>
        </div>
      )
    } else if (typeof value === 'string') {
      return (
        <div key={fullPath} className="space-y-2">
          <Label className="text-sm font-medium">{key}</Label>
          <Input
            value={value}
            onChange={(e) => updateSetting(fullPath, e.target.value)}
            placeholder={`${key} 입력`}
          />
        </div>
      )
    } else if (typeof value === 'number') {
      return (
        <div key={fullPath} className="space-y-2">
          <Label className="text-sm font-medium">{key}</Label>
          <Input
            type="number"
            value={value}
            onChange={(e) => updateSetting(fullPath, Number(e.target.value))}
            placeholder={`${key} 입력`}
          />
        </div>
      )
    } else if (Array.isArray(value)) {
      return (
        <div key={fullPath} className="space-y-2">
          <Label className="text-sm font-medium">{key}</Label>
          <Textarea
            value={JSON.stringify(value, null, 2)}
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value)
                updateSetting(fullPath, parsed)
              } catch (err) {
                // JSON 파싱 실패 시 무시
              }
            }}
            placeholder={`${key} 배열 입력`}
            rows={3}
          />
        </div>
      )
    } else if (typeof value === 'object' && value !== null) {
      return (
        <div key={fullPath} className="space-y-4 border-l-2 border-gray-200 pl-4">
          <Label className="text-sm font-medium">{key}</Label>
          {Object.entries(value).map(([subKey, subValue]) => 
            renderSettingField(subKey, subValue, fullPath)
          )}
        </div>
      )
    }
    
    return null
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
          <h2 className="text-2xl font-bold tracking-tight">플러그인 설정 관리</h2>
          <p className="text-muted-foreground">
            {pluginName} 플러그인의 설정을 관리합니다
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {hasChanges && (
            <Badge variant="secondary" className="text-orange-600">
              변경사항 있음
            </Badge>
          )}
          <Button
            variant="outline"
            onClick={resetSettings}
            disabled={saving}
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            초기화
          </Button>
          <Button
            onClick={saveSettings}
            disabled={saving || !hasChanges}
          >
            <Save className="h-4 w-4 mr-2" />
            {saving ? '저장 중...' : '저장'}
          </Button>
        </div>
      </div>

      {/* 메타데이터 */}
      {metadata && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileText className="h-5 w-5" />
              <span>설정 정보</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <Label className="text-muted-foreground">마지막 수정</Label>
                <p className="font-medium">
                  {new Date(metadata.last_modified).toLocaleString()}
                </p>
              </div>
              <div>
                <Label className="text-muted-foreground">수정자</Label>
                <p className="font-medium">{metadata.modified_by}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">버전</Label>
                <p className="font-medium">{metadata.version}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">체크섬</Label>
                <p className="font-medium font-mono text-xs">
                  {metadata.checksum.substring(0, 8)}...
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 메인 탭 */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="general">일반</TabsTrigger>
          <TabsTrigger value="advanced">고급</TabsTrigger>
          <TabsTrigger value="backup">백업</TabsTrigger>
          <TabsTrigger value="template">템플릿</TabsTrigger>
          <TabsTrigger value="tools">도구</TabsTrigger>
        </TabsList>

        {/* 일반 설정 */}
        <TabsContent value="general" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>기본 설정</CardTitle>
              <CardDescription>
                플러그인의 기본 동작을 제어하는 설정입니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(settings).map(([key, value]) => 
                renderSettingField(key, value)
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 고급 설정 */}
        <TabsContent value="advanced" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>고급 설정</CardTitle>
              <CardDescription>
                개발자 및 고급 사용자를 위한 설정입니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-sm font-medium">디버그 모드</Label>
                    <Switch
                      checked={settings.debug_mode || false}
                      onCheckedChange={(checked) => updateSetting('debug_mode', checked)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-sm font-medium">자동 재로드</Label>
                    <Switch
                      checked={settings.auto_reload || false}
                      onCheckedChange={(checked) => updateSetting('auto_reload', checked)}
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label className="text-sm font-medium">로그 레벨</Label>
                  <Select
                    value={settings.log_level || 'INFO'}
                    onValueChange={(value) => updateSetting('log_level', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="DEBUG">DEBUG</SelectItem>
                      <SelectItem value="INFO">INFO</SelectItem>
                      <SelectItem value="WARNING">WARNING</SelectItem>
                      <SelectItem value="ERROR">ERROR</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label className="text-sm font-medium">권한 설정</Label>
                  <Textarea
                    value={JSON.stringify(settings.permissions || [], null, 2)}
                    onChange={(e) => {
                      try {
                        const parsed = JSON.parse(e.target.value)
                        updateSetting('permissions', parsed)
                      } catch (err) {
                        // JSON 파싱 실패 시 무시
                      }
                    }}
                    placeholder="권한 배열 입력"
                    rows={3}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 백업 관리 */}
        <TabsContent value="backup" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>백업 관리</span>
                <Button onClick={createBackup} variant="outline" size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  백업 생성
                </Button>
              </CardTitle>
              <CardDescription>
                설정 백업을 생성하고 복원할 수 있습니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              {backups.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>버전</TableHead>
                      <TableHead>생성일</TableHead>
                      <TableHead>크기</TableHead>
                      <TableHead>작업</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {backups.map((backup) => (
                      <TableRow key={backup.version}>
                        <TableCell className="font-mono">{backup.version}</TableCell>
                        <TableCell>
                          {new Date(backup.created_at).toLocaleString()}
                        </TableCell>
                        <TableCell>{(backup.size / 1024).toFixed(1)} KB</TableCell>
                        <TableCell>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedBackup(backup)
                              setShowRestoreDialog(true)
                            }}
                          >
                            <History className="h-4 w-4 mr-2" />
                            복원
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  백업이 없습니다
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 템플릿 관리 */}
        <TabsContent value="template" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>설정 템플릿</CardTitle>
              <CardDescription>
                설정 스키마와 기본값을 관리합니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              {template ? (
                <div className="space-y-4">
                  <div>
                    <Label className="text-sm font-medium">템플릿 이름</Label>
                    <p className="text-sm text-muted-foreground">{template.name}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">설명</Label>
                    <p className="text-sm text-muted-foreground">{template.description}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">스키마</Label>
                    <Textarea
                      value={JSON.stringify(template.schema, null, 2)}
                      readOnly
                      rows={6}
                      className="font-mono text-xs"
                    />
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  템플릿이 없습니다
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 도구 */}
        <TabsContent value="tools" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>내보내기/가져오기</CardTitle>
                <CardDescription>
                  설정을 파일로 내보내거나 가져올 수 있습니다
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button
                  onClick={() => setShowExportDialog(true)}
                  variant="outline"
                  className="w-full"
                >
                  <Download className="h-4 w-4 mr-2" />
                  설정 내보내기
                </Button>
                <Button
                  onClick={() => setShowImportDialog(true)}
                  variant="outline"
                  className="w-full"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  설정 가져오기
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>마이그레이션</CardTitle>
                <CardDescription>
                  설정 버전을 업그레이드합니다
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button
                  onClick={() => setShowMigrationDialog(true)}
                  variant="outline"
                  className="w-full"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  설정 마이그레이션
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* 백업 생성 다이얼로그 */}
      <Dialog open={showBackupDialog} onOpenChange={setShowBackupDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>백업 생성</DialogTitle>
            <DialogDescription>
              현재 설정을 백업으로 저장합니다
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowBackupDialog(false)}>
              취소
            </Button>
            <Button onClick={createBackup}>
              백업 생성
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 백업 복원 다이얼로그 */}
      <Dialog open={showRestoreDialog} onOpenChange={setShowRestoreDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>백업 복원</DialogTitle>
            <DialogDescription>
              선택한 백업으로 설정을 복원합니다. 현재 설정은 덮어써집니다.
            </DialogDescription>
          </DialogHeader>
          {selectedBackup && (
            <div className="space-y-2">
              <p><strong>버전:</strong> {selectedBackup.version}</p>
              <p><strong>생성일:</strong> {new Date(selectedBackup.created_at).toLocaleString()}</p>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRestoreDialog(false)}>
              취소
            </Button>
            <Button onClick={restoreBackup} variant="destructive">
              복원
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 내보내기 다이얼로그 */}
      <Dialog open={showExportDialog} onOpenChange={setShowExportDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>설정 내보내기</DialogTitle>
            <DialogDescription>
              설정을 파일로 내보냅니다
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>형식</Label>
              <Select value={exportFormat} onValueChange={setExportFormat}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="json">JSON</SelectItem>
                  <SelectItem value="yaml">YAML</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowExportDialog(false)}>
              취소
            </Button>
            <Button onClick={exportSettings}>
              내보내기
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 가져오기 다이얼로그 */}
      <Dialog open={showImportDialog} onOpenChange={setShowImportDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>설정 가져오기</DialogTitle>
            <DialogDescription>
              파일에서 설정을 가져옵니다. 현재 설정은 덮어써집니다.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>형식</Label>
              <Select value={importFormat} onValueChange={setImportFormat}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="json">JSON</SelectItem>
                  <SelectItem value="yaml">YAML</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>데이터</Label>
              <Textarea
                value={importData}
                onChange={(e) => setImportData(e.target.value)}
                placeholder="설정 데이터를 입력하세요"
                rows={8}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowImportDialog(false)}>
              취소
            </Button>
            <Button onClick={importSettings}>
              가져오기
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 마이그레이션 다이얼로그 */}
      <Dialog open={showMigrationDialog} onOpenChange={setShowMigrationDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>설정 마이그레이션</DialogTitle>
            <DialogDescription>
              설정 버전을 업그레이드합니다
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>현재 버전</Label>
              <Input
                value={migrationFromVersion}
                onChange={(e) => setMigrationFromVersion(e.target.value)}
                placeholder="예: 1.0.0"
              />
            </div>
            <div className="space-y-2">
              <Label>대상 버전</Label>
              <Input
                value={migrationToVersion}
                onChange={(e) => setMigrationToVersion(e.target.value)}
                placeholder="예: 2.0.0"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowMigrationDialog(false)}>
              취소
            </Button>
            <Button onClick={migrateSettings}>
              마이그레이션
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
} 