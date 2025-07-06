"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  Search,
  Settings,
  Menu,
  Clock,
  MapPin,
  Users,
  Calendar,
  Pause,
  Sparkles,
  X,
  User,
  Phone,
  Mail,
} from "lucide-react";

export default function SchedulePage() {
  const router = useRouter();
  const [isLoaded, setIsLoaded] = useState(false);
  const [showAIPopup, setShowAIPopup] = useState(false);
  const [typedText, setTypedText] = useState("");
  const [isPlaying, setIsPlaying] = useState(false);
  const [staffMembers, setStaffMembers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setIsLoaded(true);
    fetchStaffData();
    const popupTimer = setTimeout(() => {
      setShowAIPopup(true);
    }, 3000);
    return () => clearTimeout(popupTimer);
  }, []);

  // 직원 데이터 변경 이벤트 리스너
  useEffect(() => {
    const handleStaffDataUpdate = () => {
      console.log('스케줄: 직원 데이터 업데이트 감지');
      fetchStaffData();
    };

    window.addEventListener('staffDataUpdated', handleStaffDataUpdate);
    return () => window.removeEventListener('staffDataUpdated', handleStaffDataUpdate);
  }, []);

  // 직원 데이터 불러오기
  const fetchStaffData = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/staff', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setStaffMembers(data.staff || []);
        } else {
          console.error('직원 데이터 로드 실패:', data.error);
        }
      } else {
        console.error('직원 데이터 로드 실패:', response.status);
      }
    } catch (error) {
      console.error('직원 데이터 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (showAIPopup) {
      const text = "이번 주 직원 스케줄이 완료되었습니다. 추가 근무 신청이 3건 있습니다.";
      let i = 0;
      const typingInterval = setInterval(() => {
        if (i < text.length) {
          setTypedText((prev) => prev + text.charAt(i));
          i++;
        } else {
          clearInterval(typingInterval);
        }
      }, 50);
      return () => clearInterval(typingInterval);
    }
  }, [showAIPopup]);

  const [currentView, setCurrentView] = useState<"daily" | "weekly" | "monthly">("weekly");
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedEvent, setSelectedEvent] = useState<any>(null);

  const handleEventClick = (event: any) => {
    setSelectedEvent(event);
  };

  // 매장 직원 스케줄 데이터
  const events = [
    {
      id: 1,
      title: "김철수 (주방)",
      startTime: "09:00",
      endTime: "17:00",
      color: "bg-blue-500",
      day: 1,
      date: "2025-03-03",
      description: "주방 근무",
      location: "주방",
      attendees: ["김철수"],
      organizer: "매니저",
      position: "주방장",
      phone: "010-1234-5678",
    },
    {
      id: 2,
      title: "이영희 (서빙)",
      startTime: "10:00",
      endTime: "18:00",
      color: "bg-green-500",
      day: 1,
      date: "2025-03-03",
      description: "서빙 근무",
      location: "홀",
      attendees: ["이영희"],
      organizer: "매니저",
      position: "서빙",
      phone: "010-2345-6789",
    },
    {
      id: 3,
      title: "박민수 (카운터)",
      startTime: "11:00",
      endTime: "19:00",
      color: "bg-purple-500",
      day: 2,
      date: "2025-03-04",
      description: "카운터 근무",
      location: "카운터",
      attendees: ["박민수"],
      organizer: "매니저",
      position: "카운터",
      phone: "010-3456-7890",
    },
    {
      id: 4,
      title: "최지영 (서빙)",
      startTime: "12:00",
      endTime: "20:00",
      color: "bg-yellow-500",
      day: 2,
      date: "2025-03-04",
      description: "서빙 근무",
      location: "홀",
      attendees: ["최지영"],
      organizer: "매니저",
      position: "서빙",
      phone: "010-4567-8901",
    },
    {
      id: 5,
      title: "정현우 (주방)",
      startTime: "13:00",
      endTime: "21:00",
      color: "bg-indigo-500",
      day: 3,
      date: "2025-03-05",
      description: "주방 근무",
      location: "주방",
      attendees: ["정현우"],
      organizer: "매니저",
      position: "부주방장",
      phone: "010-5678-9012",
    },
    {
      id: 6,
      title: "한소영 (서빙)",
      startTime: "14:00",
      endTime: "22:00",
      color: "bg-pink-500",
      day: 3,
      date: "2025-03-05",
      description: "서빙 근무",
      location: "홀",
      attendees: ["한소영"],
      organizer: "매니저",
      position: "서빙",
      phone: "010-6789-0123",
    },
    {
      id: 7,
      title: "강동현 (카운터)",
      startTime: "15:00",
      endTime: "23:00",
      color: "bg-teal-500",
      day: 4,
      date: "2025-03-06",
      description: "카운터 근무",
      location: "카운터",
      attendees: ["강동현"],
      organizer: "매니저",
      position: "카운터",
      phone: "010-7890-1234",
    },
    {
      id: 8,
      title: "윤미영 (서빙)",
      startTime: "16:00",
      endTime: "24:00",
      color: "bg-cyan-500",
      day: 4,
      date: "2025-03-06",
      description: "서빙 근무",
      location: "홀",
      attendees: ["윤미영"],
      organizer: "매니저",
      position: "서빙",
      phone: "010-8901-2345",
    },
    {
      id: 9,
      title: "임태호 (주방)",
      startTime: "08:30",
      endTime: "16:30",
      color: "bg-blue-400",
      day: 5,
      date: "2025-03-07",
      description: "주방 근무",
      location: "주방",
      attendees: ["임태호"],
      organizer: "매니저",
      position: "주방보조",
      phone: "010-9012-3456",
    },
    {
      id: 10,
      title: "송은지 (서빙)",
      startTime: "09:30",
      endTime: "17:30",
      color: "bg-purple-400",
      day: 5,
      date: "2025-03-07",
      description: "서빙 근무",
      location: "홀",
      attendees: ["송은지"],
      organizer: "매니저",
      position: "서빙",
      phone: "010-0123-4567",
    },
    {
      id: 11,
      title: "조성민 (카운터)",
      startTime: "10:30",
      endTime: "18:30",
      color: "bg-red-400",
      day: 6,
      date: "2025-03-08",
      description: "카운터 근무",
      location: "카운터",
      attendees: ["조성민"],
      organizer: "매니저",
      position: "카운터",
      phone: "010-1234-5678",
    },
    {
      id: 12,
      title: "김수진 (서빙)",
      startTime: "11:30",
      endTime: "19:30",
      color: "bg-green-400",
      day: 6,
      date: "2025-03-08",
      description: "서빙 근무",
      location: "홀",
      attendees: ["김수진"],
      organizer: "매니저",
      position: "서빙",
      phone: "010-2345-6789",
    },
  ];

  const calculateEventStyle = (startTime: string, endTime: string) => {
    const start = parseInt(startTime.split(":")[0]);
    const end = parseInt(endTime.split(":")[0]);
    const duration = end - start;
    const top = (start - 8) * 60;
    const height = duration * 60;
    return {
      top: `${top}px`,
      height: `${height}px`,
    };
  };

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  const days = ["월", "화", "수", "목", "금", "토", "일"];

  const getCurrentViewTitle = () => {
    const options = { year: 'numeric', month: 'long' } as const;
    const monthYear = currentDate.toLocaleDateString('ko-KR', options);
    
    switch (currentView) {
      case "daily":
        return `${currentDate.getDate()}일 ${monthYear}`;
      case "weekly":
        const weekStart = new Date(currentDate);
        weekStart.setDate(currentDate.getDate() - currentDate.getDay() + 1);
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekStart.getDate() + 6);
        return `${weekStart.getDate()}일 - ${weekEnd.getDate()}일 ${monthYear}`;
      case "monthly":
        return monthYear;
      default:
        return monthYear;
    }
  };

  const renderDailyView = () => (
    <div className="space-y-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold mb-4">일간 스케줄</h3>
        <div className="space-y-4">
          {events
            .filter(event => {
              const eventDate = new Date(event.date);
              return eventDate.toDateString() === currentDate.toDateString();
            })
            .map(event => (
              <div key={event.id} className="flex items-center space-x-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className={`w-4 h-4 rounded-full ${event.color}`}></div>
                <div className="flex-1">
                  <h4 className="font-medium">{event.title}</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {event.startTime} - {event.endTime} • {event.location}
                  </p>
                </div>
                <button
                  onClick={() => handleEventClick(event)}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  상세보기
                </button>
              </div>
            ))}
        </div>
      </div>
    </div>
  );

  const renderWeeklyView = () => (
    <div className="space-y-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold mb-4">주간 스케줄</h3>
        <div className="grid grid-cols-7 gap-4">
          {days.map((day, dayIndex) => (
            <div key={day} className="space-y-2">
              <div className="text-center font-medium text-sm text-gray-600 dark:text-gray-400">
                {day}
              </div>
              <div className="space-y-1">
                {events
                  .filter(event => event.day === dayIndex + 1)
                  .map(event => (
                    <div
                      key={event.id}
                      onClick={() => handleEventClick(event)}
                      className={`p-2 rounded text-xs text-white cursor-pointer ${event.color}`}
                    >
                      <div className="font-medium truncate">{event.title}</div>
                      <div className="text-xs opacity-90">
                        {event.startTime} - {event.endTime}
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderMonthlyView = () => (
    <div className="space-y-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold mb-4">월간 스케줄</h3>
        <div className="grid grid-cols-7 gap-1">
          {days.map(day => (
            <div key={day} className="text-center font-medium text-sm text-gray-600 dark:text-gray-400 p-2">
              {day}
            </div>
          ))}
          {Array.from({ length: 35 }, (_, i) => {
            const dayEvents = events.filter(event => {
              const eventDate = new Date(event.date);
              return eventDate.getDate() === i + 1;
            });
            return (
              <div key={i} className="min-h-[80px] p-1 border border-gray-200 dark:border-gray-600">
                <div className="text-xs text-gray-500 mb-1">{i + 1}</div>
                <div className="space-y-1">
                  {dayEvents.slice(0, 2).map(event => (
                    <div
                      key={event.id}
                      onClick={() => handleEventClick(event)}
                      className={`p-1 rounded text-xs text-white cursor-pointer ${event.color}`}
                    >
                      <div className="truncate">{event.title}</div>
                    </div>
                  ))}
                  {dayEvents.length > 2 && (
                    <div className="text-xs text-gray-500 text-center">
                      +{dayEvents.length - 2}개 더
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">스케줄 관리</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            직원 스케줄을 일간, 주간, 월간으로 확인하고 관리하세요.
          </p>
        </div>

        {/* Controls */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="flex flex-col sm:flex-row gap-4 flex-1">
              {/* View Toggle */}
              <div className="flex bg-gray-200 dark:bg-gray-700 rounded-lg p-1">
                <button
                  onClick={() => setCurrentView("daily")}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === "daily"
                      ? "bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm"
                      : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                  }`}
                >
                  일간
                </button>
                <button
                  onClick={() => setCurrentView("weekly")}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === "weekly"
                      ? "bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm"
                      : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                  }`}
                >
                  주간
                </button>
                <button
                  onClick={() => setCurrentView("monthly")}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === "monthly"
                      ? "bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm"
                      : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                  }`}
                >
                  월간
                </button>
              </div>

              {/* Date Navigation */}
              <div className="flex items-center gap-4">
                <button
                  onClick={() => {
                    const newDate = new Date(currentDate);
                    if (currentView === "daily") {
                      newDate.setDate(currentDate.getDate() - 1);
                    } else if (currentView === "weekly") {
                      newDate.setDate(currentDate.getDate() - 7);
                    } else if (currentView === "monthly") {
                      newDate.setMonth(currentDate.getMonth() - 1);
                    }
                    setCurrentDate(newDate);
                  }}
                  className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  <ChevronLeft className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                </button>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {getCurrentViewTitle()}
                </span>
                <button
                  onClick={() => {
                    const newDate = new Date(currentDate);
                    if (currentView === "daily") {
                      newDate.setDate(currentDate.getDate() + 1);
                    } else if (currentView === "weekly") {
                      newDate.setDate(currentDate.getDate() + 7);
                    } else if (currentView === "monthly") {
                      newDate.setMonth(currentDate.getMonth() + 1);
                    }
                    setCurrentDate(newDate);
                  }}
                  className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  <ChevronRight className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                </button>
              </div>
            </div>

            {/* Add Button */}
            <button
              onClick={() => router.push('/schedule/add')}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              스케줄 추가
            </button>
          </div>
        </div>

        {/* Schedule Content */}
        {currentView === "daily" && renderDailyView()}
        {currentView === "weekly" && renderWeeklyView()}
        {currentView === "monthly" && renderMonthlyView()}

        {/* Stats */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">오늘 근무</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {events.filter(e => new Date(e.date).toDateString() === currentDate.toDateString()).length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <Clock className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">총 근무시간</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">72시간</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
                <Calendar className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">휴가 신청</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">3건</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 dark:bg-red-900/20 rounded-lg">
                <X className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">미배정</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">2명</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Popup */}
      {showAIPopup && (
        <div className="fixed bottom-6 right-6 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <Sparkles className="h-4 w-4 text-white" />
            </div>
            <div className="flex-1">
              <p className="text-sm text-gray-900 dark:text-white mb-2">{typedText}</p>
              <div className="flex gap-2">
                <button className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors">
                  확인
                </button>
                <button
                  onClick={() => setShowAIPopup(false)}
                  className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-3 py-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                >
                  닫기
                </button>
              </div>
            </div>
            <button
              onClick={() => setShowAIPopup(false)}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Event Detail Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-96 max-w-[90vw]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {selectedEvent.title}
              </h3>
              <button
                onClick={() => setSelectedEvent(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <Clock className="h-4 w-4" />
                <span>
                  {selectedEvent.startTime} - {selectedEvent.endTime}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <MapPin className="h-4 w-4" />
                <span>{selectedEvent.location}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <User className="h-4 w-4" />
                <span>{selectedEvent.position}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <Phone className="h-4 w-4" />
                <span>{selectedEvent.phone}</span>
              </div>
              <p className="text-sm text-gray-700 dark:text-gray-300 mt-3">
                {selectedEvent.description}
              </p>
            </div>
            <div className="flex gap-2 mt-6">
              <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                수정
              </button>
              <button className="flex-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 py-2 px-4 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
                삭제
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 