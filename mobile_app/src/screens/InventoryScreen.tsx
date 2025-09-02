import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  Alert,
  SafeAreaView,
  Image,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
// import { BarCodeScanner } from 'expo-barcode-scanner'; // QR 코드 기능 비활성화
import * as ImagePicker from 'expo-image-picker';
import { api } from '../api/client';
import { socket } from '../api/socket';
import { safePost } from '../utils/queue';

interface InventoryItem {
  id?: string;
  barcode: string;
  productName?: string;
  quantity: number;
  photoUri?: string;
  timestamp?: string;
}

export default function InventoryScreen({ onBack }: { onBack: () => void }) {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [scanned, setScanned] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [inventoryItem, setInventoryItem] = useState<InventoryItem>({
    barcode: '',
    quantity: 0,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [inventoryHistory, setInventoryHistory] = useState<InventoryItem[]>([]);

  useEffect(() => {
    // 카메라 권한 요청
    (async () => {
      const { status } = await BarCodeScanner.requestPermissionsAsync();
      setHasPermission(status === 'granted');
    })();

    // 이미지 선택 권한 요청
    (async () => {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('권한 필요', '사진을 업로드하려면 갤러리 접근 권한이 필요합니다.');
      }
    })();

    // 실시간 재고 업데이트 구독
    socket.on('inventory:update', (data) => {
      console.log('재고 업데이트 수신:', data);
      Alert.alert('재고 알림', `재고가 업데이트되었습니다.\n바코드: ${data.barcode}`);
      loadInventoryHistory();
    });

    loadInventoryHistory();

    return () => {
      socket.off('inventory:update');
    };
  }, []);

  const loadInventoryHistory = async () => {
    try {
      // 실제로는 API에서 재고 히스토리를 가져옴
      // const history = await api.getInventoryHistory();
      // setInventoryHistory(history);
    } catch (error) {
      console.error('재고 히스토리 로드 오류:', error);
    }
  };

  const handleBarCodeScanned = ({ type, data }: { type: string; data: string }) => {
    setScanned(true);
    setShowCamera(false);
    setInventoryItem(prev => ({
      ...prev,
      barcode: data,
      productName: `상품-${data.slice(-4)}` // 임시 상품명
    }));
    Alert.alert('바코드 스캔 완료', `바코드: ${data}`);
  };

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      setInventoryItem(prev => ({
        ...prev,
        photoUri: result.assets[0].uri
      }));
    }
  };

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('권한 필요', '사진을 촬영하려면 카메라 접근 권한이 필요합니다.');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      setInventoryItem(prev => ({
        ...prev,
        photoUri: result.assets[0].uri
      }));
    }
  };

  const submitInventory = async () => {
    if (!inventoryItem.barcode) {
      Alert.alert('오류', '바코드를 스캔하거나 입력해주세요.');
      return;
    }

    if (inventoryItem.quantity <= 0) {
      Alert.alert('오류', '수량을 입력해주세요.');
      return;
    }

    setIsLoading(true);
    try {
      const result = await safePost('/api/mobile/inventory/check', {
        barcode: inventoryItem.barcode,
        qty: inventoryItem.quantity,
        photo_url: inventoryItem.photoUri || null
      });

      Alert.alert('성공', '재고가 성공적으로 기록되었습니다!');
      
      // 폼 초기화
      setInventoryItem({
        barcode: '',
        quantity: 0,
        photoUri: undefined
      });
      setScanned(false);
      
      // 히스토리 새로고침
      loadInventoryHistory();
      
    } catch (error: any) {
      Alert.alert('오류', error.response?.data?.error || '재고 기록에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  if (hasPermission === null) {
    return <Text>카메라 권한을 요청중입니다...</Text>;
  }
  if (hasPermission === false) {
    return <Text>카메라 접근 권한이 없습니다.</Text>;
  }

  if (showCamera) {
    return (
      <View style={styles.container}>
        <BarCodeScanner
          onBarCodeScanned={scanned ? undefined : handleBarCodeScanned}
          style={StyleSheet.absoluteFillObject}
        />
        <View style={styles.cameraOverlay}>
          <Text style={styles.cameraText}>바코드를 스캔하세요</Text>
          <TouchableOpacity
            style={styles.cancelButton}
            onPress={() => {
              setShowCamera(false);
              setScanned(false);
            }}
          >
            <Text style={styles.cancelButtonText}>취소</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={onBack}>
            <Text style={styles.backButtonText}>← 뒤로</Text>
          </TouchableOpacity>
          <Text style={styles.title}>재고 관리</Text>
        </View>

        <View style={styles.content}>
          {/* 바코드 입력 섹션 */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>상품 정보</Text>
            
            <View style={styles.barcodeContainer}>
              <TextInput
                style={styles.barcodeInput}
                placeholder="바코드 번호"
                value={inventoryItem.barcode}
                onChangeText={(text) => setInventoryItem(prev => ({ ...prev, barcode: text }))}
              />
              <TouchableOpacity
                style={styles.scanButton}
                onPress={() => setShowCamera(true)}
              >
                <Text style={styles.scanButtonText}>스캔</Text>
              </TouchableOpacity>
            </View>

            {inventoryItem.productName && (
              <Text style={styles.productName}>상품명: {inventoryItem.productName}</Text>
            )}
          </View>

          {/* 수량 입력 섹션 */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>재고 수량</Text>
            <TextInput
              style={styles.quantityInput}
              placeholder="수량을 입력하세요"
              value={inventoryItem.quantity.toString()}
              onChangeText={(text) => setInventoryItem(prev => ({ 
                ...prev, 
                quantity: parseInt(text) || 0 
              }))}
              keyboardType="numeric"
            />
          </View>

          {/* 사진 섹션 */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>재고 사진 (선택사항)</Text>
            
            <View style={styles.photoContainer}>
              <TouchableOpacity style={styles.photoButton} onPress={takePhoto}>
                <Text style={styles.photoButtonText}>📷 사진 촬영</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.photoButton} onPress={pickImage}>
                <Text style={styles.photoButtonText}>🖼️ 갤러리</Text>
              </TouchableOpacity>
            </View>

            {inventoryItem.photoUri && (
              <Image source={{ uri: inventoryItem.photoUri }} style={styles.previewImage} />
            )}
          </View>

          {/* 제출 버튼 */}
          <TouchableOpacity
            style={[styles.submitButton, isLoading && styles.submitButtonDisabled]}
            onPress={submitInventory}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#ffffff" />
            ) : (
              <Text style={styles.submitButtonText}>재고 기록</Text>
            )}
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  backButton: {
    marginRight: 16,
  },
  backButtonText: {
    fontSize: 16,
    color: '#007AFF',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  content: {
    padding: 16,
  },
  section: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  barcodeContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  barcodeInput: {
    flex: 1,
    height: 48,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 12,
    backgroundColor: '#f9f9f9',
  },
  scanButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 8,
    justifyContent: 'center',
  },
  scanButtonText: {
    color: '#ffffff',
    fontWeight: 'bold',
  },
  productName: {
    marginTop: 8,
    fontSize: 14,
    color: '#666',
    fontStyle: 'italic',
  },
  quantityInput: {
    height: 48,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 12,
    backgroundColor: '#f9f9f9',
    fontSize: 16,
  },
  photoContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
  },
  photoButton: {
    flex: 1,
    backgroundColor: '#f0f0f0',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  photoButtonText: {
    fontSize: 14,
    color: '#333',
  },
  previewImage: {
    width: '100%',
    height: 200,
    borderRadius: 8,
    resizeMode: 'cover',
  },
  submitButton: {
    backgroundColor: '#34C759',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 16,
  },
  submitButtonDisabled: {
    backgroundColor: '#cccccc',
  },
  submitButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  cameraOverlay: {
    flex: 1,
    backgroundColor: 'transparent',
    flexDirection: 'column',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 60,
  },
  cameraText: {
    fontSize: 18,
    color: '#ffffff',
    backgroundColor: 'rgba(0,0,0,0.5)',
    padding: 12,
    borderRadius: 8,
  },
  cancelButton: {
    backgroundColor: 'rgba(255,255,255,0.9)',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 25,
  },
  cancelButtonText: {
    color: '#333',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
