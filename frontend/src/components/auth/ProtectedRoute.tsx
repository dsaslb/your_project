'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import useUserStore from '@/store/useUserStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
  fallback?: React.ReactNode;
}

export default function ProtectedRoute({ children }: any) {
  // 인증 우회: 항상 children 렌더
  return <>{children}</>;
} 