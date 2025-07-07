'use client';

import React, { createContext, useContext } from 'react';
import { usePermissions } from '@/lib/useAuth';
import { Permission, UserRole } from '@/lib/auth';

// 권한 컨텍스트 타입
interface PermissionContextType {
  hasPermission: (permission: Permission) => boolean;
  hasAnyPermission: (permissions: Permission[]) => boolean;
  hasAllPermissions: (permissions: Permission[]) => boolean;
  hasRole: (role: UserRole) => boolean;
  hasAnyRole: (roles: UserRole[]) => boolean;
  isSuperAdmin: () => boolean;
  isBrandManager: () => boolean;
  isStoreManager: () => boolean;
  isEmployee: () => boolean;
  isManager: () => boolean;
  canAccessBackend: () => boolean;
  canAccessFrontend: () => boolean;
}

// 권한 컨텍스트 생성
const PermissionContext = createContext<PermissionContextType | undefined>(undefined);

// 권한 컨텍스트 사용 훅
export const usePermissionContext = () => {
  const context = useContext(PermissionContext);
  if (context === undefined) {
    throw new Error('usePermissionContext must be used within a PermissionProvider');
  }
  return context;
};

interface PermissionProviderProps {
  children: React.ReactNode;
}

export const PermissionProvider: React.FC<PermissionProviderProps> = ({ children }) => {
  const permissions = usePermissions();

  return (
    <PermissionContext.Provider value={permissions}>
      {children}
    </PermissionContext.Provider>
  );
}; 