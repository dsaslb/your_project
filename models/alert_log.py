from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

form = None  # pyright: ignore

db = SQLAlchemy()


class AlertLog(db.Model):
    """알림 로그 모델"""

    __tablename__ = "alert_logs"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.String(20), nullable=False)  # info, warning, critical
    channel = db.Column(db.String(50), nullable=False)  # slack, email, sms, kakao
    message = db.Column(db.Text, nullable=False)
    recipient = db.Column(db.String(100))  # 수신자 정보
    status = db.Column(db.String(20), default="sent")  # sent, failed, pending
    plugin_id = db.Column(db.String(100))  # 관련 플러그인 ID
    metric_type = db.Column(db.String(50))  # 관련 메트릭 타입
    threshold_value = db.Column(db.Float)  # 임계값
    actual_value = db.Column(db.Float)  # 실제값

    def __repr__(self):
        return f"<AlertLog {self.level}: {self.message[:50] if message is not None else None}...>"

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "channel": self.channel,
            "message": self.message,
            "recipient": self.recipient,
            "status": self.status,
            "plugin_id": self.plugin_id,
            "metric_type": self.metric_type,
            "threshold_value": self.threshold_value,
            "actual_value": self.actual_value,
        }
