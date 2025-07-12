import React, { useEffect, useRef, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface ChartData {
  sales: number[];
  staff: number[];
  inventory: number[];
  customerSatisfaction: number[];
  labels: string[];
}

const DataVisualization: React.FC = () => {
  const [chartData, setChartData] = useState<ChartData>({
    sales: [12000000, 13500000, 11800000, 14200000, 15600000, 14800000],
    staff: [8, 9, 8, 10, 11, 10],
    inventory: [85, 78, 82, 75, 88, 92],
    customerSatisfaction: [92, 89, 94, 91, 96, 93],
    labels: ['1월', '2월', '3월', '4월', '5월', '6월'],
  });

  const [selectedPeriod, setSelectedPeriod] = useState('6개월');

  // 매출 차트 데이터
  const salesChartData = {
    labels: chartData.labels,
    datasets: [
      {
        label: '월 매출',
        data: chartData.sales,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  // 직원 수 차트 데이터
  const staffChartData = {
    labels: chartData.labels,
    datasets: [
      {
        label: '직원 수',
        data: chartData.staff,
        backgroundColor: 'rgba(34, 197, 94, 0.8)',
        borderColor: 'rgb(34, 197, 94)',
        borderWidth: 2,
      },
    ],
  };

  // 고객 만족도 도넛 차트 데이터
  const satisfactionChartData = {
    labels: ['매우 만족', '만족', '보통', '불만족'],
    datasets: [
      {
        data: [45, 35, 15, 5],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(239, 68, 68, 0.8)',
        ],
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-purple-600 rounded-xl flex items-center justify-center">
            <span className="text-2xl">📊</span>
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">데이터 시각화</h3>
            <p className="text-sm text-gray-500">매출, 직원, 재고, 고객 만족도 분석</p>
          </div>
        </div>
        <select
          value={selectedPeriod}
          onChange={(e) => setSelectedPeriod(e.target.value)}
          className="px-3 py-1 border rounded-lg text-sm bg-white dark:bg-gray-700 dark:border-gray-600"
        >
          <option value="1개월">1개월</option>
          <option value="3개월">3개월</option>
          <option value="6개월">6개월</option>
          <option value="1년">1년</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 매출 추이 차트 */}
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 dark:text-white mb-3">매출 추이</h4>
          <div className="h-64">
            <Line data={salesChartData} options={chartOptions} />
          </div>
        </div>

        {/* 직원 수 변화 차트 */}
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 dark:text-white mb-3">직원 수 변화</h4>
          <div className="h-64">
            <Bar data={staffChartData} options={chartOptions} />
          </div>
        </div>

        {/* 고객 만족도 도넛 차트 */}
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 lg:col-span-2">
          <h4 className="font-medium text-gray-900 dark:text-white mb-3">고객 만족도 분포</h4>
          <div className="h-64 flex items-center justify-center">
            <div className="w-64 h-64">
              <Doughnut data={satisfactionChartData} options={doughnutOptions} />
            </div>
          </div>
        </div>
      </div>

      {/* 요약 통계 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
        <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">
            {Math.max(...chartData.sales).toLocaleString()}
          </div>
          <div className="text-xs text-blue-600">최고 매출 (원)</div>
        </div>
        <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <div className="text-2xl font-bold text-green-600">
            {Math.max(...chartData.staff)}
          </div>
          <div className="text-xs text-green-600">최대 직원 수</div>
        </div>
        <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
          <div className="text-2xl font-bold text-yellow-600">
            {Math.max(...chartData.inventory)}%
          </div>
          <div className="text-xs text-yellow-600">최고 재고 효율성</div>
        </div>
        <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">
            {Math.max(...chartData.customerSatisfaction)}%
          </div>
          <div className="text-xs text-purple-600">최고 고객 만족도</div>
        </div>
      </div>
    </div>
  );
};

export default DataVisualization; 