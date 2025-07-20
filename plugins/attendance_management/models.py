"""
출근관리 플러그인 데이터베이스 모델
"""

from datetime import datetime, time
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from extensions import db

class AttendanceRecord(db.Model):
    """출근 기록 모델"""
    __tablename__ = 'attendance_records'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    store_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    check_in_time = Column(DateTime, nullable=True)
    check_out_time = Column(DateTime, nullable=True)
    work_hours = Column(Float, default=0.0)  # 실제 근무시간 (시간)
    break_hours = Column(Float, default=0.0)  # 휴식시간 (시간)
    overtime_hours = Column(Float, default=0.0)  # 초과근무시간 (시간)
    status = Column(String(20), default='present')  # present, absent, late, early_leave
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    user = relationship('User', backref='attendance_records')
    store = relationship('Branch', backref='attendance_records')
    
    def __repr__(self):
        return f'<AttendanceRecord {self.user_id} {self.date.date()}>'
    
    def calculate_work_hours(self):
        """근무시간 계산"""
        if self.check_in_time and self.check_out_time:
            work_duration = self.check_out_time - self.check_in_time
            self.work_hours = work_duration.total_seconds() / 3600
            return self.work_hours
        return 0.0

class AttendanceSettings(db.Model):
    """출근 설정 모델"""
    __tablename__ = 'attendance_settings'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    work_start_time = Column(String(5), default='09:00')  # HH:MM 형식
    work_end_time = Column(String(5), default='18:00')  # HH:MM 형식
    break_time = Column(Integer, default=60)  # 분 단위
    overtime_threshold = Column(Float, default=8.0)  # 시간 단위
    late_threshold = Column(Integer, default=15)  # 분 단위
    early_leave_threshold = Column(Integer, default=30)  # 분 단위
    flexible_work = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    store = relationship('Branch', backref='attendance_settings')
    
    def __repr__(self):
        return f'<AttendanceSettings {self.store_id}>'

class AttendanceReport(db.Model):
    """출근 통계 리포트 모델"""
    __tablename__ = 'attendance_reports'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    report_date = Column(DateTime, nullable=False)
    total_work_hours = Column(Float, default=0.0)
    total_break_hours = Column(Float, default=0.0)
    total_overtime_hours = Column(Float, default=0.0)
    late_count = Column(Integer, default=0)
    absent_count = Column(Integer, default=0)
    early_leave_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    store = relationship('Branch', backref='attendance_reports')
    user = relationship('User', backref='attendance_reports')
    
    def __repr__(self):
        return f'<AttendanceReport {self.user_id} {self.report_date.date()}>' 