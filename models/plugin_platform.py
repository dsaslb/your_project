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

class PluginPlatformConfig(db.Model):
    """플러그인 플랫폼 설정 테이블"""
    __tablename__ = 'plugin_platform_configs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    
    # 지원 플랫폼
    supported_platforms = Column(JSON, default=['web', 'mobile', 'pos', 'tablet'])  # 지원하는 플랫폼 목록
    
    # 플랫폼별 활성화 상태
    web_enabled = Column(Boolean, default=True)
    mobile_enabled = Column(Boolean, default=True)
    pos_enabled = Column(Boolean, default=False)
    tablet_enabled = Column(Boolean, default=True)
    
    # 플랫폼별 우선순위
    platform_priority = Column(JSON, default={
        'web': 1,
        'mobile': 2,
        'tablet': 3,
        'pos': 4
    })
    
    # 플랫폼별 기능 제한
    platform_restrictions = Column(JSON, default={
        'mobile': ['no_file_upload', 'limited_analytics'],
        'pos': ['no_advanced_features', 'touch_optimized'],
        'tablet': ['no_desktop_features']
    })
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='platform_config')

class PluginUISchema(db.Model):
    """플러그인 UI 스키마 테이블"""
    __tablename__ = 'plugin_ui_schemas'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    platform = Column(String(20), nullable=False)  # 'web', 'mobile', 'pos', 'tablet'
    
    # UI 스키마 정의
    ui_schema = Column(JSON, default={
        'layout': 'responsive',
        'components': [],
        'navigation': {},
        'themes': {},
        'breakpoints': {}
    })
    
    # 반응형 설정
    responsive_config = Column(JSON, default={
        'mobile': {
            'max_width': 768,
            'layout': 'stacked',
            'touch_friendly': True
        },
        'tablet': {
            'max_width': 1024,
            'layout': 'grid',
            'touch_friendly': True
        },
        'desktop': {
            'min_width': 1025,
            'layout': 'sidebar',
            'touch_friendly': False
        }
    })
    
    # 플랫폼별 스타일
    platform_styles = Column(JSON, default={
        'colors': {},
        'fonts': {},
        'spacing': {},
        'animations': {}
    })
    
    # 접근성 설정
    accessibility_config = Column(JSON, default={
        'high_contrast': False,
        'large_text': False,
        'screen_reader': True,
        'keyboard_navigation': True
    })
    
    # 성능 최적화
    performance_config = Column(JSON, default={
        'lazy_loading': True,
        'image_optimization': True,
        'code_splitting': True,
        'caching': True
    })
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='ui_schemas')

class PluginDeviceSupport(db.Model):
    """플러그인 디바이스 지원 테이블"""
    __tablename__ = 'plugin_device_supports'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    
    # 지원 디바이스 타입
    device_types = Column(JSON, default=[
        'smartphone', 'tablet', 'desktop', 'laptop', 'pos_terminal', 'kiosk'
    ])
    
    # 운영체제 지원
    supported_os = Column(JSON, default={
        'mobile': ['ios', 'android'],
        'desktop': ['windows', 'macos', 'linux'],
        'web': ['chrome', 'firefox', 'safari', 'edge']
    })
    
    # 브라우저 지원
    browser_support = Column(JSON, default={
        'chrome': '>=80',
        'firefox': '>=75',
        'safari': '>=13',
        'edge': '>=80'
    })
    
    # 최소 사양 요구사항
    minimum_requirements = Column(JSON, default={
        'mobile': {
            'ram': '2GB',
            'storage': '1GB',
            'screen_resolution': '320x568'
        },
        'tablet': {
            'ram': '4GB',
            'storage': '2GB',
            'screen_resolution': '768x1024'
        },
        'desktop': {
            'ram': '8GB',
            'storage': '5GB',
            'screen_resolution': '1920x1080'
        }
    })
    
    # 테스트 완료 디바이스
    tested_devices = Column(JSON, default=[])
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='device_support')

class PluginLocalization(db.Model):
    """플러그인 다국어 지원 테이블"""
    __tablename__ = 'plugin_localizations'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    
    # 지원 언어
    supported_languages = Column(JSON, default=['ko', 'en', 'ja', 'zh'])
    default_language = Column(String(10), default='ko')
    
    # 번역 데이터
    translations = Column(JSON, default={
        'ko': {
            'title': '플러그인 제목',
            'description': '플러그인 설명',
            'buttons': {},
            'messages': {},
            'errors': {}
        },
        'en': {
            'title': 'Plugin Title',
            'description': 'Plugin Description',
            'buttons': {},
            'messages': {},
            'errors': {}
        }
    })
    
    # 지역화 설정
    localization_config = Column(JSON, default={
        'date_format': 'YYYY-MM-DD',
        'time_format': 'HH:mm:ss',
        'currency': 'KRW',
        'timezone': 'Asia/Seoul',
        'number_format': {
            'decimal_separator': '.',
            'thousands_separator': ','
        }
    })
    
    # RTL 언어 지원
    rtl_support = Column(Boolean, default=False)
    rtl_languages = Column(JSON, default=['ar', 'he', 'fa'])
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='localization')

class PluginOfflineSupport(db.Model):
    """플러그인 오프라인 지원 테이블"""
    __tablename__ = 'plugin_offline_supports'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    
    # 오프라인 지원 여부
    offline_enabled = Column(Boolean, default=False)
    
    # 오프라인 기능
    offline_features = Column(JSON, default=[
        'basic_viewing',
        'data_caching',
        'offline_forms'
    ])
    
    # 캐시 설정
    cache_config = Column(JSON, default={
        'max_cache_size': '100MB',
        'cache_duration': 86400,  # 24시간
        'cache_strategy': 'network_first',
        'cacheable_resources': [
            'images',
            'css',
            'js',
            'data'
        ]
    })
    
    # 동기화 설정
    sync_config = Column(JSON, default={
        'auto_sync': True,
        'sync_interval': 300,  # 5분
        'conflict_resolution': 'server_wins',
        'sync_on_reconnect': True
    })
    
    # 오프라인 제한사항
    offline_limitations = Column(JSON, default=[
        'no_real_time_updates',
        'limited_functionality',
        'data_sync_required'
    ])
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='offline_support')

class PluginIntegrationConfig(db.Model):
    """플러그인 통합 설정 테이블"""
    __tablename__ = 'plugin_integration_configs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    
    # 외부 서비스 통합
    external_integrations = Column(JSON, default={
        'slack': {
            'enabled': False,
            'webhook_url': '',
            'channels': []
        },
        'email': {
            'enabled': False,
            'smtp_config': {},
            'templates': []
        },
        'sms': {
            'enabled': False,
            'provider': '',
            'api_key': ''
        }
    })
    
    # API 통합
    api_integrations = Column(JSON, default={
        'rest_api': {
            'enabled': True,
            'endpoints': [],
            'authentication': 'jwt'
        },
        'graphql': {
            'enabled': False,
            'endpoint': '',
            'schema': ''
        },
        'webhook': {
            'enabled': False,
            'endpoints': [],
            'events': []
        }
    })
    
    # 데이터베이스 통합
    database_integrations = Column(JSON, default={
        'primary_db': 'postgresql',
        'read_replicas': [],
        'cache_db': 'redis',
        'search_db': 'elasticsearch'
    })
    
    # 파일 스토리지 통합
    storage_integrations = Column(JSON, default={
        'local_storage': {
            'enabled': True,
            'path': '/uploads'
        },
        'cloud_storage': {
            'enabled': False,
            'provider': 'aws_s3',
            'bucket': '',
            'region': ''
        }
    })
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='integration_config') 