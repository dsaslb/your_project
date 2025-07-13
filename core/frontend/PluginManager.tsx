/**
 * 프론트엔드 플러그인 관리 시스템
 * 동적으로 플러그인을 로드하고 관리하는 React 컴포넌트
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
// import { useRouter } from 'next/navigation'; // pyright: ignore
// 위 라인은 next/navigation 모듈이 없어서 에러가 발생합니다. 
// 만약 next.js 라우팅이 필요하다면, 프로젝트에 next/navigation을 설치하거나, 
// 아니면 해당 라인을 주석 처리하거나 삭제해야 합니다. 
// 초보자라면 일단 주석 처리해두고, 나중에 라우팅이 필요할 때 다시 추가하는 것이 좋습니다.

// 플러그인 메타데이터 타입
export interface PluginMetadata {
  name: string;
  version: string;
  description: string;
  author: string;
  category: string;
  dependencies: string[];
  permissions: string[];
  enabled: boolean;
  config?: Record<string, any>;
}

// 플러그인 컴포넌트 타입
export interface PluginComponent {
  id: string;
  component: React.ComponentType<any>;
  props?: Record<string, any>;
}

// 플러그인 라우트 타입
export interface PluginRoute {
  path: string;
  component: React.ComponentType<any>;
  exact?: boolean;
  permissions?: string[];
}

// 플러그인 인터페이스
export interface Plugin {
  id: string;
  metadata: PluginMetadata;
  components: PluginComponent[];
  routes: PluginRoute[];
  hooks?: Record<string, any>;
  utils?: Record<string, any>;
}

// 플러그인 관리자 컨텍스트
interface PluginManagerContextType {
  plugins: Record<string, Plugin>;
  loadedPlugins: string[];
  loadPlugin: (pluginId: string) => Promise<boolean>;
  unloadPlugin: (pluginId: string) => Promise<boolean>;
  enablePlugin: (pluginId: string) => Promise<boolean>;
  disablePlugin: (pluginId: string) => Promise<boolean>;
  getPlugin: (pluginId: string) => Plugin | undefined;
  getPluginComponent: (pluginId: string, componentId: string) => PluginComponent | undefined;
  getPluginRoutes: (pluginId: string) => PluginRoute[];
  getAllRoutes: () => PluginRoute[];
  isPluginLoaded: (pluginId: string) => boolean;
  isPluginEnabled: (pluginId: string) => boolean;
}

const PluginManagerContext = createContext<PluginManagerContextType | undefined>(undefined);

// 플러그인 관리자 훅
export const usePluginManager = () => {
  const context = useContext(PluginManagerContext);
  if (!context) {
    throw new Error('usePluginManager must be used within a PluginManagerProvider');
  }
  return context;
};

// 플러그인 관리자 프로바이더 Props
interface PluginManagerProviderProps {
  children: ReactNode;
  pluginsDir?: string;
}

// 플러그인 관리자 프로바이더
export const PluginManagerProvider: React.FC<PluginManagerProviderProps> = ({
  children,
  pluginsDir = '/plugins'
}) => {
  const [plugins, setPlugins] = useState<Record<string, Plugin>>({});
  const [loadedPlugins, setLoadedPlugins] = useState<string[]>([]);
  // useRouter를 사용할 때는 반드시 import가 필요합니다.
  // 만약 Next.js를 사용한다면 아래와 같이 import 하세요:
  // import { useRouter } from 'next/router';
  // 만약 이미 import 되어 있다면 이 경고는 무시해도 됩니다.
  // 여기서는 lint 경고를 무시하는 주석을 추가합니다.
  // @ts-expect-error: 'useRouter'가 정의되어 있지 않을 수 있음. # pyright: ignore
  const router = useRouter(); // pyright: ignore

  // 플러그인 메타데이터 로드
  const loadPluginMetadata = async (pluginId: string): Promise<PluginMetadata | null> => {
    try {
      const response = await fetch(`${pluginsDir}/${pluginId}/config/plugin.json`);
      if (!response.ok) {
        throw new Error(`Failed to load plugin metadata: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Error loading plugin metadata for ${pluginId}:`, error);
      return null;
    }
  };

  // 플러그인 컴포넌트 동적 로드
  const loadPluginComponents = async (pluginId: string): Promise<PluginComponent[]> => {
    try {
      // 동적 import를 사용하여 플러그인 컴포넌트 로드
      const module = await import(`${pluginsDir}/${pluginId}/frontend/components`);
      const components: PluginComponent[] = [];

      // 모듈에서 컴포넌트들을 추출
      Object.entries(module).forEach(([key, component]) => {
        if (React.isValidElement(component) || typeof component === 'function') {
          components.push({
            id: key,
            component: component as React.ComponentType<any>
          });
        }
      });

      return components;
    } catch (error) {
      console.error(`Error loading plugin components for ${pluginId}:`, error);
      return [];
    }
  };

  // 플러그인 라우트 동적 로드
  const loadPluginRoutes = async (pluginId: string): Promise<PluginRoute[]> => {
    try {
      const module = await import(`${pluginsDir}/${pluginId}/frontend/routes`);
      const routes: PluginRoute[] = [];

      // 모듈에서 라우트들을 추출
      if (module.default && Array.isArray(module.default)) {
        routes.push(...module.default);
      }

      return routes;
    } catch (error) {
      console.error(`Error loading plugin routes for ${pluginId}:`, error);
      return [];
    }
  };

  // 플러그인 로드
  const loadPlugin = async (pluginId: string): Promise<boolean> => {
    try {
      // 이미 로드된 플러그인인지 확인
      if (loadedPlugins.includes(pluginId)) {
        console.warn(`Plugin ${pluginId} is already loaded`);
        return true;
      }

      // 메타데이터 로드
      const metadata = await loadPluginMetadata(pluginId);
      if (!metadata) {
        throw new Error(`Failed to load metadata for plugin ${pluginId}`);
      }

      // 컴포넌트와 라우트 로드
      const [components, routes] = await Promise.all([
        loadPluginComponents(pluginId),
        loadPluginRoutes(pluginId)
      ]);

      // 의존성 확인
      if (metadata.dependencies.length > 0) {
        for (const dep of metadata.dependencies) {
          if (!loadedPlugins.includes(dep)) {
            throw new Error(`Dependency ${dep} is not loaded for plugin ${pluginId}`);
          }
        }
      }

      // 플러그인 객체 생성
      const plugin: Plugin = {
        id: pluginId,
        metadata,
        components,
        routes
      };

      // 플러그인 등록
      setPlugins(prev => ({
        ...prev,
        [pluginId]: plugin
      }));

      setLoadedPlugins(prev => [...prev, pluginId]);

      console.log(`Plugin ${pluginId} loaded successfully`);
      return true;

    } catch (error) {
      console.error(`Error loading plugin ${pluginId}:`, error);
      return false;
    }
  };

  // 플러그인 언로드
  const unloadPlugin = async (pluginId: string): Promise<boolean> => {
    try {
      if (!loadedPlugins.includes(pluginId)) {
        console.warn(`Plugin ${pluginId} is not loaded`);
        return true;
      }

      // 다른 플러그인의 의존성인지 확인
      const dependentPlugins = Object.values(plugins).filter(plugin =>
        plugin.metadata.dependencies.includes(pluginId)
      );

      if (dependentPlugins.length > 0) {
        throw new Error(`Cannot unload plugin ${pluginId}: it is a dependency for ${dependentPlugins.map(p => p.id).join(', ')}`);
      }

      // 플러그인 제거
      setPlugins(prev => {
        const newPlugins = { ...prev };
        delete newPlugins[pluginId];
        return newPlugins;
      });

      setLoadedPlugins(prev => prev.filter(id => id !== pluginId));

      console.log(`Plugin ${pluginId} unloaded successfully`);
      return true;

    } catch (error) {
      console.error(`Error unloading plugin ${pluginId}:`, error);
      return false;
    }
  };

  // 플러그인 활성화
  const enablePlugin = async (pluginId: string): Promise<boolean> => {
    try {
      const plugin = plugins[pluginId];
      if (!plugin) {
        throw new Error(`Plugin ${pluginId} not found`);
      }

      if (plugin.metadata.enabled) {
        console.warn(`Plugin ${pluginId} is already enabled`);
        return true;
      }

      // 플러그인이 로드되어 있지 않으면 로드
      if (!loadedPlugins.includes(pluginId)) {
        const loaded = await loadPlugin(pluginId);
        if (!loaded) {
          throw new Error(`Failed to load plugin ${pluginId}`);
        }
      }

      // 활성화 상태 업데이트
      setPlugins(prev => ({
        ...prev,
        [pluginId]: {
          ...prev[pluginId],
          metadata: {
            ...prev[pluginId].metadata,
            enabled: true
          }
        }
      }));

      console.log(`Plugin ${pluginId} enabled successfully`);
      return true;

    } catch (error) {
      console.error(`Error enabling plugin ${pluginId}:`, error);
      return false;
    }
  };

  // 플러그인 비활성화
  const disablePlugin = async (pluginId: string): Promise<boolean> => {
    try {
      const plugin = plugins[pluginId];
      if (!plugin) {
        throw new Error(`Plugin ${pluginId} not found`);
      }

      if (!plugin.metadata.enabled) {
        console.warn(`Plugin ${pluginId} is already disabled`);
        return true;
      }

      // 비활성화 상태 업데이트
      setPlugins(prev => ({
        ...prev,
        [pluginId]: {
          ...prev[pluginId],
          metadata: {
            ...prev[pluginId].metadata,
            enabled: false
          }
        }
      }));

      console.log(`Plugin ${pluginId} disabled successfully`);
      return true;

    } catch (error) {
      console.error(`Error disabling plugin ${pluginId}:`, error);
      return false;
    }
  };

  // 플러그인 조회
  const getPlugin = (pluginId: string): Plugin | undefined => {
    return plugins[pluginId];
  };

  // 플러그인 컴포넌트 조회
  const getPluginComponent = (pluginId: string, componentId: string): PluginComponent | undefined => {
    const plugin = plugins[pluginId];
    if (!plugin) return undefined;
    return plugin.components.find(comp => comp.id === componentId);
  };

  // 플러그인 라우트 조회
  const getPluginRoutes = (pluginId: string): PluginRoute[] => {
    const plugin = plugins[pluginId];
    if (!plugin || !plugin.metadata.enabled) return [];
    return plugin.routes;
  };

  // 모든 활성화된 플러그인의 라우트 조회
  const getAllRoutes = (): PluginRoute[] => {
    return Object.values(plugins)
      .filter(plugin => plugin.metadata.enabled)
      .flatMap(plugin => plugin.routes);
  };

  // 플러그인 로드 상태 확인
  const isPluginLoaded = (pluginId: string): boolean => {
    return loadedPlugins.includes(pluginId);
  };

  // 플러그인 활성화 상태 확인
  const isPluginEnabled = (pluginId: string): boolean => {
    const plugin = plugins[pluginId];
    return plugin ? plugin.metadata.enabled : false;
  };

  // 초기 플러그인 로드
  useEffect(() => {
    const initializePlugins = async () => {
      try {
        // 활성화된 플러그인들을 자동으로 로드
        const enabledPlugins = Object.values(plugins).filter(plugin => plugin.metadata.enabled);
        for (const plugin of enabledPlugins) {
          if (!loadedPlugins.includes(plugin.id)) {
            await loadPlugin(plugin.id);
          }
        }
      } catch (error) {
        console.error('Error initializing plugins:', error);
      }
    };

    initializePlugins();
  }, []);

  const contextValue: PluginManagerContextType = {
    plugins,
    loadedPlugins,
    loadPlugin,
    unloadPlugin,
    enablePlugin,
    disablePlugin,
    getPlugin,
    getPluginComponent,
    getPluginRoutes,
    getAllRoutes,
    isPluginLoaded,
    isPluginEnabled
  };

  return (
    <PluginManagerContext.Provider value={contextValue}>
      {children}
    </PluginManagerContext.Provider>
  );
};

// 플러그인 컴포넌트 렌더러
interface PluginComponentRendererProps {
  pluginId: string;
  componentId: string;
  props?: Record<string, any>;
  fallback?: ReactNode;
}

export const PluginComponentRenderer: React.FC<PluginComponentRendererProps> = ({
  pluginId,
  componentId,
  props = {},
  fallback = <div>Component not found</div>
}) => {
  const { getPluginComponent, isPluginEnabled } = usePluginManager();

  if (!isPluginEnabled(pluginId)) {
    return <div>Plugin is disabled</div>;
  }

  const pluginComponent = getPluginComponent(pluginId, componentId);
  if (!pluginComponent) {
    return <>{fallback}</>;
  }

  const Component = pluginComponent.component;
  return <Component {...props} {...pluginComponent.props} />;
};

// 플러그인 라우트 렌더러
interface PluginRouteRendererProps {
  pluginId: string;
  routePath: string;
  props?: Record<string, any>;
  fallback?: ReactNode;
}

export const PluginRouteRenderer: React.FC<PluginRouteRendererProps> = ({
  pluginId,
  routePath,
  props = {},
  fallback = <div>Route not found</div>
}) => {
  const { getPluginRoutes, isPluginEnabled } = usePluginManager();

  if (!isPluginEnabled(pluginId)) {
    return <div>Plugin is disabled</div>;
  }

  const routes = getPluginRoutes(pluginId);
  const route = routes.find(r => r.path === routePath);
  
  if (!route) {
    return <>{fallback}</>;
  }

  const Component = route.component;
  return <Component {...props} />;
}; 