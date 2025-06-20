from flask import Blueprint, request, jsonify
from models import Report, db, User, Notice, NoticeComment, SystemLog
from api.utils import admin_required

admin_report_bp = Blueprint('admin_report', __name__, url_prefix='/api/admin/reports')

@admin_report_bp.route('/', methods=['GET'])
@admin_required
def get_admin_reports(current_admin):
    """Retrieves a paginated list of all reports. Admin only."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Report.query.order_by(Report.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    result = [{
        "id": r.id,
        "target_type": r.target_type,
        "target_id": r.target_id,
        "reporter_id": r.user_id,
        "reason": r.reason,
        "category": r.category,
        "created_at": r.created_at.isoformat()
    } for r in pagination.items]
    
    return jsonify({
        "reports": result,
        "total": pagination.total,
        "page": page,
        "pages": pagination.pages
    })

@admin_report_bp.route('/<int:report_id>/resolve', methods=['POST'])
@admin_required
def resolve_report(current_admin, report_id):
    """
    Resolves a report by performing an action (delete, hide, dismiss) 
    on the target content and logs the action. Admin only.
    """
    data = request.json
    action = data.get('action')
    if action not in ['delete', 'hide', 'dismiss']:
        return jsonify({"msg": "Invalid action specified"}), 400

    report = Report.query.get_or_404(report_id)
    action_result = "No action taken"

    target_model = None
    if report.target_type == 'notice':
        target_model = Notice.query.get(report.target_id)
    elif report.target_type == 'comment':
        target_model = NoticeComment.query.get(report.target_id)
    
    if target_model:
        if action == 'delete':
            db.session.delete(target_model)
            action_result = f'{report.target_type} deleted'
        elif action == 'hide':
            target_model.is_hidden = True
            db.session.add(target_model)
            action_result = f'{report.target_type} hidden'
        else: # dismiss
            action_result = 'Report dismissed'
    else:
        action_result = 'Target content not found, report dismissed'

    # Log the administrative action
    syslog = SystemLog(
        user_id=current_admin.id,
        action=f"REPORT_RESOLVE:{action.upper()}",
        detail=f"Admin '{current_admin.username}' resolved report #{report.id} for {report.target_type} #{report.target_id}. Action: {action_result}.",
        ip_address=request.remote_addr
    )
    db.session.add(syslog)

    # Delete the report itself as it has been handled
    db.session.delete(report)
    
    db.session.commit()
    
    return jsonify({"msg": "Report resolved successfully", "result": action_result}) 