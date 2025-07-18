from datetime import datetime
from flask import Blueprint, request, jsonify

policy_manager_bp = Blueprint('policy_manager', __name__, url_prefix='/api/policy')

# 더미 정책 데이터
DUMMY_POLICIES = [
    {"id": 1, "name": "매출 급감 경보", "type": "alert", "condition": "매출 30% 이상 감소", "action": "관리자 알림", "enabled": True, "created_at": "2024-06-01"},
    {"id": 2, "name": "리뷰 평점 하락 경보", "type": "alert", "condition": "평점 3.5 이하", "action": "관리자 알림", "enabled": True, "created_at": "2024-06-01"}
]

@policy_manager_bp.route('/list', methods=['GET'])
def list_policies():
    """정책 목록 조회"""
    return jsonify({"policies": DUMMY_POLICIES}), 200

@policy_manager_bp.route('/add', methods=['POST'])
def add_policy():
    """정책 추가(더미)"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "데이터가 없습니다."}), 400
    new_policy = {
        "id": len(DUMMY_POLICIES) + 1,
        "name": data.get("name", "새 정책"),
        "type": data.get("type", "alert"),
        "condition": data.get("condition", ""),
        "action": data.get("action", ""),
        "enabled": data.get("enabled", True),
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
    DUMMY_POLICIES.append(new_policy)
    return jsonify({"success": True, "policy": new_policy}), 201

@policy_manager_bp.route('/update/<int:policy_id>', methods=['PUT'])
def update_policy(policy_id):
    """정책 수정(더미)"""
    data = request.get_json()
    for policy in DUMMY_POLICIES:
        if policy["id"] == policy_id:
            policy.update(data)
            return jsonify({"success": True, "policy": policy}), 200
    return jsonify({"error": "정책을 찾을 수 없습니다."}), 404

@policy_manager_bp.route('/delete/<int:policy_id>', methods=['DELETE'])
def delete_policy(policy_id):
    """정책 삭제(더미)"""
    global DUMMY_POLICIES
    DUMMY_POLICIES = [p for p in DUMMY_POLICIES if p["id"] != policy_id]
    return jsonify({"success": True}), 200