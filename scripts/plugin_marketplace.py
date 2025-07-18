#!/usr/bin/env python3
"""
플러그인 마켓플레이스 시스템
플러그인의 검색, 설치, 업데이트, 평가를 관리하는 중앙 집중식 마켓플레이스
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import sqlite3


@dataclass
class PluginPackage:
    """플러그인 패키지 정보"""

    id: str
    name: str
    version: str
    description: str
    author: str
    category: str
    tags: List[str]
    download_url: str
    homepage_url: Optional[str]
    license: str
    size: int
    downloads: int
    rating: float
    review_count: int
    dependencies: List[str]
    compatibility: Dict[str, str]
    release_date: str
    last_updated: str
    verified: bool
    featured: bool
    price: float = 0.0
    currency: str = "USD"


@dataclass
class PluginReview:
    """플러그인 리뷰"""

    id: str
    plugin_id: str
    user_id: str
    rating: int
    title: str
    content: str
    helpful_count: int
    created_date: str
    updated_date: str


class PluginMarketplace:
    """플러그인 마켓플레이스 관리 시스템"""

    def __init__(
        self,
        db_path: str = "plugin_marketplace.db",
        cache_dir: str = "cache/marketplace",
    ):
        self.db_path = db_path
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 데이터베이스 초기화
        self._init_database()

        # 기본 저장소 설정
        self.repositories = {
            "official": "https://plugins.your-program-system.com/api/v1",
            "community": "https://community-plugins.your-program-system.com/api/v1",
        }

    def _init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 플러그인 패키지 테이블
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS plugin_packages (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                description TEXT,
                author TEXT,
                category TEXT,
                tags TEXT,
                download_url TEXT,
                homepage_url TEXT,
                license TEXT,
                size INTEGER,
                downloads INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                review_count INTEGER DEFAULT 0,
                dependencies TEXT,
                compatibility TEXT,
                release_date TEXT,
                last_updated TEXT,
                verified BOOLEAN DEFAULT FALSE,
                featured BOOLEAN DEFAULT FALSE,
                price REAL DEFAULT 0.0,
                currency TEXT DEFAULT 'USD'
            )
        """
        )

        # 리뷰 테이블
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS plugin_reviews (
                id TEXT PRIMARY KEY,
                plugin_id TEXT,
                user_id TEXT,
                rating INTEGER,
                title TEXT,
                content TEXT,
                helpful_count INTEGER DEFAULT 0,
                created_date TEXT,
                updated_date TEXT,
                FOREIGN KEY (plugin_id) REFERENCES plugin_packages (id)
            )
        """
        )

        # 설치 히스토리 테이블
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS installation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_id TEXT,
                version TEXT,
                action TEXT,
                user_id TEXT,
                timestamp TEXT,
                success BOOLEAN,
                error_message TEXT
            )
        """
        )

        # 인덱스 생성
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_plugin_category ON plugin_packages(category)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_plugin_rating ON plugin_packages(rating)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_plugin_downloads ON plugin_packages(downloads)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_reviews_plugin ON plugin_reviews(plugin_id)"
        )

        conn.commit()
        conn.close()

    def sync_repositories(self) -> Dict[str, Any]:
        """저장소 동기화"""
        try:
            results = {}

            for repo_name, repo_url in self.repositories.items():
                print(f"🔄 {repo_name} 저장소 동기화 중...")

                try:
                    # 저장소 메타데이터 가져오기
                    response = requests.get(f"{repo_url}/plugins", timeout=30)
                    response.raise_for_status()

                    plugins_data = response.json()

                    # 플러그인 정보 저장
                    synced_count = 0
                    for plugin_data in plugins_data.get("plugins", []):
                        if self._save_plugin_package(plugin_data):
                            synced_count += 1

                    results[repo_name] = {
                        "success": True,
                        "synced_count": synced_count,
                        "total_count": len(plugins_data.get("plugins", [])),
                    }

                    print(f"✅ {repo_name}: {synced_count}개 플러그인 동기화 완료")

                except Exception as e:
                    results[repo_name] = {"success": False, "error": str(e)}
                    print(f"❌ {repo_name} 동기화 실패: {e}")

            return results

        except Exception as e:
            return {"error": f"저장소 동기화 중 오류: {e}"}

    def _save_plugin_package(self, plugin_data: Dict[str, Any]) -> bool:
        """플러그인 패키지 정보 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 기존 데이터 확인
            cursor.execute(
                "SELECT version FROM plugin_packages WHERE id = ?", (plugin_data["id"],)
            )
            existing = cursor.fetchone()

            if existing and existing[0] == plugin_data["version"]:
                # 버전이 같으면 업데이트만
                cursor.execute(
                    """
                    UPDATE plugin_packages SET
                        downloads = ?, rating = ?, review_count = ?, last_updated = ?
                    WHERE id = ?
                """,
                    (
                        plugin_data.get("downloads", 0),
                        plugin_data.get("rating", 0.0),
                        plugin_data.get("review_count", 0),
                        datetime.utcnow().isoformat(),
                        plugin_data["id"],
                    ),
                )
            else:
                # 새 플러그인이거나 새 버전이면 삽입/업데이트
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO plugin_packages (
                        id, name, version, description, author, category, tags,
                        download_url, homepage_url, license, size, downloads,
                        rating, review_count, dependencies, compatibility,
                        release_date, last_updated, verified, featured, price, currency
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        plugin_data["id"],
                        plugin_data["name"],
                        plugin_data["version"],
                        plugin_data.get("description", ""),
                        plugin_data.get("author", ""),
                        plugin_data.get("category", "general"),
                        json.dumps(plugin_data.get("tags", [])),
                        plugin_data.get("download_url", ""),
                        plugin_data.get("homepage_url"),
                        plugin_data.get("license", "MIT"),
                        plugin_data.get("size", 0),
                        plugin_data.get("downloads", 0),
                        plugin_data.get("rating", 0.0),
                        plugin_data.get("review_count", 0),
                        json.dumps(plugin_data.get("dependencies", [])),
                        json.dumps(plugin_data.get("compatibility", {})),
                        plugin_data.get("release_date", datetime.utcnow().isoformat()),
                        datetime.utcnow().isoformat(),
                        plugin_data.get("verified", False),
                        plugin_data.get("featured", False),
                        plugin_data.get("price", 0.0),
                        plugin_data.get("currency", "USD"),
                    ),
                )

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"플러그인 저장 중 오류: {e}")
            return False

    def search_plugins(
        self,
        query: str = "",
        category: str = "",
        tags: Optional[List[str]] = None,
        min_rating: float = 0.0,
        verified_only: bool = False,
        featured_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> List[PluginPackage]:
        """플러그인 검색"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 쿼리 구성
            where_conditions = []
            params = []

            if query:
                where_conditions.append(
                    """
                    (name LIKE ? OR description LIKE ? OR tags LIKE ?)
                """
                )
                search_term = f"%{query}%"
                params.extend([search_term, search_term, search_term])

            if category:
                where_conditions.append("category = ?")
                params.append(category)

            if tags:
                for tag in tags:
                    where_conditions.append("tags LIKE ?")
                    params.append(f"%{tag}%")

            if min_rating > 0:
                where_conditions.append("rating >= ?")
                params.append(min_rating)

            if verified_only:
                where_conditions.append("verified = TRUE")

            if featured_only:
                where_conditions.append("featured = TRUE")

            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

            # 쿼리 실행
            cursor.execute(
                f"""
                SELECT * FROM plugin_packages 
                WHERE {where_clause}
                ORDER BY downloads DESC, rating DESC
                LIMIT ? OFFSET ?
            """,
                params + [limit, offset],
            )

            plugins = []
            for row in cursor.fetchall():
                plugin = self._row_to_plugin_package(row)
                plugins.append(plugin)

            conn.close()
            return plugins

        except Exception as e:
            print(f"플러그인 검색 중 오류: {e}")
            return []

    def get_plugin_details(self, plugin_id: str) -> Optional[PluginPackage]:
        """플러그인 상세 정보 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM plugin_packages WHERE id = ?", (plugin_id,))
            row = cursor.fetchone()

            conn.close()

            if row:
                return self._row_to_plugin_package(row)
            return None

        except Exception as e:
            print(f"플러그인 상세 정보 조회 중 오류: {e}")
            return None

    def get_plugin_reviews(
        self, plugin_id: str, limit: int = 20, offset: int = 0
    ) -> List[PluginReview]:
        """플러그인 리뷰 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM plugin_reviews 
                WHERE plugin_id = ?
                ORDER BY helpful_count DESC, created_date DESC
                LIMIT ? OFFSET ?
            """,
                (plugin_id, limit, offset),
            )

            reviews = []
            for row in cursor.fetchall():
                review = self._row_to_plugin_review(row)
                reviews.append(review)

            conn.close()
            return reviews

        except Exception as e:
            print(f"리뷰 조회 중 오류: {e}")
            return []

    def add_review(
        self, plugin_id: str, user_id: str, rating: int, title: str, content: str
    ) -> bool:
        """리뷰 추가"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            review_id = (
                f"review_{plugin_id}_{user_id}_{int(datetime.utcnow().timestamp())}"
            )
            now = datetime.utcnow().isoformat()

            cursor.execute(
                """
                INSERT INTO plugin_reviews (
                    id, plugin_id, user_id, rating, title, content,
                    helpful_count, created_date, updated_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (review_id, plugin_id, user_id, rating, title, content, 0, now, now),
            )

            # 플러그인 평점 업데이트
            self._update_plugin_rating(plugin_id)

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"리뷰 추가 중 오류: {e}")
            return False

    def _update_plugin_rating(self, plugin_id: str):
        """플러그인 평점 업데이트"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 평균 평점 계산
            cursor.execute(
                """
                SELECT AVG(rating), COUNT(*) FROM plugin_reviews 
                WHERE plugin_id = ?
            """,
                (plugin_id,),
            )

            avg_rating, review_count = cursor.fetchone()

            if avg_rating:
                cursor.execute(
                    """
                    UPDATE plugin_packages 
                    SET rating = ?, review_count = ?
                    WHERE id = ?
                """,
                    (avg_rating, review_count, plugin_id),
                )

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"평점 업데이트 중 오류: {e}")

    def download_plugin(
        self, plugin_id: str, version: Optional[str] = None
    ) -> Dict[str, Any]:
        """플러그인 다운로드"""
        try:
            # 플러그인 정보 조회
            plugin = self.get_plugin_details(plugin_id)
            if not plugin:
                return {"error": "플러그인을 찾을 수 없습니다."}

            # 버전 확인
            if version and version != plugin.version:
                return {"error": f"요청한 버전 {version}이 존재하지 않습니다."}

            # 캐시 확인
            cache_file = self.cache_dir / f"{plugin_id}_{plugin.version}.zip"
            if cache_file.exists():
                return {
                    "success": True,
                    "cache_file": str(cache_file),
                    "plugin": asdict(plugin),
                }

            # 다운로드
            print(f"📥 {plugin_id} 플러그인 다운로드 중...")
            response = requests.get(plugin.download_url, stream=True, timeout=60)
            response.raise_for_status()

            # 파일 저장
            with open(cache_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # 다운로드 수 증가
            self._increment_download_count(plugin_id)

            return {
                "success": True,
                "cache_file": str(cache_file),
                "plugin": asdict(plugin),
            }

        except Exception as e:
            return {"error": f"다운로드 중 오류: {e}"}

    def _increment_download_count(self, plugin_id: str):
        """다운로드 수 증가"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE plugin_packages 
                SET downloads = downloads + 1
                WHERE id = ?
            """,
                (plugin_id,),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"다운로드 수 업데이트 중 오류: {e}")

    def get_categories(self) -> List[Dict[str, Any]]:
        """카테고리 목록 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT category, COUNT(*) as count, AVG(rating) as avg_rating
                FROM plugin_packages 
                GROUP BY category
                ORDER BY count DESC
            """
            )

            categories = []
            for row in cursor.fetchall():
                categories.append(
                    {"category": row[0], "count": row[1], "avg_rating": row[2] or 0.0}
                )

            conn.close()
            return categories

        except Exception as e:
            print(f"카테고리 조회 중 오류: {e}")
            return []

    def get_featured_plugins(self, limit: int = 10) -> List[PluginPackage]:
        """추천 플러그인 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM plugin_packages 
                WHERE featured = TRUE
                ORDER BY rating DESC, downloads DESC
                LIMIT ?
            """,
                (limit,),
            )

            plugins = []
            for row in cursor.fetchall():
                plugin = self._row_to_plugin_package(row)
                plugins.append(plugin)

            conn.close()
            return plugins

        except Exception as e:
            print(f"추천 플러그인 조회 중 오류: {e}")
            return []

    def get_trending_plugins(
        self, days: int = 7, limit: int = 10
    ) -> List[PluginPackage]:
        """트렌딩 플러그인 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 최근 설치 히스토리 기반으로 트렌딩 계산
            since_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

            cursor.execute(
                """
                SELECT p.*, COUNT(h.id) as recent_installs
                FROM plugin_packages p
                LEFT JOIN installation_history h ON p.id = h.plugin_id 
                    AND h.timestamp >= ? AND h.action = 'install'
                GROUP BY p.id
                ORDER BY recent_installs DESC, p.downloads DESC
                LIMIT ?
            """,
                (since_date, limit),
            )

            plugins = []
            for row in cursor.fetchall():
                plugin = self._row_to_plugin_package(row[:-1])  # recent_installs 제외
                plugins.append(plugin)

            conn.close()
            return plugins

        except Exception as e:
            print(f"트렌딩 플러그인 조회 중 오류: {e}")
            return []

    def _row_to_plugin_package(self, row) -> PluginPackage:
        """데이터베이스 행을 PluginPackage 객체로 변환"""
        return PluginPackage(
            id=row[0],
            name=row[1],
            version=row[2],
            description=row[3],
            author=row[4],
            category=row[5],
            tags=json.loads(row[6]) if row[6] else [],
            download_url=row[7],
            homepage_url=row[8],
            license=row[9],
            size=row[10],
            downloads=row[11],
            rating=row[12],
            review_count=row[13],
            dependencies=json.loads(row[14]) if row[14] else [],
            compatibility=json.loads(row[15]) if row[15] else {},
            release_date=row[16],
            last_updated=row[17],
            verified=bool(row[18]),
            featured=bool(row[19]),
            price=row[20],
            currency=row[21],
        )

    def _row_to_plugin_review(self, row) -> PluginReview:
        """데이터베이스 행을 PluginReview 객체로 변환"""
        return PluginReview(
            id=row[0],
            plugin_id=row[1],
            user_id=row[2],
            rating=row[3],
            title=row[4],
            content=row[5],
            helpful_count=row[6],
            created_date=row[7],
            updated_date=row[8],
        )

    def cleanup_cache(self, max_age_days: int = 30) -> int:
        """캐시 정리"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=max_age_days)
            deleted_count = 0

            for cache_file in self.cache_dir.glob("*.zip"):
                if cache_file.stat().st_mtime < cutoff_time.timestamp():
                    cache_file.unlink()
                    deleted_count += 1

            return deleted_count

        except Exception as e:
            print(f"캐시 정리 중 오류: {e}")
            return 0


def main():
    """메인 함수"""
    marketplace = PluginMarketplace()

    print("🛒 플러그인 마켓플레이스")
    print("=" * 50)

    while True:
        print("\n사용 가능한 기능:")
        print("1. 저장소 동기화")
        print("2. 플러그인 검색")
        print("3. 플러그인 상세 정보")
        print("4. 추천 플러그인")
        print("5. 트렌딩 플러그인")
        print("6. 카테고리 목록")
        print("7. 플러그인 다운로드")
        print("8. 리뷰 조회")
        print("9. 리뷰 작성")
        print("10. 캐시 정리")
        print("0. 종료")

        choice = input("\n선택 (0-10): ").strip()

        if choice == "0":
            break
        elif choice == "1":
            results = marketplace.sync_repositories()
            print(json.dumps(results, indent=2, ensure_ascii=False))
        elif choice == "2":
            query = input("검색어: ").strip()
            category = input("카테고리 (Enter로 전체): ").strip() or ""
            min_rating = input("최소 평점 (0.0-5.0): ").strip()
            min_rating = float(min_rating) if min_rating else 0.0

            plugins = marketplace.search_plugins(
                query=query, category=category, min_rating=min_rating
            )

            if plugins:
                print(f"\n검색 결과: {len(plugins)}개")
                for plugin in plugins[:10]:  # 상위 10개만 표시
                    print(f"  - {plugin.name} v{plugin.version} ({plugin.rating:.1f}★)")
            else:
                print("검색 결과가 없습니다.")
        elif choice == "3":
            plugin_id = input("플러그인 ID: ").strip()
            plugin = marketplace.get_plugin_details(plugin_id)
            if plugin:
                print(json.dumps(asdict(plugin), indent=2, ensure_ascii=False))
            else:
                print("플러그인을 찾을 수 없습니다.")
        elif choice == "4":
            plugins = marketplace.get_featured_plugins()
            if plugins:
                print(f"\n추천 플러그인: {len(plugins)}개")
                for plugin in plugins:
                    print(f"  - {plugin.name} v{plugin.version} ({plugin.rating:.1f}★)")
            else:
                print("추천 플러그인이 없습니다.")
        elif choice == "5":
            plugins = marketplace.get_trending_plugins()
            if plugins:
                print(f"\n트렌딩 플러그인: {len(plugins)}개")
                for plugin in plugins:
                    print(
                        f"  - {plugin.name} v{plugin.version} ({plugin.downloads} 다운로드)"
                    )
            else:
                print("트렌딩 플러그인이 없습니다.")
        elif choice == "6":
            categories = marketplace.get_categories()
            if categories:
                print(f"\n카테고리: {len(categories)}개")
                for cat in categories:
                    print(
                        f"  - {cat['category']}: {cat['count']}개 ({cat['avg_rating']:.1f}★)"
                    )
            else:
                print("카테고리가 없습니다.")
        elif choice == "7":
            plugin_id = input("플러그인 ID: ").strip()
            result = marketplace.download_plugin(plugin_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "8":
            plugin_id = input("플러그인 ID: ").strip()
            reviews = marketplace.get_plugin_reviews(plugin_id)
            if reviews:
                print(f"\n리뷰: {len(reviews)}개")
                for review in reviews[:5]:  # 상위 5개만 표시
                    print(f"  - {review.title} ({review.rating}★) - {review.user_id}")
            else:
                print("리뷰가 없습니다.")
        elif choice == "9":
            plugin_id = input("플러그인 ID: ").strip()
            user_id = input("사용자 ID: ").strip()
            rating = int(input("평점 (1-5): ").strip())
            title = input("제목: ").strip()
            content = input("내용: ").strip()

            success = marketplace.add_review(plugin_id, user_id, rating, title, content)
            if success:
                print("✅ 리뷰가 추가되었습니다.")
            else:
                print("❌ 리뷰 추가에 실패했습니다.")
        elif choice == "10":
            deleted_count = marketplace.cleanup_cache()
            print(f"✅ {deleted_count}개 캐시 파일이 정리되었습니다.")
        else:
            print("❌ 잘못된 선택입니다.")


if __name__ == "__main__":
    main()
