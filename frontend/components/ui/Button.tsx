/**
 * 🎨 Button 컴포넌트
 * 
 * 접근성을 고려한 재사용 가능한 버튼 컴포넌트입니다.
 */

import React, { forwardRef } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

// 버튼 변형 정의
const buttonVariants = cva(
  // 기본 스타일
  [
    'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
    'disabled:pointer-events-none disabled:opacity-50',
    'active:scale-95',
    'min-h-[44px]', // 접근성을 위한 최소 터치 크기
  ],
  {
    variants: {
      variant: {
        default: [
          'bg-primary-500 text-white hover:bg-primary-600',
          'focus-visible:ring-primary-500',
          'dark:bg-primary-600 dark:hover:bg-primary-700',
        ],
        destructive: [
          'bg-error-500 text-white hover:bg-error-600',
          'focus-visible:ring-error-500',
          'dark:bg-error-600 dark:hover:bg-error-700',
        ],
        outline: [
          'border border-gray-300 bg-transparent hover:bg-gray-50',
          'focus-visible:ring-gray-500',
          'dark:border-gray-600 dark:hover:bg-gray-800',
        ],
        secondary: [
          'bg-gray-100 text-gray-900 hover:bg-gray-200',
          'focus-visible:ring-gray-500',
          'dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700',
        ],
        ghost: [
          'hover:bg-gray-100 hover:text-gray-900',
          'focus-visible:ring-gray-500',
          'dark:hover:bg-gray-800 dark:hover:text-gray-100',
        ],
        link: [
          'text-primary-500 underline-offset-4 hover:underline',
          'focus-visible:ring-primary-500',
          'dark:text-primary-400',
        ],
        success: [
          'bg-success-500 text-white hover:bg-success-600',
          'focus-visible:ring-success-500',
          'dark:bg-success-600 dark:hover:bg-success-700',
        ],
        warning: [
          'bg-warning-500 text-white hover:bg-warning-600',
          'focus-visible:ring-warning-500',
          'dark:bg-warning-600 dark:hover:bg-warning-700',
        ],
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-8 px-3 text-xs',
        lg: 'h-12 px-8 text-base',
        xl: 'h-14 px-10 text-lg',
        icon: 'h-10 w-10',
      },
      fullWidth: {
        true: 'w-full',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
      fullWidth: false,
    },
  }
);

// 버튼 인터페이스
export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
}

// Button 컴포넌트
const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      fullWidth,
      asChild = false,
      loading = false,
      leftIcon,
      rightIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    // 로딩 상태일 때 비활성화
    const isDisabled = disabled || loading;

    // 접근성을 위한 aria-label 생성
    const getAriaLabel = () => {
      if (loading) {
        return `${children} 로딩 중...`;
      }
      return typeof children === 'string' ? children : undefined;
    };

    return (
      <button
        className={cn(buttonVariants({ variant, size, fullWidth, className }))}
        ref={ref}
        disabled={isDisabled}
        aria-label={getAriaLabel()}
        aria-busy={loading}
        {...props}
      >
        {/* 로딩 스피너 */}
        {loading && (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
        )}
        
        {/* 왼쪽 아이콘 */}
        {!loading && leftIcon && (
          <span className="mr-2" aria-hidden="true">
            {leftIcon}
          </span>
        )}
        
        {/* 버튼 텍스트 */}
        <span className={cn(loading && 'sr-only')}>
          {children}
        </span>
        
        {/* 오른쪽 아이콘 */}
        {!loading && rightIcon && (
          <span className="ml-2" aria-hidden="true">
            {rightIcon}
          </span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button, buttonVariants }; 