'use client';

import React from 'react';

// 임시로 비활성화 - useAuth 문제 해결 필요
export const PermissionGuard: React.FC<any> = ({ children, fallback = null }) => {
  return <>{children}</>;
};

export const WithPermission: React.FC<any> = ({ children, fallback }) => (
  <>{children}</>
);

export const WithRole: React.FC<any> = ({ children, fallback }) => (
  <>{children}</>
);

export const SuperAdminOnly: React.FC<any> = ({ children, fallback }) => (
  <>{children}</>
);

export const BrandManagerOnly: React.FC<any> = ({ children, fallback }) => (
  <>{children}</>
);

export const StoreManagerOnly: React.FC<any> = ({ children, fallback }) => (
  <>{children}</>
);

export const EmployeeOnly: React.FC<any> = ({ children, fallback }) => (
  <>{children}</>
);

export const ManagerOnly: React.FC<any> = ({ children, fallback }) => (
  <>{children}</>
);

export const BackendAccessOnly: React.FC<any> = ({ children, fallback }) => (
  <>{children}</>
);

export const FrontendAccessOnly: React.FC<any> = ({ children, fallback }) => (
  <>{children}</>
); 
