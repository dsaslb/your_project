import ComfortableLoginPage from '../comfortable-login'
import { useRouter } from 'next/navigation';
import useUserStore from '@/store/useUserStore';
import { useEffect } from 'react';

export default function LoginPage() {
  const router = useRouter();
  const { user, setUser } = useUserStore();

  useEffect(() => {
    // 로그인 후 권한별로 자동 이동 및 맞춤 안내
    if (user) {
      if (user.role === 'brand_manager') {
        router.push('/brand-dashboard'); // 브랜드 관리자 대시보드
      } else if (user.role === 'store_manager') {
        router.push('/store-dashboard'); // 매장 관리자 대시보드
      } else if (user.role === 'employee') {
        router.push('/employee-dashboard'); // 직원 대시보드
      } else {
        router.push('/dashboard'); // 기타 권한
      }
    }
  }, [user, router]);

  return <ComfortableLoginPage />
} 
