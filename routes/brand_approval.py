import logging
from datetime import datetime
from extensions import db
from models_main import User, Brand, Branch, Staff, SystemLog
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, render_template
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
브랜드 관리자 승인 시스템
브랜드 관리자 계정 생성 및 승인 관리
"""


logger = logging.getLogger(__name__)

brand_approval_bp = Blueprint('brand_approval', __name__, url_prefix='/admin/brand-approval')


@brand_approval_bp.route('/', methods=['GET'])
def brand_approval_page():
    """브랜드 관리자 승인 페이지"""
    # 로그인하지 않은 사용자도 페이지에 접속 가능하도록 수정
    return render_template('admin/brand_approval.html')


@brand_approval_bp.route('/api/pending-approvals', methods=['GET'])
@login_required
def get_pending_approvals():
    """승인 대기 중인 브랜드 관리자 목록"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        # 승인 대기 중인 브랜드 관리자
        pending_users = User.query.filter_by(
            role='brand_admin',
            status='pending'
        ).all()

        approvals = []
        for user in pending_users:
            # 브랜드 정보 조회
            brand = Brand.query.filter_by(admin_id=user.id).first()

            approvals.append({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'phone': user.phone,
                'brand_name': brand.name if brand else '미지정',
                'brand_id': brand.id if brand else None,
                'created_at': user.created_at.isoformat(),
                'request_date': user.created_at.strftime('%Y-%m-%d %H:%M')
            })

        return jsonify({
            'success': True,
            'approvals': approvals,
            'total_count': len(approvals)
        })

    except Exception as e:
        logger.error(f"승인 대기 목록 조회 오류: {str(e)}")
        return jsonify({'error': '데이터 조회 중 오류가 발생했습니다.'}), 500


@brand_approval_bp.route('/api/approve/<int:user_id>', methods=['POST'])
@login_required
def approve_brand_admin(user_id):
    """브랜드 관리자 승인"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404

        if user.role != 'brand_admin':
            return jsonify({'error': '브랜드 관리자가 아닙니다.'}), 400

        if user.status != 'pending':
            return jsonify({'error': '승인 대기 상태가 아닙니다.'}), 400

        # 사용자 승인
        user.status = 'approved'
        user.approved_at = datetime.utcnow()
        user.approved_by = current_user.id

        # 브랜드 정보 업데이트
        brand = Brand.query.filter_by(admin_id=user.id).first()
        if brand:
            brand.status = 'active'
            brand.updated_at = datetime.utcnow()

        # 시스템 로그 기록
        log = SystemLog(
            user=current_user,  # pyright: ignore
            action='brand_admin_approval',  # pyright: ignore
            detail=f'브랜드 관리자 승인: {user.username} ({user.email})',  # pyright: ignore
            ip_address=request.remote_addr  # pyright: ignore
        )
        db.session.add(log)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'{user.name} 브랜드 관리자가 승인되었습니다.'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"브랜드 관리자 승인 오류: {str(e)}")
        return jsonify({'error': '승인 처리 중 오류가 발생했습니다.'}), 500


@brand_approval_bp.route('/api/reject/<int:user_id>', methods=['POST'])
@login_required
def reject_brand_admin(user_id):
    """브랜드 관리자 거절"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        data = request.get_json()
        reason = data.get('reason', '사유 미지정')

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404

        if user.role != 'brand_admin':
            return jsonify({'error': '브랜드 관리자가 아닙니다.'}), 400

        if user.status != 'pending':
            return jsonify({'error': '승인 대기 상태가 아닙니다.'}), 400

        # 사용자 거절
        user.status = 'rejected'
        user.rejected_at = datetime.utcnow()
        user.rejected_by = current_user.id
        user.rejection_reason = reason

        # 브랜드 정보 업데이트
        brand = Brand.query.filter_by(admin_id=user.id).first()
        if brand:
            brand.status = 'inactive'
            brand.updated_at = datetime.utcnow()

        # 시스템 로그 기록
        log = SystemLog(
            user=current_user,  # pyright: ignore
            action='brand_admin_rejection',  # pyright: ignore
            detail=f'브랜드 관리자 거절: {user.username} ({user.email}) - 사유: {reason}',  # pyright: ignore
            ip_address=request.remote_addr  # pyright: ignore
        )
        db.session.add(log)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'{user.name} 브랜드 관리자가 거절되었습니다.'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"브랜드 관리자 거절 오류: {str(e)}")
        return jsonify({'error': '거절 처리 중 오류가 발생했습니다.'}), 500


@brand_approval_bp.route('/api/brand-stats', methods=['GET'])
@login_required
def get_brand_stats():
    """브랜드 통계"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        # 브랜드별 통계
        brands = Brand.query.all()
        brand_stats = []

        for brand in brands:
            # 브랜드 관리자 정보
            admin = User.query.get(brand.admin_id) if brand.admin_id else None

            # 매장 수
            branch_count = Branch.query.filter_by(brand_id=brand.id).count()

            # 직원 수
            staff_count = Staff.query.join(Branch).filter(Branch.brand_id == brand.id).count()

            brand_stats.append({
                'brand_id': brand.id,
                'brand_name': brand.name,
                'admin_name': admin.name if admin else '미지정',
                'admin_email': admin.email if admin else '미지정',
                'status': brand.status,
                'branch_count': branch_count,
                'staff_count': staff_count,
                'created_at': brand.created_at.isoformat()
            })

        # 전체 통계
        total_stats = {
            'total_brands': len(brands),
            'active_brands': len([b for b in brands if b.status == 'active']),
            'pending_brands': len([b for b in brands if b.status == 'pending']),
            'total_branches': sum([s['branch_count'] for s in brand_stats]),
            'total_staff': sum([s['staff_count'] for s in brand_stats])
        }

        return jsonify({
            'success': True,
            'brand_stats': brand_stats,
            'total_stats': total_stats
        })

    except Exception as e:
        logger.error(f"브랜드 통계 조회 오류: {str(e)}")
        return jsonify({'error': '통계 조회 중 오류가 발생했습니다.'}), 500
