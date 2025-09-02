/**
 * 📦 재고 조사 화면
 * 
 * 바코드 스캔과 수량 입력을 통한 재고 조사
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
  ScrollView,
  Image,
} from 'react-native';
import { BarCodeScanner } from 'expo-barcode-scanner';
import * as ImagePicker from 'expo-image-picker';
import { mobileAPI } from '../api/client';
import { subscribeToInventoryUpdates } from '../api/socket';

interface InventoryItem {
  id: number;
  barcode: string;
  qty: number;
  photo_url?: string;
  created_at: string;
}

export default function InventoryCheckScreen() {
  const [loading, setLoading] = useState(false);
  const [barcode, setBarcode] = useState('');
  const [quantity, setQuantity] = useState('');
  const [photo, setPhoto] = useState<string | null>(null);
  const [showScanner, setShowScanner] = useState(false);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [inventoryHistory, setInventoryHistory] = useState<InventoryItem[]>([]);

  useEffect(() => {
    // 카메라 권한 요청
    (async () => {
      const { status } = await BarCodeScanner.requestPermissionsAsync();
      setHasPermission(status === 'granted');
    })();

    // 실시간 재고 업데이트 구독
    const unsubscribe = subscribeToInventoryUpdates((data: InventoryItem) => {
      setInventoryHistory(prev => [data, ...prev]);
      Alert.alert(
        '재고 업데이트',
        `바코드 ${data.barcode}의 재고가 ${data.qty}개로 업데이트되었습니다.`
      );
    });

    return unsubscribe;
  }, []);

  const handleBarCodeScanned = ({ type, data }: { type: string; data: string }) => {
    setBarcode(data);
    setShowScanner(false);
  };

  const takePhoto = async () => {
    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setPhoto(result.assets[0].uri);
      }
    } catch (error) {
      Alert.alert('오류', '사진 촬영에 실패했습니다.');
    }
  };

  const pickImage = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setPhoto(result.assets[0].uri);
      }
    } catch (error) {
      Alert.alert('오류', '이미지 선택에 실패했습니다.');
    }
  };

  const submitInventory = async () => {
    if (!barcode.trim()) {
      Alert.alert('오류', '바코드를 입력하거나 스캔해주세요.');
      return;
    }

    if (!quantity.trim() || isNaN(Number(quantity))) {
      Alert.alert('오류', '유효한 수량을 입력해주세요.');
      return;
    }

    setLoading(true);
    try {
      const result = await mobileAPI.checkInventory({
        barcode: barcode.trim(),
        qty: parseInt(quantity),
        photo_url: photo || undefined,
      });

      if (result.ok) {
        Alert.alert('성공', '재고 조사가 완료되었습니다.');
        
        // 입력 필드 초기화
        setBarcode('');
        setQuantity('');
        setPhoto(null);
        
        // 히스토리에 추가
        const newItem: InventoryItem = {
          id: result.id,
          barcode: barcode.trim(),
          qty: parseInt(quantity),
          photo_url: photo || undefined,
          created_at: new Date().toISOString(),
        };
        
        setInventoryHistory(prev => [newItem, ...prev]);
      }
    } catch (error) {
      console.error('재고 조사 실패:', error);
      Alert.alert('오류', '재고 조사에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const clearForm = () => {
    setBarcode('');
    setQuantity('');
    setPhoto(null);
  };

  if (showScanner) {
    return (
      <View style={styles.container}>
        <BarCodeScanner
          onBarCodeScanned={handleBarCodeScanned}
          style={StyleSheet.absoluteFillObject}
        />
        <View style={styles.scannerOverlay}>
          <TouchableOpacity
            style={styles.closeButton}
            onPress={() => setShowScanner(false)}
          >
            <Text style={styles.closeButtonText}>닫기</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>재고 조사</Text>
        <Text style={styles.subtitle}>바코드 스캔 및 수량 입력</Text>
      </View>

      {/* 입력 폼 */}
      <View style={styles.formCard}>
        <Text style={styles.cardTitle}>📝 재고 정보 입력</Text>
        
        {/* 바코드 입력 */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>바코드</Text>
          <View style={styles.barcodeInput}>
            <TextInput
              style={styles.textInput}
              value={barcode}
              onChangeText={setBarcode}
              placeholder="바코드를 입력하거나 스캔하세요"
              autoCapitalize="none"
            />
            <TouchableOpacity
              style={styles.scanButton}
              onPress={() => setShowScanner(true)}
            >
              <Text style={styles.scanButtonText}>📱 스캔</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* 수량 입력 */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>수량</Text>
          <TextInput
            style={styles.textInput}
            value={quantity}
            onChangeText={setQuantity}
            placeholder="수량을 입력하세요"
            keyboardType="numeric"
          />
        </View>

        {/* 사진 첨부 */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>사진 첨부 (선택사항)</Text>
          <View style={styles.photoButtons}>
            <TouchableOpacity style={styles.photoButton} onPress={takePhoto}>
              <Text style={styles.photoButtonText}>📷 촬영</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.photoButton} onPress={pickImage}>
              <Text style={styles.photoButtonText}>🖼️ 갤러리</Text>
            </TouchableOpacity>
          </View>
          {photo && (
            <View style={styles.photoPreview}>
              <Image source={{ uri: photo }} style={styles.photoImage} />
              <TouchableOpacity
                style={styles.removePhotoButton}
                onPress={() => setPhoto(null)}
              >
                <Text style={styles.removePhotoButtonText}>❌</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>

        {/* 액션 버튼들 */}
        <View style={styles.actionButtons}>
          <TouchableOpacity
            style={[styles.actionButton, styles.submitButton]}
            onPress={submitInventory}
            disabled={loading || !barcode.trim() || !quantity.trim()}
          >
            {loading ? (
              <ActivityIndicator color="white" />
            ) : (
              <Text style={styles.actionButtonText}>재고 조사 완료</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.clearButton]}
            onPress={clearForm}
          >
            <Text style={styles.actionButtonText}>초기화</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* 최근 기록 */}
      <View style={styles.historyCard}>
        <Text style={styles.cardTitle}>📋 최근 재고 조사 기록</Text>
        {inventoryHistory.length > 0 ? (
          inventoryHistory.map((item, index) => (
            <View key={index} style={styles.historyItem}>
              <View style={styles.historyHeader}>
                <Text style={styles.historyBarcode}>{item.barcode}</Text>
                <Text style={styles.historyQuantity}>{item.qty}개</Text>
              </View>
              <Text style={styles.historyTime}>
                {new Date(item.created_at).toLocaleString('ko-KR')}
              </Text>
              {item.photo_url && (
                <Text style={styles.historyPhoto}>📷 사진 첨부됨</Text>
              )}
            </View>
          ))
        ) : (
          <Text style={styles.noHistoryText}>재고 조사 기록이 없습니다.</Text>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#4CAF50',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: 'white',
    opacity: 0.8,
  },
  formCard: {
    backgroundColor: 'white',
    margin: 20,
    padding: 20,
    borderRadius: 10,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333',
  },
  barcodeInput: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginRight: 10,
  },
  scanButton: {
    backgroundColor: '#2196F3',
    padding: 12,
    borderRadius: 8,
  },
  scanButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
  },
  photoButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  photoButton: {
    backgroundColor: '#FF9800',
    padding: 12,
    borderRadius: 8,
    flex: 1,
    marginHorizontal: 5,
    alignItems: 'center',
  },
  photoButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  photoPreview: {
    marginTop: 15,
    alignItems: 'center',
    position: 'relative',
  },
  photoImage: {
    width: 200,
    height: 150,
    borderRadius: 8,
  },
  removePhotoButton: {
    position: 'absolute',
    top: -10,
    right: -10,
    backgroundColor: 'red',
    borderRadius: 15,
    width: 30,
    height: 30,
    alignItems: 'center',
    justifyContent: 'center',
  },
  removePhotoButtonText: {
    color: 'white',
    fontSize: 16,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  actionButton: {
    flex: 1,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  submitButton: {
    backgroundColor: '#4CAF50',
  },
  clearButton: {
    backgroundColor: '#9E9E9E',
  },
  actionButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  historyCard: {
    backgroundColor: 'white',
    margin: 20,
    padding: 20,
    borderRadius: 10,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  historyItem: {
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    paddingVertical: 15,
  },
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  historyBarcode: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  historyQuantity: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  historyTime: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  historyPhoto: {
    fontSize: 12,
    color: '#FF9800',
    fontStyle: 'italic',
  },
  noHistoryText: {
    fontSize: 14,
    color: '#999',
    fontStyle: 'italic',
    textAlign: 'center',
    paddingVertical: 20,
  },
  scannerOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  closeButton: {
    position: 'absolute',
    top: 50,
    right: 20,
    backgroundColor: 'rgba(0,0,0,0.7)',
    padding: 10,
    borderRadius: 5,
  },
  closeButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
});
