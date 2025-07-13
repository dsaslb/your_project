"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  Bell, 
  X, 
  AlertTriangle, 
  CheckCircle, 
  Info, 
  Clock,
  Trash2
} from "lucide-react"

interface Notification {
  id: string
  type: 'info' | 'warning' | 'error' | 'success'
  title: string
  message: string
  timestamp: string
  read: boolean
  category?: string
  action_url?: string
}

interface RealTimeNotificationsProps {
  className?: string
}

export default function RealTimeNotifications({ className }: RealTimeNotificationsProps) {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [showNotifications, setShowNotifications] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // WebSocket 연결
    const connectWebSocket = () => {
      const token = localStorage.getItem('jwt_token')
      if (!token) return

      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/notifications'
      const ws = new WebSocket(`${wsUrl}?token=${token}`)
      
      ws.onopen = () => {
        console.log('WebSocket 연결됨')
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type === 'notification') {
            addNotification(data.notification)
          }
        } catch (error) {
          console.error('WebSocket 메시지 파싱 오류:', error)
        }
      }
      
      ws.onclose = () => {
        console.log('WebSocket 연결 종료')
        // 재연결 시도
        setTimeout(connectWebSocket, 5000)
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket 오류:', error)
      }
      
      wsRef.current = ws
    }

    connectWebSocket()

    // 컴포넌트 언마운트 시 WebSocket 연결 종료
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  const addNotification = (notification: Notification) => {
    setNotifications(prev => [notification, ...prev.slice(0, 49)]) // 최대 50개 유지
    setUnreadCount(prev => prev + 1)
    
    // 브라우저 알림 표시
    if (Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/favicon.ico'
      })
    }
  }

  const markAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === id ? { ...notif, read: true } : notif
      )
    )
    setUnreadCount(prev => Math.max(0, prev - 1))
  }

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notif => ({ ...notif, read: true }))
    )
    setUnreadCount(0)
  }

  const deleteNotification = (id: string) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id))
    setUnreadCount(prev => {
      const notification = notifications.find(n => n.id === id)
      return notification && !notification.read ? Math.max(0, prev - 1) : prev
    })
  }

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckCircle className="h-4 w-4 text-green-400" />
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-400" />
      case 'error': return <AlertTriangle className="h-4 w-4 text-red-400" />
      default: return <Info className="h-4 w-4 text-blue-400" />
    }
  }

  const getNotificationBadge = (type: string) => {
    switch (type) {
      case 'success': return <Badge className="bg-green-500/20 text-green-300 border-green-500/30">성공</Badge>
      case 'warning': return <Badge className="bg-yellow-500/20 text-yellow-300 border-yellow-500/30">경고</Badge>
      case 'error': return <Badge className="bg-red-500/20 text-red-300 border-red-500/30">오류</Badge>
      default: return <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/30">정보</Badge>
    }
  }

  const formatTime = (timestamp: string) => {
    const now = new Date()
    const time = new Date(timestamp)
    const diff = now.getTime() - time.getTime()
    
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)
    
    if (days > 0) return `${days}일 전`
    if (hours > 0) return `${hours}시간 전`
    if (minutes > 0) return `${minutes}분 전`
    return '방금 전'
  }

  return (
    <div className={`relative ${className}`}>
      {/* 알림 버튼 */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setShowNotifications(!showNotifications)}
        className="relative text-white hover:bg-white/10"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <Badge className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-xs">
            {unreadCount > 99 ? '99+' : unreadCount}
          </Badge>
        )}
      </Button>

      {/* 알림 패널 */}
      {showNotifications && (
        <div className="absolute right-0 top-12 w-80 bg-slate-800 rounded-lg shadow-lg border border-slate-700 z-50">
          <Card className="bg-transparent border-0">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-white text-sm">알림</CardTitle>
                <div className="flex items-center space-x-2">
                  {unreadCount > 0 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={markAllAsRead}
                      className="text-xs text-slate-400 hover:text-white"
                    >
                      모두 읽음
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowNotifications(false)}
                    className="text-slate-400 hover:text-white"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="max-h-96 overflow-y-auto space-y-2">
                {notifications.length === 0 ? (
                  <div className="text-center py-8">
                    <Bell className="h-8 w-8 text-slate-500 mx-auto mb-2" />
                    <p className="text-slate-400 text-sm">알림이 없습니다</p>
                  </div>
                ) : (
                  notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`p-3 rounded-lg transition-colors ${
                        notification.read 
                          ? 'bg-slate-700/50' 
                          : 'bg-blue-500/10 border border-blue-500/30'
                      }`}
                      onClick={() => markAsRead(notification.id)}
                    >
                      <div className="flex items-start space-x-3">
                        {getNotificationIcon(notification.type)}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <h4 className="text-sm font-medium text-white truncate">
                              {notification.title}
                            </h4>
                            <div className="flex items-center space-x-1">
                              {getNotificationBadge(notification.type)}
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  deleteNotification(notification.id)
                                }}
                                className="h-6 w-6 p-0 text-slate-400 hover:text-red-400"
                              >
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                          <p className="text-xs text-slate-300 mb-2 line-clamp-2">
                            {notification.message}
                          </p>
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-slate-500 flex items-center">
                              <Clock className="h-3 w-3 mr-1" />
                              {formatTime(notification.timestamp)}
                            </span>
                            {notification.category && (
                              <Badge variant="outline" className="text-xs">
                                {notification.category}
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
              
              {notifications.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-700">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setNotifications([])}
                    className="w-full text-slate-400 hover:text-white"
                  >
                    모든 알림 지우기
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
} 