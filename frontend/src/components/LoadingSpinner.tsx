'use client';

import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  text?: string;
  className?: string;
}

export default function LoadingSpinner({ 
  size = 'md', 
  color = 'primary', 
  text,
  className 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  const colorClasses = {
    primary: 'text-cyan-400',
    secondary: 'text-purple-400',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    error: 'text-red-400'
  };

  return (
    <div className={cn('flex flex-col items-center justify-center', className)}>
      <div className={cn(
        'animate-spin rounded-full border-2 border-current border-t-transparent',
        sizeClasses[size],
        colorClasses[color]
      )} />
      {text && (
        <p className="mt-2 text-sm text-slate-400">{text}</p>
      )}
    </div>
  );
} 