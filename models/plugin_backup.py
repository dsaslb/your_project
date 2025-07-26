from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, ForeignKey, Text, LargeBinary
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

class PluginSnapshot(db.Model):
    """플러그인 스냅샷 테이블"""
    __tablename__ = 'plugin_snapshots'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    installation_id = Column(Integer, ForeignKey('plugin_installations.id'))
    
    # 스냅샷 정보
    snapshot_name = Column(String(255), nullable=False)
    snapshot_type = Column(String(50), nullable=False)  # 'install', 'update', 'manual', 'auto'
    
    # 플러그인 상태 정보
    plugin_version = Column(String(50), nullable=False)
    plugin_config = Column(JSON, default={})  # 플러그인 설정
    plugin_data = Column(JSON, default={})    # 플러그인 데이터
    plugin_files = Column(JSON, default={})   # 파일 목록 및 해시
    
    # 백업 파일 (실제 구현에서는 파일 시스템에 저장)
    backup_file_path = Column(String(500))
    backup_file_size = Column(Integer, default=0)
    backup_file_hash = Column(String(64))  # SHA256 해시
    
    # 메타데이터
    description = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 상태
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # 백업 무결성 검증
    
    plugin = relationship('Plugin', backref='snapshots')
    installation = relationship('PluginInstallation', backref='snapshots')
    user = relationship('User', backref='plugin_snapshots')

class PluginVersionHistory(db.Model):
    """플러그인 버전 히스토리 테이블"""
    __tablename__ = 'plugin_version_history'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    
    # 버전 정보
    version = Column(String(50), nullable=False)
    version_type = Column(String(20), default='patch')  # 'major', 'minor', 'patch'
    
    # 변경사항
    changelog = Column(Text)
    breaking_changes = Column(Boolean, default=False)
    security_updates = Column(Boolean, default=False)
    
    # 파일 정보
    file_path = Column(String(500))
    file_size = Column(Integer, default=0)
    file_hash = Column(String(64))
    
    # 릴리즈 정보
    release_date = Column(DateTime, default=datetime.utcnow)
    release_notes = Column(Text)
    download_count = Column(Integer, default=0)
    
    # 상태
    is_active = Column(Boolean, default=True)
    is_deprecated = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='version_history')

class PluginRollback(db.Model):
    """플러그인 롤백 기록 테이블"""
    __tablename__ = 'plugin_rollbacks'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    installation_id = Column(Integer, ForeignKey('plugin_installations.id'))
    
    # 롤백 정보
    from_version = Column(String(50), nullable=False)
    to_version = Column(String(50), nullable=False)
    rollback_reason = Column(Text)
    
    # 롤백 타입
    rollback_type = Column(String(50), default='manual')  # 'manual', 'automatic', 'emergency'
    
    # 롤백 상태
    status = Column(String(20), default='pending')  # 'pending', 'in_progress', 'completed', 'failed'
    
    # 롤백 결과
    success = Column(Boolean, default=False)
    error_message = Column(Text)
    rollback_duration = Column(Integer)  # 초 단위
    
    # 데이터 복구 정보
    data_restored = Column(Boolean, default=False)
    config_restored = Column(Boolean, default=False)
    files_restored = Column(Boolean, default=False)
    
    # 실행 정보
    executed_by = Column(Integer, ForeignKey('users.id'))
    executed_at = Column(DateTime, default=datetime.utcnow)
    
    # 메타데이터
    rollback_log = Column(JSON, default={})  # 상세 롤백 로그
    
    plugin = relationship('Plugin', backref='rollbacks')
    installation = relationship('PluginInstallation', backref='rollbacks')
    user = relationship('User', backref='plugin_rollbacks')

class PluginBackupSchedule(db.Model):
    """플러그인 자동 백업 스케줄 테이블"""
    __tablename__ = 'plugin_backup_schedules'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    
    # 스케줄 설정
    schedule_type = Column(String(20), default='daily')  # 'hourly', 'daily', 'weekly', 'monthly'
    schedule_time = Column(String(10))  # HH:MM 형식
    schedule_day = Column(String(20))   # 요일 (weekly의 경우)
    
    # 백업 설정
    retention_days = Column(Integer, default=30)  # 보관 기간
    max_backups = Column(Integer, default=10)     # 최대 백업 수
    include_data = Column(Boolean, default=True)  # 데이터 포함 여부
    include_config = Column(Boolean, default=True)  # 설정 포함 여부
    
    # 자동화 설정
    auto_cleanup = Column(Boolean, default=True)  # 자동 정리
    notify_on_failure = Column(Boolean, default=True)  # 실패 시 알림
    
    # 상태
    is_active = Column(Boolean, default=True)
    last_backup_at = Column(DateTime)
    next_backup_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='backup_schedules')

class PluginBackupLog(db.Model):
    """플러그인 백업 로그 테이블"""
    __tablename__ = 'plugin_backup_logs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    snapshot_id = Column(Integer, ForeignKey('plugin_snapshots.id'))
    
    # 백업 정보
    backup_type = Column(String(50), nullable=False)  # 'scheduled', 'manual', 'pre_update', 'post_update'
    backup_status = Column(String(20), default='pending')  # 'pending', 'in_progress', 'completed', 'failed'
    
    # 백업 결과
    success = Column(Boolean, default=False)
    error_message = Column(Text)
    backup_duration = Column(Integer)  # 초 단위
    
    # 백업 크기
    backup_size = Column(Integer, default=0)  # 바이트
    compressed_size = Column(Integer, default=0)  # 압축 후 크기
    
    # 메타데이터
    backup_metadata = Column(JSON, default={})  # 백업 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='backup_logs')
    snapshot = relationship('PluginSnapshot', backref='backup_logs') 