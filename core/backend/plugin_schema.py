from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import jsonschema
import json
from typing import Optional

args = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore


class PluginSchemaValidator:
    """플러그인 메타데이터 스키마 검증기"""

    # 플러그인 메타데이터 표준 스키마
    PLUGIN_SCHEMA = {
        "type": "object",
        "required": ["name", "version", "description", "author"],
        "properties": {
            "name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 100,
                "description": "플러그인 이름",
            },
            "version": {
                "type": "string",
                "pattern": r"^\d+\.\d+\.\d+$",
                "description": "플러그인 버전 (예: 1.0.0)",
            },
            "description": {
                "type": "string",
                "minLength": 1,
                "maxLength": 500,
                "description": "플러그인 설명",
            },
            "author": {
                "type": "string",
                "minLength": 1,
                "maxLength": 100,
                "description": "플러그인 저자",
            },
            "category": {
                "type": "string",
                "enum": ["restaurant", "retail", "service", "manufacturing", "general"],
                "default": "general",
                "description": "지원 업종 카테고리",
            },
            "dependencies": {
                "type": "array",
                "items": {"type": "string"},
                "description": "의존 플러그인 목록",
            },
            "permissions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "필요 권한 목록",
            },
            "enabled": {
                "type": "boolean",
                "default": True,
                "description": "플러그인 활성화 상태",
            },
            "created_at": {
                "type": "string",
                "format": "date-time",
                "description": "생성일시",
            },
            "updated_at": {
                "type": "string",
                "format": "date-time",
                "description": "수정일시",
            },
            "config": {"type": "object", "description": "플러그인 설정"},
            "routes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["path", "methods", "handler"],
                    "properties": {
                        "path": {"type": "string", "description": "API 경로"},
                        "methods": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                            },
                            "description": "HTTP 메서드",
                        },
                        "handler": {"type": "string", "description": "핸들러 함수명"},
                        "auth_required": {
                            "type": "boolean",
                            "default": True,
                            "description": "인증 필요 여부",
                        },
                        "roles": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "접근 가능한 역할",
                        },
                        "description": {"type": "string", "description": "API 설명"},
                    },
                },
                "description": "API 라우트 정의",
            },
            "menus": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["title", "path"],
                    "properties": {
                        "title": {"type": "string", "description": "메뉴 제목"},
                        "path": {"type": "string", "description": "메뉴 경로"},
                        "icon": {"type": "string", "description": "메뉴 아이콘"},
                        "parent": {"type": "string", "description": "부모 메뉴"},
                        "roles": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "접근 가능한 역할",
                        },
                        "order": {
                            "type": "integer",
                            "minimum": 0,
                            "description": "메뉴 순서",
                        },
                        "badge": {"type": "string", "description": "배지 텍스트"},
                    },
                },
                "description": "메뉴 정의",
            },
            "config_schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["key", "type", "description"],
                    "properties": {
                        "key": {"type": "string", "description": "설정 키"},
                        "type": {
                            "type": "string",
                            "enum": [
                                "string",
                                "number",
                                "boolean",
                                "select",
                                "textarea",
                            ],
                            "description": "설정 타입",
                        },
                        "default": {"description": "기본값"},
                        "required": {
                            "type": "boolean",
                            "default": False,
                            "description": "필수 여부",
                        },
                        "description": {"type": "string", "description": "설정 설명"},
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "선택 옵션 (select 타입용)",
                        },
                        "min": {
                            "type": "number",
                            "description": "최소값 (number 타입용)",
                        },
                        "max": {
                            "type": "number",
                            "description": "최대값 (number 타입용)",
                        },
                    },
                },
                "description": "설정 스키마 정의",
            },
            "db_migrations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "데이터베이스 마이그레이션 파일 목록",
            },
            "marketplace": {
                "type": "object",
                "properties": {
                    "price": {
                        "type": "number",
                        "minimum": 0,
                        "description": "가격 (0은 무료)",
                    },
                    "currency": {
                        "type": "string",
                        "default": "KRW",
                        "description": "통화",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "마켓플레이스 태그",
                    },
                    "screenshots": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "스크린샷 파일 경로",
                    },
                    "demo_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "데모 URL",
                    },
                    "documentation_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "문서 URL",
                    },
                    "support_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "지원 URL",
                    },
                },
                "description": "마켓플레이스 정보",
            },
        },
    }

    def __init__(self):
        self.validator = jsonschema.Draft7Validator(self.PLUGIN_SCHEMA)

    def validate_plugin_config(self, config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """플러그인 설정 검증"""
        errors = []

        try:
            self.validator.validate(config)
        except jsonschema.ValidationError as e:
            errors.append(f"스키마 검증 오류: {e.message}")
        except Exception as e:
            errors.append(f"검증 중 오류 발생: {str(e)}")

        # 추가 검증 로직
        additional_errors = self._validate_additional_rules(config)
        errors.extend(additional_errors)

        return len(errors) == 0, errors

    def _validate_additional_rules(self, config: Dict[str, Any]) -> List[str]:
        """추가 검증 규칙"""
        errors = []

        # 버전 형식 검증
        version = config.get("version", "")
        if not self._is_valid_version(version):
            errors.append(f"잘못된 버전 형식: {version}")

        # 의존성 순환 검증
        dependencies = config.get("dependencies", [])
        if config.get("name") in dependencies:
            errors.append("자기 자신을 의존성으로 가질 수 없습니다")

        # 라우트 경로 중복 검증
        routes = config.get("routes", [])
        paths = [route.get("path") for route in routes if route]
        if len(paths) != len(set(paths)):
            errors.append("중복된 라우트 경로가 있습니다")

        # 메뉴 경로 중복 검증
        menus = config.get("menus", [])
        menu_paths = [menu.get("path") for menu in menus if menu]
        if len(menu_paths) != len(set(menu_paths)):
            errors.append("중복된 메뉴 경로가 있습니다")

        return errors

    def _is_valid_version(self, version: str) -> bool:
        """버전 형식 검증"""
        import re

        pattern = r"^\d+\.\d+\.\d+$"
        return bool(re.match(pattern, version))

    def create_plugin_template(self, plugin_name: str, **kwargs) -> Dict[str, Any]:
        """플러그인 템플릿 생성"""
        now = datetime.now().isoformat()

        template = {
            "name": kwargs.get("name", plugin_name),
            "version": kwargs.get("version", "1.0.0"),
            "description": kwargs.get("description", f"{plugin_name} 플러그인"),
            "author": kwargs.get("author", "Your Name"),
            "category": kwargs.get("category", "general"),
            "dependencies": kwargs.get("dependencies", []),
            "permissions": kwargs.get("permissions", []),
            "enabled": kwargs.get("enabled", True),
            "created_at": now,
            "updated_at": now,
            "config": kwargs.get("config", {}),
            "routes": kwargs.get("routes", []),
            "menus": kwargs.get("menus", []),
            "config_schema": kwargs.get("config_schema", []),
            "db_migrations": kwargs.get("db_migrations", []),
            "marketplace": kwargs.get("marketplace", {}),
        }

        return template

    def update_plugin_config(
        self, config: Dict[str, Any], updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """플러그인 설정 업데이트"""
        updated_config = config.copy()
        updated_config.update(updates)
        updated_config["updated_at"] = datetime.now().isoformat()

        return updated_config


class PluginManifest:
    """플러그인 매니페스트 관리"""

    def __init__(self, plugin_dir: Path):
        self.plugin_dir = plugin_dir
        self.config_file = plugin_dir / "config" / "plugin.json"
        self.validator = PluginSchemaValidator()

    def load(self) -> Optional[Dict[str, Any]]:
        """매니페스트 로드"""
        if not self.config_file.exists():
            return None

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 검증
            is_valid, errors = self.validator.validate_plugin_config(config)
            if not is_valid:
                raise ValueError(f"플러그인 설정 검증 실패: {', '.join(errors)}")

            return config
        except Exception as e:
            raise ValueError(f"매니페스트 로드 실패: {e}")

    def save(self, config: Dict[str, Any]) -> bool:
        """매니페스트 저장"""
        try:
            # 검증
            is_valid, errors = self.validator.validate_plugin_config(config)
            if not is_valid:
                raise ValueError(f"플러그인 설정 검증 실패: {', '.join(errors)}")

            # 디렉토리 생성
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # 저장
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            raise ValueError(f"매니페스트 저장 실패: {e}")

    def create_new(self, plugin_name: str, **kwargs) -> Dict[str, Any]:
        """새 매니페스트 생성"""
        template = self.validator.create_plugin_template(plugin_name, **kwargs)
        self.save(template)
        return template

    def update(self, updates: Dict[str, Any]) -> bool:
        """매니페스트 업데이트"""
        config = self.load()
        if not config:
            return False

        updated_config = self.validator.update_plugin_config(config, updates)
        return self.save(updated_config)
