"""
API 버전 관리 시스템
엔터프라이즈급 API 버전 관리, 호환성, 마이그레이션 시스템
"""

import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import semver
from semver import VersionInfo
import yaml
import jsonschema
from jsonschema import validate, ValidationError
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import hashlib
from collections import defaultdict

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VersionStatus(Enum):
    """버전 상태"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"

class BreakingChangeType(Enum):
    """호환성 깨짐 타입"""
    FIELD_REMOVED = "field_removed"
    FIELD_RENAMED = "field_renamed"
    FIELD_TYPE_CHANGED = "field_type_changed"
    REQUIRED_FIELD_ADDED = "required_field_added"
    ENDPOINT_REMOVED = "endpoint_removed"
    ENDPOINT_RENAMED = "endpoint_renamed"
    AUTH_CHANGED = "auth_changed"
    RESPONSE_FORMAT_CHANGED = "response_format_changed"

@dataclass
class APIVersion:
    """API 버전 정보"""
    id: str
    version: str
    name: str
    description: str
    status: VersionStatus
    release_date: Optional[datetime] = None
    deprecation_date: Optional[datetime] = None
    retirement_date: Optional[datetime] = None
    breaking_changes: List[Dict[str, Any]] = None
    migration_guide: Optional[str] = None
    changelog: List[Dict[str, Any]] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class APISchema:
    """API 스키마"""
    id: str
    version_id: str
    endpoint: str
    method: str
    request_schema: Dict[str, Any]
    response_schema: Dict[str, Any]
    examples: List[Dict[str, Any]] = None
    created_at: datetime = None

@dataclass
class BreakingChange:
    """호환성 깨짐 정보"""
    id: str
    version_id: str
    change_type: BreakingChangeType
    description: str
    affected_endpoints: List[str]
    migration_steps: List[str]
    severity: str  # low, medium, high, critical
    created_at: datetime = None

@dataclass
class VersionMigration:
    """버전 마이그레이션 정보"""
    id: str
    from_version: str
    to_version: str
    migration_script: str
    validation_rules: Dict[str, Any]
    rollback_script: Optional[str] = None
    estimated_duration: int = 0  # 분 단위
    created_at: datetime = None

class APIVersionManager:
    """API 버전 관리 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = None
        self.db_connection = None
        self.versions: Dict[str, APIVersion] = {}
        self.schemas: Dict[str, APISchema] = {}
        self.breaking_changes: Dict[str, BreakingChange] = {}
        self.migrations: Dict[str, VersionMigration] = {}
        self.version_cache: Dict[str, Any] = {}
        
        self._initialize_connections()
        self._load_versions()
        self._load_schemas()
        self._load_breaking_changes()
        self._load_migrations()
        self._setup_default_versions()
    
    def _initialize_connections(self):
        """연결 초기화"""
        try:
            # Redis 연결
            self.redis_client = redis.Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                db=self.config['redis']['db'],
                decode_responses=True
            )
            
            # PostgreSQL 연결
            self.db_connection = psycopg2.connect(
                host=self.config['database']['host'],
                port=self.config['database']['port'],
                database=self.config['database']['name'],
                user=self.config['database']['user'],
                password=self.config['database']['password']
            )
            
            logger.info("API 버전 관리 시스템 연결 초기화 완료")
            
        except Exception as e:
            logger.error(f"연결 초기화 오류: {e}")
            raise
    
    def _load_versions(self):
        """버전 정보 로드"""
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM api_versions ORDER BY version DESC
                """)
                
                for row in cursor.fetchall():
                    version = APIVersion(
                        id=row['id'],
                        version=row['version'],
                        name=row['name'],
                        description=row['description'],
                        status=VersionStatus(row['status']),
                        release_date=row['release_date'],
                        deprecation_date=row['deprecation_date'],
                        retirement_date=row['retirement_date'],
                        breaking_changes=row['breaking_changes'],
                        migration_guide=row['migration_guide'],
                        changelog=row['changelog'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    )
                    self.versions[version.id] = version
            
            logger.info(f"{len(self.versions)}개의 API 버전 로드 완료")
            
        except Exception as e:
            logger.error(f"버전 로드 오류: {e}")
    
    def _load_schemas(self):
        """스키마 정보 로드"""
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM api_schemas ORDER BY created_at DESC
                """)
                
                for row in cursor.fetchall():
                    schema = APISchema(
                        id=row['id'],
                        version_id=row['version_id'],
                        endpoint=row['endpoint'],
                        method=row['method'],
                        request_schema=row['request_schema'],
                        response_schema=row['response_schema'],
                        examples=row['examples'],
                        created_at=row['created_at']
                    )
                    self.schemas[schema.id] = schema
            
            logger.info(f"{len(self.schemas)}개의 API 스키마 로드 완료")
            
        except Exception as e:
            logger.error(f"스키마 로드 오류: {e}")
    
    def _load_breaking_changes(self):
        """호환성 깨짐 정보 로드"""
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM breaking_changes ORDER BY created_at DESC
                """)
                
                for row in cursor.fetchall():
                    breaking_change = BreakingChange(
                        id=row['id'],
                        version_id=row['version_id'],
                        change_type=BreakingChangeType(row['change_type']),
                        description=row['description'],
                        affected_endpoints=row['affected_endpoints'],
                        migration_steps=row['migration_steps'],
                        severity=row['severity'],
                        created_at=row['created_at']
                    )
                    self.breaking_changes[breaking_change.id] = breaking_change
            
            logger.info(f"{len(self.breaking_changes)}개의 호환성 깨짐 정보 로드 완료")
            
        except Exception as e:
            logger.error(f"호환성 깨짐 정보 로드 오류: {e}")
    
    def _load_migrations(self):
        """마이그레이션 정보 로드"""
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM version_migrations ORDER BY created_at DESC
                """)
                
                for row in cursor.fetchall():
                    migration = VersionMigration(
                        id=row['id'],
                        from_version=row['from_version'],
                        to_version=row['to_version'],
                        migration_script=row['migration_script'],
                        validation_rules=row['validation_rules'],
                        rollback_script=row['rollback_script'],
                        estimated_duration=row['estimated_duration'],
                        created_at=row['created_at']
                    )
                    self.migrations[migration.id] = migration
            
            logger.info(f"{len(self.migrations)}개의 마이그레이션 정보 로드 완료")
            
        except Exception as e:
            logger.error(f"마이그레이션 정보 로드 오류: {e}")
    
    def _setup_default_versions(self):
        """기본 버전 설정"""
        try:
            # v1.0.0 버전이 없으면 생성
            if not any(v.version == "1.0.0" for v in self.versions.values()):
                v1_0_0 = APIVersion(
                    id=str(uuid.uuid4()),
                    version="1.0.0",
                    name="Initial Release",
                    description="초기 API 버전",
                    status=VersionStatus.ACTIVE,
                    release_date=datetime.now(),
                    breaking_changes=[],
                    changelog=[
                        {
                            'type': 'feature',
                            'description': '초기 API 릴리스',
                            'date': datetime.now().isoformat()
                        }
                    ],
                    created_at=datetime.now()
                )
                
                self.versions[v1_0_0.id] = v1_0_0
                self._save_version_to_db(v1_0_0)
                
                logger.info("기본 v1.0.0 버전 생성 완료")
            
            # v2.0.0 버전이 없으면 생성
            if not any(v.version == "2.0.0" for v in self.versions.values()):
                v2_0_0 = APIVersion(
                    id=str(uuid.uuid4()),
                    version="2.0.0",
                    name="Enhanced API",
                    description="향상된 API 버전",
                    status=VersionStatus.DRAFT,
                    breaking_changes=[
                        {
                            'type': 'field_removed',
                            'description': 'legacy_field 필드 제거',
                            'affected_endpoints': ['/api/users', '/api/products'],
                            'migration_steps': ['legacy_field를 new_field로 변경']
                        }
                    ],
                    changelog=[
                        {
                            'type': 'breaking',
                            'description': 'legacy_field 제거',
                            'date': datetime.now().isoformat()
                        },
                        {
                            'type': 'feature',
                            'description': '새로운 인증 시스템',
                            'date': datetime.now().isoformat()
                        }
                    ],
                    created_at=datetime.now()
                )
                
                self.versions[v2_0_0.id] = v2_0_0
                self._save_version_to_db(v2_0_0)
                
                logger.info("기본 v2.0.0 버전 생성 완료")
                
        except Exception as e:
            logger.error(f"기본 버전 설정 오류: {e}")
    
    def create_version(self, version_data: Dict[str, Any]) -> str:
        """새 버전 생성"""
        try:
            # 버전 형식 검증
            version_str = version_data['version']
            if not self._is_valid_version(version_str):
                raise ValueError(f"유효하지 않은 버전 형식: {version_str}")
            
            # 버전 중복 검사
            if any(v.version == version_str for v in self.versions.values()):
                raise ValueError(f"이미 존재하는 버전: {version_str}")
            
            version_id = str(uuid.uuid4())
            
            version = APIVersion(
                id=version_id,
                version=version_str,
                name=version_data['name'],
                description=version_data.get('description', ''),
                status=VersionStatus(version_data.get('status', 'draft')),
                release_date=version_data.get('release_date'),
                deprecation_date=version_data.get('deprecation_date'),
                retirement_date=version_data.get('retirement_date'),
                breaking_changes=version_data.get('breaking_changes', []),
                migration_guide=version_data.get('migration_guide'),
                changelog=version_data.get('changelog', []),
                created_at=datetime.now()
            )
            
            self.versions[version_id] = version
            
            # 데이터베이스에 저장
            self._save_version_to_db(version)
            
            # 캐시 무효화
            self._invalidate_version_cache()
            
            logger.info(f"새 버전 생성 완료: {version_str}")
            return version_id
            
        except Exception as e:
            logger.error(f"버전 생성 오류: {e}")
            raise
    
    def _is_valid_version(self, version_str: str) -> bool:
        """버전 형식 검증"""
        try:
            VersionInfo.parse(version_str)
            return True
        except ValueError:
            return False
    
    def _save_version_to_db(self, version: APIVersion):
        """버전을 데이터베이스에 저장"""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO api_versions 
                    (id, version, name, description, status, release_date, 
                     deprecation_date, retirement_date, breaking_changes, 
                     migration_guide, changelog, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    version.id,
                    version.version,
                    version.name,
                    version.description,
                    version.status.value,
                    version.release_date,
                    version.deprecation_date,
                    version.retirement_date,
                    json.dumps(version.breaking_changes) if version.breaking_changes else None,
                    version.migration_guide,
                    json.dumps(version.changelog) if version.changelog else None,
                    version.created_at
                ))
                self.db_connection.commit()
                
        except Exception as e:
            logger.error(f"버전 저장 오류: {e}")
            raise
    
    def update_version_status(self, version_id: str, status: VersionStatus, 
                            deprecation_date: Optional[datetime] = None,
                            retirement_date: Optional[datetime] = None):
        """버전 상태 업데이트"""
        try:
            version = self.versions.get(version_id)
            if not version:
                raise ValueError(f"버전을 찾을 수 없습니다: {version_id}")
            
            version.status = status
            version.updated_at = datetime.now()
            
            if deprecation_date:
                version.deprecation_date = deprecation_date
            if retirement_date:
                version.retirement_date = retirement_date
            
            # 데이터베이스 업데이트
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE api_versions 
                    SET status = %s, deprecation_date = %s, retirement_date = %s, updated_at = %s
                    WHERE id = %s
                """, (
                    status.value,
                    version.deprecation_date,
                    version.retirement_date,
                    version.updated_at,
                    version_id
                ))
                self.db_connection.commit()
            
            # 캐시 무효화
            self._invalidate_version_cache()
            
            logger.info(f"버전 상태 업데이트 완료: {version_id} -> {status.value}")
            
        except Exception as e:
            logger.error(f"버전 상태 업데이트 오류: {e}")
            raise
    
    def add_schema(self, schema_data: Dict[str, Any]) -> str:
        """API 스키마 추가"""
        try:
            schema_id = str(uuid.uuid4())
            
            schema = APISchema(
                id=schema_id,
                version_id=schema_data['version_id'],
                endpoint=schema_data['endpoint'],
                method=schema_data['method'],
                request_schema=schema_data['request_schema'],
                response_schema=schema_data['response_schema'],
                examples=schema_data.get('examples', []),
                created_at=datetime.now()
            )
            
            self.schemas[schema_id] = schema
            
            # 데이터베이스에 저장
            self._save_schema_to_db(schema)
            
            logger.info(f"스키마 추가 완료: {schema_id}")
            return schema_id
            
        except Exception as e:
            logger.error(f"스키마 추가 오류: {e}")
            raise
    
    def _save_schema_to_db(self, schema: APISchema):
        """스키마를 데이터베이스에 저장"""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO api_schemas 
                    (id, version_id, endpoint, method, request_schema, 
                     response_schema, examples, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    schema.id,
                    schema.version_id,
                    schema.endpoint,
                    schema.method,
                    json.dumps(schema.request_schema),
                    json.dumps(schema.response_schema),
                    json.dumps(schema.examples) if schema.examples else None,
                    schema.created_at
                ))
                self.db_connection.commit()
                
        except Exception as e:
            logger.error(f"스키마 저장 오류: {e}")
            raise
    
    def validate_request(self, version: str, endpoint: str, method: str, 
                        request_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """요청 데이터 검증"""
        try:
            # 버전에 해당하는 스키마 찾기
            schema = self._find_schema(version, endpoint, method)
            if not schema:
                return False, ["스키마를 찾을 수 없습니다"]
            
            # 스키마 검증
            errors = []
            try:
                validate(instance=request_data, schema=schema.request_schema)
            except ValidationError as e:
                errors.append(str(e))
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"요청 검증 오류: {e}")
            return False, [str(e)]
    
    def validate_response(self, version: str, endpoint: str, method: str,
                         response_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """응답 데이터 검증"""
        try:
            # 버전에 해당하는 스키마 찾기
            schema = self._find_schema(version, endpoint, method)
            if not schema:
                return False, ["스키마를 찾을 수 없습니다"]
            
            # 스키마 검증
            errors = []
            try:
                validate(instance=response_data, schema=schema.response_schema)
            except ValidationError as e:
                errors.append(str(e))
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"응답 검증 오류: {e}")
            return False, [str(e)]
    
    def _find_schema(self, version: str, endpoint: str, method: str) -> Optional[APISchema]:
        """스키마 찾기"""
        try:
            # 버전 ID 찾기
            version_id = None
            for v in self.versions.values():
                if v.version == version:
                    version_id = v.id
                    break
            
            if not version_id:
                return None
            
            # 스키마 찾기
            for schema in self.schemas.values():
                if (schema.version_id == version_id and 
                    schema.endpoint == endpoint and 
                    schema.method.upper() == method.upper()):
                    return schema
            
            return None
            
        except Exception as e:
            logger.error(f"스키마 찾기 오류: {e}")
            return None
    
    def get_compatibility_report(self, from_version: str, to_version: str) -> Dict[str, Any]:
        """호환성 리포트 생성"""
        try:
            from_ver = self._get_version_by_string(from_version)
            to_ver = self._get_version_by_string(to_version)
            
            if not from_ver or not to_ver:
                return {"error": "버전을 찾을 수 없습니다"}
            
            # 호환성 분석
            breaking_changes = []
            new_features = []
            deprecated_features = []
            
            # 호환성 깨짐 분석
            for change in to_ver.breaking_changes or []:
                breaking_changes.append({
                    'type': change.get('type'),
                    'description': change.get('description'),
                    'affected_endpoints': change.get('affected_endpoints', []),
                    'migration_steps': change.get('migration_steps', [])
                })
            
            # 새 기능 분석
            for change in to_ver.changelog or []:
                if change.get('type') == 'feature':
                    new_features.append({
                        'description': change.get('description'),
                        'date': change.get('date')
                    })
            
            # 사용 중단 기능 분석
            if to_ver.deprecation_date:
                deprecated_features.append({
                    'description': '일부 기능이 사용 중단 예정',
                    'deprecation_date': to_ver.deprecation_date.isoformat()
                })
            
            return {
                'from_version': from_version,
                'to_version': to_version,
                'compatibility': 'breaking' if breaking_changes else 'compatible',
                'breaking_changes': breaking_changes,
                'new_features': new_features,
                'deprecated_features': deprecated_features,
                'migration_guide': to_ver.migration_guide,
                'recommendation': self._get_migration_recommendation(breaking_changes)
            }
            
        except Exception as e:
            logger.error(f"호환성 리포트 생성 오류: {e}")
            return {"error": str(e)}
    
    def _get_version_by_string(self, version_str: str) -> Optional[APIVersion]:
        """문자열로 버전 찾기"""
        try:
            for version in self.versions.values():
                if version.version == version_str:
                    return version
            return None
            
        except Exception as e:
            logger.error(f"버전 찾기 오류: {e}")
            return None
    
    def _get_migration_recommendation(self, breaking_changes: List[Dict[str, Any]]) -> str:
        """마이그레이션 권장사항 생성"""
        try:
            if not breaking_changes:
                return "호환성 문제가 없으므로 안전하게 업그레이드할 수 있습니다."
            
            critical_changes = [c for c in breaking_changes if c.get('type') in ['field_removed', 'endpoint_removed']]
            
            if critical_changes:
                return "중요한 호환성 문제가 있으므로 단계적 마이그레이션을 권장합니다."
            else:
                return "경미한 호환성 문제가 있으므로 주의하여 업그레이드하세요."
                
        except Exception as e:
            logger.error(f"마이그레이션 권장사항 생성 오류: {e}")
            return "마이그레이션 권장사항을 생성할 수 없습니다."
    
    def create_migration_plan(self, from_version: str, to_version: str) -> Dict[str, Any]:
        """마이그레이션 계획 생성"""
        try:
            # 호환성 리포트 생성
            compatibility_report = self.get_compatibility_report(from_version, to_version)
            
            if 'error' in compatibility_report:
                return compatibility_report
            
            # 마이그레이션 단계 생성
            migration_steps = []
            
            # 1단계: 준비
            migration_steps.append({
                'step': 1,
                'name': '마이그레이션 준비',
                'description': '현재 시스템 백업 및 테스트 환경 준비',
                'estimated_duration': 30,  # 분
                'critical': True
            })
            
            # 2단계: 코드 업데이트
            if compatibility_report['breaking_changes']:
                migration_steps.append({
                    'step': 2,
                    'name': '코드 업데이트',
                    'description': '호환성 깨짐에 따른 코드 수정',
                    'estimated_duration': 120,
                    'critical': True,
                    'details': compatibility_report['breaking_changes']
                })
            
            # 3단계: 테스트
            migration_steps.append({
                'step': 3,
                'name': '테스트',
                'description': '새 버전에 대한 종합 테스트',
                'estimated_duration': 60,
                'critical': True
            })
            
            # 4단계: 배포
            migration_steps.append({
                'step': 4,
                'name': '배포',
                'description': '프로덕션 환경에 새 버전 배포',
                'estimated_duration': 30,
                'critical': True
            })
            
            # 5단계: 검증
            migration_steps.append({
                'step': 5,
                'name': '검증',
                'description': '배포 후 시스템 검증',
                'estimated_duration': 30,
                'critical': True
            })
            
            # 총 예상 시간 계산
            total_duration = sum(step['estimated_duration'] for step in migration_steps)
            
            return {
                'from_version': from_version,
                'to_version': to_version,
                'total_duration': total_duration,
                'steps': migration_steps,
                'compatibility_report': compatibility_report,
                'risk_level': 'high' if compatibility_report['breaking_changes'] else 'low'
            }
            
        except Exception as e:
            logger.error(f"마이그레이션 계획 생성 오류: {e}")
            return {"error": str(e)}
    
    def get_version_timeline(self) -> List[Dict[str, Any]]:
        """버전 타임라인 생성"""
        try:
            timeline = []
            
            for version in sorted(self.versions.values(), key=lambda v: v.version):
                timeline.append({
                    'version': version.version,
                    'name': version.name,
                    'status': version.status.value,
                    'release_date': version.release_date.isoformat() if version.release_date else None,
                    'deprecation_date': version.deprecation_date.isoformat() if version.deprecation_date else None,
                    'retirement_date': version.retirement_date.isoformat() if version.retirement_date else None,
                    'breaking_changes_count': len(version.breaking_changes) if version.breaking_changes else 0
                })
            
            return timeline
            
        except Exception as e:
            logger.error(f"버전 타임라인 생성 오류: {e}")
            return []
    
    def get_active_versions(self) -> List[Dict[str, Any]]:
        """활성 버전 목록"""
        try:
            active_versions = []
            
            for version in self.versions.values():
                if version.status in [VersionStatus.ACTIVE, VersionStatus.DEPRECATED]:
                    active_versions.append({
                        'version': version.version,
                        'name': version.name,
                        'status': version.status.value,
                        'deprecation_date': version.deprecation_date.isoformat() if version.deprecation_date else None,
                        'endpoints_count': len([s for s in self.schemas.values() if s.version_id == version.id])
                    })
            
            return sorted(active_versions, key=lambda v: v['version'])
            
        except Exception as e:
            logger.error(f"활성 버전 목록 조회 오류: {e}")
            return []
    
    def _invalidate_version_cache(self):
        """버전 캐시 무효화"""
        try:
            # Redis 캐시 무효화
            cache_keys = self.redis_client.keys("version:*")
            if cache_keys:
                self.redis_client.delete(*cache_keys)
            
            # 메모리 캐시 무효화
            self.version_cache.clear()
            
        except Exception as e:
            logger.error(f"버전 캐시 무효화 오류: {e}")
    
    def generate_api_documentation(self, version: str) -> Dict[str, Any]:
        """API 문서 생성"""
        try:
            version_info = self._get_version_by_string(version)
            if not version_info:
                return {"error": "버전을 찾을 수 없습니다"}
            
            # 버전에 해당하는 스키마들 찾기
            schemas = [s for s in self.schemas.values() if s.version_id == version_info.id]
            
            # 엔드포인트별 문서 생성
            endpoints = {}
            for schema in schemas:
                endpoints[schema.endpoint] = {
                    'method': schema.method,
                    'request_schema': schema.request_schema,
                    'response_schema': schema.response_schema,
                    'examples': schema.examples or []
                }
            
            return {
                'version': version,
                'name': version_info.name,
                'description': version_info.description,
                'status': version_info.status.value,
                'endpoints': endpoints,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"API 문서 생성 오류: {e}")
            return {"error": str(e)}
    
    def get_version_statistics(self) -> Dict[str, Any]:
        """버전 통계"""
        try:
            stats = {
                'total_versions': len(self.versions),
                'active_versions': len([v for v in self.versions.values() if v.status == VersionStatus.ACTIVE]),
                'deprecated_versions': len([v for v in self.versions.values() if v.status == VersionStatus.DEPRECATED]),
                'retired_versions': len([v for v in self.versions.values() if v.status == VersionStatus.RETIRED]),
                'total_endpoints': len(self.schemas),
                'total_breaking_changes': len(self.breaking_changes),
                'latest_version': max([v.version for v in self.versions.values()], key=semver.VersionInfo.parse) if self.versions else None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"버전 통계 조회 오류: {e}")
            return {}

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 5
        },
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'your_program',
            'user': 'postgres',
            'password': 'password'
        }
    }
    
    # API 버전 관리자 생성
    version_manager = APIVersionManager(config)
    
    # 새 버전 생성
    version_id = version_manager.create_version({
        'version': '1.1.0',
        'name': 'Minor Update',
        'description': '사소한 업데이트',
        'status': 'active',
        'changelog': [
            {
                'type': 'feature',
                'description': '새로운 필터링 옵션 추가',
                'date': datetime.now().isoformat()
            }
        ]
    })
    
    print(f"새 버전 생성 완료: {version_id}")
    
    # 호환성 리포트 생성
    compatibility_report = version_manager.get_compatibility_report('1.0.0', '2.0.0')
    print(f"호환성 리포트: {compatibility_report}")
    
    # 버전 통계
    stats = version_manager.get_version_statistics()
    print(f"버전 통계: {stats}") 