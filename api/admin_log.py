from flask import Blueprint, request, jsonify
from models import SystemLog
from api.utils import admin_required

admin_log_bp = Blueprint('admin_log', __name__, url_prefix='/api/admin/system-logs')

@admin_log_bp.route('/', methods=['GET'])
@admin_required
def get_system_logs(current_admin):
    """Retrieves a paginated list of system logs. Admin only."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = SystemLog.query.order_by(SystemLog.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    logs = [{
        "id": log.id,
        "admin_id": log.user_id,
        "action": log.action,
        "detail": log.detail,
        "ip_address": log.ip_address,
        "created_at": log.created_at.isoformat()
    } for log in pagination.items]
    
    return jsonify({
        "logs": logs,
        "total": pagination.total,
        "page": page,
        "pages": pagination.pages
    }) 