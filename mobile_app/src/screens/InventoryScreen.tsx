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
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface InventoryItem {
  id: number;
  name: string;
  category: string;
  currentStock: number;
  minStock: number;
  maxStock: number;
  unit: string;
  price: number;
  status: 'normal' | 'low' | 'out';
  lastUpdated: string;
}

export default function InventoryScreen() {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // 데이터 로드
  const loadInventory = async () => {
    try {
      // 실제 API 호출로 대체
      const mockInventory: InventoryItem[] = [
        {
          id: 1,
          name: '아메리카노',
          category: '음료',
          currentStock: 150,
          minStock: 50,
          maxStock: 200,
          unit: '잔',
          price: 4500,
          status: 'normal',
          lastUpdated: '2024-01-15',
        },
        {
          id: 2,
          name: '카페라떼',
          category: '음료',
          currentStock: 30,
          minStock: 50,
          maxStock: 200,
          unit: '잔',
          price: 5000,
          status: 'low',
          lastUpdated: '2024-01-15',
        },
        {
          id: 3,
          name: '카푸치노',
          category: '음료',
          currentStock: 0,
          minStock: 30,
          maxStock: 150,
          unit: '잔',
          price: 5000,
          status: 'out',
          lastUpdated: '2024-01-14',
        },
        {
          id: 4,
          name: '티라떼',
          category: '음료',
          currentStock: 80,
          minStock: 40,
          maxStock: 120,
          unit: '잔',
          price: 5500,
          status: 'normal',
          lastUpdated: '2024-01-15',
        },
        {
          id: 5,
          name: '크로아상',
          category: '베이커리',
          currentStock: 25,
          minStock: 30,
          maxStock: 100,
          unit: '개',
          price: 3500,
          status: 'low',
          lastUpdated: '2024-01-15',
        },
      ];
      setInventory(mockInventory);
    } catch (error) {
      Alert.alert('오류', '재고 데이터를 불러오는데 실패했습니다.');
    }
  };

  // 새로고침
  const onRefresh = async () => {
    setRefreshing(true);
    await loadInventory();
    setRefreshing(false);
  };

  useEffect(() => {
    loadInventory();
  }, []);

  // 검색 및 필터링
  const filteredInventory = inventory.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'normal': return '#10b981';
      case 'low': return '#f59e0b';
      case 'out': return '#ef4444';
      default: return '#6b7280';
    }
  };

  // 상태별 텍스트
  const getStatusText = (status: string) => {
    switch (status) {
      case 'normal': return '정상';
      case 'low': return '부족';
      case 'out': return '품절';
      default: return '알 수 없음';
    }
  };

  // 재고 카드 컴포넌트
  const InventoryCard = ({ item }: { item: InventoryItem }) => (
    <TouchableOpacity 
      style={[styles.inventoryCard, { borderLeftColor: getStatusColor(item.status) }]}
      onPress={() => Alert.alert('재고 상세', `${item.name} 상세 정보`)}
    >
      <View style={styles.itemHeader}>
        <View style={styles.itemInfo}>
          <Text style={styles.itemName}>{item.name}</Text>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
            <Text style={styles.statusText}>{getStatusText(item.status)}</Text>
          </View>
        </View>
        <Text style={styles.itemPrice}>₩{item.price.toLocaleString()}</Text>
      </View>

      <View style={styles.itemDetails}>
        <View style={styles.detailRow}>
          <Ionicons name="cube" size={16} color="#6b7280" />
          <Text style={styles.detailText}>
            현재: {item.currentStock}{item.unit} / 최소: {item.minStock}{item.unit}
          </Text>
        </View>
        <View style={styles.detailRow}>
          <Ionicons name="pricetag" size={16} color="#6b7280" />
          <Text style={styles.detailText}>카테고리: {item.category}</Text>
        </View>
        <View style={styles.detailRow}>
          <Ionicons name="time" size={16} color="#6b7280" />
          <Text style={styles.detailText}>최종 업데이트: {item.lastUpdated}</Text>
        </View>
      </View>

      {/* 재고 바 */}
      <View style={styles.stockBar}>
        <View style={styles.stockBarBackground}>
          <View 
            style={[
              styles.stockBarFill, 
              { 
                width: `${(item.currentStock / item.maxStock) * 100}%`,
                backgroundColor: getStatusColor(item.status)
              }
            ]} 
          />
        </View>
        <Text style={styles.stockText}>
          {item.currentStock} / {item.maxStock} {item.unit}
        </Text>
      </View>

      <View style={styles.itemActions}>
        <TouchableOpacity style={styles.actionButton}>
          <Ionicons name="add-circle" size={16} color="#10b981" />
          <Text style={styles.actionText}>입고</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Ionicons name="remove-circle" size={16} color="#ef4444" />
          <Text style={styles.actionText}>출고</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Ionicons name="create" size={16} color="#3b82f6" />
          <Text style={styles.actionText}>수정</Text>
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );

  // 카테고리 필터
  const categories = ['all', '음료', '베이커리', '원두', '부자재'];
  const CategoryFilter = () => (
    <View style={styles.categoryFilter}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        {categories.map(category => (
          <TouchableOpacity
            key={category}
            style={[
              styles.categoryButton,
              selectedCategory === category && styles.categoryButtonActive
            ]}
            onPress={() => setSelectedCategory(category)}
          >
            <Text style={[
              styles.categoryText,
              selectedCategory === category && styles.categoryTextActive
            ]}>
              {category === 'all' ? '전체' : category}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );

  return (
    <View style={styles.container}>
      {/* 헤더 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>재고 관리</Text>
        <TouchableOpacity 
          style={styles.addButton}
          onPress={() => Alert.alert('새 상품', '새 상품 추가')}
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
            placeholder="상품명, 카테고리로 검색"
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

      {/* 카테고리 필터 */}
      <CategoryFilter />

      {/* 통계 */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{inventory.length}</Text>
          <Text style={styles.statLabel}>총 상품</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>
            {inventory.filter(item => item.status === 'low').length}
          </Text>
          <Text style={styles.statLabel}>재고 부족</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>
            {inventory.filter(item => item.status === 'out').length}
          </Text>
          <Text style={styles.statLabel}>품절</Text>
        </View>
      </View>

      {/* 재고 목록 */}
      <FlatList
        data={filteredInventory}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => <InventoryCard item={item} />}
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
  categoryFilter: {
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  categoryButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginRight: 8,
    borderRadius: 20,
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  categoryButtonActive: {
    backgroundColor: '#3b82f6',
    borderColor: '#3b82f6',
  },
  categoryText: {
    fontSize: 14,
    color: '#6b7280',
  },
  categoryTextActive: {
    color: 'white',
    fontWeight: '600',
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
  inventoryCard: {
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
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  itemInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  itemName: {
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
  itemPrice: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#3b82f6',
  },
  itemDetails: {
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
  stockBar: {
    marginBottom: 12,
  },
  stockBarBackground: {
    height: 8,
    backgroundColor: '#f3f4f6',
    borderRadius: 4,
    marginBottom: 4,
  },
  stockBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  stockText: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
  },
  itemActions: {
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