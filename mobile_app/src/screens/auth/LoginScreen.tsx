import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Image,
} from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';

const LoginScreen: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      Alert.alert('오류', '이메일과 비밀번호를 입력해주세요.');
      return;
    }

    setIsLoading(true);
    try {
      const success = await login(email.trim(), password);
      if (!success) {
        Alert.alert('로그인 실패', '이메일 또는 비밀번호를 확인해주세요.');
      }
    } catch (error) {
      Alert.alert('오류', '로그인 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickLogin = async (role: string) => {
    setIsLoading(true);
    try {
      let testEmail = '';
      let testPassword = '';

      switch (role) {
        case 'admin':
          testEmail = 'admin@your_program.com';
          testPassword = 'admin123';
          break;
        case 'manager':
          testEmail = 'manager@your_program.com';
          testPassword = 'manager123';
          break;
        case 'employee':
          testEmail = 'employee@your_program.com';
          testPassword = 'employee123';
          break;
        default:
          testEmail = 'admin@your_program.com';
          testPassword = 'admin123';
      }

      const success = await login(testEmail, testPassword);
      if (!success) {
        Alert.alert('로그인 실패', '테스트 계정 로그인에 실패했습니다.');
      }
    } catch (error) {
      Alert.alert('오류', '로그인 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoidingView}
      >
        <ScrollView contentContainerStyle={styles.scrollContainer}>
          {/* Logo and Title */}
          <View style={styles.header}>
            <View style={styles.logoContainer}>
              <Icon name="your_program" size={80} color="#3b82f6" />
            </View>
            <Text style={styles.title}>레스토랑 매니저</Text>
            <Text style={styles.subtitle}>스마트한 레스토랑 관리</Text>
          </View>

          {/* Login Form */}
          <View style={styles.form}>
            <View style={styles.inputContainer}>
              <Icon name="email" size={20} color="#6b7280" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="이메일"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
              />
            </View>

            <View style={styles.inputContainer}>
              <Icon name="lock" size={20} color="#6b7280" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="비밀번호"
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPassword}
                autoCapitalize="none"
              />
              <TouchableOpacity
                onPress={() => setShowPassword(!showPassword)}
                style={styles.passwordToggle}
              >
                <Icon
                  name={showPassword ? 'visibility' : 'visibility-off'}
                  size={20}
                  color="#6b7280"
                />
              </TouchableOpacity>
            </View>

            <TouchableOpacity
              style={[styles.loginButton, isLoading && styles.loginButtonDisabled]}
              onPress={handleLogin}
              disabled={isLoading}
            >
              <Text style={styles.loginButtonText}>
                {isLoading ? '로그인 중...' : '로그인'}
              </Text>
            </TouchableOpacity>

            {/* Quick Login Buttons */}
            <View style={styles.quickLoginContainer}>
              <Text style={styles.quickLoginTitle}>빠른 로그인 (테스트용)</Text>
              <View style={styles.quickLoginButtons}>
                <TouchableOpacity
                  style={[styles.quickLoginButton, styles.adminButton]}
                  onPress={() => handleQuickLogin('admin')}
                  disabled={isLoading}
                >
                  <Text style={styles.quickLoginButtonText}>관리자</Text>
                </TouchableOpacity>
                
                <TouchableOpacity
                  style={[styles.quickLoginButton, styles.managerButton]}
                  onPress={() => handleQuickLogin('manager')}
                  disabled={isLoading}
                >
                  <Text style={styles.quickLoginButtonText}>매니저</Text>
                </TouchableOpacity>
                
                <TouchableOpacity
                  style={[styles.quickLoginButton, styles.employeeButton]}
                  onPress={() => handleQuickLogin('employee')}
                  disabled={isLoading}
                >
                  <Text style={styles.quickLoginButtonText}>직원</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Additional Options */}
            <View style={styles.optionsContainer}>
              <TouchableOpacity style={styles.optionButton}>
                <Text style={styles.optionText}>비밀번호 찾기</Text>
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.optionButton}>
                <Text style={styles.optionText}>회원가입</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Footer */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>
              © 2024 your_program Manager. All rights reserved.
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logoContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#f3f4f6',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
  },
  form: {
    marginBottom: 30,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 12,
    marginBottom: 16,
    paddingHorizontal: 16,
    backgroundColor: '#f9fafb',
  },
  inputIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    height: 50,
    fontSize: 16,
    color: '#1f2937',
  },
  passwordToggle: {
    padding: 8,
  },
  loginButton: {
    backgroundColor: '#3b82f6',
    borderRadius: 12,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 8,
  },
  loginButtonDisabled: {
    backgroundColor: '#9ca3af',
  },
  loginButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  quickLoginContainer: {
    marginTop: 24,
    marginBottom: 16,
  },
  quickLoginTitle: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 12,
  },
  quickLoginButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  quickLoginButton: {
    flex: 1,
    height: 40,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 4,
  },
  adminButton: {
    backgroundColor: '#ef4444',
  },
  managerButton: {
    backgroundColor: '#f59e0b',
  },
  employeeButton: {
    backgroundColor: '#10b981',
  },
  quickLoginButtonText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
  },
  optionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  optionButton: {
    paddingVertical: 8,
  },
  optionText: {
    color: '#3b82f6',
    fontSize: 14,
  },
  footer: {
    alignItems: 'center',
    marginTop: 20,
  },
  footerText: {
    color: '#9ca3af',
    fontSize: 12,
  },
});

export default LoginScreen; 
