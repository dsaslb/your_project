"""
보안 테스트 및 취약점 스캔 시스템
"""

import requests
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import re
import ssl
import socket
from urllib.parse import urlparse, urljoin
import subprocess
import nmap
import hashlib

logger = logging.getLogger(__name__)

class VulnerabilityLevel(Enum):
    """취약점 레벨"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ScanType(Enum):
    """스캔 타입"""
    NETWORK = "network"
    WEB = "web"
    DATABASE = "database"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"

@dataclass
class Vulnerability:
    """취약점 정보"""
    id: str
    title: str
    description: str
    level: str
    scan_type: str
    target: str
    details: Dict[str, Any]
    cve_id: Optional[str]
    cvss_score: Optional[float]
    remediation: str
    discovered_at: str
    status: str  # open, fixed, false_positive

@dataclass
class ScanResult:
    """스캔 결과"""
    scan_id: str
    scan_type: str
    target: str
    start_time: str
    end_time: str
    status: str  # running, completed, failed
    vulnerabilities: List[Vulnerability]
    summary: Dict[str, Any]
    scan_config: Dict[str, Any]

class SecurityScanner:
    """보안 스캐너"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'database_file': 'security/scanner.db',
            'max_concurrent_scans': 5,
            'scan_timeout': 300,  # 5분
            'retry_attempts': 3,
            'user_agent': 'SecurityScanner/1.0',
            'excluded_paths': ['/admin', '/api/health'],
            'custom_headers': {},
            'nmap_path': 'nmap'
        }
        
        # 데이터베이스 초기화
        self._init_database()
        
        # 스캔 큐 및 스레드 풀
        self.scan_queue = []
        self.active_scans = {}
        self.scan_lock = threading.Lock()
        
        # 스캔 워커 스레드
        self.worker_threads = []
        self._start_worker_threads()
        
        # 취약점 패턴
        self.vulnerability_patterns = self._init_vulnerability_patterns()
        
        # 알림 콜백
        self.alert_callbacks = []
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            # 취약점 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    level TEXT NOT NULL,
                    scan_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    details TEXT,
                    cve_id TEXT,
                    cvss_score REAL,
                    remediation TEXT,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'open',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 스캔 결과 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_results (
                    scan_id TEXT PRIMARY KEY,
                    scan_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    status TEXT NOT NULL,
                    vulnerabilities TEXT,
                    summary TEXT,
                    scan_config TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vulns_level ON vulnerabilities(level)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vulns_target ON vulnerabilities(target)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vulns_status ON vulnerabilities(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scans_type ON scan_results(scan_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scans_status ON scan_results(status)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"스캐너 데이터베이스 초기화 실패: {e}")
    
    def _init_vulnerability_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """취약점 패턴 초기화"""
        return {
            'sql_injection': [
                {
                    'pattern': r"(\b(union|select|insert|update|delete|drop|create|alter)\b.*\b(from|into|where|table|database)\b)",
                    'level': 'high',
                    'title': 'SQL Injection Vulnerability',
                    'description': 'SQL 인젝션 취약점이 발견되었습니다.'
                }
            ],
            'xss': [
                {
                    'pattern': r"<script[^>]*>.*?</script>",
                    'level': 'high',
                    'title': 'Cross-Site Scripting (XSS)',
                    'description': 'XSS 취약점이 발견되었습니다.'
                }
            ],
            'csrf': [
                {
                    'pattern': r"csrf.*token",
                    'level': 'medium',
                    'title': 'Missing CSRF Protection',
                    'description': 'CSRF 보호가 누락되었습니다.'
                }
            ],
            'information_disclosure': [
                {
                    'pattern': r"(error|exception|stack trace|debug)",
                    'level': 'medium',
                    'title': 'Information Disclosure',
                    'description': '정보 노출 취약점이 발견되었습니다.'
                }
            ]
        }
    
    def _start_worker_threads(self):
        """워커 스레드 시작"""
        for i in range(self.config['max_concurrent_scans']):
            thread = threading.Thread(target=self._scan_worker, daemon=True)
            thread.start()
            self.worker_threads.append(thread)
    
    def _scan_worker(self):
        """스캔 워커 스레드"""
        while True:
            try:
                with self.scan_lock:
                    if not self.scan_queue:
                        time.sleep(1)
                        continue
                    
                    scan_task = self.scan_queue.pop(0)
                
                # 스캔 실행
                self._execute_scan(scan_task)
                
            except Exception as e:
                logger.error(f"스캔 워커 오류: {e}")
                time.sleep(5)
    
    def _execute_scan(self, scan_task: Dict[str, Any]):
        """스캔 실행"""
        try:
            scan_id = scan_task['scan_id']
            scan_type = scan_task['scan_type']
            target = scan_task['target']
            
            # 스캔 상태 업데이트
            self._update_scan_status(scan_id, 'running')
            
            start_time = datetime.now()
            
            # 스캔 타입별 실행
            if scan_type == 'network':
                vulnerabilities = self._scan_network(target)
            elif scan_type == 'web':
                vulnerabilities = self._scan_web(target)
            elif scan_type == 'database':
                vulnerabilities = self._scan_database(target)
            elif scan_type == 'configuration':
                vulnerabilities = self._scan_configuration(target)
            elif scan_type == 'dependency':
                vulnerabilities = self._scan_dependencies(target)
            else:
                raise ValueError(f"지원하지 않는 스캔 타입: {scan_type}")
            
            end_time = datetime.now()
            
            # 결과 저장
            self._save_scan_result(scan_id, scan_type, target, start_time, end_time, vulnerabilities)
            
            # 알림 트리거
            self._trigger_scan_alerts(scan_id, vulnerabilities)
            
        except Exception as e:
            logger.error(f"스캔 실행 실패 {scan_id}: {e}")
            self._update_scan_status(scan_id, 'failed')
    
    def _scan_network(self, target: str) -> List[Vulnerability]:
        """네트워크 스캔"""
        vulnerabilities = []
        
        try:
            # Nmap 스캔
            nm = nmap.PortScanner()
            nm.scan(target, arguments='-sS -sV -O --script vuln')
            
            for host in nm.all_hosts():
                for proto in nm[host].all_protocols():
                    ports = nm[host][proto].keys()
                    
                    for port in ports:
                        service = nm[host][proto][port]
                        
                        # 열린 포트 확인
                        if service['state'] == 'open':
                            # 불필요한 포트 확인
                            if port in [21, 23, 3389]:  # FTP, Telnet, RDP
                                vulnerabilities.append(Vulnerability(
                                    id=f"net_{host}_{port}_{int(time.time())}",
                                    title=f'Unnecessary Port Open: {port}',
                                    description=f'불필요한 포트 {port}가 열려있습니다.',
                                    level='medium',
                                    scan_type='network',
                                    target=f'{host}:{port}',
                                    details={'service': service.get('name', 'unknown')},
                                    cve_id=None,
                                    cvss_score=None,
                                    remediation=f'포트 {port}를 닫거나 방화벽에서 차단하세요.',
                                    discovered_at=datetime.now().isoformat(),
                                    status='open'
                                ))
                        
                        # 서비스 버전 정보 노출
                        if 'version' in service and service['version']:
                            vulnerabilities.append(Vulnerability(
                                id=f"net_{host}_{port}_version_{int(time.time())}",
                                title='Service Version Disclosure',
                                description=f'서비스 버전 정보가 노출되고 있습니다: {service["version"]}',
                                level='low',
                                scan_type='network',
                                target=f'{host}:{port}',
                                details={'service': service.get('name', 'unknown'), 'version': service['version']},
                                cve_id=None,
                                cvss_score=None,
                                remediation='서비스 버전 정보를 숨기거나 일반화하세요.',
                                discovered_at=datetime.now().isoformat(),
                                status='open'
                            ))
            
        except Exception as e:
            logger.error(f"네트워크 스캔 실패: {e}")
        
        return vulnerabilities
    
    def _scan_web(self, target: str) -> List[Vulnerability]:
        """웹 애플리케이션 스캔"""
        vulnerabilities = []
        
        try:
            # 기본 보안 헤더 확인
            headers = self._check_security_headers(target)
            
            # HTTPS 확인
            if not target.startswith('https://'):
                vulnerabilities.append(Vulnerability(
                    id=f"web_{hashlib.md5(target.encode()).hexdigest()}_https_{int(time.time())}",
                    title='HTTPS Not Used',
                    description='HTTPS가 사용되지 않고 있습니다.',
                    level='high',
                    scan_type='web',
                    target=target,
                    details={'protocol': 'http'},
                    cve_id=None,
                    cvss_score=7.5,
                    remediation='HTTPS를 사용하도록 설정하세요.',
                    discovered_at=datetime.now().isoformat(),
                    status='open'
                ))
            
            # 보안 헤더 누락 확인
            for header, required in headers.items():
                if not required['present']:
                    vulnerabilities.append(Vulnerability(
                        id=f"web_{hashlib.md5(target.encode()).hexdigest()}_{header}_{int(time.time())}",
                        title=f'Missing Security Header: {header}',
                        description=f'보안 헤더 {header}가 누락되었습니다.',
                        level=required['level'],
                        scan_type='web',
                        target=target,
                        details={'header': header, 'recommended_value': required.get('recommended_value')},
                        cve_id=None,
                        cvss_score=required.get('cvss_score'),
                        remediation=required.get('remediation', f'{header} 헤더를 추가하세요.'),
                        discovered_at=datetime.now().isoformat(),
                        status='open'
                    ))
            
            # 취약점 패턴 스캔
            pattern_vulns = self._scan_vulnerability_patterns(target)
            vulnerabilities.extend(pattern_vulns)
            
        except Exception as e:
            logger.error(f"웹 스캔 실패: {e}")
        
        return vulnerabilities
    
    def _check_security_headers(self, target: str) -> Dict[str, Dict[str, Any]]:
        """보안 헤더 확인"""
        try:
            response = requests.get(target, headers=self.config['custom_headers'], 
                                  timeout=self.config['scan_timeout'])
            
            headers = response.headers
            
            return {
                'X-Content-Type-Options': {
                    'present': 'X-Content-Type-Options' in headers,
                    'level': 'medium',
                    'recommended_value': 'nosniff',
                    'remediation': 'X-Content-Type-Options: nosniff 헤더를 추가하세요.',
                    'cvss_score': 4.3
                },
                'X-Frame-Options': {
                    'present': 'X-Frame-Options' in headers,
                    'level': 'medium',
                    'recommended_value': 'DENY',
                    'remediation': 'X-Frame-Options: DENY 헤더를 추가하세요.',
                    'cvss_score': 4.3
                },
                'X-XSS-Protection': {
                    'present': 'X-XSS-Protection' in headers,
                    'level': 'low',
                    'recommended_value': '1; mode=block',
                    'remediation': 'X-XSS-Protection: 1; mode=block 헤더를 추가하세요.',
                    'cvss_score': 3.1
                },
                'Strict-Transport-Security': {
                    'present': 'Strict-Transport-Security' in headers,
                    'level': 'high',
                    'recommended_value': 'max-age=31536000; includeSubDomains',
                    'remediation': 'Strict-Transport-Security 헤더를 추가하세요.',
                    'cvss_score': 7.5
                },
                'Content-Security-Policy': {
                    'present': 'Content-Security-Policy' in headers,
                    'level': 'medium',
                    'recommended_value': "default-src 'self'",
                    'remediation': 'Content-Security-Policy 헤더를 추가하세요.',
                    'cvss_score': 4.3
                }
            }
            
        except Exception as e:
            logger.error(f"보안 헤더 확인 실패: {e}")
            return {}
    
    def _scan_vulnerability_patterns(self, target: str) -> List[Vulnerability]:
        """취약점 패턴 스캔"""
        vulnerabilities = []
        
        try:
            # 테스트 페이로드
            test_payloads = [
                "' OR '1'='1",  # SQL Injection
                "<script>alert('XSS')</script>",  # XSS
                "admin'--",  # SQL Injection
                "javascript:alert('XSS')",  # XSS
            ]
            
            for payload in test_payloads:
                # GET 요청 테스트
                test_url = f"{target}?test={payload}"
                try:
                    response = requests.get(test_url, headers=self.config['custom_headers'],
                                          timeout=10, allow_redirects=False)
                    
                    # 응답에서 취약점 패턴 확인
                    for vuln_type, patterns in self.vulnerability_patterns.items():
                        for pattern in patterns:
                            if re.search(pattern['pattern'], response.text, re.IGNORECASE):
                                vulnerabilities.append(Vulnerability(
                                    id=f"web_{hashlib.md5(test_url.encode()).hexdigest()}_{vuln_type}_{int(time.time())}",
                                    title=pattern['title'],
                                    description=pattern['description'],
                                    level=pattern['level'],
                                    scan_type='web',
                                    target=test_url,
                                    details={'payload': payload, 'response_length': len(response.text)},
                                    cve_id=None,
                                    cvss_score=None,
                                    remediation='입력 검증 및 출력 인코딩을 강화하세요.',
                                    discovered_at=datetime.now().isoformat(),
                                    status='open'
                                ))
                
                except Exception as e:
                    logger.debug(f"패턴 스캔 실패 {test_url}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"취약점 패턴 스캔 실패: {e}")
        
        return vulnerabilities
    
    def _scan_database(self, target: str) -> List[Vulnerability]:
        """데이터베이스 스캔"""
        vulnerabilities = []
        
        try:
            # 데이터베이스 연결 설정 확인
            # 실제 구현에서는 데이터베이스 연결 정보를 사용
            db_config = {
                'host': 'localhost',
                'port': 5432,
                'database': 'test_db'
            }
            
            # 기본 인증 확인
            vulnerabilities.append(Vulnerability(
                id=f"db_{hashlib.md5(target.encode()).hexdigest()}_auth_{int(time.time())}",
                title='Weak Database Authentication',
                description='데이터베이스 인증이 약합니다.',
                level='high',
                scan_type='database',
                target=target,
                details={'auth_method': 'password'},
                cve_id=None,
                cvss_score=8.0,
                remediation='강력한 인증 방식을 사용하세요.',
                discovered_at=datetime.now().isoformat(),
                status='open'
            ))
            
        except Exception as e:
            logger.error(f"데이터베이스 스캔 실패: {e}")
        
        return vulnerabilities
    
    def _scan_configuration(self, target: str) -> List[Vulnerability]:
        """설정 스캔"""
        vulnerabilities = []
        
        try:
            # 환경 변수 확인
            sensitive_env_vars = ['SECRET_KEY', 'DATABASE_PASSWORD', 'API_KEY']
            
            for var in sensitive_env_vars:
                if var in self.config:
                    vulnerabilities.append(Vulnerability(
                        id=f"config_{var}_{int(time.time())}",
                        title=f'Sensitive Configuration Exposed: {var}',
                        description=f'민감한 설정 {var}가 노출되어 있습니다.',
                        level='high',
                        scan_type='configuration',
                        target=target,
                        details={'config_var': var},
                        cve_id=None,
                        cvss_score=7.5,
                        remediation=f'{var}를 환경 변수로 관리하세요.',
                        discovered_at=datetime.now().isoformat(),
                        status='open'
                    ))
            
            # 로그 레벨 확인
            if self.config.get('log_level', 'INFO') == 'DEBUG':
                vulnerabilities.append(Vulnerability(
                    id=f"config_log_level_{int(time.time())}",
                    title='Debug Logging Enabled',
                    description='디버그 로깅이 활성화되어 있습니다.',
                    level='medium',
                    scan_type='configuration',
                    target=target,
                    details={'log_level': 'DEBUG'},
                    cve_id=None,
                    cvss_score=4.3,
                    remediation='프로덕션 환경에서는 INFO 레벨 이상을 사용하세요.',
                    discovered_at=datetime.now().isoformat(),
                    status='open'
                ))
            
        except Exception as e:
            logger.error(f"설정 스캔 실패: {e}")
        
        return vulnerabilities
    
    def _scan_dependencies(self, target: str) -> List[Vulnerability]:
        """의존성 스캔"""
        vulnerabilities = []
        
        try:
            # requirements.txt 또는 package.json 확인
            # 실제 구현에서는 의존성 파일을 파싱하여 알려진 취약점 확인
            
            # 예시 취약점
            vulnerabilities.append(Vulnerability(
                id=f"dep_outdated_{int(time.time())}",
                title='Outdated Dependencies',
                description='오래된 의존성이 사용되고 있습니다.',
                level='medium',
                scan_type='dependency',
                target=target,
                details={'dependency': 'example-package', 'current_version': '1.0.0', 'latest_version': '2.0.0'},
                cve_id=None,
                cvss_score=5.0,
                remediation='의존성을 최신 버전으로 업데이트하세요.',
                discovered_at=datetime.now().isoformat(),
                status='open'
            ))
            
        except Exception as e:
            logger.error(f"의존성 스캔 실패: {e}")
        
        return vulnerabilities
    
    def start_scan(self, scan_type: str, target: str, config: Dict[str, Any] = None) -> str:
        """스캔 시작"""
        try:
            scan_id = f"scan_{scan_type}_{int(time.time())}_{hashlib.md5(target.encode()).hexdigest()[:8]}"
            
            scan_task = {
                'scan_id': scan_id,
                'scan_type': scan_type,
                'target': target,
                'config': config or {}
            }
            
            # 스캔 큐에 추가
            with self.scan_lock:
                self.scan_queue.append(scan_task)
                self.active_scans[scan_id] = scan_task
            
            # 초기 상태 저장
            self._save_scan_result(scan_id, scan_type, target, datetime.now(), None, [], 
                                 {'status': 'queued'})
            
            logger.info(f"스캔 시작: {scan_id} ({scan_type} - {target})")
            return scan_id
            
        except Exception as e:
            logger.error(f"스캔 시작 실패: {e}")
            raise
    
    def get_scan_status(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """스캔 상태 조회"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM scan_results WHERE scan_id = ?', (scan_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            columns = [description[0] for description in cursor.description]
            result = dict(zip(columns, row))
            
            if result.get('vulnerabilities'):
                result['vulnerabilities'] = json.loads(result['vulnerabilities'])
            if result.get('summary'):
                result['summary'] = json.loads(result['summary'])
            if result.get('scan_config'):
                result['scan_config'] = json.loads(result['scan_config'])
            
            return result
            
        except Exception as e:
            logger.error(f"스캔 상태 조회 실패: {e}")
            return None
    
    def _update_scan_status(self, scan_id: str, status: str):
        """스캔 상태 업데이트"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE scan_results 
                SET status = ?, end_time = ? 
                WHERE scan_id = ?
            ''', (status, datetime.now().isoformat(), scan_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"스캔 상태 업데이트 실패: {e}")
    
    def _save_scan_result(self, scan_id: str, scan_type: str, target: str, 
                         start_time: datetime, end_time: Optional[datetime],
                         vulnerabilities: List[Vulnerability], summary: Dict[str, Any]):
        """스캔 결과 저장"""
        try:
            # 취약점 저장
            for vuln in vulnerabilities:
                self._save_vulnerability(vuln)
            
            # 스캔 결과 저장
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO scan_results 
                (scan_id, scan_type, target, start_time, end_time, status, 
                 vulnerabilities, summary, scan_config)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scan_id, scan_type, target, start_time.isoformat(),
                end_time.isoformat() if end_time else None,
                'completed' if end_time else 'running',
                json.dumps([asdict(v) for v in vulnerabilities]),
                json.dumps(summary),
                json.dumps(self.config)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"스캔 결과 저장 실패: {e}")
    
    def _save_vulnerability(self, vulnerability: Vulnerability):
        """취약점 저장"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO vulnerabilities 
                (id, title, description, level, scan_type, target, details,
                 cve_id, cvss_score, remediation, discovered_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vulnerability.id, vulnerability.title, vulnerability.description,
                vulnerability.level, vulnerability.scan_type, vulnerability.target,
                json.dumps(vulnerability.details), vulnerability.cve_id,
                vulnerability.cvss_score, vulnerability.remediation,
                vulnerability.discovered_at, vulnerability.status
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"취약점 저장 실패: {e}")
    
    def _trigger_scan_alerts(self, scan_id: str, vulnerabilities: List[Vulnerability]):
        """스캔 알림 트리거"""
        try:
            # 높은 위험도 취약점 필터링
            high_risk_vulns = [v for v in vulnerabilities if v.level in ['high', 'critical']]
            
            if high_risk_vulns:
                alert_data = {
                    'scan_id': scan_id,
                    'vulnerability_count': len(vulnerabilities),
                    'high_risk_count': len(high_risk_vulns),
                    'vulnerabilities': [asdict(v) for v in high_risk_vulns]
                }
                
                for callback in self.alert_callbacks:
                    try:
                        callback(alert_data)
                    except Exception as e:
                        logger.error(f"스캔 알림 콜백 실행 실패: {e}")
            
        except Exception as e:
            logger.error(f"스캔 알림 트리거 실패: {e}")
    
    def add_alert_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """알림 콜백 추가"""
        self.alert_callbacks.append(callback)
    
    def get_vulnerabilities(self, level: Optional[str] = None, 
                          scan_type: Optional[str] = None, 
                          status: str = 'open') -> List[Dict[str, Any]]:
        """취약점 조회"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            query = "SELECT * FROM vulnerabilities WHERE status = ?"
            params = [status]
            
            if level:
                query += " AND level = ?"
                params.append(level)
            
            if scan_type:
                query += " AND scan_type = ?"
                params.append(scan_type)
            
            query += " ORDER BY discovered_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            columns = [description[0] for description in cursor.description]
            vulnerabilities = []
            
            for row in rows:
                vuln = dict(zip(columns, row))
                if vuln.get('details'):
                    vuln['details'] = json.loads(vuln['details'])
                vulnerabilities.append(vuln)
            
            conn.close()
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"취약점 조회 실패: {e}")
            return []
    
    def update_vulnerability_status(self, vuln_id: str, status: str, notes: str = None) -> bool:
        """취약점 상태 업데이트"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE vulnerabilities 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, vuln_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"취약점 상태 업데이트: {vuln_id} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"취약점 상태 업데이트 실패: {e}")
            return False
    
    def generate_security_report(self, days: int = 30) -> Dict[str, Any]:
        """보안 리포트 생성"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            # 취약점 통계
            cursor.execute("""
                SELECT level, COUNT(*) FROM vulnerabilities 
                WHERE discovered_at >= ? GROUP BY level
            """, (start_date,))
            vuln_by_level = dict(cursor.fetchall())
            
            # 스캔 통계
            cursor.execute("""
                SELECT scan_type, COUNT(*) FROM scan_results 
                WHERE start_time >= ? GROUP BY scan_type
            """, (start_date,))
            scan_by_type = dict(cursor.fetchall())
            
            # 최근 취약점
            cursor.execute("""
                SELECT * FROM vulnerabilities 
                WHERE discovered_at >= ? 
                ORDER BY discovered_at DESC LIMIT 10
            """, (start_date,))
            
            recent_vulns = []
            for row in cursor.fetchall():
                columns = [description[0] for description in cursor.description]
                vuln = dict(zip(columns, row))
                if vuln.get('details'):
                    vuln['details'] = json.loads(vuln['details'])
                recent_vulns.append(vuln)
            
            conn.close()
            
            return {
                'report_period': f'{days}일',
                'generated_at': datetime.now().isoformat(),
                'vulnerabilities_by_level': vuln_by_level,
                'scans_by_type': scan_by_type,
                'recent_vulnerabilities': recent_vulns,
                'summary': {
                    'total_vulnerabilities': sum(vuln_by_level.values()),
                    'high_critical_count': vuln_by_level.get('high', 0) + vuln_by_level.get('critical', 0),
                    'total_scans': sum(scan_by_type.values())
                }
            }
            
        except Exception as e:
            logger.error(f"보안 리포트 생성 실패: {e}")
            return {}

# 전역 보안 스캐너 인스턴스
security_scanner = SecurityScanner() 