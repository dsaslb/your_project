from extensions import db
from datetime import datetime, timedelta

class IdempotencyKey(db.Model):
    """중복 요청 방지를 위한 멱등성 키"""
    __tablename__ = 'idempotency_keys'
    
    key = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    endpoint = db.Column(db.String(255), nullable=False)  # API 엔드포인트
    method = db.Column(db.String(10), nullable=False)    # HTTP 메서드
    response_json = db.Column(db.Text, nullable=True)    # 이전 응답 캐시 (선택사항)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)  # 만료 시간 (24시간)
    
    # 관계 설정
    user = db.relationship('models_main.User', backref='idempotency_keys', foreign_keys=[user_id])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 기본적으로 24시간 후 만료
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(hours=24)
    
    def is_expired(self):
        """키가 만료되었는지 확인"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        return {
            'key': self.key,
            'user_id': self.user_id,
            'endpoint': self.endpoint,
            'method': self.method,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_expired': self.is_expired()
        }
    
    @classmethod
    def cleanup_expired(cls):
        """만료된 키들을 정리"""
        expired = cls.query.filter(cls.expires_at < datetime.utcnow()).all()
        for key in expired:
            db.session.delete(key)
        db.session.commit()
        return len(expired)
