import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Provider as PaperProvider } from 'react-native-paper';
import { QueryClient, QueryClientProvider } from 'react-query';
import * as SplashScreen from 'expo-splash-screen';
import * as Notifications from 'expo-notifications';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

// Contexts
import { AuthProvider } from './src/contexts/AuthContext';
import { NetworkProvider } from './src/contexts/NetworkContext';

// Screens
import LoginScreen from './src/screens/auth/LoginScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import InventoryScreen from './src/screens/InventoryScreen';
import OrdersScreen from './src/screens/OrdersScreen';
import AttendanceScreen from './src/screens/AttendanceScreen';
import SettingsScreen from './src/screens/SettingsScreen';

// Services
import { initializeApp } from './src/services/appInitializer';
import { setupNotifications } from './src/services/notificationService';

// Types
import { RootStackParamList } from './src/types/navigation';

// Keep the splash screen visible while we fetch resources
SplashScreen.preventAutoHideAsync();

// Configure notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

const Stack = createStackNavigator();
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});

export default function App() {
  const [appIsReady, setAppIsReady] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    async function prepare() {
      try {
        // Initialize app services
        await initializeApp();
        
        // Setup notifications
        await setupNotifications();
        
        // Check authentication status
        // This would typically check for stored tokens
        // For now, we'll start with unauthenticated state
        
      } catch (error) {
        console.warn('Error during app initialization:', error);
      } finally {
        setAppIsReady(true);
      }
    }

    prepare();
  }, []);

  useEffect(() => {
    if (appIsReady) {
      // Hide splash screen
      SplashScreen.hideAsync();
    }
  }, [appIsReady]);

  if (!appIsReady) {
    return null; // Keep splash screen visible
  }

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <QueryClientProvider client={queryClient}>
        <PaperProvider>
          <NetworkProvider>
            <AuthProvider>
              <NavigationContainer>
                <StatusBar style="auto" />
                <Stack.Navigator
                  screenOptions={{
                    headerStyle: {
                      backgroundColor: '#3B82F6',
                    },
                    headerTintColor: '#fff',
                    headerTitleStyle: {
                      fontWeight: 'bold',
                    },
                  }}
                >
                  {!isAuthenticated ? (
                    // Auth screens
                    <Stack.Screen
                      name="Login"
                      component={LoginScreen}
                      options={{
                        title: 'Your Program Mobile',
                        headerShown: false,
                      }}
                    />
                  ) : (
                    // Main app screens
                    <>
                      <Stack.Screen
                        name="Dashboard"
                        component={DashboardScreen}
                        options={{
                          title: '대시보드',
                        }}
                      />
                      <Stack.Screen
                        name="Inventory"
                        component={InventoryScreen}
                        options={{
                          title: '재고 관리',
                        }}
                      />
                      <Stack.Screen
                        name="Orders"
                        component={OrdersScreen}
                        options={{
                          title: '주문 관리',
                        }}
                      />
                      <Stack.Screen
                        name="Attendance"
                        component={AttendanceScreen}
                        options={{
                          title: '출근 관리',
                        }}
                      />
                      <Stack.Screen
                        name="Settings"
                        component={SettingsScreen}
                        options={{
                          title: '설정',
                        }}
                      />
                    </>
                  )}
                </Stack.Navigator>
              </NavigationContainer>
            </AuthProvider>
          </NetworkProvider>
        </PaperProvider>
      </QueryClientProvider>
    </GestureHandlerRootView>
  );
} 