from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import json

# Blueprint 생성
simple_plugin_bp = Blueprint('simple_plugin', __name__)

@simple_plugin_bp.route('/api/plugin/test', methods=['GET'])
@cross_origin()
def test_plugin_api():
    """플러그인 API 테스트"""
    return jsonify({
        'success': True,
        'message': '플러그인 API가 정상적으로 작동합니다!',
        'data': {
            'plugins': [
                {
                    'id': 1,
                    'name': 'ai_schedule_recommendation',
                    'display_name': 'AI 스케줄 추천',
                    'description': '직원 근무 패턴과 매장 상황을 분석하여 최적의 스케줄을 자동으로 추천해주는 AI 플러그인입니다.',
                    'version': '1.0.0',
                    'author': 'AI Team',
                    'category': 'ai',
                    'tags': ['ai', 'schedule', 'recommendation', 'automation'],
                    'icon': 'fas fa-robot',
                    'ui_schema': {
                        'menu': {
                            'title': 'AI 스케줄',
                            'icon': 'fas fa-robot',
                            'position': 1,
                            'parent': 'schedule'
                        },
                        'dashboard': {
                            'type': 'card',
                            'title': 'AI 스케줄 추천',
                            'description': '이번 주 최적 스케줄',
                            'component': 'AIScheduleCard',
                            'size': 'medium'
                        }
                    },
                    'download_count': 150,
                    'rating': 4.5,
                    'review_count': 23
                },
                {
                    'id': 2,
                    'name': 'review_auto_summary',
                    'display_name': '리뷰 자동 요약',
                    'description': '고객 리뷰를 AI가 분석하여 핵심 내용을 자동으로 요약하고 감정 분석을 제공합니다.',
                    'version': '1.2.0',
                    'author': 'Analytics Team',
                    'category': 'analytics',
                    'tags': ['ai', 'review', 'summary', 'sentiment'],
                    'icon': 'fas fa-chart-line',
                    'ui_schema': {
                        'menu': {
                            'title': '리뷰 분석',
                            'icon': 'fas fa-chart-line',
                            'position': 2,
                            'parent': 'reviews'
                        },
                        'dashboard': {
                            'type': 'chart',
                            'title': '리뷰 감정 분석',
                            'description': '최근 30일 리뷰 감정 트렌드',
                            'component': 'ReviewSentimentChart',
                            'size': 'large'
                        }
                    },
                    'download_count': 89,
                    'rating': 4.2,
                    'review_count': 15
                },
                {
                    'id': 3,
                    'name': 'qsc_auto_analysis',
                    'display_name': 'QSC 자동 분석',
                    'description': '품질(Quality), 서비스(Service), 청결(Cleanliness) 데이터를 자동으로 분석하고 개선점을 제시합니다.',
                    'version': '2.1.0',
                    'author': 'QSC Team',
                    'category': 'qsc',
                    'tags': ['qsc', 'quality', 'service', 'cleanliness', 'analysis'],
                    'icon': 'fas fa-clipboard-check',
                    'ui_schema': {
                        'menu': {
                            'title': 'QSC 분석',
                            'icon': 'fas fa-clipboard-check',
                            'position': 3,
                            'parent': 'management'
                        },
                        'dashboard': {
                            'type': 'gauge',
                            'title': 'QSC 종합 점수',
                            'description': '현재 QSC 종합 평가',
                            'component': 'QSCGauge',
                            'size': 'medium'
                        }
                    },
                    'download_count': 234,
                    'rating': 4.7,
                    'review_count': 42
                }
            ],
            'categories': ['ai', 'analytics', 'qsc', 'automation', 'inventory'],
            'total_plugins': 3
        }
    })

@simple_plugin_bp.route('/api/plugin/categories', methods=['GET'])
@cross_origin()
def get_plugin_categories():
    """플러그인 카테고리 목록 조회"""
    return jsonify({
        'success': True,
        'categories': [
            {
                'id': 'ai',
                'name': 'AI & 머신러닝',
                'description': '인공지능과 머신러닝 기반 플러그인',
                'icon': 'fas fa-brain',
                'plugin_count': 2
            },
            {
                'id': 'analytics',
                'name': '분석 & 리포팅',
                'description': '데이터 분석 및 보고서 생성 플러그인',
                'icon': 'fas fa-chart-bar',
                'plugin_count': 1
            },
            {
                'id': 'qsc',
                'name': 'QSC 관리',
                'description': '품질, 서비스, 청결 관리 플러그인',
                'icon': 'fas fa-clipboard-check',
                'plugin_count': 1
            },
            {
                'id': 'automation',
                'name': '자동화',
                'description': '업무 자동화 플러그인',
                'icon': 'fas fa-cogs',
                'plugin_count': 1
            },
            {
                'id': 'inventory',
                'name': '재고 관리',
                'description': '재고 및 발주 관리 플러그인',
                'icon': 'fas fa-boxes',
                'plugin_count': 0
            }
        ]
    })

@simple_plugin_bp.route('/api/plugin/install', methods=['POST'])
@cross_origin()
def install_plugin():
    """플러그인 설치 (더미)"""
    try:
        data = request.get_json()
        plugin_id = data.get('plugin_id')
        
        return jsonify({
            'success': True,
            'message': f'플러그인 ID {plugin_id}가 성공적으로 설치되었습니다.',
            'installation_id': f'install_{plugin_id}_{12345}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': '플러그인 설치 실패',
            'details': str(e)
        }), 500

@simple_plugin_bp.route('/api/plugin/uninstall', methods=['POST'])
@cross_origin()
def uninstall_plugin():
    """플러그인 제거 (더미)"""
    try:
        data = request.get_json()
        installation_id = data.get('installation_id')
        
        return jsonify({
            'success': True,
            'message': f'플러그인이 성공적으로 제거되었습니다.',
            'installation_id': installation_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': '플러그인 제거 실패',
            'details': str(e)
        }), 500 