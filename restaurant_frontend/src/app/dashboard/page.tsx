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
  TrendingUp,
  DollarSign,
  ShoppingCart,
  AlertTriangle,
  Sun,
  Cloud,
  CloudRain,
  CloudSnow,
  Wind,
  ClipboardList,
  Package,
  Bell,
} from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const [isLoaded, setIsLoaded] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [weather, setWeather] = useState({
    temperature: 22,
    condition: "맑음",
    humidity: 65,
    windSpeed: 3.2,
    icon: "sun"
  });

  useEffect(() => {
    setIsLoaded(true);
    
    // 실시간 시간 업데이트
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    // 날씨 정보 시뮬레이션 (실제로는 API 호출)
    const weatherInterval = setInterval(() => {
      const conditions = ["맑음", "흐림", "비", "눈"];
      const icons = ["sun", "cloud", "cloud-rain", "cloud-snow"];
      const randomIndex = Math.floor(Math.random() * 4);
      
      setWeather({
        temperature: Math.floor(Math.random() * 15) + 15, // 15-30도
        condition: conditions[randomIndex],
        humidity: Math.floor(Math.random() * 30) + 50, // 50-80%
        windSpeed: Math.random() * 5 + 1, // 1-6 m/s
        icon: icons[randomIndex]
      });
    }, 30000); // 30초마다 업데이트

    return () => {
      clearInterval(timeInterval);
      clearInterval(weatherInterval);
    };
  }, []);

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  const getWeatherIcon = (icon: string) => {
    switch (icon) {
      case "sun":
        return <Sun className="h-6 w-6 text-yellow-500" />;
      case "cloud":
        return <Cloud className="h-6 w-6 text-gray-500" />;
      case "cloud-rain":
        return <CloudRain className="h-6 w-6 text-blue-500" />;
      case "cloud-snow":
        return <CloudSnow className="h-6 w-6 text-blue-300" />;
      default:
        return <Sun className="h-6 w-6 text-yellow-500" />;
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    });
  };

  // 매장에서 해야 할 일 데이터
  const tasks = [
    {
      id: 1,
      title: "스케줄 관리",
      description: "직원 근무 스케줄 확인 및 조정",
      icon: <Calendar className="h-5 w-5" />,
      color: "bg-blue-600 hover:bg-blue-700",
      route: "/schedule",
      priority: "high"
    },
    {
      id: 2,
      title: "주문 확인",
      description: "새로운 주문 확인 및 처리",
      icon: <ShoppingCart className="h-5 w-5" />,
      color: "bg-green-600 hover:bg-green-700",
      route: "/orders",
      priority: "high"
    },
    {
      id: 3,
      title: "재고 점검",
      description: "재고 현황 확인 및 발주",
      icon: <Package className="h-5 w-5" />,
      color: "bg-yellow-600 hover:bg-yellow-700",
      route: "/inventory",
      priority: "medium"
    },
    {
      id: 4,
      title: "직원 관리",
      description: "직원 정보 및 근무 상태 관리",
      icon: <Users className="h-5 w-5" />,
      color: "bg-purple-600 hover:bg-purple-700",
      route: "/staff",
      priority: "medium"
    },
    {
      id: 5,
      title: "공지사항",
      description: "매장 공지사항 작성 및 관리",
      icon: <Bell className="h-5 w-5" />,
      color: "bg-red-600 hover:bg-red-700",
      route: "/notice",
      priority: "low"
    },
    {
      id: 6,
      title: "설정 관리",
      description: "매장 설정 및 시스템 관리",
      icon: <Settings className="h-5 w-5" />,
      color: "bg-gray-600 hover:bg-gray-700",
      route: "/settings",
      priority: "low"
    }
  ];

  const handleTaskClick = (route: string) => {
    router.push(route);
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
      position: "서버",
      phone: "010-2345-6789",
    },
    {
      id: 3,
      title: "박민수 (관리)",
      startTime: "08:00",
      endTime: "16:00",
      color: "bg-purple-500",
      day: 1,
      date: "2025-03-03",
      description: "매장 관리",
      location: "사무실",
      attendees: ["박민수"],
      organizer: "매니저",
      position: "매니저",
      phone: "010-3456-7890",
    },
  ];

  // 주문 현황 데이터
  const orders = [
    {
      id: 1,
      customerName: "김고객",
      items: ["불고기 정식", "김치찌개"],
      total: 25000,
      status: "pending",
      time: "14:30",
    },
    {
      id: 2,
      customerName: "이고객",
      items: ["제육볶음", "된장찌개"],
      total: 22000,
      status: "preparing",
      time: "14:25",
    },
    {
      id: 3,
      customerName: "박고객",
      items: ["순두부찌개", "공기밥"],
      total: 18000,
      status: "ready",
      time: "14:20",
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "preparing":
        return "bg-blue-100 text-blue-800";
      case "ready":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "pending":
        return "대기중";
      case "preparing":
        return "조리중";
      case "ready":
        return "완료";
      default:
        return "알 수 없음";
    }
  };

  const calculateEventStyle = (startTime: string, endTime: string) => {
    const start = parseInt(startTime.split(":")[0]);
    const end = parseInt(endTime.split(":")[0]);
    const duration = end - start;
    
    return {
      height: `${duration * 60}px`,
      top: `${(start - 8) * 60}px`,
    };
  };

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* 헤더 */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">매장 대시보드</h1>
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <Clock className="h-4 w-4" />
                <span>{formatTime(currentTime)}</span>
                <span>•</span>
                <span>{formatDate(currentTime)}</span>
              </div>
            </div>
            
            {/* 날씨 정보 */}
            <div className="flex items-center space-x-3 bg-gray-100 rounded-lg px-3 py-2">
              {getWeatherIcon(weather.icon)}
              <div className="text-sm">
                <div className="font-medium">{weather.temperature}°C</div>
                <div className="text-gray-500">{weather.condition}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 왼쪽 컬럼 */}
          <div className="lg:col-span-2 space-y-8">
            {/* 매장에서 해야 할 일 */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">매장에서 해야 할 일</h2>
                <div className="flex items-center space-x-2">
                  <Sparkles className="h-5 w-5 text-yellow-500" />
                  <span className="text-sm text-gray-500">빠른 작업</span>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {tasks.map((task) => (
                  <button
                    key={task.id}
                    onClick={() => handleTaskClick(task.route)}
                    className={`${task.color} text-white rounded-lg p-4 text-left transition-all duration-200 transform hover:scale-105 hover:shadow-lg`}
                  >
                    <div className="flex items-center space-x-3">
                      {task.icon}
                      <div>
                        <h3 className="font-semibold">{task.title}</h3>
                        <p className="text-sm opacity-90">{task.description}</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* 오늘의 스케줄 */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">오늘의 스케줄</h2>
              
              <div className="space-y-4">
                {events.map((event) => (
                  <div key={event.id} className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
                    <div className={`w-3 h-3 ${event.color} rounded-full`}></div>
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{event.title}</h3>
                      <p className="text-sm text-gray-500">
                        {event.startTime} - {event.endTime} • {event.location}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">{event.position}</p>
                      <p className="text-xs text-gray-500">{event.phone}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 주문 현황 */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">주문 현황</h2>
              
              <div className="space-y-4">
                {orders.map((order) => (
                  <div key={order.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{order.customerName}</h3>
                      <p className="text-sm text-gray-500">{order.items.join(", ")}</p>
                      <p className="text-xs text-gray-400">{order.time}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-gray-900">{order.total.toLocaleString()}원</p>
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>
                        {getStatusText(order.status)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 오른쪽 컬럼 */}
          <div className="space-y-8">
            {/* 통계 카드 */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">오늘의 통계</h2>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Users className="h-6 w-6 text-blue-600" />
                    <div>
                      <p className="text-sm text-gray-600">출근 직원</p>
                      <p className="text-2xl font-bold text-blue-600">8명</p>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <ShoppingCart className="h-6 w-6 text-green-600" />
                    <div>
                      <p className="text-sm text-gray-600">총 주문</p>
                      <p className="text-2xl font-bold text-green-600">24건</p>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <DollarSign className="h-6 w-6 text-yellow-600" />
                    <div>
                      <p className="text-sm text-gray-600">매출</p>
                      <p className="text-2xl font-bold text-yellow-600">₩450,000</p>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <TrendingUp className="h-6 w-6 text-purple-600" />
                    <div>
                      <p className="text-sm text-gray-600">평균 주문</p>
                      <p className="text-2xl font-bold text-purple-600">₩18,750</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 알림 */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">알림</h2>
              
              <div className="space-y-4">
                <div className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg">
                  <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-red-900">재고 부족</p>
                    <p className="text-xs text-red-700">김치, 된장이 부족합니다.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg">
                  <Clock className="h-5 w-5 text-yellow-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-yellow-900">근무 시간</p>
                    <p className="text-xs text-yellow-700">이영희 퇴근 시간이 다가옵니다.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                  <Bell className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-blue-900">새 주문</p>
                    <p className="text-xs text-blue-700">새로운 주문이 들어왔습니다.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
