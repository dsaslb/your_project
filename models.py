from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# 지점 모델
class Branch(db.Model):
    __tablename__ = "branches"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    users = db.relationship("User", backref="branch", lazy=True)

# User 모델
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'approved', 'pending', 'rejected'
    role = db.Column(db.String(20), default='employee')   # 'admin', 'employee'
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"))
    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    attendances = db.relationship("Attendance", backref="user", lazy=True)
    name = db.Column(db.String(50))
    phone = db.Column(db.String(20))

    def set_password(self, pw):
        self.password = generate_password_hash(pw)
    def check_password(self, pw):
        return check_password_hash(self.password, pw)
    def is_admin(self):
        return self.role == "admin"
    def is_manager(self):
        return self.role == "manager"
    def is_employee(self):
        return self.role == "employee"

# 출퇴근 모델
class Attendance(db.Model):
    __tablename__ = "attendances"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    clock_in = db.Column(db.DateTime, default=datetime.utcnow)
    clock_out = db.Column(db.DateTime)

    @property
    def work_minutes(self):
        if self.clock_in and self.clock_out:
            return int((self.clock_out - self.clock_in).total_seconds() // 60)
        return 0

    @property
    def status(self):
        from datetime import time
        work_start = time(9, 0)
        work_end = time(18, 0)
        if not self.clock_in or not self.clock_out:
            return "결근" if not self.clock_in and not self.clock_out else "미완료"
        s = []
        if self.clock_in.time() > work_start:
            s.append("지각")
        if self.clock_out.time() < work_end:
            s.append("조퇴")
        if not s:
            return "정상"
        return "/".join(s)

# 액션로그
class ActionLog(db.Model):
    __tablename__ = "action_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    action = db.Column(db.String(50))
    message = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 피드백 모델
class Feedback(db.Model):
    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    satisfaction = db.Column(db.Integer) # 1~5점
    health = db.Column(db.Integer) # 1~5점
    comment = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 승인/거절 이력 로그
class ApproveLog(db.Model):
    __tablename__ = "approve_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(32))  # 'approved' or 'rejected'
    timestamp = db.Column(db.DateTime, default=db.func.now())
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 처리자
    reason = db.Column(db.String(256))  # 선택: 승인/거절 사유 기록용 (옵션)
    
    def __repr__(self):
        return f"<ApproveLog {self.user_id} {self.action} {self.timestamp}>"
