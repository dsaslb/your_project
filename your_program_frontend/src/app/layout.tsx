import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import NotificationCenter from "../components/NotificationCenter";
import OfflineSyncIndicator from "../components/OfflineSyncIndicator";
import PWAInstallPrompt from "../components/PWAInstallPrompt";
import Sidebar from '@/components/Sidebar'
import RealTimeSync from '@/components/RealTimeSync'
import PluginAlertToast from '@/components/PluginAlertToast'
import { ThemeProvider } from "@/components/theme-provider"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Your Program - 관리 시스템",
  description: "Your Program 관리 시스템",
  manifest: "/manifest.json",
  themeColor: "#3b82f6",
  viewport: "width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "레스토랑 관리",
  },
  formatDetection: {
    telephone: false,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/icon-192x192.png" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="레스토랑 관리" />
      </head>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <RealTimeSync />
          <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
            <Sidebar />
            <main className="flex-1 overflow-auto">
              {children}
            </main>
          </div>
          <NotificationCenter />
          <OfflineSyncIndicator />
          <PWAInstallPrompt />
          <PluginAlertToast />
        </ThemeProvider>
      </body>
    </html>
  )
}
