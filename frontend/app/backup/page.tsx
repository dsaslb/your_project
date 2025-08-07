'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Button } from '../../src/components/ui/button';
import { Input } from '../../src/components/ui/input';
import { Label } from '../../src/components/ui/label';
import { Badge } from '../../src/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../../src/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../src/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../src/components/ui/select';
import { Switch } from '../../src/components/ui/switch';
import { Progress } from '../../src/components/ui/progress';
import { Alert, AlertDescription } from '../../src/components/ui/alert';
import { Textarea } from '../../src/components/ui/textarea';
import { Save, Play, Trash2, Download, Upload, Clock, CheckCircle, XCircle, AlertTriangle, Settings, Database, FileText, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';

// 타입 정의
interface BackupStats {
  total_backups: number;
  successful_backups: number;
  failed_backups: number;
  success_rate: number;
  total_size_mb: number;
  recent_backups_7d: number;
  active_jobs: number;
}

interface BackupJob {
  job_id: string;
  name: string;
  source_paths: string[];
  destination: string;
  schedule: string;
  last_run: string | null;
  next_run: string | null;
  is_active: boolean;
  created_at: string | null;
}

interface BackupRecord {
  backup_id: string;
  job_id: string;
  name: string;
  file_path: string;
  file_size: number;
  file_size_mb: number;
  checksum: string;
  backup_type: string;
  status: 'success' | 'failed' | 'in_progress';
  start_time: string;
  end_time: string | null;
  error_message: string | null;
  metadata: any;
}

interface BackupJobFormData {
  name: string;
  source_paths: string[];
  destination: string;
  schedule: string;
}

interface RestoreFormData {
  destination: string;
}

// 샘플 데이터
const sampleStats: BackupStats = {
  total_backups: 156,
  successful_backups: 142,
  failed_backups: 14,
  success_rate: 91,
  total_size_mb: 2048.5,
  recent_backups_7d: 12,
  active_jobs: 8
};

const sampleJobs: BackupJob[] = [
  {
    job_id: '1',
    name: '데이터베이스 백업',
    source_paths: ['/var/lib/mysql', '/etc/mysql'],
    destination: '/backup/database',
    schedule: 'daily',
    last_run: '2024-01-15T02:00:00Z',
    next_run: '2024-01-16T02:00:00Z',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    job_id: '2',
    name: '파일 시스템 백업',
    source_paths: ['/home', '/var/www'],
    destination: '/backup/files',
    schedule: 'weekly',
    last_run: '2024-01-14T03:00:00Z',
    next_run: '2024-01-21T03:00:00Z',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    job_id: '3',
    name: '설정 파일 백업',
    source_paths: ['/etc'],
    destination: '/backup/config',
    schedule: 'monthly',
    last_run: '2024-01-01T04:00:00Z',
    next_run: '2024-02-01T04:00:00Z',
    is_active: false,
    created_at: '2024-01-01T00:00:00Z'
  }
];

const sampleRecords: BackupRecord[] = [
  {
    backup_id: '1',
    job_id: '1',
    name: '데이터베이스 백업',
    file_path: '/backup/database/backup_20240115_020000.sql',
    file_size: 524288000,
    file_size_mb: 500,
    checksum: 'a1b2c3d4e5f6',
    backup_type: 'full',
    status: 'success',
    start_time: '2024-01-15T02:00:00Z',
    end_time: '2024-01-15T02:15:00Z',
    error_message: null,
    metadata: { compression: 'gzip', version: '1.0' }
  },
  {
    backup_id: '2',
    job_id: '2',
    name: '파일 시스템 백업',
    file_path: '/backup/files/backup_20240114_030000.tar.gz',
    file_size: 1073741824,
    file_size_mb: 1024,
    checksum: 'b2c3d4e5f6a1',
    backup_type: 'incremental',
    status: 'success',
    start_time: '2024-01-14T03:00:00Z',
    end_time: '2024-01-14T03:45:00Z',
    error_message: null,
    metadata: { compression: 'gzip', version: '1.0' }
  },
  {
    backup_id: '3',
    job_id: '1',
    name: '데이터베이스 백업',
    file_path: '/backup/database/backup_20240114_020000.sql',
    file_size: 524288000,
    file_size_mb: 500,
    checksum: 'c3d4e5f6a1b2',
    backup_type: 'full',
    status: 'failed',
    start_time: '2024-01-14T02:00:00Z',
    end_time: '2024-01-14T02:05:00Z',
    error_message: '디스크 공간 부족',
    metadata: { compression: 'gzip', version: '1.0' }
  }
];

const sampleSchedulerStatus = {
  is_running: true,
  backup_schedule: 'daily',
  backup_time: '02:00'
};

const BackupPage: React.FC = () => {
  // 상태 관리
  const [stats, setStats] = useState<BackupStats | null>(null);
  const [jobs, setJobs] = useState<BackupJob[]>([]);
  const [records, setRecords] = useState<BackupRecord[]>([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showRestoreDialog, setShowRestoreDialog] = useState(false);
  const [selectedJob, setSelectedJob] = useState<BackupJob | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<BackupRecord | null>(null);
  const [schedulerStatus, setSchedulerStatus] = useState<any>(null);
  const [recordFilter, setRecordFilter] = useState({
    job_id: 'all',
    status: 'all'
  });
  const [isLoading, setIsLoading] = useState(false);

  // 폼 데이터
  const [jobForm, setJobForm] = useState<BackupJobFormData>({
    name: '',
    source_paths: [''],
    destination: '',
    schedule: 'daily'
  });

  const [restoreForm, setRestoreForm] = useState<RestoreFormData>({
    destination: ''
  });

  // 데이터 로드 함수들
  const loadBackupStats = useCallback(async () => {
    try {
      setStats(sampleStats);
    } catch (error) {
      toast.error('백업 통계를 불러오는데 실패했습니다');
    }
  }, []);

  const loadBackupJobs = useCallback(async () => {
    try {
      setJobs(sampleJobs);
    } catch (error) {
      toast.error('백업 작업을 불러오는데 실패했습니다');
    }
  }, []);

  const loadBackupRecords = useCallback(async () => {
    try {
      let filteredRecords = sampleRecords;
      
      if (recordFilter.status !== 'all') {
        filteredRecords = filteredRecords.filter(record => record.status === recordFilter.status);
      }
      
      setRecords(filteredRecords);
    } catch (error) {
      toast.error('백업 기록을 불러오는데 실패했습니다');
    }
  }, [recordFilter]);

  const loadSchedulerStatus = useCallback(async () => {
    try {
      setSchedulerStatus(sampleSchedulerStatus);
    } catch (error) {
      toast.error('스케줄러 상태를 불러오는데 실패했습니다');
    }
  }, []);

  // 백업 작업 생성
  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!jobForm.name || !jobForm.destination || jobForm.source_paths.length === 0) {
      toast.error('필수 필드를 입력해주세요');
      return;
    }

    setIsLoading(true);
    try {
      const newJob: BackupJob = {
        job_id: (jobs.length + 1).toString(),
        name: jobForm.name,
        source_paths: jobForm.source_paths.filter(path => path.trim() !== ''),
        destination: jobForm.destination,
        schedule: jobForm.schedule,
        last_run: null,
        next_run: null,
        is_active: true,
        created_at: new Date().toISOString()
      };
      
      setJobs(prev => [...prev, newJob]);
      setShowCreateDialog(false);
      setJobForm({
        name: '',
        source_paths: [''],
        destination: '',
        schedule: 'daily'
      });
      
      toast.success('백업 작업이 생성되었습니다');
    } catch (error) {
      toast.error('백업 작업 생성에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // 백업 작업 수정
  const handleUpdateJob = async (jobId: string, updates: Partial<BackupJob>) => {
    setIsLoading(true);
    try {
      setJobs(prev => prev.map(job => 
        job.job_id === jobId ? { ...job, ...updates } : job
      ));
      toast.success('백업 작업이 업데이트되었습니다');
    } catch (error) {
      toast.error('백업 작업 수정에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // 백업 작업 삭제
  const handleDeleteJob = async (jobId: string) => {
    setIsLoading(true);
    try {
      setJobs(prev => prev.filter(job => job.job_id !== jobId));
      toast.success('백업 작업이 삭제되었습니다');
    } catch (error) {
      toast.error('백업 작업 삭제에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // 백업 실행
  const handleRunBackup = async (jobId: string, backupType: string = 'full') => {
    setIsLoading(true);
    try {
      toast.success('백업이 시작되었습니다');
      // 실제로는 백업 작업을 실행하는 API 호출
    } catch (error) {
      toast.error('백업 실행에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // 백업 테스트
  const handleTestBackup = async (jobId: string) => {
    setIsLoading(true);
    try {
      toast.success('백업 테스트가 완료되었습니다');
    } catch (error) {
      toast.error('백업 테스트에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // 백업 복구
  const handleRestoreBackup = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!restoreForm.destination) {
      toast.error('복구 대상 경로를 입력해주세요');
      return;
    }

    setIsLoading(true);
    try {
      toast.success('백업 복구가 시작되었습니다');
      setShowRestoreDialog(false);
      setRestoreForm({ destination: '' });
    } catch (error) {
      toast.error('백업 복구에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // 백업 기록 삭제
  const handleDeleteRecord = async (backupId: string) => {
    setIsLoading(true);
    try {
      setRecords(prev => prev.filter(record => record.backup_id !== backupId));
      toast.success('백업 기록이 삭제되었습니다');
    } catch (error) {
      toast.error('백업 기록 삭제에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // 스케줄러 시작
  const handleStartScheduler = async () => {
    setIsLoading(true);
    try {
      setSchedulerStatus((prev: any) => ({ ...prev, is_running: true }));
      toast.success('백업 스케줄러가 시작되었습니다');
    } catch (error) {
      toast.error('스케줄러 시작에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // 스케줄러 중지
  const handleStopScheduler = async () => {
    setIsLoading(true);
    try {
      setSchedulerStatus((prev: any) => ({ ...prev, is_running: false }));
      toast.success('백업 스케줄러가 중지되었습니다');
    } catch (error) {
      toast.error('스케줄러 중지에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // 정리
  const handleCleanup = async () => {
    setIsLoading(true);
    try {
      toast.success('백업 정리가 완료되었습니다');
    } catch (error) {
      toast.error('백업 정리에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // 소스 경로 추가
  const addSourcePath = () => {
    setJobForm(prev => ({
      ...prev,
      source_paths: [...prev.source_paths, '']
    }));
  };

  // 소스 경로 제거
  const removeSourcePath = (index: number) => {
    setJobForm(prev => ({
      ...prev,
      source_paths: prev.source_paths.filter((_, i) => i !== index)
    }));
  };

  // 소스 경로 업데이트
  const updateSourcePath = (index: number, value: string) => {
    setJobForm(prev => ({
      ...prev,
      source_paths: prev.source_paths.map((path, i) => i === index ? value : path)
    }));
  };

  // 초기 데이터 로드
  useEffect(() => {
    loadBackupStats();
    loadBackupJobs();
    loadBackupRecords();
    loadSchedulerStatus();
  }, [loadBackupStats, loadBackupJobs, loadBackupRecords, loadSchedulerStatus]);

  // 필터 변경 시 재로드
  useEffect(() => {
    loadBackupRecords();
  }, [recordFilter, loadBackupRecords]);

  // 유틸리티 함수들
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'bg-green-500/20 text-green-400';
      case 'failed': return 'bg-red-500/20 text-red-400';
      case 'in_progress': return 'bg-yellow-500/20 text-yellow-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getScheduleText = (schedule: string) => {
    switch (schedule) {
      case 'daily': return '매일';
      case 'weekly': return '매주';
      case 'monthly': return '매월';
      default: return schedule;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR');
  };

  const formatFileSize = (sizeMB: number) => {
    if (sizeMB < 1) {
      return `${(sizeMB * 1024).toFixed(1)} KB`;
    } else if (sizeMB < 1024) {
      return `${sizeMB.toFixed(1)} MB`;
    } else {
      return `${(sizeMB / 1024).toFixed(1)} GB`;
    }
  };

  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Database className="w-8 h-8 text-blue-400" />
          백업 관리
        </h1>
        <p className="text-gray-300 mt-2">데이터 백업 및 복구를 관리합니다</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-3 mb-6">
        <Button 
          onClick={() => setShowCreateDialog(true)}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <Save className="w-4 h-4 mr-2" />
          백업 작업 생성
        </Button>
        <Button 
          onClick={handleCleanup} 
          variant="outline"
          className="border-white/20 text-white hover:bg-white/10"
        >
          <Trash2 className="w-4 h-4 mr-2" />
          정리
        </Button>
        <Button 
          onClick={() => {
            loadBackupStats();
            loadBackupJobs();
            loadBackupRecords();
            loadSchedulerStatus();
          }}
          variant="outline"
          className="border-white/20 text-white hover:bg-white/10"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          새로고침
        </Button>
      </div>

      {/* 백업 통계 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">총 백업</CardTitle>
              <Database className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.total_backups}</div>
              <p className="text-xs text-gray-300">전체 백업 수</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">성공률</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.success_rate}%</div>
              <Progress value={stats.success_rate} className="mt-2" />
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">총 크기</CardTitle>
              <FileText className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{formatFileSize(stats.total_size_mb)}</div>
              <p className="text-xs text-gray-300">백업 파일 총 크기</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">활성 작업</CardTitle>
              <Settings className="h-4 w-4 text-orange-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.active_jobs}</div>
              <p className="text-xs text-gray-300">실행 중인 백업 작업</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 스케줄러 상태 */}
      {schedulerStatus && (
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20 mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-white">백업 스케줄러</CardTitle>
                <CardDescription className="text-gray-300">자동 백업 스케줄러 상태</CardDescription>
              </div>
              <div className="flex gap-2">
                {schedulerStatus.is_running ? (
                  <Button 
                    onClick={handleStopScheduler} 
                    variant="destructive" 
                    size="sm"
                    className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                  >
                    중지
                  </Button>
                ) : (
                  <Button 
                    onClick={handleStartScheduler} 
                    size="sm"
                    className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
                  >
                    시작
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <Badge className={schedulerStatus.is_running ? "bg-green-500/20 text-green-400" : "bg-gray-500/20 text-gray-400"}>
                {schedulerStatus.is_running ? "실행 중" : "중지됨"}
              </Badge>
              <span className="text-sm text-gray-300">
                스케줄: {getScheduleText(schedulerStatus.backup_schedule)} {schedulerStatus.backup_time}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 메인 탭 */}
      <Tabs defaultValue="jobs" className="space-y-4">
        <TabsList className="bg-white/10 border border-white/20">
          <TabsTrigger value="jobs" className="text-white data-[state=active]:bg-white/20">백업 작업</TabsTrigger>
          <TabsTrigger value="records" className="text-white data-[state=active]:bg-white/20">백업 기록</TabsTrigger>
        </TabsList>

        {/* 백업 작업 탭 */}
        <TabsContent value="jobs" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="text-white">백업 작업</CardTitle>
              <CardDescription className="text-gray-300">등록된 백업 작업을 관리합니다</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {jobs.map((job) => (
                  <div key={job.job_id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-medium text-white">{job.name}</h3>
                          <Badge className={job.is_active ? "bg-green-500/20 text-green-400" : "bg-gray-500/20 text-gray-400"}>
                            {job.is_active ? "활성" : "비활성"}
                          </Badge>
                          <Badge className="bg-white/10 text-white border border-white/20">
                            {getScheduleText(job.schedule)}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-300 space-y-1">
                          <div>소스: {job.source_paths.join(', ')}</div>
                          <div>대상: {job.destination}</div>
                          {job.last_run && (
                            <div>마지막 실행: {formatDate(job.last_run)}</div>
                          )}
                          {job.next_run && (
                            <div>다음 실행: {formatDate(job.next_run)}</div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          onClick={() => handleRunBackup(job.job_id)}
                          disabled={!job.is_active}
                          className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
                        >
                          <Play className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleTestBackup(job.job_id)}
                          disabled={!job.is_active}
                          className="border-white/20 text-white hover:bg-white/10"
                        >
                          테스트
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleUpdateJob(job.job_id, { is_active: !job.is_active })}
                          className="border-white/20 text-white hover:bg-white/10"
                        >
                          {job.is_active ? '비활성화' : '활성화'}
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleDeleteJob(job.job_id)}
                          className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
                
                {jobs.length === 0 && (
                  <div className="text-center py-8 text-gray-300">
                    등록된 백업 작업이 없습니다.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 백업 기록 탭 */}
        <TabsContent value="records" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-white">백업 기록</CardTitle>
                  <CardDescription className="text-gray-300">백업 실행 기록을 확인합니다</CardDescription>
                </div>
                <div className="flex gap-2">
                  <Select value={recordFilter.status} onValueChange={(value) => setRecordFilter(prev => ({ ...prev, status: value }))}>
                    <SelectTrigger className="w-32 bg-white/10 border-white/20 text-white">
                      <SelectValue placeholder="상태" />
                    </SelectTrigger>
                    <SelectContent className="bg-white/10 border-white/20">
                      <SelectItem value="all">전체</SelectItem>
                      <SelectItem value="success">성공</SelectItem>
                      <SelectItem value="failed">실패</SelectItem>
                      <SelectItem value="in_progress">진행 중</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {records.map((record) => (
                  <div key={record.backup_id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-medium text-white">{record.name}</h3>
                          <Badge className={getStatusColor(record.status)}>
                            {record.status === 'success' ? '성공' : 
                             record.status === 'failed' ? '실패' : '진행 중'}
                          </Badge>
                          <Badge className="bg-white/10 text-white border border-white/20">
                            {record.backup_type}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-300 space-y-1">
                          <div>파일 크기: {formatFileSize(record.file_size_mb)}</div>
                          <div>시작 시간: {formatDate(record.start_time)}</div>
                          {record.end_time && (
                            <div>완료 시간: {formatDate(record.end_time)}</div>
                          )}
                          {record.error_message && (
                            <div className="text-red-400">오류: {record.error_message}</div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {record.status === 'success' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setSelectedRecord(record);
                              setShowRestoreDialog(true);
                            }}
                            className="border-white/20 text-white hover:bg-white/10"
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleDeleteRecord(record.backup_id)}
                          className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
                
                {records.length === 0 && (
                  <div className="text-center py-8 text-gray-300">
                    백업 기록이 없습니다.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 백업 작업 생성 다이얼로그 */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-2xl bg-white/10 backdrop-blur-sm border border-white/20">
          <DialogHeader>
            <DialogTitle className="text-white">백업 작업 생성</DialogTitle>
            <DialogDescription className="text-gray-300">새로운 백업 작업을 생성합니다</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateJob} className="space-y-4">
            <div>
              <Label htmlFor="name" className="text-gray-300">작업 이름</Label>
              <Input
                id="name"
                value={jobForm.name}
                onChange={(e) => setJobForm(prev => ({ ...prev, name: e.target.value }))}
                placeholder="백업 작업 이름을 입력하세요"
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            
            <div>
              <Label className="text-gray-300">소스 경로</Label>
              <div className="space-y-2">
                {jobForm.source_paths.map((path, index) => (
                  <div key={index} className="flex gap-2">
                    <Input
                      value={path}
                      onChange={(e) => updateSourcePath(index, e.target.value)}
                      placeholder="백업할 파일/폴더 경로를 입력하세요"
                      className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                    />
                    {jobForm.source_paths.length > 1 && (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => removeSourcePath(index)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                ))}
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={addSourcePath}
                  className="border-white/20 text-white hover:bg-white/10"
                >
                  경로 추가
                </Button>
              </div>
            </div>
            
            <div>
              <Label htmlFor="destination" className="text-gray-300">대상 경로</Label>
              <Input
                id="destination"
                value={jobForm.destination}
                onChange={(e) => setJobForm(prev => ({ ...prev, destination: e.target.value }))}
                placeholder="백업 파일을 저장할 경로를 입력하세요"
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            
            <div>
              <Label htmlFor="schedule" className="text-gray-300">스케줄</Label>
              <Select value={jobForm.schedule} onValueChange={(value) => setJobForm(prev => ({ ...prev, schedule: value }))}>
                <SelectTrigger className="bg-white/10 border-white/20 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white/10 border-white/20">
                  <SelectItem value="daily">매일</SelectItem>
                  <SelectItem value="weekly">매주</SelectItem>
                  <SelectItem value="monthly">매월</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex gap-2">
              <Button 
                type="submit" 
                disabled={isLoading}
                className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
              >
                {isLoading ? "생성 중..." : "백업 작업 생성"}
              </Button>
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => setShowCreateDialog(false)}
                className="border-white/20 text-white hover:bg-white/10"
              >
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* 백업 복구 다이얼로그 */}
      <Dialog open={showRestoreDialog} onOpenChange={setShowRestoreDialog}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20">
          <DialogHeader>
            <DialogTitle className="text-white">백업 복구</DialogTitle>
            <DialogDescription className="text-gray-300">백업에서 데이터를 복구합니다</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleRestoreBackup} className="space-y-4">
            <div>
              <Label htmlFor="restore-destination" className="text-gray-300">복구 대상 경로</Label>
              <Input
                id="restore-destination"
                value={restoreForm.destination}
                onChange={(e) => setRestoreForm(prev => ({ ...prev, destination: e.target.value }))}
                placeholder="복구할 경로를 입력하세요"
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            
            {selectedRecord && (
              <Alert className="bg-white/5 border border-white/10">
                <AlertTriangle className="h-4 w-4 text-yellow-400" />
                <AlertDescription className="text-gray-300">
                  <strong className="text-white">{selectedRecord.name}</strong> 백업을 복구합니다.
                  <br />
                  파일 크기: {formatFileSize(selectedRecord.file_size_mb)}
                  <br />
                  백업 시간: {formatDate(selectedRecord.start_time)}
                </AlertDescription>
              </Alert>
            )}
            
            <div className="flex gap-2">
              <Button 
                type="submit" 
                disabled={isLoading}
                className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
              >
                {isLoading ? "복구 중..." : "복구 시작"}
              </Button>
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => setShowRestoreDialog(false)}
                className="border-white/20 text-white hover:bg-white/10"
              >
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default BackupPage; 