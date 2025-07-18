from models_main import Report, db
from api.utils import token_required  # pyright: ignore
from flask import Blueprint, jsonify, request
query = None  # pyright: ignore


api_report_bp = Blueprint("api_report", __name__, url_prefix="/api/report")


@api_report_bp.route("/", methods=["POST"])
@token_required
def post_report(current_user):
    """Creates a new report. Auth required."""
    data = request.json
    target_type = data.get("target_type") if data else None
    target_id = data.get("target_id") if data else None
    reason = data.get("reason", "").strip() if data else ''
    category = data.get("category", "").strip() if data else ''

    if not all([target_type, target_id, reason, category]):
        return jsonify({"msg": "Missing required fields"}), 400

    # Prevent duplicate reports
    existing_report = Report.query.filter_by(
        target_type=target_type, target_id=target_id, user_id=current_user.id
    ).first()
    if existing_report:
        return (
            jsonify({"msg": "You have already reported this item"}),
            409,
        )  # 409 Conflict

    report = Report(
        target_type=target_type,
        target_id=target_id,
        user_id=current_user.id,
        reason=reason,
        category=category,
    )
    db.session.add(report)
    db.session.commit()

    return jsonify({"msg": "Report submitted successfully"}), 201
