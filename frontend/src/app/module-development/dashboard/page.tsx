'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Plus, 
  Code, 
  Play, 
  Globe, 
  TrendingUp, 
  Users, 
  Clock, 
  Star,
  ArrowRight,
  Settings,
  Database,
  GitBranch,
  Download,
  Upload,
  BarChart3,
  Calendar,
  Activity,
  Zap
} from 'lucide-react';

interface Project {
  id: string;
  name: string;
  description: string;
  module_type: string;
  status: 'development' | 'testing' | 'deployed';
  version: string;
  created_at: string;
  updated_at: string;
  created_by: string;
}

interface DashboardStats {
  total_projects: number;
  development_projects: number;
  testing_projects: number;
  deployed_projects: number;
  total_components: number;
  total_deployments: number;
  active_users: number;
  recent_activity: number;
}

interface RecentActivity {
  id: string;
  type: 'project_created' | 'project_deployed' | 'component_added' | 'version_created';
  project_name: string;
  user: string;
  timestamp: string;
  description: string;
}

const ModuleDevelopmentDashboard = () => {
  const [stats, setStats] = useState<DashboardStats>({
    total_projects: 0,
    development_projects: 0,
    testing_projects: 0,
    deployed_projects: 0,
    total_components: 0,
    total_deployments: 0,
    active_users: 0,
    recent_activity: 0
  });
  const [recentProjects, setRecentProjects] = useState<Project[]>([]);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // 통계 데이터 로드
      const statsResponse = await fetch('/api/module-development/statistics');
      const statsData = await statsResponse.json();
      
      if (statsData.success) {
        setStats(statsData.statistics);
      }
      
      // 최근 프로젝트 로드
      const projectsResponse = await fetch('/api/module-development/projects?limit=5');
      const projectsData = await projectsResponse.json();
      
      if (projectsData.success) {
        setRecentProjects(projectsData.projects.slice(0, 5));
      }
      
      // 최근 활동 로드 (실제로는 별도 API 필요)
      setRecentActivity([
        {
          id: '1',
          type: 'project_created',
          project_name: '샘플 프로젝트',
          user: '개발자1',
          timestamp: '2024-01-15T14:30:00Z',
          description: '새 프로젝트를 생성했습니다.'
        },
        {
          id: '2',
          type: 'project_deployed',
          project_name: '대시보드 모듈',
          user: '개발자2',
          timestamp: '2024-01-15T13:20:00Z',
          description: '프로젝트를 마켓플레이스에 배포했습니다.'
        },
        {
          id: '3',
          type: 'component_added',
          project_name: '폼 모듈',
          user: '개발자3',
          timestamp: '2024-01-15T12:15:00Z',
          description: '새 컴포넌트를 추가했습니다.'
        }
      ]);
      
    } catch (error) {
      console.error('대시보드 데이터 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'development':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'testing':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      case 'deployed':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'development':
        return '개발중';
      case 'testing':
        return '테스트중';
      case 'deployed':
        return '배포완료';
      default:
        return status;
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'project_created':
        return <Plus className="w-4 h-4" />;
      case 'project_deployed':
        return <Globe className="w-4 h-4" />;
      case 'component_added':
        return <Code className="w-4 h-4" />;
      case 'version_created':
        return <GitBranch className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'project_created':
        return 'text-green-600 bg-green-100 dark:bg-green-900';
      case 'project_deployed':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900';
      case 'component_added':
        return 'text-purple-600 bg-purple-100 dark:bg-purple-900';
      case 'version_created':
        return 'text-orange-600 bg-orange-100 dark:bg-orange-900';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-700';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">모듈 개발 대시보드</h1>
          <p className="text-gray-600 dark:text-gray-400">샌드박스 환경에서 모듈을 개발하고 관리하세요</p>
        </div>
        <div className="flex space-x-3">
          <Link
            href="/module-development/projects"
            className="flex items-center px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            <Settings className="w-4 h-4 mr-2" />
            프로젝트 관리
          </Link>
          <Link
            href="/module-development"
            className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            <Plus className="w-4 h-4 mr-2" />
            새 프로젝트
          </Link>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <Code className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">전체 프로젝트</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_projects}</p>
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-green-600 dark:text-green-400">
            <TrendingUp className="w-4 h-4 mr-1" />
            +12% 이번 달
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg">
              <Globe className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">배포된 모듈</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.deployed_projects}</p>
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-green-600 dark:text-green-400">
            <TrendingUp className="w-4 h-4 mr-1" />
            +8% 이번 주
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <Database className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">총 컴포넌트</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_components}</p>
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-green-600 dark:text-green-400">
            <TrendingUp className="w-4 h-4 mr-1" />
            +15% 이번 달
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-orange-100 dark:bg-orange-900 rounded-lg">
              <Users className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">활성 개발자</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.active_users}</p>
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-green-600 dark:text-green-400">
            <TrendingUp className="w-4 h-4 mr-1" />
            +5% 이번 주
          </div>
        </div>
      </div>

      {/* 빠른 액션 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link
          href="/module-development"
          className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <Plus className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-3">
              <h3 className="font-medium text-gray-900 dark:text-white">새 프로젝트</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">빈 프로젝트부터 시작</p>
            </div>
          </div>
        </Link>
        
        <Link
          href="/module-development/templates"
          className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <Download className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-3">
              <h3 className="font-medium text-gray-900 dark:text-white">템플릿 사용</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">기존 템플릿으로 시작</p>
            </div>
          </div>
        </Link>
        
        <Link
          href="/module-development/import"
          className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <Upload className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="ml-3">
              <h3 className="font-medium text-gray-900 dark:text-white">프로젝트 가져오기</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">기존 프로젝트 불러오기</p>
            </div>
          </div>
        </Link>
        
        <Link
          href="/module-development/marketplace"
          className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
              <Star className="w-5 h-5 text-orange-600 dark:text-orange-400" />
            </div>
            <div className="ml-3">
              <h3 className="font-medium text-gray-900 dark:text-white">마켓플레이스</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">모듈 탐색 및 설치</p>
            </div>
          </div>
        </Link>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 최근 프로젝트 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">최근 프로젝트</h2>
              <Link
                href="/module-development/projects"
                className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 text-sm flex items-center"
              >
                모두 보기
                <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
            </div>
          </div>
          
          <div className="p-6">
            {recentProjects.length === 0 ? (
              <div className="text-center py-8">
                <Code className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">프로젝트가 없습니다.</p>
                <Link
                  href="/module-development"
                  className="mt-4 inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  첫 번째 프로젝트 생성
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {recentProjects.map((project) => (
                  <div
                    key={project.id}
                    className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <h3 className="font-medium text-gray-900 dark:text-white">
                          {project.name}
                        </h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(project.status)}`}>
                          {getStatusText(project.status)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{project.description}</p>
                      <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
                        <span className="flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {new Date(project.updated_at).toLocaleDateString()}
                        </span>
                        <span className="flex items-center">
                          <GitBranch className="w-3 h-3 mr-1" />
                          v{project.version}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Link
                        href={`/module-development/editor/${project.id}`}
                        className="p-2 text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900 rounded-lg"
                        title="편집"
                      >
                        <Code className="w-4 h-4" />
                      </Link>
                      <Link
                        href={`/module-development/preview/${project.id}`}
                        className="p-2 text-green-600 hover:bg-green-100 dark:hover:bg-green-900 rounded-lg"
                        title="미리보기"
                      >
                        <Play className="w-4 h-4" />
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 최근 활동 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">최근 활동</h2>
              <Link
                href="/module-development/activity"
                className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 text-sm flex items-center"
              >
                모두 보기
                <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
            </div>
          </div>
          
          <div className="p-6">
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3">
                  <div className={`p-2 rounded-lg ${getActivityColor(activity.type)}`}>
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900 dark:text-white">
                      <span className="font-medium">{activity.user}</span>님이{' '}
                      <span className="font-medium">{activity.project_name}</span>에서{' '}
                      {activity.description}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {new Date(activity.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 성능 통계 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">개발 성능 통계</h2>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                {Math.round((stats.deployed_projects / Math.max(stats.total_projects, 1)) * 100)}%
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">배포 성공률</p>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-2">
                {Math.round(stats.total_components / Math.max(stats.total_projects, 1))}
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">프로젝트당 평균 컴포넌트</p>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-2">
                {stats.recent_activity}
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">이번 주 활동</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModuleDevelopmentDashboard; 