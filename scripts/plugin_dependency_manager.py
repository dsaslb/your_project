#!/usr/bin/env python3
"""
플러그인 의존성 관리 시스템
플러그인 간 의존성 해결, 호환성 검사, 자동 설치
"""

import json
import sqlite3
import logging
import subprocess
import sys
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import pkg_resources
import networkx as nx

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PluginDependency:
    """플러그인 의존성 정보"""
    plugin_id: str
    dependency_id: str
    version_constraint: str  # 예: ">=1.0.0,<2.0.0"
    dependency_type: str     # "required", "optional", "conflicts"
    description: str = ""
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class DependencyResolution:
    """의존성 해결 결과"""
    success: bool
    resolved_dependencies: List[str]
    conflicts: List[str]
    missing_dependencies: List[str]
    install_order: List[str]
    message: str

@dataclass
class CompatibilityMatrix:
    """호환성 매트릭스"""
    plugin_id: str
    compatible_versions: List[str]
    incompatible_versions: List[str]
    tested_versions: List[str]
    last_updated: Optional[datetime] = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()

class PluginDependencyManager:
    """플러그인 의존성 관리 클래스"""
    
    def __init__(self, db_path: str = "plugin_dependencies.db"):
        self.db_path = db_path
        self.dependency_graph = nx.DiGraph()
        self._init_database()
        
    def _init_database(self):
        """의존성 데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 플러그인 의존성 테이블
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS plugin_dependencies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT NOT NULL,
                        dependency_id TEXT NOT NULL,
                        version_constraint TEXT NOT NULL,
                        dependency_type TEXT NOT NULL DEFAULT 'required',
                        description TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(plugin_id, dependency_id)
                    )
                """)
                
                # 호환성 매트릭스 테이블
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS compatibility_matrix (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT NOT NULL,
                        compatible_versions TEXT,
                        incompatible_versions TEXT,
                        tested_versions TEXT,
                        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 플러그인 메타데이터 테이블
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS plugin_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        version TEXT NOT NULL,
                        description TEXT,
                        author TEXT,
                        dependencies TEXT,
                        requirements TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 설치된 플러그인 테이블
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS installed_plugins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT UNIQUE NOT NULL,
                        version TEXT NOT NULL,
                        install_path TEXT NOT NULL,
                        install_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'active',
                        dependencies_installed BOOLEAN DEFAULT FALSE
                    )
                """)
                
                # 인덱스 생성
                conn.execute("CREATE INDEX IF NOT EXISTS idx_dependencies_plugin_id ON plugin_dependencies(plugin_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_dependencies_dependency_id ON plugin_dependencies(dependency_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_installed_plugins_plugin_id ON installed_plugins(plugin_id)")
                
                conn.commit()
                logger.info("의존성 관리 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def register_plugin(self, plugin_id: str, name: str, version: str, 
                       dependencies: List[Dict] = [], requirements: List[str] = [],
                       description: str = "", author: str = ""):
        """플러그인 등록"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 플러그인 메타데이터 저장
                conn.execute("""
                    INSERT OR REPLACE INTO plugin_metadata 
                    (plugin_id, name, version, description, author, dependencies, requirements, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    plugin_id,
                    name,
                    version,
                    description,
                    author,
                    json.dumps(dependencies),
                    json.dumps(requirements),
                    datetime.utcnow()
                ))
                
                # 의존성 정보 저장
                for dep in dependencies:
                    conn.execute("""
                        INSERT OR REPLACE INTO plugin_dependencies 
                        (plugin_id, dependency_id, version_constraint, dependency_type, description)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        plugin_id,
                        dep.get('id') or "",
                        dep.get('version', '>=0.0.0'),
                        dep.get('type', 'required'),
                        dep.get('description', '')
                    ))
                
                # 의존성 그래프 업데이트
                self._update_dependency_graph(plugin_id, dependencies)
                
                conn.commit()
                logger.info(f"플러그인 등록 완료: {plugin_id} v{version}")
                
        except Exception as e:
            logger.error(f"플러그인 등록 실패: {e}")
            raise
    
    def _update_dependency_graph(self, plugin_id: str, dependencies: List[Dict]):
        """의존성 그래프 업데이트"""
        # 기존 엣지 제거
        if plugin_id in self.dependency_graph:
            self.dependency_graph.remove_node(plugin_id)
        
        # 새 노드 추가
        self.dependency_graph.add_node(plugin_id)
        
        # 의존성 엣지 추가
        for dep in dependencies:
            dep_id = dep.get('id') or ""
            if dep_id:
                self.dependency_graph.add_edge(plugin_id, dep_id, **dep)
    
    def resolve_dependencies(self, plugin_id: str, target_version: Optional[str] = None) -> DependencyResolution:
        """플러그인 의존성 해결"""
        try:
            # 플러그인 정보 조회
            plugin_info = self.get_plugin_info(plugin_id)
            if not plugin_info:
                return DependencyResolution(
                    success=False,
                    resolved_dependencies=[],
                    conflicts=[],
                    missing_dependencies=[],
                    install_order=[],
                    message=f"플러그인을 찾을 수 없습니다: {plugin_id}"
                )
            
            # 의존성 목록 조회
            dependencies = self.get_plugin_dependencies(plugin_id)
            
            resolved_deps = []
            conflicts = []
            missing_deps = []
            
            # 각 의존성 검사
            for dep in dependencies or []:
                dep_id = dep['dependency_id']
                version_constraint = dep['version_constraint']
                
                # 의존성 플러그인 정보 조회
                dep_info = self.get_plugin_info(dep_id)
                if not dep_info:
                    missing_deps.append(dep_id)
                    continue
                
                # 버전 호환성 검사
                if not self._check_version_compatibility(dep_info['version'], version_constraint):
                    conflicts.append(f"{dep_id}: 요구 버전 {version_constraint}, 사용 가능 버전 {dep_info['version']}")
                    continue
                
                resolved_deps.append(dep_id)
            
            # 순환 의존성 검사
            if self._has_circular_dependency(plugin_id):
                conflicts.append("순환 의존성이 감지되었습니다")
            
            # 설치 순서 계산
            install_order = self._calculate_install_order(plugin_id)
            
            success = len(missing_deps) == 0 and len(conflicts) == 0
            
            return DependencyResolution(
                success=success,
                resolved_dependencies=resolved_deps,
                conflicts=conflicts,
                missing_dependencies=missing_deps,
                install_order=install_order,
                message="의존성 해결 완료" if success else "의존성 해결 실패"
            )
            
        except Exception as e:
            logger.error(f"의존성 해결 실패: {e}")
            return DependencyResolution(
                success=False,
                resolved_dependencies=[],
                conflicts=[str(e)],
                missing_dependencies=[],
                install_order=[],
                message=f"의존성 해결 중 오류 발생: {e}"
            )
    
    def _check_version_compatibility(self, available_version: str, constraint: str) -> bool:
        """버전 호환성 검사"""
        try:
            from packaging.specifiers import SpecifierSet
            from packaging.version import Version
            
            spec = SpecifierSet(constraint)
            version = Version(available_version)
            return version in spec
            
        except Exception as e:
            logger.error(f"버전 호환성 검사 실패: {e}")
            return False
    
    def _has_circular_dependency(self, plugin_id: str) -> bool:
        """순환 의존성 검사"""
        try:
            return not nx.is_directed_acyclic_graph(self.dependency_graph)
        except Exception:
            return True
    
    def _calculate_install_order(self, plugin_id: str) -> List[str]:
        """설치 순서 계산 (위상 정렬)"""
        try:
            if plugin_id not in self.dependency_graph:
                return [plugin_id]
            
            # 플러그인과 그 의존성들을 포함하는 서브그래프 생성
            subgraph = nx.descendants(self.dependency_graph, plugin_id)
            subgraph.add(plugin_id)
            
            subgraph_nx = nx.DiGraph(self.dependency_graph.subgraph(subgraph))
            
            # 위상 정렬 수행
            try:
                order = [str(x) for x in nx.topological_sort(subgraph_nx)]
                return order
            except nx.NetworkXError:
                # 순환 의존성이 있는 경우
                return [plugin_id]
                
        except Exception as e:
            logger.error(f"설치 순서 계산 실패: {e}")
            return [plugin_id]
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict]:
        """플러그인 정보 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT plugin_id, name, version, description, author, dependencies, requirements
                    FROM plugin_metadata WHERE plugin_id = ?
                """, (plugin_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'plugin_id': row[0],
                        'name': row[1],
                        'version': row[2],
                        'description': row[3],
                        'author': row[4],
                        'dependencies': json.loads(row[5]) if row[5] else [],
                        'requirements': json.loads(row[6]) if row[6] else []
                    }
                return None
                
        except Exception as e:
            logger.error(f"플러그인 정보 조회 실패: {e}")
            return None
    
    def get_plugin_dependencies(self, plugin_id: str) -> List[Dict]:
        """플러그인 의존성 목록 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT dependency_id, version_constraint, dependency_type, description
                    FROM plugin_dependencies WHERE plugin_id = ?
                """, (plugin_id,))
                
                dependencies = []
                for row in cursor.fetchall():
                    dependencies.append({
                        'dependency_id': row[0],
                        'version_constraint': row[1],
                        'dependency_type': row[2],
                        'description': row[3]
                    })
                return dependencies
                
        except Exception as e:
            logger.error(f"의존성 목록 조회 실패: {e}")
            return []
    
    def install_plugin_dependencies(self, plugin_id: str) -> bool:
        """플러그인 의존성 자동 설치"""
        try:
            # 의존성 해결
            resolution = self.resolve_dependencies(plugin_id)
            if not resolution.success:
                logger.error(f"의존성 해결 실패: {resolution.message}")
                return False
            
            # Python 패키지 의존성 설치
            plugin_info = self.get_plugin_info(plugin_id)
            if plugin_info and plugin_info.get('requirements'):
                for requirement in plugin_info['requirements']:
                    if not self._install_python_package(requirement):
                        logger.error(f"Python 패키지 설치 실패: {requirement}")
                        return False
            
            # 플러그인 의존성 설치
            for dep_id in resolution.install_order:
                if dep_id != plugin_id:
                    if not self._install_plugin_dependency(dep_id):
                        logger.error(f"플러그인 의존성 설치 실패: {dep_id}")
                        return False
            
            # 설치 완료 표시
            self._mark_dependencies_installed(plugin_id)
            
            logger.info(f"플러그인 의존성 설치 완료: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"의존성 설치 실패: {e}")
            return False
    
    def _install_python_package(self, requirement: str) -> bool:
        """Python 패키지 설치"""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', requirement
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"Python 패키지 설치 완료: {requirement}")
                return True
            else:
                logger.error(f"Python 패키지 설치 실패: {requirement} - {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Python 패키지 설치 오류: {e}")
            return False
    
    def _install_plugin_dependency(self, plugin_id: str) -> bool:
        """플러그인 의존성 설치"""
        try:
            # 이미 설치되어 있는지 확인
            if self._is_plugin_installed(plugin_id):
                logger.info(f"플러그인 이미 설치됨: {plugin_id}")
                return True
            
            # 플러그인 다운로드 및 설치 로직
            # (실제 구현에서는 플러그인 마켓플레이스에서 다운로드)
            logger.info(f"플러그인 의존성 설치: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 의존성 설치 오류: {e}")
            return False
    
    def _is_plugin_installed(self, plugin_id: str) -> bool:
        """플러그인 설치 여부 확인"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM installed_plugins WHERE plugin_id = ? AND status = 'active'
                """, (plugin_id,))
                return cursor.fetchone()[0] > 0
        except Exception:
            return False
    
    def _mark_dependencies_installed(self, plugin_id: str):
        """의존성 설치 완료 표시"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE installed_plugins 
                    SET dependencies_installed = TRUE 
                    WHERE plugin_id = ?
                """, (plugin_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"의존성 설치 완료 표시 실패: {e}")
    
    def check_compatibility(self, plugin_id: str, target_version: str) -> Dict[str, Any]:
        """호환성 검사"""
        try:
            plugin_info = self.get_plugin_info(plugin_id)
            if not plugin_info:
                return {
                    'compatible': False,
                    'message': '플러그인을 찾을 수 없습니다',
                    'issues': []
                }
            
            issues = []
            
            # 버전 호환성 검사
            current_version = plugin_info['version']
            if not self._check_version_compatibility(current_version, f">={target_version}"):
                issues.append(f"버전 호환성 문제: 현재 {current_version}, 요구 {target_version}")
            
            # 의존성 호환성 검사
            dependencies = self.get_plugin_dependencies(plugin_id)
            for dep in dependencies:
                dep_info = self.get_plugin_info(dep['dependency_id'])
                if dep_info:
                    if not self._check_version_compatibility(dep_info['version'], dep['version_constraint']):
                        issues.append(f"의존성 호환성 문제: {dep['dependency_id']}")
            
            # 시스템 요구사항 검사
            if plugin_info.get('requirements'):
                for requirement in plugin_info['requirements']:
                    if not self._check_system_requirement(requirement):
                        issues.append(f"시스템 요구사항 미충족: {requirement}")
            
            return {
                'compatible': len(issues) == 0,
                'message': '호환성 검사 완료',
                'issues': issues,
                'plugin_info': plugin_info
            }
            
        except Exception as e:
            logger.error(f"호환성 검사 실패: {e}")
            return {
                'compatible': False,
                'message': f'호환성 검사 오류: {e}',
                'issues': [str(e)]
            }
    
    def _check_system_requirement(self, requirement: str) -> bool:
        """시스템 요구사항 검사"""
        try:
            # Python 패키지 요구사항 검사
            if '==' in requirement or '>=' in requirement or '<=' in requirement:
                try:
                    pkg_resources.require(requirement)
                    return True
                except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
                    return False
            
            # 기타 시스템 요구사항 검사
            return True
            
        except Exception:
            return False
    
    def get_dependency_tree(self, plugin_id: str) -> Dict[str, Any]:
        """의존성 트리 조회"""
        try:
            def build_tree(node_id: str, visited: set = set()) -> Dict[str, Any]:
                if node_id in visited:
                    return {'id': node_id, 'circular': True}
                
                visited.add(node_id)
                
                node_info = self.get_plugin_info(node_id)
                dependencies = self.get_plugin_dependencies(node_id)
                
                tree = {
                    'id': node_id,
                    'name': node_info['name'] if node_info else node_id,
                    'version': node_info['version'] if node_info else 'unknown',
                    'dependencies': []
                }
                
                for dep in dependencies:
                    dep_tree = build_tree(dep['dependency_id'], visited.copy())
                    tree['dependencies'].append({
                        'dependency': dep_tree,
                        'constraint': dep['version_constraint'],
                        'type': dep['dependency_type']
                    })
                
                return tree
            
            return build_tree(plugin_id)
            
        except Exception as e:
            logger.error(f"의존성 트리 조회 실패: {e}")
            return {'error': str(e)}
    
    def export_dependency_report(self, output_path: str, plugin_ids: List[str] = []):
        """의존성 보고서 내보내기"""
        try:
            report = {
                'generated_at': datetime.utcnow().isoformat(),
                'plugins': []
            }
            
            if plugin_ids is None:
                # 모든 플러그인 조회
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("SELECT plugin_id FROM plugin_metadata")
                    plugin_ids = [row[0] for row in cursor.fetchall()]
            
            for plugin_id in plugin_ids:
                plugin_info = self.get_plugin_info(plugin_id)
                if plugin_info:
                    resolution = self.resolve_dependencies(plugin_id)
                    dependency_tree = self.get_dependency_tree(plugin_id)
                    
                    report['plugins'].append({
                        'plugin_info': plugin_info,
                        'dependency_resolution': asdict(resolution),
                        'dependency_tree': dependency_tree
                    })
            
            # JSON 파일로 저장
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"의존성 보고서 내보내기 완료: {output_path}")
            
        except Exception as e:
            logger.error(f"의존성 보고서 내보내기 실패: {e}")

def main():
    """메인 함수"""
    try:
        # 의존성 관리자 초기화
        manager = PluginDependencyManager()
        
        # 샘플 플러그인 등록
        sample_plugins = [
            {
                'id': 'analytics_core',
                'name': 'Analytics Core',
                'version': '1.2.0',
                'dependencies': [],
                'requirements': ['pandas>=1.3.0', 'numpy>=1.20.0']
            },
            {
                'id': 'reporting_engine',
                'name': 'Reporting Engine',
                'version': '2.1.0',
                'dependencies': [
                    {'id': 'analytics_core', 'version': '>=1.0.0', 'type': 'required'}
                ],
                'requirements': ['matplotlib>=3.5.0', 'seaborn>=0.11.0']
            },
            {
                'id': 'dashboard_widget',
                'name': 'Dashboard Widget',
                'version': '1.0.0',
                'dependencies': [
                    {'id': 'analytics_core', 'version': '>=1.0.0', 'type': 'required'},
                    {'id': 'reporting_engine', 'version': '>=2.0.0', 'type': 'required'}
                ],
                'requirements': ['plotly>=5.0.0']
            }
        ]
        
        # 플러그인 등록
        for plugin in sample_plugins:
            manager.register_plugin(
                plugin_id=plugin['id'],
                name=plugin['name'],
                version=plugin['version'],
                dependencies=plugin['dependencies'],
                requirements=plugin['requirements']
            )
        
        # 의존성 해결 테스트
        resolution = manager.resolve_dependencies('dashboard_widget')
        print(f"의존성 해결 결과: {resolution.success}")
        print(f"설치 순서: {resolution.install_order}")
        
        # 의존성 트리 조회
        tree = manager.get_dependency_tree('dashboard_widget')
        print(f"의존성 트리: {json.dumps(tree, indent=2, default=str)}")
        
        # 호환성 검사
        compatibility = manager.check_compatibility('dashboard_widget', '1.0.0')
        print(f"호환성 검사: {compatibility['compatible']}")
        
        # 보고서 내보내기
        manager.export_dependency_report('dependency_report.json')
        
        logger.info("의존성 관리 시스템 테스트 완료")
        
    except Exception as e:
        logger.error(f"의존성 관리 시스템 오류: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 