'use client';

import { cn } from '@/lib/utils';

interface ResponsiveContainerProps {
  children: React.ReactNode;
  className?: string;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '4xl' | '7xl' | 'full';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  center?: boolean;
}

export default function ResponsiveContainer({
  children,
  className,
  maxWidth = 'xl',
  padding = 'md',
  center = true
}: ResponsiveContainerProps) {
  const maxWidthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    '4xl': 'max-w-4xl',
    '7xl': 'max-w-7xl',
    full: 'max-w-full'
  };

  const paddingClasses = {
    none: '',
    sm: 'px-2 py-2',
    md: 'px-4 py-4',
    lg: 'px-6 py-6'
  };

  return (
    <div className={cn(
      'w-full',
      maxWidthClasses[maxWidth],
      paddingClasses[padding],
      center && 'mx-auto',
      className
    )}>
      {children}
    </div>
  );
}

// 특정 용도별 컨테이너들
export function DashboardContainer({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <ResponsiveContainer 
      maxWidth="7xl" 
      padding="lg" 
      className={cn('min-h-screen', className)}
    >
      {children}
    </ResponsiveContainer>
  );
}

export function CardContainer({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <ResponsiveContainer 
      maxWidth="4xl" 
      padding="md" 
      className={className}
    >
      {children}
    </ResponsiveContainer>
  );
}

export function FormContainer({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <ResponsiveContainer 
      maxWidth="2xl" 
      padding="lg" 
      className={className}
    >
      {children}
    </ResponsiveContainer>
  );
}

export function ModalContainer({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <ResponsiveContainer 
      maxWidth="lg" 
      padding="md" 
      className={className}
    >
      {children}
    </ResponsiveContainer>
  );
} 