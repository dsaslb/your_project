'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Download, 
  Share, 
  Settings,
  Smartphone,
  Monitor,
  Moon,
  Sun,
  Fullscreen,
  Maximize2,
  Minimize2
} from 'lucide-react';

interface Component {
  id: string;
  type: string;
  name: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
  properties: Record<string, any>;
  styles: Record<string, any>;
  children?: Component[];
}

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

interface TestData {
  [key: string]: any;
}

const ProjectPreview = () => {
  const params = useParams();
  const projectId = params.projectId as string;
  
  const [project, setProject] = useState<Project | null>(null);
  const [components, setComponents] = useState<Component[]>([]);
  const [testData, setTestData] = useState<TestData>({});
  const [previewMode, setPreviewMode] = useState<'desktop' | 'mobile' | 'tablet'>('desktop');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (projectId) {
      loadProjectPreview();
    }
  }, [projectId]);

  const loadProjectPreview = async () => {
    try {
      setLoading(true);
      
      // 프로젝트 정보 로드
      const projectResponse = await fetch(`/api/module-development/projects/${projectId}`);
      const projectData = await projectResponse.json();
      
      if (projectData.success) {
        setProject(projectData.project);
      }
      
      // 컴포넌트 로드
      const componentsResponse = await fetch(`/api/module-development/projects/${projectId}/components`);
      const componentsData = await componentsResponse.json();
      
      if (componentsData.success) {
        setComponents(componentsData.components || []);
      }
      
      // 테스트 데이터 로드
      const testDataResponse = await fetch(`/api/module-development/projects/${projectId}/test-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data_type: 'sample'
        }),
      });
      
      const testDataResult = await testDataResponse.json();
      
      if (testDataResult.success) {
        setTestData(testDataResult.test_data || {});
      }
      
    } catch (error) {
      console.error('미리보기 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const resetPreview = () => {
    loadProjectPreview();
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const sharePreview = () => {
    const url = window.location.href;
    if (navigator.share) {
      navigator.share({
        title: project?.name || '프로젝트 미리보기',
        url: url
      });
    } else {
      navigator.clipboard.writeText(url);
      alert('링크가 클립보드에 복사되었습니다.');
    }
  };

  const downloadPreview = () => {
    // 미리보기 스크린샷 다운로드 로직
    const canvas = document.createElement('canvas');
    const previewElement = document.getElementById('preview-container');
    
    if (previewElement) {
      // HTML2Canvas를 사용하여 스크린샷 생성
      // 실제 구현에서는 html2canvas 라이브러리 사용
      alert('스크린샷 다운로드 기능은 준비 중입니다.');
    }
  };

  const renderComponent = (component: Component) => {
    const style = {
      position: 'absolute' as const,
      left: component.position.x,
      top: component.position.y,
      width: component.size.width,
      height: component.size.height,
      ...component.styles,
    };

    // 테스트 데이터 적용
    const getTestValue = (key: string, defaultValue: any) => {
      return testData[key] || defaultValue;
    };

    switch (component.type) {
      case 'button':
        return (
          <button
            key={component.id}
            style={style}
            onClick={() => {
              if (component.properties.onClick) {
                // 동적 이벤트 처리
                console.log('버튼 클릭:', component.properties.onClick);
              }
            }}
          >
            {getTestValue('buttonText', component.properties.text || '버튼')}
          </button>
        );
        
      case 'card':
        return (
          <div key={component.id} style={style}>
            <h3>{getTestValue('cardTitle', component.properties.title || '카드 제목')}</h3>
            <p>{getTestValue('cardContent', component.properties.content || '카드 내용')}</p>
          </div>
        );
        
      case 'input':
        return (
          <div key={component.id} style={style}>
            <label>{getTestValue('inputLabel', component.properties.label || '라벨')}</label>
            <input
              type={component.properties.type || 'text'}
              placeholder={getTestValue('inputPlaceholder', component.properties.placeholder || '입력하세요')}
              defaultValue={getTestValue('inputValue', '')}
              style={{ width: '100%', marginTop: '4px' }}
            />
          </div>
        );
        
      case 'table':
        const headers = getTestValue('tableHeaders', component.properties.headers || ['컬럼1', '컬럼2', '컬럼3']);
        const data = getTestValue('tableData', component.properties.data || [['데이터1', '데이터2', '데이터3']]);
        
        return (
          <table key={component.id} style={style}>
            <thead>
              <tr>
                {headers.map((header: string, index: number) => (
                  <th key={index} style={{ border: '1px solid #ddd', padding: '8px' }}>
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row: string[], rowIndex: number) => (
                <tr key={rowIndex}>
                  {row.map((cell: string, cellIndex: number) => (
                    <td key={cellIndex} style={{ border: '1px solid #ddd', padding: '8px' }}>
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        );
        
      case 'chart':
        return (
          <div key={component.id} style={style}>
            <h4>차트 컴포넌트</h4>
            <p>차트 데이터: {JSON.stringify(getTestValue('chartData', component.properties.data))}</p>
          </div>
        );
        
      case 'calendar':
        return (
          <div key={component.id} style={style}>
            <h4>캘린더 컴포넌트</h4>
            <p>이벤트: {JSON.stringify(getTestValue('calendarEvents', component.properties.events || []))}</p>
          </div>
        );
        
      default:
        return (
          <div key={component.id} style={style}>
            {component.name}
          </div>
        );
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="p-6">
        <p className="text-red-500">프로젝트를 찾을 수 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
      {/* 헤더 */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
              {project.name} - 미리보기
            </h1>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setPreviewMode('desktop')}
                className={`p-2 rounded ${previewMode === 'desktop' ? 'bg-blue-100 dark:bg-blue-900' : 'bg-gray-100 dark:bg-gray-700'}`}
                title="데스크탑"
              >
                <Monitor className="w-4 h-4" />
              </button>
              <button
                onClick={() => setPreviewMode('tablet')}
                className={`p-2 rounded ${previewMode === 'tablet' ? 'bg-blue-100 dark:bg-blue-900' : 'bg-gray-100 dark:bg-gray-700'}`}
                title="태블릿"
              >
                <Maximize2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setPreviewMode('mobile')}
                className={`p-2 rounded ${previewMode === 'mobile' ? 'bg-blue-100 dark:bg-blue-900' : 'bg-gray-100 dark:bg-gray-700'}`}
                title="모바일"
              >
                <Smartphone className="w-4 h-4" />
              </button>
            </div>
            
            <button
              onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
              className="p-2 rounded bg-gray-100 dark:bg-gray-700"
              title="테마 변경"
            >
              {theme === 'light' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
            </button>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="flex items-center px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md text-sm"
              title={isPlaying ? '일시정지' : '재생'}
            >
              {isPlaying ? <Pause className="w-4 h-4 mr-1" /> : <Play className="w-4 h-4 mr-1" />}
              {isPlaying ? '일시정지' : '재생'}
            </button>
            
            <button
              onClick={resetPreview}
              className="flex items-center px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md text-sm"
              title="리셋"
            >
              <RotateCcw className="w-4 h-4 mr-1" />
              리셋
            </button>
            
            <button
              onClick={downloadPreview}
              className="flex items-center px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md text-sm"
              title="다운로드"
            >
              <Download className="w-4 h-4 mr-1" />
              다운로드
            </button>
            
            <button
              onClick={sharePreview}
              className="flex items-center px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md text-sm"
              title="공유"
            >
              <Share className="w-4 h-4 mr-1" />
              공유
            </button>
            
            <button
              onClick={toggleFullscreen}
              className="flex items-center px-3 py-2 bg-blue-500 text-white rounded-md text-sm"
              title="전체화면"
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4 mr-1" /> : <Fullscreen className="w-4 h-4 mr-1" />}
              {isFullscreen ? '종료' : '전체화면'}
            </button>
          </div>
        </div>
      </div>

      {/* 미리보기 컨테이너 */}
      <div className="flex-1 p-4 overflow-auto">
        <div className="flex justify-center">
          <div
            id="preview-container"
            className={`
              relative bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg
              ${previewMode === 'mobile' ? 'w-80 h-[600px]' : ''}
              ${previewMode === 'tablet' ? 'w-2xl h-[800px]' : ''}
              ${previewMode === 'desktop' ? 'w-full max-w-6xl h-[800px]' : ''}
              overflow-hidden
            `}
          >
            {/* 미리보기 헤더 */}
            <div className="bg-gray-100 dark:bg-gray-700 px-4 py-2 border-b border-gray-200 dark:border-gray-600">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                </div>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {project.name} - 미리보기
                </span>
                <div className="w-16"></div>
              </div>
            </div>

            {/* 실제 미리보기 영역 */}
            <div className="p-4 h-full overflow-auto">
              {components.length === 0 ? (
                <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
                  <div className="text-center">
                    <Settings className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>컴포넌트가 없습니다.</p>
                    <p className="text-sm">편집기에서 컴포넌트를 추가해주세요.</p>
                  </div>
                </div>
              ) : (
                <div className="relative w-full h-full">
                  {components.map(component => renderComponent(component))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 하단 정보 패널 */}
      <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center space-x-4">
            <span>프로젝트: {project.name}</span>
            <span>버전: {project.version}</span>
            <span>상태: {project.status}</span>
          </div>
          <div className="flex items-center space-x-4">
            <span>컴포넌트: {components.length}개</span>
            <span>테스트 데이터: {Object.keys(testData).length}개</span>
            <span>미리보기 모드: {previewMode}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectPreview; 