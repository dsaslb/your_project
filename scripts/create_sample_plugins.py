#!/usr/bin/env python3
"""
샘플 플러그인 데이터 생성 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Flask 앱 직접 실행
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship

# Flask 앱 생성
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'  # 정확한 DB 경로
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

CORS(app)
db = SQLAlchemy(app)

# 플러그인 모델 정의
class Plugin(db.Model):
    __tablename__ = 'plugins'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    version = Column(String(20), nullable=False)
    author = Column(String(100))
    category = Column(String(50))
    tags = Column(JSON)
    ui_schema = Column(JSON, nullable=False)
    icon = Column(String(100))
    menu_position = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_installed = Column(Boolean, default=False)
    installation_date = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String(500))
    file_size = Column(Integer)
    checksum = Column(String(64))
    download_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PluginUpdate(db.Model):
    __tablename__ = 'plugin_updates'
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey('plugins.id'), nullable=False)
    from_version = Column(String(20))
    to_version = Column(String(20), nullable=False)
    changelog = Column(Text)
    update_type = Column(String(20))
    file_path = Column(String(500))
    file_size = Column(Integer)
    checksum = Column(String(64))
    is_auto_update = Column(Boolean, default=False)
    requires_restart = Column(Boolean, default=False)
    breaking_changes = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, default=datetime.utcnow)

def create_sample_plugins():
    with app.app_context():
        try:
            # 기존 플러그인 삭제 (테스트용)
            Plugin.query.delete()
            PluginUpdate.query.delete()
            
            sample_plugins = [
                {
                    'name': 'ai_schedule_optimizer',
                    'display_name': 'AI 스케줄 최적화',
                    'description': '직원 스케줄을 AI로 분석하여 최적의 근무 시간을 제안합니다.',
                    'version': '1.0.0',
                    'author': 'AI Team',
                    'category': '스케줄링',
                    'tags': ['AI', '스케줄', '최적화'],
                    'ui_schema': {
                        'menu': {
                            'title': 'AI 스케줄',
                            'icon': 'calendar',
                            'position': 1
                        },
                        'dashboard': {
                            'type': 'chart',
                            'size': 'medium',
                            'component': 'ScheduleOptimizationChart'
                        }
                    },
                    'icon': 'calendar',
                    'menu_position': 1,
                    'is_active': True,
                    'is_installed': False,
                    'file_path': '/plugins/ai_schedule_optimizer.py',
                    'file_size': 1024000,
                    'checksum': 'abc123def456',
                    'download_count': 150,
                    'rating': 4.5,
                    'review_count': 23
                },
                {
                    'name': 'review_auto_summary',
                    'display_name': '리뷰 자동 요약',
                    'description': '고객 리뷰를 자동으로 분석하고 핵심 내용을 요약해드립니다.',
                    'version': '2.1.0',
                    'author': 'NLP Team',
                    'category': '고객 관리',
                    'tags': ['NLP', '리뷰', '분석'],
                    'ui_schema': {
                        'menu': {
                            'title': '리뷰 분석',
                            'icon': 'message-square',
                            'position': 2
                        },
                        'dashboard': {
                            'type': 'list',
                            'size': 'large',
                            'component': 'ReviewSummaryList'
                        }
                    },
                    'icon': 'message-square',
                    'menu_position': 2,
                    'is_active': True,
                    'is_installed': True,
                    'file_path': '/plugins/review_auto_summary.py',
                    'file_size': 2048000,
                    'checksum': 'def456ghi789',
                    'download_count': 89,
                    'rating': 4.2,
                    'review_count': 15
                },
                {
                    'name': 'qsc_auto_analyzer',
                    'display_name': 'QSC 자동 분석',
                    'description': '품질, 서비스, 청결도를 자동으로 분석하고 개선점을 제시합니다.',
                    'version': '1.5.0',
                    'author': 'Quality Team',
                    'category': '품질 관리',
                    'tags': ['QSC', '품질', '분석'],
                    'ui_schema': {
                        'menu': {
                            'title': 'QSC 분석',
                            'icon': 'bar-chart-3',
                            'position': 3
                        },
                        'dashboard': {
                            'type': 'gauge',
                            'size': 'small',
                            'component': 'QSCGaugeChart'
                        }
                    },
                    'icon': 'bar-chart-3',
                    'menu_position': 3,
                    'is_active': True,
                    'is_installed': False,
                    'file_path': '/plugins/qsc_auto_analyzer.py',
                    'file_size': 1536000,
                    'checksum': 'ghi789jkl012',
                    'download_count': 67,
                    'rating': 4.7,
                    'review_count': 12
                },
                {
                    'name': 'contract_auto_notifier',
                    'display_name': '계약 자동 알림',
                    'description': '계약 만료일, 갱신일 등을 자동으로 추적하고 알림을 보냅니다.',
                    'version': '1.2.0',
                    'author': 'Contract Team',
                    'category': '계약 관리',
                    'tags': ['계약', '알림', '자동화'],
                    'ui_schema': {
                        'menu': {
                            'title': '계약 관리',
                            'icon': 'file-text',
                            'position': 4
                        },
                        'dashboard': {
                            'type': 'table',
                            'size': 'medium',
                            'component': 'ContractNotificationTable'
                        }
                    },
                    'icon': 'file-text',
                    'menu_position': 4,
                    'is_active': True,
                    'is_installed': True,
                    'file_path': '/plugins/contract_auto_notifier.py',
                    'file_size': 768000,
                    'checksum': 'jkl012mno345',
                    'download_count': 234,
                    'rating': 4.8,
                    'review_count': 45
                },
                {
                    'name': 'inventory_predictor',
                    'display_name': '재고 예측',
                    'description': 'AI를 활용하여 재고 소진 시점을 예측하고 발주 시점을 알려줍니다.',
                    'version': '2.0.0',
                    'author': 'AI Team',
                    'category': '재고 관리',
                    'tags': ['AI', '재고', '예측'],
                    'ui_schema': {
                        'menu': {
                            'title': '재고 예측',
                            'icon': 'package',
                            'position': 5
                        },
                        'dashboard': {
                            'type': 'line-chart',
                            'size': 'large',
                            'component': 'InventoryPredictionChart'
                        }
                    },
                    'icon': 'package',
                    'menu_position': 5,
                    'is_active': True,
                    'is_installed': False,
                    'file_path': '/plugins/inventory_predictor.py',
                    'file_size': 3072000,
                    'checksum': 'mno345pqr678',
                    'download_count': 178,
                    'rating': 4.6,
                    'review_count': 34
                }
            ]
            
            for plugin_data in sample_plugins:
                plugin = Plugin(**plugin_data)
                db.session.add(plugin)
                db.session.flush()  # ID 생성
                
                # 플러그인 업데이트 정보 추가
                update = PluginUpdate(
                    plugin_id=plugin.id,
                    from_version=None,
                    to_version=plugin_data['version'],
                    changelog='초기 버전 릴리즈',
                    update_type='major',
                    file_path=plugin_data['file_path'],
                    file_size=plugin_data['file_size'],
                    checksum=plugin_data['checksum'],
                    is_auto_update=False,
                    requires_restart=False,
                    breaking_changes=False
                )
                db.session.add(update)
            
            db.session.commit()
            print(f"✅ {len(sample_plugins)}개의 샘플 플러그인이 성공적으로 생성되었습니다.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 샘플 플러그인 생성 중 오류 발생: {str(e)}")
            raise

if __name__ == '__main__':
    create_sample_plugins() 