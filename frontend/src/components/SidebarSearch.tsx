'use client';

import { useState, useMemo } from 'react';
import { Search, Filter, X, Star, Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

interface SidebarSearchProps {
  menuItems: any[];
  onSearch: (filteredItems: any[]) => void;
  onToggleFavorite: (href: string) => void;
  onToggleHidden: (href: string) => void;
  isFavorite: (href: string) => boolean;
  isHidden: (href: string) => boolean;
}

export const SidebarSearch = ({
  menuItems,
  onSearch,
  onToggleFavorite,
  onToggleHidden,
  isFavorite,
  isHidden,
}: SidebarSearchProps) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [showFilters, setShowFilters] = useState(false);

  // 카테고리 목록 추출
  const categories = useMemo(() => {
    const categorySet = new Set<string>();
    const extractCategories = (items: any[]) => {
      items.forEach(item => {
        if (item.category) {
          categorySet.add(item.category);
        }
        if (item.children) {
          extractCategories(item.children);
        }
      });
    };
    extractCategories(menuItems);
    return Array.from(categorySet);
  }, [menuItems]);

  // 검색 및 필터링
  const filteredMenus = useMemo(() => {
    const filterItems = (items: any[]): any[] => {
      return items.filter(item => {
        // 검색어 필터링
        const matchesSearch = searchTerm === '' || 
          item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (item.href && item.href.toLowerCase().includes(searchTerm.toLowerCase()));

        // 카테고리 필터링
        const matchesCategory = filterCategory === 'all' || item.category === filterCategory;

        // 숨김 메뉴 필터링
        const notHidden = !isHidden(item.href || '');

        if (item.children) {
          const filteredChildren = filterItems(item.children);
          item.children = filteredChildren;
          return matchesSearch && matchesCategory && notHidden && filteredChildren.length > 0;
        }

        return matchesSearch && matchesCategory && notHidden;
      });
    };

    return filterItems([...menuItems]);
  }, [searchTerm, filterCategory, menuItems, isHidden]);

  // 검색 결과를 부모 컴포넌트에 전달
  useMemo(() => {
    onSearch(filteredMenus);
  }, [filteredMenus, onSearch]);

  const clearSearch = () => {
    setSearchTerm('');
    setFilterCategory('all');
  };

  const hasActiveFilters = searchTerm !== '' || filterCategory !== 'all';

  return (
    <div className="p-4 border-b border-cyan-500/20">
      {/* 검색 입력 */}
      <div className="relative mb-3">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
        <Input
          type="text"
          placeholder="메뉴 검색..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10 pr-10 bg-black/50 border-cyan-500/30 text-white placeholder:text-slate-400 focus:border-cyan-500"
        />
        {searchTerm && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSearchTerm('')}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0 text-slate-400 hover:text-white"
          >
            <X className="w-3 h-3" />
          </Button>
        )}
      </div>

      {/* 필터 버튼 */}
      <div className="flex items-center justify-between mb-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowFilters(!showFilters)}
          className={cn(
            "text-xs px-2 py-1 h-auto",
            showFilters ? "bg-cyan-500/20 text-cyan-400" : "text-slate-400 hover:text-white"
          )}
        >
          <Filter className="w-3 h-3 mr-1" />
          필터
        </Button>

        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearSearch}
            className="text-xs px-2 py-1 h-auto text-red-400 hover:text-red-300"
          >
            필터 초기화
          </Button>
        )}
      </div>

      {/* 필터 옵션 */}
      {showFilters && (
        <div className="mb-3 p-3 bg-black/30 rounded-lg border border-cyan-500/20">
          {/* 카테고리 필터 */}
          <div className="mb-3">
            <label className="block text-xs text-slate-400 mb-2">카테고리</label>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="w-full px-2 py-1 text-xs bg-black/50 border border-cyan-500/30 text-white rounded focus:border-cyan-500"
            >
              <option value="all">모든 카테고리</option>
              {categories.map(category => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          {/* 빠른 필터 버튼 */}
          <div className="flex flex-wrap gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setFilterCategory('all')}
              className={cn(
                "text-xs px-2 py-1 h-auto",
                filterCategory === 'all' ? "bg-cyan-500/20 text-cyan-400" : "text-slate-400"
              )}
            >
              전체
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setFilterCategory('dashboard')}
              className={cn(
                "text-xs px-2 py-1 h-auto",
                filterCategory === 'dashboard' ? "bg-cyan-500/20 text-cyan-400" : "text-slate-400"
              )}
            >
              대시보드
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setFilterCategory('management')}
              className={cn(
                "text-xs px-2 py-1 h-auto",
                filterCategory === 'management' ? "bg-cyan-500/20 text-cyan-400" : "text-slate-400"
              )}
            >
              관리
            </Button>
          </div>
        </div>
      )}

      {/* 검색 결과 요약 */}
      {hasActiveFilters && (
        <div className="text-xs text-slate-400 mb-2">
          {filteredMenus.length}개 메뉴 발견
          {searchTerm && ` (검색어: "${searchTerm}")`}
          {filterCategory !== 'all' && ` (카테고리: ${filterCategory})`}
        </div>
      )}

      {/* 메뉴 액션 버튼 */}
      <div className="flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center space-x-2">
          <span>즐겨찾기:</span>
          <Button
            variant="ghost"
            size="sm"
            className="p-1 h-auto text-slate-400 hover:text-yellow-400"
            title="즐겨찾기 메뉴 관리"
          >
            <Star className="w-3 h-3" />
          </Button>
        </div>
        <div className="flex items-center space-x-2">
          <span>숨김:</span>
          <Button
            variant="ghost"
            size="sm"
            className="p-1 h-auto text-slate-400 hover:text-red-400"
            title="숨김 메뉴 관리"
          >
            <EyeOff className="w-3 h-3" />
          </Button>
        </div>
      </div>
    </div>
  );
}; 