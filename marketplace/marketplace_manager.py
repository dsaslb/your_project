"""
플러그인 마켓플레이스 관리자 - 고도화 버전
"""

import os
import json
import requests
import hashlib
import zipfile
import shutil
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class PluginCategory(Enum):
    """플러그인 카테고리"""
    MANAGEMENT = "management"
    ANALYTICS = "analytics"
    INTEGRATION = "integration"
    SECURITY = "security"
    UTILITY = "utility"
    CUSTOM = "custom"

class PluginRating(Enum):
    """플러그인 평점"""
    ONE_STAR = 1
    TWO_STARS = 2
    THREE_STARS = 3
    FOUR_STARS = 4
    FIVE_STARS = 5

@dataclass
class PluginMetadata:
    """플러그인 메타데이터"""
    name: str
    version: str
    description: str
    author: str
    category: str
    tags: List[str]
    permissions: List[str]
    dependencies: List[str]
    min_system_version: str
    max_system_version: str
    download_url: str
    homepage_url: str
    documentation_url: str
    license: str
    price: float = 0.0
    rating: float = 0.0
    download_count: int = 0
    review_count: int = 0
    created_at: str = None
    updated_at: str = None
    featured: bool = False
    verified: bool = False

@dataclass
class PluginReview:
    """플러그인 리뷰"""
    id: str
    plugin_name: str
    user_id: str
    user_name: str
    rating: int
    title: str
    comment: str
    created_at: str
    helpful_count: int = 0

class MarketplaceManager:
    """마켓플레이스 관리자"""
    
    def __init__(self, marketplace_dir: str = "marketplace"):
        self.marketplace_dir = marketplace_dir
        self.plugins_dir = os.path.join(marketplace_dir, "plugins")
        self.downloads_dir = os.path.join(marketplace_dir, "downloads")
        self.reviews_dir = os.path.join(marketplace_dir, "reviews")
        self.categories_file = os.path.join(marketplace_dir, "categories.json")
        self.featured_file = os.path.join(marketplace_dir, "featured.json")
        
        self.ensure_directories()
        self.load_categories()
    
    def ensure_directories(self):
        """필요한 디렉토리 생성"""
        directories = [self.marketplace_dir, self.plugins_dir, self.downloads_dir, self.reviews_dir]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def load_categories(self):
        """카테고리 정보 로드"""
        if os.path.exists(self.categories_file):
            try:
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    self.categories = json.load(f)
            except Exception as e:
                logger.error(f"카테고리 로드 실패: {e}")
                self.categories = {}
        else:
            self.categories = {
                "management": {
                    "name": "관리",
                    "description": "시스템 관리 및 운영 플러그인",
                    "icon": "settings"
                },
                "analytics": {
                    "name": "분석",
                    "description": "데이터 분석 및 리포팅 플러그인",
                    "icon": "chart"
                },
                "integration": {
                    "name": "연동",
                    "description": "외부 시스템 연동 플러그인",
                    "icon": "link"
                },
                "security": {
                    "name": "보안",
                    "description": "보안 및 인증 플러그인",
                    "icon": "shield"
                },
                "utility": {
                    "name": "유틸리티",
                    "description": "편의 기능 플러그인",
                    "icon": "tool"
                },
                "custom": {
                    "name": "커스텀",
                    "description": "사용자 정의 플러그인",
                    "icon": "code"
                }
            }
            self.save_categories()
    
    def save_categories(self):
        """카테고리 정보 저장"""
        try:
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(self.categories, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"카테고리 저장 실패: {e}")
    
    def get_plugin_metadata(self, plugin_name: str) -> Optional[PluginMetadata]:
        """플러그인 메타데이터 조회"""
        metadata_file = os.path.join(self.plugins_dir, f"{plugin_name}.json")
        
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return PluginMetadata(**data)
            except Exception as e:
                logger.error(f"플러그인 메타데이터 로드 실패 {plugin_name}: {e}")
        
        return None
    
    def save_plugin_metadata(self, metadata: PluginMetadata):
        """플러그인 메타데이터 저장"""
        try:
            metadata_file = os.path.join(self.plugins_dir, f"{metadata.name}.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(metadata), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"플러그인 메타데이터 저장 실패 {metadata.name}: {e}")
    
    def get_all_plugins(self, category: str = None, featured: bool = None, verified: bool = None) -> List[PluginMetadata]:
        """모든 플러그인 조회"""
        plugins = []
        
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith('.json'):
                plugin_name = filename[:-5]  # .json 제거
                metadata = self.get_plugin_metadata(plugin_name)
                
                if metadata:
                    # 필터링
                    if category and metadata.category != category:
                        continue
                    if featured is not None and metadata.featured != featured:
                        continue
                    if verified is not None and metadata.verified != verified:
                        continue
                    
                    plugins.append(metadata)
        
        return plugins
    
    def search_plugins(self, query: str, category: str = None) -> List[PluginMetadata]:
        """플러그인 검색"""
        plugins = self.get_all_plugins(category=category)
        results = []
        
        query_lower = query.lower()
        
        for plugin in plugins:
            # 이름, 설명, 태그에서 검색
            if (query_lower in plugin.name.lower() or
                query_lower in plugin.description.lower() or
                any(query_lower in tag.lower() for tag in plugin.tags)):
                results.append(plugin)
        
        return results
    
    def download_plugin(self, plugin_name: str, download_url: str) -> bool:
        """플러그인 다운로드"""
        try:
            # 다운로드 디렉토리 생성
            plugin_download_dir = os.path.join(self.downloads_dir, plugin_name)
            os.makedirs(plugin_download_dir, exist_ok=True)
            
            # 파일 다운로드
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # 파일 저장
            zip_path = os.path.join(plugin_download_dir, f"{plugin_name}.zip")
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 압축 해제
            extract_path = os.path.join(plugin_download_dir, "extracted")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # 다운로드 카운트 업데이트
            metadata = self.get_plugin_metadata(plugin_name)
            if metadata:
                metadata.download_count += 1
                metadata.updated_at = datetime.now().isoformat()
                self.save_plugin_metadata(metadata)
            
            logger.info(f"플러그인 다운로드 성공: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 다운로드 실패 {plugin_name}: {e}")
            return False
    
    def install_plugin_from_marketplace(self, plugin_name: str, target_dir: str = "plugins") -> bool:
        """마켓플레이스에서 플러그인 설치"""
        try:
            # 다운로드된 플러그인 경로
            download_path = os.path.join(self.downloads_dir, plugin_name, "extracted")
            
            if not os.path.exists(download_path):
                logger.error(f"다운로드된 플러그인을 찾을 수 없습니다: {plugin_name}")
                return False
            
            # 설치 대상 디렉토리
            install_path = os.path.join(target_dir, plugin_name)
            
            # 기존 플러그인 백업
            if os.path.exists(install_path):
                backup_path = f"{install_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.move(install_path, backup_path)
            
            # 플러그인 복사
            shutil.copytree(download_path, install_path)
            
            logger.info(f"플러그인 설치 성공: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 설치 실패 {plugin_name}: {e}")
            return False
    
    def add_plugin_review(self, plugin_name: str, user_id: str, user_name: str, 
                         rating: int, title: str, comment: str) -> bool:
        """플러그인 리뷰 추가"""
        try:
            review = PluginReview(
                id=f"{plugin_name}_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                plugin_name=plugin_name,
                user_id=user_id,
                user_name=user_name,
                rating=rating,
                title=title,
                comment=comment,
                created_at=datetime.now().isoformat()
            )
            
            # 리뷰 파일 저장
            review_file = os.path.join(self.reviews_dir, f"{review.id}.json")
            with open(review_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(review), f, indent=2, ensure_ascii=False)
            
            # 플러그인 평점 업데이트
            self.update_plugin_rating(plugin_name)
            
            logger.info(f"플러그인 리뷰 추가 성공: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 리뷰 추가 실패 {plugin_name}: {e}")
            return False
    
    def get_plugin_reviews(self, plugin_name: str) -> List[PluginReview]:
        """플러그인 리뷰 조회"""
        reviews = []
        
        for filename in os.listdir(self.reviews_dir):
            if filename.startswith(f"{plugin_name}_") and filename.endswith('.json'):
                try:
                    review_file = os.path.join(self.reviews_dir, filename)
                    with open(review_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        reviews.append(PluginReview(**data))
                except Exception as e:
                    logger.error(f"리뷰 로드 실패 {filename}: {e}")
        
        # 생성일 기준 정렬
        reviews.sort(key=lambda x: x.created_at, reverse=True)
        return reviews
    
    def update_plugin_rating(self, plugin_name: str):
        """플러그인 평점 업데이트"""
        try:
            reviews = self.get_plugin_reviews(plugin_name)
            
            if reviews:
                total_rating = sum(review.rating for review in reviews)
                average_rating = total_rating / len(reviews)
                
                metadata = self.get_plugin_metadata(plugin_name)
                if metadata:
                    metadata.rating = round(average_rating, 1)
                    metadata.review_count = len(reviews)
                    metadata.updated_at = datetime.now().isoformat()
                    self.save_plugin_metadata(metadata)
            
        except Exception as e:
            logger.error(f"플러그인 평점 업데이트 실패 {plugin_name}: {e}")
    
    def mark_plugin_featured(self, plugin_name: str, featured: bool = True):
        """플러그인 추천 설정"""
        try:
            metadata = self.get_plugin_metadata(plugin_name)
            if metadata:
                metadata.featured = featured
                metadata.updated_at = datetime.now().isoformat()
                self.save_plugin_metadata(metadata)
                
                # 추천 플러그인 목록 업데이트
                self.update_featured_plugins()
                
                logger.info(f"플러그인 추천 설정 성공: {plugin_name} -> {featured}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"플러그인 추천 설정 실패 {plugin_name}: {e}")
            return False
    
    def update_featured_plugins(self):
        """추천 플러그인 목록 업데이트"""
        try:
            featured_plugins = []
            plugins = self.get_all_plugins(featured=True)
            
            for plugin in plugins:
                featured_plugins.append({
                    "name": plugin.name,
                    "description": plugin.description,
                    "rating": plugin.rating,
                    "download_count": plugin.download_count
                })
            
            with open(self.featured_file, 'w', encoding='utf-8') as f:
                json.dump(featured_plugins, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"추천 플러그인 목록 업데이트 실패: {e}")
    
    def get_featured_plugins(self) -> List[Dict[str, Any]]:
        """추천 플러그인 목록 조회"""
        try:
            if os.path.exists(self.featured_file):
                with open(self.featured_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.update_featured_plugins()
                return self.get_featured_plugins()
        except Exception as e:
            logger.error(f"추천 플러그인 목록 조회 실패: {e}")
            return []
    
    def get_popular_plugins(self, limit: int = 10) -> List[PluginMetadata]:
        """인기 플러그인 조회"""
        plugins = self.get_all_plugins()
        
        # 다운로드 수 기준 정렬
        plugins.sort(key=lambda x: x.download_count, reverse=True)
        
        return plugins[:limit]
    
    def get_recent_plugins(self, limit: int = 10) -> List[PluginMetadata]:
        """최신 플러그인 조회"""
        plugins = self.get_all_plugins()
        
        # 생성일 기준 정렬
        plugins.sort(key=lambda x: x.created_at, reverse=True)
        
        return plugins[:limit]
    
    def get_plugin_statistics(self) -> Dict[str, Any]:
        """플러그인 통계 조회"""
        try:
            plugins = self.get_all_plugins()
            
            # 카테고리별 통계
            category_stats = {}
            for plugin in plugins:
                category = plugin.category
                if category not in category_stats:
                    category_stats[category] = {
                        "count": 0,
                        "total_downloads": 0,
                        "avg_rating": 0.0
                    }
                
                category_stats[category]["count"] += 1
                category_stats[category]["total_downloads"] += plugin.download_count
            
            # 평균 평점 계산
            for category in category_stats:
                category_plugins = [p for p in plugins if p.category == category]
                if category_plugins:
                    avg_rating = sum(p.rating for p in category_plugins) / len(category_plugins)
                    category_stats[category]["avg_rating"] = round(avg_rating, 1)
            
            # 전체 통계
            total_plugins = len(plugins)
            total_downloads = sum(p.download_count for p in plugins)
            total_reviews = sum(p.review_count for p in plugins)
            avg_rating = sum(p.rating for p in plugins) / total_plugins if total_plugins > 0 else 0
            
            return {
                "total_plugins": total_plugins,
                "total_downloads": total_downloads,
                "total_reviews": total_reviews,
                "average_rating": round(avg_rating, 1),
                "category_stats": category_stats,
                "featured_plugins": len([p for p in plugins if p.featured]),
                "verified_plugins": len([p for p in plugins if p.verified])
            }
            
        except Exception as e:
            logger.error(f"플러그인 통계 조회 실패: {e}")
            return {}
    
    def validate_plugin(self, plugin_path: str) -> Dict[str, Any]:
        """플러그인 유효성 검사"""
        validation_result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "metadata": None
        }
        
        try:
            # 필수 파일 확인
            required_files = ["__init__.py", "config.json"]
            for file in required_files:
                file_path = os.path.join(plugin_path, file)
                if not os.path.exists(file_path):
                    validation_result["errors"].append(f"필수 파일이 없습니다: {file}")
            
            # config.json 파싱
            config_file = os.path.join(plugin_path, "config.json")
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    # 필수 필드 확인
                    required_fields = ["name", "version", "description", "author"]
                    for field in required_fields:
                        if field not in config_data:
                            validation_result["errors"].append(f"필수 필드가 없습니다: {field}")
                    
                    validation_result["metadata"] = config_data
                    
                except json.JSONDecodeError:
                    validation_result["errors"].append("config.json 파일이 유효하지 않습니다.")
            
            # Python 파일 문법 검사
            init_file = os.path.join(plugin_path, "__init__.py")
            if os.path.exists(init_file):
                try:
                    with open(init_file, 'r', encoding='utf-8') as f:
                        compile(f.read(), init_file, 'exec')
                except SyntaxError as e:
                    validation_result["errors"].append(f"Python 문법 오류: {e}")
            
            # 유효성 판정
            validation_result["valid"] = len(validation_result["errors"]) == 0
            
            return validation_result
            
        except Exception as e:
            validation_result["errors"].append(f"검증 중 오류 발생: {e}")
            return validation_result

# 전역 마켓플레이스 관리자 인스턴스
marketplace_manager = MarketplaceManager() 