import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useNetworkState } from '../services/NetworkService';
import { useSyncStatus } from '../hooks/useSyncStatus';
import { Wifi, WifiOff, RefreshCw, AlertCircle } from 'lucide-react-native';

export function OfflineIndicator() {
  const { isOnline, isWifiConnected, isCellularConnected } = useNetworkState();
  const { isSyncing, pendingActions, lastSyncTime } = useSyncStatus();

  if (isOnline) {
    return (
      <View style={[styles.container, styles.online]}>
        <Wifi size={16} color="#10B981" />
        <Text style={styles.onlineText}>
          {isWifiConnected ? 'WiFi 연결됨' : isCellularConnected ? '모바일 데이터 연결됨' : '온라인'}
        </Text>
        {isSyncing && (
          <View style={styles.syncingContainer}>
            <RefreshCw size={14} color="#10B981" />
            <Text style={styles.syncingText}>동기화 중...</Text>
          </View>
        )}
        {pendingActions > 0 && (
          <View style={styles.pendingContainer}>
            <AlertCircle size={14} color="#F59E0B" />
            <Text style={styles.pendingText}>{pendingActions}개 대기</Text>
          </View>
        )}
      </View>
    );
  }

  return (
    <View style={[styles.container, styles.offline]}>
      <WifiOff size={16} color="#EF4444" />
      <Text style={styles.offlineText}>오프라인 모드</Text>
      {pendingActions > 0 && (
        <Text style={styles.pendingOfflineText}>
          {pendingActions}개 작업이 대기 중입니다
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    marginHorizontal: 16,
    marginVertical: 8,
  },
  online: {
    backgroundColor: '#ECFDF5',
    borderColor: '#10B981',
    borderWidth: 1,
  },
  offline: {
    backgroundColor: '#FEF2F2',
    borderColor: '#EF4444',
    borderWidth: 1,
  },
  onlineText: {
    color: '#10B981',
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 8,
  },
  offlineText: {
    color: '#EF4444',
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 8,
  },
  syncingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 12,
  },
  syncingText: {
    color: '#10B981',
    fontSize: 12,
    marginLeft: 4,
  },
  pendingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 12,
  },
  pendingText: {
    color: '#F59E0B',
    fontSize: 12,
    marginLeft: 4,
  },
  pendingOfflineText: {
    color: '#EF4444',
    fontSize: 12,
    marginLeft: 8,
  },
});
