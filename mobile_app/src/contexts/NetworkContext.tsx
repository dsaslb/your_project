import React, { createContext, useContext, useState, useEffect } from 'react';
import * as Network from 'expo-network';
import NetInfo from '@react-native-community/netinfo';

interface NetworkContextType {
  isOnline: boolean;
  connectionType: string | null;
  isConnected: boolean | null;
}

const NetworkContext = createContext<NetworkContextType | undefined>(undefined);

export const useNetwork = () => {
  const context = useContext(NetworkContext);
  if (!context) {
    throw new Error('useNetwork must be used within a NetworkProvider');
  }
  return context;
};

export const NetworkProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isOnline, setIsOnline] = useState(true);
  const [connectionType, setConnectionType] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState<boolean | null>(true);

  useEffect(() => {
    // 초기 네트워크 상태 확인
    checkNetworkStatus();

    // 네트워크 상태 변경 감지
    const unsubscribe = NetInfo.addEventListener((state: any) => {
      setIsConnected(state.isConnected);
      setIsOnline(state.isConnected ?? true);
      setConnectionType(state.type);
    });

    return () => unsubscribe();
  }, []);

  const checkNetworkStatus = async () => {
    try {
      const networkState = await Network.getNetworkStateAsync();
      setIsOnline(networkState.isConnected);
      setConnectionType(networkState.type);
    } catch (error) {
      console.error('네트워크 상태 확인 오류:', error);
    }
  };

  const value: NetworkContextType = {
    isOnline,
    connectionType,
    isConnected
  };

  return (
    <NetworkContext.Provider value={value}>
      {children}
    </NetworkContext.Provider>
  );
}; 