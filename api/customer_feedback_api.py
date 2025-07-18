from flask import Blueprint, request, jsonify
from ai.sentiment_analysis import analyze_review_sentiment  # pyright: ignore

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.route("/api/feedback/alert", methods=["POST"])
def feedback_alert():
    data = request.get_json()
    sentiment = analyze_review_sentiment(data["review"] if data is not None else None)
    if sentiment == "negative":
        response_template = "불편을 드려 죄송합니다. 빠르게 개선하겠습니다."
    elif sentiment == "positive":
        response_template = "칭찬해주셔서 감사합니다!"
    else:
        response_template = "소중한 의견 감사합니다."
    return jsonify({"sentiment": sentiment, "response_template": response_template})
