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

interface Order {
  id: number;
  orderNumber: string;
  customerName: string;
  items: string[];
  totalAmount: number;
  status: 'pending' | 'preparing' | 'ready' | 'completed' | 'cancelled';
  orderTime: string;
  storeName: string;
}

export default function OrdersScreen() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  // 데이터 로드
  const loadOrders = async () => {
    try {
      const mockOrders: Order[] = [
        {
          id: 1,
          orderNumber: '#1234',
          customerName: '김고객',
          items: ['아메리카노', '크로아상'],
          totalAmount: 8000,
          status: 'pending',
          orderTime: '14:30',
          storeName: '강남점',
        },
        {
          id: 2,
          orderNumber: '#1235',
          customerName: '이고객',
          items: ['카페라떼'],
          totalAmount: 5000,
          status: 'preparing',
          orderTime: '14:25',
          storeName: '홍대점',
        },
        {
          id: 3,
          orderNumber: '#1236',
          customerName: '박고객',
          items: ['티라떼', '마카롱'],
          totalAmount: 9000,
          status: 'ready',
          orderTime: '14:20',
          storeName: '강남점',
        },
      ];
      setOrders(mockOrders);
    } catch (error) {
      Alert.alert('오류', '주문 데이터를 불러오는데 실패했습니다.');
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadOrders();
    setRefreshing(false);
  };

  useEffect(() => {
    loadOrders();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return '#f59e0b';
      case 'preparing': return '#3b82f6';
      case 'ready': return '#10b981';
      case 'completed': return '#6b7280';
      case 'cancelled': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending': return '대기중';
      case 'preparing': return '제조중';
      case 'ready': return '준비완료';
      case 'completed': return '완료';
      case 'cancelled': return '취소';
      default: return '알 수 없음';
    }
  };

  const OrderCard = ({ order }: { order: Order }) => (
    <TouchableOpacity 
      style={[styles.orderCard, { borderLeftColor: getStatusColor(order.status) }]}
      onPress={() => Alert.alert('주문 상세', `${order.orderNumber} 상세 정보`)}
    >
      <View style={styles.orderHeader}>
        <View style={styles.orderInfo}>
          <Text style={styles.orderNumber}>{order.orderNumber}</Text>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(order.status) }]}>
            <Text style={styles.statusText}>{getStatusText(order.status)}</Text>
          </View>
        </View>
        <Text style={styles.orderTime}>{order.orderTime}</Text>
      </View>

      <View style={styles.orderDetails}>
        <Text style={styles.customerName}>{order.customerName}</Text>
        <Text style={styles.storeName}>{order.storeName}</Text>
        <Text style={styles.items}>{order.items.join(', ')}</Text>
      </View>

      <View style={styles.orderFooter}>
        <Text style={styles.totalAmount}>₩{order.totalAmount.toLocaleString()}</Text>
        <View style={styles.orderActions}>
          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="checkmark-circle" size={20} color="#10b981" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="close-circle" size={20} color="#ef4444" />
          </TouchableOpacity>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>주문 관리</Text>
        <TouchableOpacity 
          style={styles.addButton}
          onPress={() => Alert.alert('새 주문', '새 주문 생성')}
        >
          <Ionicons name="add" size={24} color="white" />
        </TouchableOpacity>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{orders.length}</Text>
          <Text style={styles.statLabel}>총 주문</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>
            {orders.filter(o => o.status === 'pending').length}
          </Text>
          <Text style={styles.statLabel}>대기중</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>
            {orders.filter(o => o.status === 'preparing').length}
          </Text>
          <Text style={styles.statLabel}>제조중</Text>
        </View>
      </View>

      <FlatList
        data={orders}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => <OrderCard order={item} />}
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
  addButton: {
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
  orderCard: {
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
  orderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  orderInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  orderNumber: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginRight: 8,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: 'white',
  },
  orderTime: {
    fontSize: 14,
    color: '#6b7280',
  },
  orderDetails: {
    marginBottom: 12,
  },
  customerName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
  },
  storeName: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 4,
  },
  items: {
    fontSize: 14,
    color: '#374151',
  },
  orderFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#f3f4f6',
  },
  totalAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#3b82f6',
  },
  orderActions: {
    flexDirection: 'row',
  },
  actionButton: {
    marginLeft: 12,
  },
}); 