import csv
import io
from models_main import AuditLog, NotificationLog
from utils.role_required import role_required  # pyright: ignore
from flask import Blueprint, request, jsonify, send_file
args = None  # pyright: ignore
query = None  # pyright: ignore

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('/list', methods=['GET'])
@role_required('admin', 'super_admin', 'brand_manager')
def list_items():
    # 검색/필터/정렬 파라미터 처리
    q = request.args.get('q', '')
    type_filter = request.args.get('type')
    status_filter = request.args.get('status')
    sort = request.args.get('sort', 'timestamp_desc')
    # AuditLog + NotificationLog 통합 쿼리(예시)
    items = []
    for log in AuditLog.query.all():
        if (not q or q in log.detail) and (not type_filter or type_filter == 'audit'):
            items.append({'type': 'audit', 'content': log.detail, 'user_name': log.user_id,
                         'status': 'success', 'timestamp': log.timestamp})
    for log in NotificationLog.query.all():
        if (not q or q in log.message) and (not type_filter or type_filter == 'notification'):
            items.append({'type': 'notification', 'content': log.message, 'user_name': log.user_id,
                         'status': log.status, 'timestamp': log.timestamp})
    # 정렬(예시)
    items.sort(key=lambda x: x['timestamp'] if x is not None else None, reverse=(sort == 'timestamp_desc'))
    return jsonify({'success': True, 'items': items})


@dashboard_bp.route('/export', methods=['GET'])
@role_required('admin', 'super_admin')
def export_items():
    # 엑셀(CSV) 내보내기 예시
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['유형', '내용', '사용자', '상태', '일시'])
    for log in AuditLog.query.all():
        writer.writerow(['이력', log.detail, log.user_id, 'success', log.timestamp])
    for log in NotificationLog.query.all():
        writer.writerow(['알림', log.message, log.user_id, log.status, log.timestamp])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name='dashboard_export.csv')
