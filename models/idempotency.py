#!/usr/bin/env python3
"""
멱등성 키 모델 - 임시로 비활성화됨
"""

# 데이터베이스 초기화 문제를 해결하기 위해 임시로 비활성화
# from extensions import db
# from datetime import datetime, timedelta

# class IdempotencyKey(db.Model):
#     __tablename__ = 'idempotency_keys'
    
#     key = db.Column(db.String(36), primary_key=True, nullable=False)
#     endpoint = db.Column(db.String(255), nullable=False)
#     method = db.Column(db.String(10), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
#     ip_address = db.Column(db.String(45), nullable=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
#     def to_dict(self):
#         """딕셔너리로 변환"""
#         return {
#             'key': self.key,
#             'endpoint': self.endpoint,
#             'method': self.method,
#             'user_id': self.user_id,
#             'ip_address': self.ip_address,
#             'created_at': self.created_at.isoformat() if self.created_at else None
#         }
    
#     @classmethod
#     def cleanup_expired_keys(cls, hours=24):
#         """만료된 키 정리"""
#         cutoff_time = datetime.utcnow() - timedelta(hours=hours)
#         return cls.query.filter(cls.created_at < cutoff_time).delete()

# 임시 더미 클래스 (테스트용)
class IdempotencyKey:
    def __init__(self, key, endpoint, method, user_id=None, ip_address=None):
        self.key = key
        self.endpoint = endpoint
        self.method = method
        self.user_id = user_id
        self.ip_address = ip_address
        self.created_at = None
    
    def to_dict(self):
        return {
            'key': self.key,
            'endpoint': self.endpoint,
            'method': self.method,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'created_at': None
        }
