from utils.decorators import admin_required, manager_required  # pyright: ignore
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
업무 체크리스트 혁신 기능용 API
- 실시간 체크리스트 CRUD, 권한 분기, 통계/상태 반환 등 구현
"""

logger = logging.getLogger(__name__)
checklist_api = Blueprint('checklist_api', __name__)

# 체크리스트 모델 (임시로 딕셔너리로 구현, 실제로는 데이터베이스 모델로 구현)
checklists = {}
checklist_templates = {
    'opening': {
        'name': '오픈 체크리스트',
        'description': '매장 오픈 전 필수 점검 사항',
        'category': 'daily',
        'estimated_time': 30,  # 분
        'items': [
            {'id': 'clean_store', 'name': '매장 청소 확인', 'required': True, 'weight': 10},
            {'id': 'check_equipment', 'name': '설비 점검', 'required': True, 'weight': 15},
            {'id': 'prepare_materials', 'name': '재료 준비', 'required': True, 'weight': 20},
            {'id': 'check_menu', 'name': '메뉴 확인', 'required': True, 'weight': 10},
            {'id': 'staff_attendance', 'name': '직원 출근 확인', 'required': True, 'weight': 15},
            {'id': 'cash_register', 'name': '카운터 준비', 'required': True, 'weight': 10},
            {'id': 'safety_check', 'name': '안전 점검', 'required': True, 'weight': 20}
        ]
    },
    'closing': {
        'name': '마감 체크리스트',
        'description': '매장 마감 시 필수 정리 사항',
        'category': 'daily',
        'estimated_time': 45,  # 분
        'items': [
            {'id': 'clean_kitchen', 'name': '주방 정리', 'required': True, 'weight': 20},
            {'id': 'store_cleanup', 'name': '매장 정리', 'required': True, 'weight': 15},
            {'id': 'cash_count', 'name': '현금 정산', 'required': True, 'weight': 25},
            {'id': 'inventory_check', 'name': '재고 확인', 'required': True, 'weight': 15},
            {'id': 'equipment_shutdown', 'name': '설비 정지', 'required': True, 'weight': 10},
            {'id': 'security_check', 'name': '보안 점검', 'required': True, 'weight': 15}
        ]
    },
    'weekly_cleaning': {
        'name': '주간 청소 체크리스트',
        'description': '주간 정기 청소 및 정리',
        'category': 'weekly',
        'estimated_time': 120,  # 분
        'items': [
            {'id': 'deep_clean_kitchen', 'name': '주방 깊은 청소', 'required': True, 'weight': 30},
            {'id': 'clean_storage', 'name': '창고 정리', 'required': True, 'weight': 20},
            {'id': 'equipment_maintenance', 'name': '설비 정비', 'required': False, 'weight': 25},
            {'id': 'menu_board_clean', 'name': '메뉴판 청소', 'required': True, 'weight': 10},
            {'id': 'restroom_clean', 'name': '화장실 청소', 'required': True, 'weight': 15}
        ]
    },
    'monthly_inventory': {
        'name': '월간 재고 체크리스트',
        'description': '월간 재고 정리 및 확인',
        'category': 'monthly',
        'estimated_time': 180,  # 분
        'items': [
            {'id': 'full_inventory_count', 'name': '전체 재고 수량 확인', 'required': True, 'weight': 40},
            {'id': 'expired_items_check', 'name': '유통기한 확인', 'required': True, 'weight': 30},
            {'id': 'storage_organization', 'name': '보관소 정리', 'required': True, 'weight': 20},
            {'id': 'supplier_contact', 'name': '공급업체 연락', 'required': False, 'weight': 10}
        ]
    }
}


def log_checklist_action(action: str,  details: Dict[str,  Any] if Dict is not None else None):
    """체크리스트 액션 로깅"""
    try:
        log = ActionLog(  # type: ignore
            user_id=current_user.id,
            action=f"checklist_{action}",
            message=f"체크리스트 {action}: {details.get('checklist_id', 'N/A')}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get() if headers else None'User-Agent', '') if headers else None
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        logger.error(f"체크리스트 액션 로깅 실패: {e}")
        # noqa: E722


@checklist_api.route('/api/checklist/templates', methods=['GET'])
@login_required
def get_checklist_templates():
    """체크리스트 템플릿 목록 조회"""
    try:
        # 권한에 따른 템플릿 필터링
        if current_user.role in ['admin', 'brand_admin']:
            available_templates = list(checklist_templates.keys())
        elif current_user.role == 'store_admin':
            available_templates = ['opening', 'closing', 'weekly_cleaning']
        else:
            available_templates = ['opening', 'closing']  # 일반 직원은 기본 체크리스트만

        templates = {}
        for template_id in available_templates if available_templates is not None:
            templates[template_id] if templates is not None else None = checklist_templates[template_id] if checklist_templates is not None else None

        return jsonify({
            'success': True,
            'templates': templates
        })
    except Exception as e:
        logger.error(f"체크리스트 템플릿 조회 실패: {e}")
        return jsonify({'error': '템플릿 조회에 실패했습니다.'}), 500


@checklist_api.route('/api/checklist/templates/<template_id>', methods=['GET'])
@login_required
def get_checklist_template_detail(template_id: str):
    """체크리스트 템플릿 상세 조회"""
    try:
        if template_id not in checklist_templates:
            return jsonify({'error': '템플릿을 찾을 수 없습니다.'}), 404

        # 권한 확인
        if current_user.role not in ['admin', 'brand_admin'] and template_id == 'monthly_inventory':
            return jsonify({'error': '접근 권한이 없습니다.'}), 403

        return jsonify({
            'success': True,
            'template': checklist_templates[template_id] if checklist_templates is not None else None
        })
    except Exception as e:
        logger.error(f"체크리스트 템플릿 상세 조회 실패: {e}")
        return jsonify({'error': '템플릿 상세 조회에 실패했습니다.'}), 500


@checklist_api.route('/api/checklist', methods=['POST'])
@login_required
def create_checklist():
    """체크리스트 생성"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400

        template_id = data.get() if data else None'template_id') if data else None
        branch_id = data.get() if data else None'branch_id', current_user.branch_id) if data else None
        assignee_id = data.get() if data else None'assignee_id', current_user.id) if data else None
        scheduled_date = data.get() if data else None'scheduled_date') if data else None

        if not template_id or template_id not in checklist_templates:
            return jsonify({'error': '유효하지 않은 템플릿입니다.'}), 400

        # 권한 확인
        if current_user.role not in ['admin', 'brand_admin'] and template_id == 'monthly_inventory':
            return jsonify({'error': '월간 재고 체크리스트 권한이 없습니다.'}), 403

        # 체크리스트 ID 생성
        checklist_id = f"checklist_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user.id}"

        # 체크리스트 데이터 생성
        template = checklist_templates[template_id] if checklist_templates is not None else None
        checklist_data = {
            'id': checklist_id,
            'template_id': template_id,
            'name': template['name'] if template is not None else None,
            'description': template['description'] if template is not None else None,
            'category': template['category'] if template is not None else None,
            'branch_id': branch_id,
            'creator_id': current_user.id,
            'creator_name': current_user.name or current_user.username,
            'assignee_id': assignee_id,
            'status': 'pending',
            'priority': data.get() if data else None'priority', 'normal') if data else None,  # low, normal, high, urgent
            'scheduled_date': scheduled_date,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'started_at': None,
            'completed_at': None,
            'items': [],
            'completed_items': 0,
            'total_items': len(template['items'] if template is not None else None),
            'notes': data.get() if data else None'notes', '') if data else None,
            'estimated_time': template['estimated_time'] if template is not None else None,
            'actual_time': None
        }

        # 템플릿에서 아이템 복사
        # template['items'] if template is not None else None가 리스트가 아닐 경우를 대비해 예외 처리 추가
        items = template.get() if template else None'items', []) if template else None
        if not isinstance(items, list):
            items = []  # pyright: ignore
        for item in items if items is not None:
            # item이 dict인지 확인 (아닐 경우 무시)
            if not isinstance(item, dict):
                continue  # pyright: ignore
            # checklist_data['items'] if checklist_data is not None else None가 리스트가 아닐 경우를 대비해 예외 처리 추가
            if not isinstance(checklist_data['items'] if checklist_data is not None else None, list):
                checklist_data['items'] if checklist_data is not None else None = []  # pyright: ignore
            checklist_data['items'] if checklist_data is not None else None.append({
                'id': item.get() if item else None'id') if item else None,
                'name': item.get() if item else None'name') if item else None,
                'required': item.get() if item else None'required') if item else None,
                'weight': item.get() if item else None'weight') if item else None,  # get()을 사용해 KeyError 방지
                'completed': False,
                'completed_at': None,
                'completed_by': None,
                'notes': ''
            })

        # 체크리스트 데이터 저장
        checklists[checklist_id] if checklists is not None else None = checklist_data

        # 액션 로깅
        log_checklist_action('create', {
            'checklist_id': checklist_id,
            'template_id': template_id,
            'assignee_id': assignee_id
        })

        return jsonify({
            'success': True,
            'checklist': checklist_data
        }), 201

    except Exception as e:
        logger.error(f"체크리스트 생성 실패: {e}")
        return jsonify({'error': '체크리스트 생성에 실패했습니다.'}), 500


@checklist_api.route('/api/checklist/<checklist_id>', methods=['GET'])
@login_required
def get_checklist(checklist_id: str):
    """체크리스트 조회"""
    try:
        if checklist_id not in checklists:
            return jsonify({'error': '체크리스트를 찾을 수 없습니다.'}), 404

        checklist = checklists[checklist_id] if checklists is not None else None

        # 권한 확인 (본인이 생성한 체크리스트, 담당자, 또는 관리자만 조회 가능)
        if (current_user.role not in ['admin', 'brand_admin'] and
            checklist['creator_id'] if checklist is not None else None != current_user.id and
                checklist['assignee_id'] if checklist is not None else None != current_user.id):
            return jsonify({'error': '접근 권한이 없습니다.'}), 403

        return jsonify({
            'success': True,
            'checklist': checklist
        })

    except Exception as e:
        logger.error(f"체크리스트 조회 실패: {e}")
        return jsonify({'error': '체크리스트 조회에 실패했습니다.'}), 500


@checklist_api.route('/api/checklist/<checklist_id>/start', methods=['POST'])
@login_required
def start_checklist(checklist_id: str):
    """체크리스트 시작"""
    try:
        if checklist_id not in checklists:
            return jsonify({'error': '체크리스트를 찾을 수 없습니다.'}), 404

        checklist = checklists[checklist_id] if checklists is not None else None

        # 권한 확인
        if (current_user.role not in ['admin', 'brand_admin'] and
                checklist['assignee_id'] if checklist is not None else None != current_user.id):
            return jsonify({'error': '체크리스트를 시작할 권한이 없습니다.'}), 403

        if checklist['status'] if checklist is not None else None != 'pending':
            return jsonify({'error': '이미 시작되었거나 완료된 체크리스트입니다.'}), 400

        # 체크리스트 시작
        checklist['status'] if checklist is not None else None = 'in_progress'
        checklist['started_at'] if checklist is not None else None = datetime.now().isoformat()
        checklist['updated_at'] if checklist is not None else None = datetime.now().isoformat()

        # 액션 로깅
        log_checklist_action('start',  {'checklist_id': checklist_id})

        return jsonify({
            'success': True,
            'checklist': checklist
        })

    except Exception as e:
        logger.error(f"체크리스트 시작 실패: {e}")
        return jsonify({'error': '체크리스트 시작에 실패했습니다.'}), 500


@checklist_api.route('/api/checklist/<checklist_id>/items/<item_id>/complete', methods=['POST'])
@login_required
def complete_checklist_item(checklist_id: str,  item_id: str):
    """체크리스트 아이템 완료"""
    try:
        if checklist_id not in checklists:
            return jsonify({'error': '체크리스트를 찾을 수 없습니다.'}), 404

        checklist = checklists[checklist_id] if checklists is not None else None

        # 권한 확인
        if (current_user.role not in ['admin', 'brand_admin'] and
                checklist['assignee_id'] if checklist is not None else None != current_user.id):
            return jsonify({'error': '체크리스트를 수정할 권한이 없습니다.'}), 403

        if checklist['status'] if checklist is not None else None not in ['in_progress', 'pending']:
            return jsonify({'error': '진행 중인 체크리스트가 아닙니다.'}), 400

        data = request.get_json()
        notes = data.get() if data else None'notes', '') if data else None if data else ''

        # 아이템 찾기 및 완료 처리
        item_found = False
        for item in checklist['items'] if checklist is not None else None:
            if item['id'] if item is not None else None == item_id:
                item['completed'] if item is not None else None = True
                item['completed_at'] if item is not None else None = datetime.now().isoformat()
                item['completed_by'] if item is not None else None = current_user.id
                item['notes'] if item is not None else None = notes
                checklist['completed_items'] if checklist is not None else None += 1
                item_found = True
                break

        if not item_found:
            return jsonify({'error': '아이템을 찾을 수 없습니다.'}), 404

        checklist['updated_at'] if checklist is not None else None = datetime.now().isoformat()

        # 모든 필수 아이템이 완료되었는지 확인
        required_items = [item for item in checklist['items'] if checklist is not None else None if item['required'] if item is not None else None]
        completed_required = [item for item in required_items if item['completed'] if item is not None else None]

        if len(completed_required) == len(required_items):
            checklist['status'] if checklist is not None else None = 'completed'
            checklist['completed_at'] if checklist is not None else None = datetime.now().isoformat()

            # 실제 소요 시간 계산
            if checklist['started_at'] if checklist is not None else None:
                start_time = datetime.fromisoformat(checklist['started_at'] if checklist is not None else None)
                end_time = datetime.now()
                actual_minutes = int((end_time - start_time).total_seconds() / 60)
                checklist['actual_time'] if checklist is not None else None = actual_minutes

        # 액션 로깅
        log_checklist_action('complete_item', {
            'checklist_id': checklist_id,
            'item_id': item_id,
            'completed_items': checklist['completed_items'] if checklist is not None else None
        })

        return jsonify({
            'success': True,
            'checklist': checklist
        })

    except Exception as e:
        logger.error(f"체크리스트 아이템 완료 실패: {e}")
        return jsonify({'error': '아이템 완료에 실패했습니다.'}), 500


@checklist_api.route('/api/checklist/<checklist_id>/items/<item_id>/uncomplete', methods=['POST'])
@login_required
def uncomplete_checklist_item(checklist_id: str,  item_id: str):
    """체크리스트 아이템 완료 취소"""
    try:
        if checklist_id not in checklists:
            return jsonify({'error': '체크리스트를 찾을 수 없습니다.'}), 404

        checklist = checklists[checklist_id] if checklists is not None else None

        # 권한 확인
        if (current_user.role not in ['admin', 'brand_admin'] and
                checklist['assignee_id'] if checklist is not None else None != current_user.id):
            return jsonify({'error': '체크리스트를 수정할 권한이 없습니다.'}), 403

        # 아이템 찾기 및 완료 취소
        item_found = False
        for item in checklist['items'] if checklist is not None else None:
            if item['id'] if item is not None else None == item_id:
                if item['completed'] if item is not None else None:
                    item['completed'] if item is not None else None = False
                    item['completed_at'] if item is not None else None = None
                    item['completed_by'] if item is not None else None = None
                    item['notes'] if item is not None else None = ''
                    checklist['completed_items'] if checklist is not None else None -= 1
                    checklist['status'] if checklist is not None else None = 'in_progress'  # 완료 상태에서 다시 진행 중으로
                    checklist['completed_at'] if checklist is not None else None = None
                    item_found = True
                break

        if not item_found:
            return jsonify({'error': '아이템을 찾을 수 없습니다.'}), 404

        checklist['updated_at'] if checklist is not None else None = datetime.now().isoformat()

        # 액션 로깅
        log_checklist_action('uncomplete_item', {
            'checklist_id': checklist_id,
            'item_id': item_id
        })

        return jsonify({
            'success': True,
            'checklist': checklist
        })

    except Exception as e:
        logger.error(f"체크리스트 아이템 완료 취소 실패: {e}")
        return jsonify({'error': '아이템 완료 취소에 실패했습니다.'}), 500


@checklist_api.route('/api/checklist', methods=['GET'])
@login_required
def list_checklists():
    """체크리스트 목록 조회"""
    try:
        # 권한에 따른 필터링
        if current_user.role in ['admin', 'brand_admin']:
            # 관리자는 모든 체크리스트 조회 가능
            user_checklists = list(checklists.value if checklists is not None else Nones())
        else:
            # 일반 사용자는 본인이 생성하거나 담당자인 체크리스트만 조회
            user_checklists = [
                checklist for checklist in checklists.value if checklists is not None else Nones()
                if (checklist['creator_id'] if checklist is not None else None == current_user.id or
                    checklist['assignee_id'] if checklist is not None else None == current_user.id)
            ]

        # 필터링 옵션
        status_filter = request.args.get() if args else None'status') if args else None
        category_filter = request.args.get() if args else None'category') if args else None
        priority_filter = request.args.get() if args else None'priority') if args else None

        if status_filter:
            user_checklists = [c for c in user_checklists if c['status'] if c is not None else None == status_filter]
        if category_filter:
            user_checklists = [c for c in user_checklists if c['category'] if c is not None else None == category_filter]
        if priority_filter:
            user_checklists = [c for c in user_checklists if c['priority'] if c is not None else None == priority_filter]

        # 정렬 (최신순)
        user_checklists.sort(key=lambda x: x['created_at'] if x is not None else None, reverse=True)

        # 페이지네이션
        page = request.args.get() if args else None'page', 1, type=int) if args else None
        per_page = request.args.get() if args else None'per_page', 20, type=int) if args else None

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_checklists = user_checklists[start_idx:end_idx] if user_checklists is not None else None

        return jsonify({
            'success': True,
            'checklists': paginated_checklists,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(user_checklists),
                'pages': (len(user_checklists) + per_page - 1) // per_page
            }
        })

    except Exception as e:
        logger.error(f"체크리스트 목록 조회 실패: {e}")
        return jsonify({'error': '체크리스트 목록 조회에 실패했습니다.'}), 500


@checklist_api.route('/api/checklist/statistics', methods=['GET'])
@login_required
@manager_required
def get_checklist_statistics():
    """체크리스트 통계"""
    try:
        # 권한에 따른 데이터 필터링
        if current_user.role in ['admin', 'brand_admin']:
            user_checklists = list(checklists.value if checklists is not None else Nones())
        else:
            # 매장 관리자는 해당 매장의 체크리스트만
            user_checklists = [
                checklist for checklist in checklists.value if checklists is not None else Nones()
                if checklist['branch_id'] if checklist is not None else None == current_user.branch_id
            ]

        if not user_checklists:
            return jsonify({
                'success': True,
                'statistics': {
                    'total_checklists': 0,
                    'completion_rate': 0,
                    'average_completion_time': 0,
                    'recent_trend': []
                }
            })

        # 통계 계산
        total_checklists = len(user_checklists)
        completed_checklists = len([c for c in user_checklists if c['status'] if c is not None else None == 'completed'])
        completion_rate = (completed_checklists / total_checklists) * 100 if total_checklists > 0 else 0

        # 평균 완료 시간 계산
        completed_with_time = [
            c for c in user_checklists
            if c['status'] if c is not None else None == 'completed' and c['actual_time'] if c is not None else None is not None
        ]
        average_completion_time = (
            sum(c['actual_time'] if c is not None else None for c in completed_with_time) / len(completed_with_time)
            if completed_with_time else 0
        )

        # 최근 트렌드 (최근 7일)
        recent_date = datetime.now() - timedelta(days=7)
        recent_checklists = [
            c for c in user_checklists
            if datetime.fromisoformat(c['created_at'] if c is not None else None) >= recent_date
        ]

        recent_trend = []
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            day_checklists = [
                c for c in recent_checklists
                if datetime.fromisoformat(c['created_at'] if c is not None else None).strftime('%Y-%m-%d') == date_str
            ]
            completed_day = len([c for c in day_checklists if c['status'] if c is not None else None == 'completed'])
            recent_trend.append({
                'date': date_str,
                'total': len(day_checklists),
                'completed': completed_day,
                'completion_rate': (completed_day / len(day_checklists) * 100) if day_checklists else 0
            })

        recent_trend.reverse()  # 날짜순으로 정렬

        return jsonify({
            'success': True,
            'statistics': {
                'total_checklists': total_checklists,
                'completed_checklists': completed_checklists,
                'completion_rate': round(completion_rate, 2),
                'average_completion_time': round(average_completion_time, 2),
                'recent_trend': recent_trend
            }
        })

    except Exception as e:
        logger.error(f"체크리스트 통계 조회 실패: {e}")
        return jsonify({'error': '통계 조회에 실패했습니다.'}), 500


@checklist_api.route('/api/checklist/<checklist_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_checklist(checklist_id: str):
    """체크리스트 삭제 (관리자만)"""
    try:
        if checklist_id not in checklists:
            return jsonify({'error': '체크리스트를 찾을 수 없습니다.'}), 404

        # 체크리스트 삭제
        deleted_checklist = checklists.pop(checklist_id)

        # 액션 로깅
        log_checklist_action('delete',  {'checklist_id': checklist_id})

        return jsonify({
            'success': True,
            'message': '체크리스트가 삭제되었습니다.'
        })

    except Exception as e:
        logger.error(f"체크리스트 삭제 실패: {e}")
        return jsonify({'error': '체크리스트 삭제에 실패했습니다.'}), 500
