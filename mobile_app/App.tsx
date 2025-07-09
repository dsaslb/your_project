import React, { useEffect, useState } from 'react';
import {
  SafeAreaView,
  StatusBar,
  StyleSheet,
  View,
  Text,
  Alert,
  Platform,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Notifications from 'expo-notifications';
import * as Network from 'expo-network';
import { Ionicons } from '@expo/vector-icons';
import 'react-native-gesture-handler';

// 화면 컴포넌트들
import DashboardScreen from './src/screens/DashboardScreen';
import StaffScreen from './src/screens/StaffScreen';
import InventoryScreen from './src/screens/InventoryScreen';
import OrdersScreen from './src/screens/OrdersScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import LoginScreen from './src/screens/LoginScreen';

// 컨텍스트
import { AuthProvider, useAuth } from './src/contexts/AuthContext';
import { NetworkProvider, useNetwork } from './src/contexts/NetworkContext';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// 푸시 알림 설정
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

// 탭 네비게이션
function TabNavigator() {
  const { isOnline } = useNetwork();

  return (
    <Tab.Navigator
      screenOptions={({ route }: { route: any }) => ({
        tabBarIcon: ({ focused, color, size }: { focused: boolean; color: string; size: number }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'Dashboard') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Staff') {
            iconName = focused ? 'people' : 'people-outline';
          } else if (route.name === 'Inventory') {
            iconName = focused ? 'cube' : 'cube-outline';
          } else if (route.name === 'Orders') {
            iconName = focused ? 'list' : 'list-outline';
          } else if (route.name === 'Settings') {
            iconName = focused ? 'settings' : 'settings-outline';
          } else {
            iconName = 'help-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#3B82F6',
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{ title: '대시보드' }}
      />
      <Tab.Screen 
        name="Staff" 
        component={StaffScreen}
        options={{ title: '직원 관리' }}
      />
      <Tab.Screen 
        name="Inventory" 
        component={InventoryScreen}
        options={{ title: '재고 관리' }}
      />
      <Tab.Screen 
        name="Orders" 
        component={OrdersScreen}
        options={{ title: '주문 관리' }}
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{ title: '설정' }}
      />
    </Tab.Navigator>
  );
}

// 메인 네비게이션
function MainNavigator() {
  const { isAuthenticated } = useAuth();

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {!isAuthenticated ? (
        <Stack.Screen name="Login" component={LoginScreen} />
      ) : (
        <Stack.Screen name="Main" component={TabNavigator} />
      )}
    </Stack.Navigator>
  );
}

// 메인 앱 컴포넌트
function AppContent() {
  const [isReady, setIsReady] = useState(false);
  const { isOnline } = useNetwork();

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // 네트워크 상태 확인
      const networkState = await Network.getNetworkStateAsync();
      console.log('네트워크 상태:', networkState);

      // 푸시 알림 권한 요청
      const { status } = await Notifications.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('알림 권한', '푸시 알림을 받으려면 권한이 필요합니다.');
      }

      // 푸시 토큰 가져오기
      const token = await Notifications.getExpoPushTokenAsync();
      console.log('푸시 토큰:', token);

      // 오프라인 데이터 동기화
      await syncOfflineData();

      setIsReady(true);
    } catch (error) {
      console.error('앱 초기화 오류:', error);
      setIsReady(true); // 오류가 있어도 앱은 실행
    }
  };

  const syncOfflineData = async () => {
    try {
      const offlineData = await AsyncStorage.getItem('offline_data');
      if (offlineData && isOnline) {
        const data = JSON.parse(offlineData);
        // TODO: 서버와 동기화
        console.log('오프라인 데이터 동기화:', data);
        await AsyncStorage.removeItem('offline_data');
      }
    } catch (error) {
      console.error('오프라인 데이터 동기화 오류:', error);
    }
  };

  if (!isReady) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>앱 로딩 중...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      <NavigationContainer>
        <MainNavigator />
      </NavigationContainer>
      
      {/* 네트워크 상태 표시 */}
      {!isOnline && (
        <View style={styles.offlineBanner}>
          <Text style={styles.offlineText}>오프라인 모드</Text>
        </View>
      )}
    </SafeAreaView>
  );
}

// 스타일
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  loadingText: {
    fontSize: 18,
    color: '#666666',
  },
  offlineBanner: {
    position: 'absolute',
    top: Platform.OS === 'ios' ? 50 : 30,
    left: 0,
    right: 0,
    backgroundColor: '#EF4444',
    paddingVertical: 8,
    paddingHorizontal: 16,
    alignItems: 'center',
  },
  offlineText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
});

// 앱 래퍼
export default function App() {
  return (
    <AuthProvider>
      <NetworkProvider>
        <AppContent />
      </NetworkProvider>
    </AuthProvider>
  );
} 