import NetInfo from '@react-native-community/netinfo';
import { useState, useEffect, useCallback } from 'react';

export interface NetworkState {
  isConnected: boolean;
  isInternetReachable: boolean | null;
  type: string | null;
  isWifiEnabled: boolean;
  isCellularEnabled: boolean;
}

export class NetworkService {
  private static instance: NetworkService;
  private listeners: Set<(state: NetworkState) => void> = new Set();
  private currentState: NetworkState = {
    isConnected: false,
    isInternetReachable: null,
    type: null,
    isWifiEnabled: false,
    isCellularEnabled: false,
  };

  private constructor() {
    this.initialize();
  }

  public static getInstance(): NetworkService {
    if (!NetworkService.instance) {
      NetworkService.instance = new NetworkService();
    }
    return NetworkService.instance;
  }

  private async initialize() {
    // 초기 네트워크 상태 확인
    const state = await NetInfo.fetch();
    this.updateState(state);

    // 네트워크 상태 변경 리스너 등록
    NetInfo.addEventListener(this.handleNetworkChange.bind(this));
  }

  private handleNetworkChange(state: any) {
    this.updateState(state);
    this.notifyListeners();
  }

  private updateState(state: any) {
    this.currentState = {
      isConnected: state.isConnected ?? false,
      isInternetReachable: state.isInternetReachable,
      type: state.type,
      isWifiEnabled: state.type === 'wifi',
      isCellularEnabled: state.type === 'cellular',
    };
  }

  private notifyListeners() {
    this.listeners.forEach(listener => {
      try {
        listener(this.currentState);
      } catch (error) {
        console.error('네트워크 상태 리스너 오류:', error);
      }
    });
  }

  /**
   * 네트워크 상태 변경 리스너 등록
   */
  addListener(listener: (state: NetworkState) => void): () => void {
    this.listeners.add(listener);
    
    // 즉시 현재 상태 전달
    listener(this.currentState);
    
    // 리스너 제거 함수 반환
    return () => {
      this.listeners.delete(listener);
    };
  }

  /**
   * 현재 네트워크 상태 반환
   */
  getCurrentState(): NetworkState {
    return { ...this.currentState };
  }

  /**
   * 네트워크 연결 상태 확인
   */
  isOnline(): boolean {
    return this.currentState.isConnected && 
           this.currentState.isInternetReachable === true;
  }

  /**
   * WiFi 연결 상태 확인
   */
  isWifiConnected(): boolean {
    return this.currentState.isConnected && 
           this.currentState.isWifiEnabled;
  }

  /**
   * 셀룰러 연결 상태 확인
   */
  isCellularConnected(): boolean {
    return this.currentState.isConnected && 
           this.currentState.isCellularEnabled;
  }

  /**
   * 네트워크 상태 새로고침
   */
  async refresh(): Promise<NetworkState> {
    const state = await NetInfo.fetch();
    this.updateState(state);
    this.notifyListeners();
    return this.getCurrentState();
  }

  /**
   * 연결 품질 확인 (간단한 ping 테스트)
   */
  async checkConnectionQuality(): Promise<'excellent' | 'good' | 'poor' | 'offline'> {
    if (!this.isOnline()) {
      return 'offline';
    }

    try {
      const startTime = Date.now();
      
      // 간단한 ping 테스트 (Google DNS)
      const response = await fetch('https://8.8.8.8', {
        method: 'HEAD',
        mode: 'no-cors',
        cache: 'no-cache',
      });
      
      const endTime = Date.now();
      const latency = endTime - startTime;

      if (latency < 100) return 'excellent';
      if (latency < 300) return 'good';
      return 'poor';
    } catch (error) {
      return 'poor';
    }
  }
}

// 싱글톤 인스턴스 내보내기
export const networkService = NetworkService.getInstance();

// React Hook으로 네트워크 상태 사용
export function useNetworkState() {
  const [networkState, setNetworkState] = useState<NetworkState>(
    networkService.getCurrentState()
  );

  useEffect(() => {
    const unsubscribe = networkService.addListener(setNetworkState);
    return unsubscribe;
  }, []);

  return {
    ...networkState,
    isOnline: networkService.isOnline(),
    isWifiConnected: networkService.isWifiConnected(),
    isCellularConnected: networkService.isCellularConnected(),
    refresh: networkService.refresh.bind(networkService),
    checkQuality: networkService.checkConnectionQuality.bind(networkService),
  };
}
