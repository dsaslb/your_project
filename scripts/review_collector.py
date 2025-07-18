import requests
from models.external_integration import ExternalIntegration
from models.customer_feedback import CustomerFeedback, db


def collect_reviews(brand_id, platform="naver"):
    integration = ExternalIntegration.query.filter_by(
        brand_id=brand_id, platform=platform
    ).first()
    if not integration:
        print("연동 정보 없음")
        return
    resp = requests.get(
        "https://openapi.naver.com/v1/reviews",
        headers={"X-API-KEY": integration.api_key},
    )
    for review in resp.json().get("reviews", []):
        feedback = CustomerFeedback(
            customer_id=review["customer_id"],
            store_id=review["store_id"],
            review=review["content"],
            nps_score=review.get("nps_score", 0),
        )
        db.session.add(feedback)
    db.session.commit()
