from flask import Blueprint, request, jsonify
from utils.role_required import role_required
from models import Notice, db

notice_bp = Blueprint('notice', __name__, url_prefix='/api/notice')

@notice_bp.route('/create', methods=['POST'])
@role_required('admin', 'super_admin', 'brand_manager')
def create_notice():
    # 브랜드별 공지사항 등록
    data = request.json
    notice = Notice(
        title=data['title'],
        content=data['content'],
        brand_id=data.get('brand_id'),
        created_by=request.current_user.id
    )
    db.session.add(notice)
    db.session.commit()
    return jsonify({'success': True, 'notice_id': notice.id})

@notice_bp.route('/list', methods=['GET'])
@role_required('admin', 'super_admin', 'brand_manager')
def list_notice():
    # 브랜드별 공지사항 조회
    brand_id = request.args.get('brand_id')
    query = Notice.query
    if brand_id:
        query = query.filter_by(brand_id=brand_id)
    notices = query.order_by(Notice.created_at.desc()).all()
    return jsonify({'success': True, 'notices': [n.to_dict() for n in notices]}) 