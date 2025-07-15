'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Code, 
  FolderOpen, 
  Eye, 
  BarChart3, 
  Settings,
  Palette,
  GitBranch,
  Globe
} from 'lucide-react';

const ModuleDevelopmentNav = () => {
  const pathname = usePathname();

  const navItems = [
    {
      name: '대시보드',
      href: '/module-development/dashboard',
      icon: BarChart3,
      description: '개발 현황 및 통계'
    },
    {
      name: '프로젝트',
      href: '/module-development/projects',
      icon: FolderOpen,
      description: '프로젝트 관리'
    },
    {
      name: '편집기',
      href: '/module-development',
      icon: Code,
      description: '시각적 개발 도구'
    },
    {
      name: '미리보기',
      href: '/module-development/preview',
      icon: Eye,
      description: '실시간 미리보기'
    },
    {
      name: '컴포넌트',
      href: '/module-development/components',
      icon: Palette,
      description: '컴포넌트 라이브러리'
    },
    {
      name: '버전 관리',
      href: '/module-development/versions',
      icon: GitBranch,
      description: '버전 및 배포 관리'
    },
    {
      name: '마켓플레이스',
      href: '/module-development/marketplace',
      icon: Globe,
      description: '모듈 마켓플레이스'
    },
    {
      name: '설정',
      href: '/module-development/settings',
      icon: Settings,
      description: '개발 환경 설정'
    }
  ];

  return (
    <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link href="/module-development/dashboard" className="flex items-center">
                <Code className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                <span className="ml-2 text-xl font-bold text-gray-900 dark:text-white">
                  모듈 개발
                </span>
              </Link>
            </div>
            
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navItems.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                      isActive
                        ? 'border-blue-500 text-gray-900 dark:text-white'
                        : 'border-transparent text-gray-500 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-700 dark:hover:text-gray-300'
                    }`}
                    title={item.description}
                  >
                    <item.icon className="w-4 h-4 mr-1" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>
          
          <div className="hidden sm:ml-6 sm:flex sm:items-center">
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500 dark:text-gray-400">
                샌드박스 모드
              </span>
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>
      
      {/* 모바일 메뉴 */}
      <div className="sm:hidden">
        <div className="pt-2 pb-3 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`block pl-3 pr-4 py-2 border-l-4 text-base font-medium ${
                  isActive
                    ? 'bg-blue-50 dark:bg-blue-900 border-blue-500 text-blue-700 dark:text-blue-300'
                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-800 dark:hover:text-gray-200'
                }`}
              >
                <div className="flex items-center">
                  <item.icon className="w-4 h-4 mr-2" />
                  {item.name}
                </div>
                <p className="ml-6 text-sm text-gray-500 dark:text-gray-400">
                  {item.description}
                </p>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

export default ModuleDevelopmentNav; 