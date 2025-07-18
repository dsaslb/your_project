from flask import Blueprint, jsonify, request, current_app
from models.branch import Branch  # pyright: ignore
from datetime import datetime

franchise_bp = Blueprint('franchise', __name__, url_prefix='/api/franchise')

# 더미 데이터
branches = [
    Branch(1, '본사', None, True),
    Branch(2, '강남지점', 1),
    Branch(3, '홍대지점', 1)
]


@franchise_bp.route('/branches', methods=['GET'])
def get_branches():
    try:
        return jsonify({'success': True, 'branches': [
            {'id': b.id, 'name': b.name, 'parent_id': b.parent_id, 'is_head_office': b.is_head_office} for b in branches
        ]}), 200
    except Exception as e:
        current_app.logger.error(f"지점 목록 오류: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@franchise_bp.route('/apply_policy', methods=['POST'])
def apply_policy():
    try:
        data = request.get_json() or {}
        policy = data.get('policy') if data else None
        for b in branches:
            b.apply_policy(policy)
        return jsonify({'success': True, 'message': '정책 일괄 적용 완료'}), 200
    except Exception as e:
        current_app.logger.error(f"정책 적용 오류: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@franchise_bp.route('/collaboration', methods=['POST'])
def collaboration():
    try:
        data = request.get_json() or {}
        # Q&A/이슈 공유 더미 처리
        return jsonify({'success': True, 'message': '이슈/질문이 공유되었습니다.'}), 200
    except Exception as e:
        current_app.logger.error(f"협업 오류: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
