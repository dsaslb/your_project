import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createDrawerNavigator } from '@react-navigation/drawer';
import { useAuth } from '../contexts/AuthContext';
import Icon from 'react-native-vector-icons/MaterialIcons';

// Auth Screens
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';
import ForgotPasswordScreen from '../screens/auth/ForgotPasswordScreen';

// Main Screens
import DashboardScreen from '../screens/main/DashboardScreen';
import ScheduleScreen from '../screens/main/ScheduleScreen';
import AttendanceScreen from '../screens/main/AttendanceScreen';
import OrdersScreen from '../screens/main/OrdersScreen';
import InventoryScreen from '../screens/main/InventoryScreen';
import CleaningScreen from '../screens/main/CleaningScreen';
import NotificationsScreen from '../screens/main/NotificationsScreen';

// Admin Screens
import StaffManagementScreen from '../screens/admin/StaffManagementScreen';
import ReportsScreen from '../screens/admin/ReportsScreen';
import AnalyticsScreen from '../screens/admin/AnalyticsScreen';
import SettingsScreen from '../screens/admin/SettingsScreen';

// Advanced Features
import AdvancedFeaturesScreen from '../screens/advanced/AdvancedFeaturesScreen';
import ChatbotScreen from '../screens/advanced/ChatbotScreen';
import VoiceRecognitionScreen from '../screens/advanced/VoiceRecognitionScreen';
import ImageAnalysisScreen from '../screens/advanced/ImageAnalysisScreen';
import TranslationScreen from '../screens/advanced/TranslationScreen';

// Common Screens
import ProfileScreen from '../screens/common/ProfileScreen';
import SettingsScreen as CommonSettingsScreen from '../screens/common/SettingsScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();
const Drawer = createDrawerNavigator();

// Auth Navigator
const AuthNavigator = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="Login" component={LoginScreen} />
    <Stack.Screen name="Register" component={RegisterScreen} />
    <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
  </Stack.Navigator>
);

// Employee Tab Navigator
const EmployeeTabNavigator = () => (
  <Tab.Navigator
    screenOptions={({ route }) => ({
      tabBarIcon: ({ focused, color, size }) => {
        let iconName: string;

        switch (route.name) {
          case 'Dashboard':
            iconName = 'dashboard';
            break;
          case 'Schedule':
            iconName = 'schedule';
            break;
          case 'Attendance':
            iconName = 'person';
            break;
          case 'Orders':
            iconName = 'shopping-cart';
            break;
          case 'Notifications':
            iconName = 'notifications';
            break;
          default:
            iconName = 'help';
        }

        return <Icon name={iconName} size={size} color={color} />;
      },
      tabBarActiveTintColor: '#3b82f6',
      tabBarInactiveTintColor: 'gray',
    })}
  >
    <Tab.Screen name="Dashboard" component={DashboardScreen} />
    <Tab.Screen name="Schedule" component={ScheduleScreen} />
    <Tab.Screen name="Attendance" component={AttendanceScreen} />
    <Tab.Screen name="Orders" component={OrdersScreen} />
    <Tab.Screen name="Notifications" component={NotificationsScreen} />
  </Tab.Navigator>
);

// Manager Tab Navigator
const ManagerTabNavigator = () => (
  <Tab.Navigator
    screenOptions={({ route }) => ({
      tabBarIcon: ({ focused, color, size }) => {
        let iconName: string;

        switch (route.name) {
          case 'Dashboard':
            iconName = 'dashboard';
            break;
          case 'Staff':
            iconName = 'people';
            break;
          case 'Inventory':
            iconName = 'inventory';
            break;
          case 'Reports':
            iconName = 'assessment';
            break;
          case 'Settings':
            iconName = 'settings';
            break;
          default:
            iconName = 'help';
        }

        return <Icon name={iconName} size={size} color={color} />;
      },
      tabBarActiveTintColor: '#3b82f6',
      tabBarInactiveTintColor: 'gray',
    })}
  >
    <Tab.Screen name="Dashboard" component={DashboardScreen} />
    <Tab.Screen name="Staff" component={StaffManagementScreen} />
    <Tab.Screen name="Inventory" component={InventoryScreen} />
    <Tab.Screen name="Reports" component={ReportsScreen} />
    <Tab.Screen name="Settings" component={SettingsScreen} />
  </Tab.Navigator>
);

// Admin Tab Navigator
const AdminTabNavigator = () => (
  <Tab.Navigator
    screenOptions={({ route }) => ({
      tabBarIcon: ({ focused, color, size }) => {
        let iconName: string;

        switch (route.name) {
          case 'Dashboard':
            iconName = 'dashboard';
            break;
          case 'Analytics':
            iconName = 'analytics';
            break;
          case 'Staff':
            iconName = 'people';
            break;
          case 'Reports':
            iconName = 'assessment';
            break;
          case 'Settings':
            iconName = 'settings';
            break;
          default:
            iconName = 'help';
        }

        return <Icon name={iconName} size={size} color={color} />;
      },
      tabBarActiveTintColor: '#3b82f6',
      tabBarInactiveTintColor: 'gray',
    })}
  >
    <Tab.Screen name="Dashboard" component={DashboardScreen} />
    <Tab.Screen name="Analytics" component={AnalyticsScreen} />
    <Tab.Screen name="Staff" component={StaffManagementScreen} />
    <Tab.Screen name="Reports" component={ReportsScreen} />
    <Tab.Screen name="Settings" component={SettingsScreen} />
  </Tab.Navigator>
);

// Main Stack Navigator
const MainStackNavigator = () => {
  const { user } = useAuth();

  const getTabNavigator = () => {
    if (!user) return EmployeeTabNavigator;
    
    switch (user.role) {
      case 'admin':
      case 'super_admin':
        return AdminTabNavigator;
      case 'manager':
        return ManagerTabNavigator;
      default:
        return EmployeeTabNavigator;
    }
  };

  const TabNavigator = getTabNavigator();

  return (
    <Stack.Navigator>
      <Stack.Screen 
        name="MainTabs" 
        component={TabNavigator}
        options={{ headerShown: false }}
      />
      <Stack.Screen name="Profile" component={ProfileScreen} />
      <Stack.Screen name="CommonSettings" component={CommonSettingsScreen} />
      <Stack.Screen name="AdvancedFeatures" component={AdvancedFeaturesScreen} />
      <Stack.Screen name="Chatbot" component={ChatbotScreen} />
      <Stack.Screen name="VoiceRecognition" component={VoiceRecognitionScreen} />
      <Stack.Screen name="ImageAnalysis" component={ImageAnalysisScreen} />
      <Stack.Screen name="Translation" component={TranslationScreen} />
      <Stack.Screen name="Cleaning" component={CleaningScreen} />
    </Stack.Navigator>
  );
};

// Main App Navigator
const AppNavigator = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    // Loading screen would go here
    return null;
  }

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {user ? (
        <Stack.Screen name="Main" component={MainStackNavigator} />
      ) : (
        <Stack.Screen name="Auth" component={AuthNavigator} />
      )}
    </Stack.Navigator>
  );
};

export default AppNavigator; 