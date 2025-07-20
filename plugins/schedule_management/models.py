"""
스케줄관리 플러그인 데이터베이스 모델
"""

from datetime import datetime, time
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from extensions import db
import enum

class ShiftType(enum.Enum):
    """근무 유형"""
    MORNING = "morning"  # 오전
    AFTERNOON = "afternoon"  # 오후
    NIGHT = "night"  # 야간
    FULL_DAY = "full_day"  # 종일
    PART_TIME = "part_time"  # 파트타임

class ScheduleStatus(enum.Enum):
    """스케줄 상태"""
    DRAFT = "draft"  # 임시저장
    PUBLISHED = "published"  # 발표됨
    CONFIRMED = "confirmed"  # 확정됨
    CANCELLED = "cancelled"  # 취소됨

class RequestStatus(enum.Enum):
    """요청 상태"""
    PENDING = "pending"  # 대기
    APPROVED = "approved"  # 승인
    REJECTED = "rejected"  # 거절

class WorkSchedule(db.Model):
    """근무 스케줄 모델"""
    __tablename__ = 'work_schedules'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    schedule_date = Column(DateTime, nullable=False)
    shift_type = Column(Enum(ShiftType), nullable=False)
    start_time = Column(String(5), nullable=False)  # HH:MM 형식
    end_time = Column(String(5), nullable=False)  # HH:MM 형식
    break_start = Column(String(5), nullable=True)  # 휴식 시작
    break_end = Column(String(5), nullable=True)  # 휴식 종료
    total_hours = Column(Float, default=0.0)  # 총 근무시간
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.DRAFT)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    store = relationship('Branch', backref='work_schedules')
    user = relationship('User', foreign_keys=[user_id], backref='work_schedules')
    created_user = relationship('User', foreign_keys=[created_by], backref='created_schedules')
    
    def __repr__(self):
        return f'<WorkSchedule {self.user_id} {self.schedule_date.date()}>'
    
    def calculate_hours(self):
        """근무시간 계산"""
        start = datetime.strptime(self.start_time, '%H:%M')
        end = datetime.strptime(self.end_time, '%H:%M')
        
        # 날짜가 다른 경우 (야간 근무 등)
        if end < start:
            end = end.replace(day=end.day + 1)
        
        work_duration = end - start
        self.total_hours = work_duration.total_seconds() / 3600
        
        # 휴식시간 차감
        if self.break_start and self.break_end:
            break_start = datetime.strptime(self.break_start, '%H:%M')
            break_end = datetime.strptime(self.break_end, '%H:%M')
            
            if break_end < break_start:
                break_end = break_end.replace(day=break_end.day + 1)
            
            break_duration = break_end - break_start
            break_hours = break_duration.total_seconds() / 3600
            self.total_hours -= break_hours
        
        return self.total_hours

class ScheduleTemplate(db.Model):
    """스케줄 템플릿 모델"""
    __tablename__ = 'schedule_templates'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    shift_type = Column(Enum(ShiftType), nullable=False)
    start_time = Column(String(5), nullable=False)
    end_time = Column(String(5), nullable=False)
    break_start = Column(String(5), nullable=True)
    break_end = Column(String(5), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    store = relationship('Branch', backref='schedule_templates')
    
    def __repr__(self):
        return f'<ScheduleTemplate {self.name}>'

class ScheduleRequest(db.Model):
    """스케줄 변경 요청 모델"""
    __tablename__ = 'schedule_requests'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    schedule_id = Column(Integer, ForeignKey('work_schedules.id'), nullable=False)
    request_type = Column(String(20), nullable=False)  # change, swap, cancel
    requested_date = Column(DateTime, nullable=False)
    requested_start_time = Column(String(5), nullable=True)
    requested_end_time = Column(String(5), nullable=True)
    reason = Column(Text, nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    user = relationship('User', foreign_keys=[user_id], backref='schedule_requests')
    schedule = relationship('WorkSchedule', backref='schedule_requests')
    approved_user = relationship('User', foreign_keys=[approved_by], backref='approved_schedule_requests')
    
    def __repr__(self):
        return f'<ScheduleRequest {self.user_id} {self.request_type}>'

class ScheduleSettings(db.Model):
    """스케줄 관리 설정 모델"""
    __tablename__ = 'schedule_settings'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    default_shift_hours = Column(Float, default=8.0)
    break_time_minutes = Column(Integer, default=60)
    overtime_threshold = Column(Float, default=8.0)
    auto_schedule_enabled = Column(Boolean, default=False)
    max_consecutive_days = Column(Integer, default=7)  # 최대 연속 근무일
    min_rest_hours = Column(Float, default=11.0)  # 최소 휴식시간
    schedule_publish_days = Column(Integer, default=7)  # 스케줄 발표일 (일전)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    store = relationship('Branch', backref='schedule_settings')
    
    def __repr__(self):
        return f'<ScheduleSettings {self.store_id}>'

class ScheduleReport(db.Model):
    """스케줄 리포트 모델"""
    __tablename__ = 'schedule_reports'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    report_date = Column(DateTime, nullable=False)
    total_schedules = Column(Integer, default=0)
    total_hours = Column(Float, default=0.0)
    overtime_hours = Column(Float, default=0.0)
    pending_requests = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    store = relationship('Branch', backref='schedule_reports')
    
    def __repr__(self):
        return f'<ScheduleReport {self.store_id} {self.report_date.date()}>' 