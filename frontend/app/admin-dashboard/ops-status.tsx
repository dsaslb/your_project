import React from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/router';
// import { useAuth } from '../../hooks/useAuth'; // 실제 인증 훅이 있다면 사용

// 동적 import로 코드 스플리팅
const OpsStatus = dynamic(() => import('./OpsStatus'), { ssr: false });

const AdminOpsStatusPage: React.FC = () => {
  // const { user, isLoading } = useAuth();
  const router = useRouter();

  // 관리자 권한 체크 예시 (실제 인증 훅/로직에 맞게 수정)
  // if (isLoading) return <div>로딩 중...</div>;
  // if (!user || user.role !== 'admin') {
  //   if (typeof window !== 'undefined') router.replace('/unauthorized');
  //   return <div>접근 권한이 없습니다.</div>;
  // }

  return <OpsStatus />;
};

export default AdminOpsStatusPage; 