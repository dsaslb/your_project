from flask import Blueprint, request, jsonify

from models import NoticeComment, db
from api.utils import token_required

api_comment_bp = Blueprint('api_comment', __name__, url_prefix='/api')

@api_comment_bp.route('/notices/<int:notice_id>/comments', methods=['POST'])
@token_required
def post_comment(current_user, notice_id):
    """Creates a new comment on a notice. Auth required."""
    data = request.json
    content = data.get('content', '').strip()
    if not content:
        return jsonify({"msg": "Content is empty"}), 400
    
    comment = NoticeComment(notice_id=notice_id, user_id=current_user.id, content=content)
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({"msg": "Comment created successfully", "comment_id": comment.id}), 201

@api_comment_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@token_required
def delete_comment(current_user, comment_id):
    """Deletes a comment. Auth required, user must be owner or admin."""
    comment = NoticeComment.query.get_or_404(comment_id)
    
    # Check if the user is the owner or an admin
    if comment.user_id != current_user.id and not current_user.is_admin():
        return jsonify({"msg": "Permission denied"}), 403
        
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({"msg": "Comment deleted successfully"}) 