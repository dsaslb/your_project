import { useState, useEffect } from 'react';
import useUserStore from '@/store/useUserStore';

interface UserMenuPreferences {
  userId: string;
  favoriteMenus: string[];
  hiddenMenus: string[];
  menuOrder: string[];
  lastAccessed: Record<string, Date>;
  customCategories: Record<string, string[]>;
}

export const useMenuPreferences = () => {
  const { user } = useUserStore();
  const [preferences, setPreferences] = useState<UserMenuPreferences>({
    userId: user?.id?.toString() || '',
    favoriteMenus: [],
    hiddenMenus: [],
    menuOrder: [],
    lastAccessed: {},
    customCategories: {},
  });

  const [loading, setLoading] = useState(true);

  // 로컬 스토리지에서 설정 로드
  const loadPreferences = () => {
    if (!user?.id) return;

    try {
      const stored = localStorage.getItem(`menu_preferences_${user.id}`);
      if (stored) {
        const parsed = JSON.parse(stored);
        setPreferences(parsed);
      }
    } catch (error) {
      console.error('메뉴 설정 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  // 로컬 스토리지에 설정 저장
  const savePreferences = (newPreferences: UserMenuPreferences) => {
    if (!user?.id) return;

    try {
      localStorage.setItem(`menu_preferences_${user.id}`, JSON.stringify(newPreferences));
      setPreferences(newPreferences);
    } catch (error) {
      console.error('메뉴 설정 저장 오류:', error);
    }
  };

  // 즐겨찾기 메뉴 추가/제거
  const toggleFavorite = (href: string) => {
    const newPreferences = { ...preferences };
    const index = newPreferences.favoriteMenus.indexOf(href);
    
    if (index > -1) {
      newPreferences.favoriteMenus.splice(index, 1);
    } else {
      newPreferences.favoriteMenus.push(href);
    }
    
    savePreferences(newPreferences);
  };

  // 메뉴 숨김/표시
  const toggleHidden = (href: string) => {
    const newPreferences = { ...preferences };
    const index = newPreferences.hiddenMenus.indexOf(href);
    
    if (index > -1) {
      newPreferences.hiddenMenus.splice(index, 1);
    } else {
      newPreferences.hiddenMenus.push(href);
    }
    
    savePreferences(newPreferences);
  };

  // 메뉴 접근 기록 업데이트
  const updateLastAccessed = (href: string) => {
    const newPreferences = { ...preferences };
    newPreferences.lastAccessed[href] = new Date();
    savePreferences(newPreferences);
  };

  // 메뉴 우선순위 계산
  const getMenuPriority = (href: string): number => {
    const isFavorite = preferences.favoriteMenus.includes(href);
    const lastAccessed = preferences.lastAccessed[href];
    const daysSinceLastAccess = lastAccessed 
      ? (new Date().getTime() - new Date(lastAccessed).getTime()) / (1000 * 60 * 60 * 24)
      : 999;

    let priority = 0;
    
    // 즐겨찾기는 높은 우선순위
    if (isFavorite) priority += 100;
    
    // 최근 접근은 높은 우선순위 (최대 30일)
    if (daysSinceLastAccess < 30) {
      priority += Math.max(0, 30 - daysSinceLastAccess);
    }

    return priority;
  };

  // 메뉴 필터링 (숨김 메뉴 제외)
  const filterHiddenMenus = (menus: any[]) => {
    return menus.filter(menu => !preferences.hiddenMenus.includes(menu.href || ''));
  };

  // 메뉴 정렬 (우선순위 기반)
  const sortMenusByPriority = (menus: any[]) => {
    return [...menus].sort((a, b) => {
      const priorityA = getMenuPriority(a.href || '');
      const priorityB = getMenuPriority(b.href || '');
      return priorityB - priorityA;
    });
  };

  // 즐겨찾기 메뉴만 가져오기
  const getFavoriteMenus = (menus: any[]) => {
    return menus.filter(menu => preferences.favoriteMenus.includes(menu.href || ''));
  };

  // 최근 접근 메뉴 가져오기 (최근 7일)
  const getRecentMenus = (menus: any[], days: number = 7) => {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    return menus.filter(menu => {
      const lastAccessed = preferences.lastAccessed[menu.href || ''];
      return lastAccessed && new Date(lastAccessed) > cutoffDate;
    });
  };

  useEffect(() => {
    loadPreferences();
  }, [user?.id]);

  return {
    preferences,
    loading,
    toggleFavorite,
    toggleHidden,
    updateLastAccessed,
    getMenuPriority,
    filterHiddenMenus,
    sortMenusByPriority,
    getFavoriteMenus,
    getRecentMenus,
    isFavorite: (href: string) => preferences.favoriteMenus.includes(href),
    isHidden: (href: string) => preferences.hiddenMenus.includes(href),
  };
}; 