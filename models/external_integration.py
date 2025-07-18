from extensions import db

form = None  # pyright: ignore


class ExternalIntegration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, nullable=False)
    platform = db.Column(
        db.String(32), nullable=False
    )  # 예: 'naver', 'kakao', 'baemin', 'coupang'
    api_key = db.Column(db.String(128))
    api_secret = db.Column(db.String(128))
    config = db.Column(db.JSON)  # 기타 인증/설정 정보
    created_at = db.Column(db.DateTime, server_default=db.func.now())
