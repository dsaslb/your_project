# 플러그인 개발 가이드

## 📋 개요

Your Program 플랫폼은 플러그인/모듈형 확장 시스템을 제공합니다. 이 가이드를 통해 업종별, 브랜드별 맞춤 기능을 개발할 수 있습니다.

## 🏗️ 플러그인 구조

```
plugins/
├── your_plugin_name/
│   ├── backend/
│   │   ├── main.py              # 플러그인 메인 파일
│   │   ├── models.py            # 데이터 모델 (선택사항)
│   │   ├── routes.py            # API 라우트 (선택사항)
│   │   └── services.py          # 비즈니스 로직 (선택사항)
│   ├── frontend/
│   │   ├── components/          # React 컴포넌트
│   │   ├── pages/               # 페이지 컴포넌트
│   │   └── hooks/               # 커스텀 훅
│   ├── config/
│   │   └── plugin.json          # 플러그인 설정
│   ├── migrations/              # DB 마이그레이션
│   └── README.md                # 플러그인 문서
```

## 🚀 플러그인 생성

### 1. 기본 구조 생성

```bash
mkdir -p plugins/my_plugin/{backend,frontend,config,migrations}
```

### 2. 플러그인 설정 파일 생성

`plugins/my_plugin/config/plugin.json`:

```json
{
  "name": "내 플러그인",
  "version": "1.0.0",
  "description": "플러그인 설명",
  "author": "개발자 이름",
  "category": "business",
  "dependencies": [],
  "permissions": ["my_plugin_access"],
  "enabled": true,
  "created_at": "2024-12-01T00:00:00Z",
  "updated_at": "2024-12-01T00:00:00Z",
  "config": {
    "feature_enabled": true,
    "max_items": 100
  }
}
```

### 3. 백엔드 메인 파일 생성

`plugins/my_plugin/backend/main.py`:

```python
from core.backend.plugin_interface import (
    BasePlugin, PluginMetadata, PluginRoute, 
    PluginMenu, PluginConfig
)
from datetime import datetime

class MyPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self._initialized = False
        
        # 메타데이터 설정
        self.metadata = PluginMetadata(
            name="내 플러그인",
            version="1.0.0",
            description="플러그인 설명",
            author="개발자 이름",
            category="business",
            dependencies=[],
            permissions=["my_plugin_access"],
            enabled=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # 라우트 설정
        self.routes = [
            PluginRoute(
                path="/my-endpoint",
                methods=["GET", "POST"],
                handler="handle_my_endpoint",
                auth_required=True,
                roles=["admin", "manager"],
                description="내 API 엔드포인트"
            )
        ]
        
        # 메뉴 설정
        self.menus = [
            PluginMenu(
                title="내 메뉴",
                path="/my-plugin/page",
                icon="settings",
                parent="plugins",
                roles=["admin", "manager"],
                order=1
            )
        ]
        
        # 설정 스키마
        self.config_schema = [
            PluginConfig(
                key="feature_enabled",
                type="boolean",
                default=True,
                required=False,
                description="기능 활성화"
            ),
            PluginConfig(
                key="max_items",
                type="number",
                default=100,
                required=False,
                description="최대 아이템 수"
            )
        ]
    
    def initialize(self) -> bool:
        """플러그인 초기화"""
        try:
            print(f"플러그인 초기화: {self.metadata.name}")
            self._initialized = True
            return True
        except Exception as e:
            print(f"초기화 실패: {e}")
            return False
    
    def cleanup(self) -> bool:
        """플러그인 정리"""
        try:
            print(f"플러그인 정리: {self.metadata.name}")
            self._initialized = False
            return True
        except Exception as e:
            print(f"정리 실패: {e}")
            return False
    
    def get_metadata(self) -> PluginMetadata:
        """메타데이터 반환"""
        if self.metadata is None:
            raise ValueError("메타데이터가 설정되지 않았습니다")
        return self.metadata

# 플러그인 생성 함수
def create_plugin() -> BasePlugin:
    return MyPlugin()
```

## 🔧 API 개발

### 라우트 핸들러 구현

`plugins/my_plugin/backend/routes.py`:

```python
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

my_plugin_bp = Blueprint('my_plugin', __name__)

@my_plugin_bp.route('/my-endpoint', methods=['GET'])
@login_required
def handle_my_endpoint():
    """내 API 엔드포인트"""
    try:
        # 비즈니스 로직 구현
        data = {
            'message': '플러그인 API 응답',
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

## 🎨 프론트엔드 개발

### React 컴포넌트 생성

`plugins/my_plugin/frontend/components/MyComponent.tsx`:

```tsx
import React, { useState, useEffect } from 'react';

interface MyComponentProps {
  config?: any;
}

export const MyComponent: React.FC<MyComponentProps> = ({ config }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // API 호출
    fetch('/api/plugins/my_plugin/my-endpoint')
      .then(res => res.json())
      .then(result => {
        setData(result.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('API 호출 실패:', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>로딩 중...</div>;
  }

  return (
    <div className="my-plugin-component">
      <h2>내 플러그인 컴포넌트</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
};
```

### 페이지 컴포넌트 생성

`plugins/my_plugin/frontend/pages/MyPage.tsx`:

```tsx
import React from 'react';
import { MyComponent } from '../components/MyComponent';

export const MyPage: React.FC = () => {
  return (
    <div className="my-plugin-page">
      <h1>내 플러그인 페이지</h1>
      <MyComponent />
    </div>
  );
};
```

## 🗄️ 데이터베이스 마이그레이션

### 마이그레이션 파일 생성

`plugins/my_plugin/migrations/001_create_my_table.sql`:

```sql
-- 내 플러그인 테이블 생성
CREATE TABLE IF NOT EXISTS my_plugin_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_my_plugin_data_name ON my_plugin_data(name);
```

## ⚙️ 설정 관리

### 설정 스키마 정의

플러그인의 설정은 `config_schema`에 정의됩니다:

```python
self.config_schema = [
    PluginConfig(
        key="api_key",
        type="string",
        default="",
        required=True,
        description="외부 API 키"
    ),
    PluginConfig(
        key="max_requests",
        type="number",
        default=1000,
        required=False,
        description="최대 요청 수"
    ),
    PluginConfig(
        key="debug_mode",
        type="boolean",
        default=False,
        required=False,
        description="디버그 모드"
    ),
    PluginConfig(
        key="notification_type",
        type="select",
        default="email",
        required=False,
        description="알림 타입",
        options=["email", "sms", "push"]
    )
]
```

## 🔐 권한 관리

### 권한 정의

플러그인에서 필요한 권한을 정의합니다:

```python
# 메타데이터에 권한 추가
self.metadata = PluginMetadata(
    # ... 기타 설정
    permissions=[
        "my_plugin_view",      # 조회 권한
        "my_plugin_edit",      # 편집 권한
        "my_plugin_admin"      # 관리 권한
    ]
)
```

### 권한 확인

```python
from flask_login import current_user

def check_permission(permission):
    """권한 확인"""
    if not current_user.is_authenticated:
        return False
    
    # 사용자 권한 확인
    user_permissions = current_user.get_permissions()
    return user_permissions.get(permission, False)

@my_plugin_bp.route('/admin', methods=['GET'])
@login_required
def admin_page():
    """관리자 페이지"""
    if not check_permission("my_plugin_admin"):
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    # 관리자 기능 구현
    return jsonify({'message': '관리자 페이지'})
```

## 🧪 테스트

### 단위 테스트

`plugins/my_plugin/tests/test_plugin.py`:

```python
import unittest
from plugins.my_plugin.backend.main import MyPlugin

class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = MyPlugin()
    
    def test_initialization(self):
        """플러그인 초기화 테스트"""
        self.assertTrue(self.plugin.initialize())
        self.assertTrue(self.plugin._initialized)
    
    def test_cleanup(self):
        """플러그인 정리 테스트"""
        self.plugin.initialize()
        self.assertTrue(self.plugin.cleanup())
        self.assertFalse(self.plugin._initialized)
    
    def test_metadata(self):
        """메타데이터 테스트"""
        metadata = self.plugin.get_metadata()
        self.assertEqual(metadata.name, "내 플러그인")
        self.assertEqual(metadata.version, "1.0.0")

if __name__ == '__main__':
    unittest.main()
```

## 📦 배포

### 플러그인 패키징

```bash
# 플러그인 디렉토리 압축
cd plugins
zip -r my_plugin.zip my_plugin/
```

### 플러그인 설치

1. 플러그인 파일을 `plugins/` 디렉토리에 복사
2. 관리자 페이지에서 플러그인 활성화
3. 설정 구성

## 🔄 업데이트

### 버전 관리

플러그인 업데이트 시 버전을 증가시킵니다:

```json
{
  "name": "내 플러그인",
  "version": "1.1.0",
  "description": "업데이트된 플러그인",
  // ... 기타 설정
}
```

### 마이그레이션 실행

새 버전의 마이그레이션 파일을 실행합니다:

```sql
-- 002_update_my_table.sql
ALTER TABLE my_plugin_data ADD COLUMN status VARCHAR(20) DEFAULT 'active';
```

## 🐛 디버깅

### 로그 확인

플러그인 로그는 시스템 로그에 포함됩니다:

```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.info("플러그인 함수 실행")
    try:
        # 비즈니스 로직
        pass
    except Exception as e:
        logger.error(f"오류 발생: {e}")
```

### 상태 확인

플러그인 상태는 관리자 API를 통해 확인할 수 있습니다:

```bash
# 플러그인 상태 조회
curl -X GET http://localhost:5000/api/plugins/my_plugin

# 플러그인 재로드
curl -X POST http://localhost:5000/api/plugins/my_plugin/reload
```

## 📚 예제 플러그인

### 레스토랑 관리 플러그인

`plugins/restaurant_management/` 디렉토리에 완전한 예제 플러그인이 포함되어 있습니다.

### 주요 기능

- 메뉴 관리 API
- 주문 처리 시스템
- 재고 관리
- 설정 관리
- 권한 기반 접근 제어

## 🤝 지원

플러그인 개발 중 문제가 발생하면:

1. 로그 확인
2. API 문서 참조
3. 예제 플러그인 분석
4. 개발팀 문의

## 📝 체크리스트

플러그인 개발 완료 후 확인사항:

- [ ] 플러그인 초기화 성공
- [ ] API 엔드포인트 정상 동작
- [ ] 권한 설정 완료
- [ ] 설정 스키마 정의
- [ ] 메뉴 등록 완료
- [ ] 테스트 통과
- [ ] 문서 작성 완료
- [ ] 배포 준비 완료 