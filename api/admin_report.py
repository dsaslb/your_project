from flask import Blueprint, request, jsonify
from models import Report, db, User, Notice, NoticeComment, SystemLog
from api.utils import admin_required

admin_report_bp = Blueprint('admin_report', __name__, url_prefix='/api/admin/reports')

@admin_report_bp.route('/', methods=['GET'])
@admin_required
def get_admin_reports(current_admin):
    """
    관리자용 신고 목록 조회
    ---
    tags:
      - Admin
    summary: 모든 신고 내역을 페이징으로 조회합니다
    description: 관리자 권한이 필요하며, JWT 토큰 인증이 필요합니다.
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        description: 페이지 번호 (기본값: 1)
        required: false
        default: 1
      - name: per_page
        in: query
        type: integer
        description: 페이지당 항목 수 (기본값: 20)
        required: false
        default: 20
    responses:
      200:
        description: 신고 목록 조회 성공
        schema:
          type: object
          properties:
            reports:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: 신고 ID
                  target_type:
                    type: string
                    description: 신고 대상 유형
                    enum: ["notice", "comment"]
                  target_id:
                    type: integer
                    description: 신고 대상 ID
                  reporter_id:
                    type: integer
                    description: 신고자 ID
                  reason:
                    type: string
                    description: 신고 사유
                  category:
                    type: string
                    description: 신고 카테고리
                  created_at:
                    type: string
                    format: date-time
                    description: 신고 일시
            total:
              type: integer
              description: 전체 신고 수
            page:
              type: integer
              description: 현재 페이지
            pages:
              type: integer
              description: 전체 페이지 수
      401:
        description: 인증 필요
      403:
        description: 관리자 권한 필요
    """
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
    신고 처리
    ---
    tags:
      - Admin
    summary: 신고를 처리하여 대상 콘텐츠에 조치를 취합니다
    description: 관리자 권한이 필요하며, 신고된 콘텐츠를 삭제/숨김/기각할 수 있습니다.
    security:
      - Bearer: []
    parameters:
      - name: report_id
        in: path
        type: integer
        required: true
        description: 처리할 신고 ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - action
          properties:
            action:
              type: string
              description: 처리 액션
              enum: ["delete", "hide", "dismiss"]
              example: "delete"
    responses:
      200:
        description: 신고 처리 성공
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Report resolved successfully"
            result:
              type: string
              example: "notice deleted"
      400:
        description: 잘못된 요청
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Invalid action specified"
      401:
        description: 인증 필요
      403:
        description: 관리자 권한 필요
      404:
        description: 신고를 찾을 수 없음
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