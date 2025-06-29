#!/usr/bin/env python3
"""DataChangeLog 모델을 models.py에 추가하는 스크립트"""


def add_data_change_log_model():
    """DataChangeLog 모델을 models.py에 추가"""

    model_code = '''
class DataChangeLog(db.Model):
    """데이터 변경 이력 모델"""
    __tablename__ = 'data_change_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event = db.Column(db.String(100), nullable=False)  # 이벤트 종류
    target_type = db.Column(db.String(50))  # 변경 대상 타입 (User, Notice, Payroll 등)
    target_id = db.Column(db.Integer)  # 변경 대상 ID
    old_value = db.Column(db.Text)  # 이전 값 (JSON 형태로 저장)
    new_value = db.Column(db.Text)  # 새로운 값 (JSON 형태로 저장)
    detail = db.Column(db.String(500))  # 상세 설명
    ip_address = db.Column(db.String(45))  # IP 주소
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # 관계 설정
    user = db.relationship('User', backref='data_changes')
    
    def __repr__(self):
        return f'<DataChangeLog {self.event} by {self.user_id} at {self.created_at}>'
    
    def to_dict(self):
        """딕셔너리 형태로 변환"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'event': self.event,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'detail': self.detail,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
'''

    try:
        # models.py 파일 읽기
        with open("models.py", "r", encoding="utf-8") as f:
            content = f.read()

        # 이미 모델이 있는지 확인
        if "class DataChangeLog" in content:
            print("DataChangeLog 모델이 이미 존재합니다.")
            return

        # 파일 끝에 모델 추가
        with open("models.py", "a", encoding="utf-8") as f:
            f.write(model_code)

        print("✅ DataChangeLog 모델이 models.py에 추가되었습니다!")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    add_data_change_log_model()
