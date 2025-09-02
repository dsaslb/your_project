/**
 * 🧭 앱 네비게이션
 * 
 * 모바일 앱의 메인 네비게이션 구조
 */

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { Ionicons } from '@expo/vector-icons';

// 화면들 import
import AttendanceScreen from '../screens/Attendance';
import InventoryCheckScreen from '../screens/InventoryCheck';
import DashboardScreen from '../screens/Dashboard';
import LoginScreen from '../screens/Login';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// 메인 탭 네비게이터
function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'Dashboard') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Attendance') {
            iconName = focused ? 'time' : 'time-outline';
          } else if (route.name === 'Inventory') {
            iconName = focused ? 'cube' : 'cube-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#2196F3',
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
        name="Attendance" 
        component={AttendanceScreen}
        options={{ title: '출퇴근' }}
      />
      <Tab.Screen 
        name="Inventory" 
        component={InventoryCheckScreen}
        options={{ title: '재고' }}
      />
    </Tab.Navigator>
  );
}

// 메인 앱 네비게이터
export default function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Main">
        <Stack.Screen 
          name="Main" 
          component={MainTabNavigator}
          options={{ headerShown: false }}
        />
        <Stack.Screen 
          name="Login" 
          component={LoginScreen}
          options={{ title: '로그인' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
