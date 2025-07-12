import { useState, useEffect } from 'react';

interface MobileState {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  orientation: 'portrait' | 'landscape';
  screenSize: {
    width: number;
    height: number;
  };
  isPWA: boolean;
  isStandalone: boolean;
}

export const useMobile = (): MobileState => {
  const [mobileState, setMobileState] = useState<MobileState>({
    isMobile: false,
    isTablet: false,
    isDesktop: false,
    orientation: 'portrait',
    screenSize: { width: 0, height: 0 },
    isPWA: false,
    isStandalone: false,
  });

  useEffect(() => {
    const updateMobileState = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      // 화면 크기별 분류
      const isMobile = width < 768;
      const isTablet = width >= 768 && width < 1024;
      const isDesktop = width >= 1024;
      
      // 방향 감지
      const orientation = width > height ? 'landscape' : 'portrait';
      
      // PWA 감지
      const isPWA = window.matchMedia('(display-mode: standalone)').matches;
      const isStandalone = (window.navigator as any).standalone || isPWA;

      setMobileState({
        isMobile,
        isTablet,
        isDesktop,
        orientation,
        screenSize: { width, height },
        isPWA,
        isStandalone,
      });
    };

    // 초기 상태 설정
    updateMobileState();

    // 리사이즈 이벤트 리스너
    window.addEventListener('resize', updateMobileState);
    window.addEventListener('orientationchange', updateMobileState);

    return () => {
      window.removeEventListener('resize', updateMobileState);
      window.removeEventListener('orientationchange', updateMobileState);
    };
  }, []);

  return mobileState;
};

// 터치 제스처 훅
export const useTouchGestures = () => {
  const [touchStart, setTouchStart] = useState<{ x: number; y: number } | null>(null);
  const [touchEnd, setTouchEnd] = useState<{ x: number; y: number } | null>(null);

  const minSwipeDistance = 50;

  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null);
    setTouchStart({
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY,
    });
  };

  const onTouchMove = (e: React.TouchEvent) => {
    setTouchEnd({
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY,
    });
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;

    const distanceX = touchStart.x - touchEnd.x;
    const distanceY = touchStart.y - touchEnd.y;
    const isHorizontalSwipe = Math.abs(distanceX) > Math.abs(distanceY);

    if (isHorizontalSwipe) {
      if (Math.abs(distanceX) > minSwipeDistance) {
        if (distanceX > 0) {
          // 왼쪽으로 스와이프
          return 'swipeLeft';
        } else {
          // 오른쪽으로 스와이프
          return 'swipeRight';
        }
      }
    } else {
      if (Math.abs(distanceY) > minSwipeDistance) {
        if (distanceY > 0) {
          // 위로 스와이프
          return 'swipeUp';
        } else {
          // 아래로 스와이프
          return 'swipeDown';
        }
      }
    }

    return null;
  };

  return {
    onTouchStart,
    onTouchMove,
    onTouchEnd,
  };
};

// 모바일 최적화 훅
export const useMobileOptimization = () => {
  const { isMobile, isTablet, isStandalone } = useMobile();

  const mobileOptimizations = {
    // 터치 친화적 버튼 크기
    touchTargetSize: isMobile ? 'min-h-[44px] min-w-[44px]' : '',
    
    // 모바일에서 더 큰 폰트
    mobileTextSize: isMobile ? 'text-base' : 'text-sm',
    
    // 모바일에서 더 큰 간격
    mobileSpacing: isMobile ? 'space-y-4' : 'space-y-2',
    
    // PWA 모드에서 상태바 높이 고려
    pwaPadding: isStandalone ? 'pt-8' : '',
    
    // 모바일에서 그리드 컬럼 수 조정
    mobileGridCols: isMobile ? 'grid-cols-1' : isTablet ? 'grid-cols-2' : 'grid-cols-3',
    
    // 모바일에서 카드 레이아웃
    mobileCardLayout: isMobile ? 'flex flex-col' : 'grid grid-cols-2 gap-4',
  };

  return mobileOptimizations;
}; 