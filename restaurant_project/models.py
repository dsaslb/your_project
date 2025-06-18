from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="employee")
    status = db.Column(db.String(20), nullable=False, default="approved")
    phone = db.Column(db.String(20))
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # 상위 관리자 
    deleted = db.Column(db.Boolean, default=False)    # soft delete
    deleted_at = db.Column(db.DateTime, nullable=True, default=None)

class ActionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)      # 대상 회원
    actor_id = db.Column(db.Integer)     # 행위자(관리자/매장관리자 등)
    action = db.Column(db.String(30))    # 'register', 'approve', 'reject', 'delete'
    detail = db.Column(db.String(255))   # 부가 설명
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50))  # 'register', 'approve', 'reject', 'delete'
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 조작한 관리자 id
    timestamp = db.Column(db.DateTime, default=db.func.now())
    detail = db.Column(db.String(200)) 

class ApprovalLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(20))  # 'approved' or 'rejected'
    by_admin = db.Column(db.String(80))  # admin username
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) 

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    clock_in = db.Column(db.DateTime, nullable=False)
    clock_out = db.Column(db.DateTime, nullable=True)
    # clock_in, clock_out이 한 쌍

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(100), default='근무')
    created_by = db.Column(db.String(80))  # 관리자명 