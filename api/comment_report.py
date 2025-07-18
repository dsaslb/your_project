from models_main import NoticeComment, Report, db
from api.utils import admin_required  # pyright: ignore
from flask import Blueprint, jsonify, request
args = None  # pyright: ignore
form = None  # pyright: ignore


comment_report_bp = Blueprint(
    "comment_report", __name__, url_prefix="/api/admin/comment-reports"
)


@comment_report_bp.route("/", methods=["GET"])
@admin_required
def get_comment_reports(current_user):
    """Retrieves a paginated list of comment-specific reports. Admin only."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = Report.query.filter_by(target_type="comment").order_by(
        Report.created_at.desc()
    )
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    reports_data = []
    for report in pagination.items:
        comment = NoticeComment.query.get(report.target_id)
        reports_data.append(
            {
                "report_id": report.id,
                "comment_id": report.target_id,
                "comment_content": comment.content if comment else "[Deleted Comment]",
                "reporter_id": report.user_id,
                "reason": report.reason,
                "category": report.category,
                "created_at": report.created_at.isoformat(),
            }
        )

    return jsonify(
        {
            "reports": reports_data,
            "total": pagination.total,
            "page": page,
            "pages": pagination.pages,
        }
    )
