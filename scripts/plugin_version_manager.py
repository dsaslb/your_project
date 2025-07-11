#!/usr/bin/env python3
"""
플러그인 버전 관리 시스템
플러그인의 버전 관리, 업데이트, 롤백, 호환성 검사를 담당하는 시스템
"""

import os
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import sqlite3
import semver
import requests


@dataclass
class PluginVersion:
    """플러그인 버전 정보"""
    plugin_id: str
    version: str
    release_date: str
    changelog: str
    download_url: str
    file_size: int
    checksum: str
    dependencies: List[str]
    compatibility: Dict[str, str]
    breaking_changes: List[str]
    security_fixes: List[str]
    performance_improvements: List[str]
    verified: bool
    download_count: int = 0


@dataclass
class VersionCompatibility:
    """버전 호환성 정보"""
    plugin_id: str
    current_version: str
    target_version: str
    compatible: bool
    breaking_changes: List[str]
    migration_steps: List[str]
    estimated_migration_time: str
    risk_level: str  # low, medium, high, critical


class PluginVersionManager:
    """플러그인 버전 관리 시스템"""
    
    def __init__(self, db_path: str = "plugin_versions.db", 
                 plugins_dir: str = "plugins",
                 backup_dir: str = "backups/plugins"):
        self.db_path = db_path
        self.plugins_dir = Path(plugins_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 데이터베이스 초기화
        self._init_database()
    
    def _init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 플러그인 버전 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plugin_versions (
                plugin_id TEXT,
                version TEXT,
                release_date TEXT,
                changelog TEXT,
                download_url TEXT,
                file_size INTEGER,
                checksum TEXT,
                dependencies TEXT,
                compatibility TEXT,
                breaking_changes TEXT,
                security_fixes TEXT,
                performance_improvements TEXT,
                verified BOOLEAN DEFAULT FALSE,
                download_count INTEGER DEFAULT 0,
                PRIMARY KEY (plugin_id, version)
            )
        ''')
        
        # 설치 히스토리 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS installation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_id TEXT,
                from_version TEXT,
                to_version TEXT,
                action TEXT,
                user_id TEXT,
                timestamp TEXT,
                success BOOLEAN,
                error_message TEXT,
                backup_path TEXT
            )
        ''')
        
        # 호환성 매트릭스 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compatibility_matrix (
                plugin_id TEXT,
                from_version TEXT,
                to_version TEXT,
                compatible BOOLEAN,
                breaking_changes TEXT,
                migration_steps TEXT,
                estimated_time TEXT,
                risk_level TEXT,
                PRIMARY KEY (plugin_id, from_version, to_version)
            )
        ''')
        
        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plugin_versions ON plugin_versions(plugin_id, version)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_installation_history ON installation_history(plugin_id, timestamp)')
        
        conn.commit()
        conn.close()
    
    def add_version(self, plugin_id: str, version_info: Dict[str, Any]) -> bool:
        """새 버전 추가"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO plugin_versions (
                    plugin_id, version, release_date, changelog, download_url,
                    file_size, checksum, dependencies, compatibility,
                    breaking_changes, security_fixes, performance_improvements,
                    verified, download_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                plugin_id,
                version_info["version"],
                version_info.get("release_date", datetime.utcnow().isoformat()),
                version_info.get("changelog", ""),
                version_info.get("download_url", ""),
                version_info.get("file_size", 0),
                version_info.get("checksum", ""),
                json.dumps(version_info.get("dependencies", [])),
                json.dumps(version_info.get("compatibility", {})),
                json.dumps(version_info.get("breaking_changes", [])),
                json.dumps(version_info.get("security_fixes", [])),
                json.dumps(version_info.get("performance_improvements", [])),
                version_info.get("verified", False),
                version_info.get("download_count", 0)
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"버전 추가 중 오류: {e}")
            return False
    
    def get_versions(self, plugin_id: str) -> List[PluginVersion]:
        """플러그인 버전 목록 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM plugin_versions 
                WHERE plugin_id = ?
                ORDER BY version DESC
            ''', (plugin_id,))
            
            versions = []
            for row in cursor.fetchall():
                version = self._row_to_plugin_version(row)
                versions.append(version)
            
            conn.close()
            return versions
            
        except Exception as e:
            print(f"버전 목록 조회 중 오류: {e}")
            return []
    
    def get_latest_version(self, plugin_id: str) -> Optional[PluginVersion]:
        """최신 버전 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM plugin_versions 
                WHERE plugin_id = ?
                ORDER BY version DESC
                LIMIT 1
            ''', (plugin_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_plugin_version(row)
            return None
            
        except Exception as e:
            print(f"최신 버전 조회 중 오류: {e}")
            return None
    
    def get_current_version(self, plugin_id: str) -> Optional[str]:
        """현재 설치된 버전 조회"""
        try:
            plugin_path = self.plugins_dir / plugin_id
            if not plugin_path.exists():
                return None
            
            # plugin.json에서 버전 정보 읽기
            plugin_config_path = plugin_path / "plugin.json"
            if plugin_config_path.exists():
                with open(plugin_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("version")
            
            return None
            
        except Exception as e:
            print(f"현재 버전 조회 중 오류: {e}")
            return None
    
    def check_for_updates(self, plugin_id: str) -> List[PluginVersion]:
        """업데이트 확인"""
        try:
            current_version = self.get_current_version(plugin_id)
            if not current_version:
                return []
            
            # 사용 가능한 버전들 조회
            available_versions = self.get_versions(plugin_id)
            
            # 현재 버전보다 높은 버전들 필터링
            updates = []
            for version in available_versions:
                if semver.compare(version.version, current_version) > 0:
                    updates.append(version)
            
            return updates
            
        except Exception as e:
            print(f"업데이트 확인 중 오류: {e}")
            return []
    
    def update_plugin(self, plugin_id: str, target_version: str, 
                     user_id: str = "system") -> Dict[str, Any]:
        """플러그인 업데이트"""
        try:
            current_version = self.get_current_version(plugin_id)
            if not current_version:
                return {"error": "현재 설치된 버전을 찾을 수 없습니다."}
            
            # 호환성 검사
            compatibility = self.check_compatibility(plugin_id, current_version, target_version)
            if not compatibility.compatible:
                return {
                    "error": "호환되지 않는 버전입니다.",
                    "compatibility": asdict(compatibility)
                }
            
            # 백업 생성
            backup_path = self._create_backup(plugin_id, current_version)
            if not backup_path:
                return {"error": "백업 생성에 실패했습니다."}
            
            # 업데이트 실행
            try:
                # 새 버전 다운로드
                version_info = self._get_version_info(plugin_id, target_version)
                if not version_info:
                    return {"error": "버전 정보를 찾을 수 없습니다."}
                
                # 플러그인 디렉토리 백업
                plugin_path = self.plugins_dir / plugin_id
                temp_backup = plugin_path.with_suffix('.backup')
                shutil.move(str(plugin_path), str(temp_backup))
                
                # 새 버전 설치
                success = self._install_version(plugin_id, target_version, version_info)
                
                if success:
                    # 설치 히스토리 기록
                    self._record_installation(plugin_id, current_version, target_version, 
                                           "update", user_id, True, "", backup_path)
                    
                    # 임시 백업 정리
                    shutil.rmtree(temp_backup, ignore_errors=True)
                    
                    return {
                        "success": True,
                        "from_version": current_version,
                        "to_version": target_version,
                        "backup_path": backup_path
                    }
                else:
                    # 실패 시 롤백
                    shutil.rmtree(plugin_path, ignore_errors=True)
                    shutil.move(str(temp_backup), str(plugin_path))
                    
                    self._record_installation(plugin_id, current_version, target_version,
                                           "update", user_id, False, "설치 실패", backup_path)
                    
                    return {"error": "업데이트에 실패했습니다."}
                
            except Exception as e:
                # 오류 발생 시 롤백
                plugin_path = self.plugins_dir / plugin_id
                temp_backup = plugin_path.with_suffix('.backup')
                if temp_backup.exists():
                    shutil.rmtree(plugin_path, ignore_errors=True)
                    shutil.move(str(temp_backup), str(plugin_path))
                
                self._record_installation(plugin_id, current_version, target_version,
                                       "update", user_id, False, str(e), backup_path)
                
                return {"error": f"업데이트 중 오류: {e}"}
            
        except Exception as e:
            return {"error": f"업데이트 중 오류: {e}"}
    
    def rollback_plugin(self, plugin_id: str, target_version: str,
                       user_id: str = "system") -> Dict[str, Any]:
        """플러그인 롤백"""
        try:
            current_version = self.get_current_version(plugin_id)
            if not current_version:
                return {"error": "현재 설치된 버전을 찾을 수 없습니다."}
            
            # 백업에서 복원
            backup_path = self._find_backup(plugin_id, target_version)
            if not backup_path:
                return {"error": "해당 버전의 백업을 찾을 수 없습니다."}
            
            # 현재 플러그인 백업
            current_backup = self._create_backup(plugin_id, current_version)
            
            # 롤백 실행
            try:
                plugin_path = self.plugins_dir / plugin_id
                shutil.rmtree(plugin_path, ignore_errors=True)
                shutil.copytree(backup_path, plugin_path)
                
                # 설치 히스토리 기록
                self._record_installation(plugin_id, current_version, target_version,
                                       "rollback", user_id, True, "", current_backup)
                
                return {
                    "success": True,
                    "from_version": current_version,
                    "to_version": target_version,
                    "backup_path": current_backup
                }
                
            except Exception as e:
                self._record_installation(plugin_id, current_version, target_version,
                                       "rollback", user_id, False, str(e), current_backup)
                return {"error": f"롤백 중 오류: {e}"}
            
        except Exception as e:
            return {"error": f"롤백 중 오류: {e}"}
    
    def check_compatibility(self, plugin_id: str, from_version: str, 
                           to_version: str) -> VersionCompatibility:
        """버전 호환성 검사"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 캐시된 호환성 정보 확인
            cursor.execute('''
                SELECT * FROM compatibility_matrix 
                WHERE plugin_id = ? AND from_version = ? AND to_version = ?
            ''', (plugin_id, from_version, to_version))
            
            row = cursor.fetchone()
            if row:
                conn.close()
                return self._row_to_compatibility(row)
            
            # 새로 계산
            from_info = self._get_version_info(plugin_id, from_version)
            to_info = self._get_version_info(plugin_id, to_version)
            
            if not from_info or not to_info:
                conn.close()
                return VersionCompatibility(
                    plugin_id=plugin_id,
                    current_version=from_version,
                    target_version=to_version,
                    compatible=False,
                    breaking_changes=["버전 정보를 찾을 수 없습니다."],
                    migration_steps=[],
                    estimated_migration_time="알 수 없음",
                    risk_level="high"
                )
            
            # 호환성 분석
            compatible = True
            breaking_changes = []
            migration_steps = []
            risk_level = "low"
            
            # 의존성 변경 확인
            from_deps = set(from_info.get("dependencies", []))
            to_deps = set(to_info.get("dependencies", []))
            
            removed_deps = from_deps - to_deps
            added_deps = to_deps - from_deps
            
            if removed_deps:
                breaking_changes.append(f"제거된 의존성: {', '.join(removed_deps)}")
                compatible = False
                risk_level = "medium"
            
            if added_deps:
                migration_steps.append(f"새 의존성 설치: {', '.join(added_deps)}")
            
            # 호환성 정보 저장
            cursor.execute('''
                INSERT OR REPLACE INTO compatibility_matrix (
                    plugin_id, from_version, to_version, compatible,
                    breaking_changes, migration_steps, estimated_time, risk_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                plugin_id, from_version, to_version, compatible,
                json.dumps(breaking_changes),
                json.dumps(migration_steps),
                "5-10분",
                risk_level
            ))
            
            conn.commit()
            conn.close()
            
            return VersionCompatibility(
                plugin_id=plugin_id,
                current_version=from_version,
                target_version=to_version,
                compatible=compatible,
                breaking_changes=breaking_changes,
                migration_steps=migration_steps,
                estimated_migration_time="5-10분",
                risk_level=risk_level
            )
            
        except Exception as e:
            print(f"호환성 검사 중 오류: {e}")
            return VersionCompatibility(
                plugin_id=plugin_id,
                current_version=from_version,
                target_version=to_version,
                compatible=False,
                breaking_changes=[f"호환성 검사 오류: {e}"],
                migration_steps=[],
                estimated_migration_time="알 수 없음",
                risk_level="high"
            )
    
    def _create_backup(self, plugin_id: str, version: str) -> Optional[str]:
        """백업 생성"""
        try:
            plugin_path = self.plugins_dir / plugin_id
            if not plugin_path.exists():
                return None
            
            backup_name = f"{plugin_id}_{version}_{int(datetime.utcnow().timestamp())}"
            backup_path = self.backup_dir / backup_name
            
            shutil.copytree(plugin_path, backup_path)
            return str(backup_path)
            
        except Exception as e:
            print(f"백업 생성 중 오류: {e}")
            return None
    
    def _find_backup(self, plugin_id: str, version: str) -> Optional[str]:
        """백업 찾기"""
        try:
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.name.startswith(f"{plugin_id}_{version}_"):
                    return str(backup_dir)
            return None
            
        except Exception as e:
            print(f"백업 찾기 중 오류: {e}")
            return None
    
    def _get_version_info(self, plugin_id: str, version: str) -> Optional[Dict[str, Any]]:
        """버전 정보 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM plugin_versions 
                WHERE plugin_id = ? AND version = ?
            ''', (plugin_id, version))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_dict(row)
            return None
            
        except Exception as e:
            print(f"버전 정보 조회 중 오류: {e}")
            return None
    
    def _install_version(self, plugin_id: str, version: str, 
                        version_info: Dict[str, Any]) -> bool:
        """버전 설치"""
        try:
            # 다운로드 URL에서 플러그인 다운로드
            if not version_info.get("download_url"):
                return False
            
            response = requests.get(version_info["download_url"], stream=True)
            response.raise_for_status()
            
            # 임시 파일에 저장
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                temp_file = f.name
            
            # 압축 해제
            plugin_path = self.plugins_dir / plugin_id
            with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                zip_ref.extractall(plugin_path)
            
            # 임시 파일 삭제
            os.unlink(temp_file)
            
            return True
            
        except Exception as e:
            print(f"버전 설치 중 오류: {e}")
            return False
    
    def _record_installation(self, plugin_id: str, from_version: str, to_version: str,
                           action: str, user_id: str, success: bool, 
                           error_message: str, backup_path: Optional[str]):
        """설치 히스토리 기록"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO installation_history (
                    plugin_id, from_version, to_version, action, user_id,
                    timestamp, success, error_message, backup_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                plugin_id, from_version, to_version, action, user_id,
                datetime.utcnow().isoformat(), success, error_message, backup_path
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"설치 히스토리 기록 중 오류: {e}")
    
    def _row_to_plugin_version(self, row) -> PluginVersion:
        """데이터베이스 행을 PluginVersion 객체로 변환"""
        return PluginVersion(
            plugin_id=row[0],
            version=row[1],
            release_date=row[2],
            changelog=row[3],
            download_url=row[4],
            file_size=row[5],
            checksum=row[6],
            dependencies=json.loads(row[7]) if row[7] else [],
            compatibility=json.loads(row[8]) if row[8] else {},
            breaking_changes=json.loads(row[9]) if row[9] else [],
            security_fixes=json.loads(row[10]) if row[10] else [],
            performance_improvements=json.loads(row[11]) if row[11] else [],
            verified=bool(row[12]),
            download_count=row[13]
        )
    
    def _row_to_compatibility(self, row) -> VersionCompatibility:
        """데이터베이스 행을 VersionCompatibility 객체로 변환"""
        return VersionCompatibility(
            plugin_id=row[0],
            current_version=row[1],
            target_version=row[2],
            compatible=bool(row[3]),
            breaking_changes=json.loads(row[4]) if row[4] else [],
            migration_steps=json.loads(row[5]) if row[5] else [],
            estimated_migration_time=row[6],
            risk_level=row[7]
        )
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """데이터베이스 행을 딕셔너리로 변환"""
        return {
            "plugin_id": row[0],
            "version": row[1],
            "release_date": row[2],
            "changelog": row[3],
            "download_url": row[4],
            "file_size": row[5],
            "checksum": row[6],
            "dependencies": json.loads(row[7]) if row[7] else [],
            "compatibility": json.loads(row[8]) if row[8] else {},
            "breaking_changes": json.loads(row[9]) if row[9] else [],
            "security_fixes": json.loads(row[10]) if row[10] else [],
            "performance_improvements": json.loads(row[11]) if row[11] else [],
            "verified": bool(row[12]),
            "download_count": row[13]
        }


def main():
    """메인 함수"""
    version_manager = PluginVersionManager()
    
    print("🔄 플러그인 버전 관리")
    print("=" * 50)
    
    while True:
        print("\n사용 가능한 기능:")
        print("1. 버전 목록 조회")
        print("2. 업데이트 확인")
        print("3. 플러그인 업데이트")
        print("4. 플러그인 롤백")
        print("5. 호환성 검사")
        print("6. 설치 히스토리")
        print("0. 종료")
        
        choice = input("\n선택 (0-6): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            plugin_id = input("플러그인 ID: ").strip()
            versions = version_manager.get_versions(plugin_id)
            if versions:
                print(f"\n{plugin_id} 버전 목록:")
                for version in versions:
                    print(f"  - v{version.version} ({version.release_date})")
            else:
                print("버전 정보가 없습니다.")
        elif choice == "2":
            plugin_id = input("플러그인 ID: ").strip()
            updates = version_manager.check_for_updates(plugin_id)
            if updates:
                print(f"\n{plugin_id} 업데이트 가능:")
                for update in updates:
                    print(f"  - v{update.version} ({update.release_date})")
            else:
                print("업데이트가 없습니다.")
        elif choice == "3":
            plugin_id = input("플러그인 ID: ").strip()
            target_version = input("대상 버전: ").strip()
            result = version_manager.update_plugin(plugin_id, target_version)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "4":
            plugin_id = input("플러그인 ID: ").strip()
            target_version = input("롤백 버전: ").strip()
            result = version_manager.rollback_plugin(plugin_id, target_version)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "5":
            plugin_id = input("플러그인 ID: ").strip()
            from_version = input("현재 버전: ").strip()
            to_version = input("대상 버전: ").strip()
            compatibility = version_manager.check_compatibility(plugin_id, from_version, to_version)
            print(json.dumps(asdict(compatibility), indent=2, ensure_ascii=False))
        elif choice == "6":
            plugin_id = input("플러그인 ID (Enter로 전체): ").strip() or None
            # 설치 히스토리 조회 로직 구현 필요
            print("설치 히스토리 조회 기능은 추후 구현 예정입니다.")
        else:
            print("❌ 잘못된 선택입니다.")


if __name__ == "__main__":
    main() 