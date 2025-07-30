'use client';

import { useState, useEffect, useRef } from 'react';
import { useSystemStatus } from '@/hooks/useSystemStatus';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';

interface ChartData {
  timestamp: number;
  value: number;
}

interface ChartProps {
  title: string;
  data: ChartData[];
  color: string;
  unit?: string;
  maxValue?: number;
}

export const RealTimeChart = ({ title, data, color, unit = '', maxValue }: ChartProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [chartWidth, setChartWidth] = useState(0);
  const [chartHeight, setChartHeight] = useState(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 캔버스 크기 설정
    const rect = canvas.getBoundingClientRect();
    setChartWidth(rect.width);
    setChartHeight(rect.height);
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    // 차트 그리기
    drawChart(ctx, rect.width, rect.height);
  }, [data, color, maxValue]);

  const drawChart = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    if (data.length < 2) return;

    ctx.clearRect(0, 0, width, height);

    const padding = 20;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    // 데이터 정규화
    const values = data.map(d => d.value);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const range = maxValue - minValue || 1;

    // 경로 그리기
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;

    data.forEach((point, index) => {
      const x = padding + (index / (data.length - 1)) * chartWidth;
      const y = padding + chartHeight - ((point.value - minValue) / range) * chartHeight;

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();

    // 그라데이션 영역 채우기
    const gradient = ctx.createLinearGradient(0, padding, 0, height - padding);
    gradient.addColorStop(0, color + '40');
    gradient.addColorStop(1, color + '10');

    ctx.beginPath();
    ctx.fillStyle = gradient;
    ctx.moveTo(padding, height - padding);

    data.forEach((point, index) => {
      const x = padding + (index / (data.length - 1)) * chartWidth;
      const y = padding + chartHeight - ((point.value - minValue) / range) * chartHeight;
      ctx.lineTo(x, y);
    });

    ctx.lineTo(width - padding, height - padding);
    ctx.closePath();
    ctx.fill();
  };

  const getCurrentValue = () => {
    return data.length > 0 ? data[data.length - 1].value : 0;
  };

  const getChange = () => {
    if (data.length < 2) return 0;
    const current = data[data.length - 1].value;
    const previous = data[data.length - 2].value;
    return ((current - previous) / previous) * 100;
  };

  const change = getChange();

  return (
    <div className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">{title}</h3>
        <div className="flex items-center space-x-2">
          {change > 0 ? (
            <TrendingUp className="w-3 h-3 text-green-400" />
          ) : (
            <TrendingDown className="w-3 h-3 text-red-400" />
          )}
          <span className={cn(
            "text-xs font-mono",
            change > 0 ? "text-green-400" : "text-red-400"
          )}>
            {change > 0 ? '+' : ''}{change.toFixed(1)}%
          </span>
        </div>
      </div>

      <div className="mb-2">
        <span className="text-2xl font-bold text-white">
          {getCurrentValue().toLocaleString()}{unit}
        </span>
      </div>

      <div className="relative">
        <canvas
          ref={canvasRef}
          className="w-full h-32"
          style={{ height: '128px' }}
        />
      </div>
    </div>
  );
};

// 시스템 성능 차트
export const SystemPerformanceChart = () => {
  const { status } = useSystemStatus();
  const [cpuData, setCpuData] = useState<ChartData[]>([]);
  const [memoryData, setMemoryData] = useState<ChartData[]>([]);

  useEffect(() => {
    const now = Date.now();
    
    // CPU 데이터 업데이트
    setCpuData(prev => {
      const newData = [...prev, { timestamp: now, value: status.performance.cpu }];
      return newData.slice(-20); // 최근 20개 데이터만 유지
    });

    // 메모리 데이터 업데이트
    setMemoryData(prev => {
      const newData = [...prev, { timestamp: now, value: status.performance.memory }];
      return newData.slice(-20);
    });
  }, [status.performance]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <RealTimeChart
        title="CPU 사용률"
        data={cpuData}
        color="#06b6d4"
        unit="%"
        maxValue={100}
      />
      <RealTimeChart
        title="메모리 사용률"
        data={memoryData}
        color="#10b981"
        unit="%"
        maxValue={100}
      />
    </div>
  );
};

// 응답시간 차트
export const ResponseTimeChart = () => {
  const { status } = useSystemStatus();
  const [responseTimeData, setResponseTimeData] = useState<ChartData[]>([]);

  useEffect(() => {
    const now = Date.now();
    
    setResponseTimeData(prev => {
      const newData = [...prev, { timestamp: now, value: status.performance.responseTime }];
      return newData.slice(-20);
    });
  }, [status.performance.responseTime]);

  return (
    <RealTimeChart
      title="응답시간"
      data={responseTimeData}
      color="#f59e0b"
      unit="ms"
    />
  );
};

// 사용자 활동 차트
export const UserActivityChart = () => {
  const [userActivityData, setUserActivityData] = useState<ChartData[]>([]);

  useEffect(() => {
    // 사용자 활동 데이터 시뮬레이션
    const generateData = () => {
      const now = Date.now();
      const baseValue = 50 + Math.random() * 30; // 50-80 사이 랜덤 값
      
      setUserActivityData(prev => {
        const newData = [...prev, { timestamp: now, value: baseValue }];
        return newData.slice(-20);
      });
    };

    generateData();
    const interval = setInterval(generateData, 5000); // 5초마다 업데이트

    return () => clearInterval(interval);
  }, []);

  return (
    <RealTimeChart
      title="활성 사용자"
      data={userActivityData}
      color="#8b5cf6"
      unit="명"
    />
  );
}; 