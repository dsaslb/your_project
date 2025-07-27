from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from models_main import db

class Plugin(db.Model):
    """플러그인 정보 테이블"""
    __tablename__ = 'plugins'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    version = Column(String(20), nullable=False)
    author = Column(String(100))
    category = Column(String(50))  # ai, analytics, automation, qsc, etc.
    tags = Column(JSON)  # ["ai", "schedule", "recommendation"]
    
    # UI Schema 정보
    ui_schema = Column(JSON, nullable=False)  # 메뉴, 아이콘, 컴포넌트 정보
    icon = Column(String(100))  # 아이콘 클래스명
    menu_position = Column(Integer, default=0)  # 메뉴 순서
    
    # 플러그인 설정
    is_active = Column(Boolean, default=True)
    is_installed = Column(Boolean, default=False)
    installation_date = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # 파일 정보
    file_path = Column(String(500))
    file_size = Column(Integer)
    checksum = Column(String(64))
    
    # 통계
    download_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    
    # 관계
    installations = relationship("PluginInstallation", back_populates="plugin")
    reviews = relationship("PluginReview", back_populates="plugin")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PluginInstallation(db.Model):
    """플러그인 설치 정보 테이블"""
    __tablename__ = 'plugin_installations'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=True)  # 브랜드별 설치
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)  # 매장별 설치
    
    # 설치 정보
    version = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    installed_by = Column(Integer, ForeignKey('users.id'))
    installed_at = Column(DateTime, default=datetime.utcnow)
    
    # 설정
    settings = Column(JSON, default={})  # 플러그인별 설정
    permissions = Column(JSON, default={})  # 권한 설정
    
    # 상태
    status = Column(String(20), default='active')  # active, disabled, error
    last_used = Column(DateTime)
    usage_count = Column(Integer, default=0)
    
    # 관계
    plugin = relationship("Plugin", back_populates="installations")
    brand = relationship("Brand")
    branch = relationship("Branch")
    installer = relationship("User")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PluginReview(db.Model):
    """플러그인 리뷰 테이블"""
    __tablename__ = 'plugin_reviews'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # 리뷰 정보
    rating = Column(Integer, nullable=False)  # 1-5점
    title = Column(String(200))
    content = Column(Text)
    is_verified = Column(Boolean, default=False)  # 실제 사용자 확인
    is_public = Column(Boolean, default=True)
    status = Column(String(20), default="active")  # active, hidden, deleted
    helpful_count = Column(Integer, default=0)
    
    # 관계
    plugin = relationship("Plugin", back_populates="reviews")
    user = relationship("User")
    responses = relationship("PluginReviewResponse", back_populates="review", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PluginReviewResponse(db.Model):
    """플러그인 리뷰 응답 모델 (개발자/관리자 답변)"""
    __tablename__ = 'plugin_review_responses'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, ForeignKey('plugin_reviews.id'), nullable=False)
    responder_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    responder_type = Column(String(20), nullable=False)  # developer, admin
    content = Column(Text, nullable=False)
    is_public = Column(Boolean, default=True)
    
    # 관계
    review = relationship("PluginReview", back_populates="responses")
    responder = relationship("User")
    
    created_at = Column(DateTime, default=datetime.utcnow)

class PluginUpdate(db.Model):
    """플러그인 업데이트 기록 테이블"""
    __tablename__ = 'plugin_updates'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    
    # 업데이트 정보
    from_version = Column(String(20))
    to_version = Column(String(20), nullable=False)
    changelog = Column(Text)
    update_type = Column(String(20))  # major, minor, patch
    
    # 파일 정보
    file_path = Column(String(500))
    file_size = Column(Integer)
    checksum = Column(String(64))
    
    # 배포 정보
    is_auto_update = Column(Boolean, default=False)
    requires_restart = Column(Boolean, default=False)
    breaking_changes = Column(Boolean, default=False)
    
    # 관계
    plugin = relationship("Plugin")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, default=datetime.utcnow)

class PluginUsage(db.Model):
    """플러그인 사용 통계 테이블"""
    __tablename__ = 'plugin_usage'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    installation_id = Column(Integer, ForeignKey('plugin_installations.id'), nullable=False)
    
    # 사용 정보
    action = Column(String(50))  # install, uninstall, enable, disable, use
    user_id = Column(Integer, ForeignKey('users.id'))
    session_duration = Column(Integer)  # 초 단위
    
    # 메타데이터
    meta_data = Column(JSON, default={})  # 추가 정보
    
    # 관계
    plugin = relationship("Plugin")
    installation = relationship("PluginInstallation")
    user = relationship("User")
    
    created_at = Column(DateTime, default=datetime.utcnow) 