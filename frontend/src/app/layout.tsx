import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { useEffect } from 'react'
import { initializePerformanceMonitoring, cleanupPerformanceMonitoring } from '@/utils/performance'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Your Program - 관리 시스템',
  description: '현대적인 비즈니스 관리 시스템',
  keywords: ['관리', '비즈니스', '시스템', '대시보드'],
  authors: [{ name: 'Your Program Team' }],
  creator: 'Your Program',
  publisher: 'Your Program',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('http://localhost:3000'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'Your Program - 관리 시스템',
    description: '현대적인 비즈니스 관리 시스템',
    url: 'http://localhost:3000',
    siteName: 'Your Program',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Your Program',
      },
    ],
    locale: 'ko_KR',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Your Program - 관리 시스템',
    description: '현대적인 비즈니스 관리 시스템',
    images: ['/og-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
  },
}

// 성능 모니터링 컴포넌트
function PerformanceMonitor() {
  useEffect(() => {
    // 성능 모니터링 초기화
    initializePerformanceMonitoring();

    // 컴포넌트 언마운트 시 정리
    return () => {
      cleanupPerformanceMonitoring();
    };
  }, []);

  return null; // 이 컴포넌트는 UI를 렌더링하지 않음
}

// Google Analytics 스크립트
function GoogleAnalytics() {
  useEffect(() => {
    // Google Analytics 초기화
    if (typeof window !== 'undefined' && process.env.NEXT_PUBLIC_GA_ID) {
      // Google Analytics 4 설정
      (window as any).dataLayer = (window as any).dataLayer || [];
      function gtag(...args: any[]) {
        (window as any).dataLayer.push(args);
      }
      (window as any).gtag = gtag;
      gtag('js', new Date());
      gtag('config', process.env.NEXT_PUBLIC_GA_ID, {
        page_title: document.title,
        page_location: window.location.href,
      });
    }
  }, []);

  return null;
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko" className="h-full">
      <head>
        {/* 성능 최적화 메타 태그 */}
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
        <meta name="theme-color" content="#3B82F6" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="Your Program" />
        
        {/* DNS 프리페치 */}
        <link rel="dns-prefetch" href="//fonts.googleapis.com" />
        <link rel="dns-prefetch" href="//fonts.gstatic.com" />
        <link rel="dns-prefetch" href="//www.googletagmanager.com" />
        
        {/* 리소스 프리로드 */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        
        {/* PWA 매니페스트 */}
        <link rel="manifest" href="/manifest.json" />
        
        {/* 파비콘 */}
        <link rel="icon" type="image/x-icon" href="/favicon.ico" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        
        {/* 보안 헤더 */}
        <meta httpEquiv="X-Content-Type-Options" content="nosniff" />
        <meta httpEquiv="X-Frame-Options" content="DENY" />
        <meta httpEquiv="X-XSS-Protection" content="1; mode=block" />
        <meta httpEquiv="Referrer-Policy" content="origin-when-cross-origin" />
        
        {/* Google Analytics 스크립트 */}
        {process.env.NEXT_PUBLIC_GA_ID && (
          <>
            <script
              async
              src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`}
            />
            <script
              dangerouslySetInnerHTML={{
                __html: `
                  window.dataLayer = window.dataLayer || [];
                  function gtag(){dataLayer.push(arguments);}
                  gtag('js', new Date());
                  gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}', {
                    page_title: document.title,
                    page_location: window.location.href,
                  });
                `,
              }}
            />
          </>
        )}
      </head>
      <body className={`${inter.className} h-full antialiased`}>
        {/* 성능 모니터링 */}
        <PerformanceMonitor />
        
        {/* Google Analytics */}
        <GoogleAnalytics />
        
        {/* 메인 컨텐츠 */}
        <div id="root" className="h-full">
          {children}
        </div>
        
        {/* 성능 최적화 스크립트 */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // 서비스 워커 등록 (PWA 지원)
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js')
                    .then(function(registration) {
                      console.log('SW registered: ', registration);
                    })
                    .catch(function(registrationError) {
                      console.log('SW registration failed: ', registrationError);
                    });
                });
              }
              
              // 성능 최적화
              document.addEventListener('DOMContentLoaded', function() {
                // 이미지 지연 로딩
                const images = document.querySelectorAll('img[data-src]');
                const imageObserver = new IntersectionObserver((entries) => {
                  entries.forEach(entry => {
                    if (entry.isIntersecting) {
                      const img = entry.target;
                      img.src = img.dataset.src;
                      img.classList.remove('lazy');
                      imageObserver.unobserve(img);
                    }
                  });
                });
                
                images.forEach(img => imageObserver.observe(img));
                
                // 스크롤 성능 최적화
                let ticking = false;
                function updateScroll() {
                  ticking = false;
                }
                
                function requestTick() {
                  if (!ticking) {
                    requestAnimationFrame(updateScroll);
                    ticking = true;
                  }
                }
                
                window.addEventListener('scroll', requestTick, { passive: true });
              });
            `,
          }}
        />
      </body>
    </html>
  )
}
