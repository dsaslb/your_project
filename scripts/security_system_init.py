#!/usr/bin/env python3
"""
보안 시스템 초기화 스크립트
고급 보안 및 암호화 시스템의 초기 설정을 수행합니다.
"""

import os
import sys
import logging
import sqlite3
import json
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 보안 모듈 import
from security.multi_factor_auth import MultiFactorAuth
from security.data_encryption import DataEncryption
from security.audit_logger import SecurityAuditLogger
from security.threat_detection import ThreatDetection

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/security_init.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SecuritySystemInitializer:
    """보안 시스템 초기화 클래스"""
    
    def __init__(self):
        self.project_root = project_root
        self.security_dir = project_root / 'security'
        self.data_dir = project_root / 'data' / 'security'
        self.logs_dir = project_root / 'logs'
        
        # 디렉토리 생성
        self.create_directories()
        
        # 보안 모듈 인스턴스
        self.mfa = MultiFactorAuth()
        self.encryption = DataEncryption()
        self.audit_logger = SecurityAuditLogger()
        self.threat_detection = ThreatDetection()
    
    def create_directories(self):
        """필요한 디렉토리들을 생성합니다."""
        directories = [
            self.security_dir,
            self.data_dir,
            self.logs_dir,
            self.data_dir / 'mfa',
            self.data_dir / 'encryption',
            self.data_dir / 'audit',
            self.data_dir / 'threats',
            self.data_dir / 'keys'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"디렉토리 생성: {directory}")
    
    def initialize_databases(self):
        """보안 시스템 데이터베이스들을 초기화합니다."""
        try:
            # MFA 데이터베이스 초기화
            self.mfa.initialize_database()
            logger.info("MFA 데이터베이스 초기화 완료")
            
            # 암호화 시스템 데이터베이스 초기화
            self.encryption.initialize_database()
            logger.info("암호화 시스템 데이터베이스 초기화 완료")
            
            # 감사 로그 데이터베이스 초기화
            self.audit_logger.initialize_database()
            logger.info("감사 로그 데이터베이스 초기화 완료")
            
            # 위협 탐지 데이터베이스 초기화
            self.threat_detection.initialize_database()
            logger.info("위협 탐지 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {str(e)}")
            raise
    
    def setup_default_configurations(self):
        """기본 보안 설정을 구성합니다."""
        try:
            # MFA 기본 설정
            mfa_config = {
                'totp_enabled': True,
                'sms_enabled': True,
                'email_enabled': True,
                'backup_codes_count': 10,
                'session_timeout': 3600,
                'max_attempts': 5,
                'lockout_duration': 1800
            }
            
            with open(self.data_dir / 'mfa' / 'config.json', 'w', encoding='utf-8') as f:
                json.dump(mfa_config, f, indent=2, ensure_ascii=False)
            
            logger.info("MFA 기본 설정 구성 완료")
            
            # 암호화 시스템 기본 설정
            encryption_config = {
                'symmetric_algorithm': 'Fernet',
                'asymmetric_algorithm': 'RSA',
                'key_rotation_days': 90,
                'password_hash_algorithm': 'PBKDF2',
                'password_hash_iterations': 100000,
                'token_expiry_hours': 24
            }
            
            with open(self.data_dir / 'encryption' / 'config.json', 'w', encoding='utf-8') as f:
                json.dump(encryption_config, f, indent=2, ensure_ascii=False)
            
            logger.info("암호화 시스템 기본 설정 구성 완료")
            
            # 감사 로그 기본 설정
            audit_config = {
                'log_retention_days': 365,
                'max_log_size_mb': 100,
                'compression_enabled': True,
                'alert_threshold': 10,
                'anomaly_detection_enabled': True,
                'risk_scoring_enabled': True
            }
            
            with open(self.data_dir / 'audit' / 'config.json', 'w', encoding='utf-8') as f:
                json.dump(audit_config, f, indent=2, ensure_ascii=False)
            
            logger.info("감사 로그 기본 설정 구성 완료")
            
            # 위협 탐지 기본 설정
            threat_config = {
                'sql_injection_detection': True,
                'xss_detection': True,
                'csrf_detection': True,
                'brute_force_detection': True,
                'ddos_detection': True,
                'rate_limiting_enabled': True,
                'auto_block_enabled': True,
                'block_duration_seconds': 3600,
                'alert_enabled': True
            }
            
            with open(self.data_dir / 'threats' / 'config.json', 'w', encoding='utf-8') as f:
                json.dump(threat_config, f, indent=2, ensure_ascii=False)
            
            logger.info("위협 탐지 기본 설정 구성 완료")
            
        except Exception as e:
            logger.error(f"기본 설정 구성 오류: {str(e)}")
            raise
    
    def generate_master_keys(self):
        """마스터 키들을 생성합니다."""
        try:
            # 암호화 마스터 키 생성
            master_key = self.encryption.generate_master_key()
            
            # RSA 키 쌍 생성
            private_key, public_key = self.encryption.generate_rsa_keys()
            
            # 키 저장
            keys_config = {
                'master_key_created': datetime.now().isoformat(),
                'rsa_keys_created': datetime.now().isoformat(),
                'key_rotation_schedule': '90_days'
            }
            
            with open(self.data_dir / 'keys' / 'keys_info.json', 'w', encoding='utf-8') as f:
                json.dump(keys_config, f, indent=2, ensure_ascii=False)
            
            logger.info("마스터 키 생성 완료")
            
        except Exception as e:
            logger.error(f"마스터 키 생성 오류: {str(e)}")
            raise
    
    def setup_default_users(self):
        """기본 보안 관리자 사용자를 설정합니다."""
        try:
            # 기본 관리자 MFA 설정 (예시)
            admin_user_id = 1
            mfa_result = self.mfa.setup_mfa(admin_user_id)
            
            if mfa_result['success']:
                logger.info(f"관리자 사용자 MFA 설정 완료: {admin_user_id}")
                
                # 감사 로그에 기록
                self.audit_logger.log_event(
                    event_type='system_initialization',
                    user_id=admin_user_id,
                    ip_address='127.0.0.1',
                    details="보안 시스템 초기화 완료"
                )
            else:
                logger.warning(f"관리자 MFA 설정 실패: {mfa_result['error']}")
            
        except Exception as e:
            logger.error(f"기본 사용자 설정 오류: {str(e)}")
            raise
    
    def create_sample_threat_patterns(self):
        """샘플 위협 패턴들을 생성합니다."""
        try:
            # SQL Injection 패턴
            sql_patterns = [
                "'; DROP TABLE users; --",
                "'; INSERT INTO users VALUES ('hacker', 'password'); --",
                "'; UPDATE users SET password='hacked'; --",
                "'; SELECT * FROM users WHERE id=1 OR 1=1; --"
            ]
            
            # XSS 패턴
            xss_patterns = [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')",
                "<svg onload=alert('XSS')>"
            ]
            
            # CSRF 패턴
            csrf_patterns = [
                "malicious-site.com/transfer?amount=1000",
                "evil.com/change-password",
                "attacker.com/delete-account"
            ]
            
            patterns = {
                'sql_injection': sql_patterns,
                'xss': xss_patterns,
                'csrf': csrf_patterns,
                'brute_force': ['admin', 'password', '123456', 'qwerty'],
                'ddos': ['flood', 'overload', 'excessive_requests']
            }
            
            with open(self.data_dir / 'threats' / 'patterns.json', 'w', encoding='utf-8') as f:
                json.dump(patterns, f, indent=2, ensure_ascii=False)
            
            logger.info("샘플 위협 패턴 생성 완료")
            
        except Exception as e:
            logger.error(f"위협 패턴 생성 오류: {str(e)}")
            raise
    
    def setup_monitoring(self):
        """보안 모니터링 시스템을 설정합니다."""
        try:
            # 위협 탐지 모니터링 시작
            self.threat_detection.start_monitoring()
            logger.info("위협 탐지 모니터링 시작")
            
            # 감사 로그 모니터링 설정
            self.audit_logger.start_monitoring()
            logger.info("감사 로그 모니터링 시작")
            
        except Exception as e:
            logger.error(f"모니터링 설정 오류: {str(e)}")
            raise
    
    def create_security_policies(self):
        """보안 정책들을 생성합니다."""
        try:
            policies = {
                'password_policy': {
                    'min_length': 8,
                    'require_uppercase': True,
                    'require_lowercase': True,
                    'require_numbers': True,
                    'require_special_chars': True,
                    'max_age_days': 90
                },
                'session_policy': {
                    'timeout_minutes': 30,
                    'max_concurrent_sessions': 3,
                    'force_logout_on_password_change': True
                },
                'mfa_policy': {
                    'required_for_admin': True,
                    'required_for_sensitive_operations': True,
                    'grace_period_days': 7
                },
                'data_encryption_policy': {
                    'encrypt_sensitive_data': True,
                    'encrypt_backups': True,
                    'encrypt_transmissions': True
                },
                'audit_policy': {
                    'log_all_authentication_events': True,
                    'log_all_data_access': True,
                    'log_all_configuration_changes': True,
                    'retention_period_days': 365
                }
            }
            
            with open(self.data_dir / 'policies.json', 'w', encoding='utf-8') as f:
                json.dump(policies, f, indent=2, ensure_ascii=False)
            
            logger.info("보안 정책 생성 완료")
            
        except Exception as e:
            logger.error(f"보안 정책 생성 오류: {str(e)}")
            raise
    
    def run_health_check(self):
        """보안 시스템 상태를 확인합니다."""
        try:
            health_status = {
                'mfa_system': self.mfa.is_healthy(),
                'encryption_system': self.encryption.is_healthy(),
                'audit_system': self.audit_logger.is_healthy(),
                'threat_detection_system': self.threat_detection.is_healthy(),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.data_dir / 'health_status.json', 'w', encoding='utf-8') as f:
                json.dump(health_status, f, indent=2, ensure_ascii=False)
            
            logger.info("보안 시스템 상태 확인 완료")
            
            # 상태 출력
            for system, status in health_status.items():
                if system != 'timestamp':
                    status_text = "정상" if status else "오류"
                    logger.info(f"{system}: {status_text}")
            
        except Exception as e:
            logger.error(f"상태 확인 오류: {str(e)}")
            raise
    
    def initialize(self):
        """전체 보안 시스템을 초기화합니다."""
        logger.info("보안 시스템 초기화를 시작합니다...")
        
        try:
            # 1. 데이터베이스 초기화
            logger.info("1. 데이터베이스 초기화 중...")
            self.initialize_databases()
            
            # 2. 기본 설정 구성
            logger.info("2. 기본 설정 구성 중...")
            self.setup_default_configurations()
            
            # 3. 마스터 키 생성
            logger.info("3. 마스터 키 생성 중...")
            self.generate_master_keys()
            
            # 4. 기본 사용자 설정
            logger.info("4. 기본 사용자 설정 중...")
            self.setup_default_users()
            
            # 5. 위협 패턴 생성
            logger.info("5. 위협 패턴 생성 중...")
            self.create_sample_threat_patterns()
            
            # 6. 보안 정책 생성
            logger.info("6. 보안 정책 생성 중...")
            self.create_security_policies()
            
            # 7. 모니터링 설정
            logger.info("7. 모니터링 설정 중...")
            self.setup_monitoring()
            
            # 8. 상태 확인
            logger.info("8. 시스템 상태 확인 중...")
            self.run_health_check()
            
            logger.info("보안 시스템 초기화가 완료되었습니다!")
            
        except Exception as e:
            logger.error(f"보안 시스템 초기화 실패: {str(e)}")
            raise

def main():
    """메인 함수"""
    try:
        initializer = SecuritySystemInitializer()
        initializer.initialize()
        
        print("\n" + "="*50)
        print("보안 시스템 초기화가 성공적으로 완료되었습니다!")
        print("="*50)
        print("\n다음 단계:")
        print("1. /admin/security 에서 보안 대시보드에 접속하세요")
        print("2. /api/security/security-status 에서 API 상태를 확인하세요")
        print("3. 보안 설정을 필요에 따라 조정하세요")
        print("\n주의사항:")
        print("- 생성된 키와 설정 파일을 안전하게 보관하세요")
        print("- 정기적으로 키 로테이션을 수행하세요")
        print("- 보안 로그를 모니터링하세요")
        
    except Exception as e:
        logger.error(f"초기화 실패: {str(e)}")
        print(f"\n오류: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 