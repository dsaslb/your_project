import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  StatusBar,
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
  Alert,
  Platform,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialIcons';

// 화면 컴포넌트들
import DashboardScreen from './src/screens/DashboardScreen';
import AnalyticsScreen from './src/screens/AnalyticsScreen';
import NotificationsScreen from './src/screens/NotificationsScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import LoginScreen from './src/screens/LoginScreen';

// 컨텍스트 및 훅
import { AuthProvider, useAuth } from './src/contexts/AuthContext';
import { NotificationProvider } from './src/contexts/NotificationContext';
import { ThemeProvider, useTheme } from './src/contexts/ThemeContext';

// 유틸리티
import { API_BASE_URL } from './src/utils/config';
import { checkNetworkStatus } from './src/utils/network';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// 탭 네비게이터
function TabNavigator() {
  const { theme } = useTheme();
  const { user } = useAuth();

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          switch (route.name) {
            case 'Dashboard':
              iconName = 'dashboard';
              break;
            case 'Analytics':
              iconName = 'analytics';
              break;
            case 'Notifications':
              iconName = 'notifications';
              break;
            case 'Profile':
              iconName = 'person';
              break;
            default:
              iconName = 'home';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.gray,
        tabBarStyle: {
          backgroundColor: theme.colors.background,
          borderTopColor: theme.colors.border,
          paddingBottom: Platform.OS === 'ios' ? 20 : 10,
          paddingTop: 10,
          height: Platform.OS === 'ios' ? 90 : 70,
        },
        headerStyle: {
          backgroundColor: theme.colors.primary,
        },
        headerTintColor: theme.colors.white,
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{ title: '대시보드' }}
      />
      <Tab.Screen 
        name="Analytics" 
        component={AnalyticsScreen}
        options={{ title: '분석' }}
      />
      <Tab.Screen 
        name="Notifications" 
        component={NotificationsScreen}
        options={{ 
          title: '알림',
          tabBarBadge: user?.unreadNotifications || undefined,
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{ title: '프로필' }}
      />
    </Tab.Navigator>
  );
}

// 메인 앱 컴포넌트
function AppContent() {
  const { user, isLoading } = useAuth();
  const { theme } = useTheme();
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    // 네트워크 상태 모니터링
    const checkNetwork = async () => {
      const networkStatus = await checkNetworkStatus();
      setIsOnline(networkStatus);
      
      if (!networkStatus) {
        Alert.alert(
          '네트워크 오류',
          '인터넷 연결을 확인해주세요.',
          [{ text: '확인' }]
        );
      }
    };

    checkNetwork();
    const interval = setInterval(checkNetwork, 30000); // 30초마다 체크

    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: theme.colors.background }]}>
        <Text style={[styles.loadingText, { color: theme.colors.text }]}>
          로딩 중...
        </Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <StatusBar 
        barStyle={theme.dark ? 'light-content' : 'dark-content'}
        backgroundColor={theme.colors.primary}
      />
      
      {!isOnline && (
        <View style={styles.offlineBanner}>
          <Text style={styles.offlineText}>오프라인 모드</Text>
        </View>
      )}

      <NavigationContainer theme={theme}>
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          {user ? (
            <Stack.Screen name="Main" component={TabNavigator} />
          ) : (
            <Stack.Screen name="Login" component={LoginScreen} />
          )}
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaView>
  );
}

// 루트 앱 컴포넌트
export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <NotificationProvider>
          <AppContent />
        </NotificationProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 18,
    fontWeight: '600',
  },
  offlineBanner: {
    backgroundColor: '#ff6b6b',
    padding: 10,
    alignItems: 'center',
  },
  offlineText: {
    color: 'white',
    fontWeight: '600',
  },
}); 