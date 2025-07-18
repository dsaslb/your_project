from datetime import datetime
import random
from flask import Blueprint, jsonify, request, current_app
form = None  # pyright: ignore

integration_external_bp = Blueprint('integration_external', __name__, url_prefix='/api/integration')

# 1. POS 연동


@integration_external_bp.route('/pos', methods=['POST'])
def sync_pos():
    try:
        # 실제 구현 시 외부 POS API 연동
        data = request.get_json() or {}
        # 더미 성공/실패 시뮬레이션
        if random.random() < 0.9:
            return jsonify({'success': True, 'message': 'POS 연동 성공', 'synced_at': datetime.now().isoformat()}), 200
        else:
            raise Exception('POS 연동 실패(더미)')
    except Exception as e:
        current_app.logger.error(f"POS 연동 오류: {str(e)}")
        # TODO: 관리자 알림 연동
        return jsonify({'success': False, 'error': str(e)}), 500

# 2. 회계 연동


@integration_external_bp.route('/accounting', methods=['POST'])
def sync_accounting():
    try:
        data = request.get_json() or {}
        if random.random() < 0.9:
            return jsonify({'success': True, 'message': '회계 연동 성공', 'synced_at': datetime.now().isoformat()}), 200
        else:
            raise Exception('회계 연동 실패(더미)')
    except Exception as e:
        current_app.logger.error(f"회계 연동 오류: {str(e)}")
        # TODO: 관리자 알림 연동
        return jsonify({'success': False, 'error': str(e)}), 500

# 3. 리뷰 플랫폼 연동 및 감성분석


@integration_external_bp.route('/review', methods=['POST'])
def sync_review():
    try:
        data = request.get_json() or {}
        # 더미 리뷰 데이터 및 감성분석
        reviews = [
            {"platform": "네이버", "content": "맛있어요!", "score": 5},
            {"platform": "배민", "content": "별로였어요...", "score": 2},
            {"platform": "쿠팡이츠", "content": "빠르고 친절", "score": 4}
        ]
        positive = sum(1 for r in reviews if r and int(r.get("score", 0)) >= 4)
        negative = sum(1 for r in reviews if r and int(r.get("score", 0)) <= 2)
        neutral = len(reviews) - positive - negative
        avg_score = round(sum(int(r.get("score", 0)) for r in reviews if r) / len(reviews), 2)
        return jsonify({
            'success': True,
            'reviews': reviews,
            'sentiment': {
                'positive': positive,
                'negative': negative,
                'neutral': neutral,
                'avg_score': avg_score
            },
            'synced_at': datetime.now().isoformat()
        }), 200
    except Exception as e:
        current_app.logger.error(f"리뷰 연동 오류: {str(e)}")
        # TODO: 관리자 알림 연동
        return jsonify({'success': False, 'error': str(e)}), 500
