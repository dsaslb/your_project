'use client';

import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Menu, X, ChevronDown, ChevronUp, Home, Settings, User } from 'lucide-react';
import { Button } from '@/components/ui/button';

// 모바일 하단 네비게이션
export const MobileBottomNavigation = () => {
  const [activeTab, setActiveTab] = useState('home');

  const tabs = [
    { id: 'home', label: '홈', icon: Home },
    { id: 'dashboard', label: '대시보드', icon: Home },
    { id: 'profile', label: '프로필', icon: User },
    { id: 'settings', label: '설정', icon: Settings },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-black/95 backdrop-blur-xl border-t border-cyan-500/20 md:hidden z-50">
      <div className="flex items-center justify-around p-2">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={cn(
              "flex flex-col items-center space-y-1 p-2 rounded-lg transition-all duration-200",
              activeTab === id
                ? "text-cyan-400 bg-cyan-500/20"
                : "text-slate-400 hover:text-white"
            )}
          >
            <Icon className="w-5 h-5" />
            <span className="text-xs">{label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

// 모바일 스와이프 가능한 카드
export const SwipeableCard = ({ 
  children, 
  onSwipeLeft, 
  onSwipeRight,
  className 
}: {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  className?: string;
}) => {
  const [startX, setStartX] = useState(0);
  const [currentX, setCurrentX] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  const handleTouchStart = (e: React.TouchEvent) => {
    setStartX(e.touches[0].clientX);
    setIsDragging(true);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging) return;
    setCurrentX(e.touches[0].clientX);
  };

  const handleTouchEnd = () => {
    if (!isDragging) return;
    
    const diff = startX - currentX;
    const threshold = 50;

    if (Math.abs(diff) > threshold) {
      if (diff > 0 && onSwipeLeft) {
        onSwipeLeft();
      } else if (diff < 0 && onSwipeRight) {
        onSwipeRight();
      }
    }

    setIsDragging(false);
    setCurrentX(0);
  };

  return (
    <div
      className={cn(
        "touch-pan-y select-none",
        className
      )}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      style={{
        transform: isDragging ? `translateX(${currentX - startX}px)` : 'none',
        transition: isDragging ? 'none' : 'transform 0.2s ease-out',
      }}
    >
      {children}
    </div>
  );
};

// 모바일 최적화된 데이터 테이블
export const MobileDataTable = ({ 
  data, 
  columns,
  title 
}: {
  data: any[];
  columns: { key: string; title: string; render?: (value: any, row: any) => React.ReactNode }[];
  title?: string;
}) => {
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());

  const toggleRow = (index: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedRows(newExpanded);
  };

  return (
    <div className="space-y-2">
      {title && (
        <h3 className="text-lg font-semibold text-white px-4">{title}</h3>
      )}
      
      {data.map((row, index) => (
        <SwipeableCard
          key={index}
          className="bg-black/30 backdrop-blur-sm border border-cyan-500/20 rounded-lg mx-4"
          onSwipeLeft={() => console.log('Swipe left on row', index)}
          onSwipeRight={() => console.log('Swipe right on row', index)}
        >
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                {columns.slice(0, 2).map(col => (
                  <div key={col.key} className="mb-1">
                    <span className="text-xs text-slate-400">{col.title}: </span>
                    <span className="text-sm text-white">
                      {col.render ? col.render(row[col.key], row) : row[col.key]}
                    </span>
                  </div>
                ))}
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => toggleRow(index)}
                className="text-slate-400"
              >
                {expandedRows.has(index) ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </Button>
            </div>
            
            {expandedRows.has(index) && (
              <div className="mt-3 pt-3 border-t border-cyan-500/20">
                {columns.slice(2).map(col => (
                  <div key={col.key} className="mb-2">
                    <span className="text-xs text-slate-400">{col.title}: </span>
                    <span className="text-sm text-white">
                      {col.render ? col.render(row[col.key], row) : row[col.key]}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </SwipeableCard>
      ))}
    </div>
  );
};

// 모바일 최적화된 차트
export const MobileChart = ({ 
  title, 
  data, 
  color = '#06b6d4' 
}: {
  title: string;
  data: { value: number; label: string }[];
  color?: string;
}) => {
  const maxValue = Math.max(...data.map(d => d.value));

  return (
    <div className="p-4 bg-black/30 backdrop-blur-sm border border-cyan-500/20 rounded-lg mx-4">
      <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
      
      <div className="space-y-3">
        {data.map((item, index) => (
          <div key={index} className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-300">{item.label}</span>
              <span className="text-sm font-mono text-white">{item.value}</span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2">
              <div
                className="h-2 rounded-full transition-all duration-300"
                style={{
                  width: `${(item.value / maxValue) * 100}%`,
                  backgroundColor: color,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// 모바일 터치 최적화된 버튼
export const TouchButton = ({ 
  children, 
  onClick, 
  variant = 'default',
  size = 'default',
  className 
}: {
  children: React.ReactNode;
  onClick: () => void;
  variant?: 'default' | 'ghost' | 'outline';
  size?: 'sm' | 'default' | 'lg';
  className?: string;
}) => {
  return (
    <button
      onClick={onClick}
      className={cn(
        "touch-manipulation active:scale-95 transition-transform duration-100",
        "min-h-[44px] min-w-[44px]", // 터치 최적화를 위한 최소 크기
        variant === 'default' && "bg-cyan-500 text-white px-4 py-2 rounded-lg",
        variant === 'ghost' && "text-slate-400 hover:text-white px-4 py-2 rounded-lg",
        variant === 'outline' && "border border-cyan-500/30 text-cyan-400 px-4 py-2 rounded-lg",
        size === 'sm' && "text-sm px-3 py-1",
        size === 'lg' && "text-lg px-6 py-3",
        className
      )}
    >
      {children}
    </button>
  );
};

// 모바일 터치 피드백 훅
export const useTouchFeedback = () => {
  const [isPressed, setIsPressed] = useState(false);

  const touchProps = {
    onTouchStart: () => setIsPressed(true),
    onTouchEnd: () => setIsPressed(false),
    onTouchCancel: () => setIsPressed(false),
  };

  return { isPressed, touchProps };
}; 