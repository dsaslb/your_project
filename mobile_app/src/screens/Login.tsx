/**
 * 🔐 로그인 화면
 * 
 * 모바일 앱 사용자 인증
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { mobileAPI } from '../api/client';

export default function LoginScreen({ navigation }: any) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      Alert.alert('오류', '사용자명과 비밀번호를 입력해주세요.');
      return;
    }

    setLoading(true);
    try {
      const result = await mobileAPI.login(username.trim(), password.trim());
      
      if (result.token) {
        // 토큰과 사용자 정보 저장
        await AsyncStorage.setItem('token', result.token);
        await AsyncStorage.setItem('user', JSON.stringify(result.user));
        
        Alert.alert(
          '로그인 성공',
          `${result.user.username}님 환영합니다!`,
          [
            {
              text: '확인',
              onPress: () => navigation.navigate('Main')
            }
          ]
        );
      } else {
        Alert.alert('오류', '로그인에 실패했습니다.');
      }
    } catch (error: any) {
      console.error('로그인 오류:', error);
      
      let errorMessage = '로그인에 실패했습니다.';
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      }
      
      Alert.alert('로그인 실패', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    // 데모 계정으로 로그인 (테스트용)
    setUsername('demo');
    setPassword('demo123');
    
    setLoading(true);
    try {
      // 실제 API 호출 대신 데모 데이터 사용
      const demoUser = {
        token: 'demo-token-12345',
        user: {
          id: 1,
          username: 'demo',
          role: 'employee'
        }
      };
      
      await AsyncStorage.setItem('token', demoUser.token);
      await AsyncStorage.setItem('user', JSON.stringify(demoUser.user));
      
      Alert.alert(
        '데모 로그인 성공',
        '데모 계정으로 로그인되었습니다.',
        [
          {
            text: '확인',
            onPress: () => navigation.navigate('Main')
          }
        ]
      );
    } catch (error) {
      Alert.alert('오류', '데모 로그인에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        {/* 로고 및 제목 */}
        <View style={styles.header}>
          <Text style={styles.logo}>🏢</Text>
          <Text style={styles.title}>비즈니스 관리 시스템</Text>
          <Text style={styles.subtitle}>모바일 앱</Text>
        </View>

        {/* 로그인 폼 */}
        <View style={styles.formCard}>
          <Text style={styles.formTitle}>🔐 로그인</Text>
          
          <View style={styles.inputGroup}>
            <Text style={styles.label}>사용자명</Text>
            <TextInput
              style={styles.textInput}
              value={username}
              onChangeText={setUsername}
              placeholder="사용자명을 입력하세요"
              autoCapitalize="none"
              autoCorrect={false}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>비밀번호</Text>
            <TextInput
              style={styles.textInput}
              value={password}
              onChangeText={setPassword}
              placeholder="비밀번호를 입력하세요"
              secureTextEntry
              autoCapitalize="none"
            />
          </View>

          {/* 로그인 버튼 */}
          <TouchableOpacity
            style={[styles.loginButton, loading && styles.disabledButton]}
            onPress={handleLogin}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="white" />
            ) : (
              <Text style={styles.loginButtonText}>로그인</Text>
            )}
          </TouchableOpacity>

          {/* 데모 로그인 버튼 */}
          <TouchableOpacity
            style={styles.demoButton}
            onPress={handleDemoLogin}
            disabled={loading}
          >
            <Text style={styles.demoButtonText}>🎯 데모 로그인 (테스트용)</Text>
          </TouchableOpacity>
        </View>

        {/* 도움말 */}
        <View style={styles.helpCard}>
          <Text style={styles.helpTitle}>💡 도움말</Text>
          <Text style={styles.helpText}>
            • 사용자명과 비밀번호를 입력하여 로그인하세요{'\n'}
            • 데모 계정으로 테스트할 수 있습니다{'\n'}
            • 로그인 후 출퇴근, 재고 조사 등의 기능을 사용할 수 있습니다
          </Text>
        </View>

        {/* 테스트 계정 정보 */}
        <View style={styles.testAccountCard}>
          <Text style={styles.testAccountTitle}>🧪 테스트 계정</Text>
          <Text style={styles.testAccountText}>
            사용자명: demo{'\n'}
            비밀번호: demo123
          </Text>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContainer: {
    flexGrow: 1,
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginTop: 60,
    marginBottom: 40,
  },
  logo: {
    fontSize: 60,
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  formCard: {
    backgroundColor: 'white',
    padding: 30,
    borderRadius: 15,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    marginBottom: 20,
  },
  formTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 25,
    textAlign: 'center',
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  textInput: {
    borderWidth: 2,
    borderColor: '#e1e1e1',
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    backgroundColor: '#fafafa',
  },
  loginButton: {
    backgroundColor: '#2196F3',
    padding: 18,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 15,
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  loginButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  demoButton: {
    backgroundColor: '#FF9800',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  demoButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  helpCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 10,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    marginBottom: 20,
  },
  helpTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  helpText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  testAccountCard: {
    backgroundColor: '#e3f2fd',
    padding: 20,
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#2196F3',
  },
  testAccountTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1976d2',
    marginBottom: 10,
  },
  testAccountText: {
    fontSize: 14,
    color: '#1976d2',
    lineHeight: 20,
  },
});
