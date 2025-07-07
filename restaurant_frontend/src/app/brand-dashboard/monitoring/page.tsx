"use client";
import { useState, useEffect } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  Users,
  ShoppingCart,
  Package,
  Building2,
  TrendingUp,
  TrendingDown,
  Wifi,
  WifiOff,
  Battery,
  BatteryCharging,
  Thermometer,
  Zap,
} from "lucide-react";

interface MonitoringData {
  timestamp: string;
  branches: Array<{
    id: number;
    name: string;
    status: "online" | "offline" | "warning";
    sales: number;
    orders: number;
    employees: number;
    customers: number;
    temperature: number;
    humidity: number;
    power: number;
    internet: boolean;
    alerts: Array<{
      type: "info" | "warning" | "error" | "success";
      message: string;
      time: string;
    }>;
  }>;
  system: {
    uptime: string;
    memory: number;
    cpu: number;
    disk: number;
    activeConnections: number;
  };
}

export default function MonitoringPage() {
  const [monitoringData, setMonitoringData] = useState<MonitoringData | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadMonitoringData();
    
    if (autoRefresh) {
      const interval = setInterval(loadMonitoringData, 30000); // 30초마다 업데이트
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadMonitoringData = async () => {
    // 실제로는 WebSocket 또는 API 호출
    const mockData: MonitoringData = {
      timestamp: new Date().toLocaleString('ko-KR'),
      branches: [
        {
          id: 1,
          name: "강남점",
          status: "online",
          sales: 9200000,
          orders: 175,
          employees: 12,
          customers: 135,
          temperature: 22.5,
          humidity: 65,
          power: 85,
          internet: true,
          alerts: [
            { type: "success", message: "일일 매출 목표 달성", time: "5분 전" },
            { type: "info", message: "새로운 주문 접수", time: "2분 전" },
          ],
        },
        {
          id: 2,
          name: "홍대점",
          status: "online",
          sales: 7800000,
          orders: 142,
          employees: 10,
          customers: 98,
          temperature: 23.1,
          humidity: 62,
          power: 92,
          internet: true,
          alerts: [
            { type: "warning", message: "재고 부족 - 토마토", time: "10분 전" },
            { type: "info", message: "직원 출근", time: "15분 전" },
          ],
        },
        {
          id: 3,
          name: "부산점",
          status: "warning",
          sales: 6800000,
          orders: 98,
          employees: 8,
          customers: 75,
          temperature: 24.8,
          humidity: 70,
          power: 45,
          internet: true,
          alerts: [
            { type: "error", message: "전력 부족 경고", time: "1분 전" },
            { type: "warning", message: "온도 상승", time: "5분 전" },
          ],
        },
        {
          id: 4,
          name: "대구점",
          status: "online",
          sales: 6100000,
          orders: 87,
          employees: 9,
          customers: 65,
          temperature: 21.9,
          humidity: 58,
          power: 78,
          internet: true,
          alerts: [
            { type: "info", message: "정상 운영 중", time: "30분 전" },
          ],
        },
        {
          id: 5,
          name: "인천점",
          status: "offline",
          sales: 0,
          orders: 0,
          employees: 0,
          customers: 0,
          temperature: 0,
          humidity: 0,
          power: 0,
          internet: false,
          alerts: [
            { type: "error", message: "시스템 오프라인", time: "1시간 전" },
            { type: "error", message: "인터넷 연결 끊김", time: "1시간 전" },
          ],
        },
      ],
      system: {
        uptime: "24시간 15분",
        memory: 65,
        cpu: 42,
        disk: 78,
        activeConnections: 156,
      },
    };

    setMonitoringData(mockData);
    setIsLoaded(true);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR').format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
        return "text-green-600 bg-green-100";
      case "warning":
        return "text-yellow-600 bg-yellow-100";
      case "offline":
        return "text-red-600 bg-red-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "online":
        return <CheckCircle className="h-4 w-4" />;
      case "warning":
        return <AlertTriangle className="h-4 w-4" />;
      case "offline":
        return <X className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case "error":
        return <X className="h-4 w-4 text-red-600" />;
      default:
        return <Activity className="h-4 w-4 text-blue-600" />;
    }
  };

  if (!isLoaded || !monitoringData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">모니터링 데이터 로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* 헤더 */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">실시간 모니터링</h1>
            <p className="text-gray-600 mt-2">
              마지막 업데이트: {monitoringData.timestamp}
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded border-gray-300"
              />
              <span className="text-sm text-gray-600">자동 새로고침</span>
            </label>
            <button
              onClick={loadMonitoringData}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
            >
              <Activity className="h-4 w-4" />
              새로고침
            </button>
          </div>
        </div>
      </div>

      {/* 시스템 상태 */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">시스템 상태</h3>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <Clock className="h-6 w-6 text-blue-600" />
            </div>
            <p className="text-sm text-gray-600">가동시간</p>
            <p className="text-lg font-semibold text-gray-900">{monitoringData.system.uptime}</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <Zap className="h-6 w-6 text-yellow-600" />
            </div>
            <p className="text-sm text-gray-600">CPU 사용률</p>
            <p className="text-lg font-semibold text-gray-900">{monitoringData.system.cpu}%</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <Activity className="h-6 w-6 text-purple-600" />
            </div>
            <p className="text-sm text-gray-600">메모리 사용률</p>
            <p className="text-lg font-semibold text-gray-900">{monitoringData.system.memory}%</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <Package className="h-6 w-6 text-green-600" />
            </div>
            <p className="text-sm text-gray-600">디스크 사용률</p>
            <p className="text-lg font-semibold text-gray-900">{monitoringData.system.disk}%</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <Users className="h-6 w-6 text-indigo-600" />
            </div>
            <p className="text-sm text-gray-600">활성 연결</p>
            <p className="text-lg font-semibold text-gray-900">{monitoringData.system.activeConnections}</p>
          </div>
        </div>
      </div>

      {/* 매장별 모니터링 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {monitoringData.branches.map((branch) => (
          <div key={branch.id} className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Building2 className="h-6 w-6 text-gray-400" />
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{branch.name}</h3>
                  <p className="text-sm text-gray-500">매장 #{branch.id}</p>
                </div>
              </div>
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(branch.status)}`}>
                {getStatusIcon(branch.status)}
                <span className="ml-1">
                  {branch.status === "online" && "온라인"}
                  {branch.status === "warning" && "경고"}
                  {branch.status === "offline" && "오프라인"}
                </span>
              </span>
            </div>

            {/* 매장 통계 */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <DollarSign className="h-5 w-5 text-green-600 mx-auto mb-1" />
                <p className="text-sm text-gray-600">매출</p>
                <p className="text-lg font-semibold text-gray-900">
                  {formatCurrency(branch.sales)}원
                </p>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <ShoppingCart className="h-5 w-5 text-blue-600 mx-auto mb-1" />
                <p className="text-sm text-gray-600">주문</p>
                <p className="text-lg font-semibold text-gray-900">
                  {branch.orders}건
                </p>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <Users className="h-5 w-5 text-purple-600 mx-auto mb-1" />
                <p className="text-sm text-gray-600">직원</p>
                <p className="text-lg font-semibold text-gray-900">
                  {branch.employees}명
                </p>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <Activity className="h-5 w-5 text-indigo-600 mx-auto mb-1" />
                <p className="text-sm text-gray-600">고객</p>
                <p className="text-lg font-semibold text-gray-900">
                  {branch.customers}명
                </p>
              </div>
            </div>

            {/* 환경 정보 */}
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="flex items-center space-x-2">
                <Thermometer className="h-4 w-4 text-red-500" />
                <div>
                  <p className="text-xs text-gray-500">온도</p>
                  <p className="text-sm font-medium">{branch.temperature}°C</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Activity className="h-4 w-4 text-blue-500" />
                <div>
                  <p className="text-xs text-gray-500">습도</p>
                  <p className="text-sm font-medium">{branch.humidity}%</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {branch.power > 20 ? (
                  <Battery className="h-4 w-4 text-green-500" />
                ) : (
                  <BatteryCharging className="h-4 w-4 text-yellow-500" />
                )}
                <div>
                  <p className="text-xs text-gray-500">전력</p>
                  <p className="text-sm font-medium">{branch.power}%</p>
                </div>
              </div>
            </div>

            {/* 연결 상태 */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                {branch.internet ? (
                  <Wifi className="h-4 w-4 text-green-500" />
                ) : (
                  <WifiOff className="h-4 w-4 text-red-500" />
                )}
                <span className="text-sm text-gray-600">
                  {branch.internet ? "인터넷 연결됨" : "인터넷 연결 끊김"}
                </span>
              </div>
            </div>

            {/* 알림 */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-900">최근 알림</h4>
              {branch.alerts.slice(0, 3).map((alert, index) => (
                <div key={index} className="flex items-center space-x-2 p-2 bg-gray-50 rounded">
                  {getAlertIcon(alert.type)}
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">{alert.message}</p>
                    <p className="text-xs text-gray-500">{alert.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 