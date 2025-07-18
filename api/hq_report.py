from extensions import db
from flask import Blueprint, request, jsonify
args = None  # pyright: ignore

hq_bp = Blueprint('hq_report', __name__)


@hq_bp.route('/api/hq/report/summary', methods=['GET'])
def hq_report_summary():
    brand_id = request.args.get() if args else None'brand_id') if args else None
    summary = db.session.execute(
        """
        SELECT store_id, SUM(amount) as total_sales
        FROM sales
        WHERE brand_id = :brand_id
        GROUP BY store_id
        """, {'brand_id': brand_id}
    ).fetchall()
    return jsonify([dict(row) for row in summary])
