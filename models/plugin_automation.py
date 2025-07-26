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

class PluginEvent(db.Model):
    """플러그인/시스템 이벤트 테이블"""
    __tablename__ = 'plugin_events'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'))
    event_type = Column(String(50), nullable=False)  # 'install', 'update', 'execute', 'error', 'custom', ...
    event_source = Column(String(50), default='system')  # 'system', 'user', 'api', ...
    event_payload = Column(JSON, default={})
    triggered_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    plugin = relationship('Plugin', backref='events')
    user = relationship('User', backref='triggered_events')

class PluginTrigger(db.Model):
    """이벤트 트리거 테이블"""
    __tablename__ = 'plugin_triggers'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    event_type = Column(String(50), nullable=False)  # 트리거할 이벤트 타입
    filter_conditions = Column(JSON, default={})  # 필터/조건 (예: 특정 플러그인, 사용자, 값 등)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', backref='created_triggers')
    workflows = relationship('PluginWorkflow', backref='trigger')

class PluginAction(db.Model):
    """액션 테이블"""
    __tablename__ = 'plugin_actions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    action_type = Column(String(50), nullable=False)  # 'notify', 'api_call', 'plugin_execute', 'custom', ...
    action_payload = Column(JSON, default={})  # 실행 파라미터/설정
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', backref='created_actions')
    workflows = relationship('PluginWorkflow', backref='action')

class PluginWorkflow(db.Model):
    """트리거-액션 워크플로우 테이블"""
    __tablename__ = 'plugin_workflows'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    trigger_id = Column(Integer, ForeignKey('plugin_triggers.id'), nullable=False)
    action_id = Column(Integer, ForeignKey('plugin_actions.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    execution_order = Column(Integer, default=1)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', backref='created_workflows')

class PluginAutomationLog(db.Model):
    """자동화 실행 로그 테이블"""
    __tablename__ = 'plugin_automation_logs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey('plugin_workflows.id'))
    event_id = Column(Integer, ForeignKey('plugin_events.id'))
    action_id = Column(Integer, ForeignKey('plugin_actions.id'))
    status = Column(String(20), default='pending')  # 'pending', 'success', 'failed'
    result = Column(JSON, default={})
    error_message = Column(Text)
    executed_at = Column(DateTime, default=datetime.utcnow)
    
    workflow = relationship('PluginWorkflow', backref='automation_logs')
    event = relationship('PluginEvent', backref='automation_logs')
    action = relationship('PluginAction', backref='automation_logs') 