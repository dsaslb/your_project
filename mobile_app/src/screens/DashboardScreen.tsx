import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useAuth } from '../contexts/AuthContext';

const DashboardScreen: React.FC = () => {
  const { user } = useAuth();

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>대시보드</Text>
        <Text style={styles.subtitle}>안녕하세요, {user?.name}님!</Text>
      </View>
      
      <View style={styles.content}>
        <Text style={styles.sectionTitle}>오늘의 요약</Text>
        <View style={styles.card}>
          <Text style={styles.cardTitle}>주문 현황</Text>
          <Text style={styles.cardValue}>0건</Text>
        </View>
        
        <View style={styles.card}>
          <Text style={styles.cardTitle}>재고 알림</Text>
          <Text style={styles.cardValue}>0건</Text>
        </View>
        
        <View style={styles.card}>
          <Text style={styles.cardTitle}>직원 출근</Text>
          <Text style={styles.cardValue}>0명</Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#3B82F6',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  subtitle: {
    fontSize: 16,
    color: '#ffffff',
    marginTop: 5,
  },
  content: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333333',
  },
  card: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666666',
    marginBottom: 10,
  },
  cardValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#3B82F6',
  },
});

export default DashboardScreen; 