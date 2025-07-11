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
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadMenus = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/plugins/menus')
      const data = await response.json()
      
      if (data.status === 'success') {
        // order 기준으로 정렬
        const sortedMenus = data.data.sort((a: PluginMenuItem, b: PluginMenuItem) => {
          const orderA = a.order || 999
          const orderB = b.order || 999
          return orderA - orderB
        })
        setMenus(sortedMenus)
      } else {
        setError('메뉴 목록을 불러오는데 실패했습니다')
      }
    } catch (err) {
      setError('메뉴 목록을 불러오는데 실패했습니다')
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