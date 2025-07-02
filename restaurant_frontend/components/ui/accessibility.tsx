import React from 'react';
import { cn } from '@/lib/utils';

// 접근성 강화된 버튼
interface AccessibleButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  loading?: boolean;
  description?: string;
}

export function AccessibleButton({
  children,
  className,
  variant = 'default',
  size = 'default',
  loading = false,
  description,
  ...props
}: AccessibleButtonProps) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background',
        {
          'bg-primary text-primary-foreground hover:bg-primary/90': variant === 'default',
          'bg-destructive text-destructive-foreground hover:bg-destructive/90': variant === 'destructive',
          'border border-input hover:bg-accent hover:text-accent-foreground': variant === 'outline',
          'bg-secondary text-secondary-foreground hover:bg-secondary/80': variant === 'secondary',
          'hover:bg-accent hover:text-accent-foreground': variant === 'ghost',
          'underline-offset-4 hover:underline text-primary': variant === 'link',
          'h-10 py-2 px-4': size === 'default',
          'h-9 px-3 rounded-md': size === 'sm',
          'h-11 px-8 rounded-md': size === 'lg',
          'h-10 w-10': size === 'icon',
        },
        className
      )}
      disabled={loading || props.disabled}
      aria-describedby={description ? 'button-description' : undefined}
      {...props}
    >
      {loading && (
        <svg
          className="mr-2 h-4 w-4 animate-spin"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {children}
      {description && (
        <span id="button-description" className="sr-only">
          {description}
        </span>
      )}
    </button>
  );
}

// 접근성 강화된 카드
interface AccessibleCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  role?: string;
  tabIndex?: number;
}

export function AccessibleCard({
  children,
  className,
  role = 'region',
  tabIndex,
  ...props
}: AccessibleCardProps) {
  return (
    <div
      className={cn(
        'rounded-lg border bg-card text-card-foreground shadow-sm',
        className
      )}
      role={role}
      tabIndex={tabIndex}
      {...props}
    >
      {children}
    </div>
  );
}

// 접근성 강화된 모달
interface AccessibleModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  description?: string;
}

export function AccessibleModal({
  isOpen,
  onClose,
  title,
  children,
  description
}: AccessibleModalProps) {
  React.useEffect(() => {
    if (isOpen) {
      // 모달이 열릴 때 body 스크롤 방지
      document.body.style.overflow = 'hidden';
      // 포커스를 모달로 이동
      const modal = document.getElementById('modal-content');
      if (modal) {
        modal.focus();
      }
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      aria-describedby={description ? 'modal-description' : undefined}
    >
      <div
        id="modal-content"
        className="bg-white dark:bg-gray-900 rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto"
        tabIndex={-1}
        role="document"
      >
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 id="modal-title" className="text-xl font-bold text-gray-900 dark:text-white">
              {title}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              aria-label="모달 닫기"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          {description && (
            <p id="modal-description" className="text-gray-600 dark:text-gray-400 mb-4">
              {description}
            </p>
          )}
          {children}
        </div>
      </div>
    </div>
  );
}

// 접근성 강화된 토스트
interface AccessibleToastProps {
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  onClose: () => void;
  duration?: number;
}

export function AccessibleToast({
  message,
  type,
  onClose,
  duration = 3000
}: AccessibleToastProps) {
  React.useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  };

  const colors = {
    success: 'bg-green-600 text-white',
    error: 'bg-red-600 text-white',
    warning: 'bg-yellow-600 text-white',
    info: 'bg-blue-600 text-white'
  };

  return (
    <div
      className={`fixed top-6 right-6 z-50 px-4 py-3 rounded shadow-lg ${colors[type]}`}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div className="flex items-center gap-2">
        <span aria-hidden="true">{icons[type]}</span>
        <span>{message}</span>
        <button
          onClick={onClose}
          className="ml-2 text-white hover:text-gray-200"
          aria-label="토스트 닫기"
        >
          ✕
        </button>
      </div>
    </div>
  );
}

// 접근성 강화된 네비게이션
interface AccessibleNavProps {
  items: Array<{
    id: string;
    label: string;
    href: string;
    icon?: React.ReactNode;
  }>;
  currentPath: string;
}

export function AccessibleNav({ items, currentPath }: AccessibleNavProps) {
  return (
    <nav role="navigation" aria-label="메인 네비게이션">
      <ul className="flex flex-col space-y-1">
        {items.map((item) => {
          const isActive = currentPath === item.href;
          return (
            <li key={item.id}>
              <a
                href={item.href}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-800'
                }`}
                aria-current={isActive ? 'page' : undefined}
              >
                {item.icon && <span className="mr-3" aria-hidden="true">{item.icon}</span>}
                {item.label}
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
} 