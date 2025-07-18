from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import random

reward_system_bp = Blueprint("reward_system", __name__, url_prefix="/api/reward")

# 1. 건강설문/피드백


@reward_system_bp.route("/survey", methods=["POST"])
def submit_survey():
    try:
        data = request.get_json() or {}
        # 더미 설문 저장 처리
        return jsonify({"success": True, "message": "설문이 제출되었습니다."}), 200
    except Exception as e:
        current_app.logger.error(f"설문 오류: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@reward_system_bp.route("/feedback", methods=["POST"])
def submit_feedback():
    try:
        data = request.get_json() or {}
        # 더미 피드백 저장 처리
        return jsonify({"success": True, "message": "피드백이 제출되었습니다."}), 200
    except Exception as e:
        current_app.logger.error(f"피드백 오류: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


# 2. 포인트/리워드 지급


@reward_system_bp.route("/reward", methods=["POST"])
def give_reward():
    try:
        data = request.get_json() or {}
        # 더미 지급 처리
        if random.random() < 0.95:
            return (
                jsonify(
                    {"success": True, "message": "포인트/리워드가 지급되었습니다."}
                ),
                200,
            )
        else:
            raise Exception("지급 실패(더미)")
    except Exception as e:
        current_app.logger.error(f"리워드 지급 오류: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


# 3. 이벤트/쿠폰 발급


@reward_system_bp.route("/event", methods=["POST"])
def create_event():
    try:
        data = request.get_json() or {}
        # 더미 이벤트/쿠폰 발급 처리
        return (
            jsonify({"success": True, "message": "이벤트/쿠폰이 발급되었습니다."}),
            200,
        )
    except Exception as e:
        current_app.logger.error(f"이벤트/쿠폰 오류: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
