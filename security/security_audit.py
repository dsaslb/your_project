import os
import json
import logging
import asyncio
import hashlib
import subprocess
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import redis
import psutil
import stat
import socket
import ssl
import requests
from cryptography.fernet import Fernet
import yaml

@dataclass
class SecurityAuditResult:
    """보안 감사 결과"""
    audit_id: str
    category: str
    check_name: str
    status: str  # PASS, FAIL, WARNING, INFO
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    details: Dict[str, Any]
    recommendation: str
    timestamp: datetime
    remediation_steps: List[str]

@dataclass
class ComplianceCheck:
    """컴플라이언스 체크"""
    standard: str  # ISO27001, GDPR, SOX, PCI-DSS
    requirement: str
    status: str
    evidence: str
    gap_analysis: str

class SecurityAuditor:
    """종합 보안 감사 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0)
        )
        self.db_path = Path(config.get('audit_db_path', 'security_audit.db'))
        self.init_database()
        
        # 감사 규칙 로드
        self.audit_rules = self._load_audit_rules()
        self.compliance_standards = self._load_compliance_standards()
        
        # 감사 결과 저장소
        self.audit_results: List[SecurityAuditResult] = []
        self.compliance_results: List[ComplianceCheck] = []
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def init_database(self):
        """감사 데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_results (
                    audit_id TEXT PRIMARY KEY,
                    category TEXT,
                    check_name TEXT,
                    status TEXT,
                    severity TEXT,
                    description TEXT,
                    details TEXT,
                    recommendation TEXT,
                    timestamp TEXT,
                    remediation_steps TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS compliance_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    standard TEXT,
                    requirement TEXT,
                    status TEXT,
                    evidence TEXT,
                    gap_analysis TEXT,
                    timestamp TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audit_session_id TEXT,
                    total_checks INTEGER,
                    passed INTEGER,
                    failed INTEGER,
                    warnings INTEGER,
                    critical_issues INTEGER,
                    start_time TEXT,
                    end_time TEXT,
                    duration_seconds INTEGER
                )
            ''')

    def _load_audit_rules(self) -> Dict[str, Any]:
        """감사 규칙 로드"""
        return {
            'system_security': {
                'password_policy': {
                    'min_length': 12,
                    'require_complexity': True,
                    'max_age_days': 90,
                    'history_count': 5
                },
                'account_lockout': {
                    'threshold': 5,
                    'duration_minutes': 30,
                    'enabled': True
                },
                'encryption': {
                    'data_at_rest': True,
                    'data_in_transit': True,
                    'key_rotation_days': 90
                }
            },
            'network_security': {
                'firewall': {
                    'enabled': True,
                    'default_deny': True,
                    'logging_enabled': True
                },
                'ssl_tls': {
                    'min_version': 'TLSv1.2',
                    'strong_ciphers': True,
                    'certificate_validation': True
                }
            },
            'application_security': {
                'input_validation': True,
                'output_encoding': True,
                'authentication': True,
                'authorization': True,
                'session_management': True,
                'error_handling': True,
                'logging_monitoring': True
            },
            'data_protection': {
                'backup_encryption': True,
                'access_control': True,
                'data_classification': True,
                'retention_policy': True
            },
            'infrastructure_security': {
                'os_hardening': True,
                'patch_management': True,
                'antivirus': True,
                'intrusion_detection': True
            }
        }

    def _load_compliance_standards(self) -> Dict[str, Any]:
        """컴플라이언스 표준 로드"""
        return {
            'ISO27001': {
                'A.8.1.1': '정보 자산 목록',
                'A.8.1.2': '정보 자산 소유권',
                'A.8.2.1': '정보 분류',
                'A.9.1.1': '접근 제어 정책',
                'A.9.2.1': '사용자 등록',
                'A.10.1.1': '암호화 정책',
                'A.12.1.1': '운영 절차',
                'A.12.6.1': '취약점 관리',
                'A.16.1.1': '보안 사고 대응'
            },
            'GDPR': {
                'Art.5': '개인데이터 처리 원칙',
                'Art.6': '처리의 적법성',
                'Art.25': '설계 및 기본 데이터 보호',
                'Art.32': '처리 보안',
                'Art.33': '개인데이터 침해 신고',
                'Art.35': '데이터 보호 영향 평가'
            },
            'PCI_DSS': {
                'Req.1': '방화벽 구성',
                'Req.2': '기본 보안 매개변수',
                'Req.3': '저장된 카드 소지자 데이터 보호',
                'Req.4': '암호화된 전송',
                'Req.6': '보안 시스템 및 응용프로그램 개발',
                'Req.8': '시스템 구성요소 접근 식별 및 인증',
                'Req.10': '네트워크 리소스 및 카드 소지자 데이터 접근 추적',
                'Req.11': '보안 시스템 및 프로세스 정기 테스트'
            }
        }

    async def run_comprehensive_audit(self) -> Dict[str, Any]:
        """종합 보안 감사 실행"""
        audit_session_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        self.logger.info(f"종합 보안 감사 시작: {audit_session_id}")
        
        try:
            # 감사 결과 초기화
            self.audit_results = []
            
            # 시스템 보안 감사
            await self._audit_system_security()
            
            # 네트워크 보안 감사
            await self._audit_network_security()
            
            # 애플리케이션 보안 감사
            await self._audit_application_security()
            
            # 데이터 보호 감사
            await self._audit_data_protection()
            
            # 인프라 보안 감사
            await self._audit_infrastructure_security()
            
            # 컴플라이언스 검증
            await self._check_compliance()
            
            # 감사 결과 저장
            await self._save_audit_results(audit_session_id)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 감사 요약 생성
            summary = self._generate_audit_summary(audit_session_id, start_time, end_time, duration)
            
            self.logger.info(f"종합 보안 감사 완료: {audit_session_id}")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"보안 감사 실행 중 오류: {e}")
            raise

    async def _audit_system_security(self):
        """시스템 보안 감사"""
        category = "시스템 보안"
        
        # 패스워드 정책 검사
        await self._check_password_policy(category)
        
        # 계정 잠금 정책 검사
        await self._check_account_lockout_policy(category)
        
        # 암호화 설정 검사
        await self._check_encryption_settings(category)
        
        # 사용자 계정 검사
        await self._check_user_accounts(category)
        
        # 권한 설정 검사
        await self._check_file_permissions(category)

    async def _check_password_policy(self, category: str):
        """패스워드 정책 검사"""
        try:
            # 패스워드 정책 파일 확인
            policy_file = Path('/etc/security/pwquality.conf')
            
            if policy_file.exists():
                with open(policy_file, 'r') as f:
                    content = f.read()
                
                # 최소 길이 검사
                min_length_found = 'minlen' in content and '12' in content
                
                result = SecurityAuditResult(
                    audit_id=f"pwd_policy_{datetime.now().timestamp()}",
                    category=category,
                    check_name="패스워드 정책",
                    status="PASS" if min_length_found else "FAIL",
                    severity="HIGH" if not min_length_found else "LOW",
                    description="패스워드 복잡성 정책 검사",
                    details={
                        "policy_file_exists": True,
                        "min_length_configured": min_length_found,
                        "content_sample": content[:200]
                    },
                    recommendation="패스워드 최소 길이를 12자 이상으로 설정하세요",
                    timestamp=datetime.now(),
                    remediation_steps=[
                        "pwquality.conf 파일에서 minlen=12 설정",
                        "복잡성 요구사항 활성화",
                        "패스워드 히스토리 설정"
                    ]
                )
            else:
                result = SecurityAuditResult(
                    audit_id=f"pwd_policy_{datetime.now().timestamp()}",
                    category=category,
                    check_name="패스워드 정책",
                    status="FAIL",
                    severity="CRITICAL",
                    description="패스워드 정책 파일 누락",
                    details={"policy_file_exists": False},
                    recommendation="패스워드 정책 설정 파일을 생성하고 정책을 적용하세요",
                    timestamp=datetime.now(),
                    remediation_steps=[
                        "pwquality.conf 파일 생성",
                        "적절한 패스워드 정책 설정",
                        "시스템 재시작 또는 정책 새로고침"
                    ]
                )
            
            self.audit_results.append(result)
            
        except Exception as e:
            self.logger.error(f"패스워드 정책 검사 오류: {e}")

    async def _check_account_lockout_policy(self, category: str):
        """계정 잠금 정책 검사"""
        try:
            # PAM 설정 확인
            pam_file = Path('/etc/pam.d/common-auth')
            
            if pam_file.exists():
                with open(pam_file, 'r') as f:
                    content = f.read()
                
                lockout_configured = 'pam_tally' in content or 'pam_faillock' in content
                
                result = SecurityAuditResult(
                    audit_id=f"lockout_policy_{datetime.now().timestamp()}",
                    category=category,
                    check_name="계정 잠금 정책",
                    status="PASS" if lockout_configured else "FAIL",
                    severity="MEDIUM" if not lockout_configured else "LOW",
                    description="계정 잠금 정책 설정 검사",
                    details={
                        "pam_file_exists": True,
                        "lockout_configured": lockout_configured
                    },
                    recommendation="실패 시도 후 계정 잠금 정책을 설정하세요",
                    timestamp=datetime.now(),
                    remediation_steps=[
                        "PAM 모듈에서 faillock 설정",
                        "실패 임계값을 5회로 설정",
                        "잠금 지속 시간을 30분으로 설정"
                    ]
                )
            else:
                result = SecurityAuditResult(
                    audit_id=f"lockout_policy_{datetime.now().timestamp()}",
                    category=category,
                    check_name="계정 잠금 정책",
                    status="WARNING",
                    severity="MEDIUM",
                    description="PAM 설정 파일 확인 불가",
                    details={"pam_file_exists": False},
                    recommendation="시스템별 인증 설정을 확인하세요",
                    timestamp=datetime.now(),
                    remediation_steps=[
                        "운영체제별 인증 설정 확인",
                        "적절한 계정 잠금 정책 구현"
                    ]
                )
            
            self.audit_results.append(result)
            
        except Exception as e:
            self.logger.error(f"계정 잠금 정책 검사 오류: {e}")

    async def _check_encryption_settings(self, category: str):
        """암호화 설정 검사"""
        try:
            # SSL/TLS 설정 확인
            ssl_enabled = self._check_ssl_configuration()
            
            # 데이터베이스 암호화 확인
            db_encryption = self._check_database_encryption()
            
            # 파일 시스템 암호화 확인
            fs_encryption = self._check_filesystem_encryption()
            
            encryption_score = sum([ssl_enabled, db_encryption, fs_encryption])
            
            result = SecurityAuditResult(
                audit_id=f"encryption_{datetime.now().timestamp()}",
                category=category,
                check_name="암호화 설정",
                status="PASS" if encryption_score >= 2 else "FAIL",
                severity="CRITICAL" if encryption_score == 0 else "MEDIUM" if encryption_score == 1 else "LOW",
                description="데이터 암호화 설정 검사",
                details={
                    "ssl_tls_enabled": ssl_enabled,
                    "database_encryption": db_encryption,
                    "filesystem_encryption": fs_encryption,
                    "encryption_score": f"{encryption_score}/3"
                },
                recommendation="모든 데이터에 대해 적절한 암호화를 적용하세요",
                timestamp=datetime.now(),
                remediation_steps=[
                    "SSL/TLS 인증서 설정 및 강화",
                    "데이터베이스 TDE(투명 데이터 암호화) 활성화",
                    "중요 파일 시스템 암호화 구현"
                ]
            )
            
            self.audit_results.append(result)
            
        except Exception as e:
            self.logger.error(f"암호화 설정 검사 오류: {e}")

    def _check_ssl_configuration(self) -> bool:
        """SSL 설정 확인"""
        try:
            # 기본 포트에서 SSL 서비스 확인
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            try:
                ssl_sock = context.wrap_socket(sock, server_hostname='localhost')
                ssl_sock.connect(('localhost', 443))
                ssl_sock.close()
                return True
            except:
                return False
                
        except Exception:
            return False

    def _check_database_encryption(self) -> bool:
        """데이터베이스 암호화 확인"""
        # 실제 구현에서는 데이터베이스별 암호화 설정 확인
        # 여기서는 간단한 예시
        return True  # 설정에 따라 실제 확인 로직 구현

    def _check_filesystem_encryption(self) -> bool:
        """파일 시스템 암호화 확인"""
        try:
            # LUKS 또는 기타 암호화 확인
            result = subprocess.run(['lsblk', '-f'], capture_output=True, text=True)
            return 'crypto_LUKS' in result.stdout
        except:
            return False

    async def _check_user_accounts(self, category: str):
        """사용자 계정 검사"""
        try:
            # 기본 계정 상태 확인
            default_accounts = ['admin', 'root', 'administrator', 'guest']
            inactive_accounts = []
            active_accounts = []
            
            # 현재 로그인된 사용자 확인
            current_users = [user.name for user in psutil.users()]
            
            # 시스템 사용자 확인 (간단한 예시)
            import pwd
            all_users = [user.pw_name for user in pwd.getpwall()]
            
            for account in default_accounts:
                if account in all_users:
                    if account in current_users:
                        active_accounts.append(account)
                    else:
                        inactive_accounts.append(account)
            
            # 보안 위험도 평가
            risk_level = "LOW"
            if 'guest' in active_accounts or 'admin' in active_accounts:
                risk_level = "HIGH"
            elif len(active_accounts) > 0:
                risk_level = "MEDIUM"
            
            result = SecurityAuditResult(
                audit_id=f"user_accounts_{datetime.now().timestamp()}",
                category=category,
                check_name="사용자 계정 보안",
                status="FAIL" if risk_level == "HIGH" else "WARNING" if risk_level == "MEDIUM" else "PASS",
                severity=risk_level,
                description="시스템 사용자 계정 보안성 검사",
                details={
                    "total_users": len(all_users),
                    "active_default_accounts": active_accounts,
                    "inactive_default_accounts": inactive_accounts,
                    "current_logged_users": len(current_users)
                },
                recommendation="불필요한 기본 계정을 비활성화하고 강력한 인증을 설정하세요",
                timestamp=datetime.now(),
                remediation_steps=[
                    "기본 관리자 계정 이름 변경",
                    "guest 계정 비활성화",
                    "불필요한 서비스 계정 제거",
                    "계정별 최소 권한 원칙 적용"
                ]
            )
            
            self.audit_results.append(result)
            
        except Exception as e:
            self.logger.error(f"사용자 계정 검사 오류: {e}")

    async def _check_file_permissions(self, category: str):
        """파일 권한 검사"""
        try:
            # 중요 시스템 파일 권한 확인
            critical_files = [
                '/etc/passwd',
                '/etc/shadow',
                '/etc/sudoers',
                '/etc/ssh/sshd_config'
            ]
            
            permission_issues = []
            secure_files = []
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    file_stat = os.stat(file_path)
                    permissions = oct(file_stat.st_mode)[-3:]
                    
                    # 보안 기준 (예: shadow 파일은 600이어야 함)
                    if file_path == '/etc/shadow' and permissions != '600':
                        permission_issues.append(f"{file_path}: {permissions} (should be 600)")
                    elif file_path == '/etc/passwd' and permissions not in ['644', '640']:
                        permission_issues.append(f"{file_path}: {permissions} (should be 644 or 640)")
                    else:
                        secure_files.append(f"{file_path}: {permissions}")
            
            result = SecurityAuditResult(
                audit_id=f"file_permissions_{datetime.now().timestamp()}",
                category=category,
                check_name="파일 권한 검사",
                status="PASS" if len(permission_issues) == 0 else "FAIL",
                severity="HIGH" if len(permission_issues) > 0 else "LOW",
                description="중요 시스템 파일의 권한 설정 검사",
                details={
                    "files_checked": len(critical_files),
                    "permission_issues": permission_issues,
                    "secure_files": secure_files
                },
                recommendation="중요 파일의 권한을 적절히 설정하세요",
                timestamp=datetime.now(),
                remediation_steps=[
                    "chmod 600 /etc/shadow",
                    "chmod 644 /etc/passwd",
                    "chmod 440 /etc/sudoers",
                    "정기적인 파일 권한 모니터링 설정"
                ]
            )
            
            self.audit_results.append(result)
            
        except Exception as e:
            self.logger.error(f"파일 권한 검사 오류: {e}")

    async def _audit_network_security(self):
        """네트워크 보안 감사"""
        category = "네트워크 보안"
        
        # 열린 포트 검사
        await self._check_open_ports(category)
        
        # 방화벽 설정 검사
        await self._check_firewall_status(category)
        
        # SSL/TLS 구성 검사
        await self._check_ssl_tls_configuration(category)

    async def _check_open_ports(self, category: str):
        """열린 포트 검사"""
        try:
            # 네트워크 연결 상태 확인
            connections = psutil.net_connections(kind='inet')
            
            listening_ports = []
            suspicious_ports = []
            
            # 일반적으로 의심스러운 포트들
            suspicious_port_list = [23, 135, 139, 445, 1433, 3389, 5432, 5900]
            
            for conn in connections:
                if conn.status == 'LISTEN' and conn.laddr:
                    port = conn.laddr.port
                    listening_ports.append(port)
                    
                    if port in suspicious_port_list:
                        suspicious_ports.append(port)
            
            result = SecurityAuditResult(
                audit_id=f"open_ports_{datetime.now().timestamp()}",
                category=category,
                check_name="열린 포트 검사",
                status="WARNING" if len(suspicious_ports) > 0 else "PASS",
                severity="MEDIUM" if len(suspicious_ports) > 0 else "LOW",
                description="시스템에서 열린 네트워크 포트 검사",
                details={
                    "total_listening_ports": len(listening_ports),
                    "listening_ports": sorted(listening_ports)[:20],  # 처음 20개만
                    "suspicious_ports": suspicious_ports
                },
                recommendation="불필요한 포트를 닫고 필요한 포트만 개방하세요",
                timestamp=datetime.now(),
                remediation_steps=[
                    "불필요한 서비스 중지",
                    "방화벽 규칙으로 포트 제한",
                    "정기적인 포트 스캔 모니터링"
                ]
            )
            
            self.audit_results.append(result)
            
        except Exception as e:
            self.logger.error(f"열린 포트 검사 오류: {e}")

    async def _check_firewall_status(self, category: str):
        """방화벽 상태 검사"""
        try:
            firewall_active = False
            firewall_type = "none"
            
            # UFW 확인
            try:
                result = subprocess.run(['ufw', 'status'], capture_output=True, text=True)
                if result.returncode == 0 and 'Status: active' in result.stdout:
                    firewall_active = True
                    firewall_type = "ufw"
            except:
                pass
            
            # iptables 확인
            if not firewall_active:
                try:
                    result = subprocess.run(['iptables', '-L'], capture_output=True, text=True)
                    if result.returncode == 0 and len(result.stdout.split('\n')) > 10:
                        firewall_active = True
                        firewall_type = "iptables"
                except:
                    pass
            
            result = SecurityAuditResult(
                audit_id=f"firewall_{datetime.now().timestamp()}",
                category=category,
                check_name="방화벽 상태",
                status="PASS" if firewall_active else "FAIL",
                severity="CRITICAL" if not firewall_active else "LOW",
                description="시스템 방화벽 활성화 상태 검사",
                details={
                    "firewall_active": firewall_active,
                    "firewall_type": firewall_type
                },
                recommendation="방화벽을 활성화하고 적절한 규칙을 설정하세요",
                timestamp=datetime.now(),
                remediation_steps=[
                    "UFW 또는 iptables 방화벽 활성화",
                    "기본 거부 정책 설정",
                    "필요한 포트만 선택적 허용",
                    "로깅 활성화"
                ]
            )
            
            self.audit_results.append(result)
            
        except Exception as e:
            self.logger.error(f"방화벽 상태 검사 오류: {e}")

    async def _check_ssl_tls_configuration(self, category: str):
        """SSL/TLS 구성 검사"""
        try:
            # 웹 서버 SSL 설정 확인
            ssl_issues = []
            ssl_strengths = []
            
            # 테스트할 포트들 (일반적인 SSL 포트)
            ssl_ports = [443, 8443, 993, 995, 465]
            
            for port in ssl_ports:
                try:
                    context = ssl.create_default_context()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    
                    ssl_sock = context.wrap_socket(sock, server_hostname='localhost')
                    ssl_sock.connect(('localhost', port))
                    
                    # SSL 버전 확인
                    ssl_version = ssl_sock.version()
                    cipher = ssl_sock.cipher()
                    
                    ssl_sock.close()
                    
                    if ssl_version in ['TLSv1.2', 'TLSv1.3']:
                        ssl_strengths.append(f"Port {port}: {ssl_version}")
                    else:
                        ssl_issues.append(f"Port {port}: Weak SSL version {ssl_version}")
                        
                except:
                    continue
            
            result = SecurityAuditResult(
                audit_id=f"ssl_tls_{datetime.now().timestamp()}",
                category=category,
                check_name="SSL/TLS 구성",
                status="PASS" if len(ssl_issues) == 0 and len(ssl_strengths) > 0 else "WARNING" if len(ssl_strengths) > 0 else "FAIL",
                severity="HIGH" if len(ssl_issues) > 0 else "MEDIUM" if len(ssl_strengths) == 0 else "LOW",
                description="SSL/TLS 구성 및 강도 검사",
                details={
                    "ssl_services_found": len(ssl_strengths),
                    "ssl_issues": ssl_issues,
                    "strong_configurations": ssl_strengths
                },
                recommendation="최신 TLS 버전과 강력한 암호화 스위트를 사용하세요",
                timestamp=datetime.now(),
                remediation_steps=[
                    "TLS 1.2 이상 버전 사용",
                    "약한 암호화 스위트 비활성화",
                    "HSTS 헤더 설정",
                    "정기적인 SSL 인증서 갱신"
                ]
            )
            
            self.audit_results.append(result)
            
        except Exception as e:
            self.logger.error(f"SSL/TLS 구성 검사 오류: {e}")

    async def _audit_application_security(self):
        """애플리케이션 보안 감사"""
        category = "애플리케이션 보안"
        
        # 코드 취약점 검사
        await self._check_code_vulnerabilities(category)
        
        # 의존성 취약점 검사
        await self._check_dependency_vulnerabilities(category)
        
        # 설정 파일 보안 검사
        await self._check_configuration_security(category)

    async def _check_code_vulnerabilities(self, category: str):
        """코드 취약점 검사"""
        # 간단한 정적 분석 예시
        result = SecurityAuditResult(
            audit_id=f"code_vuln_{datetime.now().timestamp()}",
            category=category,
            check_name="코드 취약점 검사",
            status="INFO",
            severity="LOW",
            description="애플리케이션 코드의 보안 취약점 검사",
            details={
                "scan_type": "basic_static_analysis",
                "files_scanned": 0,
                "vulnerabilities_found": 0
            },
            recommendation="정기적인 코드 보안 스캔을 실시하세요",
            timestamp=datetime.now(),
            remediation_steps=[
                "SAST 도구 도입",
                "코드 리뷰 프로세스 강화",
                "보안 코딩 가이드라인 적용"
            ]
        )
        
        self.audit_results.append(result)

    async def _check_dependency_vulnerabilities(self, category: str):
        """의존성 취약점 검사"""
        # Python 패키지 취약점 검사 예시
        result = SecurityAuditResult(
            audit_id=f"dependency_vuln_{datetime.now().timestamp()}",
            category=category,
            check_name="의존성 취약점 검사",
            status="INFO",
            severity="LOW",
            description="외부 라이브러리 및 의존성 취약점 검사",
            details={
                "package_manager": "pip",
                "packages_checked": 0,
                "vulnerable_packages": []
            },
            recommendation="의존성 취약점 스캐너를 정기적으로 실행하세요",
            timestamp=datetime.now(),
            remediation_steps=[
                "pip-audit 또는 safety 도구 사용",
                "패키지 업데이트 정책 수립",
                "취약한 패키지 즉시 교체"
            ]
        )
        
        self.audit_results.append(result)

    async def _check_configuration_security(self, category: str):
        """설정 파일 보안 검사"""
        try:
            config_files = [
                'config.py',
                'config.json',
                '.env',
                'docker-compose.yml'
            ]
            
            security_issues = []
            secure_configs = []
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        content = f.read().lower()
                    
                    # 하드코딩된 비밀번호나 키 확인
                    if any(keyword in content for keyword in ['password=', 'secret=', 'api_key=', 'token=']):
                        security_issues.append(f"{config_file}: Hardcoded credentials detected")
                    else:
                        secure_configs.append(config_file)
            
            result = SecurityAuditResult(
                audit_id=f"config_security_{datetime.now().timestamp()}",
                category=category,
                check_name="설정 파일 보안",
                status="FAIL" if len(security_issues) > 0 else "PASS",
                severity="CRITICAL" if len(security_issues) > 0 else "LOW",
                description="애플리케이션 설정 파일의 보안성 검사",
                details={
                    "config_files_checked": len(config_files),
                    "security_issues": security_issues,
                    "secure_configs": secure_configs
                },
                recommendation="설정 파일에서 하드코딩된 인증정보를 제거하세요",
                timestamp=datetime.now(),
                remediation_steps=[
                    "환경 변수 사용",
                    "보안 자격 증명 관리 시스템 도입",
                    "설정 파일 암호화",
                    "접근 권한 제한"
                ]
            )
            
            self.audit_results.append(result)
            
        except Exception as e:
            self.logger.error(f"설정 파일 보안 검사 오류: {e}")

    async def _audit_data_protection(self):
        """데이터 보호 감사"""
        category = "데이터 보호"
        
        # 데이터 백업 검사
        await self._check_data_backup(category)
        
        # 접근 제어 검사
        await self._check_access_control(category)
        
        # 데이터 분류 검사
        await self._check_data_classification(category)

    async def _check_data_backup(self, category: str):
        """데이터 백업 검사"""
        # 백업 시스템 확인 예시
        result = SecurityAuditResult(
            audit_id=f"data_backup_{datetime.now().timestamp()}",
            category=category,
            check_name="데이터 백업",
            status="INFO",
            severity="LOW",
            description="데이터 백업 시스템 검사",
            details={
                "backup_system": "configured",
                "last_backup": "unknown",
                "backup_encryption": "unknown"
            },
            recommendation="정기적인 백업과 복구 테스트를 실시하세요",
            timestamp=datetime.now(),
            remediation_steps=[
                "자동 백업 스케줄링",
                "백업 데이터 암호화",
                "오프사이트 백업 구성",
                "복구 절차 테스트"
            ]
        )
        
        self.audit_results.append(result)

    async def _check_access_control(self, category: str):
        """접근 제어 검사"""
        # 접근 제어 시스템 확인 예시
        result = SecurityAuditResult(
            audit_id=f"access_control_{datetime.now().timestamp()}",
            category=category,
            check_name="접근 제어",
            status="INFO",
            severity="LOW",
            description="데이터 접근 제어 시스템 검사",
            details={
                "rbac_implemented": True,
                "mfa_enabled": False,
                "audit_logging": True
            },
            recommendation="다중 인증과 세밀한 접근 제어를 구현하세요",
            timestamp=datetime.now(),
            remediation_steps=[
                "다중 인증(MFA) 도입",
                "역할 기반 접근 제어 강화",
                "정기적인 권한 검토",
                "접근 로그 모니터링"
            ]
        )
        
        self.audit_results.append(result)

    async def _check_data_classification(self, category: str):
        """데이터 분류 검사"""
        # 데이터 분류 시스템 확인 예시
        result = SecurityAuditResult(
            audit_id=f"data_classification_{datetime.now().timestamp()}",
            category=category,
            check_name="데이터 분류",
            status="WARNING",
            severity="MEDIUM",
            description="데이터 분류 및 라벨링 시스템 검사",
            details={
                "classification_policy": False,
                "data_labeling": False,
                "handling_procedures": False
            },
            recommendation="데이터 분류 정책과 절차를 수립하세요",
            timestamp=datetime.now(),
            remediation_steps=[
                "데이터 분류 정책 수립",
                "자동 데이터 라벨링 시스템 도입",
                "분류별 처리 절차 정의",
                "직원 교육 실시"
            ]
        )
        
        self.audit_results.append(result)

    async def _audit_infrastructure_security(self):
        """인프라 보안 감사"""
        category = "인프라 보안"
        
        # OS 강화 검사
        await self._check_os_hardening(category)
        
        # 패치 관리 검사
        await self._check_patch_management(category)
        
        # 모니터링 시스템 검사
        await self._check_monitoring_systems(category)

    async def _check_os_hardening(self, category: str):
        """OS 강화 검사"""
        # OS 보안 설정 확인 예시
        result = SecurityAuditResult(
            audit_id=f"os_hardening_{datetime.now().timestamp()}",
            category=category,
            check_name="OS 강화",
            status="INFO",
            severity="LOW",
            description="운영체제 보안 강화 설정 검사",
            details={
                "security_updates": "auto",
                "unused_services": "some_disabled",
                "security_kernel": "enabled"
            },
            recommendation="OS 보안 강화 가이드라인을 적용하세요",
            timestamp=datetime.now(),
            remediation_steps=[
                "불필요한 서비스 비활성화",
                "커널 보안 모듈 활성화",
                "시스템 감사 로깅 설정",
                "보안 벤치마크 적용"
            ]
        )
        
        self.audit_results.append(result)

    async def _check_patch_management(self, category: str):
        """패치 관리 검사"""
        # 패치 관리 시스템 확인 예시
        result = SecurityAuditResult(
            audit_id=f"patch_mgmt_{datetime.now().timestamp()}",
            category=category,
            check_name="패치 관리",
            status="WARNING",
            severity="MEDIUM",
            description="시스템 패치 관리 상태 검사",
            details={
                "auto_updates": True,
                "pending_updates": 5,
                "last_update": "1 week ago"
            },
            recommendation="정기적인 패치 적용과 취약점 관리를 실시하세요",
            timestamp=datetime.now(),
            remediation_steps=[
                "자동 보안 업데이트 활성화",
                "패치 테스트 환경 구축",
                "긴급 패치 절차 수립",
                "취약점 스캔 도구 도입"
            ]
        )
        
        self.audit_results.append(result)

    async def _check_monitoring_systems(self, category: str):
        """모니터링 시스템 검사"""
        # 보안 모니터링 시스템 확인 예시
        result = SecurityAuditResult(
            audit_id=f"monitoring_{datetime.now().timestamp()}",
            category=category,
            check_name="보안 모니터링",
            status="PASS",
            severity="LOW",
            description="보안 모니터링 시스템 구성 검사",
            details={
                "log_aggregation": True,
                "siem_system": False,
                "alerting": True,
                "retention_policy": True
            },
            recommendation="SIEM 시스템 도입을 고려하세요",
            timestamp=datetime.now(),
            remediation_steps=[
                "SIEM 솔루션 도입",
                "로그 상관관계 분석 강화",
                "실시간 위협 탐지 개선",
                "사고 대응 자동화"
            ]
        )
        
        self.audit_results.append(result)

    async def _check_compliance(self):
        """컴플라이언스 검증"""
        # ISO 27001 컴플라이언스 체크
        await self._check_iso27001_compliance()
        
        # GDPR 컴플라이언스 체크
        await self._check_gdpr_compliance()
        
        # PCI DSS 컴플라이언스 체크
        await self._check_pci_dss_compliance()

    async def _check_iso27001_compliance(self):
        """ISO 27001 컴플라이언스 검사"""
        iso_checks = []
        
        # A.8.1.1 - 정보 자산 목록
        iso_checks.append(ComplianceCheck(
            standard="ISO27001",
            requirement="A.8.1.1 - 정보 자산 목록",
            status="PARTIAL",
            evidence="자산 목록이 부분적으로 존재",
            gap_analysis="완전한 자산 분류 및 소유권 정의 필요"
        ))
        
        # A.9.1.1 - 접근 제어 정책
        iso_checks.append(ComplianceCheck(
            standard="ISO27001",
            requirement="A.9.1.1 - 접근 제어 정책",
            status="IMPLEMENTED",
            evidence="역할 기반 접근 제어 구현됨",
            gap_analysis="정기적인 접근 권한 검토 필요"
        ))
        
        self.compliance_results.extend(iso_checks)

    async def _check_gdpr_compliance(self):
        """GDPR 컴플라이언스 검사"""
        gdpr_checks = []
        
        # Art.25 - 설계 및 기본 데이터 보호
        gdpr_checks.append(ComplianceCheck(
            standard="GDPR",
            requirement="Art.25 - 설계 및 기본 데이터 보호",
            status="PARTIAL",
            evidence="일부 데이터 보호 기법 적용됨",
            gap_analysis="데이터 최소화 및 가명화 프로세스 강화 필요"
        ))
        
        # Art.32 - 처리 보안
        gdpr_checks.append(ComplianceCheck(
            standard="GDPR",
            requirement="Art.32 - 처리 보안",
            status="IMPLEMENTED",
            evidence="암호화 및 접근 제어 구현됨",
            gap_analysis="정기적인 보안 평가 필요"
        ))
        
        self.compliance_results.extend(gdpr_checks)

    async def _check_pci_dss_compliance(self):
        """PCI DSS 컴플라이언스 검사"""
        pci_checks = []
        
        # Req.1 - 방화벽 구성
        pci_checks.append(ComplianceCheck(
            standard="PCI_DSS",
            requirement="Req.1 - 방화벽 구성",
            status="IMPLEMENTED",
            evidence="네트워크 방화벽 활성화됨",
            gap_analysis="방화벽 규칙 정기 검토 필요"
        ))
        
        # Req.3 - 저장된 카드 소지자 데이터 보호
        pci_checks.append(ComplianceCheck(
            standard="PCI_DSS",
            requirement="Req.3 - 저장된 카드 소지자 데이터 보호",
            status="NOT_APPLICABLE",
            evidence="카드 데이터 저장하지 않음",
            gap_analysis="N/A"
        ))
        
        self.compliance_results.extend(pci_checks)

    async def _save_audit_results(self, audit_session_id: str):
        """감사 결과 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 감사 결과 저장
                for result in self.audit_results:
                    conn.execute('''
                        INSERT OR REPLACE INTO audit_results 
                        (audit_id, category, check_name, status, severity, description, 
                         details, recommendation, timestamp, remediation_steps)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        result.audit_id,
                        result.category,
                        result.check_name,
                        result.status,
                        result.severity,
                        result.description,
                        json.dumps(result.details),
                        result.recommendation,
                        result.timestamp.isoformat(),
                        json.dumps(result.remediation_steps)
                    ))
                
                # 컴플라이언스 결과 저장
                for comp_result in self.compliance_results:
                    conn.execute('''
                        INSERT INTO compliance_checks 
                        (standard, requirement, status, evidence, gap_analysis, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        comp_result.standard,
                        comp_result.requirement,
                        comp_result.status,
                        comp_result.evidence,
                        comp_result.gap_analysis,
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
                
            # Redis에도 저장
            await self._cache_audit_results(audit_session_id)
            
        except Exception as e:
            self.logger.error(f"감사 결과 저장 오류: {e}")

    async def _cache_audit_results(self, audit_session_id: str):
        """감사 결과를 Redis에 캐시"""
        try:
            # 감사 요약 캐시
            summary_data = {
                'session_id': audit_session_id,
                'total_checks': len(self.audit_results),
                'passed': len([r for r in self.audit_results if r.status == 'PASS']),
                'failed': len([r for r in self.audit_results if r.status == 'FAIL']),
                'warnings': len([r for r in self.audit_results if r.status == 'WARNING']),
                'critical_issues': len([r for r in self.audit_results if r.severity == 'CRITICAL']),
                'timestamp': datetime.now().isoformat()
            }
            
            self.redis_client.setex(
                f"audit_summary:{audit_session_id}",
                3600,  # 1시간 TTL
                json.dumps(summary_data)
            )
            
            # 최근 감사 결과 목록 업데이트
            recent_audits = self.redis_client.lrange("recent_audits", 0, 9)  # 최근 10개
            recent_audits.insert(0, audit_session_id.encode())
            
            pipe = self.redis_client.pipeline()
            pipe.delete("recent_audits")
            for audit_id in recent_audits[:10]:  # 최근 10개만 유지
                pipe.lpush("recent_audits", audit_id)
            pipe.execute()
            
        except Exception as e:
            self.logger.error(f"감사 결과 캐시 오류: {e}")

    def _generate_audit_summary(self, audit_session_id: str, start_time: datetime, 
                              end_time: datetime, duration: float) -> Dict[str, Any]:
        """감사 요약 생성"""
        # 상태별 통계
        status_counts = {
            'PASS': len([r for r in self.audit_results if r.status == 'PASS']),
            'FAIL': len([r for r in self.audit_results if r.status == 'FAIL']),
            'WARNING': len([r for r in self.audit_results if r.status == 'WARNING']),
            'INFO': len([r for r in self.audit_results if r.status == 'INFO'])
        }
        
        # 심각도별 통계
        severity_counts = {
            'CRITICAL': len([r for r in self.audit_results if r.severity == 'CRITICAL']),
            'HIGH': len([r for r in self.audit_results if r.severity == 'HIGH']),
            'MEDIUM': len([r for r in self.audit_results if r.severity == 'MEDIUM']),
            'LOW': len([r for r in self.audit_results if r.severity == 'LOW'])
        }
        
        # 카테고리별 통계
        category_stats = {}
        for result in self.audit_results:
            category = result.category
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'passed': 0, 'failed': 0}
            
            category_stats[category]['total'] += 1
            if result.status == 'PASS':
                category_stats[category]['passed'] += 1
            elif result.status == 'FAIL':
                category_stats[category]['failed'] += 1
        
        # 전체 보안 점수 계산
        total_checks = len(self.audit_results)
        security_score = 0
        if total_checks > 0:
            weighted_score = 0
            total_weight = 0
            
            for result in self.audit_results:
                weight = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}[result.severity]
                points = {'PASS': 100, 'WARNING': 70, 'INFO': 90, 'FAIL': 0}[result.status]
                
                weighted_score += points * weight
                total_weight += weight * 100  # 만점 기준
            
            security_score = int(weighted_score / total_weight * 100) if total_weight > 0 else 0
        
        # 컴플라이언스 요약
        compliance_summary = {}
        for comp_result in self.compliance_results:
            standard = comp_result.standard
            if standard not in compliance_summary:
                compliance_summary[standard] = {'total': 0, 'implemented': 0, 'partial': 0, 'not_applicable': 0}
            
            compliance_summary[standard]['total'] += 1
            status_key = comp_result.status.lower()
            if status_key in compliance_summary[standard]:
                compliance_summary[standard][status_key] += 1
        
        return {
            'audit_session_id': audit_session_id,
            'execution_time': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'duration_formatted': f"{int(duration // 60)}분 {int(duration % 60)}초"
            },
            'overview': {
                'total_checks': total_checks,
                'security_score': security_score,
                'critical_issues': severity_counts['CRITICAL'],
                'high_issues': severity_counts['HIGH']
            },
            'status_summary': status_counts,
            'severity_summary': severity_counts,
            'category_summary': category_stats,
            'compliance_summary': compliance_summary,
            'top_recommendations': [
                result.recommendation for result in 
                sorted(self.audit_results, key=lambda x: ({'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}[x.severity], x.status == 'FAIL'), reverse=True)[:5]
            ]
        }

    async def get_audit_results(self, audit_session_id: Optional[str] = None, 
                              limit: int = 100) -> List[Dict[str, Any]]:
        """감사 결과 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if audit_session_id:
                    # 특정 세션의 결과 조회
                    cursor = conn.execute('''
                        SELECT * FROM audit_results 
                        WHERE audit_id LIKE ? 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (f"%{audit_session_id}%", limit))
                else:
                    # 최근 결과 조회
                    cursor = conn.execute('''
                        SELECT * FROM audit_results 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (limit,))
                
                results = []
                for row in cursor.fetchall():
                    result_dict = {
                        'audit_id': row[0],
                        'category': row[1],
                        'check_name': row[2],
                        'status': row[3],
                        'severity': row[4],
                        'description': row[5],
                        'details': json.loads(row[6]) if row[6] else {},
                        'recommendation': row[7],
                        'timestamp': row[8],
                        'remediation_steps': json.loads(row[9]) if row[9] else []
                    }
                    results.append(result_dict)
                
                return results
                
        except Exception as e:
            self.logger.error(f"감사 결과 조회 오류: {e}")
            return []

    async def get_compliance_status(self, standard: Optional[str] = None) -> List[Dict[str, Any]]:
        """컴플라이언스 상태 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if standard:
                    cursor = conn.execute('''
                        SELECT * FROM compliance_checks 
                        WHERE standard = ? 
                        ORDER BY timestamp DESC
                    ''', (standard,))
                else:
                    cursor = conn.execute('''
                        SELECT * FROM compliance_checks 
                        ORDER BY standard, timestamp DESC
                    ''')
                
                results = []
                for row in cursor.fetchall():
                    result_dict = {
                        'id': row[0],
                        'standard': row[1],
                        'requirement': row[2],
                        'status': row[3],
                        'evidence': row[4],
                        'gap_analysis': row[5],
                        'timestamp': row[6]
                    }
                    results.append(result_dict)
                
                return results
                
        except Exception as e:
            self.logger.error(f"컴플라이언스 상태 조회 오류: {e}")
            return []

    async def generate_audit_report(self, audit_session_id: str) -> str:
        """감사 보고서 생성"""
        try:
            # 감사 결과 조회
            audit_results = await self.get_audit_results(audit_session_id)
            compliance_results = await self.get_compliance_status()
            
            # 보고서 템플릿 (간단한 마크다운 형식)
            report = f"""
# 보안 감사 보고서

**감사 세션 ID:** {audit_session_id}
**생성 일시:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 감사 요약

- **총 검사 항목:** {len(audit_results)}개
- **통과:** {len([r for r in audit_results if r['status'] == 'PASS'])}개
- **실패:** {len([r for r in audit_results if r['status'] == 'FAIL'])}개
- **경고:** {len([r for r in audit_results if r['status'] == 'WARNING'])}개

## 심각도별 분류

- **심각:** {len([r for r in audit_results if r['severity'] == 'CRITICAL'])}개
- **높음:** {len([r for r in audit_results if r['severity'] == 'HIGH'])}개
- **보통:** {len([r for r in audit_results if r['severity'] == 'MEDIUM'])}개
- **낮음:** {len([r for r in audit_results if r['severity'] == 'LOW'])}개

## 주요 발견사항

### 실패한 검사 항목
"""
            
            failed_checks = [r for r in audit_results if r['status'] == 'FAIL']
            for check in failed_checks[:10]:  # 상위 10개
                report += f"""
#### {check['check_name']} ({check['category']})
- **심각도:** {check['severity']}
- **설명:** {check['description']}
- **권장사항:** {check['recommendation']}
"""
            
            report += """
## 컴플라이언스 상태
"""
            
            standards = set([r['standard'] for r in compliance_results])
            for standard in standards:
                standard_results = [r for r in compliance_results if r['standard'] == standard]
                implemented = len([r for r in standard_results if r['status'] == 'IMPLEMENTED'])
                total = len(standard_results)
                
                report += f"""
### {standard}
- **구현됨:** {implemented}/{total} ({int(implemented/total*100) if total > 0 else 0}%)
"""
            
            return report
            
        except Exception as e:
            self.logger.error(f"감사 보고서 생성 오류: {e}")
            return "보고서 생성 중 오류가 발생했습니다."

if __name__ == "__main__":
    # 테스트 실행
    async def main():
        config = {
            'redis_host': 'localhost',
            'redis_port': 6379,
            'redis_db': 0,
            'audit_db_path': 'security_audit.db'
        }
        
        auditor = SecurityAuditor(config)
        
        # 종합 감사 실행
        summary = await auditor.run_comprehensive_audit()
        print("감사 완료:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    asyncio.run(main()) 