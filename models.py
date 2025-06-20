from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

# 지점 모델
class Branch(db.Model):
    __tablename__ = "branches"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    users = db.relationship("User", backref="branch", lazy=True)

    def __repr__(self):
        return f'<Branch {self.name}>'

# User 모델
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(20), default='pending', index=True)  # 'approved', 'pending', 'rejected'
    role = db.Column(db.String(20), default='employee', index=True)   # 'admin', 'manager', 'employee'
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), index=True)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    attendances = db.relationship("Attendance", backref="user", lazy=True, cascade="all, delete-orphan")
    name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, index=True)
    last_login = db.Column(db.DateTime, index=True)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, index=True)
    failed_login = db.Column(db.Integer, default=0)    # 로그인 실패 횟수
    
    # is_locked는 프로퍼티로 관리하는 것이 더 효율적
    # is_locked = db.Column(db.Boolean, default=False)   # 계정 잠금 여부

    def set_password(self, pw):
        if len(pw) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")
        if not re.search(r'[A-Za-z]', pw) or not re.search(r'\d', pw):
            raise ValueError("비밀번호는 영문자와 숫자를 포함해야 합니다.")
        self.password = generate_password_hash(pw, method='pbkdf2:sha256')
    
    def check_password(self, pw):
        return check_password_hash(self.password, pw)
    
    def is_admin(self):
        return self.role == "admin"
    
    def is_manager(self):
        return self.role == "manager"
    
    def is_employee(self):
        return self.role == "employee"
    
    @property
    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def increment_login_attempts(self):
        self.login_attempts += 1
        if self.login_attempts >= 5:
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
    
    def reset_login_attempts(self):
        self.login_attempts = 0
        self.locked_until = None
        self.last_login = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

# 출퇴근 모델
class Attendance(db.Model):
    __tablename__ = "attendances"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    clock_in = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    clock_out = db.Column(db.DateTime, index=True)
    location_in = db.Column(db.String(100))  # 출근 위치 (GPS 등)
    location_out = db.Column(db.String(100))  # 퇴근 위치
    notes = db.Column(db.Text)  # 메모
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 복합 인덱스 추가
    __table_args__ = (
        db.Index('idx_attendance_user_date', 'user_id', 'clock_in'),
        db.Index('idx_attendance_date_range', 'clock_in', 'clock_out'),
    )

    @property
    def work_minutes(self):
        if self.clock_in and self.clock_out:
            return int((self.clock_out - self.clock_in).total_seconds() // 60)
        return 0

    @property
    def work_hours(self):
        return round(self.work_minutes / 60, 2)

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

    def __repr__(self):
        return f'<Attendance {self.user_id} {self.clock_in.date()}>'

# 액션로그
class ActionLog(db.Model):
    __tablename__ = "action_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False, index=True)
    message = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))  # IPv6 지원
    user_agent = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 복합 인덱스 추가
    __table_args__ = (
        db.Index('idx_actionlog_user_action', 'user_id', 'action'),
        db.Index('idx_actionlog_action_date', 'action', 'created_at'),
    )

    def __repr__(self):
        return f'<ActionLog {self.user_id} {self.action}>'

# 피드백 모델
class Feedback(db.Model):
    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    satisfaction = db.Column(db.Integer) # 1~5점
    health = db.Column(db.Integer) # 1~5점
    comment = db.Column(db.String(500))  # 길이 증가
    category = db.Column(db.String(50))  # 피드백 카테고리
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Feedback {self.user_id} {self.satisfaction}>'

# 승인/거절 이력 로그
class ApproveLog(db.Model):
    __tablename__ = "approve_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(32), nullable=False, index=True)  # 'approved' or 'rejected'
    timestamp = db.Column(db.DateTime, default=db.func.now(), index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # 처리자
    reason = db.Column(db.String(256))  # 선택: 승인/거절 사유 기록용 (옵션)
    ip_address = db.Column(db.String(45))
    
    # 복합 인덱스 추가
    __table_args__ = (
        db.Index('idx_approvelog_user_action', 'user_id', 'action'),
        db.Index('idx_approvelog_admin_date', 'admin_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<ApproveLog {self.user_id} {self.action} {self.timestamp}>"

# 근무 변경(교대) 신청 모델
class ShiftRequest(db.Model):
    __tablename__ = "shift_requests"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    request_date = db.Column(db.Date, nullable=False, index=True)  # 신청 날짜
    desired_date = db.Column(db.Date, nullable=False, index=True)  # 희망 날짜
    reason = db.Column(db.String(255), nullable=False)  # 사유
    status = db.Column(db.String(20), default='pending', index=True)  # pending/approved/rejected
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # 관계 설정
    user = db.relationship("User", backref="shift_requests")
    
    # 복합 인덱스 추가
    __table_args__ = (
        db.Index('idx_shiftrequest_user_status', 'user_id', 'status'),
        db.Index('idx_shiftrequest_date_range', 'request_date', 'desired_date'),
    )
    
    def __repr__(self):
        return f'<ShiftRequest {self.user_id} {self.desired_date} {self.status}>'

# 알림 모델
class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    is_read = db.Column(db.Boolean, default=False, index=True)
    
    # 관계 설정
    user = db.relationship("User", backref="notifications")
    
    # 복합 인덱스 추가
    __table_args__ = (
        db.Index('idx_notification_user_read', 'user_id', 'is_read'),
        db.Index('idx_notification_created', 'created_at'),
    )
    
    def __repr__(self):
        return f'<Notification {self.user_id} {self.message[:20]}...>'

# 공지사항 모델
class Notice(db.Model):
    __tablename__ = "notices"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255))  # 첨부파일 경로
    file_type = db.Column(db.String(20))   # 파일 확장자
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category = db.Column(db.String(30), index=True)  # 공지사항, 자료실 등
    is_hidden = db.Column(db.Boolean, default=False, index=True)  # 숨김 처리 여부
    
    # 관계 설정
    author = db.relationship("User", backref="notices")
    reads = db.relationship("NoticeRead", backref="notice", cascade="all, delete-orphan")
    comments = db.relationship("NoticeComment", backref="notice", cascade="all, delete-orphan")
    
    # 검색 최적화를 위한 인덱스 추가
    __table_args__ = (
        db.Index('idx_notice_author_date', 'author_id', 'created_at'),
        db.Index('idx_notice_category_date', 'category', 'created_at'),
        db.Index('idx_notice_hidden_date', 'is_hidden', 'created_at'),
    )

    def __repr__(self):
        return f'<Notice {self.id}: {self.title}>'

# 공지사항 읽음 모델
class NoticeRead(db.Model):
    __tablename__ = "notice_reads"
    id = db.Column(db.Integer, primary_key=True)
    notice_id = db.Column(db.Integer, db.ForeignKey('notices.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    read_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    
    # 복합 인덱스 추가
    __table_args__ = (
        db.Index('idx_noticeread_user_notice', 'user_id', 'notice_id'),
    )
    
    def __repr__(self):
        return f'<NoticeRead user:{self.user_id} notice:{self.notice_id}>'

# 익명 건의함 모델
class Suggestion(db.Model):
    __tablename__ = "suggestions"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    answered_at = db.Column(db.DateTime, index=True)
    is_anonymous = db.Column(db.Boolean, default=True, index=True)
    
    # 복합 인덱스 추가
    __table_args__ = (
        db.Index('idx_suggestion_created', 'created_at'),
        db.Index('idx_suggestion_answered', 'answered_at'),
    )
    
    def __repr__(self):
        return f'<Suggestion {self.id}>'

# 공지사항 댓글 모델
class NoticeComment(db.Model):
    __tablename__ = "notice_comments"
    id = db.Column(db.Integer, primary_key=True)
    notice_id = db.Column(db.Integer, db.ForeignKey('notices.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    is_hidden = db.Column(db.Boolean, default=False, index=True)  # 숨김 처리 여부
    
    # 관계 설정
    user = db.relationship("User", backref="notice_comments")
    
    # 복합 인덱스 추가
    __table_args__ = (
        db.Index('idx_comment_notice_date', 'notice_id', 'created_at'),
        db.Index('idx_comment_user_date', 'user_id', 'created_at'),
        db.Index('idx_comment_hidden_date', 'is_hidden', 'created_at'),
    )
    
    def __repr__(self):
        return f'<NoticeComment {self.id}>'

# 공지사항 변경이력 모델
class NoticeHistory(db.Model):
    __tablename__ = "notice_histories"
    id = db.Column(db.Integer, primary_key=True)
    notice_id = db.Column(db.Integer, db.ForeignKey('notices.id'), nullable=False, index=True)
    editor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    before_title = db.Column(db.String(100))
    before_content = db.Column(db.Text)
    before_file_path = db.Column(db.String(255))
    before_file_type = db.Column(db.String(20))
    edited_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    action = db.Column(db.String(10), index=True)  # 'edit'/'delete'/'hide'/'unhide'
    ip_address = db.Column(db.String(45))
    
    # 관계 설정
    editor = db.relationship("User", backref="notice_histories")
    notice = db.relationship("Notice", backref="histories")
    
    # 복합 인덱스 추가
    __table_args__ = (
        db.Index('idx_history_notice_date', 'notice_id', 'edited_at'),
        db.Index('idx_history_editor_date', 'editor_id', 'edited_at'),
        db.Index('idx_history_action_date', 'action', 'edited_at'),
    )
    
    def __repr__(self):
        return f'<NoticeHistory {self.id} for notice {self.notice_id}>'

# 댓글 변경이력 모델
class CommentHistory(db.Model):
    __tablename__ = "comment_histories"
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('notice_comments.id'), nullable=False, index=True)
    editor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    before_content = db.Column(db.Text)
    edited_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    action = db.Column(db.String(10), index=True)  # 'edit'/'delete'/'hide'/'unhide'
    ip_address = db.Column(db.String(45))
    
    # 관계 설정
    editor = db.relationship("User", backref="comment_histories")
    comment = db.relationship("NoticeComment", backref="histories")
    
    # 복합 인덱스 추가
    __table_args__ = (
        db.Index('idx_comment_history_comment_date', 'comment_id', 'edited_at'),
        db.Index('idx_comment_history_editor_date', 'editor_id', 'edited_at'),
        db.Index('idx_comment_history_action_date', 'action', 'edited_at'),
    )
    
    def __repr__(self):
        return f'<CommentHistory {self.id} for comment {self.comment_id}>'

# 신고 모델
class Report(db.Model):
    __tablename__ = "reports"
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(10), nullable=False, index=True)  # 'notice'/'comment'
    target_id = db.Column(db.Integer, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reason = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), index=True)  # '욕설/비방', '음란', '홍보', '기타'
    detail = db.Column(db.Text)  # 상세 사유
    status = db.Column(db.String(20), default='pending', index=True)  # 'pending'/'reviewed'/'resolved'
    admin_comment = db.Column(db.Text)  # 관리자 처리 코멘트
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    reviewed_at = db.Column(db.DateTime, index=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    
    # 관계 설정
    reporter = db.relationship("User", foreign_keys=[user_id], backref="reports")
    reviewer = db.relationship("User", foreign_keys=[reviewed_by], backref="reviewed_reports")
    
    # 복합 인덱스 추가
    __table_args__ = (
        db.Index('idx_report_target', 'target_type', 'target_id'),
        db.Index('idx_report_user_date', 'user_id', 'created_at'),
        db.Index('idx_report_status_date', 'status', 'created_at'),
        db.Index('idx_report_category', 'category'),
    )
    
    def __repr__(self):
        return f'<Report {self.id} for {self.target_type}:{self.target_id}>'

class SystemLog(db.Model):
    """시스템 로그 모델"""
    __tablename__ = 'system_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.String(500), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # 관계 설정
    user = db.relationship('User', backref='system_logs')

    def __repr__(self):
        return f'<SystemLog {self.id}: {self.action}>'
