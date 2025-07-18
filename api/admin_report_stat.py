from models_main import Report, db
from api.utils import admin_required  # pyright: ignore
from sqlalchemy import func
from flask import Blueprint, jsonify

query = None  # pyright: ignore


admin_report_stat_bp = Blueprint(
    "admin_report_stat", __name__, url_prefix="/api/admin/report-stats"
)


@admin_report_stat_bp.route("/", methods=["GET"])
@admin_required
def get_report_stats(current_admin):
    """
    Retrieves statistics on reports, grouped by category and target type.
    Admin only.
    """
    try:
        stats = (
            db.session.query(
                Report.category,
                Report.target_type,
                func.count(Report.id).label("count"),
            )
            .group_by(Report.category, Report.target_type)
            .all()
        )

        result = [
            {"category": category, "target_type": target_type, "count": count}
            for category, target_type, count in stats
        ]

        return jsonify({"stats": result})
    except Exception as e:
        return jsonify({"msg": "Could not retrieve stats", "error": str(e)}), 500
