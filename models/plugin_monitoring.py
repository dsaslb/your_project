from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, ForeignKey, Text, Float
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

class PluginSystemStatus(db.Model):
    """플러그인 시스템 상태 테이블"""
    __tablename__ = 'plugin_system_status'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    
    # 시스템 전체 상태
    system_status = Column(String(20), default='healthy')  # 'healthy', 'warning', 'critical', 'maintenance'
    total_plugins = Column(Integer, default=0)
    active_plugins = Column(Integer, default=0)
    error_plugins = Column(Integer, default=0)
    
    # 성능 메트릭
    avg_response_time_ms = Column(Float, default=0.0)
    avg_cpu_usage_percent = Column(Float, default=0.0)
    avg_memory_usage_mb = Column(Float, default=0.0)
    total_api_calls = Column(Integer, default=0)
    error_rate_percent = Column(Float, default=0.0)
    
    # 리소스 사용량
    total_disk_usage_mb = Column(Float, default=0.0)
    total_memory_usage_mb = Column(Float, default=0.0)
    total_cpu_usage_percent = Column(Float, default=0.0)
    
    # 네트워크 상태
    network_latency_ms = Column(Float, default=0.0)
    network_throughput_mbps = Column(Float, default=0.0)
    
    # 업데이트 시간
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class PluginPerformanceMetrics(db.Model):
    """플러그인 성능 메트릭 테이블"""
    __tablename__ = 'plugin_performance_metrics'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    installation_id = Column(Integer, ForeignKey('plugin_installations.id'))
    
    # 성능 메트릭
    response_time_ms = Column(Float, default=0.0)
    cpu_usage_percent = Column(Float, default=0.0)
    memory_usage_mb = Column(Float, default=0.0)
    execution_time_seconds = Column(Float, default=0.0)
    
    # API 메트릭
    api_calls_count = Column(Integer, default=0)
    api_errors_count = Column(Integer, default=0)
    api_success_rate_percent = Column(Float, default=100.0)
    
    # 데이터베이스 메트릭
    db_queries_count = Column(Integer, default=0)
    db_query_time_ms = Column(Float, default=0.0)
    db_connections_count = Column(Integer, default=0)
    
    # 파일 시스템 메트릭
    file_operations_count = Column(Integer, default=0)
    file_read_bytes = Column(Integer, default=0)
    file_write_bytes = Column(Integer, default=0)
    
    # 네트워크 메트릭
    network_requests_count = Column(Integer, default=0)
    network_bytes_sent = Column(Integer, default=0)
    network_bytes_received = Column(Integer, default=0)
    
    # 측정 시간
    measured_at = Column(DateTime, default=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='performance_metrics')
    installation = relationship('PluginInstallation', backref='performance_metrics')

class PluginErrorLog(db.Model):
    """플러그인 오류 로그 테이블"""
    __tablename__ = 'plugin_error_logs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    installation_id = Column(Integer, ForeignKey('plugin_installations.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # 오류 정보
    error_type = Column(String(100), nullable=False)  # 'exception', 'timeout', 'permission_denied', 'resource_limit'
    error_message = Column(Text, nullable=False)
    error_stack_trace = Column(Text)
    error_code = Column(String(50))
    
    # 오류 컨텍스트
    error_context = Column(JSON, default={})  # 요청 정보, 파라미터, 환경 정보
    severity_level = Column(String(20), default='error')  # 'info', 'warning', 'error', 'critical'
    
    # 처리 상태
    is_resolved = Column(Boolean, default=False)
    resolution_notes = Column(Text)
    resolved_by = Column(Integer, ForeignKey('users.id'))
    resolved_at = Column(DateTime)
    
    # 발생 정보
    occurred_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    plugin = relationship('Plugin', backref='error_logs')
    installation = relationship('PluginInstallation', backref='error_logs')
    user = relationship('User', foreign_keys=[user_id], backref='plugin_error_logs')
    resolver = relationship('User', foreign_keys=[resolved_by], backref='resolved_plugin_errors')

class PluginHealthCheck(db.Model):
    """플러그인 헬스체크 테이블"""
    __tablename__ = 'plugin_health_checks'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    installation_id = Column(Integer, ForeignKey('plugin_installations.id'))
    
    # 헬스체크 결과
    health_status = Column(String(20), default='healthy')  # 'healthy', 'warning', 'unhealthy', 'unknown'
    response_time_ms = Column(Float, default=0.0)
    is_responding = Column(Boolean, default=True)
    
    # 체크 항목
    checks = Column(JSON, default={
        'api_endpoint': True,
        'database_connection': True,
        'file_system': True,
        'memory_usage': True,
        'cpu_usage': True,
        'plugin_functionality': True
    })
    
    # 상세 정보
    details = Column(JSON, default={})
    error_message = Column(Text)
    
    # 체크 시간
    checked_at = Column(DateTime, default=datetime.utcnow)
    next_check_at = Column(DateTime)
    
    plugin = relationship('Plugin', backref='health_checks')
    installation = relationship('PluginInstallation', backref='health_checks')

class PluginAlert(db.Model):
    """플러그인 알림 테이블"""
    __tablename__ = 'plugin_alerts'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    
    # 알림 정보
    alert_type = Column(String(50), nullable=False)  # 'performance', 'error', 'security', 'resource', 'health'
    alert_level = Column(String(20), default='warning')  # 'info', 'warning', 'error', 'critical'
    alert_title = Column(String(255), nullable=False)
    alert_message = Column(Text, nullable=False)
    
    # 알림 조건
    threshold_value = Column(Float)
    current_value = Column(Float)
    condition = Column(String(20))  # 'gt', 'lt', 'eq', 'gte', 'lte'
    
    # 알림 상태
    is_active = Column(Boolean, default=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, ForeignKey('users.id'))
    acknowledged_at = Column(DateTime)
    
    # 알림 설정
    notification_channels = Column(JSON, default=['email', 'dashboard'])  # 'email', 'sms', 'slack', 'dashboard'
    auto_resolve = Column(Boolean, default=False)
    auto_resolve_after_hours = Column(Integer, default=24)
    
    # 생성 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='alerts')
    user = relationship('User', backref='acknowledged_alerts')

class PluginMonitoringConfig(db.Model):
    """플러그인 모니터링 설정 테이블"""
    __tablename__ = 'plugin_monitoring_configs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    
    # 모니터링 활성화
    is_monitoring_enabled = Column(Boolean, default=True)
    monitoring_interval_seconds = Column(Integer, default=300)  # 5분
    
    # 성능 임계값
    max_response_time_ms = Column(Integer, default=5000)
    max_cpu_usage_percent = Column(Integer, default=80)
    max_memory_usage_mb = Column(Integer, default=512)
    max_error_rate_percent = Column(Float, default=5.0)
    
    # 헬스체크 설정
    health_check_enabled = Column(Boolean, default=True)
    health_check_interval_seconds = Column(Integer, default=60)
    health_check_timeout_seconds = Column(Integer, default=30)
    
    # 알림 설정
    alert_enabled = Column(Boolean, default=True)
    alert_channels = Column(JSON, default=['email', 'dashboard'])
    alert_cooldown_minutes = Column(Integer, default=30)
    
    # 로깅 설정
    log_level = Column(String(20), default='info')  # 'debug', 'info', 'warning', 'error'
    log_retention_days = Column(Integer, default=30)
    
    # 자동 조치
    auto_restart_on_failure = Column(Boolean, default=False)
    auto_rollback_on_critical = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='monitoring_config')

class PluginSystemLog(db.Model):
    """플러그인 시스템 로그 테이블"""
    __tablename__ = 'plugin_system_logs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    
    # 로그 정보
    log_level = Column(String(20), default='info')  # 'debug', 'info', 'warning', 'error', 'critical'
    log_message = Column(Text, nullable=False)
    log_source = Column(String(100))  # 'plugin', 'system', 'monitor', 'health_check'
    
    # 컨텍스트 정보
    context_data = Column(JSON, default={})
    stack_trace = Column(Text)
    
    # 시스템 정보
    hostname = Column(String(255))
    process_id = Column(Integer)
    thread_id = Column(Integer)
    
    # 시간 정보
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='system_logs') 