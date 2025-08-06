import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Switch,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface UserProfile {
  name: string;
  email: string;
  role: string;
  store: string;
  avatar: string;
}

export default function ProfileScreen() {
  const [profile] = useState<UserProfile>({
    name: '김매니저',
    email: 'manager@example.com',
    role: '매니저',
    store: '강남점',
    avatar: '',
  });

  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [darkModeEnabled, setDarkModeEnabled] = useState(false);

  const ProfileSection = ({ title, children }: { title: string; children: React.ReactNode }) => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {children}
    </View>
  );

  const ProfileItem = ({ icon, title, value, onPress }: {
    icon: string;
    title: string;
    value?: string;
    onPress?: () => void;
  }) => (
    <TouchableOpacity 
      style={styles.profileItem} 
      onPress={onPress}
      disabled={!onPress}
    >
      <View style={styles.profileItemLeft}>
        <Ionicons name={icon as any} size={20} color="#6b7280" />
        <Text style={styles.profileItemTitle}>{title}</Text>
      </View>
      <View style={styles.profileItemRight}>
        {value && <Text style={styles.profileItemValue}>{value}</Text>}
        {onPress && <Ionicons name="chevron-forward" size={20} color="#6b7280" />}
      </View>
    </TouchableOpacity>
  );

  const SettingItem = ({ icon, title, value, onPress, showSwitch = false, switchValue = false, onSwitchChange }: {
    icon: string;
    title: string;
    value?: string;
    onPress?: () => void;
    showSwitch?: boolean;
    switchValue?: boolean;
    onSwitchChange?: (value: boolean) => void;
  }) => (
    <TouchableOpacity 
      style={styles.profileItem} 
      onPress={onPress}
      disabled={!onPress || showSwitch}
    >
      <View style={styles.profileItemLeft}>
        <Ionicons name={icon as any} size={20} color="#6b7280" />
        <Text style={styles.profileItemTitle}>{title}</Text>
      </View>
      <View style={styles.profileItemRight}>
        {value && <Text style={styles.profileItemValue}>{value}</Text>}
        {showSwitch && (
          <Switch
            value={switchValue}
            onValueChange={onSwitchChange}
            trackColor={{ false: '#e5e7eb', true: '#3b82f6' }}
            thumbColor={switchValue ? '#ffffff' : '#ffffff'}
          />
        )}
        {onPress && !showSwitch && <Ionicons name="chevron-forward" size={20} color="#6b7280" />}
      </View>
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container}>
      {/* 헤더 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>프로필</Text>
      </View>

      {/* 프로필 정보 */}
      <View style={styles.profileHeader}>
        <View style={styles.avatarContainer}>
          <Ionicons name="person" size={40} color="white" />
        </View>
        <View style={styles.profileInfo}>
          <Text style={styles.profileName}>{profile.name}</Text>
          <Text style={styles.profileRole}>{profile.role}</Text>
          <Text style={styles.profileStore}>{profile.store}</Text>
        </View>
        <TouchableOpacity 
          style={styles.editButton}
          onPress={() => Alert.alert('프로필 수정', '프로필 수정 기능')}
        >
          <Ionicons name="create" size={20} color="#3b82f6" />
        </TouchableOpacity>
      </View>

      {/* 계정 정보 */}
      <ProfileSection title="계정 정보">
        <ProfileItem
          icon="person"
          title="이름"
          value={profile.name}
          onPress={() => Alert.alert('이름 수정', '이름 수정 기능')}
        />
        <ProfileItem
          icon="mail"
          title="이메일"
          value={profile.email}
          onPress={() => Alert.alert('이메일 수정', '이메일 수정 기능')}
        />
        <ProfileItem
          icon="business"
          title="소속 매장"
          value={profile.store}
        />
        <ProfileItem
          icon="shield-checkmark"
          title="역할"
          value={profile.role}
        />
      </ProfileSection>

      {/* 설정 */}
      <ProfileSection title="설정">
        <SettingItem
          icon="notifications"
          title="알림"
          showSwitch={true}
          switchValue={notificationsEnabled}
          onSwitchChange={setNotificationsEnabled}
        />
        <SettingItem
          icon="moon"
          title="다크 모드"
          showSwitch={true}
          switchValue={darkModeEnabled}
          onSwitchChange={setDarkModeEnabled}
        />
        <ProfileItem
          icon="language"
          title="언어"
          value="한국어"
          onPress={() => Alert.alert('언어 설정', '언어 설정 기능')}
        />
        <ProfileItem
          icon="time"
          title="시간대"
          value="Asia/Seoul"
          onPress={() => Alert.alert('시간대 설정', '시간대 설정 기능')}
        />
      </ProfileSection>

      {/* 보안 */}
      <ProfileSection title="보안">
        <ProfileItem
          icon="lock-closed"
          title="비밀번호 변경"
          onPress={() => Alert.alert('비밀번호 변경', '비밀번호 변경 기능')}
        />
        <ProfileItem
          icon="finger-print"
          title="생체 인증"
          onPress={() => Alert.alert('생체 인증', '생체 인증 설정')}
        />
        <ProfileItem
          icon="shield-checkmark"
          title="2단계 인증"
          onPress={() => Alert.alert('2단계 인증', '2단계 인증 설정')}
        />
      </ProfileSection>

      {/* 지원 */}
      <ProfileSection title="지원">
        <ProfileItem
          icon="help-circle"
          title="도움말"
          onPress={() => Alert.alert('도움말', '도움말 페이지')}
        />
        <ProfileItem
          icon="document-text"
          title="이용약관"
          onPress={() => Alert.alert('이용약관', '이용약관 페이지')}
        />
        <ProfileItem
          icon="shield"
          title="개인정보처리방침"
          onPress={() => Alert.alert('개인정보처리방침', '개인정보처리방침 페이지')}
        />
        <ProfileItem
          icon="chatbubble"
          title="고객 지원"
          onPress={() => Alert.alert('고객 지원', '고객 지원 연락처')}
        />
      </ProfileSection>

      {/* 앱 정보 */}
      <ProfileSection title="앱 정보">
        <ProfileItem
          icon="information-circle"
          title="버전"
          value="1.0.0"
        />
        <ProfileItem
          icon="refresh"
          title="업데이트 확인"
          onPress={() => Alert.alert('업데이트', '최신 버전입니다.')}
        />
      </ProfileSection>

      {/* 로그아웃 */}
      <View style={styles.logoutSection}>
        <TouchableOpacity 
          style={styles.logoutButton}
          onPress={() => Alert.alert('로그아웃', '정말 로그아웃하시겠습니까?')}
        >
          <Ionicons name="log-out" size={20} color="#ef4444" />
          <Text style={styles.logoutText}>로그아웃</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    padding: 20,
    backgroundColor: '#3b82f6',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    backgroundColor: 'white',
    margin: 16,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  avatarContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#3b82f6',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  profileInfo: {
    flex: 1,
  },
  profileName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  profileRole: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 2,
  },
  profileStore: {
    fontSize: 14,
    color: '#3b82f6',
  },
  editButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#eff6ff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 12,
    marginHorizontal: 16,
  },
  profileItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 20,
    backgroundColor: 'white',
    marginHorizontal: 16,
    marginBottom: 1,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  profileItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  profileItemTitle: {
    fontSize: 16,
    color: '#1f2937',
    marginLeft: 12,
  },
  profileItemRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  profileItemValue: {
    fontSize: 14,
    color: '#6b7280',
    marginRight: 8,
  },
  logoutSection: {
    padding: 16,
    marginBottom: 32,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    backgroundColor: 'white',
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  logoutText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ef4444',
    marginLeft: 8,
  },
}); 