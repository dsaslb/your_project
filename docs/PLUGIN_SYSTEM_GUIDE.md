# 플러그인 시스템 사용 가이드

## 개요

이 문서는 레스토랑 관리 시스템의 플러그인 시스템에 대한 종합적인 가이드입니다. 플러그인 개발자, 시스템 관리자, 일반 사용자를 위한 정보를 포함합니다.

## 목차

1. [시스템 아키텍처](#시스템-아키텍처)
2. [플러그인 개발 가이드](#플러그인-개발-가이드)
3. [마켓플레이스 사용법](#마켓플레이스-사용법)
4. [보안 및 권한 관리](#보안-및-권한-관리)
5. [배포 및 관리](#배포-및-관리)
6. [문제 해결](#문제-해결)
7. [API 참조](#api-참조)

## 시스템 아키텍처

### 핵심 컴포넌트

```
플러그인 시스템
├── 플러그인 로더 (PluginLoader)
├── 플러그인 레지스트리 (PluginRegistry)
├── 플러그인 매니저 (PluginManager)
├── 마켓플레이스 (PluginMarketplace)
├── 보안 시스템 (PluginSecuritySystem)
├── 배포 시스템 (PluginDeploymentSystem)
├── 테스트 시스템 (PluginTestingSystem)
└── 최적화 시스템 (PluginOptimizer)
```

### 플러그인 생명주기

1. **개발** → 플러그인 코드 작성 및 테스트
2. **등록** → 마켓플레이스에 플러그인 등록
3. **검토** → 관리자 승인/거부
4. **배포** → 시스템에 플러그인 배포
5. **활성화** → 사용자 환경에서 플러그인 활성화
6. **모니터링** → 성능 및 보안 모니터링
7. **업데이트** → 버전 업데이트 및 유지보수

## 플러그인 개발 가이드

### 기본 구조

플러그인은 다음과 같은 구조를 가져야 합니다:

```
my_plugin/
├── plugin.json          # 플러그인 메타데이터
├── main.py             # 메인 플러그인 코드
├── requirements.txt    # 의존성 목록
├── README.md          # 플러그인 설명서
├── tests/             # 테스트 코드
│   ├── test_main.py
│   └── test_integration.py
└── config/            # 설정 파일
    └── default.json
```

### plugin.json 예시

```json
{
  "plugin_id": "my_restaurant_plugin",
  "name": "내 레스토랑 플러그인",
  "version": "1.0.0",
  "description": "레스토랑 관리를 위한 플러그인",
  "author": "개발자 이름",
  "author_email": "developer@example.com",
  "category": "business",
  "tags": ["restaurant", "management", "analytics"],
  "license": "MIT",
  "homepage": "https://github.com/developer/my-plugin",
  "repository": "https://github.com/developer/my-plugin",
  "support_email": "support@example.com",
  "dependencies": [],
  "permissions": ["read", "write", "admin"],
  "entry_point": "main.py",
  "config_schema": {
    "type": "object",
    "properties": {
      "enabled": {
        "type": "boolean",
        "default": true,
        "description": "플러그인 활성화 여부"
      },
      "debug_mode": {
        "type": "boolean",
        "default": false,
        "description": "디버그 모드"
      }
    }
  }
}
```

### 메인 플러그인 코드 예시

```python
#!/usr/bin/env python3
"""
내 레스토랑 플러그인
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class MyRestaurantPlugin:
    """레스토랑 관리 플러그인"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.debug_mode = config.get("debug_mode", False)
        
        if self.debug_mode:
            logger.setLevel(logging.DEBUG)
        
        logger.info("내 레스토랑 플러그인이 초기화되었습니다.")
    
    def start(self):
        """플러그인 시작"""
        if not self.enabled:
            logger.info("플러그인이 비활성화되어 있습니다.")
            return
        
        logger.info("내 레스토랑 플러그인이 시작되었습니다.")
        self._initialize_plugin()
    
    def stop(self):
        """플러그인 중지"""
        logger.info("내 레스토랑 플러그인이 중지되었습니다.")
    
    def _initialize_plugin(self):
        """플러그인 초기화"""
        logger.debug("플러그인 초기화 중...")
        # 여기에 초기화 로직을 구현하세요
    
    def get_metadata(self) -> Dict[str, Any]:
        """플러그인 메타데이터 반환"""
        return {
            'name': '내 레스토랑 플러그인',
            'version': '1.0.0',
            'description': '레스토랑 관리를 위한 플러그인'
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """플러그인 상태 반환"""
        return {
            'status': 'healthy',
            'last_check': datetime.now().isoformat(),
            'enabled': self.enabled
        }
    
    def get_menus(self) -> List[Dict[str, Any]]:
        """플러그인 메뉴 반환"""
        return [
            {
                'title': '내 플러그인',
                'path': '/my-plugin',
                'icon': 'restaurant',
                'roles': ['admin', 'manager']
            }
        ]

def create_plugin(config: Dict[str, Any]):
    """플러그인 인스턴스 생성"""
    return MyRestaurantPlugin(config)
```

### 테스트 작성

```python
#!/usr/bin/env python3
"""
플러그인 테스트
"""

import unittest
from unittest.mock import Mock, patch
from main import MyRestaurantPlugin

class TestMyRestaurantPlugin(unittest.TestCase):
    
    def setUp(self):
        self.config = {
            'enabled': True,
            'debug_mode': False
        }
        self.plugin = MyRestaurantPlugin(self.config)
    
    def test_plugin_initialization(self):
        """플러그인 초기화 테스트"""
        self.assertIsNotNone(self.plugin)
        self.assertTrue(self.plugin.enabled)
        self.assertFalse(self.plugin.debug_mode)
    
    def test_plugin_metadata(self):
        """플러그인 메타데이터 테스트"""
        metadata = self.plugin.get_metadata()
        self.assertEqual(metadata['name'], '내 레스토랑 플러그인')
        self.assertEqual(metadata['version'], '1.0.0')
    
    def test_plugin_health_status(self):
        """플러그인 상태 테스트"""
        status = self.plugin.get_health_status()
        self.assertEqual(status['status'], 'healthy')
        self.assertTrue(status['enabled'])

if __name__ == '__main__':
    unittest.main()
```

## 마켓플레이스 사용법

### 플러그인 등록

1. **플러그인 패키징**
   ```bash
   # 플러그인 디렉토리를 ZIP으로 압축
   zip -r my_plugin.zip my_plugin/
   ```

2. **마켓플레이스에 등록**
   - 관리자 페이지에서 "플러그인 등록" 메뉴 접속
   - 플러그인 파일 업로드
   - 메타데이터 입력 및 제출

3. **관리자 승인**
   - 관리자가 플러그인 검토
   - 보안 검사 및 기능 테스트
   - 승인 또는 거부 결정

### 플러그인 검색 및 다운로드

1. **마켓플레이스 접속**
   - `/plugin-marketplace` 페이지 접속

2. **플러그인 검색**
   - 검색어, 카테고리, 상태별 필터링
   - 평점 및 다운로드 수 확인

3. **플러그인 다운로드**
   - 원하는 플러그인 선택
   - "다운로드" 버튼 클릭
   - 설치 및 활성화

### 플러그인 평점 및 리뷰

- 플러그인 사용 후 1-5점 평점 부여
- 사용 경험 및 개선 사항 리뷰 작성
- 다른 사용자들의 평가 참고

## 보안 및 권한 관리

### 보안 정책

1. **플러그인 검증**
   - 코드 정적 분석
   - 보안 취약점 스캔
   - 의존성 보안 검사

2. **실행 환경 격리**
   - 샌드박스 환경에서 실행
   - 리소스 사용량 제한
   - 네트워크 접근 제어

3. **API 키 관리**
   - 플러그인별 고유 API 키 발급
   - 권한별 접근 제어
   - 키 만료 및 갱신

### 권한 시스템

```python
# 권한 레벨
PERMISSIONS = {
    'read': '읽기 권한',
    'write': '쓰기 권한', 
    'admin': '관리자 권한',
    'system': '시스템 권한'
}

# 역할별 권한
ROLE_PERMISSIONS = {
    'user': ['read'],
    'manager': ['read', 'write'],
    'admin': ['read', 'write', 'admin'],
    'super_admin': ['read', 'write', 'admin', 'system']
}
```

## 배포 및 관리

### 배포 환경

1. **개발 환경 (Development)**
   - 플러그인 개발 및 테스트
   - 디버깅 및 로깅 활성화

2. **스테이징 환경 (Staging)**
   - 통합 테스트
   - 성능 및 보안 검증

3. **프로덕션 환경 (Production)**
   - 실제 서비스 운영
   - 모니터링 및 백업

### 배포 프로세스

```bash
# 1. 플러그인 빌드
python setup.py build

# 2. 테스트 실행
python -m pytest tests/

# 3. 배포
python deploy.py --environment production

# 4. 활성화
python activate_plugin.py my_plugin
```

### 모니터링 및 로깅

```python
# 성능 모니터링
from core.backend.plugin_optimizer import system_optimizer

# 모니터링 시작
system_optimizer.start_auto_optimization()

# 성능 리포트 조회
report = system_optimizer.get_system_status()
```

## 문제 해결

### 일반적인 문제들

1. **플러그인 로딩 실패**
   ```
   문제: 플러그인이 로드되지 않음
   해결: plugin.json 파일 확인, 의존성 설치
   ```

2. **권한 오류**
   ```
   문제: API 접근 권한 없음
   해결: API 키 확인, 권한 설정 확인
   ```

3. **성능 문제**
   ```
   문제: 플러그인 실행이 느림
   해결: 성능 최적화, 리소스 사용량 확인
   ```

### 디버깅 방법

1. **로그 확인**
   ```bash
   tail -f logs/plugin_system.log
   ```

2. **플러그인 상태 확인**
   ```python
   from core.backend.plugin_registry import plugin_registry
   
   plugins = plugin_registry.get_all_plugins()
   for plugin_id, plugin in plugins.items():
       status = plugin.get_health_status()
       print(f"{plugin_id}: {status}")
   ```

3. **성능 분석**
   ```python
   from core.backend.plugin_optimizer import system_optimizer
   
   report = system_optimizer.get_system_status()
   print(report['performance_report'])
   ```

## API 참조

### 플러그인 관리 API

#### 플러그인 등록
```http
POST /api/plugins/register
Content-Type: application/json

{
  "plugin_id": "my_plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "Plugin description"
}
```

#### 플러그인 조회
```http
GET /api/plugins/{plugin_id}
```

#### 플러그인 활성화/비활성화
```http
PUT /api/plugins/{plugin_id}/status
Content-Type: application/json

{
  "enabled": true
}
```

### 마켓플레이스 API

#### 플러그인 검색
```http
GET /api/marketplace/plugins?query=restaurant&category=business
```

#### 플러그인 다운로드
```http
POST /api/marketplace/plugins/{plugin_id}/download
```

#### 플러그인 평점
```http
POST /api/marketplace/plugins/{plugin_id}/rate
Content-Type: application/json

{
  "rating": 4.5
}
```

### 보안 API

#### 보안 정책 생성
```http
POST /api/plugin-security/policies
Content-Type: application/json

{
  "plugin_id": "my_plugin",
  "security_level": "high",
  "allowed_ips": ["127.0.0.1"]
}
```

#### API 키 생성
```http
POST /api/plugin-security/api-keys
Content-Type: application/json

{
  "plugin_id": "my_plugin",
  "name": "My API Key",
  "permissions": ["read", "write"]
}
```

### 배포 API

#### 플러그인 배포
```http
POST /api/marketplace/deployments/{plugin_id}/deploy
Content-Type: application/json

{
  "environment": "production"
}
```

#### 배포 상태 조회
```http
GET /api/marketplace/deployments?plugin_id={plugin_id}
```

## 결론

이 가이드는 플러그인 시스템의 기본적인 사용법과 개발 방법을 다루었습니다. 더 자세한 정보나 특정 기능에 대한 문의사항이 있으시면 개발팀에 문의해 주세요.

### 추가 리소스

- [API 문서](./API_REFERENCE.md)
- [보안 가이드](./SECURITY_GUIDE.md)
- [성능 최적화 가이드](./PERFORMANCE_GUIDE.md)
- [문제 해결 FAQ](./TROUBLESHOOTING_FAQ.md)

---

**버전**: 1.0.0  
**최종 업데이트**: 2024년 1월  
**작성자**: 개발팀 