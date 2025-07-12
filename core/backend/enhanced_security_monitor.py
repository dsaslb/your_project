"""
고도화된 플러그인 보안 모니터링 시스템
- 취약점 스캔, 악성코드 감지, 권한 모니터링, 보안 이벤트 추적, 자동 대응
"""

import logging
import json
import os
import hashlib
import re
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from collections import defaultdict
import subprocess
import tempfile
import shutil

logger = logging.getLogger(__name__)

@dataclass
class SecurityVulnerability:
    """보안 취약점 정보"""
    id: str
    plugin_id: str
    severity: str  # critical, high, medium, low, info
    title: str
    description: str
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    affected_component: str = ""
    remediation: str = ""
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "open"  # open, fixed, false_positive
    false_positive_reason: str = ""

@dataclass
class MalwareDetection:
    """악성코드 감지 정보"""
    id: str
    plugin_id: str
    file_path: str
    malware_type: str  # trojan, virus, spyware, ransomware, etc.
    signature: str
    confidence: float  # 0.0 - 1.0
    description: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "detected"  # detected, quarantined, removed, false_positive

@dataclass
class SecurityEvent:
    """보안 이벤트 정보"""
    id: str
    plugin_id: str
    event_type: str  # unauthorized_access, privilege_escalation, data_exfiltration, etc.
    severity: str  # critical, high, medium, low, info
    description: str
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolution_notes: str = ""

@dataclass
class PluginSecurityProfile:
    """플러그인 보안 프로필"""
    plugin_id: str
    risk_level: str  # low, medium, high, critical
    last_scan: datetime = field(default_factory=datetime.utcnow)
    vulnerabilities_count: int = 0
    malware_count: int = 0
    security_events_count: int = 0
    permissions: List[str] = field(default_factory=list)
    network_access: List[str] = field(default_factory=list)
    file_access: List[str] = field(default_factory=list)
    api_calls: List[str] = field(default_factory=list)
    security_score: float = 100.0  # 0-100
    compliance_status: str = "unknown"  # compliant, non_compliant, unknown

class EnhancedSecurityMonitor:
    """고도화된 플러그인 보안 모니터링 시스템"""
    
    def __init__(self, db_path: str = "security_monitor.db", plugins_dir: str = "plugins"):
        self.db_path = db_path
        self.plugins_dir = Path(plugins_dir)
        self.scan_interval = 3600  # 1시간마다 스캔
        self.monitoring_active = False
        self.scan_thread = None
        
        # 보안 규칙 및 시그니처
        self.malware_signatures = [
            r"eval\s*\(",
            r"exec\s*\(",
            r"system\s*\(",
            r"subprocess\.call",
            r"os\.system",
            r"__import__\s*\(",
            r"getattr\s*\(\s*__builtins__",
            r"file\s*\(",
            r"open\s*\(\s*['\"]/etc/passwd",
            r"requests\.get\s*\(\s*['\"]http://",
            r"urllib\.request\.urlopen",
            r"base64\.b64decode",
            r"pickle\.loads",
            r"marshal\.loads",
            r"yaml\.load\s*\(",
            r"json\.loads\s*\(\s*requests\.get",
        ]
        
        self.suspicious_patterns = [
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"api_key\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]",
            r"token\s*=\s*['\"][^'\"]+['\"]",
            r"\.env",
            r"config\.json",
            r"database\.sqlite",
            r"\.git",
            r"\.ssh",
        ]
        
        self.privileged_operations = [
            "os.remove", "os.rmdir", "shutil.rmtree",
            "subprocess.Popen", "subprocess.run",
            "open", "file",
            "import", "__import__",
            "eval", "exec", "compile",
            "getattr", "setattr", "delattr",
            "globals", "locals",
        ]
        
        self._init_database()
        self._load_security_rules()
    
    def _init_database(self):
        """보안 모니터링 데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 취약점 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    id TEXT PRIMARY KEY,
                    plugin_id TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    cve_id TEXT,
                    cvss_score REAL,
                    affected_component TEXT,
                    remediation TEXT,
                    discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'open',
                    false_positive_reason TEXT
                )
            ''')
            
            # 악성코드 감지 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS malware_detections (
                    id TEXT PRIMARY KEY,
                    plugin_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    malware_type TEXT NOT NULL,
                    signature TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    description TEXT NOT NULL,
                    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'detected'
                )
            ''')
            
            # 보안 이벤트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    id TEXT PRIMARY KEY,
                    plugin_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT NOT NULL,
                    source_ip TEXT,
                    user_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolution_notes TEXT
                )
            ''')
            
            # 플러그인 보안 프로필 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plugin_security_profiles (
                    plugin_id TEXT PRIMARY KEY,
                    risk_level TEXT DEFAULT 'unknown',
                    last_scan DATETIME DEFAULT CURRENT_TIMESTAMP,
                    vulnerabilities_count INTEGER DEFAULT 0,
                    malware_count INTEGER DEFAULT 0,
                    security_events_count INTEGER DEFAULT 0,
                    permissions TEXT,
                    network_access TEXT,
                    file_access TEXT,
                    api_calls TEXT,
                    security_score REAL DEFAULT 100.0,
                    compliance_status TEXT DEFAULT 'unknown'
                )
            ''')
            
            # 보안 스캔 이력 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    scan_type TEXT NOT NULL,
                    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    status TEXT DEFAULT 'running',
                    findings_count INTEGER DEFAULT 0,
                    scan_duration REAL DEFAULT 0.0
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vulns_plugin ON vulnerabilities(plugin_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vulns_severity ON vulnerabilities(severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_malware_plugin ON malware_detections(plugin_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_plugin ON security_events(plugin_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON security_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scans_plugin ON security_scans(plugin_id)')
            
            conn.commit()
            conn.close()
            logger.info("보안 모니터링 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"보안 모니터링 데이터베이스 초기화 오류: {e}")
    
    def _load_security_rules(self):
        """보안 규칙 로드"""
        try:
            # 추가 보안 규칙을 파일에서 로드할 수 있음
            rules_file = Path("security_rules.json")
            if rules_file.exists():
                with open(rules_file, 'r', encoding='utf-8') as f:
                    rules = json.load(f)
                    self.malware_signatures.extend(rules.get('malware_signatures', []))
                    self.suspicious_patterns.extend(rules.get('suspicious_patterns', []))
                    self.privileged_operations.extend(rules.get('privileged_operations', []))
            
            logger.info(f"보안 규칙 로드 완료 - 악성코드 시그니처: {len(self.malware_signatures)}, 의심 패턴: {len(self.suspicious_patterns)}")
            
        except Exception as e:
            logger.error(f"보안 규칙 로드 오류: {e}")
    
    def start_monitoring(self):
        """보안 모니터링 시작"""
        if self.monitoring_active:
            logger.warning("보안 모니터링이 이미 실행 중입니다.")
            return False
        
        try:
            self.monitoring_active = True
            self.scan_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.scan_thread.start()
            logger.info("보안 모니터링 시작")
            return True
            
        except Exception as e:
            logger.error(f"보안 모니터링 시작 실패: {e}")
            self.monitoring_active = False
            return False
    
    def stop_monitoring(self):
        """보안 모니터링 중지"""
        self.monitoring_active = False
        if self.scan_thread:
            self.scan_thread.join(timeout=5)
        logger.info("보안 모니터링 중지")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                # 모든 플러그인에 대해 보안 스캔 실행
                self.scan_all_plugins()
                time.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기
    
    def scan_all_plugins(self):
        """모든 플러그인 보안 스캔"""
        try:
            plugin_dirs = [d for d in self.plugins_dir.iterdir() if d.is_dir()]
            
            for plugin_dir in plugin_dirs:
                plugin_id = plugin_dir.name
                try:
                    self.scan_plugin(plugin_id)
                except Exception as e:
                    logger.error(f"플러그인 {plugin_id} 스캔 오류: {e}")
                    
        except Exception as e:
            logger.error(f"전체 플러그인 스캔 오류: {e}")
    
    def scan_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """개별 플러그인 보안 스캔"""
        scan_start = time.time()
        scan_id = f"{plugin_id}_{int(scan_start)}"
        
        try:
            # 스캔 시작 기록
            self._record_scan_start(scan_id, plugin_id, "comprehensive")
            
            plugin_dir = self.plugins_dir / plugin_id
            if not plugin_dir.exists():
                raise FileNotFoundError(f"플러그인 디렉토리를 찾을 수 없습니다: {plugin_id}")
            
            findings = {
                'vulnerabilities': [],
                'malware_detections': [],
                'security_events': [],
                'risk_assessment': {}
            }
            
            # 1. 코드 취약점 스캔
            vulnerabilities = self._scan_vulnerabilities(plugin_id, plugin_dir)
            findings['vulnerabilities'] = vulnerabilities
            
            # 2. 악성코드 감지
            malware_detections = self._scan_malware(plugin_id, plugin_dir)
            findings['malware_detections'] = malware_detections
            
            # 3. 권한 및 접근 분석
            security_events = self._analyze_permissions(plugin_id, plugin_dir)
            findings['security_events'] = security_events
            
            # 4. 위험도 평가
            risk_assessment = self._assess_risk(plugin_id, vulnerabilities, malware_detections, security_events)
            findings['risk_assessment'] = risk_assessment
            
            # 5. 보안 프로필 업데이트
            self._update_security_profile(plugin_id, findings)
            
            # 스캔 완료 기록
            scan_duration = time.time() - scan_start
            self._record_scan_complete(scan_id, len(vulnerabilities) + len(malware_detections), scan_duration)
            
            logger.info(f"플러그인 {plugin_id} 보안 스캔 완료 - 취약점: {len(vulnerabilities)}, 악성코드: {len(malware_detections)}")
            return findings
            
        except Exception as e:
            logger.error(f"플러그인 {plugin_id} 스캔 실패: {e}")
            self._record_scan_error(scan_id, str(e))
            return {'error': str(e)}
    
    def _scan_vulnerabilities(self, plugin_id: str, plugin_dir: Path) -> List[SecurityVulnerability]:
        """취약점 스캔"""
        vulnerabilities = []
        
        try:
            # Python 파일 스캔
            python_files = list(plugin_dir.rglob("*.py"))
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                    
                    # 각 라인에서 취약점 패턴 검사
                    for line_num, line in enumerate(lines, 1):
                        # SQL 인젝션 취약점
                        if re.search(r"execute\s*\(\s*['\"].*\+.*['\"]", line):
                            vuln = SecurityVulnerability(
                                id=f"{plugin_id}_sql_injection_{line_num}",
                                plugin_id=plugin_id,
                                severity="high",
                                title="SQL Injection 취약점",
                                description=f"파일 {py_file.name}의 {line_num}번째 라인에서 SQL 인젝션 취약점이 발견되었습니다.",
                                affected_component=str(py_file),
                                remediation="매개변수화된 쿼리 사용을 권장합니다."
                            )
                            vulnerabilities.append(vuln)
                        
                        # 명령어 인젝션 취약점
                        if re.search(r"subprocess\.(call|run|Popen)\s*\(\s*['\"].*\+.*['\"]", line):
                            vuln = SecurityVulnerability(
                                id=f"{plugin_id}_command_injection_{line_num}",
                                plugin_id=plugin_id,
                                severity="critical",
                                title="명령어 인젝션 취약점",
                                description=f"파일 {py_file.name}의 {line_num}번째 라인에서 명령어 인젝션 취약점이 발견되었습니다.",
                                affected_component=str(py_file),
                                remediation="사용자 입력 검증 및 화이트리스트 기반 명령어 실행을 권장합니다."
                            )
                            vulnerabilities.append(vuln)
                        
                        # 경로 순회 취약점
                        if re.search(r"open\s*\(\s*['\"].*\.\./", line):
                            vuln = SecurityVulnerability(
                                id=f"{plugin_id}_path_traversal_{line_num}",
                                plugin_id=plugin_id,
                                severity="high",
                                title="경로 순회 취약점",
                                description=f"파일 {py_file.name}의 {line_num}번째 라인에서 경로 순회 취약점이 발견되었습니다.",
                                affected_component=str(py_file),
                                remediation="절대 경로 검증 및 경로 정규화를 권장합니다."
                            )
                            vulnerabilities.append(vuln)
                        
                        # 하드코딩된 비밀번호
                        if re.search(r"password\s*=\s*['\"][^'\"]{8,}['\"]", line):
                            vuln = SecurityVulnerability(
                                id=f"{plugin_id}_hardcoded_password_{line_num}",
                                plugin_id=plugin_id,
                                severity="medium",
                                title="하드코딩된 비밀번호",
                                description=f"파일 {py_file.name}의 {line_num}번째 라인에서 하드코딩된 비밀번호가 발견되었습니다.",
                                affected_component=str(py_file),
                                remediation="환경 변수나 설정 파일을 통한 비밀번호 관리를 권장합니다."
                            )
                            vulnerabilities.append(vuln)
                        
                        # 안전하지 않은 직렬화
                        if re.search(r"pickle\.loads\s*\(", line):
                            vuln = SecurityVulnerability(
                                id=f"{plugin_id}_unsafe_deserialization_{line_num}",
                                plugin_id=plugin_id,
                                severity="high",
                                title="안전하지 않은 역직렬화",
                                description=f"파일 {py_file.name}의 {line_num}번째 라인에서 안전하지 않은 역직렬화가 발견되었습니다.",
                                affected_component=str(py_file),
                                remediation="JSON이나 다른 안전한 직렬화 방식을 사용하거나 신뢰할 수 있는 소스에서만 역직렬화를 수행하세요."
                            )
                            vulnerabilities.append(vuln)
                
                except Exception as e:
                    logger.error(f"파일 {py_file} 스캔 오류: {e}")
            
            # 취약점을 데이터베이스에 저장
            for vuln in vulnerabilities:
                self._save_vulnerability(vuln)
            
        except Exception as e:
            logger.error(f"취약점 스캔 오류: {e}")
        
        return vulnerabilities
    
    def _scan_malware(self, plugin_id: str, plugin_dir: Path) -> List[MalwareDetection]:
        """악성코드 감지"""
        malware_detections = []
        
        try:
            # 모든 파일 스캔
            all_files = list(plugin_dir.rglob("*"))
            
            for file_path in all_files:
                if file_path.is_file():
                    try:
                        # 텍스트 파일인 경우 내용 스캔
                        if file_path.suffix in ['.py', '.js', '.html', '.txt', '.json', '.xml']:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            # 악성코드 시그니처 검사
                            for signature in self.malware_signatures:
                                if re.search(signature, content, re.IGNORECASE):
                                    malware_type = self._classify_malware(signature)
                                    confidence = self._calculate_confidence(signature, content)
                                    
                                    detection = MalwareDetection(
                                        id=f"{plugin_id}_malware_{len(malware_detections)}",
                                        plugin_id=plugin_id,
                                        file_path=str(file_path),
                                        malware_type=malware_type,
                                        signature=signature,
                                        confidence=confidence,
                                        description=f"파일 {file_path.name}에서 {malware_type} 악성코드가 감지되었습니다."
                                    )
                                    malware_detections.append(detection)
                        
                        # 바이너리 파일 해시 검사
                        elif file_path.suffix in ['.exe', '.dll', '.so', '.dylib']:
                            file_hash = self._calculate_file_hash(file_path)
                            if self._is_known_malware_hash(file_hash):
                                detection = MalwareDetection(
                                    id=f"{plugin_id}_malware_binary_{len(malware_detections)}",
                                    plugin_id=plugin_id,
                                    file_path=str(file_path),
                                    malware_type="trojan",
                                    signature=file_hash,
                                    confidence=0.9,
                                    description=f"파일 {file_path.name}이 알려진 악성코드 해시와 일치합니다."
                                )
                                malware_detections.append(detection)
                    
                    except Exception as e:
                        logger.error(f"파일 {file_path} 악성코드 스캔 오류: {e}")
            
            # 악성코드 감지를 데이터베이스에 저장
            for detection in malware_detections:
                self._save_malware_detection(detection)
            
        except Exception as e:
            logger.error(f"악성코드 스캔 오류: {e}")
        
        return malware_detections
    
    def _analyze_permissions(self, plugin_id: str, plugin_dir: Path) -> List[SecurityEvent]:
        """권한 및 접근 분석"""
        security_events = []
        
        try:
            # Python 파일에서 권한 관련 코드 분석
            python_files = list(plugin_dir.rglob("*.py"))
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                    
                    for line_num, line in enumerate(lines, 1):
                        # 파일 시스템 접근
                        if re.search(r"open\s*\(\s*['\"]/", line):
                            event = SecurityEvent(
                                id=f"{plugin_id}_file_access_{line_num}",
                                plugin_id=plugin_id,
                                event_type="file_access",
                                severity="medium",
                                description=f"파일 {py_file.name}의 {line_num}번째 라인에서 절대 경로 파일 접근이 발견되었습니다.",
                                source_ip="localhost"
                            )
                            security_events.append(event)
                        
                        # 네트워크 접근
                        if re.search(r"requests\.(get|post|put|delete)", line):
                            event = SecurityEvent(
                                id=f"{plugin_id}_network_access_{line_num}",
                                plugin_id=plugin_id,
                                event_type="network_access",
                                severity="low",
                                description=f"파일 {py_file.name}의 {line_num}번째 라인에서 네트워크 접근이 발견되었습니다.",
                                source_ip="localhost"
                            )
                            security_events.append(event)
                        
                        # 시스템 명령어 실행
                        if re.search(r"subprocess\.(call|run|Popen)", line):
                            event = SecurityEvent(
                                id=f"{plugin_id}_system_command_{line_num}",
                                plugin_id=plugin_id,
                                event_type="system_command",
                                severity="high",
                                description=f"파일 {py_file.name}의 {line_num}번째 라인에서 시스템 명령어 실행이 발견되었습니다.",
                                source_ip="localhost"
                            )
                            security_events.append(event)
                        
                        # 동적 코드 실행
                        if re.search(r"eval\s*\(", line):
                            event = SecurityEvent(
                                id=f"{plugin_id}_dynamic_execution_{line_num}",
                                plugin_id=plugin_id,
                                event_type="dynamic_execution",
                                severity="critical",
                                description=f"파일 {py_file.name}의 {line_num}번째 라인에서 동적 코드 실행이 발견되었습니다.",
                                source_ip="localhost"
                            )
                            security_events.append(event)
                
                except Exception as e:
                    logger.error(f"파일 {py_file} 권한 분석 오류: {e}")
            
            # 보안 이벤트를 데이터베이스에 저장
            for event in security_events:
                self._save_security_event(event)
            
        except Exception as e:
            logger.error(f"권한 분석 오류: {e}")
        
        return security_events
    
    def _assess_risk(self, plugin_id: str, vulnerabilities: List[SecurityVulnerability], 
                    malware_detections: List[MalwareDetection], 
                    security_events: List[SecurityEvent]) -> Dict[str, Any]:
        """위험도 평가"""
        risk_score = 100.0
        risk_level = "low"
        
        # 취약점 기반 점수 차감
        for vuln in vulnerabilities:
            if vuln.severity == "critical":
                risk_score -= 25
            elif vuln.severity == "high":
                risk_score -= 15
            elif vuln.severity == "medium":
                risk_score -= 10
            elif vuln.severity == "low":
                risk_score -= 5
        
        # 악성코드 기반 점수 차감
        for malware in malware_detections:
            risk_score -= malware.confidence * 30
        
        # 보안 이벤트 기반 점수 차감
        for event in security_events:
            if event.severity == "critical":
                risk_score -= 20
            elif event.severity == "high":
                risk_score -= 15
            elif event.severity == "medium":
                risk_score -= 10
            elif event.severity == "low":
                risk_score -= 5
        
        # 위험도 레벨 결정
        if risk_score <= 25:
            risk_level = "critical"
        elif risk_score <= 50:
            risk_level = "high"
        elif risk_score <= 75:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            'risk_score': max(0, risk_score),
            'risk_level': risk_level,
            'vulnerabilities_count': len(vulnerabilities),
            'malware_count': len(malware_detections),
            'security_events_count': len(security_events)
        }
    
    def _classify_malware(self, signature: str) -> str:
        """악성코드 분류"""
        if "eval" in signature or "exec" in signature:
            return "code_injection"
        elif "subprocess" in signature:
            return "command_execution"
        elif "requests" in signature or "urllib" in signature:
            return "network_communication"
        elif "base64" in signature:
            return "obfuscation"
        elif "pickle" in signature:
            return "deserialization_attack"
        else:
            return "suspicious_code"
    
    def _calculate_confidence(self, signature: str, content: str) -> float:
        """악성코드 감지 신뢰도 계산"""
        matches = len(re.findall(signature, content, re.IGNORECASE))
        if matches > 5:
            return 0.9
        elif matches > 2:
            return 0.7
        elif matches > 0:
            return 0.5
        return 0.0
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """파일 해시 계산"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _is_known_malware_hash(self, file_hash: str) -> bool:
        """알려진 악성코드 해시 확인 (실제로는 외부 데이터베이스 연동)"""
        # 샘플 악성 해시 (실제로는 VirusTotal API 등 사용)
        known_malware_hashes = [
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # 빈 파일
        ]
        return file_hash in known_malware_hashes
    
    def _save_vulnerability(self, vulnerability: SecurityVulnerability):
        """취약점 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO vulnerabilities 
                (id, plugin_id, severity, title, description, cve_id, cvss_score, 
                 affected_component, remediation, discovered_at, status, false_positive_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vulnerability.id, vulnerability.plugin_id, vulnerability.severity,
                vulnerability.title, vulnerability.description, vulnerability.cve_id,
                vulnerability.cvss_score, vulnerability.affected_component,
                vulnerability.remediation, vulnerability.discovered_at.isoformat(),
                vulnerability.status, vulnerability.false_positive_reason
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"취약점 저장 오류: {e}")
    
    def _save_malware_detection(self, detection: MalwareDetection):
        """악성코드 감지 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO malware_detections 
                (id, plugin_id, file_path, malware_type, signature, confidence, 
                 description, detected_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                detection.id, detection.plugin_id, detection.file_path,
                detection.malware_type, detection.signature, detection.confidence,
                detection.description, detection.detected_at.isoformat(), detection.status
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"악성코드 감지 저장 오류: {e}")
    
    def _save_security_event(self, event: SecurityEvent):
        """보안 이벤트 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO security_events 
                (id, plugin_id, event_type, severity, description, source_ip, 
                 user_id, timestamp, resolved, resolution_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.id, event.plugin_id, event.event_type, event.severity,
                event.description, event.source_ip, event.user_id,
                event.timestamp.isoformat(), event.resolved, event.resolution_notes
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"보안 이벤트 저장 오류: {e}")
    
    def _update_security_profile(self, plugin_id: str, findings: Dict[str, Any]):
        """보안 프로필 업데이트"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            risk_assessment = findings.get('risk_assessment', {})
            
            cursor.execute('''
                INSERT OR REPLACE INTO plugin_security_profiles 
                (plugin_id, risk_level, last_scan, vulnerabilities_count, malware_count,
                 security_events_count, security_score, compliance_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                plugin_id, risk_assessment.get('risk_level', 'unknown'),
                datetime.utcnow().isoformat(),
                risk_assessment.get('vulnerabilities_count', 0),
                risk_assessment.get('malware_count', 0),
                risk_assessment.get('security_events_count', 0),
                risk_assessment.get('risk_score', 100.0),
                'compliant' if risk_assessment.get('risk_score', 100) > 70 else 'non_compliant'
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"보안 프로필 업데이트 오류: {e}")
    
    def _record_scan_start(self, scan_id: str, plugin_id: str, scan_type: str):
        """스캔 시작 기록"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO security_scans 
                (id, plugin_id, scan_type, started_at, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (scan_id, plugin_id, scan_type, datetime.utcnow().isoformat(), 'running'))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"스캔 시작 기록 오류: {e}")
    
    def _record_scan_complete(self, scan_id: str, findings_count: int, duration: float):
        """스캔 완료 기록"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE security_scans 
                SET completed_at = ?, status = ?, findings_count = ?, scan_duration = ?
                WHERE id = ?
            ''', (datetime.utcnow().isoformat(), 'completed', findings_count, duration, scan_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"스캔 완료 기록 오류: {e}")
    
    def _record_scan_error(self, scan_id: str, error_message: str):
        """스캔 오류 기록"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE security_scans 
                SET completed_at = ?, status = ?
                WHERE id = ?
            ''', (datetime.utcnow().isoformat(), f'error: {error_message}', scan_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"스캔 오류 기록 실패: {e}")
    
    def get_security_summary(self) -> Dict[str, Any]:
        """보안 요약 정보 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 전체 통계
            cursor.execute('SELECT COUNT(*) FROM vulnerabilities WHERE status = "open"')
            open_vulnerabilities = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM malware_detections WHERE status = "detected"')
            active_malware = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM security_events WHERE resolved = FALSE')
            unresolved_events = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM plugin_security_profiles WHERE risk_level = "critical"')
            critical_plugins = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM plugin_security_profiles WHERE risk_level = "high"')
            high_risk_plugins = cursor.fetchone()[0]
            
            # 최근 보안 이벤트
            cursor.execute('''
                SELECT plugin_id, event_type, severity, description, timestamp
                FROM security_events 
                WHERE timestamp > datetime('now', '-24 hours')
                ORDER BY timestamp DESC
                LIMIT 10
            ''')
            recent_events = cursor.fetchall()
            
            conn.close()
            
            return {
                'open_vulnerabilities': open_vulnerabilities,
                'active_malware': active_malware,
                'unresolved_events': unresolved_events,
                'critical_plugins': critical_plugins,
                'high_risk_plugins': high_risk_plugins,
                'recent_events': recent_events
            }
            
        except Exception as e:
            logger.error(f"보안 요약 조회 오류: {e}")
            return {}

# 전역 인스턴스
enhanced_security_monitor = EnhancedSecurityMonitor() 