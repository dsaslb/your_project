import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Navigation from '../components/Navigation'

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
        <div className="flex min-h-screen bg-black text-white relative overflow-hidden">
          {/* 배경 효과 */}
          <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900"></div>
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(120,119,198,0.3),transparent_50%)]"></div>
          <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(68,68,68,0.2)_50%,transparent_75%)] bg-[length:20px_20px]"></div>
          
          {/* 상단 네온 라인 */}
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-60"></div>
          
          <div className="relative z-10 flex w-full">
            {/* 멀티테넌시 관리 시스템 사이드바 */}
            <Navigation />
            
            {/* 메인 콘텐츠 */}
            <div className="flex-1">
              {children}
            </div>
          </div>
          
          {/* 하단 네온 라인 */}
          <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-400 to-transparent opacity-60"></div>
        </div>
      </body>
    </html>
  )
} 