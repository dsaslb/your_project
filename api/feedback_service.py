from flask import Blueprint, request, jsonify
from utils.role_required import role_required
from models import Feedback, db

feedback_bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')

@feedback_bp.route('/create', methods=['POST'])
@role_required('admin', 'super_admin', 'brand_manager', 'employee')
def create_feedback():
    # 피드백 등록
    data = request.json
    feedback = Feedback(
        content=data['content'],
        brand_id=data.get('brand_id'),
        user_id=request.current_user.id
    )
    db.session.add(feedback)
    db.session.commit()
    return jsonify({'success': True, 'feedback_id': feedback.id})

@feedback_bp.route('/list', methods=['GET'])
@role_required('admin', 'super_admin', 'brand_manager')
def list_feedback():
    # 브랜드별 피드백 조회
    brand_id = request.args.get('brand_id')
    query = Feedback.query
    if brand_id:
        query = query.filter_by(brand_id=brand_id)
    feedbacks = query.order_by(Feedback.created_at.desc()).all()
    return jsonify({'success': True, 'feedbacks': [f.to_dict() for f in feedbacks]}) 