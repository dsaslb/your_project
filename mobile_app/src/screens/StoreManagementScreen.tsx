import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
  TextInput,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Store {
  id: number;
  name: string;
  address: string;
  phone: string;
  manager: string;
  status: 'active' | 'inactive';
  sales: number;
  employees: number;
}

export default function StoreManagementScreen() {
  const [stores, setStores] = useState<Store[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // 데이터 로드
  const loadStores = async () => {
    try {
      // 실제 API 호출로 대체
      const mockStores: Store[] = [
        {
          id: 1,
          name: '강남점',
          address: '서울시 강남구 테헤란로 123',
          phone: '02-1234-5678',
          manager: '김매니저',
          status: 'active',
          sales: 2500000,
          employees: 8,
        },
        {
          id: 2,
          name: '홍대점',
          address: '서울시 마포구 홍대로 456',
          phone: '02-2345-6789',
          manager: '이매니저',
          status: 'active',
          sales: 1800000,
          employees: 6,
        },
        {
          id: 3,
          name: '부산점',
          address: '부산시 해운대구 해운대로 789',
          phone: '051-3456-7890',
          manager: '박매니저',
          status: 'inactive',
          sales: 1200000,
          employees: 4,
        },
      ];
      setStores(mockStores);
    } catch (error) {
      Alert.alert('오류', '매장 데이터를 불러오는데 실패했습니다.');
    }
  };

  // 새로고침
  const onRefresh = async () => {
    setRefreshing(true);
    await loadStores();
    setRefreshing(false);
  };

  useEffect(() => {
    loadStores();
  }, []);

  // 검색 필터링
  const filteredStores = stores.filter(store =>
    store.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    store.address.toLowerCase().includes(searchQuery.toLowerCase()) ||
    store.manager.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // 매장 상태 토글
  const toggleStoreStatus = (storeId: number) => {
    setStores(prevStores =>
      prevStores.map(store =>
        store.id === storeId
          ? { ...store, status: store.status === 'active' ? 'inactive' : 'active' }
          : store
      )
    );
  };

  // 매장 카드 컴포넌트
  const StoreCard = ({ store }: { store: Store }) => (
    <TouchableOpacity 
      style={[styles.storeCard, { opacity: store.status === 'inactive' ? 0.6 : 1 }]}
      onPress={() => Alert.alert('매장 상세', `${store.name} 상세 정보`)}
    >
      <View style={styles.storeHeader}>
        <View style={styles.storeInfo}>
          <Text style={styles.storeName}>{store.name}</Text>
          <View style={[styles.statusBadge, { backgroundColor: store.status === 'active' ? '#10b981' : '#6b7280' }]}>
            <Text style={styles.statusText}>
              {store.status === 'active' ? '운영중' : '운영중단'}
            </Text>
          </View>
        </View>
        <TouchableOpacity
          onPress={() => toggleStoreStatus(store.id)}
          style={styles.statusToggle}
        >
          <Ionicons 
            name={store.status === 'active' ? 'checkmark-circle' : 'close-circle'} 
            size={24} 
            color={store.status === 'active' ? '#10b981' : '#6b7280'} 
          />
        </TouchableOpacity>
      </View>

      <View style={styles.storeDetails}>
        <View style={styles.detailRow}>
          <Ionicons name="location" size={16} color="#6b7280" />
          <Text style={styles.detailText}>{store.address}</Text>
        </View>
        <View style={styles.detailRow}>
          <Ionicons name="call" size={16} color="#6b7280" />
          <Text style={styles.detailText}>{store.phone}</Text>
        </View>
        <View style={styles.detailRow}>
          <Ionicons name="person" size={16} color="#6b7280" />
          <Text style={styles.detailText}>매니저: {store.manager}</Text>
        </View>
      </View>

      <View style={styles.storeStats}>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>오늘 매출</Text>
          <Text style={styles.statValue}>₩{store.sales.toLocaleString()}</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>직원 수</Text>
          <Text style={styles.statValue}>{store.employees}명</Text>
        </View>
      </View>

      <View style={styles.storeActions}>
        <TouchableOpacity style={styles.actionButton}>
          <Ionicons name="create" size={16} color="#3b82f6" />
          <Text style={styles.actionText}>수정</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Ionicons name="people" size={16} color="#10b981" />
          <Text style={styles.actionText}>직원</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Ionicons name="analytics" size={16} color="#8b5cf6" />
          <Text style={styles.actionText}>분석</Text>
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {/* 헤더 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>매장 관리</Text>
        <TouchableOpacity 
          style={styles.addButton}
          onPress={() => Alert.alert('새 매장', '새 매장 추가')}
        >
          <Ionicons name="add" size={24} color="white" />
        </TouchableOpacity>
      </View>

      {/* 검색 */}
      <View style={styles.searchContainer}>
        <View style={styles.searchBox}>
          <Ionicons name="search" size={20} color="#6b7280" />
          <TextInput
            style={styles.searchInput}
            placeholder="매장명, 주소, 매니저로 검색"
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery('')}>
              <Ionicons name="close-circle" size={20} color="#6b7280" />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* 통계 */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{stores.length}</Text>
          <Text style={styles.statLabel}>총 매장</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>
            {stores.filter(s => s.status === 'active').length}
          </Text>
          <Text style={styles.statLabel}>운영중</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>
            {stores.reduce((sum, store) => sum + store.employees, 0)}
          </Text>
          <Text style={styles.statLabel}>총 직원</Text>
        </View>
      </View>

      {/* 매장 목록 */}
      <FlatList
        data={filteredStores}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => <StoreCard store={item} />}
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
  searchContainer: {
    padding: 16,
  },
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  searchInput: {
    flex: 1,
    marginLeft: 12,
    fontSize: 16,
    color: '#1f2937',
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
  storeCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  storeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  storeInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  storeName: {
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
  statusToggle: {
    padding: 4,
  },
  storeDetails: {
    marginBottom: 12,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  detailText: {
    fontSize: 14,
    color: '#6b7280',
    marginLeft: 8,
  },
  storeStats: {
    flexDirection: 'row',
    marginBottom: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#f3f4f6',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  storeActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#f3f4f6',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  actionText: {
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 4,
  },
}); 