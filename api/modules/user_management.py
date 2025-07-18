from datetime import datetime
from api.gateway import token_required, role_required  # pyright: ignore
from models_main import User, db
from functools import wraps
from flask import Blueprint, request, jsonify, current_app

user_management = Blueprint('user_management', __name__)

# 사용자 목록 조회


@user_management.route('/users', methods=['GET'])
@token_required
@role_required(['super_admin', 'brand_manager'])
def get_users(current_user):
    """사용자 목록 조회 - 슈퍼 관리자, 브랜드 관리자만 접근 가능"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role_filter = request.args.get('role')
        search = request.args.get('search')

        query = User.query

        # 역할 필터
        if role_filter:
            query = query.filter(User.role == role_filter)

        # 검색 필터
        if search:
            query = query.filter(
                (User.username.contains(search)) |
                (User.name.contains(search)) |
                (User.email.contains(search))
            )

        # 슈퍼 관리자가 아닌 경우 자신의 브랜드/매장 사용자만 조회
        if current_user.role != 'super_admin':
            # 브랜드 관리자는 자신의 브랜드 사용자만 조회
            if current_user.role == 'brand_manager':
                query = query.filter(User.brand_id == current_user.brand_id)
            # 매장 관리자는 자신의 매장 사용자만 조회
            elif current_user.role == 'store_manager':
                query = query.filter(User.branch_id == current_user.branch_id)

        # 페이지네이션
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        users = []
        for user in pagination.items:
            users.append({
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'status': user.status,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            })

        return jsonify({
            'users': users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Get users error: {str(e)}")
        return jsonify({'message': '사용자 목록 조회 중 오류가 발생했습니다'}), 500

# 사용자 상세 조회


@user_management.route('/users/<int:user_id>', methods=['GET'])
@token_required
@role_required(['super_admin', 'brand_manager', 'store_manager'])
def get_user(current_user, user_id):
    """사용자 상세 조회"""
    try:
        user = User.query.get_or_404(user_id)

        # 권한 확인
        if current_user.role != 'super_admin':
            if current_user.role == 'brand_manager' and user.brand_id != current_user.brand_id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403
            elif current_user.role == 'store_manager' and user.store_id != current_user.store_id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403

        return jsonify({
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'status': user.status,
            'brand_id': user.brand_id,
            'branch_id': user.branch_id,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }), 200

    except Exception as e:
        current_app.logger.error(f"Get user error: {str(e)}")
        return jsonify({'message': '사용자 조회 중 오류가 발생했습니다'}), 500

# 사용자 생성


@user_management.route('/users', methods=['POST'])
@token_required
@role_required(['super_admin', 'brand_manager'])
def create_user(current_user):
    """사용자 생성"""
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['username', 'password', 'name', 'email', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} 필드는 필수입니다'}), 400

        # 사용자명 중복 확인
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': '이미 존재하는 사용자명입니다'}), 400

        # 이메일 중복 확인
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': '이미 존재하는 이메일입니다'}), 400

        # 권한 확인
        if current_user.role != 'super_admin':
            # 브랜드 관리자는 자신의 브랜드에만 사용자 생성 가능
            if current_user.role == 'brand_manager':
                data['brand_id'] = current_user.brand_id
                # 브랜드 관리자는 매장 관리자와 직원만 생성 가능
                if data['role'] not in ['store_manager', 'employee']:
                    return jsonify({'message': '권한이 없습니다'}), 403

        # 사용자 생성
        user = User()
        user.username = data['username']
        user.name = data['name']
        user.email = data['email']
        user.role = data['role']
        user.brand_id = data.get('brand_id')
        user.branch_id = data.get('branch_id')
        user.status = data.get('status', 'approved')
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': '사용자가 생성되었습니다',
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create user error: {str(e)}")
        return jsonify({'message': '사용자 생성 중 오류가 발생했습니다'}), 500

# 사용자 수정


@user_management.route('/users/<int:user_id>', methods=['PUT'])
@token_required
@role_required(['super_admin', 'brand_manager', 'store_manager'])
def update_user(current_user, user_id):
    """사용자 수정"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()

        # 권한 확인
        if current_user.role != 'super_admin':
            if current_user.role == 'brand_manager' and user.brand_id != current_user.brand_id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403
            elif current_user.role == 'store_manager' and user.store_id != current_user.store_id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403

        # 수정 가능한 필드들
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            # 이메일 중복 확인
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'message': '이미 존재하는 이메일입니다'}), 400
            user.email = data['email']
        if 'role' in data and current_user.role == 'super_admin':
            user.role = data['role']
        if 'status' in data:
            user.status = data['status']
        if 'password' in data:
            user.set_password(data['password'])

        db.session.commit()

        return jsonify({
            'message': '사용자 정보가 업데이트되었습니다',
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'status': user.status
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update user error: {str(e)}")
        return jsonify({'message': '사용자 수정 중 오류가 발생했습니다'}), 500

# 사용자 삭제


@user_management.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@role_required(['super_admin', 'brand_manager'])
def delete_user(current_user, user_id):
    """사용자 삭제"""
    try:
        user = User.query.get_or_404(user_id)

        # 자신을 삭제할 수 없음
        if user.id == current_user.id:
            return jsonify({'message': '자신을 삭제할 수 없습니다'}), 400

        # 권한 확인
        if current_user.role != 'super_admin':
            if current_user.role == 'brand_manager' and user.brand_id != current_user.brand_id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403

        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': '사용자가 삭제되었습니다'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete user error: {str(e)}")
        return jsonify({'message': '사용자 삭제 중 오류가 발생했습니다'}), 500

# 사용자 통계


@user_management.route('/users/stats', methods=['GET'])
@token_required
@role_required(['super_admin', 'brand_manager'])
def get_user_stats(current_user):
    """사용자 통계"""
    try:
        # 기본 쿼리
        query = User.query

        # 슈퍼 관리자가 아닌 경우 자신의 브랜드 사용자만 조회
        if current_user.role != 'super_admin':
            if current_user.role == 'brand_manager':
                query = query.filter(User.brand_id == current_user.brand_id)

        # 역할별 사용자 수
        role_stats = {}
        for role in ['super_admin', 'brand_manager', 'store_manager', 'employee']:
            count = query.filter(User.role == role).count()
            role_stats[role] = count

        # 상태별 사용자 수
        status_stats = {}
        for status in ['active', 'inactive', 'pending', 'approved']:
            count = query.filter(User.status == status).count()
            status_stats[status] = count

        # 총 사용자 수
        total_users = query.count()

        # 최근 가입한 사용자 수 (30일)
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_users = query.filter(User.created_at >= thirty_days_ago).count()

        return jsonify({
            'total_users': total_users,
            'recent_users': recent_users,
            'role_stats': role_stats,
            'status_stats': status_stats
        }), 200

    except Exception as e:
        current_app.logger.error(f"Get user stats error: {str(e)}")
        return jsonify({'message': '사용자 통계 조회 중 오류가 발생했습니다'}), 500
