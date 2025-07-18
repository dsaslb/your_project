#!/usr/bin/env python3
"""
플러그인 개발 템플릿 생성기
업종별 플러그인 템플릿을 자동으로 생성하는 도구
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict


class PluginTemplateGenerator:
    def __init__(self, base_path: str = "plugins"):
        self.base_path = Path(base_path)
        self.templates = {
            "restaurant": {
                "name": "레스토랑 관리",
                "description": "레스토랑 업종 전용 관리 기능",
                "category": "restaurant",
                "features": ["메뉴 관리", "주문 처리", "재고 관리", "직원 관리"],
            },
            "cafe": {
                "name": "카페 관리",
                "description": "카페 업종 전용 관리 기능",
                "category": "cafe",
                "features": ["음료 관리", "주문 처리", "재고 관리", "직원 관리"],
            },
            "retail": {
                "name": "소매점 관리",
                "description": "소매점 업종 전용 관리 기능",
                "category": "retail",
                "features": ["상품 관리", "판매 처리", "재고 관리", "직원 관리"],
            },
            "custom": {
                "name": "커스텀 플러그인",
                "description": "사용자 정의 플러그인",
                "category": "custom",
                "features": ["기본 기능"],
            },
        }

    def generate_plugin_structure(
        self,
        plugin_id: str,
        industry: str,
        author: str = "Developer",
        version: str = "1.0.0",
    ) -> bool:
        """플러그인 구조 생성"""
        try:
            plugin_path = self.base_path / plugin_id

            if plugin_path.exists():
                print(f"❌ 플러그인 {plugin_id}이 이미 존재합니다.")
                return False

            # 플러그인 디렉토리 생성
            plugin_path.mkdir(parents=True, exist_ok=True)

            # 업종별 템플릿 정보 가져오기
            template_info = self.templates.get(industry, self.templates["custom"])

            # 기본 파일 구조 생성
            self._create_backend_structure(
                plugin_path, plugin_id, template_info, author, version
            )
            self._create_frontend_structure(plugin_path, plugin_id, template_info)
            self._create_config_structure(
                plugin_path, plugin_id, template_info, author, version
            )
            self._create_docs_structure(plugin_path, plugin_id, template_info)

            print(f"✅ 플러그인 {plugin_id} 구조가 생성되었습니다.")
            print(f"📁 위치: {plugin_path}")
            return True

        except Exception as e:
            print(f"❌ 플러그인 생성 중 오류: {e}")
            return False

    def _create_backend_structure(
        self,
        plugin_path: Path,
        plugin_id: str,
        template_info: Dict,
        author: str,
        version: str,
    ):
        """백엔드 구조 생성"""
        backend_path = plugin_path / "backend"
        backend_path.mkdir(exist_ok=True)

        # main.py 생성
        main_content = self._generate_main_py(plugin_id, template_info, author, version)
        with open(backend_path / "main.py", "w", encoding="utf-8") as f:
            f.write(main_content)

        # __init__.py 생성
        init_content = f'''"""
{template_info['name']} 플러그인 백엔드
{template_info['description']}
"""

from .main import {plugin_id.replace('-', '_').title()}Plugin

__all__ = ['{plugin_id.replace('-', '_').title()}Plugin']
'''
        with open(backend_path / "__init__.py", "w", encoding="utf-8") as f:
            f.write(init_content)

    def _create_frontend_structure(
        self, plugin_path: Path, plugin_id: str, template_info: Dict
    ):
        """프론트엔드 구조 생성"""
        frontend_path = plugin_path / "frontend"
        frontend_path.mkdir(exist_ok=True)

        # package.json 생성
        package_json = {
            "name": f"@{plugin_id}/frontend",
            "version": "1.0.0",
            "description": template_info["description"],
            "main": "index.js",
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
            },
            "dependencies": {
                "react": "^18.0.0",
                "next": "^13.0.0",
                "@types/react": "^18.0.0",
            },
        }

        with open(frontend_path / "package.json", "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2, ensure_ascii=False)

    def _create_config_structure(
        self,
        plugin_path: Path,
        plugin_id: str,
        template_info: Dict,
        author: str,
        version: str,
    ):
        """설정 파일 구조 생성"""
        config_path = plugin_path / "config"
        config_path.mkdir(exist_ok=True)

        # plugin.json 생성
        plugin_config = {
            "id": plugin_id,
            "name": template_info["name"],
            "version": version,
            "description": template_info["description"],
            "author": author,
            "category": template_info["category"],
            "dependencies": [],
            "permissions": ["read", "write"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        with open(config_path / "plugin.json", "w", encoding="utf-8") as f:
            json.dump(plugin_config, f, indent=2, ensure_ascii=False)

        # requirements.txt 생성
        requirements = ["flask>=2.0.0", "sqlalchemy>=1.4.0", "pydantic>=1.8.0"]

        with open(config_path / "requirements.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(requirements))

    def _create_docs_structure(
        self, plugin_path: Path, plugin_id: str, template_info: Dict
    ):
        """문서 구조 생성"""
        docs_path = plugin_path / "docs"
        docs_path.mkdir(exist_ok=True)

        # README.md 생성
        readme_content = f"""# {template_info['name']} 플러그인

{template_info['description']}

## 기능

{chr(10).join([f"- {feature}" for feature in template_info['features']])}

## 설치

1. 플러그인을 `plugins/{plugin_id}` 디렉토리에 복사
2. 백엔드 의존성 설치: `pip install -r config/requirements.txt`
3. 프론트엔드 의존성 설치: `npm install` (frontend 디렉토리에서)
4. 플러그인 활성화

## 설정

`config/plugin.json` 파일에서 플러그인 설정을 수정할 수 있습니다.

## 개발

### 백엔드 개발
- `backend/main.py`: 메인 플러그인 로직
- `backend/__init__.py`: 플러그인 진입점

### 프론트엔드 개발
- `frontend/`: Next.js 기반 프론트엔드
- `frontend/pages/`: 페이지 컴포넌트
- `frontend/components/`: 재사용 가능한 컴포넌트

## API

플러그인 API는 `/api/plugins/{plugin_id}/` 경로에서 접근할 수 있습니다.

## 라이선스

MIT License
"""

        with open(docs_path / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)

    def _generate_main_py(
        self, plugin_id: str, template_info: Dict, author: str, version: str
    ) -> str:
        """main.py 파일 내용 생성"""
        class_name = plugin_id.replace("-", "_").title()

        return f'''"""
{template_info['name']} 플러그인
{template_info['description']}
"""

from datetime import datetime
from flask import Blueprint, jsonify, request
from core.backend.plugin_interface import (
    BasePlugin, PluginMetadata, PluginRoute, PluginMenu, 
    PluginConfig, PluginDependency
)


class {class_name}Plugin(BasePlugin):
    """{template_info['name']} 플러그인 클래스"""
    
    def __init__(self):
        super().__init__()
        self.plugin_id = "{plugin_id}"
        self.blueprint = Blueprint(self.plugin_id, __name__)
        self._setup_routes()
    
    def get_metadata(self) -> PluginMetadata:
        """플러그인 메타데이터 반환"""
        return PluginMetadata(
            id=self.plugin_id,
            name="{template_info['name']}",
            version="{version}",
            description="{template_info['description']}",
            author="{author}",
            category="{template_info['category']}",
            dependencies=[],
            permissions=["read", "write"]
        )
    
    def get_routes(self) -> List[PluginRoute]:
        """플러그인 라우트 반환"""
        return [
            PluginRoute(
                path="/",
                methods=["GET"],
                handler=self._index_handler,
                description="플러그인 메인 페이지"
            ),
            PluginRoute(
                path="/api/status",
                methods=["GET"],
                handler=self._status_handler,
                description="플러그인 상태 확인"
            )
        ]
    
    def get_menus(self) -> List[PluginMenu]:
        """플러그인 메뉴 반환"""
        return [
            PluginMenu(
                id=f"{plugin_id}_main",
                title="{template_info['name']}",
                path=f"/{plugin_id}",
                icon="package",
                parent=None,
                order=1
            )
        ]
    
    def get_config_schema(self) -> Dict:
        """플러그인 설정 스키마 반환"""
        return {{
            "type": "object",
            "properties": {{
                "enabled": {{
                    "type": "boolean",
                    "default": True,
                    "description": "플러그인 활성화 여부"
                }},
                "debug_mode": {{
                    "type": "boolean",
                    "default": False,
                    "description": "디버그 모드"
                }}
            }}
        }}
    
    def on_enable(self) -> bool:
        """플러그인 활성화 시 호출"""
        try:
            print(f"✅ {template_info['name']} 플러그인이 활성화되었습니다.")
            return True
        except Exception as e:
            print(f"❌ {template_info['name']} 플러그인 활성화 실패: {{e}}")
            return False
    
    def on_disable(self) -> bool:
        """플러그인 비활성화 시 호출"""
        try:
            print(f"✅ {template_info['name']} 플러그인이 비활성화되었습니다.")
            return True
        except Exception as e:
            print(f"❌ {template_info['name']} 플러그인 비활성화 실패: {{e}}")
            return False
    
    def get_health_status(self) -> Dict:
        """플러그인 상태 반환"""
        return {{
            "status": "healthy",
            "uptime": datetime.utcnow().isoformat(),
            "version": "{version}",
            "features": {template_info['features']}
        }}
    
    def _setup_routes(self):
        """라우트 설정"""
        @self.blueprint.route("/")
        def index():
            return jsonify({{
                "plugin": "{plugin_id}",
                "name": "{template_info['name']}",
                "version": "{version}",
                "status": "active"
            }})
        
        @self.blueprint.route("/api/status")
        def status():
            return jsonify(self.get_health_status())
    
    def _index_handler(self):
        """메인 페이지 핸들러"""
        return jsonify({{
            "plugin": "{plugin_id}",
            "name": "{template_info['name']}",
            "version": "{version}",
            "status": "active"
        }})
    
    def _status_handler(self):
        """상태 확인 핸들러"""
        return jsonify(self.get_health_status())


# 플러그인 인스턴스 생성
{plugin_id.replace('-', '_')}_plugin = {class_name}Plugin()
'''

    def list_templates(self) -> Dict[str, Dict]:
        """사용 가능한 템플릿 목록 반환"""
        return self.templates

    def validate_plugin_id(self, plugin_id: str) -> bool:
        """플러그인 ID 유효성 검사"""
        if not plugin_id:
            return False

        # 허용된 문자만 포함
        allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789-_"
        return all(c in allowed_chars for c in plugin_id.lower())

    def create_sample_data(self, plugin_id: str, industry: str) -> bool:
        """샘플 데이터 생성"""
        try:
            plugin_path = self.base_path / plugin_id
            if not plugin_path.exists():
                print(f"❌ 플러그인 {plugin_id}이 존재하지 않습니다.")
                return False

            # 업종별 샘플 데이터 생성
            if industry == "restaurant":
                self._create_restaurant_sample_data(plugin_path)
            elif industry == "cafe":
                self._create_cafe_sample_data(plugin_path)
            elif industry == "retail":
                self._create_retail_sample_data(plugin_path)

            print(f"✅ {plugin_id} 플러그인에 샘플 데이터가 생성되었습니다.")
            return True

        except Exception as e:
            print(f"❌ 샘플 데이터 생성 중 오류: {e}")
            return False

    def _create_restaurant_sample_data(self, plugin_path: Path):
        """레스토랑 샘플 데이터 생성"""
        data_path = plugin_path / "data"
        data_path.mkdir(exist_ok=True)

        sample_data = {
            "menus": [
                {"id": 1, "name": "스테이크", "price": 25000, "category": "메인"},
                {"id": 2, "name": "파스타", "price": 15000, "category": "메인"},
                {"id": 3, "name": "샐러드", "price": 8000, "category": "사이드"},
            ],
            "orders": [
                {"id": 1, "menu_id": 1, "quantity": 2, "status": "completed"},
                {"id": 2, "menu_id": 2, "quantity": 1, "status": "pending"},
            ],
        }

        with open(data_path / "sample_data.json", "w", encoding="utf-8") as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)

    def _create_cafe_sample_data(self, plugin_path: Path):
        """카페 샘플 데이터 생성"""
        data_path = plugin_path / "data"
        data_path.mkdir(exist_ok=True)

        sample_data = {
            "drinks": [
                {"id": 1, "name": "아메리카노", "price": 4500, "category": "커피"},
                {"id": 2, "name": "카페라떼", "price": 5500, "category": "커피"},
                {"id": 3, "name": "스무디", "price": 6500, "category": "음료"},
            ],
            "orders": [
                {"id": 1, "drink_id": 1, "quantity": 1, "status": "completed"},
                {"id": 2, "drink_id": 2, "quantity": 2, "status": "pending"},
            ],
        }

        with open(data_path / "sample_data.json", "w", encoding="utf-8") as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)

    def _create_retail_sample_data(self, plugin_path: Path):
        """소매점 샘플 데이터 생성"""
        data_path = plugin_path / "data"
        data_path.mkdir(exist_ok=True)

        sample_data = {
            "products": [
                {"id": 1, "name": "노트북", "price": 800000, "category": "전자제품"},
                {"id": 2, "name": "마우스", "price": 25000, "category": "전자제품"},
                {"id": 3, "name": "키보드", "price": 50000, "category": "전자제품"},
            ],
            "sales": [
                {"id": 1, "product_id": 1, "quantity": 1, "status": "completed"},
                {"id": 2, "product_id": 2, "quantity": 3, "status": "pending"},
            ],
        }

        with open(data_path / "sample_data.json", "w", encoding="utf-8") as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)


def main():
    """메인 함수"""
    generator = PluginTemplateGenerator()

    print("🚀 플러그인 템플릿 생성기")
    print("=" * 50)

    # 사용 가능한 템플릿 목록 표시
    print("\n📋 사용 가능한 템플릿:")
    for key, template in generator.templates.items():
        print(f"  {key}: {template['name']} - {template['description']}")

    # 사용자 입력 받기
    print("\n" + "=" * 50)
    plugin_id = input("플러그인 ID를 입력하세요 (예: my-restaurant-plugin): ").strip()

    if not generator.validate_plugin_id(plugin_id):
        print(
            "❌ 잘못된 플러그인 ID입니다. 영문자, 숫자, 하이픈, 언더스코어만 사용 가능합니다."
        )
        return

    print("\n업종을 선택하세요:")
    for i, (key, template) in enumerate(generator.templates.items(), 1):
        print(f"  {i}. {key}: {template['name']}")

    try:
        choice = int(input("선택 (1-4): ").strip())
        industries = list(generator.templates.keys())
        if 1 <= choice <= len(industries):
            industry = industries[choice - 1]
        else:
            print("❌ 잘못된 선택입니다.")
            return
    except ValueError:
        print("❌ 숫자를 입력해주세요.")
        return

    author = input("작성자 이름 (기본값: Developer): ").strip() or "Developer"
    version = input("버전 (기본값: 1.0.0): ").strip() or "1.0.0"

    # 플러그인 생성
    print(f"\n🔨 {plugin_id} 플러그인을 생성 중...")
    if generator.generate_plugin_structure(plugin_id, industry, author, version):
        # 샘플 데이터 생성 여부 확인
        create_sample = (
            input("\n샘플 데이터를 생성하시겠습니까? (y/N): ").strip().lower()
        )
        if create_sample == "y":
            generator.create_sample_data(plugin_id, industry)

        print(f"\n🎉 플러그인 생성이 완료되었습니다!")
        print(f"📁 위치: plugins/{plugin_id}")
        print(f"📖 문서: plugins/{plugin_id}/docs/README.md")
        print(f"⚙️  설정: plugins/{plugin_id}/config/plugin.json")
        print("\n다음 단계:")
        print("1. 플러그인 디렉토리로 이동")
        print("2. 백엔드 의존성 설치: pip install -r config/requirements.txt")
        print("3. 플러그인 개발 시작")


if __name__ == "__main__":
    main()
