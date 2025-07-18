from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import shutil
import json
from typing import Optional
from flask import jsonify
from flask import Blueprint
from flask import request

config = None  # pyright: ignore
form = None  # pyright: ignore


@dataclass
class MarketplacePlugin:
    """마켓플레이스 플러그인 정보"""

    id: str
    name: str
    version: str
    description: str
    author: str
    category: str
    price: float
    currency: str
    tags: List[str] = field(default_factory=list)  # pyright: ignore
    screenshots: List[str] = field(default_factory=list)  # pyright: ignore
    demo_url: Optional[str] = None
    documentation_url: Optional[str] = None
    support_url: Optional[str] = None
    rating: float = 0.0
    downloads: int = 0
    reviews: List[Dict[str, Any]] = field(default_factory=list)  # pyright: ignore
    created_at: str = ""
    updated_at: str = ""
    status: str = "active"


@dataclass
class PluginReview:
    """플러그인 리뷰"""

    id: str
    plugin_id: str
    user_id: str
    user_name: str
    rating: int
    comment: str
    created_at: str
    helpful_count: int = 0


class PluginMarketplace:
    """플러그인 마켓플레이스 관리"""

    def __init__(self, marketplace_dir="marketplace"):
        self.marketplace_dir = Path(marketplace_dir)
        self.marketplace_dir.mkdir(exist_ok=True)

        # 마켓플레이스 데이터 파일
        self.plugins_file = self.marketplace_dir / "plugins.json"
        self.reviews_file = self.marketplace_dir / "reviews.json"
        self.categories_file = self.marketplace_dir / "categories.json"

        # 초기화
        self._init_marketplace()

    def _init_marketplace(self):
        """마켓플레이스 초기화"""
        # 기본 카테고리 생성
        if not self.categories_file.exists():
            categories = [
                {
                    "id": "restaurant",
                    "name": "레스토랑",
                    "description": "레스토랑 업종 전용",
                },
                {"id": "retail", "name": "소매", "description": "소매 업종 전용"},
                {"id": "service", "name": "서비스", "description": "서비스 업종 전용"},
                {
                    "id": "manufacturing",
                    "name": "제조",
                    "description": "제조 업종 전용",
                },
                {"id": "general", "name": "일반", "description": "모든 업종 공통"},
            ]
            with open(self.categories_file, "w", encoding="utf-8") as f:
                json.dump(categories, f, indent=2, ensure_ascii=False)

        # 플러그인 목록 초기화
        if not self.plugins_file.exists():
            with open(self.plugins_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

        # 리뷰 목록 초기화
        if not self.reviews_file.exists():
            with open(self.reviews_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

    def add_plugin_to_marketplace(self, plugin_data: Dict[str, Any]) -> bool:
        """마켓플레이스에 플러그인 추가"""
        try:
            plugins = self._load_plugins()

            # 중복 검사
            existing_plugin = next(
                (p for p in plugins if p["id"] == plugin_data["id"]), None
            )
            if existing_plugin:
                # 기존 플러그인 업데이트
                existing_plugin.update(plugin_data)
                existing_plugin["updated_at"] = datetime.now().isoformat()
            else:
                # 새 플러그인 추가
                plugin_data["created_at"] = datetime.now().isoformat()
                plugin_data["updated_at"] = datetime.now().isoformat()
                plugin_data.setdefault("rating", 0.0)
                plugin_data.setdefault("downloads", 0)
                plugin_data.setdefault("reviews", [])
                plugin_data.setdefault("status", "active")
                plugins.append(plugin_data)

            self._save_plugins(plugins)
            return True

        except Exception as e:
            print(f"마켓플레이스 플러그인 추가 실패: {e}")
            return False

    def remove_plugin_from_marketplace(self, plugin_id: str) -> bool:
        """마켓플레이스에서 플러그인 제거"""
        try:
            plugins = self._load_plugins()
            plugins = [p for p in plugins if p["id"] != plugin_id]
            self._save_plugins(plugins)
            return True

        except Exception as e:
            print(f"마켓플레이스 플러그인 제거 실패: {e}")
            return False

    def get_marketplace_plugins(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "rating",
        sort_order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """마켓플레이스 플러그인 목록 조회"""
        try:
            plugins = self._load_plugins()
            if category:
                plugins = [p for p in plugins if p.get("category") == category]
            if search:
                search_lower = search.lower()
                plugins = [
                    p
                    for p in plugins
                    if search_lower in p.get("name", "").lower()
                    or search_lower in p.get("description", "").lower()
                    or any(search_lower in tag.lower() for tag in p.get("tags", []))
                ]
            reverse = sort_order == "desc"
            if sort_by == "rating":
                plugins.sort(key=lambda x: x.get("rating", 0), reverse=reverse)
            elif sort_by == "downloads":
                plugins.sort(key=lambda x: x.get("downloads", 0), reverse=reverse)
            elif sort_by == "created_at":
                plugins.sort(key=lambda x: x.get("created_at", ""), reverse=reverse)
            elif sort_by == "price":
                plugins.sort(key=lambda x: x.get("price", 0), reverse=reverse)
            return plugins
        except Exception as e:
            print(f"마켓플레이스 플러그인 목록 조회 실패: {e}")
            return []

    def get_plugin_details(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """플러그인 상세 정보 조회"""
        try:
            plugins = self._load_plugins()
            plugin = next((p for p in plugins if p.get("id") == plugin_id), None)
            return plugin
        except Exception as e:
            print(f"플러그인 상세 정보 조회 실패: {e}")
            return None

    def install_plugin_from_marketplace(
        self, plugin_id: str, target_dir: str = "plugins"
    ) -> bool:
        """마켓플레이스에서 플러그인 설치"""
        try:
            plugin = self.get_plugin_details(plugin_id)
            if not plugin:
                return False

            # 플러그인 파일 복사 (실제 구현에서는 다운로드/압축해제)
            plugin_dir = Path(target_dir) / plugin_id
            if plugin_dir.exists():
                shutil.rmtree(plugin_dir)

            # 기본 플러그인 구조 생성
            plugin_dir.mkdir(parents=True, exist_ok=True)
            (plugin_dir / "backend").mkdir(exist_ok=True)
            (plugin_dir / "config").mkdir(exist_ok=True)
            (plugin_dir / "templates").mkdir(exist_ok=True)
            (plugin_dir / "static").mkdir(exist_ok=True)

            # 플러그인 매니페스트 생성
            manifest = {
                "name": plugin.get("name"),
                "version": plugin.get("version"),
                "description": plugin.get("description"),
                "author": plugin.get("author"),
                "category": plugin.get("category"),
                "dependencies": [],
                "permissions": [],
                "enabled": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "config": {},
                "routes": [],
                "menus": [],
                "config_schema": [],
                "db_migrations": [],
                "marketplace": {
                    "price": plugin.get("price", 0),
                    "currency": plugin.get("currency", "KRW"),
                    "tags": plugin.get("tags", []),
                    "screenshots": plugin.get("screenshots", []),
                    "demo_url": plugin.get("demo_url"),
                    "documentation_url": plugin.get("documentation_url"),
                    "support_url": plugin.get("support_url"),
                },
            }

            with open(
                plugin_dir / "config" / "plugin.json", "w", encoding="utf-8"
            ) as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)

            # 기본 백엔드 파일 생성
            backend_file = plugin_dir / "backend" / "main.py"
            with open(backend_file, "w", encoding="utf-8") as f:
                f.write(
                    f'''# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request

def register_blueprint(bp):
    """플러그인 블루프린트 등록"""
    @bp.route('/')
    def index():
        """플러그인 메인 페이지"""
        return jsonify({{
            "message": "Hello from {plugin.get('name')} plugin!",
            "plugin": "{plugin_id}",
            "version": "{plugin.get('version')}"
        }})
    @bp.route('/config')
    def get_config():
        """플러그인 설정 조회"""
        return jsonify({{
            "plugin": "{plugin_id}",
            "config": {{}}
        }})
# 블루프린트 생성
bp = Blueprint('{plugin_id}', __name__)
# 블루프린트 등록
register_blueprint(bp)
'''
                )

            # 다운로드 수 증가
            self._increment_downloads(plugin_id)

            return True

        except Exception as e:
            print(f"플러그인 설치 실패: {e}")
            return False

    def add_review(
        self, plugin_id: str, user_id: str, user_name: str, rating: int, comment: str
    ) -> bool:
        """플러그인 리뷰 추가"""
        try:
            reviews = self._load_reviews()

            review = {
                "id": f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}",
                "plugin_id": plugin_id,
                "user_id": user_id,
                "user_name": user_name,
                "rating": rating,
                "comment": comment,
                "created_at": datetime.now().isoformat(),
                "helpful_count": 0,
            }

            reviews.append(review)
            self._save_reviews(reviews)

            # 플러그인 평점 업데이트
            self._update_plugin_rating(plugin_id)

            return True

        except Exception as e:
            print(f"리뷰 추가 실패: {e}")
            return False

    def get_plugin_reviews(
        self, plugin_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """플러그인 리뷰 목록 조회"""
        try:
            reviews = self._load_reviews()
            plugin_reviews = [r for r in reviews if r.get("plugin_id") == plugin_id]
            return plugin_reviews[-limit:]

        except Exception as e:
            print(f"플러그인 리뷰 조회 실패: {e}")
            return []

    def get_categories(self) -> List[Dict[str, Any]]:
        """카테고리 목록 조회"""
        try:
            with open(self.categories_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _load_plugins(self) -> List[Dict[str, Any]]:
        """플러그인 목록 로드"""
        try:
            with open(self.plugins_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_plugins(self, plugins: List[Dict[str, Any]]):
        """플러그인 목록 저장"""
        with open(self.plugins_file, "w", encoding="utf-8") as f:
            json.dump(plugins, f, indent=2, ensure_ascii=False)

    def _load_reviews(self) -> List[Dict[str, Any]]:
        """리뷰 목록 로드"""
        try:
            with open(self.reviews_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_reviews(self, reviews: List[Dict[str, Any]]):
        """리뷰 목록 저장"""
        with open(self.reviews_file, "w", encoding="utf-8") as f:
            json.dump(reviews, f, indent=2, ensure_ascii=False)

    def _increment_downloads(self, plugin_id: str):
        """다운로드 수 증가"""
        plugins = self._load_plugins()
        for plugin in plugins:
            if plugin["id"] == plugin_id:
                plugin["downloads"] = plugin.get("downloads", 0) + 1
                break
        self._save_plugins(plugins)

    def _update_plugin_rating(self, plugin_id: str):
        """플러그인 평점 업데이트"""
        plugins = self._load_plugins()
        reviews = self._load_reviews()

        plugin_reviews = [r for r in reviews if r.get("plugin_id") == plugin_id]
        if plugin_reviews:
            avg_rating = sum(r["rating"] for r in plugin_reviews) / len(plugin_reviews)

            for plugin in plugins:
                if plugin["id"] == plugin_id:
                    plugin["rating"] = round(avg_rating, 1)
                    plugin["reviews"] = [r for r in plugin_reviews]
                    break

        self._save_plugins(plugins)


# 플러그인 마켓플레이스 더미 구현


class DummyPluginMarketplace:
    def get_available_plugins(self):
        return []


plugin_marketplace = DummyPluginMarketplace()
