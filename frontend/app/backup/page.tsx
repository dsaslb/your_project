'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Badge } from '../../components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Switch } from '../../components/ui/switch';
import { Progress } from '../../components/ui/progress';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Textarea } from '../../components/ui/textarea';
import { Save, Play, Trash2, Download, Upload, Clock, CheckCircle, XCircle, AlertTriangle, Settings, Database, FileText } from 'lucide-react';
// import { useLoadingState } from '../../hooks/useLoadingState';
import { useErrorHandler } from '../../hooks/useErrorHandler';
import { ApiClient } from '../../lib/api-client';

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
    job_id: '',
    status: ''
  });

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

  // 훅 사용
  const [isLoading, setIsLoading] = useState(false);
  const { handleError } = useErrorHandler();
    // 데이터 로드 함수들
  const loadBackupStats = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/backup/stats');
      setStats(response.data);
    } catch (error) {
      handleError(error, '백업 통계를 불러오는데 실패했습니다');
    }
  }, [apiClient, handleError]);

  const loadBackupJobs = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/backup/jobs');
      setJobs(response.data.jobs);
    } catch (error) {
      handleError(error, '백업 작업을 불러오는데 실패했습니다');
    }
  }, [apiClient, handleError]);

  const loadBackupRecords = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (recordFilter.job_id) params.append('job_id', recordFilter.job_id);
      if (recordFilter.status) params.append('status', recordFilter.status);
      
      const response = await apiClient.get(`/api/backup/records?${params.toString()}`);
      setRecords(response.data.records);
    } catch (error) {
      handleError(error, '백업 기록을 불러오는데 실패했습니다');
    }
  }, [apiClient, handleError, recordFilter]);

  const loadSchedulerStatus = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/backup/scheduler/status');
      setSchedulerStatus(response.data);
    } catch (error) {
      handleError(error, '스케줄러 상태를 불러오는데 실패했습니다');
    }
  }, [apiClient, handleError]);

  // 백업 작업 생성
  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!jobForm.name || !jobForm.destination || jobForm.source_paths.length === 0) {
      showError('필수 필드를 입력해주세요');
      return;
    }

    await withLoading(async () => {
      try {
        const response = await apiClient.post('/api/backup/jobs', jobForm);
        
        setShowCreateDialog(false);
        setJobForm({
          name: '',
          source_paths: [''],
          destination: '',
          schedule: 'daily'
        });
        
        await loadBackupJobs();
        await loadBackupStats();
        
        showError('백업 작업이 생성되었습니다', 'success');
      } catch (error: any) {
        if (error.response?.data?.error) {
          showError(error.response.data.error);
        } else {
          showError('백업 작업 생성에 실패했습니다');
        }
      }
    });
  };

  // 백업 작업 수정
  const handleUpdateJob = async (jobId: string, updates: Partial<BackupJob>) => {
    await withLoading(async () => {
      try {
        await apiClient.put(`/api/backup/jobs/${jobId}`, updates);
        await loadBackupJobs();
        showError('백업 작업이 업데이트되었습니다', 'success');
      } catch (error) {
        handleError(error, '백업 작업 수정에 실패했습니다');
      }
    });
  };

  // 백업 작업 삭제
  const handleDeleteJob = async (jobId: string) => {
    if (!confirm('정말로 이 백업 작업을 삭제하시겠습니까?')) {
      return;
    }

    await withLoading(async () => {
      try {
        await apiClient.delete(`/api/backup/jobs/${jobId}`);
        await loadBackupJobs();
        await loadBackupStats();
        showError('백업 작업이 삭제되었습니다', 'success');
      } catch (error) {
        handleError(error, '백업 작업 삭제에 실패했습니다');
      }
    });
  };

  // 백업 실행
  const handleRunBackup = async (jobId: string, backupType: string = 'full') => {
    await withLoading(async () => {
      try {
        const response = await apiClient.post(`/api/backup/jobs/${jobId}/run`, {
          backup_type: backupType
        });
        
        await loadBackupRecords();
        await loadBackupStats();
        
        showError('백업이 시작되었습니다', 'success');
      } catch (error) {
        handleError(error, '백업 실행에 실패했습니다');
      }
    });
  };

  // 백업 테스트
  const handleTestBackup = async (jobId: string) => {
    await withLoading(async () => {
      try {
        await apiClient.post(`/api/backup/jobs/${jobId}/test`);
        showError('백업 테스트가 성공했습니다', 'success');
      } catch (error) {
        showError('백업 테스트가 실패했습니다');
      }
    });
  };

  // 백업 복구
  const handleRestoreBackup = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedRecord || !restoreForm.destination) {
      showError('복구 대상 경로를 입력해주세요');
      return;
    }

    await withLoading(async () => {
      try {
        await apiClient.post(`/api/backup/records/${selectedRecord.backup_id}/restore`, restoreForm);
        
        setShowRestoreDialog(false);
        setRestoreForm({ destination: '' });
        setSelectedRecord(null);
        
        showError('백업에서 복구가 완료되었습니다', 'success');
      } catch (error) {
        handleError(error, '백업 복구에 실패했습니다');
      }
    });
  };

  // 백업 기록 삭제
  const handleDeleteRecord = async (backupId: string) => {
    if (!confirm('정말로 이 백업 기록을 삭제하시겠습니까?')) {
      return;
    }

    await withLoading(async () => {
      try {
        await apiClient.delete(`/api/backup/records/${backupId}`);
        await loadBackupRecords();
        await loadBackupStats();
        showError('백업 기록이 삭제되었습니다', 'success');
      } catch (error) {
        handleError(error, '백업 기록 삭제에 실패했습니다');
      }
    });
  };

  // 스케줄러 제어
  const handleStartScheduler = async () => {
    await withLoading(async () => {
      try {
        await apiClient.post('/api/backup/scheduler/start');
        await loadSchedulerStatus();
        showError('백업 스케줄러가 시작되었습니다', 'success');
      } catch (error) {
        handleError(error, '스케줄러 시작에 실패했습니다');
      }
    });
  };

  const handleStopScheduler = async () => {
    await withLoading(async () => {
      try {
        await apiClient.post('/api/backup/scheduler/stop');
        await loadSchedulerStatus();
        showError('백업 스케줄러가 중지되었습니다', 'success');
      } catch (error) {
        handleError(error, '스케줄러 중지에 실패했습니다');
      }
    });
  };

  // 오래된 백업 정리
  const handleCleanup = async () => {
    if (!confirm('오래된 백업을 정리하시겠습니까?')) {
      return;
    }

    await withLoading(async () => {
      try {
        await apiClient.post('/api/backup/cleanup');
        await loadBackupRecords();
        await loadBackupStats();
        showError('오래된 백업이 정리되었습니다', 'success');
      } catch (error) {
        handleError(error, '백업 정리에 실패했습니다');
      }
    });
  };

  // 소스 경로 추가/제거
  const addSourcePath = () => {
    setJobForm(prev => ({
      ...prev,
      source_paths: [...prev.source_paths, '']
    }));
  };

  const removeSourcePath = (index: number) => {
    setJobForm(prev => ({
      ...prev,
      source_paths: prev.source_paths.filter((_, i) => i !== index)
    }));
  };

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
      case 'success': return 'default';
      case 'failed': return 'destructive';
      case 'in_progress': return 'secondary';
      default: return 'default';
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
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">백업 관리</h1>
          <p className="text-muted-foreground">데이터 백업 및 복구를 관리합니다</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowCreateDialog(true)}>
            <Save className="w-4 h-4 mr-2" />
            백업 작업 생성
          </Button>
          <Button onClick={handleCleanup} variant="outline">
            <Trash2 className="w-4 h-4 mr-2" />
            정리
          </Button>
        </div>
      </div>

      {/* 백업 통계 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 백업</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_backups}</div>
              <p className="text-xs text-muted-foreground">전체 백업 수</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">성공률</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.success_rate}%</div>
              <Progress value={stats.success_rate} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 크기</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatFileSize(stats.total_size_mb)}</div>
              <p className="text-xs text-muted-foreground">백업 파일 총 크기</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">활성 작업</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.active_jobs}</div>
              <p className="text-xs text-muted-foreground">실행 중인 백업 작업</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 스케줄러 상태 */}
      {schedulerStatus && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>백업 스케줄러</CardTitle>
                <CardDescription>자동 백업 스케줄러 상태</CardDescription>
              </div>
              <div className="flex gap-2">
                {schedulerStatus.is_running ? (
                  <Button onClick={handleStopScheduler} variant="destructive" size="sm">
                    중지
                  </Button>
                ) : (
                  <Button onClick={handleStartScheduler} size="sm">
                    시작
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <Badge variant={schedulerStatus.is_running ? "default" : "secondary"}>
                {schedulerStatus.is_running ? "실행 중" : "중지됨"}
              </Badge>
              <span className="text-sm text-muted-foreground">
                스케줄: {getScheduleText(schedulerStatus.backup_schedule)} {schedulerStatus.backup_time}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 메인 탭 */}
      <Tabs defaultValue="jobs" className="space-y-4">
        <TabsList>
          <TabsTrigger value="jobs">백업 작업</TabsTrigger>
          <TabsTrigger value="records">백업 기록</TabsTrigger>
        </TabsList>

        {/* 백업 작업 탭 */}
        <TabsContent value="jobs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>백업 작업</CardTitle>
              <CardDescription>등록된 백업 작업을 관리합니다</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {jobs.map((job) => (
                  <div key={job.job_id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-medium">{job.name}</h3>
                        <Badge variant={job.is_active ? "default" : "secondary"}>
                          {job.is_active ? "활성" : "비활성"}
                        </Badge>
                        <Badge variant="outline">
                          {getScheduleText(job.schedule)}
                        </Badge>
                      </div>
                      <div className="text-sm text-muted-foreground space-y-1">
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
                      >
                        <Play className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleTestBackup(job.job_id)}
                        disabled={!job.is_active}
                      >
                        테스트
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleUpdateJob(job.job_id, { is_active: !job.is_active })}
                      >
                        {job.is_active ? '비활성화' : '활성화'}
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDeleteJob(job.job_id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
                
                {jobs.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    등록된 백업 작업이 없습니다.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 백업 기록 탭 */}
        <TabsContent value="records" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>백업 기록</CardTitle>
                  <CardDescription>백업 실행 기록을 확인합니다</CardDescription>
                </div>
                <div className="flex gap-2">
                  <Select value={recordFilter.status} onValueChange={(value) => setRecordFilter(prev => ({ ...prev, status: value }))}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="상태" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">전체</SelectItem>
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
                  <div key={record.backup_id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-medium">{record.name}</h3>
                        <Badge variant={getStatusColor(record.status)}>
                          {record.status === 'success' ? '성공' : 
                           record.status === 'failed' ? '실패' : '진행 중'}
                        </Badge>
                        <Badge variant="outline">
                          {record.backup_type}
                        </Badge>
                      </div>
                      <div className="text-sm text-muted-foreground space-y-1">
                        <div>파일 크기: {formatFileSize(record.file_size_mb)}</div>
                        <div>시작 시간: {formatDate(record.start_time)}</div>
                        {record.end_time && (
                          <div>완료 시간: {formatDate(record.end_time)}</div>
                        )}
                        {record.error_message && (
                          <div className="text-red-500">오류: {record.error_message}</div>
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
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDeleteRecord(record.backup_id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
                
                {records.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
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
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>백업 작업 생성</DialogTitle>
            <DialogDescription>새로운 백업 작업을 생성합니다</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateJob} className="space-y-4">
            <div>
              <Label htmlFor="name">작업 이름</Label>
              <Input
                id="name"
                value={jobForm.name}
                onChange={(e) => setJobForm(prev => ({ ...prev, name: e.target.value }))}
                placeholder="백업 작업 이름을 입력하세요"
              />
            </div>
            
            <div>
              <Label>소스 경로</Label>
              <div className="space-y-2">
                {jobForm.source_paths.map((path, index) => (
                  <div key={index} className="flex gap-2">
                    <Input
                      value={path}
                      onChange={(e) => updateSourcePath(index, e.target.value)}
                      placeholder="백업할 파일/폴더 경로를 입력하세요"
                    />
                    {jobForm.source_paths.length > 1 && (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => removeSourcePath(index)}
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
                >
                  경로 추가
                </Button>
              </div>
            </div>
            
            <div>
              <Label htmlFor="destination">대상 경로</Label>
              <Input
                id="destination"
                value={jobForm.destination}
                onChange={(e) => setJobForm(prev => ({ ...prev, destination: e.target.value }))}
                placeholder="백업 파일을 저장할 경로를 입력하세요"
              />
            </div>
            
            <div>
              <Label htmlFor="schedule">스케줄</Label>
              <Select value={jobForm.schedule} onValueChange={(value) => setJobForm(prev => ({ ...prev, schedule: value }))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="daily">매일</SelectItem>
                  <SelectItem value="weekly">매주</SelectItem>
                  <SelectItem value="monthly">매월</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex gap-2">
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "생성 중..." : "백업 작업 생성"}
              </Button>
              <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* 백업 복구 다이얼로그 */}
      <Dialog open={showRestoreDialog} onOpenChange={setShowRestoreDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>백업 복구</DialogTitle>
            <DialogDescription>백업에서 데이터를 복구합니다</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleRestoreBackup} className="space-y-4">
            <div>
              <Label htmlFor="restore-destination">복구 대상 경로</Label>
              <Input
                id="restore-destination"
                value={restoreForm.destination}
                onChange={(e) => setRestoreForm(prev => ({ ...prev, destination: e.target.value }))}
                placeholder="복구할 경로를 입력하세요"
              />
            </div>
            
            {selectedRecord && (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  <strong>{selectedRecord.name}</strong> 백업을 복구합니다.
                  <br />
                  파일 크기: {formatFileSize(selectedRecord.file_size_mb)}
                  <br />
                  백업 시간: {formatDate(selectedRecord.start_time)}
                </AlertDescription>
              </Alert>
            )}
            
            <div className="flex gap-2">
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "복구 중..." : "복구 시작"}
              </Button>
              <Button type="button" variant="outline" onClick={() => setShowRestoreDialog(false)}>
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