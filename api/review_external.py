from datetime import datetime
import random
from flask import Blueprint, request, jsonify
form = None  # pyright: ignore

review_external_bp = Blueprint('review_external', __name__, url_prefix='/api/review/external')

# 더미 리뷰 데이터
DUMMY_REVIEWS = [
    {"platform": "네이버", "author": "홍길동", "content": "맛있고 친절해요!", "score": 5, "created_at": "2024-06-01"},
    {"platform": "구글", "author": "Jane", "content": "음식이 빨리 나와서 좋아요.", "score": 4, "created_at": "2024-06-02"},
    {"platform": "네이버", "author": "김철수", "content": "별로였어요...", "score": 2, "created_at": "2024-06-03"},
    {"platform": "구글", "author": "Tom", "content": "서비스가 조금 느렸어요.", "score": 3, "created_at": "2024-06-04"},
    {"platform": "네이버", "author": "이영희", "content": "최고! 또 방문할게요.", "score": 5, "created_at": "2024-06-05"}
]


@review_external_bp.route('/fetch', methods=['POST'])
def fetch_reviews():
    """외부 리뷰 수집(더미)"""
    # 실제 구현 시 외부 API 호출
    return jsonify({"success": True, "reviews": DUMMY_REVIEWS, "fetched_at": datetime.now().isoformat()}), 200


@review_external_bp.route('/analysis', methods=['GET'])
def analyze_reviews():
    """감성분석 결과 반환(더미)"""
    # 더미 감성분석 결과
    total = len(DUMMY_REVIEWS)
    positive = sum(1 for r in DUMMY_REVIEWS if r and int(r.get('score', 0)) >= 4)
    negative = sum(1 for r in DUMMY_REVIEWS if r and int(r.get('score', 0)) <= 2)
    neutral = total - positive - negative
    avg_score = round(sum(int(r.get('score', 0)) for r in DUMMY_REVIEWS) / total, 2) if total else 0
    return jsonify({
        "total_reviews": total,
        "positive_count": positive,
        "negative_count": negative,
        "neutral_count": neutral,
        "avg_score": avg_score,
        "positive_ratio": round(positive/total, 2) if total else 0,
        "negative_ratio": round(negative/total, 2) if total else 0,
        "neutral_ratio": round(neutral/total, 2) if total else 0,
        "last_updated": datetime.now().isoformat()
    }), 200
