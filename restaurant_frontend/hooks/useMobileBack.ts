"use client"

import { useEffect, useRef } from 'react';
import { useRouter, usePathname } from 'next/navigation';

export function useMobileBack() {
  const router = useRouter();
  const pathname = usePathname();
  const historyStack = useRef<string[]>([]);
  const isInitialized = useRef(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // 초기화
    if (!isInitialized.current) {
      historyStack.current = ['/'];
      isInitialized.current = true;
    }

    // 현재 페이지를 히스토리 스택에 추가 (중복 방지)
    if (historyStack.current[historyStack.current.length - 1] !== pathname) {
      historyStack.current.push(pathname);
    }

    // 뒤로가기 이벤트 처리
    const handlePopState = (event: PopStateEvent) => {
      // 히스토리 스택에서 이전 페이지 가져오기
      if (historyStack.current.length > 1) {
        historyStack.current.pop(); // 현재 페이지 제거
        const previousPage = historyStack.current[historyStack.current.length - 1];
        
        if (previousPage && previousPage !== pathname) {
          router.push(previousPage);
        } else {
          // 이전 페이지가 없으면 대시보드로
          router.push('/');
        }
      } else {
        // 히스토리가 비어있으면 대시보드로
        router.push('/');
      }
    };

    // 페이지 떠나기 전 확인
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      if (pathname !== '/') {
        // 모바일에서 뒤로가기 버튼을 눌렀을 때
        event.preventDefault();
        event.returnValue = '';
        
        // 히스토리 스택에서 이전 페이지로 이동
        if (historyStack.current.length > 1) {
          historyStack.current.pop();
          const previousPage = historyStack.current[historyStack.current.length - 1];
          if (previousPage) {
            router.push(previousPage);
          }
        }
      }
    };

    // 이벤트 리스너 등록
    window.addEventListener('popstate', handlePopState);
    window.addEventListener('beforeunload', handleBeforeUnload);

    // 히스토리 상태 업데이트
    window.history.replaceState(
      { 
        page: pathname, 
        stack: historyStack.current 
      }, 
      '', 
      pathname
    );

    return () => {
      window.removeEventListener('popstate', handlePopState);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [pathname, router]);

  // 수동 뒤로가기 함수
  const goBack = () => {
    if (historyStack.current.length > 1) {
      historyStack.current.pop();
      const previousPage = historyStack.current[historyStack.current.length - 1];
      if (previousPage) {
        router.push(previousPage);
      }
    } else {
      router.push('/');
    }
  };

  return { goBack, historyStack: historyStack.current };
} 