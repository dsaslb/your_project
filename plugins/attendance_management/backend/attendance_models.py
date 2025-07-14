from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict

@dataclass
class AttendanceRecord:
    """출근 기록 모델"""
    id: str
    employee_id: str
    date: str
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    work_hours: Optional[float] = None
    is_late: bool = False
    overtime_hours: float = 0.0
    status: str = 'pending'
    location: str = 'main_office'
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'date': self.date,
            'check_in_time': self.check_in_time,
            'check_out_time': self.check_out_time,
            'work_hours': self.work_hours,
            'is_late': self.is_late,
            'overtime_hours': self.overtime_hours,
            'status': self.status,
            'location': self.location,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AttendanceRecord':
        """딕셔너리에서 생성"""
        return cls(
            id=data.get('id', ''),
            employee_id=data.get('employee_id', ''),
            date=data.get('date', ''),
            check_in_time=data.get('check_in_time'),
            check_out_time=data.get('check_out_time'),
            work_hours=data.get('work_hours'),
            is_late=data.get('is_late', False),
            overtime_hours=data.get('overtime_hours', 0.0),
            status=data.get('status', 'pending'),
            location=data.get('location', 'main_office'),
            notes=data.get('notes')
        )

@dataclass
class AttendanceStats:
    """출근 통계 모델"""
    total_records: int
    present_count: int
    late_count: int
    absent_count: int
    average_work_hours: float
    on_time_rate: float
    total_overtime: float
    period: str
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            'total_records': self.total_records,
            'present_count': self.present_count,
            'late_count': self.late_count,
            'absent_count': self.absent_count,
            'average_work_hours': self.average_work_hours,
            'on_time_rate': self.on_time_rate,
            'total_overtime': self.total_overtime,
            'period': self.period
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AttendanceStats':
        """딕셔너리에서 생성"""
        return cls(
            total_records=data.get('total_records', 0),
            present_count=data.get('present_count', 0),
            late_count=data.get('late_count', 0),
            absent_count=data.get('absent_count', 0),
            average_work_hours=data.get('average_work_hours', 0.0),
            on_time_rate=data.get('on_time_rate', 0.0),
            total_overtime=data.get('total_overtime', 0.0),
            period=data.get('period', 'all_time')
        )

@dataclass
class Employee:
    """직원 모델"""
    id: str
    name: str
    position: str
    store_id: str
    brand_id: str
    avatar: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'store_id': self.store_id,
            'brand_id': self.brand_id,
            'avatar': self.avatar
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Employee':
        """딕셔너리에서 생성"""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            position=data.get('position', ''),
            store_id=data.get('store_id', ''),
            brand_id=data.get('brand_id', ''),
            avatar=data.get('avatar')
        )

@dataclass
class AttendanceReport:
    """출근 리포트 모델"""
    records: List[AttendanceRecord]
    statistics: AttendanceStats
    filters: Dict
    generated_at: datetime
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            'records': [record.to_dict() for record in self.records],
            'statistics': self.statistics.to_dict(),
            'filters': self.filters,
            'generated_at': self.generated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AttendanceReport':
        """딕셔너리에서 생성"""
        return cls(
            records=[AttendanceRecord.from_dict(r) for r in data.get('records', [])],
            statistics=AttendanceStats.from_dict(data.get('statistics', {})),
            filters=data.get('filters', {}),
            generated_at=datetime.fromisoformat(data.get('generated_at', datetime.now().isoformat()))
        ) 