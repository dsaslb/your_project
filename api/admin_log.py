from flask import Blueprint, jsonify, request

from api.utils import admin_required
from models import SystemLog
from utils.role_required import role_required

admin_log_bp = Blueprint("admin_log", __name__, url_prefix="/api/admin/system-logs")


@admin_log_bp.route("/", methods=["GET"])
@role_required('admin', 'super_admin', 'brand_manager')
def get_system_logs(current_admin):
    """Retrieves a paginated list of system logs. Admin only."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = SystemLog.query
    # [브랜드별 필터링] 브랜드 관리자는 자신의 브랜드 로그만 조회
    if hasattr(current_admin, 'role') and current_admin.role == 'brand_manager':
        query = query.filter_by(brand_id=current_admin.brand_id)
    # 슈퍼관리자/총관리자는 전체 로그 조회
    elif hasattr(current_admin, 'role') and current_admin.role in ['admin', 'super_admin']:
        pass
    else:
        # 기타 권한은 접근 불가
        return jsonify({'error': '권한이 없습니다.'}), 403

    pagination = query.order_by(SystemLog.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    logs = [
        {
            "id": log.id,
            "admin_id": log.user_id,
            "action": log.action,
            "detail": log.detail,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat(),
        }
        for log in pagination.items
    ]

    return jsonify(
        {
            "logs": logs,
            "total": pagination.total,
            "page": page,
            "pages": pagination.pages,
        }
    )
