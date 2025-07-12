"""
고도화된 플러그인 마켓플레이스 시스템
- 검색/필터/정렬, 상세 정보, 설치/업데이트/삭제, 리뷰/평점, 통계/추천
"""

import logging
import json
import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class PluginInfo:
    """플러그인 상세 정보"""
    id: str
    name: str
    description: str
    version: str
    author: str
    category: str
    tags: List[str] = field(default_factory=list)
    price: float = 0.0
    download_count: int = 0
    rating: float = 0.0
    review_count: int = 0
    size: int = 0
    dependencies: List[str] = field(default_factory=list)
    compatibility: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "active"  # active, deprecated, beta
    license: str = "MIT"
    homepage: str = ""
    repository: str = ""

@dataclass
class PluginReview:
    """플러그인 리뷰"""
    id: int
    plugin_id: str
    user_id: str
    rating: int  # 1-5
    title: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    helpful_count: int = 0
    reported: bool = False

@dataclass
class DownloadStats:
    """다운로드 통계"""
    plugin_id: str
    total_downloads: int = 0
    daily_downloads: int = 0
    weekly_downloads: int = 0
    monthly_downloads: int = 0
    last_download: datetime = field(default_factory=datetime.utcnow)

class EnhancedMarketplace:
    """고도화된 플러그인 마켓플레이스"""
    
    def __init__(self, db_path: str = "marketplace.db", plugins_dir: str = "marketplace/plugins"):
        self.db_path = db_path
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # 샘플 플러그인 데이터
        self.sample_plugins = [
            PluginInfo(
                id="restaurant_management",
                name="레스토랑 관리 시스템",
                description="레스토랑의 주문, 재고, 직원 관리를 위한 종합 플러그인",
                version="2.1.0",
                author="PluginDev Team",
                category="business",
                tags=["restaurant", "order", "inventory", "staff"],
                price=0.0,
                download_count=1250,
                rating=4.5,
                review_count=89,
                size=2048576,
                dependencies=["core_management"],
                compatibility=["v2.0+", "v3.0+"],
                license="MIT",
                homepage="https://example.com/restaurant-plugin"
            ),
            PluginInfo(
                id="analytics_dashboard",
                name="고급 분석 대시보드",
                description="실시간 데이터 분석 및 시각화를 위한 고급 대시보드",
                version="1.8.2",
                author="Analytics Pro",
                category="analytics",
                tags=["dashboard", "analytics", "visualization", "reports"],
                price=29.99,
                download_count=890,
                rating=4.8,
                review_count=156,
                size=5120000,
                dependencies=["core_management"],
                compatibility=["v2.5+", "v3.0+"],
                license="Commercial",
                homepage="https://example.com/analytics-dashboard"
            ),
            PluginInfo(
                id="security_monitor",
                name="보안 모니터링 시스템",
                description="시스템 보안 상태를 실시간으로 모니터링하고 알림",
                version="1.5.1",
                author="Security Labs",
                category="security",
                tags=["security", "monitoring", "alerts", "compliance"],
                price=0.0,
                download_count=2100,
                rating=4.3,
                review_count=234,
                size=1536000,
                dependencies=["core_management"],
                compatibility=["v2.0+", "v3.0+"],
                license="GPL",
                homepage="https://example.com/security-monitor"
            ),
            PluginInfo(
                id="mobile_app_sync",
                name="모바일 앱 동기화",
                description="모바일 앱과 웹 시스템 간의 실시간 데이터 동기화",
                version="2.0.0",
                author="MobileSync Inc",
                category="integration",
                tags=["mobile", "sync", "api", "real-time"],
                price=49.99,
                download_count=567,
                rating=4.6,
                review_count=78,
                size=3072000,
                dependencies=["core_management", "api_gateway"],
                compatibility=["v3.0+"],
                license="Commercial",
                homepage="https://example.com/mobile-sync"
            ),
            PluginInfo(
                id="ai_chatbot",
                name="AI 챗봇 시스템",
                description="인공지능 기반 고객 지원 챗봇 시스템",
                version="1.2.0",
                author="AI Solutions",
                category="ai",
                tags=["ai", "chatbot", "customer-support", "nlp"],
                price=99.99,
                download_count=345,
                rating=4.7,
                review_count=45,
                size=8192000,
                dependencies=["core_management", "nlp_engine"],
                compatibility=["v3.0+"],
                license="Commercial",
                homepage="https://example.com/ai-chatbot"
            )
        ]
        
        self._init_database()
        self._load_sample_data()
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 플러그인 정보 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plugins (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    version TEXT NOT NULL,
                    author TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tags TEXT,
                    price REAL DEFAULT 0.0,
                    download_count INTEGER DEFAULT 0,
                    rating REAL DEFAULT 0.0,
                    review_count INTEGER DEFAULT 0,
                    size INTEGER DEFAULT 0,
                    dependencies TEXT,
                    compatibility TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    license TEXT DEFAULT 'MIT',
                    homepage TEXT,
                    repository TEXT
                )
            ''')
            
            # 리뷰 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    helpful_count INTEGER DEFAULT 0,
                    reported BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (plugin_id) REFERENCES plugins (id)
                )
            ''')
            
            # 다운로드 통계 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS download_stats (
                    plugin_id TEXT PRIMARY KEY,
                    total_downloads INTEGER DEFAULT 0,
                    daily_downloads INTEGER DEFAULT 0,
                    weekly_downloads INTEGER DEFAULT 0,
                    monthly_downloads INTEGER DEFAULT 0,
                    last_download DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plugin_id) REFERENCES plugins (id)
                )
            ''')
            
            # 다운로드 이력 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS download_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    user_id TEXT,
                    downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    version TEXT,
                    FOREIGN KEY (plugin_id) REFERENCES plugins (id)
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_plugins_category ON plugins(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_plugins_rating ON plugins(rating)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_plugins_downloads ON plugins(download_count)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reviews_plugin ON reviews(plugin_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_downloads_plugin ON download_history(plugin_id)')
            
            conn.commit()
            conn.close()
            logger.info("마켓플레이스 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
    
    def _load_sample_data(self):
        """샘플 데이터 로드"""
        try:
            for plugin in self.sample_plugins:
                self.add_plugin(plugin)
            logger.info("샘플 플러그인 데이터 로드 완료")
        except Exception as e:
            logger.error(f"샘플 데이터 로드 오류: {e}")
    
    def add_plugin(self, plugin: PluginInfo) -> bool:
        """플러그인 추가"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO plugins 
                (id, name, description, version, author, category, tags, price, 
                 download_count, rating, review_count, size, dependencies, 
                 compatibility, created_at, updated_at, status, license, homepage, repository)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                plugin.id, plugin.name, plugin.description, plugin.version, plugin.author,
                plugin.category, json.dumps(plugin.tags), plugin.price, plugin.download_count,
                plugin.rating, plugin.review_count, plugin.size, json.dumps(plugin.dependencies),
                json.dumps(plugin.compatibility), plugin.created_at.isoformat(),
                plugin.updated_at.isoformat(), plugin.status, plugin.license,
                plugin.homepage, plugin.repository
            ))
            
            # 다운로드 통계 초기화
            cursor.execute('''
                INSERT OR REPLACE INTO download_stats 
                (plugin_id, total_downloads, daily_downloads, weekly_downloads, monthly_downloads, last_download)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                plugin.id, plugin.download_count, 0, 0, 0, datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"플러그인 추가 오류: {e}")
            return False
    
    def get_plugins(self, category: str = None, search: str = None, 
                   sort_by: str = "name", sort_order: str = "asc",
                   limit: int = 50, offset: int = 0) -> List[PluginInfo]:
        """플러그인 목록 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 쿼리 조건 구성
            conditions = []
            params = []
            
            if category:
                conditions.append("category = ?")
                params.append(category)
            
            if search:
                conditions.append("(name LIKE ? OR description LIKE ? OR tags LIKE ?)")
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # 정렬 조건
            valid_sort_fields = ["name", "rating", "download_count", "created_at", "price"]
            if sort_by not in valid_sort_fields:
                sort_by = "name"
            
            sort_direction = "DESC" if sort_order.lower() == "desc" else "ASC"
            
            query = f'''
                SELECT id, name, description, version, author, category, tags, price,
                       download_count, rating, review_count, size, dependencies,
                       compatibility, created_at, updated_at, status, license, homepage, repository
                FROM plugins
                WHERE {where_clause}
                ORDER BY {sort_by} {sort_direction}
                LIMIT ? OFFSET ?
            '''
            
            cursor.execute(query, params + [limit, offset])
            rows = cursor.fetchall()
            
            plugins = []
            for row in rows:
                plugin = PluginInfo(
                    id=row[0], name=row[1], description=row[2], version=row[3],
                    author=row[4], category=row[5], tags=json.loads(row[6]) if row[6] else [],
                    price=row[7], download_count=row[8], rating=row[9], review_count=row[10],
                    size=row[11], dependencies=json.loads(row[12]) if row[12] else [],
                    compatibility=json.loads(row[13]) if row[13] else [],
                    created_at=datetime.fromisoformat(row[14]),
                    updated_at=datetime.fromisoformat(row[15]),
                    status=row[16], license=row[17], homepage=row[18], repository=row[19]
                )
                plugins.append(plugin)
            
            conn.close()
            return plugins
            
        except Exception as e:
            logger.error(f"플러그인 목록 조회 오류: {e}")
            return []
    
    def get_plugin(self, plugin_id: str) -> Optional[PluginInfo]:
        """플러그인 상세 정보 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, description, version, author, category, tags, price,
                       download_count, rating, review_count, size, dependencies,
                       compatibility, created_at, updated_at, status, license, homepage, repository
                FROM plugins WHERE id = ?
            ''', (plugin_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            plugin = PluginInfo(
                id=row[0], name=row[1], description=row[2], version=row[3],
                author=row[4], category=row[5], tags=json.loads(row[6]) if row[6] else [],
                price=row[7], download_count=row[8], rating=row[9], review_count=row[10],
                size=row[11], dependencies=json.loads(row[12]) if row[12] else [],
                compatibility=json.loads(row[13]) if row[13] else [],
                created_at=datetime.fromisoformat(row[14]),
                updated_at=datetime.fromisoformat(row[15]),
                status=row[16], license=row[17], homepage=row[18], repository=row[19]
            )
            
            conn.close()
            return plugin
            
        except Exception as e:
            logger.error(f"플러그인 상세 조회 오류: {e}")
            return None
    
    def add_review(self, plugin_id: str, user_id: str, rating: int, 
                   title: str, content: str) -> bool:
        """리뷰 추가"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 리뷰 추가
            cursor.execute('''
                INSERT INTO reviews (plugin_id, user_id, rating, title, content)
                VALUES (?, ?, ?, ?, ?)
            ''', (plugin_id, user_id, rating, title, content))
            
            # 플러그인 평점 업데이트
            cursor.execute('''
                UPDATE plugins 
                SET rating = (
                    SELECT AVG(rating) FROM reviews WHERE plugin_id = ?
                ),
                review_count = (
                    SELECT COUNT(*) FROM reviews WHERE plugin_id = ?
                )
                WHERE id = ?
            ''', (plugin_id, plugin_id, plugin_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"리뷰 추가 오류: {e}")
            return False
    
    def get_reviews(self, plugin_id: str, limit: int = 20, offset: int = 0) -> List[PluginReview]:
        """리뷰 목록 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, plugin_id, user_id, rating, title, content, 
                       created_at, helpful_count, reported
                FROM reviews 
                WHERE plugin_id = ? AND reported = FALSE
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (plugin_id, limit, offset))
            
            rows = cursor.fetchall()
            reviews = []
            for row in rows:
                review = PluginReview(
                    id=row[0], plugin_id=row[1], user_id=row[2], rating=row[3],
                    title=row[4], content=row[5], created_at=datetime.fromisoformat(row[6]),
                    helpful_count=row[7], reported=row[8]
                )
                reviews.append(review)
            
            conn.close()
            return reviews
            
        except Exception as e:
            logger.error(f"리뷰 목록 조회 오류: {e}")
            return []
    
    def download_plugin(self, plugin_id: str, user_id: str = None, version: str = None) -> bool:
        """플러그인 다운로드"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 다운로드 이력 추가
            cursor.execute('''
                INSERT INTO download_history (plugin_id, user_id, version)
                VALUES (?, ?, ?)
            ''', (plugin_id, user_id, version))
            
            # 다운로드 통계 업데이트
            cursor.execute('''
                UPDATE download_stats 
                SET total_downloads = total_downloads + 1,
                    daily_downloads = daily_downloads + 1,
                    last_download = CURRENT_TIMESTAMP
                WHERE plugin_id = ?
            ''', (plugin_id,))
            
            # 플러그인 다운로드 수 업데이트
            cursor.execute('''
                UPDATE plugins 
                SET download_count = download_count + 1
                WHERE id = ?
            ''', (plugin_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"플러그인 다운로드 오류: {e}")
            return False
    
    def get_download_stats(self, plugin_id: str) -> Optional[DownloadStats]:
        """다운로드 통계 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT plugin_id, total_downloads, daily_downloads, 
                       weekly_downloads, monthly_downloads, last_download
                FROM download_stats WHERE plugin_id = ?
            ''', (plugin_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            stats = DownloadStats(
                plugin_id=row[0], total_downloads=row[1], daily_downloads=row[2],
                weekly_downloads=row[3], monthly_downloads=row[4],
                last_download=datetime.fromisoformat(row[5])
            )
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"다운로드 통계 조회 오류: {e}")
            return None
    
    def get_categories(self) -> List[str]:
        """카테고리 목록 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT DISTINCT category FROM plugins ORDER BY category')
            categories = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return categories
            
        except Exception as e:
            logger.error(f"카테고리 목록 조회 오류: {e}")
            return []
    
    def get_popular_plugins(self, limit: int = 10) -> List[PluginInfo]:
        """인기 플러그인 조회"""
        return self.get_plugins(sort_by="download_count", sort_order="desc", limit=limit)
    
    def get_recommended_plugins(self, user_id: str = None, limit: int = 10) -> List[PluginInfo]:
        """추천 플러그인 조회 (간단한 구현)"""
        # 실제로는 사용자 기반 협업 필터링이나 콘텐츠 기반 필터링 사용
        return self.get_plugins(sort_by="rating", sort_order="desc", limit=limit)

# 전역 인스턴스
enhanced_marketplace = EnhancedMarketplace() 