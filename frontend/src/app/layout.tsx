import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from '@/lib/queryClient'
import { ToastContainer } from '@/components/ui/Toast'
import { useToastStore } from '@/store/useToastStore'
import { WebSocketProvider } from '@/components/WebSocketProvider'

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  preload: true,
})

export const metadata: Metadata = {
  title: 'Your Program',
  description: 'Comprehensive management system',
}

function ToastProvider() {
  const toasts = useToastStore((state) => state.toasts);
  const removeToast = useToastStore((state) => state.removeToast);

  return <ToastContainer toasts={toasts} onClose={removeToast} />;
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body className={inter.className}>
        <QueryClientProvider client={queryClient}>
          <WebSocketProvider>
            {children}
            <ToastProvider />
          </WebSocketProvider>
        </QueryClientProvider>
      </body>
    </html>
  )
}
