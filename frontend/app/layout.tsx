import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { LayoutWrapper } from '@/components/LayoutWrapper'
import ErrorBoundary from '../src/components/ErrorBoundary'
import GlobalErrorHandler from '../src/components/GlobalErrorHandler'
import { AccessibilityProvider } from '../src/components/AccessibilityProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: '멀티테넌시 관리 시스템',
  description: '업종/브랜드/매장/직원 계층별 관리 시스템',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body className={inter.className}>
        <ErrorBoundary>
          <AccessibilityProvider>
            <GlobalErrorHandler />
            <LayoutWrapper>
              {children}
            </LayoutWrapper>
          </AccessibilityProvider>
        </ErrorBoundary>
      </body>
    </html>
  )
} 