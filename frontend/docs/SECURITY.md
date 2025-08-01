# 🔒 보안 강화 시스템

## 개요

이 프로젝트는 포괄적인 보안 시스템을 구현하여 사용자 데이터와 시스템을 보호합니다. XSS, CSRF, SQL 인젝션, 세션 하이재킹 등 다양한 보안 위협에 대응합니다.

## 🛡️ 주요 보안 기능

### 1. 인증 및 권한 관리
- **JWT 토큰 기반 인증**: 안전한 토큰 관리
- **자동 토큰 새로고침**: 세션 지속성 보장
- **세분화된 권한 시스템**: 모듈별 접근 제어
- **로그인 시도 제한**: 무차별 대입 공격 방지

### 2. 입력 검증 및 필터링
- **XSS 방지**: HTML 이스케이프 처리
- **SQL 인젝션 방지**: 입력 데이터 검증
- **파일 업로드 보안**: 허용된 파일 타입만 업로드
- **입력 길이 제한**: 버퍼 오버플로우 방지

### 3. 세션 보안
- **세션 타임아웃**: 비활성 시간 모니터링
- **HTTPS 강제**: 보안 연결 보장
- **세션 하이재킹 방지**: 안전한 세션 관리
- **자동 로그아웃**: 보안 위험 시 자동 세션 종료

### 4. Rate Limiting
- **API 요청 제한**: DDoS 공격 방지
- **로그인 시도 제한**: 무차별 대입 공격 방지
- **동적 임계값 조정**: 상황에 따른 제한 조정

## 🔧 보안 유틸리티

### SecurityUtils 클래스

```typescript
import { SecurityUtils } from '@/utils/security';

// HTML 이스케이프
const safeHtml = SecurityUtils.escapeHtml('<script>alert("xss")</script>');

// 입력 검증
const sanitizedInput = SecurityUtils.sanitizeInput(userInput);

// 비밀번호 강도 검증
const passwordValidation = SecurityUtils.validatePassword('MyP@ssw0rd');
console.log(passwordValidation.isValid); // true
console.log(passwordValidation.score); // 5
console.log(passwordValidation.feedback); // []

// 이메일 검증
const isValidEmail = SecurityUtils.validateEmail('user@example.com');

// 파일 업로드 검증
const fileValidation = SecurityUtils.validateFileUpload(file);
if (!fileValidation.isValid) {
  console.error(fileValidation.error);
}

// 민감한 데이터 마스킹
const maskedEmail = SecurityUtils.maskSensitiveData('user@example.com', 'email');
// 결과: "us***@example.com"

const maskedPhone = SecurityUtils.maskSensitiveData('010-1234-5678', 'phone');
// 결과: "010-****-5678"
```

### SecurityMiddleware 클래스

```typescript
import { SecurityMiddleware } from '@/utils/security';

// API 요청 검증
const canMakeRequest = SecurityMiddleware.validateApiRequest('user-123');

// 로그인 시도 검증
const canLogin = SecurityMiddleware.validateLoginAttempt('user-123');

// 로그인 잠금 상태 확인
const isLocked = SecurityMiddleware.isLoginLocked('user-123');

// 잠금 해제 시간 확인
const remainingTime = SecurityMiddleware.getLoginLockRemainingTime('user-123');
```

## 🎯 보안 설정

### SECURITY_CONFIG 상수

```typescript
export const SECURITY_CONFIG = {
  // 토큰 관련
  TOKEN_REFRESH_THRESHOLD: 5 * 60 * 1000, // 5분
  SESSION_TIMEOUT: 30 * 60 * 1000, // 30분
  
  // 로그인 시도 제한
  MAX_LOGIN_ATTEMPTS: 5,
  LOCKOUT_DURATION: 15 * 60 * 1000, // 15분
  
  // Rate Limiting
  API_RATE_LIMIT: {
    requests: 100,
    windowMs: 15 * 60 * 1000 // 15분
  },
  
  // 파일 업로드
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_FILE_TYPES: [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'application/pdf'
  ],
  
  // 입력 검증
  MAX_INPUT_LENGTH: 1000,
  MIN_PASSWORD_LENGTH: 8,
  
  // 세션 관리
  SESSION_CHECK_INTERVAL: 60 * 1000, // 1분
  INACTIVE_TIMEOUT: 20 * 60 * 1000 // 20분
};
```

## 🔐 보안 컴포넌트

### SecurityProvider

```tsx
import { SecurityProvider } from '@/components/SecurityProvider';

function App() {
  return (
    <SecurityProvider>
      <YourApp />
    </SecurityProvider>
  );
}
```

### useSecurity 훅

```tsx
import { useSecurity } from '@/components/SecurityProvider';

function LoginForm() {
  const { 
    validatePassword, 
    validateEmail, 
    checkLoginAttempts,
    isLoginLocked,
    logSecurityEvent 
  } = useSecurity();

  const handleLogin = async (credentials) => {
    // 로그인 시도 제한 확인
    if (isLoginLocked(credentials.username)) {
      setError('로그인이 잠겨있습니다.');
      return;
    }

    // 입력 검증
    const passwordValidation = validatePassword(credentials.password);
    if (!passwordValidation.isValid) {
      setError(passwordValidation.feedback.join(', '));
      return;
    }

    // 보안 로그 기록
    logSecurityEvent('login_attempt', { username: credentials.username });

    // 로그인 처리...
  };

  return (
    <form onSubmit={handleLogin}>
      {/* 폼 내용 */}
    </form>
  );
}
```

### SecurityWarning 컴포넌트

```tsx
import { SecurityWarning } from '@/components/SecurityProvider';

function Dashboard() {
  return (
    <div>
      <SecurityWarning 
        message="보안을 위해 HTTPS 연결을 사용하세요." 
        onDismiss={() => console.log('경고 닫힘')}
      />
      {/* 대시보드 내용 */}
    </div>
  );
}
```

### SecurityStatus 컴포넌트

```tsx
import { SecurityStatus } from '@/components/SecurityProvider';

function Header() {
  return (
    <header>
      <div className="flex items-center space-x-4">
        <h1>Your Program</h1>
        <SecurityStatus />
      </div>
    </header>
  );
}
```

## 🚨 보안 이벤트

### 보안 이벤트 타입

```typescript
const SECURITY_EVENTS = {
  LOGIN_ATTEMPT: 'login_attempt',
  LOGIN_SUCCESS: 'login_success',
  LOGIN_FAILURE: 'login_failure',
  LOGOUT: 'logout',
  PASSWORD_CHANGE: 'password_change',
  PERMISSION_CHANGE: 'permission_change',
  SUSPICIOUS_ACTIVITY: 'suspicious_activity',
  FILE_UPLOAD: 'file_upload',
  API_ACCESS: 'api_access'
};
```

### 보안 로그 생성

```typescript
import { SecurityUtils } from '@/utils/security';

// 보안 이벤트 로그
SecurityUtils.createSecurityLog(
  SecurityUtils.SECURITY_EVENTS.LOGIN_SUCCESS,
  'user-123',
  { ip: '192.168.1.1', userAgent: 'Mozilla/5.0...' }
);

SecurityUtils.createSecurityLog(
  SecurityUtils.SECURITY_EVENTS.SUSPICIOUS_ACTIVITY,
  'user-123',
  { activity: 'multiple_failed_logins', count: 10 }
);
```

## 🔍 보안 모니터링

### 세션 보안 체크

```typescript
const { checkSessionSecurity, refreshSession } = useSecurity();

// 주기적 세션 보안 체크
useEffect(() => {
  const interval = setInterval(() => {
    if (!checkSessionSecurity()) {
      // 보안 위험 시 자동 로그아웃
      logout();
    }
  }, 60000); // 1분마다

  return () => clearInterval(interval);
}, []);
```

### 사용자 활동 모니터링

```typescript
const { logSecurityEvent } = useSecurity();

// 사용자 활동 추적
useEffect(() => {
  const trackActivity = () => {
    logSecurityEvent('user_activity', { 
      timestamp: new Date().toISOString(),
      action: 'user_interaction'
    });
  };

  document.addEventListener('click', trackActivity);
  document.addEventListener('keypress', trackActivity);

  return () => {
    document.removeEventListener('click', trackActivity);
    document.removeEventListener('keypress', trackActivity);
  };
}, []);
```

## 🛠️ 보안 헤더

### 보안 헤더 설정

```typescript
const securityHeaders = {
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'none';"
};
```

## 📊 보안 모범 사례

### 1. 비밀번호 정책

```typescript
// 강력한 비밀번호 요구사항
const passwordRequirements = {
  minLength: 8,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSpecialChars: true,
  preventCommonPasswords: true
};
```

### 2. 입력 검증

```typescript
// 모든 사용자 입력 검증
const validateUserInput = (input: string) => {
  return SecurityUtils.sanitizeInput(input);
};

// 특수한 입력 검증
const validateEmail = (email: string) => {
  return SecurityUtils.validateEmail(email);
};

const validatePhone = (phone: string) => {
  return SecurityUtils.validatePhone(phone);
};
```

### 3. 파일 업로드 보안

```typescript
const handleFileUpload = (file: File) => {
  const validation = SecurityUtils.validateFileUpload(file);
  
  if (!validation.isValid) {
    throw new Error(validation.error);
  }
  
  // 안전한 파일 업로드 처리
  return uploadFile(file);
};
```

### 4. API 보안

```typescript
const secureApiCall = async (endpoint: string, data: any) => {
  // Rate Limiting 체크
  if (!SecurityMiddleware.validateApiRequest('user-123')) {
    throw new Error('요청이 너무 많습니다.');
  }
  
  // 보안 헤더 추가
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...SecurityUtils.getSecurityHeaders(),
    },
    body: JSON.stringify(data),
  });
  
  return response.json();
};
```

## 🚨 보안 경고 및 대응

### 1. 로그인 시도 제한

```typescript
const handleLogin = async (credentials) => {
  const identifier = credentials.username;
  
  // 잠금 상태 확인
  if (SecurityMiddleware.isLoginLocked(identifier)) {
    const remainingTime = SecurityMiddleware.getLoginLockRemainingTime(identifier);
    const minutes = Math.ceil(remainingTime / (60 * 1000));
    throw new Error(`로그인이 잠겨있습니다. ${minutes}분 후에 다시 시도해주세요.`);
  }
  
  // 로그인 시도
  const canAttempt = SecurityMiddleware.validateLoginAttempt(identifier);
  if (!canAttempt) {
    throw new Error('로그인 시도 횟수를 초과했습니다.');
  }
  
  // 로그인 처리...
};
```

### 2. 세션 보안

```typescript
const checkSessionSecurity = () => {
  // HTTPS 체크
  if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost') {
    return false;
  }
  
  // 비활성 시간 체크
  const lastActivity = getLastActivityTime();
  const inactiveTime = Date.now() - lastActivity;
  
  if (inactiveTime > SECURITY_CONFIG.INACTIVE_TIMEOUT) {
    return false;
  }
  
  return true;
};
```

### 3. 의심스러운 활동 감지

```typescript
const detectSuspiciousActivity = (activity: any) => {
  const suspiciousPatterns = [
    'multiple_failed_logins',
    'unusual_location',
    'unusual_time',
    'rapid_requests'
  ];
  
  if (suspiciousPatterns.some(pattern => activity.includes(pattern))) {
    SecurityUtils.createSecurityLog(
      SecurityUtils.SECURITY_EVENTS.SUSPICIOUS_ACTIVITY,
      activity.userId,
      activity
    );
    
    // 추가 보안 조치
    return true;
  }
  
  return false;
};
```

## 📈 보안 성능 최적화

### 1. Rate Limiting 최적화

```typescript
// 메모리 기반 Rate Limiter
const createOptimizedRateLimiter = (maxRequests: number, windowMs: number) => {
  const requests = new Map<string, number[]>();
  
  return (identifier: string): boolean => {
    const now = Date.now();
    const windowStart = now - windowMs;
    
    if (!requests.has(identifier)) {
      requests.set(identifier, [now]);
      return true;
    }
    
    const userRequests = requests.get(identifier)!;
    const recentRequests = userRequests.filter(time => time > windowStart);
    
    if (recentRequests.length >= maxRequests) {
      return false;
    }
    
    recentRequests.push(now);
    requests.set(identifier, recentRequests);
    return true;
  };
};
```

### 2. 보안 로그 최적화

```typescript
// 배치 로그 처리
class SecurityLogManager {
  private logs: any[] = [];
  private batchSize = 10;
  private flushInterval = 5000; // 5초
  
  addLog(log: any) {
    this.logs.push(log);
    
    if (this.logs.length >= this.batchSize) {
      this.flush();
    }
  }
  
  private flush() {
    if (this.logs.length > 0) {
      // 배치로 로그 전송
      this.sendLogs(this.logs);
      this.logs = [];
    }
  }
  
  private sendLogs(logs: any[]) {
    // 실제 로그 전송 로직
    console.log('Sending logs:', logs);
  }
}
```

## 🔄 업데이트 로그

### v1.0.0 (2024-01-15)
- ✅ 기본 보안 유틸리티 구현
- ✅ JWT 토큰 관리 강화
- ✅ 입력 검증 및 필터링
- ✅ Rate Limiting 시스템
- ✅ 로그인 시도 제한
- ✅ 보안 헤더 설정
- ✅ 보안 로그 시스템
- ✅ 세션 보안 모니터링

### 예정 기능
- 🔄 2FA (Two-Factor Authentication)
- 🔄 보안 감사 로그
- 🔄 자동 보안 스캔
- 🔄 보안 알림 시스템

## 📚 참고 자료

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Web Security Guidelines](https://developer.mozilla.org/en-US/docs/Web/Security)
- [JWT Security Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)

---

**마지막 업데이트**: 2024년 1월 15일 