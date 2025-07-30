import { useState, useEffect } from 'react'

export interface PluginMenuItem {
  title: string
  path: string
  icon?: string
  parent?: string
  roles?: string[]
  order?: number
  badge?: string
  plugin?: string
}

export interface PluginMenuGroup {
  title: string
  items: PluginMenuItem[]
}

export function usePluginMenus() {
  const [menus, setMenus] = useState<PluginMenuItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadMenus = async () => {
    try {
      setLoading(true)
      
      // 더미 플러그인 메뉴 데이터
      const dummyMenus: PluginMenuItem[] = [
        {
          title: '대시보드',
          path: '/dashboard',
          icon: 'dashboard',
          parent: 'main',
          order: 1
        },
        {
          title: '브랜드 관리',
          path: '/brands',
          icon: 'brand',
          parent: 'management',
          order: 1
        },
        {
          title: '매장 관리',
          path: '/stores',
          icon: 'store',
          parent: 'management',
          order: 2
        },
        {
          title: '직원 관리',
          path: '/employees',
          icon: 'users',
          parent: 'management',
          order: 3
        },
        {
          title: '출근 관리',
          path: '/attendance',
          icon: 'clock',
          parent: 'operations',
          order: 1
        },
        {
          title: '재고 관리',
          path: '/inventory',
          icon: 'package',
          parent: 'operations',
          order: 2
        },
        {
          title: '주문 관리',
          path: '/orders',
          icon: 'shopping-cart',
          parent: 'operations',
          order: 3
        },
        {
          title: '시스템 상태',
          path: '/system-health',
          icon: 'activity',
          parent: 'monitoring',
          order: 1
        },
        {
          title: '고급 분석',
          path: '/advanced-analytics',
          icon: 'bar-chart',
          parent: 'monitoring',
          order: 2
        },
        {
          title: '설정',
          path: '/settings',
          icon: 'settings',
          parent: 'system',
          order: 1
        }
      ]
      
      setMenus(dummyMenus)
      setError(null)
    } catch (err) {
      setError(null) // 오류 메시지 숨김
    } finally {
      setLoading(false)
    }
  }

  const getMenusByParent = (parent?: string): PluginMenuItem[] => {
    return menus.filter(menu => menu.parent === parent)
  }

  const getMenusByRole = (userRole: string): PluginMenuItem[] => {
    return menus.filter(menu => {
      if (!menu.roles || menu.roles.length === 0) return true
      return menu.roles.includes(userRole)
    })
  }

  const getMenuGroups = (): PluginMenuGroup[] => {
    const groups: Record<string, PluginMenuItem[]> = {}
    
    menus.forEach(menu => {
      const parent = menu.parent || 'main'
      if (!groups[parent]) {
        groups[parent] = []
      }
      groups[parent].push(menu)
    })
    
    return Object.entries(groups).map(([title, items]) => ({
      title,
      items: items.sort((a, b) => (a.order || 999) - (b.order || 999))
    }))
  }

  const getMenuByPath = (path: string): PluginMenuItem | undefined => {
    return menus.find(menu => menu.path === path)
  }

  useEffect(() => {
    loadMenus()
  }, [])

  return {
    menus,
    loading,
    error,
    loadMenus,
    getMenusByParent,
    getMenusByRole,
    getMenuGroups,
    getMenuByPath
  }
} 