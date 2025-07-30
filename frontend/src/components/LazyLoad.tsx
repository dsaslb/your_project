import React, { useState, useEffect, useRef, ReactNode } from 'react';

interface LazyLoadProps {
  children: ReactNode;
  threshold?: number;
  rootMargin?: string;
  fallback?: ReactNode;
  className?: string;
}

export const LazyLoad: React.FC<LazyLoadProps> = ({
  children,
  threshold = 0.1,
  rootMargin = '50px',
  fallback = <div className="animate-pulse bg-gray-200 h-32 rounded" />,
  className = '',
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      {
        threshold,
        rootMargin,
      }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [threshold, rootMargin]);

  useEffect(() => {
    if (isVisible) {
      // 지연 로딩 시뮬레이션 (실제로는 필요 없음)
      const timer = setTimeout(() => {
        setHasLoaded(true);
      }, 100);

      return () => clearTimeout(timer);
    }
  }, [isVisible]);

  return (
    <div ref={ref} className={className}>
      {!hasLoaded ? fallback : children}
    </div>
  );
};

// 특정 컴포넌트용 지연 로딩
export const LazyComponent: React.FC<{
  component: React.ComponentType<any>;
  props?: any;
  fallback?: ReactNode;
}> = ({ component: Component, props = {}, fallback }) => {
  return (
    <LazyLoad fallback={fallback}>
      <Component {...props} />
    </LazyLoad>
  );
};

export default LazyLoad; 