from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# app import를 안전하게 처리
try:
    from app import db
except ImportError:
    # app이 없을 경우를 대비한 더미 db 객체
    class DummyDB:
        class Model:
            pass
    db = DummyDB()

class PluginPermission(db.Model):
    """플러그인 권한 설정 테이블"""
    __tablename__ = 'plugin_permissions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    
    # 데이터 접근 범위
    data_access = Column(JSON, default={
        'schedule': True,      # 스케줄 데이터 접근
        'employee': False,     # 직원 정보 접근
        'sales': False,        # 매출 데이터 접근
        'inventory': False,    # 재고 데이터 접근
        'reviews': False,      # 리뷰 데이터 접근
        'qsc': False,          # QSC 데이터 접근
        'contracts': False,    # 계약 데이터 접근
    })
    
    # API 사용 범위
    api_access = Column(JSON, default={
        'read': True,          # 읽기 API
        'write': False,        # 쓰기 API
        'delete': False,       # 삭제 API
        'admin': False,        # 관리자 API
        'external': False,     # 외부 API 호출
    })
    
    # 실행 제한
    execution_limits = Column(JSON, default={
        'max_execution_time': 30,    # 최대 실행시간 (초)
        'max_memory_mb': 512,        # 최대 메모리 사용량 (MB)
        'max_db_queries': 100,       # 최대 DB 쿼리 수
        'max_file_size_mb': 10,      # 최대 파일 크기 (MB)
        'allow_file_upload': False,  # 파일 업로드 허용
        'allow_network': False,      # 네트워크 접근 허용
    })
    
    # 샌드박스 설정
    sandbox_settings = Column(JSON, default={
        'isolated_environment': True,  # 격리된 실행 환경
        'readonly_filesystem': True,   # 읽기 전용 파일시스템
        'restricted_network': True,    # 제한된 네트워크
        'memory_limit': True,          # 메모리 제한
        'cpu_limit': True,             # CPU 제한
    })
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='permissions')

class PluginSecurityLog(db.Model):
    """플러그인 보안 로그 테이블"""
    __tablename__ = 'plugin_security_logs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # 보안 이벤트 타입
    event_type = Column(String(50), nullable=False)  # 'permission_violation', 'resource_limit', 'suspicious_activity'
    
    # 이벤트 상세 정보
    event_details = Column(JSON, default={})
    
    # 보안 레벨
    security_level = Column(String(20), default='info')  # 'info', 'warning', 'error', 'critical'
    
    # 처리 상태
    status = Column(String(20), default='pending')  # 'pending', 'reviewed', 'resolved', 'ignored'
    
    # 추가 정보
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='security_logs')
    user = relationship('User', backref='plugin_security_logs')

class PluginResourceUsage(db.Model):
    """플러그인 리소스 사용량 모니터링 테이블"""
    __tablename__ = 'plugin_resource_usage'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    installation_id = Column(Integer, ForeignKey('plugin_installations.id'))
    
    # 리소스 사용량
    cpu_usage_percent = Column(Integer, default=0)
    memory_usage_mb = Column(Integer, default=0)
    execution_time_seconds = Column(Integer, default=0)
    db_queries_count = Column(Integer, default=0)
    file_operations_count = Column(Integer, default=0)
    network_requests_count = Column(Integer, default=0)
    
    # 제한값
    cpu_limit_percent = Column(Integer, default=100)
    memory_limit_mb = Column(Integer, default=512)
    execution_time_limit_seconds = Column(Integer, default=30)
    db_queries_limit = Column(Integer, default=100)
    
    # 상태
    is_over_limit = Column(Boolean, default=False)
    is_suspended = Column(Boolean, default=False)
    
    # 모니터링 시간
    monitored_at = Column(DateTime, default=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='resource_usage')
    installation = relationship('PluginInstallation', backref='resource_usage')

class PluginWhitelist(db.Model):
    """플러그인 화이트리스트 테이블"""
    __tablename__ = 'plugin_whitelists'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    
    # 화이트리스트 타입
    whitelist_type = Column(String(50), nullable=False)  # 'api_endpoint', 'file_path', 'network_domain'
    
    # 허용된 값
    allowed_value = Column(String(255), nullable=False)
    
    # 설명
    description = Column(Text)
    
    # 활성화 상태
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='whitelists')

class PluginBlacklist(db.Model):
    """플러그인 블랙리스트 테이블"""
    __tablename__ = 'plugin_blacklists'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    
    # 블랙리스트 타입
    blacklist_type = Column(String(50), nullable=False)  # 'api_endpoint', 'file_path', 'network_domain', 'pattern'
    
    # 차단된 값
    blocked_value = Column(String(255), nullable=False)
    
    # 차단 사유
    reason = Column(Text)
    
    # 차단 레벨
    block_level = Column(String(20), default='warning')  # 'warning', 'error', 'critical'
    
    # 활성화 상태
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='blacklists') 