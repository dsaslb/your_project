import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';

interface DashboardLayoutProps {
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  stats: Array<{
    label: string;
    value: string | number;
    icon: React.ReactNode;
    color: string;
  }>;
  actions: Array<{
    label: string;
    onClick: () => void;
    icon: React.ReactNode;
    variant?: 'default' | 'outline' | 'secondary' | 'ghost' | 'link' | 'destructive';
  }>;
  onRefresh?: () => void;
  loading?: boolean;
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  title,
  subtitle,
  icon,
  stats,
  actions,
  onRefresh,
  loading = false,
  children
}) => {
  return (
    <div className="min-h-screen p-8 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* 헤더 */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            {icon}
            {title}
          </h1>
          <p className="text-slate-400 mt-2">{subtitle}</p>
        </div>
        
        <div className="flex gap-2">
          {onRefresh && (
            <Button
              variant="outline"
              onClick={onRefresh}
              disabled={loading}
              className="flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              새로고침
            </Button>
          )}
          
          {actions.map((action, index) => (
            <Button
              key={index}
              variant={action.variant || 'default'}
              onClick={action.onClick}
              className="flex items-center gap-2"
            >
              {action.icon}
              {action.label}
            </Button>
          ))}
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => (
          <Card key={index} className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">{stat.label}</p>
                  <p className="text-2xl font-bold text-white">{stat.value}</p>
                </div>
                <div className={stat.color}>
                  {stat.icon}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 메인 콘텐츠 */}
      <div className="space-y-6">
        {children}
      </div>
    </div>
  );
};

export default DashboardLayout; 