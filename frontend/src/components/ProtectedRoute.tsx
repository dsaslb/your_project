'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import LoadingSpinner from './LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'admin' | 'brand_admin' | 'store_admin' | 'manager' | 'employee';
  requiredPermission?: {
    module: string;
    action: string;
  };
  fallback?: React.ReactNode;
  redirectTo?: string;
}

export default function ProtectedRoute({
  children,
  requiredRole,
  requiredPermission,
  fallback,
  redirectTo = '/unauthorized'
}: ProtectedRouteProps) {
  const { currentUser, isLoading, isAuthenticated, hasPermission } = useAuth();
  const router = useRouter();
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    if (isLoading) return;

    // 개발 모드: 인증 우회
    if (process.env.NODE_ENV === 'development') {
      setIsAuthorized(true);
      return;
    }

    // 인증 확인
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    // 역할 확인
    if (requiredRole && currentUser?.role !== requiredRole) {
      router.push(redirectTo);
      return;
    }

    // 권한 확인
    if (requiredPermission && !hasPermission(requiredPermission.module, requiredPermission.action)) {
      router.push(redirectTo);
      return;
    }

    setIsAuthorized(true);
  }, [currentUser, isLoading, requiredRole, requiredPermission, redirectTo, router, isAuthenticated, hasPermission]);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!isAuthorized) {
    return fallback || <LoadingSpinner />;
  }

  return <>{children}</>;
} 