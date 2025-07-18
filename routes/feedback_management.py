import logging
from datetime import datetime, timedelta
from extensions import db
from models_main import User, Brand, Branch, SystemLog, Suggestion
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, render_template
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
피드백 관리 시스템
브랜드 관리자 및 직원들의 피드백 수집 및 응답 관리
"""


logger = logging.getLogger(__name__)

feedback_management_bp = Blueprint('feedback_management', __name__, url_prefix='/admin/feedback-management')


@feedback_management_bp.route('/', methods=['GET'])
@login_required
def feedback_management_page():
    """피드백 관리 페이지"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    return render_template('admin/feedback_management.html')


@feedback_management_bp.route('/api/feedbacks', methods=['GET'])
@login_required
def get_feedbacks():
    """피드백 목록 조회"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        # 페이지네이션 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # 필터링 파라미터
        status = request.args.get('status', 'all')
        category = request.args.get('category', 'all')

        # 쿼리 구성
        query = Suggestion.query

        if status != 'all':
            if status == 'answered':
                query = query.filter(Suggestion.answer.isnot(None))
            elif status == 'unanswered':
                query = query.filter(Suggestion.answer.is_(None))

        # 최신순 정렬
        query = query.order_by(Suggestion.created_at.desc())

        # 페이지네이션
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        feedback_list = []
        for suggestion in pagination.items:
            # 사용자 정보
            user = User.query.get(suggestion.user_id) if query else None

            # 브랜드 정보
            brand = Brand.query.get(user.brand_id) if query and user and user.brand_id else None

            feedback_list.append({
                'suggestion_id': suggestion.id,
                'user_id': suggestion.user_id,
                'user_name': user.name if user else '알 수 없음',
                'user_email': user.email if user else '알 수 없음',
                'brand_name': brand.name if brand else '미지정',
                'content': suggestion.content,
                'answer': suggestion.answer,
                'is_anonymous': suggestion.is_anonymous,
                'created_at': suggestion.created_at.isoformat(),
                'answered_at': suggestion.answered_at.isoformat() if suggestion.answered_at else None,
                'status': 'answered' if suggestion.answer else 'unanswered'
            })

        # 통계 데이터 계산
        total_feedback = Suggestion.query.count()
        pending_feedback = Suggestion.query.filter(Suggestion.answer.is_(None)).count()
        answered_feedback = Suggestion.query.filter(Suggestion.answer.isnot(None)).count()

        # 평균 만족도 계산 (만약 만족도 필드가 있다면)
        avg_satisfaction = 0.0  # 기본값

        return jsonify({
            'success': True,
            'feedbacks': feedback_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'statistics': {
                'total': total_feedback,
                'pending': pending_feedback,
                'answered': answered_feedback,
                'avg_satisfaction': avg_satisfaction
            }
        })

    except Exception as e:
        logger.error(f"피드백 목록 조회 오류: {str(e)}")
        return jsonify({'error': '데이터 조회 중 오류가 발생했습니다.'}), 500


@feedback_management_bp.route('/api/feedback/<int:suggestion_id>/details', methods=['GET'])
@login_required
def get_feedback_details(suggestion_id):
    """피드백 상세 정보 조회"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        suggestion = Suggestion.query.get(suggestion_id) if query else None
        if not suggestion:
            return jsonify({'error': '피드백을 찾을 수 없습니다.'}), 404

        # 사용자 정보
        user = User.query.get(suggestion.user_id) if query else None

        # 브랜드 정보
        brand = Brand.query.get(user.brand_id) if query and user and user.brand_id else None

        # 매장 정보
        branch = Branch.query.get(user.branch_id) if query and user and user.branch_id else None

        # 관련 피드백 (같은 사용자의 다른 피드백)
        related_feedbacks = Suggestion.query.filter(
            Suggestion.user_id == suggestion.user_id,
            Suggestion.id != suggestion.id
        ).order_by(Suggestion.created_at.desc()).limit(5).all()

        related_list = []
        for related in related_feedbacks or []:
            related_list.append({
                'suggestion_id': related.id,
                'content': (related.content[:100] + '...') if len(related.content) > 100 else related.content,
                'answer': related.answer,
                'created_at': related.created_at.isoformat(),
                'status': 'answered' if related.answer else 'unanswered'
            })

        return jsonify({
            'success': True,
            'feedback': {
                'suggestion_id': suggestion.id,
                'user_id': suggestion.user_id,
                'user_name': user.name if user else '알 수 없음',
                'user_email': user.email if user else '알 수 없음',
                'user_role': user.role if user else '알 수 없음',
                'brand_name': brand.name if brand else '미지정',
                'store_name': branch.name if branch else '미지정',
                'content': suggestion.content,
                'answer': suggestion.answer,
                'is_anonymous': suggestion.is_anonymous,
                'created_at': suggestion.created_at.isoformat(),
                'answered_at': suggestion.answered_at.isoformat() if suggestion.answered_at else None,
                'status': 'answered' if suggestion.answer else 'unanswered'
            },
            'related_feedbacks': related_list
        })

    except Exception as e:
        logger.error(f"피드백 상세 정보 조회 오류: {str(e)}")
        return jsonify({'error': '데이터 조회 중 오류가 발생했습니다.'}), 500


@feedback_management_bp.route('/api/feedback/<int:suggestion_id>/answer', methods=['POST'])
@login_required
def answer_feedback(suggestion_id):
    """피드백 답변"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        data = request.get_json()
        answer_content = data.get('answer', '').strip() if data else ''

        if not answer_content:
            return jsonify({'error': '답변 내용을 입력해주세요.'}), 400

        suggestion = Suggestion.query.get(suggestion_id) if query else None
        if not suggestion:
            return jsonify({'error': '피드백을 찾을 수 없습니다.'}), 404

        if suggestion.answer:
            return jsonify({'error': '이미 답변이 작성된 피드백입니다.'}), 400

        # 답변 저장
        suggestion.answer = answer_content
        suggestion.answered_at = datetime.utcnow()

        # 시스템 로그 기록
        log = SystemLog()
        log.user_id = current_user.id  # pyright: ignore
        log.action = 'feedback_answer'  # pyright: ignore
        log.detail = f'피드백 답변: {suggestion.id}'  # pyright: ignore
        log.ip_address = request.remote_addr  # pyright: ignore
        db.session.add(log)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '피드백에 답변이 작성되었습니다.'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"피드백 답변 오류: {str(e)}")
        return jsonify({'error': '답변 작성 중 오류가 발생했습니다.'}), 500


@feedback_management_bp.route('/api/feedback/<int:suggestion_id>/update-answer', methods=['PUT'])
@login_required
def update_feedback_answer(suggestion_id):
    """피드백 답변 수정"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        data = request.get_json()
        answer_content = data.get('answer', '').strip() if data else ''

        if not answer_content:
            return jsonify({'error': '답변 내용을 입력해주세요.'}), 400

        suggestion = Suggestion.query.get(suggestion_id) if query else None
        if not suggestion:
            return jsonify({'error': '피드백을 찾을 수 없습니다.'}), 404

        if not suggestion.answer:
            return jsonify({'error': '아직 답변이 작성되지 않은 피드백입니다.'}), 400

        # 답변 수정
        suggestion.answer = answer_content
        suggestion.answered_at = datetime.utcnow()

        # 시스템 로그 기록
        log = SystemLog()  # pyright: ignore
        log.user_id = current_user.id  # pyright: ignore
        log.action = 'feedback_answer_update'  # pyright: ignore
        log.detail = f'피드백 답변 수정: {suggestion.id}'  # pyright: ignore
        log.ip_address = request.remote_addr  # pyright: ignore
        db.session.add(log)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '피드백 답변이 수정되었습니다.'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"피드백 답변 수정 오류: {str(e)}")
        return jsonify({'error': '답변 수정 중 오류가 발생했습니다.'}), 500


@feedback_management_bp.route('/api/feedback/analytics', methods=['GET'])
@login_required
def get_feedback_analytics():
    """피드백 분석 데이터"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        # 최근 30일 데이터
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=30)

        # 전체 피드백 통계
        total_feedbacks = Suggestion.query.count()
        answered_feedbacks = Suggestion.query.filter(Suggestion.answer.isnot(None)).count()
        unanswered_feedbacks = total_feedbacks - answered_feedbacks

        # 최근 30일 피드백
        recent_feedbacks = Suggestion.query.filter(
            Suggestion.created_at >= start_date
        ).all()

        recent_stats = {
            'total': len(recent_feedbacks),
            'answered': len([f for f in recent_feedbacks if f.answer]),
            'unanswered': len([f for f in recent_feedbacks if not f.answer]),
            'anonymous': len([f for f in recent_feedbacks if f.is_anonymous])
        }

        # 브랜드별 피드백 통계
        brands = Brand.query.all()
        brand_stats = []

        for brand in brands or []:
            # 해당 브랜드 사용자들의 피드백
            brand_users = User.query.filter_by(brand_id=brand.id).all()
            user_ids = [user.id for user in brand_users]

            if user_ids:
                brand_feedbacks = Suggestion.query.filter(
                    Suggestion.user_id.in_(user_ids)
                ).all()

                brand_stats.append({
                    'brand_id': brand.id,
                    'brand_name': brand.name,
                    'total_feedbacks': len(brand_feedbacks),
                    'answered_feedbacks': len([f for f in brand_feedbacks if f.answer]),
                    'unanswered_feedbacks': len([f for f in brand_feedbacks if not f.answer])
                })

        # 월별 피드백 추이
        monthly_feedbacks = {}
        for feedback in recent_feedbacks or []:
            month_key = feedback.created_at.strftime('%Y-%m')
            if month_key not in monthly_feedbacks:
                monthly_feedbacks[month_key] = 0
            monthly_feedbacks[month_key] += 1

        return jsonify({
            'success': True,
            'analytics': {
                'overall_stats': {
                    'total_feedbacks': total_feedbacks,
                    'answered_feedbacks': answered_feedbacks,
                    'unanswered_feedbacks': unanswered_feedbacks,
                    'answer_rate': (answered_feedbacks / total_feedbacks * 100) if total_feedbacks > 0 else 0
                },
                'recent_stats': recent_stats,
                'brand_stats': brand_stats,
                'monthly_trend': monthly_feedbacks,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }
        })

    except Exception as e:
        logger.error(f"피드백 분석 데이터 조회 오류: {str(e)}")
        return jsonify({'error': '분석 데이터 조회 중 오류가 발생했습니다.'}), 500
