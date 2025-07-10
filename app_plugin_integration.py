"""
플러그인 시스템이 통합된 메인 Flask 앱
기존 기능을 플러그인 시스템과 연동
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import sys

# 코어 시스템 import
sys.path.append(os.path.join(os.path.dirname(__file__), 'core', 'backend'))
from core.backend.plugin_manager import plugin_manager
from core.backend.api_router import init_dynamic_router
from core.backend.feedback_system import feedback_system

# 기존 앱 import
from models import db, Staff, Order
from utils.decorators import login_required, admin_required

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask 앱 생성
app = Flask(__name__)
app.config.from_object('config.Config')

# CORS 설정
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

# 데이터베이스 초기화
db.init_app(app)

# 동적 라우터 초기화
dynamic_router = init_dynamic_router(app)

# 플러그인 시스템 초기화
def initialize_plugin_system():
    """플러그인 시스템 초기화"""
    try:
        # 활성화된 플러그인들 로드
        all_plugins = plugin_manager.get_all_plugins()
        for plugin_name, metadata in all_plugins.items():
            if metadata.enabled:
                logger.info(f"플러그인 로드 중: {plugin_name}")
                if plugin_manager.load_plugin(plugin_name):
                    # 플러그인의 API 라우트 등록
                    dynamic_router.register_plugin_routes(plugin_name)
                    logger.info(f"플러그인 {plugin_name} 로드 완료")
                else:
                    logger.error(f"플러그인 {plugin_name} 로드 실패")
        
        logger.info("플러그인 시스템 초기화 완료")
        
    except Exception as e:
        logger.error(f"플러그인 시스템 초기화 실패: {e}")

# 플러그인 관리 API
@app.route('/api/plugins', methods=['GET'])
@admin_required
def get_plugins():
    """플러그인 목록 조회"""
    try:
        plugins = plugin_manager.get_all_plugins()
        loaded_plugins = plugin_manager.get_loaded_plugins()
        
        plugin_list = []
        for plugin_name, metadata in plugins.items():
            plugin_list.append({
                'id': plugin_name,
                'name': metadata.name,
                'version': metadata.version,
                'description': metadata.description,
                'author': metadata.author,
                'category': metadata.category,
                'dependencies': metadata.dependencies,
                'permissions': metadata.permissions,
                'enabled': metadata.enabled,
                'loaded': plugin_name in loaded_plugins,
                'config': metadata.config
            })
        
        return jsonify({
            'success': True,
            'plugins': plugin_list
        })
        
    except Exception as e:
        logger.error(f"플러그인 목록 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/plugins/<plugin_name>/load', methods=['POST'])
@admin_required
def load_plugin(plugin_name):
    """플러그인 로드"""
    try:
        success = plugin_manager.load_plugin(plugin_name)
        if success:
            # API 라우트 등록
            dynamic_router.register_plugin_routes(plugin_name)
            return jsonify({
                'success': True,
                'message': f'플러그인 {plugin_name} 로드 완료'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'플러그인 {plugin_name} 로드 실패'
            }), 400
            
    except Exception as e:
        logger.error(f"플러그인 {plugin_name} 로드 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/plugins/<plugin_name>/unload', methods=['POST'])
@admin_required
def unload_plugin(plugin_name):
    """플러그인 언로드"""
    try:
        # API 라우트 등록 해제
        dynamic_router.unregister_plugin_routes(plugin_name)
        
        success = plugin_manager.unload_plugin(plugin_name)
        if success:
            return jsonify({
                'success': True,
                'message': f'플러그인 {plugin_name} 언로드 완료'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'플러그인 {plugin_name} 언로드 실패'
            }), 400
            
    except Exception as e:
        logger.error(f"플러그인 {plugin_name} 언로드 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/plugins/<plugin_name>/enable', methods=['POST'])
@admin_required
def enable_plugin(plugin_name):
    """플러그인 활성화"""
    try:
        success = plugin_manager.enable_plugin(plugin_name)
        if success:
            return jsonify({
                'success': True,
                'message': f'플러그인 {plugin_name} 활성화 완료'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'플러그인 {plugin_name} 활성화 실패'
            }), 400
            
    except Exception as e:
        logger.error(f"플러그인 {plugin_name} 활성화 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/plugins/<plugin_name>/disable', methods=['POST'])
@admin_required
def disable_plugin(plugin_name):
    """플러그인 비활성화"""
    try:
        success = plugin_manager.disable_plugin(plugin_name)
        if success:
            return jsonify({
                'success': True,
                'message': f'플러그인 {plugin_name} 비활성화 완료'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'플러그인 {plugin_name} 비활성화 실패'
            }), 400
            
    except Exception as e:
        logger.error(f"플러그인 {plugin_name} 비활성화 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/plugins/reload', methods=['POST'])
@admin_required
def reload_all_plugins():
    """모든 플러그인 재로드"""
    try:
        success = dynamic_router.reload_all_plugins()
        if success:
            return jsonify({
                'success': True,
                'message': '모든 플러그인 재로드 완료'
            })
        else:
            return jsonify({
                'success': False,
                'error': '플러그인 재로드 실패'
            }), 400
            
    except Exception as e:
        logger.error(f"플러그인 재로드 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 피드백 시스템 API
@app.route('/api/feedback', methods=['GET'])
@login_required
def get_feedbacks():
    """피드백 목록 조회"""
    try:
        # 현재 로그인한 사용자 정보 가져오기
        from flask_login import current_user
        user = current_user
        
        if user.role == 'admin':
            # 관리자는 모든 피드백 조회
            feedbacks = feedback_system.get_all_feedbacks()
        else:
            # 일반 사용자는 자신의 피드백만 조회
            feedbacks = feedback_system.get_user_feedbacks(str(user.id))
        
        return jsonify({
            'success': True,
            'feedbacks': [feedback.to_dict() for feedback in feedbacks]
        })
        
    except Exception as e:
        logger.error(f"피드백 목록 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/feedback', methods=['POST'])
@login_required
def submit_feedback():
    """피드백 제출"""
    try:
        from flask_login import current_user
        user = current_user
        data = request.get_json()
        
        feedback_id = feedback_system.submit_feedback(str(user.id), data)
        
        return jsonify({
            'success': True,
            'feedback_id': feedback_id,
            'message': '피드백 제출 완료'
        }), 201
        
    except Exception as e:
        logger.error(f"피드백 제출 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/feedback/<feedback_id>', methods=['GET'])
@login_required
def get_feedback(feedback_id):
    """피드백 상세 조회"""
    try:
        feedback = feedback_system.get_feedback(feedback_id)
        if not feedback:
            return jsonify({
                'success': False,
                'error': '피드백을 찾을 수 없습니다'
            }), 404
        
        return jsonify({
            'success': True,
            'feedback': feedback.to_dict()
        })
        
    except Exception as e:
        logger.error(f"피드백 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/feedback/<feedback_id>/status', methods=['PUT'])
@admin_required
def update_feedback_status(feedback_id):
    """피드백 상태 업데이트"""
    try:
        from flask_login import current_user
        user = current_user
        data = request.get_json()
        status = data.get('status')
        comment = data.get('comment', '')
        
        if not status:
            return jsonify({
                'success': False,
                'error': '상태 정보가 필요합니다'
            }), 400
        
        from core.backend.feedback_system import FeedbackStatus
        success = feedback_system.update_feedback_status(
            feedback_id, 
            FeedbackStatus(status), 
            str(user.id), 
            comment
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '피드백 상태 업데이트 완료'
            })
        else:
            return jsonify({
                'success': False,
                'error': '피드백 상태 업데이트 실패'
            }), 400
            
    except Exception as e:
        logger.error(f"피드백 상태 업데이트 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/feedback/<feedback_id>/comment', methods=['POST'])
@login_required
def add_feedback_comment(feedback_id):
    """피드백 댓글 추가"""
    try:
        from flask_login import current_user
        user = current_user
        data = request.get_json()
        comment = data.get('comment')
        is_admin = data.get('is_admin', False)
        
        if not comment:
            return jsonify({
                'success': False,
                'error': '댓글 내용이 필요합니다'
            }), 400
        
        success = feedback_system.add_feedback_comment(
            feedback_id, 
            str(user.id), 
            comment, 
            is_admin
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '댓글 추가 완료'
            })
        else:
            return jsonify({
                'success': False,
                'error': '댓글 추가 실패'
            }), 400
            
    except Exception as e:
        logger.error(f"피드백 댓글 추가 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/feedback/statistics', methods=['GET'])
@admin_required
def get_feedback_statistics():
    """피드백 통계 조회"""
    try:
        stats = feedback_system.get_feedback_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"피드백 통계 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/feedback/search', methods=['GET'])
@login_required
def search_feedbacks():
    """피드백 검색"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({
                'success': False,
                'error': '검색어가 필요합니다'
            }), 400
        
        results = feedback_system.search_feedbacks(query)
        return jsonify({
            'success': True,
            'feedbacks': [feedback.to_dict() for feedback in results]
        })
        
    except Exception as e:
        logger.error(f"피드백 검색 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 시스템 상태 확인 API
@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """시스템 상태 조회"""
    try:
        # 플러그인 상태
        plugins = plugin_manager.get_all_plugins()
        loaded_plugins = plugin_manager.get_loaded_plugins()
        
        # 데이터베이스 상태
        db_status = 'healthy'
        try:
            db.session.execute(db.text('SELECT 1'))
        except Exception:
            db_status = 'error'
        
        return jsonify({
            'success': True,
            'system': {
                'status': 'running',
                'plugins': {
                    'total': len(plugins),
                    'loaded': len(loaded_plugins),
                    'enabled': len([p for p in plugins.values() if p.enabled])
                },
                'database': db_status,
                'feedback_system': 'active'
            }
        })
        
    except Exception as e:
        logger.error(f"시스템 상태 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 기존 라우트들을 플러그인 시스템과 통합
@app.route('/api/restaurant/staff', methods=['GET'])
@login_required
def get_restaurant_staff():
    """외식업 플러그인의 직원 관리 API (기존 기능과 연동)"""
    try:
        # 기존 Staff 모델 사용
        staff_list = Staff.query.all()
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': staff.id,
                    'name': staff.name,
                    'position': staff.position,
                    'status': staff.status,
                    'branch_id': staff.branch_id
                }
                for staff in staff_list
            ]
        })
        
    except Exception as e:
        logger.error(f"직원 목록 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/restaurant/orders', methods=['GET'])
@login_required
def get_restaurant_orders():
    """외식업 플러그인의 주문 관리 API (기존 기능과 연동)"""
    try:
        # 기존 Order 모델 사용
        order_list = Order.query.all()
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': order.id,
                    'order_number': order.order_number,
                    'status': order.status,
                    'total_amount': order.total_amount,
                    'created_at': order.created_at.isoformat() if order.created_at else None
                }
                for order in order_list
            ]
        })
        
    except Exception as e:
        logger.error(f"주문 목록 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 앱 초기화
def create_app():
    """플러그인 시스템이 통합된 Flask 앱 생성"""
    with app.app_context():
        # 데이터베이스 테이블 생성
        db.create_all()
        
        # 플러그인 시스템 초기화
        initialize_plugin_system()
        
        logger.info("플러그인 시스템이 통합된 앱 초기화 완료")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 