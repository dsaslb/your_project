/**
 * 🎨 Card 컴포넌트
 * 
 * 접근성을 고려한 재사용 가능한 카드 컴포넌트입니다.
 */

import React, { forwardRef } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

// 카드 변형 정의
const cardVariants = cva(
  // 기본 스타일
  [
    'rounded-lg border bg-white shadow-sm',
    'transition-all duration-200',
    'focus-within:ring-2 focus-within:ring-primary-500 focus-within:ring-offset-2',
    'dark:bg-gray-800 dark:border-gray-700',
  ],
  {
    variants: {
      variant: {
        default: '',
        elevated: [
          'shadow-md hover:shadow-lg',
          'dark:shadow-gray-900/20',
        ],
        outlined: [
          'border-2 border-gray-200',
          'dark:border-gray-600',
        ],
        interactive: [
          'cursor-pointer hover:shadow-md hover:scale-[1.02]',
          'active:scale-[0.98]',
          'focus-within:shadow-lg',
        ],
        flat: [
          'border-0 shadow-none',
          'bg-gray-50',
          'dark:bg-gray-900',
        ],
      },
      padding: {
        none: 'p-0',
        sm: 'p-3',
        default: 'p-4',
        lg: 'p-6',
        xl: 'p-8',
      },
      fullWidth: {
        true: 'w-full',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'default',
      padding: 'default',
      fullWidth: false,
    },
  }
);

// 카드 인터페이스
export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  asChild?: boolean;
  children: React.ReactNode;
}

// Card 컴포넌트
const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, padding, fullWidth, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(cardVariants({ variant, padding, fullWidth, className }))}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

// CardHeader 컴포넌트
export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const CardHeader = forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('flex flex-col space-y-1.5 p-6', className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardHeader.displayName = 'CardHeader';

// CardTitle 컴포넌트
export interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
}

const CardTitle = forwardRef<HTMLHeadingElement, CardTitleProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <h3
        ref={ref}
        className={cn(
          'text-2xl font-semibold leading-none tracking-tight',
          'text-gray-900 dark:text-gray-100',
          className
        )}
        {...props}
      >
        {children}
      </h3>
    );
  }
);

CardTitle.displayName = 'CardTitle';

// CardDescription 컴포넌트
export interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode;
}

const CardDescription = forwardRef<HTMLParagraphElement, CardDescriptionProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <p
        ref={ref}
        className={cn(
          'text-sm text-gray-600 dark:text-gray-400',
          className
        )}
        {...props}
      >
        {children}
      </p>
    );
  }
);

CardDescription.displayName = 'CardDescription';

// CardContent 컴포넌트
export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const CardContent = forwardRef<HTMLDivElement, CardContentProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('p-6 pt-0', className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardContent.displayName = 'CardContent';

// CardFooter 컴포넌트
export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const CardFooter = forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('flex items-center p-6 pt-0', className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardFooter.displayName = 'CardFooter';

export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  cardVariants,
}; 