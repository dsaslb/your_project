import re
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
import secrets
import hashlib
import json
from typing import Optional
from flask import request
query = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore


class SecurityLevel(Enum):
    """보안 레벨"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PermissionType(Enum):
    """권한 유형"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


@dataclass
class SecurityPolicy:
    """보안 정책"""
    plugin_id: str
    security_level: SecurityLevel
    allowed_ips: List[str]
    allowed_domains: List[str]
    max_requests_per_minute: int
    require_authentication: bool
    require_authorization: bool
    allowed_permissions: List[PermissionType]
    created_at: str
    updated_at: str


@dataclass
class ApiKey:
    """API 키"""
    key_id: str
    plugin_id: str
    name: str
    key_hash: str
    permissions: List[PermissionType]
    expires_at: Optional[str]
    last_used: Optional[str]
    created_at: str
    is_active: bool


@dataclass
class SecurityAuditLog:
    """보안 감사 로그"""
    log_id: str
    plugin_id: str
    user_id: Optional[str]
    action: str
    resource: str
    ip_address: str
    user_agent: str
    success: bool
    details: Dict[str, Any]
    timestamp: str


@dataclass
class VulnerabilityReport:
    """취약점 보고서"""
    report_id: str
    plugin_id: str
    severity: SecurityLevel
    title: str
    description: str
    cve_id: Optional[str]
    affected_versions: List[str]
    fixed_versions: List[str]
    remediation: str
    discovered_at: str
    status: str  # open, fixed, ignored


class PluginSecuritySystem:
    """플러그인 보안/인증/권한 관리 시스템"""

    def __init__(self, security_dir="plugin_security"):
        self.security_dir = Path(security_dir)
        self.security_dir.mkdir(exist_ok=True)

        # 보안 데이터 파일
        self.policies_file = self.security_dir / "policies.json"
        self.api_keys_file = self.security_dir / "api_keys.json"
        self.audit_logs_file = self.security_dir / "audit_logs.json"
        self.vulnerabilities_file = self.security_dir / "vulnerabilities.json"
        self.secret_key_file = self.security_dir / "secret.key"

        # 초기화
        self._init_security_system()

    def _init_security_system(self):
        """보안 시스템 초기화"""
        # 보안 정책 초기화
        if not self.policies_file.exists():
            with open(self.policies_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)

        # API 키 초기화
        if not self.api_keys_file.exists():
            with open(self.api_keys_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)

        # 감사 로그 초기화
        if not self.audit_logs_file.exists():
            with open(self.audit_logs_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)

        # 취약점 보고서 초기화
        if not self.vulnerabilities_file.exists():
            with open(self.vulnerabilities_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)

        # 시크릿 키 생성
        if not self.secret_key_file.exists():
            secret_key = secrets.token_hex(32)
            with open(self.secret_key_file, 'w') as f:
                f.write(secret_key)

    def create_security_policy(self,  plugin_id: str,  policy_data: Dict[str, Any]) -> bool:
        """보안 정책 생성"""
        try:
            policies = self._load_policies()

            # 기존 정책 확인
            existing_policy = next((p for p in policies if p['plugin_id'] == plugin_id), None)
            if existing_policy:
                return False  # 이미 존재하는 정책

            policy = SecurityPolicy(
                plugin_id=plugin_id,
                security_level=SecurityLevel(policy_data.get('security_level', 'medium')),
                allowed_ips=policy_data.get('allowed_ips', []),
                allowed_domains=policy_data.get('allowed_domains', []),
                max_requests_per_minute=policy_data.get('max_requests_per_minute', 100),
                require_authentication=policy_data.get('require_authentication', True),
                require_authorization=policy_data.get('require_authorization', True),
                allowed_permissions=[PermissionType(p) for p in policy_data.get('allowed_permissions', ['read'])],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )

            policies.append(self._policy_to_dict(policy))
            self._save_policies(policies)

            return True

        except Exception as e:
            print(f"보안 정책 생성 실패: {e}")
            return False

    def update_security_policy(self, plugin_id: str, policy_data: Dict) -> bool:
        """보안 정책 업데이트"""
        try:
            policies = self._load_policies()
            policy = next((p for p in policies if p['plugin_id'] == plugin_id), None)

            if not policy:
                return False

            # 정책 업데이트
            if 'security_level' in policy_data:
                policy['security_level'] = policy_data['security_level']
            if 'allowed_ips' in policy_data:
                policy['allowed_ips'] = policy_data['allowed_ips']
            if 'allowed_domains' in policy_data:
                policy['allowed_domains'] = policy_data['allowed_domains']
            if 'max_requests_per_minute' in policy_data:
                policy['max_requests_per_minute'] = policy_data['max_requests_per_minute']
            if 'require_authentication' in policy_data:
                policy['require_authentication'] = policy_data['require_authentication']
            if 'require_authorization' in policy_data:
                policy['require_authorization'] = policy_data['require_authorization']
            if 'allowed_permissions' in policy_data:
                policy['allowed_permissions'] = policy_data['allowed_permissions']

            policy['updated_at'] = datetime.now().isoformat()
            self._save_policies(policies)

            return True

        except Exception as e:
            print(f"보안 정책 업데이트 실패: {e}")
            return False

    def get_security_policy(self, plugin_id: str) -> Optional[Dict]:
        """보안 정책 조회"""
        try:
            policies = self._load_policies()
            policy = next((p for p in policies if p['plugin_id'] == plugin_id), None)
            return policy
        except Exception as e:
            print(f"보안 정책 조회 실패: {e}")
            return None

    def delete_security_policy(self, plugin_id: str) -> bool:
        """보안 정책 삭제"""
        try:
            policies = self._load_policies()
            policies = [p for p in policies if p['plugin_id'] != plugin_id]
            self._save_policies(policies)
            return True
        except Exception as e:
            print(f"보안 정책 삭제 실패: {e}")
            return False

    def generate_api_key(self, plugin_id: str, name: str, permissions: List[str], expires_in_days: Optional[int] = None) -> Optional[str]:
        """API 키 생성"""
        try:
            api_keys = self._load_api_keys()

            # API 키 생성
            key_value = secrets.token_urlsafe(32)
            key_hash = hashlib.sha256(key_value.encode()).hexdigest()

            expires_at = None
            if expires_in_days:
                expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()

            api_key = ApiKey(
                key_id=str(uuid.uuid4()),
                plugin_id=plugin_id,
                name=name,
                key_hash=key_hash,
                permissions=[PermissionType(p) for p in permissions],
                expires_at=expires_at,
                last_used=None,
                created_at=datetime.now().isoformat(),
                is_active=True
            )

            api_keys.append(self._api_key_to_dict(api_key))
            self._save_api_keys(api_keys)

            return key_value

        except Exception as e:
            print(f"API 키 생성 실패: {e}")
            return None

    def validate_api_key(self, key_value: str, plugin_id: str, required_permission: PermissionType) -> Optional[Dict]:
        """API 키 검증"""
        try:
            api_keys = self._load_api_keys()
            key_hash = hashlib.sha256(key_value.encode()).hexdigest()

            api_key = next((k for k in api_keys if k['key_hash'] == key_hash), None)

            if not api_key:
                return None

            # 플러그인 확인
            if api_key['plugin_id'] != plugin_id:
                return None

            # 활성 상태 확인
            if not api_key['is_active']:
                return None

            # 만료 확인
            if api_key['expires_at']:
                expires_at = datetime.fromisoformat(api_key['expires_at'])
                if datetime.now() > expires_at:
                    return None

            # 권한 확인
            if required_permission not in [PermissionType(p) for p in api_key['permissions']]:
                return None

            # 마지막 사용 시간 업데이트
            api_key['last_used'] = datetime.now().isoformat()
            self._save_api_keys(api_keys)

            return {
                'key_id': api_key['key_id'],
                'plugin_id': api_key['plugin_id'],
                'name': api_key['name'],
                'permissions': api_key['permissions']
            }

        except Exception as e:
            print(f"API 키 검증 실패: {e}")
            return None

    def revoke_api_key(self, key_id: str) -> bool:
        """API 키 폐기"""
        try:
            api_keys = self._load_api_keys()
            api_key = next((k for k in api_keys if k['key_id'] == key_id), None)

            if not api_key:
                return False

            api_key['is_active'] = False
            self._save_api_keys(api_keys)

            return True

        except Exception as e:
            print(f"API 키 폐기 실패: {e}")
            return False

    def get_api_keys(self, plugin_id: Optional[str] = None) -> List[Dict]:
        """API 키 목록 조회"""
        try:
            api_keys = self._load_api_keys()
            if plugin_id:
                api_keys = [k for k in api_keys if k['plugin_id'] == plugin_id]
            for key in api_keys:
                if 'key_hash' in key:
                    del key['key_hash']
            return api_keys
        except Exception as e:
            print(f"API 키 목록 조회 실패: {e}")
            return []

    def log_security_event(self, plugin_id: str, user_id: Optional[str] = None, action: str = "", resource: str = "", ip_address: str = "", user_agent: str = "", success: bool = False, details: Optional[Dict] = None) -> bool:
        """보안 이벤트 로깅"""
        try:
            audit_logs = self._load_audit_logs()
            log_entry = SecurityAuditLog(
                log_id=str(uuid.uuid4()),
                plugin_id=plugin_id,
                user_id=user_id or '',
                action=action,
                resource=resource,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                details=details or {},
                timestamp=datetime.now().isoformat()
            )
            audit_logs.append(self._audit_log_to_dict(log_entry))
            cutoff_time = datetime.now() - timedelta(days=30)
            audit_logs = [log for log in audit_logs if datetime.fromisoformat(log['timestamp']) > cutoff_time]
            self._save_audit_logs(audit_logs)
            return True
        except Exception as e:
            print(f"보안 이벤트 로깅 실패: {e}")
            return False

    def get_audit_logs(self, plugin_id: Optional[str] = None, user_id: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """감사 로그 조회"""
        try:
            audit_logs = self._load_audit_logs()
            if plugin_id:
                audit_logs = [log for log in audit_logs if log['plugin_id'] == plugin_id]
            if user_id:
                audit_logs = [log for log in audit_logs if log.get('user_id') == user_id]
            if start_date:
                start_dt = datetime.fromisoformat(start_date)
                audit_logs = [log for log in audit_logs if datetime.fromisoformat(log['timestamp']) >= start_dt]
            if end_date:
                end_dt = datetime.fromisoformat(end_date)
                audit_logs = [log for log in audit_logs if datetime.fromisoformat(log['timestamp']) <= end_dt]
            audit_logs.sort(key=lambda x: x['timestamp'], reverse=True)
            return audit_logs[:limit]
        except Exception as e:
            print(f"감사 로그 조회 실패: {e}")
            return []

    def scan_plugin_vulnerabilities(self, plugin_id: str) -> List[Dict]:
        """플러그인 취약점 스캔"""
        try:
            plugin_dir = Path("plugins") / plugin_id
            if not plugin_dir.exists():
                return []

            vulnerabilities = []

            # Python 파일 보안 스캔
            python_files = list(plugin_dir.glob("**/*.py"))
            for py_file in python_files:
                file_vulns = self._scan_python_file(py_file,  plugin_id)
                vulnerabilities.extend(file_vulns)

            # 설정 파일 보안 스캔
            config_files = list(plugin_dir.glob("**/*.json")) + \
                list(plugin_dir.glob("**/*.yaml")) + list(plugin_dir.glob("**/*.yml"))
            for config_file in config_files:
                file_vulns = self._scan_config_file(config_file,  plugin_id)
                vulnerabilities.extend(file_vulns)

            # 취약점 저장
            if vulnerabilities:
                self._save_vulnerabilities(vulnerabilities)

            return vulnerabilities

        except Exception as e:
            print(f"플러그인 취약점 스캔 실패: {e}")
            return []

    def _scan_python_file(self,  file_path: Path,  plugin_id: str) -> List[Dict]:
        """Python 파일 보안 스캔"""
        vulnerabilities = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 위험한 함수 사용 검사
            dangerous_functions = [
                'eval', 'exec', 'os.system', 'subprocess.call', 'subprocess.Popen',
                'pickle.loads', 'marshal.loads', 'yaml.load', 'json.loads'
            ]

            for func in dangerous_functions:
                if func in content:
                    vulnerabilities.append({
                        'report_id': str(uuid.uuid4()),
                        'plugin_id': plugin_id,
                        'severity': SecurityLevel.HIGH.value,
                        'title': f'위험한 함수 사용: {func}',
                        'description': f'파일 {file_path.name}에서 위험한 함수 {func}가 사용되었습니다.',
                        'cve_id': None,
                        'affected_versions': ['all'],
                        'fixed_versions': [],
                        'remediation': f'{func} 함수 사용을 피하고 더 안전한 대안을 사용하세요.',
                        'discovered_at': datetime.now().isoformat(),
                        'status': 'open'
                    })

            # 하드코딩된 비밀번호 검사
            password_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'key\s*=\s*["\'][^"\']+["\']'
            ]

            for pattern in password_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    vulnerabilities.append({
                        'report_id': str(uuid.uuid4()),
                        'plugin_id': plugin_id,
                        'severity': SecurityLevel.CRITICAL.value,
                        'title': '하드코딩된 비밀번호 발견',
                        'description': f'파일 {file_path.name}에서 하드코딩된 비밀번호가 발견되었습니다.',
                        'cve_id': None,
                        'affected_versions': ['all'],
                        'fixed_versions': [],
                        'remediation': '환경 변수나 설정 파일을 사용하여 비밀번호를 관리하세요.',
                        'discovered_at': datetime.now().isoformat(),
                        'status': 'open'
                    })
                    break

            # SQL 인젝션 취약점 검사
            sql_patterns = [
                r'execute\s*\(\s*["\'][^"\']*\+[^"\']*["\']',
                r'query\s*=\s*["\'][^"\']*\+[^"\']*["\']'
            ]

            for pattern in sql_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    vulnerabilities.append({
                        'report_id': str(uuid.uuid4()),
                        'plugin_id': plugin_id,
                        'severity': SecurityLevel.CRITICAL.value,
                        'title': 'SQL 인젝션 취약점 발견',
                        'description': f'파일 {file_path.name}에서 SQL 인젝션 취약점이 발견되었습니다.',
                        'cve_id': None,
                        'affected_versions': ['all'],
                        'fixed_versions': [],
                        'remediation': '매개변수화된 쿼리를 사용하세요.',
                        'discovered_at': datetime.now().isoformat(),
                        'status': 'open'
                    })
                    break

        except Exception as e:
            print(f"Python 파일 스캔 실패: {e}")

        return vulnerabilities

    def _scan_config_file(self,  file_path: Path,  plugin_id: str) -> List[Dict]:
        """설정 파일 보안 스캔"""
        vulnerabilities = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 하드코딩된 비밀번호 검사
            password_patterns = [
                r'"password"\s*:\s*"[^"]+"',
                r'"secret"\s*:\s*"[^"]+"',
                r'"key"\s*:\s*"[^"]+"'
            ]

            for pattern in password_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    vulnerabilities.append({
                        'report_id': str(uuid.uuid4()),
                        'plugin_id': plugin_id,
                        'severity': SecurityLevel.CRITICAL.value,
                        'title': '설정 파일에 하드코딩된 비밀번호',
                        'description': f'설정 파일 {file_path.name}에 하드코딩된 비밀번호가 발견되었습니다.',
                        'cve_id': None,
                        'affected_versions': ['all'],
                        'fixed_versions': [],
                        'remediation': '환경 변수나 별도의 보안 저장소를 사용하세요.',
                        'discovered_at': datetime.now().isoformat(),
                        'status': 'open'
                    })
                    break

        except Exception as e:
            print(f"설정 파일 스캔 실패: {e}")

        return vulnerabilities

    def get_vulnerabilities(self, plugin_id=None, severity=None, status=None) -> List[Dict]:
        """취약점 보고서 조회"""
        try:
            vulnerabilities = self._load_vulnerabilities()
            if plugin_id:
                vulnerabilities = [v for v in vulnerabilities if v['plugin_id'] == plugin_id]
            if severity:
                vulnerabilities = [v for v in vulnerabilities if v['severity'] == severity]
            if status:
                vulnerabilities = [v for v in vulnerabilities if v['status'] == status]
            vulnerabilities.sort(key=lambda x: x['discovered_at'], reverse=True)
            return vulnerabilities
        except Exception as e:
            print(f"취약점 보고서 조회 실패: {e}")
            return []

    def update_vulnerability_status(self, report_id: str, status: str) -> bool:
        """취약점 상태 업데이트"""
        try:
            vulnerabilities = self._load_vulnerabilities()
            vulnerability = next((v for v in vulnerabilities if v['report_id'] == report_id), None)

            if not vulnerability:
                return False

            vulnerability['status'] = status
            self._save_vulnerabilities(vulnerabilities)

            return True

        except Exception as e:
            print(f"취약점 상태 업데이트 실패: {e}")
            return False

    def check_permission(self, plugin_id: str, user_id: str, permission: PermissionType) -> bool:
        """권한 확인"""
        try:
            policy = self.get_security_policy(plugin_id)
            if not policy:
                return False

            allowed_permissions = [PermissionType(p) for p in policy.get('allowed_permissions', [])]
            return permission in allowed_permissions

        except Exception as e:
            print(f"권한 확인 실패: {e}")
            return False

    def _policy_to_dict(self, policy: SecurityPolicy) -> Dict:
        """SecurityPolicy를 딕셔너리로 변환"""
        return {
            'plugin_id': policy.plugin_id,
            'security_level': policy.security_level.value,
            'allowed_ips': policy.allowed_ips,
            'allowed_domains': policy.allowed_domains,
            'max_requests_per_minute': policy.max_requests_per_minute,
            'require_authentication': policy.require_authentication,
            'require_authorization': policy.require_authorization,
            'allowed_permissions': [p.value for p in policy.allowed_permissions],
            'created_at': policy.created_at,
            'updated_at': policy.updated_at
        }

    def _api_key_to_dict(self, api_key: ApiKey) -> Dict:
        """ApiKey를 딕셔너리로 변환"""
        return {
            'key_id': api_key.key_id,
            'plugin_id': api_key.plugin_id,
            'name': api_key.name,
            'key_hash': api_key.key_hash,
            'permissions': [p.value for p in api_key.permissions],
            'expires_at': api_key.expires_at,
            'last_used': api_key.last_used,
            'created_at': api_key.created_at,
            'is_active': api_key.is_active
        }

    def _audit_log_to_dict(self, audit_log: SecurityAuditLog) -> Dict:
        """SecurityAuditLog를 딕셔너리로 변환"""
        return {
            'log_id': audit_log.log_id,
            'plugin_id': audit_log.plugin_id,
            'user_id': audit_log.user_id,
            'action': audit_log.action,
            'resource': audit_log.resource,
            'ip_address': audit_log.ip_address,
            'user_agent': audit_log.user_agent,
            'success': audit_log.success,
            'details': audit_log.details,
            'timestamp': audit_log.timestamp
        }

    def _load_policies(self) -> List[Dict]:
        """보안 정책 로드"""
        try:
            with open(self.policies_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_policies(self, policies: List[Dict]):
        """보안 정책 저장"""
        try:
            with open(self.policies_file, 'w', encoding='utf-8') as f:
                json.dump(policies, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"보안 정책 저장 실패: {e}")

    def _load_api_keys(self) -> List[Dict]:
        """API 키 로드"""
        try:
            with open(self.api_keys_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_api_keys(self, api_keys: List[Dict]):
        """API 키 저장"""
        try:
            with open(self.api_keys_file, 'w', encoding='utf-8') as f:
                json.dump(api_keys, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"API 키 저장 실패: {e}")

    def _load_audit_logs(self) -> List[Dict]:
        """감사 로그 로드"""
        try:
            with open(self.audit_logs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_audit_logs(self, audit_logs: List[Dict]):
        """감사 로그 저장"""
        try:
            with open(self.audit_logs_file, 'w', encoding='utf-8') as f:
                json.dump(audit_logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"감사 로그 저장 실패: {e}")

    def _load_vulnerabilities(self) -> List[Dict]:
        """취약점 보고서 로드"""
        try:
            with open(self.vulnerabilities_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_vulnerabilities(self, vulnerabilities: List[Dict]):
        """취약점 보고서 저장"""
        try:
            existing_vulns = self._load_vulnerabilities()
            existing_vulns.extend(vulnerabilities)

            with open(self.vulnerabilities_file, 'w', encoding='utf-8') as f:
                json.dump(existing_vulns, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"취약점 보고서 저장 실패: {e}")
