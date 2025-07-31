'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  RefreshCw, 
  Settings, 
  Bell, 
  Search,
  Zap,
  TrendingUp,
  Users,
  Building2,
  Store
} from 'lucide-react';

interface DashboardLayoutProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  stats?: {
    label: string;
    value: string | number;
    icon?: React.ReactNode;
    color?: string;
  }[];
  actions?: {
    label: string;
    onClick: () => void;
    icon?: React.ReactNode;
    variant?: 'default' | 'outline' | 'ghost';
  }[];
  onRefresh?: () => void;
  loading?: boolean;
}

export default function DashboardLayout({
  title,
  subtitle,
  icon = <Zap className="w-6 h-6" />,
  children,
  stats = [],
  actions = [],
  onRefresh,
  loading = false
}: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* 헤더 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-xl flex items-center justify-center">
              {icon}
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">
                {title}
              </h1>
              {subtitle && (
                <p className="text-slate-400 mt-1">{subtitle}</p>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {onRefresh && (
              <Button
                variant="outline"
                size="sm"
                onClick={onRefresh}
                disabled={loading}
                className="border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                새로고침
              </Button>
            )}
            
            {actions.map((action, index) => (
              <Button
                key={index}
                variant={action.variant || 'default'}
                size="sm"
                onClick={action.onClick}
                className={action.variant === 'outline' ? 'border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10' : ''}
              >
                {action.icon && <span className="mr-2">{action.icon}</span>}
                {action.label}
              </Button>
            ))}
          </div>
        </div>

        {/* 통계 카드 */}
        {stats.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <Card 
                key={index}
                className="group bg-slate-800/50 border-slate-600 backdrop-blur-xl hover:border-cyan-400/50 transition-all duration-300"
              >
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-400 mb-1">{stat.label}</p>
                      <p className={`text-2xl font-bold ${stat.color || 'text-white'}`}>
                        {stat.value}
                      </p>
                    </div>
                    {stat.icon && (
                      <div className="w-12 h-12 bg-gradient-to-br from-cyan-500/20 to-purple-500/20 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                        {stat.icon}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* 메인 콘텐츠 */}
        <div className="space-y-6">
          {children}
        </div>
      </div>
    </div>
  );
}

// 통계 카드 컴포넌트
export function StatCard({ 
  label, 
  value, 
  icon, 
  color = 'text-white',
  trend,
  trendValue
}: {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  color?: string;
  trend?: 'up' | 'down';
  trendValue?: string;
}) {
  return (
    <Card className="group bg-slate-800/50 border-slate-600 backdrop-blur-xl hover:border-cyan-400/50 transition-all duration-300">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-400 mb-1">{label}</p>
            <p className={`text-2xl font-bold ${color}`}>
              {value}
            </p>
            {trend && trendValue && (
              <div className="flex items-center gap-1 mt-1">
                <TrendingUp 
                  className={`w-3 h-3 ${trend === 'up' ? 'text-emerald-400' : 'text-red-400'}`} 
                />
                <span className={`text-xs ${trend === 'up' ? 'text-emerald-400' : 'text-red-400'}`}>
                  {trendValue}
                </span>
              </div>
            )}
          </div>
          {icon && (
            <div className="w-12 h-12 bg-gradient-to-br from-cyan-500/20 to-purple-500/20 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              {icon}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// 검색 및 필터 컴포넌트
export function SearchAndFilter({
  searchTerm,
  onSearchChange,
  placeholder = "검색...",
  filters = [],
  onFilterChange
}: {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  placeholder?: string;
  filters?: { label: string; value: string; options: { label: string; value: string }[] }[];
  onFilterChange?: (filter: string, value: string) => void;
}) {
  return (
    <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
      <CardContent className="p-6">
        <div className="flex items-center gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input
              type="text"
              placeholder={placeholder}
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder:text-slate-400 focus:border-cyan-400/50 focus:outline-none focus:ring-1 focus:ring-cyan-400/20"
            />
          </div>
          
          {filters.map((filter, index) => (
            <select
              key={index}
              onChange={(e) => onFilterChange?.(filter.value, e.target.value)}
              className="px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:border-cyan-400/50 focus:outline-none"
            >
              <option value="">{filter.label}</option>
              {filter.options.map((option, optionIndex) => (
                <option key={optionIndex} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          ))}
        </div>
      </CardContent>
    </Card>
  );
} 