#!/usr/bin/env python3
"""
플러그인 템플릿 생성기
새로운 플러그인을 쉽게 생성할 수 있는 스크립트
"""

import json
import argparse
from datetime import datetime
from pathlib import Path


class PluginTemplateGenerator:
    """플러그인 템플릿 생성기"""

    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(exist_ok=True)

    def create_plugin(
        self,
        plugin_id: str,
        name: str,
        description: str,
        category: str,
        author: str = "Your Program Team",
    ) -> bool:
        """새 플러그인 생성"""
        try:
            plugin_dir = self.plugins_dir / plugin_id

            if plugin_dir.exists():
                print(f"플러그인 디렉토리가 이미 존재합니다: {plugin_dir}")
                return False

            # 플러그인 디렉토리 구조 생성
            self._create_directory_structure(plugin_dir)

            # 플러그인 설정 파일 생성
            self._create_plugin_config(
                plugin_dir, plugin_id, name, description, category, author
            )

            # 백엔드 메인 파일 생성
            self._create_backend_main(
                plugin_dir, plugin_id, name, description, category, author
            )

            # 프론트엔드 컴포넌트 생성
            self._create_frontend_components(plugin_dir, plugin_id, name)

            # README 파일 생성
            self._create_readme(plugin_dir, plugin_id, name, description)

            print(f"플러그인 '{name}' ({plugin_id}) 생성 완료!")
            print(f"위치: {plugin_dir}")
            print("\n다음 단계:")
            print("1. 플러그인 코드 수정")
            print("2. 설정 파일 확인")
            print("3. 서버 재시작")

            return True

        except Exception as e:
            print(f"플러그인 생성 실패: {e}")
            return False

    def _create_directory_structure(self, plugin_dir: Path):
        """플러그인 디렉토리 구조 생성"""
        # 백엔드 디렉토리
        (plugin_dir / "backend").mkdir(parents=True)

        # 프론트엔드 디렉토리
        (plugin_dir / "frontend").mkdir()
        (plugin_dir / "frontend" / "components").mkdir()
        (plugin_dir / "frontend" / "pages").mkdir()

        # 설정 디렉토리
        (plugin_dir / "config").mkdir()

        # DB 마이그레이션 디렉토리
        (plugin_dir / "migrations").mkdir()

        # 정적 파일 디렉토리
        (plugin_dir / "static").mkdir()
        (plugin_dir / "static" / "css").mkdir()
        (plugin_dir / "static" / "js").mkdir()
        (plugin_dir / "static" / "images").mkdir()

        # 테스트 디렉토리
        (plugin_dir / "tests").mkdir()

    def _create_plugin_config(
        self,
        plugin_dir: Path,
        plugin_id: str,
        name: str,
        description: str,
        category: str,
        author: str,
    ):
        """플러그인 설정 파일 생성"""
        config = {
            "name": name,
            "version": "1.0.0",
            "description": description,
            "author": author,
            "category": category,
            "dependencies": [],
            "permissions": [f"{plugin_id}_management"],
            "enabled": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "config": {"auto_enable": True, "debug_mode": False},
            "routes": [
                {
                    "path": "/main",
                    "methods": ["GET", "POST"],
                    "handler": "handle_main",
                    "auth_required": True,
                    "roles": ["admin", "manager"],
                    "description": "메인 기능 API",
                }
            ],
            "menus": [
                {
                    "title": name,
                    "path": f"/{plugin_id}",
                    "icon": "puzzle-piece",
                    "parent": category,
                    "roles": ["admin", "manager"],
                    "order": 1,
                }
            ],
            "config_schema": [
                {
                    "key": "auto_enable",
                    "type": "boolean",
                    "default": True,
                    "required": False,
                    "description": "자동 활성화",
                },
                {
                    "key": "debug_mode",
                    "type": "boolean",
                    "default": False,
                    "required": False,
                    "description": "디버그 모드",
                },
            ],
            "db_migrations": [f"001_create_{plugin_id}_table.sql"],
        }

        config_file = plugin_dir / "config" / "plugin.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _create_backend_main(
        self,
        plugin_dir: Path,
        plugin_id: str,
        name: str,
        description: str,
        category: str,
        author: str,
    ):
        """백엔드 메인 파일 생성"""
        main_content = f'''"""
{name} 플러그인
{description}
"""

from datetime import datetime
from typing import Dict, List, Any
from flask import Blueprint, jsonify, request
from core.backend.plugin_interface import (
    BasePlugin, PluginMetadata, PluginRoute, PluginMenu, 
    PluginConfig, PluginDependency
)

class {plugin_id.replace('_', '').title()}Plugin(BasePlugin):
    """{name} 플러그인"""
    
    def __init__(self):
        super().__init__()
        self.blueprint = Blueprint('{plugin_id}', __name__)
        self._setup_routes()
        self._setup_menus()
        self._setup_config_schema()
        self._setup_dependencies()
        
    def _setup_routes(self):
        """라우트 설정"""
        self.routes = [
            PluginRoute(
                path="/main",
                methods=["GET", "POST"],
                handler="handle_main",
                auth_required=True,
                roles=["admin", "manager"],
                description="메인 기능 API",
                version="v1"
            )
        ]
    
    def _setup_menus(self):
        """메뉴 설정"""
        self.menus = [
            PluginMenu(
                title="{name}",
                path="/{plugin_id}",
                icon="puzzle-piece",
                parent="{category}",
                roles=["admin", "manager"],
                order=1
            )
        ]
    
    def _setup_config_schema(self):
        """설정 스키마 설정"""
        self.config_schema = [
            PluginConfig(
                key="auto_enable",
                type="boolean",
                default=True,
                required=False,
                description="자동 활성화"
            ),
            PluginConfig(
                key="debug_mode",
                type="boolean",
                default=False,
                required=False,
                description="디버그 모드"
            )
        ]
    
    def _setup_dependencies(self):
        """의존성 설정"""
        self.dependencies = []
    
    def initialize(self) -> bool:
        """플러그인 초기화"""
        try:
            # 메타데이터 설정
            self.metadata = PluginMetadata(
                name="{name}",
                version="1.0.0",
                description="{description}",
                author="{author}",
                category="{category}",
                dependencies=[],
                permissions=["{plugin_id}_management"],
                enabled=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # 의존성 플러그인 알림 (플러그인 레지스트리가 있을 때만)
            try:
                from core.backend.plugin_interface import plugin_registry
                for dep in self.dependencies:
                    if dep.plugin_id in plugin_registry.plugins:
                        dep_plugin = plugin_registry.plugins[dep.plugin_id]
                        self.on_dependency_loaded(dep.plugin_id, dep_plugin)
            except ImportError:
                pass  # 플러그인 레지스트리를 찾을 수 없는 경우 무시
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"{name} 플러그인 초기화 실패: {{e}}")
            return False
    
    def cleanup(self) -> bool:
        """플러그인 정리"""
        try:
            self._initialized = False
            return True
        except Exception as e:
            print(f"{name} 플러그인 정리 실패: {{e}}")
            return False
    
    def get_metadata(self) -> PluginMetadata:
        """메타데이터 반환"""
        if self.metadata is None:
            raise ValueError("플러그인 메타데이터가 설정되지 않았습니다")
        return self.metadata
    
    # API 핸들러 메서드들
    def handle_main(self):
        """메인 기능 핸들러"""
        if request.method == "GET":
            # 데이터 조회
            data = {{
                "message": "{name} 플러그인이 정상적으로 작동하고 있습니다",
                "timestamp": datetime.utcnow().isoformat(),
                "plugin_id": "{plugin_id}"
            }}
            return jsonify(data)
        elif request.method == "POST":
            # 데이터 생성
            data = request.get_json()
            return jsonify({{"message": "데이터가 생성되었습니다", "data": data}})

def create_plugin() -> {plugin_id.replace('_', '').title()}Plugin:
    """플러그인 인스턴스 생성"""
    return {plugin_id.replace('_', '').title()}Plugin()
'''

        main_file = plugin_dir / "backend" / "main.py"
        with open(main_file, "w", encoding="utf-8") as f:
            f.write(main_content)

    def _create_frontend_components(self, plugin_dir: Path, plugin_id: str, name: str):
        """프론트엔드 컴포넌트 생성"""
        # 메인 페이지 컴포넌트
        page_content = f"""import React from 'react';
import {{ Card, CardContent, CardHeader, CardTitle }} from '@/components/ui/card';
import {{ Button }} from '@/components/ui/button';

export default function {plugin_id.replace('_', '').title()}Page() {{
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">{name}</h1>
        <Button>새로 만들기</Button>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>{name} 대시보드</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            {name} 플러그인이 성공적으로 로드되었습니다.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}}
"""

        page_file = plugin_dir / "frontend" / "pages" / f"{plugin_id}.tsx"
        with open(page_file, "w", encoding="utf-8") as f:
            f.write(page_content)

    def _create_readme(
        self, plugin_dir: Path, plugin_id: str, name: str, description: str
    ):
        """README 파일 생성"""
        readme_content = f"""# {name} 플러그인

{description}

## 설치

이 플러그인은 자동으로 로드됩니다. 서버를 재시작하면 활성화됩니다.

## 설정

플러그인 설정은 `config/plugin.json` 파일에서 관리됩니다.

## API 엔드포인트

- `GET /api/plugins/{plugin_id}/main` - 메인 기능 조회
- `POST /api/plugins/{plugin_id}/main` - 메인 기능 생성

## 개발

### 백엔드

백엔드 코드는 `backend/main.py` 파일에 있습니다.

### 프론트엔드

프론트엔드 컴포넌트는 `frontend/` 디렉토리에 있습니다.

## 테스트

테스트는 `tests/` 디렉토리에 작성하세요.

## 라이센스

MIT License
"""

        readme_file = plugin_dir / "README.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(readme_content)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="플러그인 템플릿 생성기")
    parser.add_argument("plugin_id", help="플러그인 ID (예: my_plugin)")
    parser.add_argument("name", help="플러그인 이름 (예: 내 플러그인)")
    parser.add_argument("description", help="플러그인 설명")
    parser.add_argument(
        "--category", default="general", help="플러그인 카테고리 (기본값: general)"
    )
    parser.add_argument(
        "--author",
        default="Your Program Team",
        help="작성자 (기본값: Your Program Team)",
    )
    parser.add_argument(
        "--plugins-dir", default="plugins", help="플러그인 디렉토리 (기본값: plugins)"
    )

    args = parser.parse_args()

    generator = PluginTemplateGenerator(args.plugins_dir)
    success = generator.create_plugin(
        plugin_id=args.plugin_id,
        name=args.name,
        description=args.description,
        category=args.category,
        author=args.author,
    )

    if success:
        print("✅ 플러그인 생성 완료!")
    else:
        print("❌ 플러그인 생성 실패!")
        exit(1)


if __name__ == "__main__":
    main()
