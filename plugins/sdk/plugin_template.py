"""
Your Program 플러그인 개발 SDK
플러그인 개발을 위한 공식 템플릿 및 가이드
"""

import os
import json
import zipfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import requests
import yaml
import subprocess


class PluginTemplate:
    """플러그인 템플릿 생성기"""

    def __init__(self, plugin_name: str, plugin_type: str = "basic"):
        self.plugin_name = plugin_name
        self.plugin_type = plugin_type
        self.template_dir = Path(__file__).parent / "templates"
        self.output_dir = Path(f"plugins/{plugin_name}")

    def create_template(self) -> bool:
        """플러그인 템플릿 생성"""
        try:
            # 기본 디렉토리 구조 생성
            self._create_directory_structure()

            # 플러그인 매니페스트 생성
            self._create_manifest()

            # 기본 파일들 생성
            self._create_basic_files()

            # 타입별 추가 파일 생성
            if self.plugin_type == "api":
                self._create_api_template()
            elif self.plugin_type == "ui":
                self._create_ui_template()
            elif self.plugin_type == "ai":
                self._create_ai_template()

            # 개발 가이드 생성
            self._create_development_guide()

            print(f"✅ 플러그인 템플릿 '{self.plugin_name}' 생성 완료!")
            print(f"📁 위치: {self.output_dir}")
            return True

        except Exception as e:
            print(f"❌ 템플릿 생성 실패: {e}")
            return False

    def _create_directory_structure(self):
        """기본 디렉토리 구조 생성"""
        directories = [
            "backend",
            "frontend",
            "config",
            "tests",
            "docs",
            "assets",
            "scripts",
        ]

        for dir_name in directories:
            (self.output_dir / dir_name).mkdir(parents=True, exist_ok=True)

    def _create_manifest(self):
        """플러그인 매니페스트 생성"""
        manifest = {
            "name": self.plugin_name,
            "version": "1.0.0",
            "description": f"{self.plugin_name} 플러그인",
            "author": "Your Name",
            "author_email": "your.email@example.com",
            "license": "MIT",
            "category": "utility",
            "tags": ["plugin", "template"],
            "compatibility": {
                "min_version": "1.0.0",
                "max_version": "2.0.0",
                "python_version": ">=3.8",
            },
            "dependencies": [],
            "permissions": [],
            "api_endpoints": [],
            "ui_components": [],
            "settings": {},
            "hooks": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        with open(
            self.output_dir / "config" / "plugin.json", "w", encoding="utf-8"
        ) as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

    def _create_basic_files(self):
        """기본 파일들 생성"""
        # README.md
        readme_content = f"""# {self.plugin_name}

## 설명
{self.plugin_name} 플러그인입니다.

## 설치
1. 플러그인 파일을 다운로드
2. 관리자 대시보드에서 플러그인 업로드
3. 플러그인 활성화

## 사용법
플러그인 사용법을 여기에 작성하세요.

## 설정
플러그인 설정 방법을 여기에 작성하세요.

## 개발
개발 관련 정보를 여기에 작성하세요.

## 라이선스
MIT License
"""

        with open(self.output_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)

        # requirements.txt
        requirements = ["flask>=2.0.0", "requests>=2.25.0", "python-dotenv>=0.19.0"]

        with open(self.output_dir / "requirements.txt", "w") as f:
            f.write("\n".join(requirements))

        # .gitignore
        gitignore = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Config
.env
config/local.json
"""

        with open(self.output_dir / ".gitignore", "w") as f:
            f.write(gitignore)

    def _create_api_template(self):
        """API 플러그인 템플릿 생성"""
        # main.py
        main_content = '''from flask import Blueprint, request, jsonify
from functools import wraps
import logging

# 플러그인 블루프린트 생성
plugin_bp = Blueprint(f'{self.plugin_name}', __name__)

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
        'plugin': f'{self.plugin_name}',
        'version': '1.0.0'
    })

@plugin_bp.route('/api/example', methods=['GET'])
@require_auth
def example_endpoint():
    """예제 API 엔드포인트"""
    return jsonify({
        'message': f'Hello from {self.plugin_name}!',
        'data': []
    })

# 플러그인 초기화 함수
def init_plugin(app):
    """플러그인 초기화"""
    app.register_blueprint(plugin_bp, url_prefix=f'/{self.plugin_name}')
    logger.info(f'{self.plugin_name} 플러그인이 초기화되었습니다.')
'''

        with open(self.output_dir / "backend" / "main.py", "w", encoding="utf-8") as f:
            f.write(main_content)

    def _create_ui_template(self):
        """UI 플러그인 템플릿 생성"""
        # frontend/index.html
        ui_content = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ self.plugin_name }} 플러그인</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <div class="bg-white rounded-lg shadow-md p-6">
            <h1 class="text-2xl font-bold mb-4">{{ self.plugin_name }} 플러그인</h1>
            <p class="text-gray-600 mb-4">플러그인 UI 컴포넌트입니다.</p>
            <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                예제 버튼
            </button>
        </div>
    </div>
    
    <script>
        // 플러그인 JavaScript 코드
        console.log('{{ self.plugin_name }} 플러그인이 로드되었습니다.');
    </script>
</body>
</html>"""

        with open(
            self.output_dir / "frontend" / "index.html", "w", encoding="utf-8"
        ) as f:
            f.write(ui_content)

    def _create_ai_template(self):
        """AI 플러그인 템플릿 생성"""
        # ai_model.py
        ai_content = '''import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class AIModel:
    """AI 모델 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.is_trained = False
        
    def load_model(self, model_path: str) -> bool:
        """모델 로드"""
        try:
            # 모델 로드 로직 구현
            logger.info(f"모델 로드 완료: {model_path}")
            return True
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            return False
    
    def predict(self, input_data: Any) -> Dict[str, Any]:
        """예측 수행"""
        try:
            # 예측 로직 구현
            result = {
                'prediction': 'sample_result',
                'confidence': 0.95,
                'model_info': {
                    'name': f'{self.plugin_name}',
                    'version': '1.0.0'
                }
            }
            return result
        except Exception as e:
            logger.error(f"예측 실패: {e}")
            return {'error': str(e)}
    
    def train(self, training_data: List[Any]) -> bool:
        """모델 학습"""
        try:
            # 학습 로직 구현
            self.is_trained = True
            logger.info("모델 학습 완료")
            return True
        except Exception as e:
            logger.error(f"모델 학습 실패: {e}")
            return False

# 플러그인 초기화
def init_ai_plugin(config: Dict[str, Any]):
    """AI 플러그인 초기화"""
    model = AIModel(config)
    return model'''

        with open(
            self.output_dir / "backend" / "ai_model.py", "w", encoding="utf-8"
        ) as f:
            f.write(ai_content)

    def _create_development_guide(self):
        """개발 가이드 생성"""
        guide_content = f"""# {self.plugin_name} 개발 가이드

## 개발 환경 설정

### 1. 필수 요구사항
- Python 3.8 이상
- Flask 2.0 이상
- Git

### 2. 개발 환경 설정
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\\Scripts\\activate
# macOS/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

## 플러그인 구조

```
{self.plugin_name}/
├── backend/           # 백엔드 코드
├── frontend/          # 프론트엔드 코드
├── config/           # 설정 파일
├── tests/            # 테스트 코드
├── docs/             # 문서
├── assets/           # 리소스 파일
├── scripts/          # 스크립트
├── plugin.json       # 플러그인 매니페스트
├── README.md         # 설명서
└── requirements.txt  # 의존성
```

## 개발 가이드라인

### 1. 코드 스타일
- PEP 8 준수
- 타입 힌트 사용
- 문서화 주석 작성

### 2. 보안
- 입력값 검증
- SQL 인젝션 방지
- XSS 방지
- CSRF 토큰 사용

### 3. 테스트
- 단위 테스트 작성
- 통합 테스트 작성
- 보안 테스트 수행

### 4. 문서화
- API 문서 작성
- 사용자 가이드 작성
- 개발자 문서 작성

## 배포 가이드

### 1. 플러그인 패키징
```bash
python scripts/package.py
```

### 2. 플러그인 업로드
1. 관리자 대시보드 접속
2. 플러그인 마켓플레이스 이동
3. 플러그인 업로드
4. 승인 대기

### 3. 버전 관리
- 시맨틱 버저닝 사용
- CHANGELOG.md 작성
- Git 태그 사용

## 문제 해결

### 자주 발생하는 문제
1. 플러그인 로드 실패
2. API 엔드포인트 오류
3. 권한 문제
4. 의존성 충돌

### 디버깅 방법
1. 로그 확인
2. 플러그인 상태 확인
3. 시스템 요구사항 확인
4. 의존성 확인

## 지원

- 이슈 리포트: GitHub Issues
- 문서: docs/ 폴더
- 예제: examples/ 폴더
"""

        with open(
            self.output_dir / "docs" / "DEVELOPMENT.md", "w", encoding="utf-8"
        ) as f:
            f.write(guide_content)


class PluginPackager:
    """플러그인 패키징 도구"""

    def __init__(self, plugin_path: str):
        self.plugin_path = Path(plugin_path)
        self.manifest_path = self.plugin_path / "config" / "plugin.json"

    def package(self, output_path: Optional[str] = None) -> str:
        """플러그인 패키징"""
        try:
            # 매니페스트 로드
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            # 출력 파일명 생성
            if not output_path:
                version = manifest.get("version", "1.0.0")
                output_path = f"{manifest['name']}_v{version}.zip"

            # ZIP 파일 생성
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in self.plugin_path.rglob("*"):
                    if file_path.is_file() and not self._should_exclude(file_path):
                        arcname = file_path.relative_to(self.plugin_path)
                        zipf.write(file_path, arcname)

            print(f"✅ 플러그인 패키징 완료: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ 패키징 실패: {e}")
            return ""  # 빈 문자열 반환

    def _should_exclude(self, file_path: Path) -> bool:
        """제외할 파일 확인"""
        exclude_patterns = [
            "__pycache__",
            ".git",
            ".vscode",
            ".idea",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".DS_Store",
            "Thumbs.db",
            "*.log",
            "venv",
            "env",
            "node_modules",
        ]

        file_str = str(file_path)
        return any(pattern in file_str for pattern in exclude_patterns)


class PluginValidator:
    """플러그인 검증 도구"""

    def __init__(self, plugin_path: str):
        self.plugin_path = Path(plugin_path)
        self.errors = []
        self.warnings = []

    def validate(self, run_pytest: bool = False) -> bool:
        """플러그인 검증 및 테스트 자동화"""
        try:
            self._validate_structure()
            self._validate_manifest()
            self._validate_code()
            self._validate_security()
            test_result = None
            if run_pytest:
                test_path = self.plugin_path / "tests"
                if test_path.exists():
                    print("🧪 pytest로 테스트 자동 실행 중...")
                    try:
                        completed = subprocess.run(
                            [
                                "pytest",
                                str(test_path),
                                "--maxfail=1",
                                "--disable-warnings",
                                "-q",
                                "--tb=short",
                                "--json-report",
                            ],
                            capture_output=True,
                            text=True,
                        )
                        print(completed.stdout)
                        if completed.returncode != 0:
                            self.errors.append("pytest 테스트 실패")
                            test_result = False
                        else:
                            test_result = True
                        # pytest 결과 파일 저장
                        report_path = test_path / ".report.json"
                        if report_path.exists():
                            with open(report_path, "r", encoding="utf-8") as f:
                                import json

                                result_json = json.load(f)
                            with open(
                                self.plugin_path / "test_result.json",
                                "w",
                                encoding="utf-8",
                            ) as f:
                                json.dump(result_json, f, indent=2, ensure_ascii=False)
                    except Exception as e:
                        self.errors.append(f"pytest 실행 오류: {e}")
                        test_result = False
                else:
                    self.warnings.append("tests/ 디렉토리가 없습니다.")
            self._print_results()
            return len(self.errors) == 0 and (test_result is not False)
        except Exception as e:
            print(f"❌ 검증 실패: {e}")
            return False

    def _validate_structure(self):
        """구조 검증"""
        required_dirs = ["backend", "config"]
        required_files = ["config/plugin.json", "README.md"]

        for dir_name in required_dirs:
            if not (self.plugin_path / dir_name).exists():
                self.errors.append(f"필수 디렉토리 누락: {dir_name}")

        for file_name in required_files:
            if not (self.plugin_path / file_name).exists():
                self.errors.append(f"필수 파일 누락: {file_name}")

    def _validate_manifest(self):
        """매니페스트 검증"""
        manifest_path = self.plugin_path / "config" / "plugin.json"

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            required_fields = ["name", "version", "description", "author"]
            for field in required_fields:
                if field not in manifest:
                    self.errors.append(f"매니페스트 필수 필드 누락: {field}")

            # 버전 형식 검증
            version = manifest.get("version", "")
            if not self._is_valid_version(version):
                self.errors.append(f"잘못된 버전 형식: {version}")

        except json.JSONDecodeError:
            self.errors.append("매니페스트 JSON 형식 오류")
        except Exception as e:
            self.errors.append(f"매니페스트 검증 실패: {e}")

    def _validate_code(self):
        """코드 검증"""
        # Python 파일 검증
        for py_file in self.plugin_path.rglob("*.py"):
            self._validate_python_file(py_file)

    def _validate_python_file(self, file_path: Path):
        """Python 파일 검증"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 기본 검증
            if "import os" in content and "os.system" in content:
                self.warnings.append(f"잠재적 보안 위험: {file_path}")

            if "eval(" in content:
                self.errors.append(f"보안 위험 함수 사용: {file_path}")

        except Exception as e:
            self.warnings.append(f"파일 읽기 실패: {file_path} - {e}")

    def _validate_security(self):
        """보안 검증"""
        # 기본 보안 검증 로직
        pass

    def _is_valid_version(self, version: str) -> bool:
        """버전 형식 검증"""
        import re

        pattern = r"^\d+\.\d+\.\d+$"
        return bool(re.match(pattern, version))

    def _print_results(self):
        """검증 결과 출력"""
        if self.errors:
            print("❌ 검증 오류:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print("⚠️ 검증 경고:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("✅ 검증 통과!")


# 사용 예제
if __name__ == "__main__":
    # 플러그인 템플릿 생성
    template = PluginTemplate("my_plugin", "api")
    template.create_template()

    # 플러그인 검증
    validator = PluginValidator("plugins/my_plugin")
    validator.validate()

    # 플러그인 패키징
    packager = PluginPackager("plugins/my_plugin")
    packager.package()
