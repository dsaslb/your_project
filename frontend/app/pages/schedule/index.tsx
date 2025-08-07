'use client';

import React, { useState, useEffect } from 'react';
import { format, startOfWeek, addDays, isToday, isSameDay } from 'date-fns';
import { ko } from 'date-fns/locale';
import { 
  Clock, 
  Calendar, 
  Users, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Plus,
  Edit,
  Trash2,
  Download,
  Upload,
  RefreshCw
} from 'lucide-react';

interface ScheduleData {
  id: string;
  date: string;
  employee_id: number;
  employee_name: string;
  start_time: string;
  end_time: string;
  position: string;
  status: 'scheduled' | 'completed' | 'absent';
}

interface AttendanceData {
  id: string;
  date: string;
  employee_id: number;
  employee_name: string;
  check_in: string;
  check_out?: string;
  status: 'present' | 'late' | 'absent' | 'early_leave';
  location?: string;
}

interface AIAnalysisResult {
  efficiency_score: number;
  summary: string;
  issues: string[];
  recommendations: string[];
  sections: {
    staffing: any;
    attendance: any;
    work_hours: any;
  };
  visual_indicators: {
    icon: string;
    color: string;
  };
}

const SchedulePage: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [schedules, setSchedules] = useState<ScheduleData[]>([]);
  const [attendance, setAttendance] = useState<AttendanceData[]>([]);
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState<'schedule' | 'attendance' | 'analysis'>('schedule');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<ScheduleData | null>(null);

  // 샘플 데이터
  useEffect(() => {
    // 실제로는 API에서 데이터를 가져옴
    const sampleSchedules: ScheduleData[] = [
      {
        id: '1',
        date: format(new Date(), 'yyyy-MM-dd'),
        employee_id: 1,
        employee_name: '김철수',
        start_time: '09:00',
        end_time: '17:00',
        position: '매니저',
        status: 'scheduled'
      },
      {
        id: '2',
        date: format(new Date(), 'yyyy-MM-dd'),
        employee_id: 2,
        employee_name: '이영희',
        start_time: '10:00',
        end_time: '18:00',
        position: '직원',
        status: 'scheduled'
      }
    ];

    const sampleAttendance: AttendanceData[] = [
      {
        id: '1',
        date: format(new Date(), 'yyyy-MM-dd'),
        employee_id: 1,
        employee_name: '김철수',
        check_in: '08:55',
        status: 'present'
      },
      {
        id: '2',
        date: format(new Date(), 'yyyy-MM-dd'),
        employee_id: 2,
        employee_name: '이영희',
        check_in: '10:15',
        status: 'late'
      }
    ];

    setSchedules(sampleSchedules);
    setAttendance(sampleAttendance);
  }, []);

  // 주간 날짜 생성
  const weekDates = Array.from({ length: 7 }, (_, i) => 
    addDays(startOfWeek(currentDate, { weekStartsOn: 1 }), i)
  );

  // AI 분석 실행
  const runAIAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      // 실제로는 AI 분석 API 호출
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockAnalysis: AIAnalysisResult = {
        efficiency_score: 75.5,
        summary: "전반적으로 양호하나 일부 개선이 필요합니다.",
        issues: [
          "인원 과다 배치: 3시간",
          "지각 발생: 1건"
        ],
        recommendations: [
          "과다 배치된 시간대의 인원을 다른 시간대로 재배치하거나 근무 시간을 조정하세요.",
          "지각 방지를 위한 출근 시간 관리 시스템을 강화하세요."
        ],
        sections: {
          staffing: { score: 80, status: 'good' },
          attendance: { score: 85, status: 'acceptable' },
          work_hours: { score: 70, status: 'warning' }
        },
        visual_indicators: {
          icon: '⚠️',
          color: '#F59E0B'
        }
      };
      
      setAiAnalysis(mockAnalysis);
    } catch (error) {
      console.error('AI 분석 중 오류:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 출근 체크인
  const handleClockIn = (employeeId: number) => {
    const now = new Date();
    const newAttendance: AttendanceData = {
      id: Date.now().toString(),
      date: format(now, 'yyyy-MM-dd'),
      employee_id: employeeId,
      employee_name: schedules.find(s => s.employee_id === employeeId)?.employee_name || '',
      check_in: format(now, 'HH:mm'),
      status: 'present'
    };
    setAttendance(prev => [...prev, newAttendance]);
  };

  // 퇴근 체크아웃
  const handleClockOut = (employeeId: number) => {
    const now = new Date();
    setAttendance(prev => prev.map(att => 
      att.employee_id === employeeId && att.date === format(now, 'yyyy-MM-dd')
        ? { ...att, check_out: format(now, 'HH:mm') }
        : att
    ));
  };

  // 스케줄 추가
  const handleAddSchedule = (scheduleData: Omit<ScheduleData, 'id'>) => {
    const newSchedule: ScheduleData = {
      ...scheduleData,
      id: Date.now().toString()
    };
    setSchedules(prev => [...prev, newSchedule]);
    setShowAddModal(false);
  };

  // 스케줄 수정
  const handleEditSchedule = (schedule: ScheduleData) => {
    setEditingSchedule(schedule);
    setShowAddModal(true);
  };

  // 스케줄 삭제
  const handleDeleteSchedule = (scheduleId: string) => {
    setSchedules(prev => prev.filter(s => s.id !== scheduleId));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">스케줄 관리</h1>
              <p className="text-sm text-gray-600">매장별 출퇴근 기록 및 스케줄 관리</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowAddModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                스케줄 추가
              </button>
              <button
                onClick={runAIAnalysis}
                disabled={isAnalyzing}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
              >
                {isAnalyzing ? (
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <TrendingUp className="w-4 h-4 mr-2" />
                )}
                {isAnalyzing ? '분석 중...' : 'AI 분석'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 탭 네비게이션 */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: 'schedule', label: '스케줄', icon: Calendar },
              { id: 'attendance', label: '출퇴근', icon: Clock },
              { id: 'analysis', label: 'AI 분석', icon: TrendingUp }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* 메인 컨텐츠 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'schedule' && (
          <div className="space-y-6">
            {/* 주간 캘린더 */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b">
                <h2 className="text-lg font-medium text-gray-900">주간 스케줄</h2>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-7 gap-4">
                  {weekDates.map((date) => (
                    <div
                      key={date.toISOString()}
                      className={`p-4 rounded-lg border ${
                        isToday(date) ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200'
                      }`}
                    >
                      <div className="text-center">
                        <div className="text-sm font-medium text-gray-900">
                          {format(date, 'EEE', { locale: ko })}
                        </div>
                        <div className={`text-lg font-bold ${
                          isToday(date) ? 'text-blue-600' : 'text-gray-700'
                        }`}>
                          {format(date, 'd')}
                        </div>
                      </div>
                      <div className="mt-3 space-y-2">
                        {schedules
                          .filter(s => isSameDay(new Date(s.date), date))
                          .map(schedule => (
                            <div
                              key={schedule.id}
                              className="p-2 bg-white rounded border text-xs"
                            >
                              <div className="font-medium">{schedule.employee_name}</div>
                              <div className="text-gray-600">
                                {schedule.start_time} - {schedule.end_time}
                              </div>
                            </div>
                          ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 스케줄 목록 */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b">
                <h2 className="text-lg font-medium text-gray-900">스케줄 목록</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        직원명
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        날짜
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        근무시간
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        직책
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        상태
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        작업
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {schedules.map((schedule) => (
                      <tr key={schedule.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {schedule.employee_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {format(new Date(schedule.date), 'yyyy-MM-dd')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {schedule.start_time} - {schedule.end_time}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {schedule.position}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            schedule.status === 'completed' ? 'bg-green-100 text-green-800' :
                            schedule.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {schedule.status === 'completed' ? '완료' :
                             schedule.status === 'scheduled' ? '예정' : '결근'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                          <button
                            onClick={() => handleEditSchedule(schedule)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteSchedule(schedule.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'attendance' && (
          <div className="space-y-6">
            {/* 출퇴근 현황 */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b">
                <h2 className="text-lg font-medium text-gray-900">출퇴근 현황</h2>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {schedules.map((schedule) => {
                    const todayAttendance = attendance.find(
                      att => att.employee_id === schedule.employee_id && 
                             att.date === format(new Date(), 'yyyy-MM-dd')
                    );
                    
                    return (
                      <div key={schedule.id} className="bg-gray-50 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">
                              {schedule.employee_name}
                            </h3>
                            <p className="text-sm text-gray-600">{schedule.position}</p>
                          </div>
                          <div className="text-right">
                            <div className="text-sm text-gray-600">예정 시간</div>
                            <div className="text-sm font-medium">
                              {schedule.start_time} - {schedule.end_time}
                            </div>
                          </div>
                        </div>
                        
                        <div className="space-y-3">
                          {todayAttendance ? (
                            <div className="space-y-2">
                              <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-600">출근:</span>
                                <span className="text-sm font-medium">{todayAttendance.check_in}</span>
                              </div>
                              {todayAttendance.check_out && (
                                <div className="flex items-center justify-between">
                                  <span className="text-sm text-gray-600">퇴근:</span>
                                  <span className="text-sm font-medium">{todayAttendance.check_out}</span>
                                </div>
                              )}
                              <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-600">상태:</span>
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                  todayAttendance.status === 'present' ? 'bg-green-100 text-green-800' :
                                  todayAttendance.status === 'late' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                  {todayAttendance.status === 'present' ? '정상' :
                                   todayAttendance.status === 'late' ? '지각' : '결근'}
                                </span>
                              </div>
                              {!todayAttendance.check_out && (
                                <button
                                  onClick={() => handleClockOut(schedule.employee_id)}
                                  className="w-full mt-2 px-3 py-2 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700"
                                >
                                  퇴근 체크
                                </button>
                              )}
                            </div>
                          ) : (
                            <div className="text-center">
                              <p className="text-sm text-gray-500 mb-3">출근하지 않음</p>
                              <button
                                onClick={() => handleClockIn(schedule.employee_id)}
                                className="w-full px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700"
                              >
                                출근 체크
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* 출퇴근 기록 */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b">
                <h2 className="text-lg font-medium text-gray-900">출퇴근 기록</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        직원명
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        날짜
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        출근시간
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        퇴근시간
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        상태
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {attendance.map((record) => (
                      <tr key={record.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {record.employee_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {format(new Date(record.date), 'yyyy-MM-dd')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {record.check_in}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {record.check_out || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            record.status === 'present' ? 'bg-green-100 text-green-800' :
                            record.status === 'late' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {record.status === 'present' ? '정상' :
                             record.status === 'late' ? '지각' : '결근'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="space-y-6">
            {aiAnalysis ? (
              <>
                {/* AI 분석 결과 요약 */}
                <div className="bg-white rounded-lg shadow">
                  <div className="px-6 py-4 border-b">
                    <h2 className="text-lg font-medium text-gray-900">AI 분석 결과</h2>
                  </div>
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center space-x-4">
                        <div 
                          className="w-16 h-16 rounded-full flex items-center justify-center text-2xl"
                          style={{ backgroundColor: `${aiAnalysis.visual_indicators.color}20` }}
                        >
                          {aiAnalysis.visual_indicators.icon}
                        </div>
                        <div>
                          <h3 className="text-xl font-bold text-gray-900">
                            효율성 점수: {aiAnalysis.efficiency_score}점
                          </h3>
                          <p className="text-gray-600">{aiAnalysis.summary}</p>
                        </div>
                      </div>
                      <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                        <Download className="w-4 h-4 mr-2 inline" />
                        리포트 다운로드
                      </button>
                    </div>

                    {/* 세부 분석 */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      {Object.entries(aiAnalysis.sections).map(([key, section]) => (
                        <div key={key} className="bg-gray-50 rounded-lg p-4">
                          <h4 className="font-medium text-gray-900 mb-2">
                            {key === 'staffing' ? '인력 배치' :
                             key === 'attendance' ? '출근률' : '근무시간'}
                          </h4>
                          <div className="text-2xl font-bold text-gray-900 mb-2">
                            {section.score}점
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${section.score}%` }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* 문제점 및 개선안 */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* 발견된 문제점 */}
                  <div className="bg-white rounded-lg shadow">
                    <div className="px-6 py-4 border-b">
                      <h3 className="text-lg font-medium text-gray-900 flex items-center">
                        <AlertTriangle className="w-5 h-5 mr-2 text-red-500" />
                        발견된 문제점
                      </h3>
                    </div>
                    <div className="p-6">
                      <ul className="space-y-3">
                        {aiAnalysis.issues.map((issue, index) => (
                          <li key={index} className="flex items-start space-x-3">
                            <XCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                            <span className="text-gray-700">{issue}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* 개선 제안 */}
                  <div className="bg-white rounded-lg shadow">
                    <div className="px-6 py-4 border-b">
                      <h3 className="text-lg font-medium text-gray-900 flex items-center">
                        <CheckCircle className="w-5 h-5 mr-2 text-green-500" />
                        개선 제안
                      </h3>
                    </div>
                    <div className="p-6">
                      <ul className="space-y-3">
                        {aiAnalysis.recommendations.map((recommendation, index) => (
                          <li key={index} className="flex items-start space-x-3">
                            <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                            <span className="text-gray-700">{recommendation}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <TrendingUp className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  AI 분석을 실행해주세요
                </h3>
                <p className="text-gray-600 mb-6">
                  스케줄과 출퇴근 데이터를 기반으로 AI가 효율성을 분석하고 개선안을 제시합니다.
                </p>
                <button
                  onClick={runAIAnalysis}
                  disabled={isAnalyzing}
                  className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                >
                  {isAnalyzing ? (
                    <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                  ) : (
                    <TrendingUp className="w-5 h-5 mr-2" />
                  )}
                  {isAnalyzing ? '분석 중...' : 'AI 분석 시작'}
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 스케줄 추가/수정 모달 */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingSchedule ? '스케줄 수정' : '스케줄 추가'}
              </h3>
              <form onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                handleAddSchedule({
                  date: formData.get('date') as string,
                  employee_id: parseInt(formData.get('employee_id') as string),
                  employee_name: formData.get('employee_name') as string,
                  start_time: formData.get('start_time') as string,
                  end_time: formData.get('end_time') as string,
                  position: formData.get('position') as string,
                  status: 'scheduled'
                });
              }}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">직원명</label>
                    <input
                      type="text"
                      name="employee_name"
                      defaultValue={editingSchedule?.employee_name}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">날짜</label>
                    <input
                      type="date"
                      name="date"
                      defaultValue={editingSchedule?.date || format(new Date(), 'yyyy-MM-dd')}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">시작시간</label>
                      <input
                        type="time"
                        name="start_time"
                        defaultValue={editingSchedule?.start_time}
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">종료시간</label>
                      <input
                        type="time"
                        name="end_time"
                        defaultValue={editingSchedule?.end_time}
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        required
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">직책</label>
                    <select
                      name="position"
                      defaultValue={editingSchedule?.position}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      required
                    >
                      <option value="">선택하세요</option>
                      <option value="매니저">매니저</option>
                      <option value="직원">직원</option>
                      <option value="아르바이트">아르바이트</option>
                    </select>
                  </div>
                </div>
                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddModal(false);
                      setEditingSchedule(null);
                    }}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    취소
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                  >
                    {editingSchedule ? '수정' : '추가'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SchedulePage;
