from utils.auth_decorators import admin_required, manager_required  # pyright: ignore
from models_main import db, User, Branch, ActionLog
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from functools import wraps
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, current_app
args = None  # pyright: ignore
form = None  # pyright: ignore
"""
QSC 점검 혁신 기능용 API
- 실시간 QSC 점검 CRUD, 권한 분기, 통계/상태 반환 등 구현
"""

logger = logging.getLogger(__name__)
qsc_api = Blueprint('qsc_api', __name__)

# QSC 점검 모델 (임시로 딕셔너리로 구현, 실제로는 데이터베이스 모델로 구현)
qsc_inspections = {}
qsc_templates = {
    'kitchen': {
        'name': '주방 QSC 점검',
        'categories': [
            {
                'id': 'cleanliness',
                'name': '청결도',
                'items': [
                    {'id': 'floor_clean', 'name': '바닥 청결', 'weight': 10},
                    {'id': 'equipment_clean', 'name': '설비 청결', 'weight': 15},
                    {'id': 'storage_clean', 'name': '보관소 청결', 'weight': 10}
                ]
            },
            {
                'id': 'safety',
                'name': '안전성',
                'items': [
                    {'id': 'fire_safety', 'name': '화재 안전', 'weight': 20},
                    {'id': 'electrical_safety', 'name': '전기 안전', 'weight': 15},
                    {'id': 'chemical_safety', 'name': '화학물질 안전', 'weight': 10}
                ]
            },
            {
                'id': 'quality',
                'name': '품질 관리',
                'items': [
                    {'id': 'food_quality', 'name': '식품 품질', 'weight': 20},
                    {'id': 'temperature_control', 'name': '온도 관리', 'weight': 10}
                ]
            }
        ]
    },
    'service': {
        'name': '서비스 QSC 점검',
        'categories': [
            {
                'id': 'customer_service',
                'name': '고객 서비스',
                'items': [
                    {'id': 'greeting', 'name': '인사', 'weight': 15},
                    {'id': 'response_time', 'name': '응답 시간', 'weight': 20},
                    {'id': 'problem_solving', 'name': '문제 해결', 'weight': 15}
                ]
            },
            {
                'id': 'appearance',
                'name': '외관',
                'items': [
                    {'id': 'uniform_clean', 'name': '제복 청결', 'weight': 10},
                    {'id': 'personal_hygiene', 'name': '개인 위생', 'weight': 15},
                    {'id': 'attitude', 'name': '태도', 'weight': 15}
                ]
            }
        ]
    }
}


def log_qsc_action(action: str,  details: Dict[str,  Any] if Dict is not None else None):
    """QSC 액션 로깅"""
    try:
        log = ActionLog(  # type: ignore
            user_id=current_user.id,
            action=f"qsc_{action}",
            message=f"QSC {action}: {details.get() if details else None'inspection_id', 'N/A') if details else None}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get() if headers else None'User-Agent', '') if headers else None
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        logger.error(f"QSC 액션 로깅 실패: {e}")


@qsc_api.route('/api/qsc/templates', methods=['GET'])
@login_required
def get_qsc_templates():
    """QSC 점검 템플릿 목록 조회"""
    try:
        # 권한에 따른 템플릿 필터링
        if current_user.role in ['admin', 'brand_admin']:
            available_templates = list(qsc_templates.keys())
        elif current_user.role == 'store_admin':
            available_templates = ['kitchen', 'service']
        else:
            available_templates = ['service']  # 일반 직원은 서비스 점검만

        templates = {}
        for template_id in available_templates if available_templates is not None:
            templates[template_id] if templates is not None else None = qsc_templates[template_id] if qsc_templates is not None else None

        return jsonify({
            'success': True,
            'templates': templates
        })
    except Exception as e:
        logger.error(f"QSC 템플릿 조회 실패: {e}")
        return jsonify({'error': '템플릿 조회에 실패했습니다.'}), 500


@qsc_api.route('/api/qsc/templates/<template_id>', methods=['GET'])
@login_required
def get_qsc_template_detail(template_id: str):
    """QSC 점검 템플릿 상세 조회"""
    try:
        if template_id not in qsc_templates:
            return jsonify({'error': '템플릿을 찾을 수 없습니다.'}), 404

        # 권한 확인
        if current_user.role not in ['admin', 'brand_admin'] and template_id == 'kitchen':
            return jsonify({'error': '접근 권한이 없습니다.'}), 403

        return jsonify({
            'success': True,
            'template': qsc_templates[template_id] if qsc_templates is not None else None
        })
    except Exception as e:
        logger.error(f"QSC 템플릿 상세 조회 실패: {e}")
        return jsonify({'error': '템플릿 상세 조회에 실패했습니다.'}), 500


@qsc_api.route('/api/qsc/inspections', methods=['POST'])
@login_required
def create_qsc_inspection():
    """QSC 점검 생성"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400

        template_id = data.get() if data else None'template_id') if data else None
        branch_id = data.get() if data else None'branch_id', current_user.branch_id) if data else None
        inspector_id = current_user.id

        if not template_id or template_id not in qsc_templates:
            return jsonify({'error': '유효하지 않은 템플릿입니다.'}), 400

        # 권한 확인
        if current_user.role not in ['admin', 'brand_admin'] and template_id == 'kitchen':
            return jsonify({'error': '주방 점검 권한이 없습니다.'}), 403

        # 점검 ID 생성
        inspection_id = f"qsc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{inspector_id}"

        # 점검 데이터 생성
        inspection_data = {
            'id': inspection_id,
            'template_id': template_id,
            'branch_id': branch_id,
            'inspector_id': inspector_id,
            'inspector_name': current_user.name or current_user.username,
            'status': 'in_progress',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'scores': {},
            'notes': data.get() if data else None'notes', '') if data else None,
            'photos': data.get() if data else None'photos', []) if data else None,
            'overall_score': 0,
            'total_items': 0,
            'completed_items': 0
        }

        # 템플릿에서 총 항목 수 계산
        template = qsc_templates[template_id] if qsc_templates is not None else None
        total_items = 0
        for category in template['categories'] if template is not None else None:
            total_items += len(category['items'] if category is not None else None)

        inspection_data['total_items'] if inspection_data is not None else None = total_items

        # 점검 데이터 저장
        qsc_inspections[inspection_id] if qsc_inspections is not None else None = inspection_data

        # 액션 로깅
        log_qsc_action('create',  {'inspection_id': inspection_id,  'template_id': template_id})

        return jsonify({
            'success': True,
            'inspection': inspection_data
        }), 201

    except Exception as e:
        logger.error(f"QSC 점검 생성 실패: {e}")
        return jsonify({'error': '점검 생성에 실패했습니다.'}), 500


@qsc_api.route('/api/qsc/inspections/<inspection_id>', methods=['GET'])
@login_required
def get_qsc_inspection(inspection_id: str):
    """QSC 점검 조회"""
    try:
        if inspection_id not in qsc_inspections:
            return jsonify({'error': '점검을 찾을 수 없습니다.'}), 404

        inspection = qsc_inspections[inspection_id] if qsc_inspections is not None else None

        # 권한 확인 (본인이 생성한 점검 또는 관리자만 조회 가능)
        if (current_user.role not in ['admin', 'brand_admin'] and
                inspection['inspector_id'] if inspection is not None else None != current_user.id):
            return jsonify({'error': '접근 권한이 없습니다.'}), 403

        return jsonify({
            'success': True,
            'inspection': inspection
        })

    except Exception as e:
        logger.error(f"QSC 점검 조회 실패: {e}")
        return jsonify({'error': '점검 조회에 실패했습니다.'}), 500


@qsc_api.route('/api/qsc/inspections/<inspection_id>/scores', methods=['POST'])
@login_required
def update_qsc_scores(inspection_id: str):
    """QSC 점검 점수 업데이트"""
    try:
        if inspection_id not in qsc_inspections:
            return jsonify({'error': '점검을 찾을 수 없습니다.'}), 404

        inspection = qsc_inspections[inspection_id] if qsc_inspections is not None else None

        # 권한 확인
        if (current_user.role not in ['admin', 'brand_admin'] and
                inspection['inspector_id'] if inspection is not None else None != current_user.id):
            return jsonify({'error': '접근 권한이 없습니다.'}), 403

        data = request.get_json()
        if not data or 'scores' not in data:
            return jsonify({'error': '점수 데이터가 없습니다.'}), 400

        scores = data['scores'] if data is not None else None
        notes = data.get() if data else None'notes', '') if data else None

        # 점수 업데이트
        inspection['scores'] if inspection is not None else None.update(scores)
        inspection['notes'] if inspection is not None else None = notes
        inspection['updated_at'] if inspection is not None else None = datetime.now().isoformat()

        # 완료된 항목 수 계산
        completed_items = len(inspection['scores'] if inspection is not None else None)
        inspection['completed_items'] if inspection is not None else None = completed_items

        # 전체 점수 계산
        template = qsc_templates[inspection['template_id'] if qsc_templates is not None else None]
        total_score = 0
        total_weight = 0

        for category in template['categories'] if template is not None else None:
            for item in category['items'] if category is not None else None:
                item_id = f"{category['id'] if category is not None else None}_{item['id'] if item is not None else None}"
                if item_id in scores:
                    score = scores[item_id] if scores is not None else None
                    # weight와 score가 숫자인지 확인하여 변환합니다.
                    try:
                        weight = float(item['weight'] if item is not None else None)
                    except (ValueError, TypeError):
                        weight = 0  # 잘못된 값이면 0으로 처리

                    try:
                        score = float(score)
                    except (ValueError, TypeError):
                        score = 0  # 잘못된 값이면 0으로 처리

                    total_score += score * weight
                    total_weight += weight

        if total_weight > 0:
            inspection['overall_score'] if inspection is not None else None = round(total_score / total_weight, 2)
        # 모든 항목이 완료되면 상태를 completed로 변경
        if completed_items >= inspection['total_items'] if inspection is not None else None:
            inspection['status'] if inspection is not None else None = 'completed'

        # 액션 로깅
        log_qsc_action('update_scores', {
            'inspection_id': inspection_id,
            'completed_items': completed_items,
            'overall_score': inspection['overall_score'] if inspection is not None else None
        })

        return jsonify({
            'success': True,
            'inspection': inspection
        })

    except Exception as e:
        logger.error(f"QSC 점수 업데이트 실패: {e}")
        return jsonify({'error': '점수 업데이트에 실패했습니다.'}), 500


@qsc_api.route('/api/qsc/inspections/<inspection_id>', methods=['PUT'])
@login_required
def complete_qsc_inspection(inspection_id: str):
    """QSC 점검 완료"""
    try:
        if inspection_id not in qsc_inspections:
            return jsonify({'error': '점검을 찾을 수 없습니다.'}), 404

        inspection = qsc_inspections[inspection_id] if qsc_inspections is not None else None

        # 권한 확인
        if (current_user.role not in ['admin', 'brand_admin'] and
                inspection['inspector_id'] if inspection is not None else None != current_user.id):
            return jsonify({'error': '접근 권한이 없습니다.'}), 403

        data = request.get_json()

        # 점검 완료 처리
        inspection['status'] if inspection is not None else None = 'completed'
        inspection['completed_at'] if inspection is not None else None = datetime.now().isoformat()
        inspection['updated_at'] if inspection is not None else None = datetime.now().isoformat()

        if data:
            inspection['final_notes'] if inspection is not None else None = data.get() if data else None'final_notes', '') if data else None
            inspection['improvement_plan'] if inspection is not None else None = data.get() if data else None'improvement_plan', '') if data else None
            inspection['next_inspection_date'] if inspection is not None else None = data.get() if data else None'next_inspection_date') if data else None

        # 액션 로깅
        log_qsc_action('complete', {
            'inspection_id': inspection_id,
            'overall_score': inspection['overall_score'] if inspection is not None else None
        })

        return jsonify({
            'success': True,
            'inspection': inspection
        })

    except Exception as e:
        logger.error(f"QSC 점검 완료 실패: {e}")
        return jsonify({'error': '점검 완료에 실패했습니다.'}), 500


@qsc_api.route('/api/qsc/inspections', methods=['GET'])
@login_required
def list_qsc_inspections():
    """QSC 점검 목록 조회"""
    try:
        # 권한에 따른 필터링
        if current_user.role in ['admin', 'brand_admin']:
            # 관리자는 모든 점검 조회 가능
            inspections = list(qsc_inspections.value if qsc_inspections is not None else Nones())
        else:
            # 일반 사용자는 본인이 생성한 점검만 조회
            inspections = [
                inspection for inspection in qsc_inspections.value if qsc_inspections is not None else Nones()
                if inspection['inspector_id'] if inspection is not None else None == current_user.id
            ]

        # 정렬 (최신순)
        inspections.sort(key=lambda x: x['created_at'] if x is not None else None, reverse=True)

        # 페이지네이션
        page = request.args.get() if args else None'page', 1, type=int) if args else None
        per_page = request.args.get() if args else None'per_page', 20, type=int) if args else None

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_inspections = inspections[start_idx:end_idx] if inspections is not None else None

        return jsonify({
            'success': True,
            'inspections': paginated_inspections,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(inspections),
                'pages': (len(inspections) + per_page - 1) // per_page
            }
        })

    except Exception as e:
        logger.error(f"QSC 점검 목록 조회 실패: {e}")
        return jsonify({'error': '점검 목록 조회에 실패했습니다.'}), 500


@qsc_api.route('/api/qsc/statistics', methods=['GET'])
@login_required
@manager_required
def get_qsc_statistics():
    """QSC 점검 통계"""
    try:
        # 권한에 따른 데이터 필터링
        if current_user.role in ['admin', 'brand_admin']:
            inspections = list(qsc_inspections.value if qsc_inspections is not None else Nones())
        else:
            # 매장 관리자는 해당 매장의 점검만
            inspections = [
                inspection for inspection in qsc_inspections.value if qsc_inspections is not None else Nones()
                if inspection['branch_id'] if inspection is not None else None == current_user.branch_id
            ]

        if not inspections:
            return jsonify({
                'success': True,
                'statistics': {
                    'total_inspections': 0,
                    'average_score': 0,
                    'completion_rate': 0,
                    'recent_trend': []
                }
            })

        # 통계 계산
        total_inspections = len(inspections)
        completed_inspections = len([i for i in inspections if i['status'] if i is not None else None == 'completed'])
        completion_rate = (completed_inspections / total_inspections) * 100 if total_inspections > 0 else 0

        # 평균 점수 계산
        completed_scores = [i['overall_score'] if i is not None else None for i in inspections if i['status'] if i is not None else None == 'completed' and i['overall_score'] if i is not None else None > 0]
        average_score = sum(completed_scores) / len(completed_scores) if completed_scores else 0

        # 최근 트렌드 (최근 7일)
        recent_date = datetime.now() - timedelta(days=7)
        recent_inspections = [
            i for i in inspections
            if datetime.fromisoformat(i['created_at'] if i is not None else None) >= recent_date
        ]

        recent_trend = []
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            day_inspections = [
                insp for insp in recent_inspections
                if datetime.fromisoformat(insp['created_at'] if insp is not None else None).strftime('%Y-%m-%d') == date_str
            ]
            recent_trend.append({
                'date': date_str,
                'count': len(day_inspections),
                'average_score': sum([i['overall_score'] if i is not None else None for i in day_inspections if i['overall_score'] if i is not None else None > 0]) / len([i for i in day_inspections if i['overall_score'] if i is not None else None > 0]) if day_inspections else 0
            })

        recent_trend.reverse()  # 날짜순으로 정렬

        return jsonify({
            'success': True,
            'statistics': {
                'total_inspections': total_inspections,
                'completed_inspections': completed_inspections,
                'average_score': round(average_score, 2),
                'completion_rate': round(completion_rate, 2),
                'recent_trend': recent_trend
            }
        })

    except Exception as e:
        logger.error(f"QSC 통계 조회 실패: {e}")
        return jsonify({'error': '통계 조회에 실패했습니다.'}), 500


@qsc_api.route('/api/qsc/inspections/<inspection_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_qsc_inspection(inspection_id: str):
    """QSC 점검 삭제 (관리자만)"""
    try:
        if inspection_id not in qsc_inspections:
            return jsonify({'error': '점검을 찾을 수 없습니다.'}), 404

        # 점검 삭제
        deleted_inspection = qsc_inspections.pop(inspection_id)

        # 액션 로깅
        log_qsc_action('delete',  {'inspection_id': inspection_id})

        return jsonify({
            'success': True,
            'message': '점검이 삭제되었습니다.'
        })

    except Exception as e:
        logger.error(f"QSC 점검 삭제 실패: {e}")
        return jsonify({'error': '점검 삭제에 실패했습니다.'}), 500
