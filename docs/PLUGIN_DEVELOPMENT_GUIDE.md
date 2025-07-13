# Your Program 플러그인 개발 가이드

## 목차
1. [개요](#개요)
2. [개발 환경 설정](#개발-환경-설정)
3. [플러그인 구조](#플러그인-구조)
4. [플러그인 개발](#플러그인-개발)
5. [테스트 및 검증](#테스트-및-검증)
6. [배포 및 배포](#배포-및-배포)
7. [모니터링 및 유지보수](#모니터링-및-유지보수)
8. [모범 사례](#모범-사례)
9. [문제 해결](#문제-해결)

## 개요

Your Program 플러그인 시스템은 확장 가능하고 모듈화된 아키텍처를 제공합니다. 이 가이드를 통해 고품질의 플러그인을 개발하고 배포할 수 있습니다.

### 플러그인 시스템의 특징
- **모듈화**: 독립적인 기능 단위로 개발
- **확장성**: 새로운 기능을 쉽게 추가
- **보안**: 자동 보안 검사 및 승인 시스템
- **성능**: 실시간 모니터링 및 최적화
- **사용자 친화적**: 직관적인 관리 인터페이스

## 개발 환경 설정

### 필수 요구사항
- Python 3.8 이상
- Flask 2.0 이상
- Git
- Your Program SDK

### 개발 환경 설정

1. **SDK 설치**
```bash
# SDK 다운로드
git clone https://github.com/your-program/plugin-sdk.git
cd plugin-sdk

# 의존성 설치
pip install -r requirements.txt
```

2. **개발 도구 설치**
```bash
# 플러그인 CLI 도구 설치
pip install your-program-cli

# 개발 도구 확인
yp-cli --version
```

3. **개발 환경 설정**
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 개발 의존성 설치
pip install -r requirements-dev.txt
```

## 플러그인 구조

### 기본 디렉토리 구조
```
my_plugin/
├── backend/           # 백엔드 코드
│   ├── __init__.py
│   ├── main.py        # 메인 플러그인 로직
│   ├── models.py      # 데이터 모델
│   ├── api.py         # API 엔드포인트
│   └── utils.py       # 유틸리티 함수
├── frontend/          # 프론트엔드 코드
│   ├── index.html
│   ├── style.css
│   └── script.js
├── config/           # 설정 파일
│   ├── plugin.json   # 플러그인 매니페스트
│   └── settings.json # 기본 설정
├── tests/            # 테스트 코드
│   ├── test_main.py
│   ├── test_api.py
│   └── test_integration.py
├── docs/             # 문서
│   ├── README.md
│   ├── API.md
│   └── CHANGELOG.md
├── assets/           # 리소스 파일
│   ├── images/
│   └── icons/
├── scripts/          # 스크립트
│   ├── install.sh
│   └── uninstall.sh
├── plugin.json       # 플러그인 매니페스트
├── README.md         # 설명서
├── requirements.txt  # Python 의존성
├── .gitignore        # Git 제외 파일
└── LICENSE           # 라이선스
```

### 플러그인 매니페스트 (plugin.json)
```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "description": "플러그인 설명",
  "author": "개발자 이름",
  "author_email": "developer@example.com",
  "license": "MIT",
  "category": "utility",
  "tags": ["plugin", "example"],
  "compatibility": {
    "min_version": "1.0.0",
    "max_version": "2.0.0",
    "python_version": ">=3.8"
  },
  "dependencies": [
    "flask>=2.0.0",
    "requests>=2.25.0"
  ],
  "permissions": [
    "read_files",
    "write_files"
  ],
  "api_endpoints": [
    "/api/my_plugin/health",
    "/api/my_plugin/data"
  ],
  "ui_components": [
    "my_plugin_dashboard",
    "my_plugin_settings"
  ],
  "settings": {
    "api_key": {
      "type": "string",
      "default": "",
      "description": "API 키"
    },
    "timeout": {
      "type": "integer",
      "default": 30,
      "description": "타임아웃 (초)"
    }
  },
  "hooks": [
    "on_install",
    "on_uninstall",
    "on_activate",
    "on_deactivate"
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## 플러그인 개발

### 1. 플러그인 템플릿 생성

```bash
# CLI를 사용한 템플릿 생성
yp-cli create my_plugin --type api

# 또는 SDK를 직접 사용
python -c "
from plugin_template import PluginTemplate
template = PluginTemplate('my_plugin', 'api')
template.create_template()
"
```

### 2. 기본 플러그인 구조

#### 백엔드 메인 파일 (backend/main.py)
```python
from flask import Blueprint, request, jsonify
from functools import wraps
import logging

# 플러그인 블루프린트 생성
plugin_bp = Blueprint('my_plugin', __name__)

# 로깅 설정
logger = logging.getLogger(__name__)

def require_auth(f):
    """인증 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 인증 로직 구현
        return f(*args, **kwargs)
    return decorated_function

@plugin_bp.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        'status': 'healthy',
        'plugin': 'my_plugin',
        'version': '1.0.0'
    })

@plugin_bp.route('/api/data', methods=['GET'])
@require_auth
def get_data():
    """데이터 조회 엔드포인트"""
    try:
        # 플러그인 로직 구현
        data = {
            'message': 'Hello from my_plugin!',
            'data': []
        }
        return jsonify(data)
    except Exception as e:
        logger.error(f"데이터 조회 실패: {e}")
        return jsonify({'error': str(e)}), 500

# 플러그인 초기화 함수
def init_plugin(app):
    """플러그인 초기화"""
    app.register_blueprint(plugin_bp, url_prefix='/my_plugin')
    logger.info('my_plugin 플러그인이 초기화되었습니다.')
```

#### 데이터 모델 (backend/models.py)
```python
from datetime import datetime
from typing import Optional

class PluginData:
    """플러그인 데이터 모델"""
    
    def __init__(self, id: str, name: str, value: str):
        self.id = id
        self.name = name
        self.value = value
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """딕셔너리에서 생성"""
        instance = cls(
            id=data['id'],
            name=data['name'],
            value=data['value']
        )
        instance.created_at = datetime.fromisoformat(data['created_at'])
        instance.updated_at = datetime.fromisoformat(data['updated_at'])
        return instance
```

#### API 엔드포인트 (backend/api.py)
```python
from flask import Blueprint, request, jsonify
from .models import PluginData
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('my_plugin_api', __name__)

@api_bp.route('/api/data', methods=['GET'])
def get_all_data():
    """모든 데이터 조회"""
    try:
        # 데이터베이스에서 데이터 조회
        data_list = []  # 실제로는 데이터베이스에서 조회
        return jsonify({'data': data_list})
    except Exception as e:
        logger.error(f"데이터 조회 실패: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/data', methods=['POST'])
def create_data():
    """새 데이터 생성"""
    try:
        data = request.get_json()
        
        # 데이터 검증
        if not data or 'name' not in data or 'value' not in data:
            return jsonify({'error': '필수 필드가 누락되었습니다'}), 400
        
        # 새 데이터 생성
        new_data = PluginData(
            id=f"data_{datetime.now().timestamp()}",
            name=data['name'],
            value=data['value']
        )
        
        # 데이터베이스에 저장
        # save_to_database(new_data)
        
        return jsonify(new_data.to_dict()), 201
    except Exception as e:
        logger.error(f"데이터 생성 실패: {e}")
        return jsonify({'error': str(e)}), 500
```

### 3. 프론트엔드 개발

#### HTML 템플릿 (frontend/index.html)
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Plugin Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="style.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <div class="bg-white rounded-lg shadow-md p-6">
            <h1 class="text-2xl font-bold mb-4">My Plugin Dashboard</h1>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h2 class="text-lg font-semibold mb-3">데이터 목록</h2>
                    <div id="dataList" class="space-y-2">
                        <!-- 데이터 목록이 여기에 동적으로 추가됩니다 -->
                    </div>
                </div>
                
                <div>
                    <h2 class="text-lg font-semibold mb-3">새 데이터 추가</h2>
                    <form id="addDataForm" class="space-y-3">
                        <div>
                            <label class="block text-sm font-medium text-gray-700">이름</label>
                            <input type="text" id="dataName" name="name" 
                                   class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700">값</label>
                            <input type="text" id="dataValue" name="value" 
                                   class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2">
                        </div>
                        <button type="submit" 
                                class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md">
                            추가
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <script src="script.js"></script>
</body>
</html>
```

#### CSS 스타일 (frontend/style.css)
```css
/* 플러그인 전용 스타일 */
.plugin-card {
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 1rem;
    background-color: white;
    transition: box-shadow 0.2s;
}

.plugin-card:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.plugin-button {
    background-color: #3b82f6;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
    border: none;
    cursor: pointer;
    transition: background-color 0.2s;
}

.plugin-button:hover {
    background-color: #2563eb;
}

.plugin-button:disabled {
    background-color: #9ca3af;
    cursor: not-allowed;
}
```

#### JavaScript 로직 (frontend/script.js)
```javascript
// 플러그인 JavaScript 로직
class MyPlugin {
    constructor() {
        this.apiBase = '/my_plugin/api';
        this.init();
    }
    
    init() {
        this.loadData();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const form = document.getElementById('addDataForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleAddData(e));
        }
    }
    
    async loadData() {
        try {
            const response = await fetch(`${this.apiBase}/data`);
            const data = await response.json();
            
            this.renderDataList(data.data || []);
        } catch (error) {
            console.error('데이터 로드 실패:', error);
            this.showNotification('데이터를 불러올 수 없습니다.', 'error');
        }
    }
    
    renderDataList(dataList) {
        const container = document.getElementById('dataList');
        if (!container) return;
        
        container.innerHTML = dataList.map(item => `
            <div class="plugin-card">
                <div class="flex justify-between items-center">
                    <div>
                        <h3 class="font-medium">${item.name}</h3>
                        <p class="text-gray-600">${item.value}</p>
                    </div>
                    <button onclick="myPlugin.deleteData('${item.id}')" 
                            class="plugin-button bg-red-600 hover:bg-red-700">
                        삭제
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    async handleAddData(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const data = {
            name: formData.get('name'),
            value: formData.get('value')
        };
        
        try {
            const response = await fetch(`${this.apiBase}/data`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                this.showNotification('데이터가 추가되었습니다.', 'success');
                event.target.reset();
                this.loadData();
            } else {
                const error = await response.json();
                this.showNotification(error.error || '데이터 추가에 실패했습니다.', 'error');
            }
        } catch (error) {
            console.error('데이터 추가 실패:', error);
            this.showNotification('데이터 추가에 실패했습니다.', 'error');
        }
    }
    
    async deleteData(id) {
        if (!confirm('정말 삭제하시겠습니까?')) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBase}/data/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.showNotification('데이터가 삭제되었습니다.', 'success');
                this.loadData();
            } else {
                this.showNotification('삭제에 실패했습니다.', 'error');
            }
        } catch (error) {
            console.error('데이터 삭제 실패:', error);
            this.showNotification('삭제에 실패했습니다.', 'error');
        }
    }
    
    showNotification(message, type = 'info') {
        // 간단한 알림 구현
        alert(message);
    }
}

// 플러그인 인스턴스 생성
const myPlugin = new MyPlugin();
```

## 테스트 및 검증

### 1. 단위 테스트

#### 테스트 파일 (tests/test_main.py)
```python
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 플러그인 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import health_check, get_data

class TestMyPlugin(unittest.TestCase):
    """My Plugin 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        pass
    
    def test_health_check(self):
        """헬스 체크 테스트"""
        with patch('main.jsonify') as mock_jsonify:
            health_check()
            mock_jsonify.assert_called_with({
                'status': 'healthy',
                'plugin': 'my_plugin',
                'version': '1.0.0'
            })
    
    def test_get_data_success(self):
        """데이터 조회 성공 테스트"""
        with patch('main.jsonify') as mock_jsonify:
            get_data()
            mock_jsonify.assert_called_with({
                'message': 'Hello from my_plugin!',
                'data': []
            })
    
    def test_get_data_error(self):
        """데이터 조회 오류 테스트"""
        with patch('main.get_data', side_effect=Exception('Test error')):
            with patch('main.jsonify') as mock_jsonify:
                get_data()
                mock_jsonify.assert_called_with({'error': 'Test error'})

if __name__ == '__main__':
    unittest.main()
```

### 2. 통합 테스트

#### 통합 테스트 파일 (tests/test_integration.py)
```python
import unittest
import requests
import json
from flask import Flask
from backend.main import init_plugin

class TestMyPluginIntegration(unittest.TestCase):
    """My Plugin 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.app = Flask(__name__)
        init_plugin(self.app)
        self.client = self.app.test_client()
    
    def test_health_endpoint(self):
        """헬스 체크 엔드포인트 테스트"""
        response = self.client.get('/my_plugin/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['plugin'], 'my_plugin')
    
    def test_data_endpoint(self):
        """데이터 엔드포인트 테스트"""
        response = self.client.get('/my_plugin/api/data')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('data', data)

if __name__ == '__main__':
    unittest.main()
```

### 3. 보안 테스트

#### 보안 테스트 파일 (tests/test_security.py)
```python
import unittest
import requests
from backend.main import plugin_bp

class TestMyPluginSecurity(unittest.TestCase):
    """My Plugin 보안 테스트"""
    
    def test_sql_injection_prevention(self):
        """SQL 인젝션 방지 테스트"""
        # SQL 인젝션 시도
        malicious_input = "'; DROP TABLE users; --"
        
        # 실제 구현에서는 이 입력이 안전하게 처리되는지 확인
        # 여기서는 예시로만 작성
        self.assertTrue(self.is_safe_input(malicious_input))
    
    def test_xss_prevention(self):
        """XSS 방지 테스트"""
        # XSS 시도
        malicious_input = "<script>alert('xss')</script>"
        
        # 실제 구현에서는 이 입력이 안전하게 처리되는지 확인
        self.assertTrue(self.is_safe_input(malicious_input))
    
    def is_safe_input(self, input_str):
        """입력값 안전성 검사"""
        # 실제 구현에서는 적절한 검증 로직 구현
        dangerous_patterns = [
            '<script>',
            'javascript:',
            'onload=',
            'onerror='
        ]
        
        for pattern in dangerous_patterns:
            if pattern in input_str.lower():
                return False
        
        return True

if __name__ == '__main__':
    unittest.main()
```

### 4. 성능 테스트

#### 성능 테스트 파일 (tests/test_performance.py)
```python
import unittest
import time
import threading
from backend.main import get_data

class TestMyPluginPerformance(unittest.TestCase):
    """My Plugin 성능 테스트"""
    
    def test_response_time(self):
        """응답 시간 테스트"""
        start_time = time.time()
        get_data()
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertLess(response_time, 0.1)  # 100ms 이내
    
    def test_concurrent_requests(self):
        """동시 요청 테스트"""
        def make_request():
            get_data()
        
        threads = []
        start_time = time.time()
        
        # 10개의 동시 요청
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 모든 스레드 완료 대기
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 10개 요청이 1초 이내에 완료되어야 함
        self.assertLess(total_time, 1.0)

if __name__ == '__main__':
    unittest.main()
```

## 배포 및 배포

### 1. 플러그인 패키징

```bash
# CLI를 사용한 패키징
yp-cli package plugins/my_plugin

# 또는 SDK를 직접 사용
python -c "
from plugin_template import PluginPackager
packager = PluginPackager('plugins/my_plugin')
packager.package()
"
```

### 2. 플러그인 검증

```bash
# CLI를 사용한 검증
yp-cli validate plugins/my_plugin

# 또는 SDK를 직접 사용
python -c "
from plugin_template import PluginValidator
validator = PluginValidator('plugins/my_plugin')
validator.validate()
"
```

### 3. 플러그인 업로드

#### ZIP 파일 업로드
```bash
# ZIP 파일 생성 후 업로드
zip -r my_plugin_v1.0.0.zip plugins/my_plugin/
```

#### GitHub에서 업로드
```bash
# GitHub 저장소 URL로 업로드
curl -X POST http://localhost:5000/api/plugins/register/github \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/username/my_plugin"}'
```

#### URL에서 업로드
```bash
# 직접 다운로드 URL로 업로드
curl -X POST http://localhost:5000/api/plugins/register/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/my_plugin.zip"}'
```

### 4. 자동화된 배포 (CI/CD)

#### GitHub Actions 워크플로우 (.github/workflows/deploy.yml)
```yaml
name: Deploy Plugin

on:
  push:
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          python -m pytest tests/ -v
      
      - name: Run security tests
        run: |
          python -m pytest tests/test_security.py -v
      
      - name: Run performance tests
        run: |
          python -m pytest tests/test_performance.py -v

  package:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Package plugin
        run: |
          python -m plugin_template.PluginPackager .
      
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: plugin-package
          path: *.zip

  deploy:
    needs: package
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Download artifact
        uses: actions/download-artifact@v2
        with:
          name: plugin-package
      
      - name: Deploy to marketplace
        run: |
          curl -X POST ${{ secrets.MARKETPLACE_URL }}/api/plugins/register/upload \
            -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" \
            -F "file=@*.zip"
```

## 모니터링 및 유지보수

### 1. 로깅

```python
import logging

# 플러그인 전용 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 파일 핸들러 추가
file_handler = logging.FileHandler('my_plugin.log')
file_handler.setLevel(logging.INFO)

# 포맷터 설정
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# 로깅 사용 예시
logger.info('플러그인이 시작되었습니다.')
logger.error('오류가 발생했습니다: %s', error_message)
```

### 2. 성능 모니터링

```python
import time
import functools

def monitor_performance(func):
    """성능 모니터링 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 성능 메트릭 기록
            logger.info(f'{func.__name__} 실행 시간: {execution_time:.3f}초')
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f'{func.__name__} 실행 실패 (시간: {execution_time:.3f}초): {e}')
            raise
    
    return wrapper

# 사용 예시
@monitor_performance
def process_data(data):
    # 데이터 처리 로직
    pass
```

### 3. 상태 모니터링

```python
class PluginHealthMonitor:
    """플러그인 상태 모니터링"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
    
    def record_request(self):
        """요청 기록"""
        self.request_count += 1
    
    def record_error(self):
        """오류 기록"""
        self.error_count += 1
    
    def get_health_status(self):
        """상태 정보 반환"""
        uptime = time.time() - self.start_time
        error_rate = self.error_count / max(self.request_count, 1)
        
        return {
            'status': 'healthy' if error_rate < 0.1 else 'degraded',
            'uptime': uptime,
            'request_count': self.request_count,
            'error_count': self.error_count,
            'error_rate': error_rate
        }

# 전역 모니터 인스턴스
health_monitor = PluginHealthMonitor()
```

## 모범 사례

### 1. 코드 품질

#### 코드 스타일
- PEP 8 준수
- 타입 힌트 사용
- 문서화 주석 작성
- 일관된 네이밍 컨벤션

```python
from typing import List, Dict, Optional
from datetime import datetime

def process_user_data(user_id: str, data: Dict[str, any]) -> Optional[Dict[str, any]]:
    """
    사용자 데이터를 처리합니다.
    
    Args:
        user_id: 사용자 ID
        data: 처리할 데이터
        
    Returns:
        처리된 데이터 또는 None
    """
    try:
        # 데이터 검증
        if not user_id or not data:
            return None
        
        # 데이터 처리 로직
        processed_data = {
            'user_id': user_id,
            'processed_at': datetime.now().isoformat(),
            'data': data
        }
        
        return processed_data
    except Exception as e:
        logger.error(f"데이터 처리 실패: {e}")
        return None
```

#### 에러 처리
```python
class PluginError(Exception):
    """플러그인 전용 예외 클래스"""
    pass

class ValidationError(PluginError):
    """검증 오류"""
    pass

class ProcessingError(PluginError):
    """처리 오류"""
    pass

def safe_process_data(data):
    """안전한 데이터 처리"""
    try:
        # 데이터 검증
        if not validate_data(data):
            raise ValidationError("데이터 검증 실패")
        
        # 데이터 처리
        result = process_data(data)
        if not result:
            raise ProcessingError("데이터 처리 실패")
        
        return result
    except ValidationError as e:
        logger.warning(f"검증 오류: {e}")
        return None
    except ProcessingError as e:
        logger.error(f"처리 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        return None
```

### 2. 보안

#### 입력값 검증
```python
import re
from typing import Any

def validate_input(input_data: Any) -> bool:
    """입력값 검증"""
    if not input_data:
        return False
    
    # 문자열 길이 제한
    if isinstance(input_data, str) and len(input_data) > 1000:
        return False
    
    # 위험한 패턴 검사
    dangerous_patterns = [
        r'<script.*?>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe.*?>',
        r'<object.*?>'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, str(input_data), re.IGNORECASE):
            return False
    
    return True

def sanitize_input(input_data: str) -> str:
    """입력값 정제"""
    import html
    
    # HTML 엔티티 이스케이프
    sanitized = html.escape(input_data)
    
    # 추가 정제 로직
    sanitized = re.sub(r'<[^>]*>', '', sanitized)
    
    return sanitized
```

#### 인증 및 권한
```python
from functools import wraps
from flask import request, jsonify, g

def require_auth(f):
    """인증 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': '인증 토큰이 필요합니다'}), 401
        
        # 토큰 검증 로직
        user = verify_token(token)
        if not user:
            return jsonify({'error': '유효하지 않은 토큰입니다'}), 401
        
        g.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function

def require_permission(permission):
    """권한 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = g.current_user
            
            if not has_permission(user, permission):
                return jsonify({'error': '권한이 없습니다'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 사용 예시
@require_auth
@require_permission('read_data')
def get_sensitive_data():
    return jsonify({'data': 'sensitive information'})
```

### 3. 성능 최적화

#### 캐싱
```python
import functools
from typing import Any, Callable
import time

class Cache:
    """간단한 캐시 구현"""
    
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Any:
        """캐시에서 값 조회"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """캐시에 값 저장"""
        self.cache[key] = (value, time.time())
    
    def clear(self):
        """캐시 초기화"""
        self.cache.clear()

# 전역 캐시 인스턴스
cache = Cache()

def cached(ttl: int = 300):
    """캐시 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 캐시에서 조회
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 결과 캐시
            cache.set(cache_key, result)
            
            return result
        return wrapper
    return decorator

# 사용 예시
@cached(ttl=600)  # 10분 캐시
def expensive_operation(data):
    # 비용이 많이 드는 연산
    time.sleep(1)
    return f"processed_{data}"
```

#### 비동기 처리
```python
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

async def async_fetch_data(url: str) -> dict:
    """비동기 데이터 조회"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def process_multiple_data(urls: List[str]) -> List[dict]:
    """여러 데이터 비동기 처리"""
    tasks = [async_fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 오류 필터링
    return [result for result in results if not isinstance(result, Exception)]

def run_async_in_thread(coro):
    """스레드에서 비동기 함수 실행"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Flask에서 비동기 함수 사용
def sync_endpoint():
    """동기 엔드포인트에서 비동기 함수 호출"""
    with ThreadPoolExecutor() as executor:
        future = executor.submit(run_async_in_thread, async_fetch_data('https://api.example.com/data'))
        result = future.result()
    
    return jsonify(result)
```

## 문제 해결

### 1. 일반적인 문제

#### 플러그인 로드 실패
```python
# 문제: 플러그인이 로드되지 않음
# 해결: 매니페스트 파일 확인
def check_manifest(plugin_path: str) -> bool:
    """매니페스트 파일 검증"""
    manifest_path = os.path.join(plugin_path, 'config', 'plugin.json')
    
    if not os.path.exists(manifest_path):
        print(f"매니페스트 파일이 없습니다: {manifest_path}")
        return False
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        required_fields = ['name', 'version', 'description', 'author']
        for field in required_fields:
            if field not in manifest:
                print(f"필수 필드가 누락되었습니다: {field}")
                return False
        
        return True
    except json.JSONDecodeError as e:
        print(f"매니페스트 JSON 형식 오류: {e}")
        return False
    except Exception as e:
        print(f"매니페스트 검증 실패: {e}")
        return False
```

#### 의존성 충돌
```python
# 문제: 의존성 충돌
# 해결: 가상환경 사용 및 버전 고정
def check_dependencies(requirements_file: str) -> List[str]:
    """의존성 충돌 검사"""
    conflicts = []
    
    try:
        with open(requirements_file, 'r') as f:
            requirements = f.readlines()
        
        # 버전 충돌 검사
        package_versions = {}
        for req in requirements:
            req = req.strip()
            if req and not req.startswith('#'):
                if '==' in req:
                    package, version = req.split('==')
                    if package in package_versions:
                        if package_versions[package] != version:
                            conflicts.append(f"{package}: {package_versions[package]} vs {version}")
                    else:
                        package_versions[package] = version
        
        return conflicts
    except Exception as e:
        print(f"의존성 검사 실패: {e}")
        return []
```

#### 성능 문제
```python
# 문제: 성능 저하
# 해결: 프로파일링 및 최적화
import cProfile
import pstats
import io

def profile_function(func, *args, **kwargs):
    """함수 프로파일링"""
    pr = cProfile.Profile()
    pr.enable()
    
    result = func(*args, **kwargs)
    
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    
    print(s.getvalue())
    return result

# 사용 예시
def slow_function():
    import time
    time.sleep(1)
    return "done"

# 프로파일링 실행
result = profile_function(slow_function)
```

### 2. 디버깅

#### 로그 분석
```python
import logging
import traceback

def setup_debug_logging():
    """디버그 로깅 설정"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('debug.log'),
            logging.StreamHandler()
        ]
    )

def debug_function(func):
    """디버그 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"함수 호출: {func.__name__}")
        logger.debug(f"인수: args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"함수 결과: {result}")
            return result
        except Exception as e:
            logger.error(f"함수 오류: {e}")
            logger.error(f"스택 트레이스: {traceback.format_exc()}")
            raise
    
    return wrapper
```

#### 메모리 사용량 모니터링
```python
import psutil
import os

def monitor_memory_usage():
    """메모리 사용량 모니터링"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    logger.info(f"메모리 사용량: {memory_info.rss / 1024 / 1024:.2f} MB")
    
    if memory_info.rss > 100 * 1024 * 1024:  # 100MB
        logger.warning("메모리 사용량이 높습니다!")

def memory_efficient_processing(data_list):
    """메모리 효율적인 처리"""
    for item in data_list:
        # 한 번에 하나씩 처리하여 메모리 사용량 최소화
        yield process_item(item)
```

### 3. 지원 및 커뮤니티

#### 이슈 리포트 템플릿
```markdown
## 버그 리포트

### 버그 설명
[버그에 대한 자세한 설명]

### 재현 단계
1. [첫 번째 단계]
2. [두 번째 단계]
3. [세 번째 단계]

### 예상 동작
[예상되는 정상 동작]

### 실제 동작
[실제로 발생하는 동작]

### 환경 정보
- 플러그인 버전: [버전]
- Your Program 버전: [버전]
- 운영체제: [OS]
- Python 버전: [버전]

### 추가 정보
[스크린샷, 로그, 코드 등]
```

#### 기능 요청 템플릿
```markdown
## 기능 요청

### 기능 설명
[요청하는 기능에 대한 자세한 설명]

### 사용 사례
[이 기능이 어떻게 사용될 것인지]

### 대안
[현재 사용 가능한 대안이 있다면]

### 추가 정보
[구현 아이디어, 참고 자료 등]
```

---

이 가이드를 통해 Your Program 플러그인 개발의 모든 측면을 다룰 수 있습니다. 추가 질문이나 도움이 필요하시면 언제든지 문의해주세요! 
