import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Notification {
  id: number;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  timestamp: string;
  isRead: boolean;
}

export default function NotificationsScreen() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadNotifications = async () => {
    try {
      const mockNotifications: Notification[] = [
        {
          id: 1,
          title: '재고 부족 알림',
          message: '카페라떼 재고가 부족합니다. 발주를 확인해주세요.',
          type: 'warning',
          timestamp: '5분 전',
          isRead: false,
        },
        {
          id: 2,
          title: '주문 완료',
          message: '주문 #1234가 완료되었습니다.',
          type: 'success',
          timestamp: '15분 전',
          isRead: true,
        },
        {
          id: 3,
          title: '시스템 업데이트',
          message: '새로운 기능이 추가되었습니다.',
          type: 'info',
          timestamp: '1시간 전',
          isRead: true,
        },
      ];
      setNotifications(mockNotifications);
    } catch (error) {
      Alert.alert('오류', '알림 데이터를 불러오는데 실패했습니다.');
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadNotifications();
    setRefreshing(false);
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'info': return '#3b82f6';
      case 'warning': return '#f59e0b';
      case 'error': return '#ef4444';
      case 'success': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'info': return 'information-circle';
      case 'warning': return 'warning';
      case 'error': return 'close-circle';
      case 'success': return 'checkmark-circle';
      default: return 'notifications';
    }
  };

  const NotificationCard = ({ notification }: { notification: Notification }) => (
    <TouchableOpacity 
      style={[
        styles.notificationCard, 
        { 
          borderLeftColor: getTypeColor(notification.type),
          backgroundColor: notification.isRead ? 'white' : '#f0f9ff'
        }
      ]}
      onPress={() => {
        if (!notification.isRead) {
          setNotifications(prev => 
            prev.map(n => n.id === notification.id ? { ...n, isRead: true } : n)
          );
        }
        Alert.alert(notification.title, notification.message);
      }}
    >
      <View style={styles.notificationHeader}>
        <View style={styles.notificationInfo}>
          <Ionicons 
            name={getTypeIcon(notification.type)} 
            size={20} 
            color={getTypeColor(notification.type)} 
          />
          <Text style={styles.notificationTitle}>{notification.title}</Text>
          {!notification.isRead && <View style={styles.unreadDot} />}
        </View>
        <Text style={styles.timestamp}>{notification.timestamp}</Text>
      </View>

      <Text style={styles.notificationMessage}>{notification.message}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>알림</Text>
        <TouchableOpacity 
          style={styles.clearButton}
          onPress={() => {
            setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));
            Alert.alert('알림', '모든 알림을 읽음 처리했습니다.');
          }}
        >
          <Ionicons name="checkmark-done" size={24} color="white" />
        </TouchableOpacity>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{notifications.length}</Text>
          <Text style={styles.statLabel}>총 알림</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>
            {notifications.filter(n => !n.isRead).length}
          </Text>
          <Text style={styles.statLabel}>읽지 않음</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>
            {notifications.filter(n => n.type === 'warning').length}
          </Text>
          <Text style={styles.statLabel}>경고</Text>
        </View>
      </View>

      <FlatList
        data={notifications}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => <NotificationCard notification={item} />}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#3b82f6',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  clearButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#3b82f6',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#6b7280',
  },
  listContainer: {
    padding: 16,
  },
  notificationCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  notificationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  notificationInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  notificationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginLeft: 8,
    flex: 1,
  },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#3b82f6',
    marginLeft: 8,
  },
  timestamp: {
    fontSize: 12,
    color: '#6b7280',
  },
  notificationMessage: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
}); 