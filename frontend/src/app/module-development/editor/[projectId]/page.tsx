'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'next/navigation';
import { 
  Save, 
  Eye, 
  Play, 
  Settings, 
  Code, 
  Database, 
  History, 
  Download,
  Undo,
  Redo,
  Layers,
  Palette,
  Smartphone,
  Monitor,
  Moon,
  Sun,
  GitBranch,
  TestTube,
  Globe
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

const ProjectEditor = () => {
  const params = useParams();
  const projectId = params.projectId as string;
  
  const [project, setProject] = useState<Project | null>(null);
  const [components, setComponents] = useState<Component[]>([]);
  const [selectedComponent, setSelectedComponent] = useState<Component | null>(null);
  const [previewMode, setPreviewMode] = useState<'desktop' | 'mobile' | 'tablet'>('desktop');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [activeTab, setActiveTab] = useState<'properties' | 'code' | 'data' | 'versions'>('properties');
  const [loading, setLoading] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [history, setHistory] = useState<Component[][]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  
  const canvasRef = useRef<HTMLDivElement>(null);

  // 컴포넌트 라이브러리
  const componentLibrary = {
    basic: [
      { type: 'button', name: '버튼', icon: '🔘', category: 'basic' },
      { type: 'card', name: '카드', icon: '🃏', category: 'basic' },
      { type: 'form', name: '폼', icon: '📝', category: 'basic' },
      { type: 'input', name: '입력 필드', icon: '📝', category: 'basic' },
      { type: 'table', name: '테이블', icon: '📊', category: 'basic' },
    ],
    advanced: [
      { type: 'chart', name: '차트', icon: '📈', category: 'advanced' },
      { type: 'calendar', name: '캘린더', icon: '📅', category: 'advanced' },
      { type: 'modal', name: '모달', icon: '🪟', category: 'advanced' },
      { type: 'tabs', name: '탭', icon: '📑', category: 'advanced' },
      { type: 'carousel', name: '캐러셀', icon: '🎠', category: 'advanced' },
    ],
    layout: [
      { type: 'container', name: '컨테이너', icon: '📦', category: 'layout' },
      { type: 'grid', name: '그리드', icon: '⊞', category: 'layout' },
      { type: 'sidebar', name: '사이드바', icon: '📋', category: 'layout' },
      { type: 'header', name: '헤더', icon: '📄', category: 'layout' },
      { type: 'footer', name: '푸터', icon: '📄', category: 'layout' },
    ]
  };

  useEffect(() => {
    if (projectId) {
      loadProject();
      loadComponents();
    }
  }, [projectId]);

  const loadProject = async () => {
    try {
      const response = await fetch(`/api/module-development/projects/${projectId}`);
      const data = await response.json();
      
      if (data.success) {
        setProject(data.project);
      }
    } catch (error) {
      console.error('프로젝트 로드 실패:', error);
    }
  };

  const loadComponents = async () => {
    try {
      const response = await fetch(`/api/module-development/projects/${projectId}/components`);
      const data = await response.json();
      
      if (data.success) {
        setComponents(data.components || []);
        addToHistory(data.components || []);
      }
    } catch (error) {
      console.error('컴포넌트 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToHistory = (newComponents: Component[]) => {
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push([...newComponents]);
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
  };

  const undo = () => {
    if (historyIndex > 0) {
      setHistoryIndex(historyIndex - 1);
      setComponents([...history[historyIndex - 1]]);
    }
  };

  const redo = () => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex(historyIndex + 1);
      setComponents([...history[historyIndex + 1]]);
    }
  };

  const handleDragStart = (componentType: string) => {
    setIsDragging(true);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const componentType = e.dataTransfer.getData('componentType');
    const rect = canvasRef.current?.getBoundingClientRect();
    
    if (rect) {
      const position = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      };
      
      addComponentToCanvas(componentType, position);
    }
  };

  const addComponentToCanvas = (componentType: string, position: { x: number; y: number }) => {
    const newComponent: Component = {
      id: `component-${Date.now()}`,
      type: componentType,
      name: `${componentType} 컴포넌트`,
      position,
      size: { width: 200, height: 100 },
      properties: getDefaultProperties(componentType),
      styles: getDefaultStyles(componentType),
    };

    const newComponents = [...components, newComponent];
    setComponents(newComponents);
    setSelectedComponent(newComponent);
    addToHistory(newComponents);
  };

  const getDefaultProperties = (type: string) => {
    const defaults: Record<string, any> = {
      button: { text: '버튼', variant: 'primary', size: 'medium' },
      card: { title: '카드 제목', content: '카드 내용' },
      form: { title: '폼 제목', fields: [] },
      input: { placeholder: '입력하세요', type: 'text', label: '라벨' },
      table: { headers: ['컬럼1', '컬럼2', '컬럼3'], data: [['데이터1', '데이터2', '데이터3']] },
    };
    return defaults[type] || {};
  };

  const getDefaultStyles = (type: string) => {
    const defaults: Record<string, any> = {
      button: {
        backgroundColor: '#3498db',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        padding: '8px 16px',
        cursor: 'pointer'
      },
      card: {
        backgroundColor: 'white',
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '16px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      },
      form: {
        backgroundColor: 'white',
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '20px'
      },
      input: {
        border: '1px solid #ddd',
        borderRadius: '4px',
        padding: '8px 12px',
        width: '100%'
      },
      table: {
        width: '100%',
        borderCollapse: 'collapse',
        border: '1px solid #ddd'
      }
    };
    return defaults[type] || {};
  };

  const updateComponentProperty = (componentId: string, property: string, value: any) => {
    const newComponents = components.map(comp => 
      comp.id === componentId 
        ? { ...comp, properties: { ...comp.properties, [property]: value } }
        : comp
    );
    
    setComponents(newComponents);
    addToHistory(newComponents);
    
    if (selectedComponent?.id === componentId) {
      setSelectedComponent({
        ...selectedComponent,
        properties: { ...selectedComponent.properties, [property]: value }
      });
    }
  };

  const updateComponentStyle = (componentId: string, style: string, value: string) => {
    const newComponents = components.map(comp => 
      comp.id === componentId 
        ? { ...comp, styles: { ...comp.styles, [style]: value } }
        : comp
    );
    
    setComponents(newComponents);
    addToHistory(newComponents);
    
    if (selectedComponent?.id === componentId) {
      setSelectedComponent({
        ...selectedComponent,
        styles: { ...selectedComponent.styles, [style]: value }
      });
    }
  };

  const deleteComponent = (componentId: string) => {
    const newComponents = components.filter(comp => comp.id !== componentId);
    setComponents(newComponents);
    addToHistory(newComponents);
    
    if (selectedComponent?.id === componentId) {
      setSelectedComponent(null);
    }
  };

  const saveProject = async () => {
    try {
      // 컴포넌트 저장
      for (const component of components) {
        await fetch(`/api/module-development/projects/${projectId}/components/${component.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: component.name,
            position: component.position,
            size: component.size,
            properties: component.properties,
            styles: component.styles
          }),
        });
      }
      
      alert('프로젝트가 저장되었습니다.');
    } catch (error) {
      console.error('저장 실패:', error);
      alert('저장 중 오류가 발생했습니다.');
    }
  };

  const testProject = async () => {
    try {
      const response = await fetch(`/api/module-development/projects/${projectId}/test-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data_type: 'sample'
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        alert('테스트 데이터가 생성되었습니다.');
        window.open(`/module-development/preview/${projectId}`, '_blank');
      }
    } catch (error) {
      console.error('테스트 실패:', error);
      alert('테스트 중 오류가 발생했습니다.');
    }
  };

  const deployProject = async () => {
    try {
      const response = await fetch(`/api/module-development/projects/${projectId}/deploy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          version_id: 'latest',
          environment: 'marketplace',
          deployed_by: 'current_user'
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        alert('프로젝트가 성공적으로 배포되었습니다.');
      } else {
        alert('배포 실패: ' + data.error);
      }
    } catch (error) {
      console.error('배포 실패:', error);
      alert('배포 중 오류가 발생했습니다.');
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
      cursor: 'pointer',
      border: selectedComponent?.id === component.id ? '2px solid #3498db' : '1px solid #ddd'
    };

    switch (component.type) {
      case 'button':
        return (
          <button
            key={component.id}
            style={style}
            onClick={() => setSelectedComponent(component)}
          >
            {component.properties.text || '버튼'}
          </button>
        );
      case 'card':
        return (
          <div
            key={component.id}
            style={style}
            onClick={() => setSelectedComponent(component)}
          >
            <h3>{component.properties.title || '카드 제목'}</h3>
            <p>{component.properties.content || '카드 내용'}</p>
          </div>
        );
      case 'input':
        return (
          <div key={component.id} style={style} onClick={() => setSelectedComponent(component)}>
            <label>{component.properties.label || '라벨'}</label>
            <input
              type={component.properties.type || 'text'}
              placeholder={component.properties.placeholder || '입력하세요'}
              style={{ width: '100%', marginTop: '4px' }}
            />
          </div>
        );
      default:
        return (
          <div
            key={component.id}
            style={style}
            onClick={() => setSelectedComponent(component)}
          >
            {component.name}
          </div>
        );
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
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
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* 좌측: 컴포넌트 팔레트 */}
      <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">컴포넌트 팔레트</h2>
        </div>
        
        <div className="p-4 space-y-4">
          {Object.entries(componentLibrary).map(([category, items]) => (
            <div key={category}>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 capitalize">
                {category}
              </h3>
              <div className="space-y-2">
                {items.map((item) => (
                  <div
                    key={item.type}
                    className="flex items-center p-2 bg-gray-50 dark:bg-gray-700 rounded cursor-move hover:bg-gray-100 dark:hover:bg-gray-600"
                    draggable
                    onDragStart={(e) => {
                      e.dataTransfer.setData('componentType', item.type);
                      handleDragStart(item.type);
                    }}
                  >
                    <span className="mr-2">{item.icon}</span>
                    <span className="text-sm text-gray-700 dark:text-gray-300">{item.name}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 중앙: 캔버스 */}
      <div className="flex-1 flex flex-col">
        {/* 툴바 */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
                {project.name} - 편집기
              </h1>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={undo}
                  disabled={historyIndex <= 0}
                  className="p-2 rounded bg-gray-100 dark:bg-gray-700 disabled:opacity-50"
                  title="실행 취소"
                >
                  <Undo className="w-4 h-4" />
                </button>
                <button
                  onClick={redo}
                  disabled={historyIndex >= history.length - 1}
                  className="p-2 rounded bg-gray-100 dark:bg-gray-700 disabled:opacity-50"
                  title="다시 실행"
                >
                  <Redo className="w-4 h-4" />
                </button>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setPreviewMode('desktop')}
                  className={`p-2 rounded ${previewMode === 'desktop' ? 'bg-blue-100 dark:bg-blue-900' : 'bg-gray-100 dark:bg-gray-700'}`}
                >
                  <Monitor className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setPreviewMode('tablet')}
                  className={`p-2 rounded ${previewMode === 'tablet' ? 'bg-blue-100 dark:bg-blue-900' : 'bg-gray-100 dark:bg-gray-700'}`}
                >
                  <Layers className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setPreviewMode('mobile')}
                  className={`p-2 rounded ${previewMode === 'mobile' ? 'bg-blue-100 dark:bg-blue-900' : 'bg-gray-100 dark:bg-gray-700'}`}
                >
                  <Smartphone className="w-4 h-4" />
                </button>
              </div>
              
              <button
                onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
                className="p-2 rounded bg-gray-100 dark:bg-gray-700"
              >
                {theme === 'light' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
              </button>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={saveProject}
                className="flex items-center px-3 py-2 bg-blue-500 text-white rounded-md text-sm"
              >
                <Save className="w-4 h-4 mr-1" />
                저장
              </button>
              <button
                onClick={testProject}
                className="flex items-center px-3 py-2 bg-green-500 text-white rounded-md text-sm"
              >
                <TestTube className="w-4 h-4 mr-1" />
                테스트
              </button>
              <button
                onClick={deployProject}
                className="flex items-center px-3 py-2 bg-purple-500 text-white rounded-md text-sm"
              >
                <Globe className="w-4 h-4 mr-1" />
                배포
              </button>
            </div>
          </div>
        </div>

        {/* 캔버스 */}
        <div className="flex-1 p-4 overflow-auto">
          <div
            ref={canvasRef}
            className={`
              relative bg-white dark:bg-gray-800 border-2 border-dashed border-gray-300 dark:border-gray-600
              ${previewMode === 'mobile' ? 'max-w-sm mx-auto' : ''}
              ${previewMode === 'tablet' ? 'max-w-2xl mx-auto' : ''}
              ${previewMode === 'desktop' ? 'w-full' : ''}
              h-full min-h-[600px]
            `}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
          >
            {components.map(component => renderComponent(component))}
          </div>
        </div>
      </div>

      {/* 우측: 속성 패널 */}
      <div className="w-80 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">속성 편집</h2>
        </div>
        
        <div className="p-4">
          <div className="flex space-x-1 mb-4">
            <button
              onClick={() => setActiveTab('properties')}
              className={`flex-1 px-3 py-2 text-sm rounded ${activeTab === 'properties' ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' : 'bg-gray-100 dark:bg-gray-700'}`}
            >
              <Palette className="w-4 h-4 mr-1" />
              속성
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={`flex-1 px-3 py-2 text-sm rounded ${activeTab === 'code' ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' : 'bg-gray-100 dark:bg-gray-700'}`}
            >
              <Code className="w-4 h-4 mr-1" />
              코드
            </button>
            <button
              onClick={() => setActiveTab('data')}
              className={`flex-1 px-3 py-2 text-sm rounded ${activeTab === 'data' ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' : 'bg-gray-100 dark:bg-gray-700'}`}
            >
              <Database className="w-4 h-4 mr-1" />
              데이터
            </button>
            <button
              onClick={() => setActiveTab('versions')}
              className={`flex-1 px-3 py-2 text-sm rounded ${activeTab === 'versions' ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' : 'bg-gray-100 dark:bg-gray-700'}`}
            >
              <History className="w-4 h-4 mr-1" />
              버전
            </button>
          </div>

          {selectedComponent ? (
            <div className="space-y-4">
              {activeTab === 'properties' && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    컴포넌트 속성
                  </h3>
                  <div className="space-y-3">
                    {Object.entries(selectedComponent.properties).map(([key, value]) => (
                      <div key={key}>
                        <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                          {key}
                        </label>
                        <input
                          type="text"
                          value={value as string}
                          onChange={(e) => updateComponentProperty(selectedComponent.id, key, e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                        />
                      </div>
                    ))}
                  </div>
                  
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 mt-4">
                    스타일
                  </h3>
                  <div className="space-y-3">
                    {Object.entries(selectedComponent.styles).map(([key, value]) => (
                      <div key={key}>
                        <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                          {key}
                        </label>
                        <input
                          type="text"
                          value={value as string}
                          onChange={(e) => updateComponentStyle(selectedComponent.id, key, e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                        />
                      </div>
                    ))}
                  </div>
                  
                  <button
                    onClick={() => deleteComponent(selectedComponent.id)}
                    className="w-full mt-4 px-3 py-2 bg-red-500 text-white rounded-md text-sm"
                  >
                    컴포넌트 삭제
                  </button>
                </div>
              )}
              
              {activeTab === 'code' && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    HTML 코드
                  </h3>
                  <textarea
                    className="w-full h-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white text-sm font-mono"
                    value={`<${selectedComponent.type}>\n  ${selectedComponent.properties.text || ''}\n</${selectedComponent.type}>`}
                    readOnly
                  />
                  
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 mt-4">
                    CSS 스타일
                  </h3>
                  <textarea
                    className="w-full h-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white text-sm font-mono"
                    value={Object.entries(selectedComponent.styles).map(([key, value]) => `  ${key}: ${value};`).join('\n')}
                    readOnly
                  />
                </div>
              )}
              
              {activeTab === 'data' && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    테스트 데이터
                  </h3>
                  <button className="w-full px-3 py-2 bg-blue-500 text-white rounded-md text-sm mb-3">
                    <Database className="w-4 h-4 mr-1 inline" />
                    샘플 데이터 생성
                  </button>
                  <button className="w-full px-3 py-2 bg-gray-500 text-white rounded-md text-sm">
                    <TestTube className="w-4 h-4 mr-1 inline" />
                    데이터 리셋
                  </button>
                </div>
              )}
              
              {activeTab === 'versions' && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    버전 관리
                  </h3>
                  <button className="w-full px-3 py-2 bg-green-500 text-white rounded-md text-sm mb-3">
                    <GitBranch className="w-4 h-4 mr-1 inline" />
                    스냅샷 생성
                  </button>
                  <div className="space-y-2">
                    <div className="p-2 bg-gray-50 dark:bg-gray-700 rounded text-xs">
                      <div className="font-medium">v1.0.0</div>
                      <div className="text-gray-500">2024-01-15 14:30</div>
                    </div>
                    <div className="p-2 bg-gray-50 dark:bg-gray-700 rounded text-xs">
                      <div className="font-medium">v0.9.0</div>
                      <div className="text-gray-500">2024-01-14 16:20</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center text-gray-500 dark:text-gray-400 py-8">
              <Palette className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>컴포넌트를 선택하여 속성을 편집하세요</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectEditor; 