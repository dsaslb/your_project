#!/usr/bin/env python3
"""
플러그인 호환성 검사 도구
버전 호환성, 의존성 충돌, 시스템 요구사항 종합 검사
"""

import json
import sqlite3
import logging
import os
import platform
import pkg_resources
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from packaging import version, specifiers

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CompatibilityIssue:
    """호환성 문제 정보"""
    issue_type: str  # 'version_conflict', 'dependency_missing', 'system_requirement', 'circular_dependency'
    severity: str    # 'low', 'medium', 'high', 'critical'
    plugin_id: str
    message: str
    details: Dict[str, Any]
    suggested_fix: str = ""
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class CompatibilityReport:
    """호환성 검사 보고서"""
    plugin_id: str
    plugin_name: str
    plugin_version: str
    compatible: bool
    issues: List[CompatibilityIssue]
    dependencies_checked: List[str]
    system_requirements_checked: List[str]
    recommendations: List[str]
    generated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.utcnow()

@dataclass
class SystemInfo:
    """시스템 정보"""
    platform: str
    python_version: str
    architecture: str
    installed_packages: Dict[str, str]
    available_memory: int
    cpu_count: int
    disk_space: Dict[str, int]

class PluginCompatibilityChecker:
    """플러그인 호환성 검사 클래스"""
    
    def __init__(self, db_path: str = "plugin_compatibility.db"):
        self.db_path = db_path
        self.system_info = self._get_system_info()
        self._init_database()
        
    def _init_database(self):
        """호환성 데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 호환성 검사 결과 테이블
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS compatibility_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT NOT NULL,
                        plugin_version TEXT NOT NULL,
                        compatible BOOLEAN NOT NULL,
                        issues TEXT,
                        system_info TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 호환성 매트릭스 테이블
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS compatibility_matrix (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT NOT NULL,
                        target_plugin_id TEXT NOT NULL,
                        compatible BOOLEAN NOT NULL,
                        tested_versions TEXT,
                        notes TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(plugin_id, target_plugin_id)
                    )
                """)
                
                # 시스템 요구사항 테이블
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS system_requirements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT NOT NULL,
                        requirement_type TEXT NOT NULL,
                        requirement_value TEXT NOT NULL,
                        description TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 인덱스 생성
                conn.execute("CREATE INDEX IF NOT EXISTS idx_compatibility_plugin_id ON compatibility_results(plugin_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_matrix_plugin_id ON compatibility_matrix(plugin_id)")
                
                conn.commit()
                logger.info("호환성 검사 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def _get_system_info(self) -> SystemInfo:
        """시스템 정보 수집"""
        try:
            # 설치된 Python 패키지 정보
            installed_packages = {}
            for dist in pkg_resources.working_set or []:
                installed_packages[dist.project_name] = dist.version
            
            # 메모리 정보
            try:
                import psutil
                available_memory = psutil.virtual_memory().available
            except ImportError:
                available_memory = 0
            
            # 디스크 공간 정보
            disk_space = {}
            try:
                for partition in psutil.disk_partitions():
                    if partition.device:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disk_space[partition.mountpoint] = usage.free
            except Exception:
                pass
            
            return SystemInfo(
                platform=platform.platform(),
                python_version=platform.python_version(),
                architecture=platform.architecture()[0],
                installed_packages=installed_packages,
                available_memory=available_memory,
                cpu_count=os.cpu_count() or 1, # psutil.cpu_count() 추가
                disk_space=disk_space
            )
            
        except Exception as e:
            logger.error(f"시스템 정보 수집 실패: {e}")
            return SystemInfo(
                platform="unknown",
                python_version="unknown",
                architecture="unknown",
                installed_packages={},
                available_memory=0,
                cpu_count=1,
                disk_space={}
            )
    
    def check_plugin_compatibility(self, plugin_id: str, plugin_version: Optional[str] = None) -> CompatibilityReport:
        """플러그인 호환성 종합 검사"""
        try:
            # 플러그인 정보 조회
            plugin_info = self._get_plugin_info(plugin_id)
            if not plugin_info:
                return CompatibilityReport(
                    plugin_id=plugin_id,
                    plugin_name="Unknown",
                    plugin_version=plugin_version or "unknown",
                    compatible=False,
                    issues=[CompatibilityIssue(
                        issue_type="plugin_not_found",
                        severity="critical",
                        plugin_id=plugin_id,
                        message="플러그인을 찾을 수 없습니다",
                        details={},
                        suggested_fix="플러그인이 올바르게 등록되었는지 확인하세요"
                    )],
                    dependencies_checked=[],
                    system_requirements_checked=[],
                    recommendations=["플러그인을 먼저 등록하세요"]
                )
            
            plugin_version = plugin_version or plugin_info.get('version') or "unknown"
            
            issues = []
            dependencies_checked = []
            system_requirements_checked = []
            recommendations = []
            
            # 1. 버전 호환성 검사
            version_issues = self._check_version_compatibility(plugin_id, plugin_version)
            issues.extend(version_issues)
            
            # 2. 의존성 호환성 검사
            dep_issues, checked_deps = self._check_dependency_compatibility(plugin_id, plugin_version)
            issues.extend(dep_issues)
            dependencies_checked.extend(checked_deps)
            
            # 3. 시스템 요구사항 검사
            sys_issues, checked_reqs = self._check_system_requirements(plugin_id, plugin_version)
            issues.extend(sys_issues)
            system_requirements_checked.extend(checked_reqs)
            
            # 4. 순환 의존성 검사
            circular_issues = self._check_circular_dependencies(plugin_id)
            issues.extend(circular_issues)
            
            # 5. 리소스 충돌 검사
            resource_issues = self._check_resource_conflicts(plugin_id, plugin_version)
            issues.extend(resource_issues)
            
            # 호환성 판정
            compatible = len([i for i in issues if i.severity in ['high', 'critical']]) == 0
            
            # 권장사항 생성
            recommendations = self._generate_recommendations(issues, plugin_info)
            
            # 결과 저장
            self._save_compatibility_result(plugin_id, plugin_version, compatible, issues)
            
            return CompatibilityReport(
                plugin_id=plugin_id,
                plugin_name=plugin_info.get('name', plugin_id),
                plugin_version=plugin_version,
                compatible=compatible,
                issues=issues,
                dependencies_checked=dependencies_checked,
                system_requirements_checked=system_requirements_checked,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"호환성 검사 실패: {e}")
            return CompatibilityReport(
                plugin_id=plugin_id,
                plugin_name="Unknown",
                plugin_version=plugin_version or "unknown",
                compatible=False,
                issues=[CompatibilityIssue(
                    issue_type="check_error",
                    severity="critical",
                    plugin_id=plugin_id,
                    message=f"호환성 검사 중 오류 발생: {e}",
                    details={},
                    suggested_fix="시스템 로그를 확인하고 다시 시도하세요"
                )],
                dependencies_checked=[],
                system_requirements_checked=[],
                recommendations=["시스템 관리자에게 문의하세요"]
            )
    
    def _check_version_compatibility(self, plugin_id: str, target_version: str) -> List[CompatibilityIssue]:
        """버전 호환성 검사"""
        issues = []
        
        try:
            plugin_info = self._get_plugin_info(plugin_id)
            if not plugin_info:
                return issues
            
            current_version = plugin_info['version']
            
            # 버전 비교
            try:
                current_ver = version.parse(current_version)
                target_ver = version.parse(target_version)
                
                if current_ver < target_ver:
                    issues.append(CompatibilityIssue(
                        issue_type="version_conflict",
                        severity="high",
                        plugin_id=plugin_id,
                        message=f"버전이 낮습니다: 현재 {current_version}, 요구 {target_version}",
                        details={
                            'current_version': current_version,
                            'target_version': target_version
                        },
                        suggested_fix=f"플러그인을 버전 {target_version} 이상으로 업데이트하세요"
                    ))
                
            except version.InvalidVersion as e:
                issues.append(CompatibilityIssue(
                    issue_type="version_format_error",
                    severity="medium",
                    plugin_id=plugin_id,
                    message=f"잘못된 버전 형식: {e}",
                    details={
                        'current_version': current_version,
                        'target_version': target_version
                    },
                    suggested_fix="올바른 버전 형식(예: 1.2.3)을 사용하세요"
                ))
            
        except Exception as e:
            logger.error(f"버전 호환성 검사 실패: {e}")
        
        return issues
    
    def _check_dependency_compatibility(self, plugin_id: str, plugin_version: str) -> Tuple[List[CompatibilityIssue], List[str]]:
        """의존성 호환성 검사"""
        issues = []
        checked_deps = []
        
        try:
            dependencies = self._get_plugin_dependencies(plugin_id)
            for dep in (dependencies or []):
                dep_id = dep['dependency_id']
                version_constraint = dep['version_constraint']
                checked_deps.append(dep_id)
                
                # 의존성 플러그인 정보 조회
                dep_info = self._get_plugin_info(dep_id)
                if not dep_info:
                    issues.append(CompatibilityIssue(
                        issue_type="dependency_missing",
                        severity="critical",
                        plugin_id=plugin_id,
                        message=f"의존성 플러그인이 없습니다: {dep_id}",
                        details={
                            'dependency_id': dep_id,
                            'constraint': version_constraint
                        },
                        suggested_fix=f"플러그인 {dep_id}를 먼저 설치하세요"
                    ))
                    continue
                
                # 버전 호환성 검사
                try:
                    dep_version = dep_info['version']
                    spec = specifiers.SpecifierSet(version_constraint)
                    dep_ver = version.parse(dep_version)
                    
                    if dep_ver not in spec:
                        issues.append(CompatibilityIssue(
                            issue_type="dependency_version_conflict",
                            severity="high",
                            plugin_id=plugin_id,
                            message=f"의존성 버전 충돌: {dep_id} {dep_version} (요구: {version_constraint})",
                            details={
                                'dependency_id': dep_id,
                                'current_version': dep_version,
                                'required_constraint': version_constraint
                            },
                            suggested_fix=f"플러그인 {dep_id}를 버전 {version_constraint}에 맞게 업데이트하세요"
                        ))
                
                except (version.InvalidVersion, specifiers.InvalidSpecifier) as e:
                    issues.append(CompatibilityIssue(
                        issue_type="dependency_version_error",
                        severity="medium",
                        plugin_id=plugin_id,
                        message=f"의존성 버전 형식 오류: {dep_id} - {e}",
                        details={
                            'dependency_id': dep_id,
                            'constraint': version_constraint
                        },
                        suggested_fix="올바른 버전 제약 조건을 사용하세요"
                    ))
            
        except Exception as e:
            logger.error(f"의존성 호환성 검사 실패: {e}")
        
        return issues, checked_deps
    
    def _check_system_requirements(self, plugin_id: str, plugin_version: str) -> Tuple[List[CompatibilityIssue], List[str]]:
        """시스템 요구사항 검사"""
        issues = []
        checked_reqs = []
        
        try:
            requirements = self._get_plugin_requirements(plugin_id)
            
            for req in requirements or []:
                checked_reqs.append(req)
                
                if req.startswith('python'):
                    # Python 버전 요구사항
                    try:
                        spec = specifiers.SpecifierSet(req)
                        current_python = version.parse(self.system_info.python_version)
                        if current_python not in spec:
                            issues.append(CompatibilityIssue(
                                issue_type="python_version_incompatible",
                                severity="critical",
                                plugin_id=plugin_id,
                                message=f"Python 버전이 맞지 않습니다: 현재 {self.system_info.python_version}",
                                details={
                                    'requirement': req,
                                    'current_version': self.system_info.python_version
                                },
                                suggested_fix=f"Python을 {req}에 맞는 버전으로 업데이트하세요"
                            ))
                    except specifiers.InvalidSpecifier:
                        pass
                
                elif '>=' in req or '==' in req or '<=' in req:
                    # Python 패키지 요구사항
                    try:
                        result = pkg_resources.require(req)  # type: ignore
                        if result is None:
                            continue
                    except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict) as e:
                        issues.append(CompatibilityIssue(
                            issue_type="package_missing",
                            severity="high",
                            plugin_id=plugin_id,
                            message=f"필요한 패키지가 없습니다: {req}",
                            details={
                                'requirement': req,
                                'error': str(e)
                            },
                            suggested_fix=f"pip install {req}로 패키지를 설치하세요"
                        ))
                
                elif req.startswith('memory'):
                    # 메모리 요구사항
                    try:
                        required_memory = int(req.split('>=')[1].replace('MB', '').replace('GB', '')) * (1024**3 if 'GB' in req else 1024**2)
                        if self.system_info.available_memory < required_memory:
                            issues.append(CompatibilityIssue(
                                issue_type="insufficient_memory",
                                severity="medium",
                                plugin_id=plugin_id,
                                message=f"메모리가 부족합니다: 필요 {req}, 사용 가능 {self.system_info.available_memory // (1024**3)}GB",
                                details={
                                    'requirement': req,
                                    'available': self.system_info.available_memory
                                },
                                suggested_fix="메모리를 확보하거나 다른 프로세스를 종료하세요"
                            ))
                    except (ValueError, IndexError):
                        pass
                
                elif req.startswith('cpu'):
                    # CPU 요구사항
                    try:
                        required_cpus = int(req.split('>=')[1])
                        if self.system_info.cpu_count < required_cpus:
                            issues.append(CompatibilityIssue(
                                issue_type="insufficient_cpu",
                                severity="medium",
                                plugin_id=plugin_id,
                                message=f"CPU 코어가 부족합니다: 필요 {required_cpus}, 사용 가능 {self.system_info.cpu_count}",
                                details={
                                    'requirement': req,
                                    'available': self.system_info.cpu_count
                                },
                                suggested_fix="더 많은 CPU 코어가 있는 시스템을 사용하세요"
                            ))
                    except (ValueError, IndexError):
                        pass
            
        except Exception as e:
            logger.error(f"시스템 요구사항 검사 실패: {e}")
        
        return issues, checked_reqs
    
    def _check_circular_dependencies(self, plugin_id: str) -> List[CompatibilityIssue]:
        """순환 의존성 검사"""
        issues = []
        
        try:
            # 의존성 그래프 생성 및 순환 검사
            visited = set()
            recursion_stack = set()
            
            def has_cycle(node: str) -> bool:
                if node in recursion_stack:
                    return True
                if node in visited:
                    return False
                
                visited.add(node)
                recursion_stack.add(node)
                
                dependencies = self._get_plugin_dependencies(node)
                for dep in (dependencies or []):
                    if has_cycle(dep['dependency_id']):
                        return True
                
                recursion_stack.remove(node)
                return False
            
            if has_cycle(plugin_id):
                issues.append(CompatibilityIssue(
                    issue_type="circular_dependency",
                    severity="critical",
                    plugin_id=plugin_id,
                    message="순환 의존성이 감지되었습니다",
                    details={},
                    suggested_fix="의존성 구조를 재검토하고 순환을 제거하세요"
                ))
            
        except Exception as e:
            logger.error(f"순환 의존성 검사 실패: {e}")
        
        return issues
    
    def _check_resource_conflicts(self, plugin_id: str, plugin_version: str) -> List[CompatibilityIssue]:
        """리소스 충돌 검사"""
        issues = []
        
        try:
            # 포트 충돌 검사
            port_conflicts = self._check_port_conflicts(plugin_id)
            issues.extend(port_conflicts)
            
            # 파일 경로 충돌 검사
            path_conflicts = self._check_path_conflicts(plugin_id)
            issues.extend(path_conflicts)
            
            # 환경 변수 충돌 검사
            env_conflicts = self._check_environment_conflicts(plugin_id)
            issues.extend(env_conflicts)
            
        except Exception as e:
            logger.error(f"리소스 충돌 검사 실패: {e}")
        
        return issues
    
    def _check_port_conflicts(self, plugin_id: str) -> List[CompatibilityIssue]:
        """포트 충돌 검사"""
        issues = []
        
        try:
            # 플러그인 설정에서 포트 정보 조회
            plugin_config = self._get_plugin_config(plugin_id)
            if plugin_config and 'port' in plugin_config:
                port = plugin_config['port']
                
                # 포트 사용 여부 확인
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    issues.append(CompatibilityIssue(
                        issue_type="port_conflict",
                        severity="medium",
                        plugin_id=plugin_id,
                        message=f"포트 {port}가 이미 사용 중입니다",
                        details={'port': port},
                        suggested_fix=f"다른 포트를 사용하거나 포트 {port}를 사용하는 프로세스를 종료하세요"
                    ))
            
        except Exception as e:
            logger.error(f"포트 충돌 검사 실패: {e}")
        
        return issues
    
    def _check_path_conflicts(self, plugin_id: str) -> List[CompatibilityIssue]:
        """파일 경로 충돌 검사"""
        issues = []
        
        try:
            plugin_config = self._get_plugin_config(plugin_id)
            if plugin_config and 'paths' in plugin_config:
                for path_info in plugin_config['paths'] or []:
                    path = path_info.get('path')
                    if path and os.path.exists(path):
                        # 파일이 이미 존재하는 경우
                        if path_info.get('exclusive', False):
                            issues.append(CompatibilityIssue(
                                issue_type="path_conflict",
                                severity="medium",
                                plugin_id=plugin_id,
                                message=f"경로 충돌: {path}",
                                details={'path': path},
                                suggested_fix=f"경로 {path}를 백업하고 제거하거나 다른 경로를 사용하세요"
                            ))
            
        except Exception as e:
            logger.error(f"경로 충돌 검사 실패: {e}")
        
        return issues
    
    def _check_environment_conflicts(self, plugin_id: str) -> List[CompatibilityIssue]:
        """환경 변수 충돌 검사"""
        issues = []
        
        try:
            plugin_config = self._get_plugin_config(plugin_id)
            if plugin_config and 'environment' in plugin_config:
                for env_var in plugin_config['environment'] or []:
                    var_name = env_var.get('name')
                    required_value = env_var.get('value')
                    
                    if var_name in os.environ:
                        current_value = os.environ[var_name]
                        if current_value != required_value:
                            issues.append(CompatibilityIssue(
                                issue_type="environment_conflict",
                                severity="low",
                                plugin_id=plugin_id,
                                message=f"환경 변수 충돌: {var_name}",
                                details={
                                    'variable': var_name,
                                    'current': current_value,
                                    'required': required_value
                                },
                                suggested_fix=f"환경 변수 {var_name}를 {required_value}로 설정하세요"
                            ))
            
        except Exception as e:
            logger.error(f"환경 변수 충돌 검사 실패: {e}")
        
        return issues
    
    def _generate_recommendations(self, issues: List[CompatibilityIssue], plugin_info: Dict) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        # 심각도별 문제 수 계산
        critical_count = len([i for i in issues if i.severity == 'critical'])
        high_count = len([i for i in issues if i.severity == 'high'])
        
        if critical_count > 0:
            recommendations.append("중요한 호환성 문제가 있습니다. 먼저 해결하세요.")
        
        if high_count > 0:
            recommendations.append("높은 우선순위 문제를 해결하는 것을 권장합니다.")
        
        # 특정 문제 유형별 권장사항
        issue_types = [i.issue_type for i in issues]
        
        if 'version_conflict' in issue_types:
            recommendations.append("플러그인 버전을 업데이트하세요.")
        
        if 'dependency_missing' in issue_types:
            recommendations.append("필요한 의존성 플러그인을 설치하세요.")
        
        if 'package_missing' in issue_types:
            recommendations.append("필요한 Python 패키지를 설치하세요.")
        
        if 'circular_dependency' in issue_types:
            recommendations.append("의존성 구조를 재검토하세요.")
        
        if len(recommendations) == 0:
            recommendations.append("호환성 검사를 통과했습니다.")
        
        return recommendations
    
    def _get_plugin_info(self, plugin_id: str) -> Optional[Dict]:
        """플러그인 정보 조회"""
        # 실제 구현에서는 플러그인 데이터베이스에서 조회
        return None
    
    def _get_plugin_dependencies(self, plugin_id: str) -> List[Dict]:
        # 실제 구현에서는 의존성 데이터베이스에서 조회
        return []
    
    def _get_plugin_requirements(self, plugin_id: str) -> List[str]:
        """플러그인 요구사항 조회"""
        # 실제 구현에서는 플러그인 설정에서 조회
        return []
    
    def _get_plugin_config(self, plugin_id: str) -> Optional[Dict]:
        """플러그인 설정 조회"""
        # 실제 구현에서는 플러그인 설정 파일에서 조회
        return None
    
    def _save_compatibility_result(self, plugin_id: str, plugin_version: str, compatible: bool, issues: List[CompatibilityIssue]):
        """호환성 검사 결과 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO compatibility_results 
                    (plugin_id, plugin_version, compatible, issues, system_info)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    plugin_id,
                    plugin_version,
                    compatible,
                    json.dumps([asdict(issue) for issue in issues]),
                    json.dumps(asdict(self.system_info))
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"호환성 검사 결과 저장 실패: {e}")
    
    def batch_compatibility_check(self, plugin_ids: List[str]) -> Dict[str, CompatibilityReport]:
        """일괄 호환성 검사"""
        results = {}
        
        for plugin_id in plugin_ids:
            try:
                report = self.check_plugin_compatibility(plugin_id)
                results[plugin_id] = report
                logger.info(f"호환성 검사 완료: {plugin_id} - {'호환' if report.compatible else '비호환'}")
            except Exception as e:
                logger.error(f"호환성 검사 실패: {plugin_id} - {e}")
        
        return results
    
    def export_compatibility_report(self, output_path: str, reports: Dict[str, CompatibilityReport]):
        """호환성 보고서 내보내기"""
        try:
            report_data = {
                'generated_at': datetime.utcnow().isoformat(),
                'system_info': asdict(self.system_info),
                'reports': {
                    plugin_id: asdict(report) for plugin_id, report in reports.items()
                },
                'summary': {
                    'total_plugins': len(reports),
                    'compatible_plugins': len([r for r in reports.values() if r.compatible]),
                    'incompatible_plugins': len([r for r in reports.values() if not r.compatible]),
                    'total_issues': sum(len(r.issues) for r in reports.values()),
                    'critical_issues': sum(len([i for i in r.issues if i.severity == 'critical']) for r in reports.values()),
                    'high_issues': sum(len([i for i in r.issues if i.severity == 'high']) for r in reports.values())
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"호환성 보고서 내보내기 완료: {output_path}")
            
        except Exception as e:
            logger.error(f"호환성 보고서 내보내기 실패: {e}")

def main():
    """메인 함수"""
    try:
        # 호환성 검사기 초기화
        checker = PluginCompatibilityChecker()
        
        # 샘플 플러그인 호환성 검사
        sample_plugins = [
            'analytics_core',
            'reporting_engine',
            'dashboard_widget',
            'security_plugin',
            'backup_plugin'
        ]
        
        # 일괄 호환성 검사
        reports = checker.batch_compatibility_check(sample_plugins)
        
        # 결과 출력
        for plugin_id, report in reports.items():
            print(f"\n=== {plugin_id} 호환성 검사 결과 ===")
            print(f"호환성: {'✅ 호환' if report.compatible else '❌ 비호환'}")
            print(f"문제 수: {len(report.issues)}개")
            
            for issue in report.issues:
                print(f"  - [{issue.severity.upper()}] {issue.message}")
            
            print(f"권장사항:")
            for rec in report.recommendations:
                print(f"  - {rec}")
        
        # 보고서 내보내기
        checker.export_compatibility_report('compatibility_report.json', reports)
        
        logger.info("호환성 검사 완료")
        
    except Exception as e:
        logger.error(f"호환성 검사 시스템 오류: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 