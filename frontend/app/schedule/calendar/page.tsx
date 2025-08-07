'use client';

import React, { useState, useEffect, useRef } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import koLocale from '@fullcalendar/core/locales/ko';
import { 
  Calendar, 
  Clock, 
  Users, 
  TrendingUp, 
  Plus,
  Edit,
  Trash2,
  Download,
  Upload,
  RefreshCw,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

interface CalendarEvent {
  id: string;
  title: string;
  start: string;
  end: string;
  employee_id: number;
  employee_name: string;
  position: string;
  status: 'scheduled' | 'completed' | 'absent';
  backgroundColor?: string;
  borderColor?: string;
  extendedProps: {
    employee_id: number;
    employee_name: string;
    position: string;
    status: string;
  };
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

const ScheduleCalendar: React.FC = () => {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [showEventModal, setShowEventModal] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [viewMode, setViewMode] = useState<'dayGridMonth' | 'timeGridWeek' | 'timeGridDay'>('dayGridMonth');
  const calendarRef = useRef<any>(null);

  // 샘플 데이터 초기화
  useEffect(() => {
    const sampleEvents: CalendarEvent[] = [
      {
        id: '1',
        title: '김철수 (매니저)',
        start: '2025-01-07T09:00:00',
        end: '2025-01-07T17:00:00',
        employee_id: 1,
        employee_name: '김철수',
        position: '매니저',
        status: 'scheduled',
        backgroundColor: '#3B82F6',
        borderColor: '#2563EB',
        extendedProps: {
          employee_id: 1,
          employee_name: '김철수',
          position: '매니저',
          status: 'scheduled'
        }
      },
      {
        id: '2',
        title: '이영희 (직원)',
        start: '2025-01-07T10:00:00',
        end: '2025-01-07T18:00:00',
        employee_id: 2,
        employee_name: '이영희',
        position: '직원',
        status: 'scheduled',
        backgroundColor: '#10B981',
        borderColor: '#059669',
        extendedProps: {
          employee_id: 2,
          employee_name: '이영희',
          position: '직원',
          status: 'scheduled'
        }
      },
      {
        id: '3',
        title: '박민수 (아르바이트)',
        start: '2025-01-08T12:00:00',
        end: '2025-01-08T18:00:00',
        employee_id: 3,
        employee_name: '박민수',
        position: '아르바이트',
        status: 'scheduled',
        backgroundColor: '#F59E0B',
        borderColor: '#D97706',
        extendedProps: {
          employee_id: 3,
          employee_name: '박민수',
          position: '아르바이트',
          status: 'scheduled'
        }
      }
    ];
    setEvents(sampleEvents);
  }, []);

  // AI 분석 실행
  const runAIAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      // 실제로는 AI 분석 API 호출
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockAnalysis: AIAnalysisResult = {
        efficiency_score: 78.5,
        summary: "전반적으로 양호하나 일부 시간대 인력 조정이 필요합니다.",
        issues: [
          "월요일 오후 인원 과다: 2시간",
          "수요일 오전 인원 부족: 1시간",
          "지각 발생: 1건"
        ],
        recommendations: [
          "월요일 14:00-16:00 시간대 인원 1명 감축",
          "수요일 09:00-11:00 시간대 아르바이트 추가 배정",
          "출근 시간 관리 시스템 강화"
        ],
        sections: {
          staffing: { score: 75, status: 'warning' },
          attendance: { score: 85, status: 'acceptable' },
          work_hours: { score: 80, status: 'good' }
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

  // 이벤트 클릭 핸들러
  const handleEventClick = (clickInfo: any) => {
    setSelectedEvent(clickInfo.event);
    setShowEventModal(true);
  };

  // 날짜 클릭 핸들러
  const handleDateClick = (arg: any) => {
    setShowAddModal(true);
    // 선택된 날짜 정보를 모달에 전달
  };

  // 이벤트 드래그 앤 드롭 핸들러
  const handleEventDrop = (dropInfo: any) => {
    const updatedEvents = events.map(event => {
      if (event.id === dropInfo.event.id) {
        return {
          ...event,
          start: dropInfo.event.startStr,
          end: dropInfo.event.endStr
        };
      }
      return event;
    });
    setEvents(updatedEvents);
  };

  // 이벤트 리사이즈 핸들러
  const handleEventResize = (resizeInfo: any) => {
    const updatedEvents = events.map(event => {
      if (event.id === resizeInfo.event.id) {
        return {
          ...event,
          start: resizeInfo.event.startStr,
          end: resizeInfo.event.endStr
        };
      }
      return event;
    });
    setEvents(updatedEvents);
  };

  // 새 이벤트 추가
  const handleAddEvent = (eventData: Omit<CalendarEvent, 'id'>) => {
    const newEvent: CalendarEvent = {
      ...eventData,
      id: Date.now().toString(),
      title: `${eventData.employee_name} (${eventData.position})`,
      extendedProps: {
        employee_id: eventData.employee_id,
        employee_name: eventData.employee_name,
        position: eventData.position,
        status: eventData.status
      }
    };
    setEvents(prev => [...prev, newEvent]);
    setShowAddModal(false);
  };

  // 이벤트 수정
  const handleEditEvent = (eventData: CalendarEvent) => {
    setEvents(prev => prev.map(event => 
      event.id === eventData.id ? eventData : event
    ));
    setShowEventModal(false);
    setSelectedEvent(null);
  };

  // 이벤트 삭제
  const handleDeleteEvent = (eventId: string) => {
    setEvents(prev => prev.filter(event => event.id !== eventId));
    setShowEventModal(false);
    setSelectedEvent(null);
  };

  // 캘린더 내보내기
  const handleExportCalendar = () => {
    const calendarApi = calendarRef.current?.getApi();
    if (calendarApi) {
      // 캘린더 데이터를 JSON으로 내보내기
      const calendarData = {
        events: events,
        exportDate: new Date().toISOString()
      };
      
      const dataStr = JSON.stringify(calendarData, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `schedule-calendar-${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">스케줄 캘린더</h1>
              <p className="text-sm text-gray-600">FullCalendar를 활용한 직관적인 스케줄 관리</p>
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
              <button
                onClick={handleExportCalendar}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <Download className="w-4 h-4 mr-2" />
                내보내기
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 뷰 모드 선택 */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-4 py-4">
            {[
              { id: 'dayGridMonth', label: '월간', icon: Calendar },
              { id: 'timeGridWeek', label: '주간', icon: Clock },
              { id: 'timeGridDay', label: '일간', icon: Users }
            ].map((view) => {
              const Icon = view.icon;
              return (
                <button
                  key={view.id}
                  onClick={() => setViewMode(view.id as any)}
                  className={`px-4 py-2 rounded-md text-sm font-medium flex items-center space-x-2 ${
                    viewMode === view.id
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{view.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* 메인 컨텐츠 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 캘린더 */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow">
              <div className="p-6">
                <FullCalendar
                  ref={calendarRef}
                  plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
                  headerToolbar={{
                    left: 'prev,next today',
                    center: 'title',
                    right: ''
                  }}
                  initialView={viewMode}
                  views={{
                    dayGridMonth: {
                      titleFormat: { year: 'numeric', month: 'long' }
                    },
                    timeGridWeek: {
                      titleFormat: { year: 'numeric', month: 'long', day: 'numeric' }
                    },
                    timeGridDay: {
                      titleFormat: { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
                    }
                  }}
                  locale={koLocale}
                  events={events}
                  editable={true}
                  droppable={true}
                  eventClick={handleEventClick}
                  dateClick={handleDateClick}
                  eventDrop={handleEventDrop}
                  eventResize={handleEventResize}
                  height="auto"
                  slotMinTime="06:00:00"
                  slotMaxTime="24:00:00"
                  allDaySlot={false}
                  slotDuration="00:30:00"
                  slotLabelInterval="01:00"
                  eventTimeFormat={{
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: false
                  }}
                  eventDisplay="block"
                  eventColor="#3B82F6"
                  eventTextColor="#ffffff"
                  dayMaxEvents={true}
                  moreLinkClick="popover"
                  businessHours={{
                    daysOfWeek: [1, 2, 3, 4, 5, 6, 0],
                    startTime: '09:00',
                    endTime: '18:00'
                  }}
                />
              </div>
            </div>
          </div>

          {/* 사이드바 */}
          <div className="lg:col-span-1 space-y-6">
            {/* AI 분석 결과 */}
            {aiAnalysis && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-green-500" />
                  AI 분석 결과
                </h3>
                <div className="space-y-4">
                  <div className="text-center">
                    <div 
                      className="w-12 h-12 rounded-full flex items-center justify-center text-xl mx-auto mb-2"
                      style={{ backgroundColor: `${aiAnalysis.visual_indicators.color}20` }}
                    >
                      {aiAnalysis.visual_indicators.icon}
                    </div>
                    <div className="text-2xl font-bold text-gray-900">
                      {aiAnalysis.efficiency_score}점
                    </div>
                    <div className="text-sm text-gray-600">
                      효율성 점수
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-700">
                    {aiAnalysis.summary}
                  </div>

                  {aiAnalysis.issues.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                        <AlertTriangle className="w-4 h-4 mr-1 text-red-500" />
                        문제점
                      </h4>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {aiAnalysis.issues.slice(0, 3).map((issue, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-red-500 mr-1">•</span>
                            {issue}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {aiAnalysis.recommendations.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                        <CheckCircle className="w-4 h-4 mr-1 text-green-500" />
                        개선안
                      </h4>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {aiAnalysis.recommendations.slice(0, 2).map((rec, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-green-500 mr-1">•</span>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* 빠른 통계 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">빠른 통계</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">총 스케줄</span>
                  <span className="text-lg font-semibold text-gray-900">{events.length}개</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">이번 주</span>
                  <span className="text-lg font-semibold text-blue-600">
                    {events.filter(e => {
                      const eventDate = new Date(e.start);
                      const now = new Date();
                      const startOfWeek = new Date(now.setDate(now.getDate() - now.getDay()));
                      const endOfWeek = new Date(startOfWeek);
                      endOfWeek.setDate(startOfWeek.getDate() + 6);
                      return eventDate >= startOfWeek && eventDate <= endOfWeek;
                    }).length}개
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">매니저</span>
                  <span className="text-lg font-semibold text-green-600">
                    {events.filter(e => e.position === '매니저').length}명
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">직원</span>
                  <span className="text-lg font-semibold text-yellow-600">
                    {events.filter(e => e.position === '직원').length}명
                  </span>
                </div>
              </div>
            </div>

            {/* 색상 범례 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">색상 범례</h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="w-4 h-4 bg-blue-500 rounded"></div>
                  <span className="text-sm text-gray-600">매니저</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-4 h-4 bg-green-500 rounded"></div>
                  <span className="text-sm text-gray-600">직원</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-4 h-4 bg-yellow-500 rounded"></div>
                  <span className="text-sm text-gray-600">아르바이트</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-4 h-4 bg-red-500 rounded"></div>
                  <span className="text-sm text-gray-600">결근</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 이벤트 상세 모달 */}
      {showEventModal && selectedEvent && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">스케줄 상세</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">직원명</label>
                  <input
                    type="text"
                    value={selectedEvent.employee_name}
                    onChange={(e) => setSelectedEvent({
                      ...selectedEvent,
                      employee_name: e.target.value,
                      title: `${e.target.value} (${selectedEvent.position})`
                    })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">직책</label>
                  <select
                    value={selectedEvent.position}
                    onChange={(e) => setSelectedEvent({
                      ...selectedEvent,
                      position: e.target.value,
                      title: `${selectedEvent.employee_name} (${e.target.value})`
                    })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="매니저">매니저</option>
                    <option value="직원">직원</option>
                    <option value="아르바이트">아르바이트</option>
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">시작시간</label>
                    <input
                      type="datetime-local"
                      value={selectedEvent.start.replace('Z', '')}
                      onChange={(e) => setSelectedEvent({
                        ...selectedEvent,
                        start: e.target.value
                      })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">종료시간</label>
                    <input
                      type="datetime-local"
                      value={selectedEvent.end.replace('Z', '')}
                      onChange={(e) => setSelectedEvent({
                        ...selectedEvent,
                        end: e.target.value
                      })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">상태</label>
                  <select
                    value={selectedEvent.status}
                    onChange={(e) => setSelectedEvent({
                      ...selectedEvent,
                      status: e.target.value as any
                    })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="scheduled">예정</option>
                    <option value="completed">완료</option>
                    <option value="absent">결근</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => handleDeleteEvent(selectedEvent.id)}
                  className="px-4 py-2 border border-red-300 rounded-md text-sm font-medium text-red-700 hover:bg-red-50"
                >
                  삭제
                </button>
                <button
                  onClick={() => handleEditEvent(selectedEvent)}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                >
                  수정
                </button>
                <button
                  onClick={() => {
                    setShowEventModal(false);
                    setSelectedEvent(null);
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  취소
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 새 이벤트 추가 모달 */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">새 스케줄 추가</h3>
              <form onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                handleAddEvent({
                  title: '',
                  start: formData.get('start') as string,
                  end: formData.get('end') as string,
                  employee_id: parseInt(formData.get('employee_id') as string),
                  employee_name: formData.get('employee_name') as string,
                  position: formData.get('position') as string,
                  status: 'scheduled',
                  extendedProps: {
                    employee_id: parseInt(formData.get('employee_id') as string),
                    employee_name: formData.get('employee_name') as string,
                    position: formData.get('position') as string,
                    status: 'scheduled'
                  }
                });
              }}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">직원명</label>
                    <input
                      type="text"
                      name="employee_name"
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">직책</label>
                    <select
                      name="position"
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      required
                    >
                      <option value="">선택하세요</option>
                      <option value="매니저">매니저</option>
                      <option value="직원">직원</option>
                      <option value="아르바이트">아르바이트</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">시작시간</label>
                      <input
                        type="datetime-local"
                        name="start"
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">종료시간</label>
                      <input
                        type="datetime-local"
                        name="end"
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        required
                      />
                    </div>
                  </div>
                  <input type="hidden" name="employee_id" value={Date.now()} />
                </div>
                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    취소
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                  >
                    추가
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

export default ScheduleCalendar;
