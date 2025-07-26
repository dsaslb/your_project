'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts';

interface PluginUISchema {
  menu?: {
    title: string;
    icon: string;
    position: number;
    parent?: string;
  };
  dashboard?: {
    type: 'card' | 'chart' | 'gauge' | 'list' | 'table';
    title: string;
    description: string;
    component: string;
    size: 'small' | 'medium' | 'large';
  };
  settings?: Record<string, any>;
}

interface PluginRendererProps {
  plugin: {
    id: number;
    name: string;
    display_name: string;
    ui_schema: PluginUISchema;
    [key: string]: any;
  };
  data?: any;
}

// 더미 데이터 생성 함수들
const generateChartData = (type: string) => {
  if (type === 'bar') {
    return [
      { name: '1월', value: 400 },
      { name: '2월', value: 300 },
      { name: '3월', value: 600 },
      { name: '4월', value: 800 },
      { name: '5월', value: 500 },
    ];
  } else if (type === 'pie') {
    return [
      { name: '완료', value: 400, color: '#10b981' },
      { name: '진행중', value: 300, color: '#f59e0b' },
      { name: '대기', value: 200, color: '#ef4444' },
    ];
  } else if (type === 'line') {
    return [
      { name: '1월', value: 400 },
      { name: '2월', value: 300 },
      { name: '3월', value: 600 },
      { name: '4월', value: 800 },
      { name: '5월', value: 500 },
    ];
  }
  return [];
};

const generateListData = () => {
  return [
    { id: 1, title: '스케줄 최적화 완료', status: 'success', time: '2시간 전' },
    { id: 2, title: '직원 근무 시간 조정', status: 'pending', time: '4시간 전' },
    { id: 3, title: '매장 인력 배치 개선', status: 'processing', time: '6시간 전' },
  ];
};

const generateTableData = () => {
  return [
    { id: 1, name: '커피 원두', current: 50, recommended: 80, status: 'low' },
    { id: 2, name: '우유', current: 30, recommended: 40, status: 'normal' },
    { id: 3, name: '시럽', current: 20, recommended: 25, status: 'normal' },
    { id: 4, name: '컵', current: 200, recommended: 300, status: 'low' },
  ];
};

// 차트 컴포넌트들
const BarChartComponent = ({ data }: { data: any[] }) => (
  <ResponsiveContainer width="100%" height={200}>
    <BarChart data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="value" fill="#3b82f6" />
    </BarChart>
  </ResponsiveContainer>
);

const PieChartComponent = ({ data }: { data: any[] }) => (
  <ResponsiveContainer width="100%" height={200}>
    <PieChart>
      <Pie
        data={data}
        cx="50%"
        cy="50%"
        outerRadius={80}
        dataKey="value"
        label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
      >
        {data.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={entry.color} />
        ))}
      </Pie>
      <Tooltip />
    </PieChart>
  </ResponsiveContainer>
);

const LineChartComponent = ({ data }: { data: any[] }) => (
  <ResponsiveContainer width="100%" height={200}>
    <LineChart data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} />
    </LineChart>
  </ResponsiveContainer>
);

// 게이지 컴포넌트
const GaugeComponent = ({ value, max = 100 }: { value: number; max?: number }) => {
  const percentage = (value / max) * 100;
  const color = percentage >= 80 ? '#10b981' : percentage >= 60 ? '#f59e0b' : '#ef4444';
  
  return (
    <div className="text-center">
      <div className="relative w-32 h-32 mx-auto mb-4">
        <svg className="w-32 h-32 transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="#e5e7eb"
            strokeWidth="8"
            fill="none"
          />
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke={color}
            strokeWidth="8"
            fill="none"
            strokeDasharray={`${2 * Math.PI * 56}`}
            strokeDashoffset={`${2 * Math.PI * 56 * (1 - percentage / 100)}`}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold">{value}</span>
        </div>
      </div>
      <p className="text-sm text-gray-600">점수</p>
    </div>
  );
};

// 리스트 컴포넌트
const ListComponent = ({ data }: { data: any[] }) => (
  <div className="space-y-2">
    {data.map((item) => (
      <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
        <div>
          <p className="font-medium">{item.title}</p>
          <p className="text-sm text-gray-500">{item.time}</p>
        </div>
        <Badge 
          variant={
            item.status === 'success' ? 'default' : 
            item.status === 'pending' ? 'secondary' : 'destructive'
          }
        >
          {item.status === 'success' ? '완료' : 
           item.status === 'pending' ? '대기' : '진행중'}
        </Badge>
      </div>
    ))}
  </div>
);

// 테이블 컴포넌트
const TableComponent = ({ data }: { data: any[] }) => (
  <div className="overflow-x-auto">
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b">
          <th className="text-left p-2">상품명</th>
          <th className="text-left p-2">현재 재고</th>
          <th className="text-left p-2">권장 재고</th>
          <th className="text-left p-2">상태</th>
        </tr>
      </thead>
      <tbody>
        {data.map((item) => (
          <tr key={item.id} className="border-b">
            <td className="p-2">{item.name}</td>
            <td className="p-2">{item.current}</td>
            <td className="p-2">{item.recommended}</td>
            <td className="p-2">
              <Badge variant={item.status === 'low' ? 'destructive' : 'secondary'}>
                {item.status === 'low' ? '부족' : '정상'}
              </Badge>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export default function PluginRenderer({ plugin, data }: PluginRendererProps) {
  const { ui_schema } = plugin;
  const dashboard = ui_schema.dashboard;

  if (!dashboard) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{plugin.display_name}</CardTitle>
          <CardDescription>대시보드 구성이 없습니다.</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const renderContent = () => {
    switch (dashboard.type) {
      case 'card':
        return (
          <div className="text-center p-6">
            <div className="text-4xl font-bold text-blue-600 mb-2">85%</div>
            <p className="text-gray-600">최적화 완료율</p>
            <div className="mt-4">
              <Progress value={85} className="w-full" />
            </div>
          </div>
        );

      case 'chart':
        const chartData = generateChartData('bar');
        return <BarChartComponent data={chartData} />;

      case 'gauge':
        return <GaugeComponent value={78} />;

      case 'list':
        const listData = generateListData();
        return <ListComponent data={listData} />;

      case 'table':
        const tableData = generateTableData();
        return <TableComponent data={tableData} />;

      default:
        return <div>지원하지 않는 컴포넌트 타입입니다.</div>;
    }
  };

  const getSizeClass = () => {
    switch (dashboard.size) {
      case 'small':
        return 'col-span-1';
      case 'medium':
        return 'col-span-1 md:col-span-2';
      case 'large':
        return 'col-span-1 md:col-span-2 lg:col-span-3';
      default:
        return 'col-span-1';
    }
  };

  return (
    <Card className={getSizeClass()}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">{dashboard.title}</CardTitle>
            <CardDescription>{dashboard.description}</CardDescription>
          </div>
          <div className="p-2 bg-gray-100 rounded-lg">
            <i className={`${ui_schema.menu?.icon || 'fas fa-puzzle-piece'} text-lg`}></i>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {renderContent()}
      </CardContent>
    </Card>
  );
} 