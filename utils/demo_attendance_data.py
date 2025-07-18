"""
출퇴근 관리 모듈 데모 데이터
마켓플레이스에서 미리보기/데모 실행 시 사용되는 샘플 데이터
"""

import json
from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional
import random


class DemoAttendanceData:
    """출퇴근 관리 모듈 데모 데이터"""

    @staticmethod
    def get_demo_users() -> Optional[List[Dict[str, Any]]]:
        """데모용 직원 데이터"""
        return [
            {
                "id": 1,
                "name": "김매니저",
                "position": "매니저",
                "department": "매장관리",
                "branch_id": 1,
                "work_start_time": "09:00",
                "work_end_time": "18:00",
                "status": "active"
            },
            {
                "id": 2,
                "name": "이직원",
                "position": "직원",
                "department": "서빙",
                "branch_id": 1,
                "work_start_time": "09:00",
                "work_end_time": "18:00",
                "status": "active"
            },
            {
                "id": 3,
                "name": "박주방",
                "position": "주방장",
                "department": "주방",
                "branch_id": 1,
                "work_start_time": "08:00",
                "work_end_time": "17:00",
                "status": "active"
            },
            {
                "id": 4,
                "name": "최서빙",
                "position": "직원",
                "department": "서빙",
                "branch_id": 1,
                "work_start_time": "10:00",
                "work_end_time": "19:00",
                "status": "active"
            },
            {
                "id": 5,
                "name": "정청소",
                "position": "직원",
                "department": "청소",
                "branch_id": 1,
                "work_start_time": "07:00",
                "work_end_time": "16:00",
                "status": "active"
            }
        ]

    @staticmethod
    def get_demo_attendance_data(days: int = 30) -> Optional[List[Dict[str, Any]]]:
        """데모용 출퇴근 데이터 (최근 N일)"""
        attendance_data = []
        today = datetime.now()

        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')

            # 각 직원별 출퇴근 데이터 생성
            for user in DemoAttendanceData.get_demo_users() or []:
                # 주말 제외 (토,일)
                if date.weekday() >= 5:
                    continue

                # 출근 시간 (정시 또는 지각)
                clock_in_hour = 9
                clock_in_minute = 0

                # 20% 확률로 지각
                if random.random() < 0.2:
                    clock_in_hour = 9
                    clock_in_minute = random.randint(5, 45)

                # 퇴근 시간 (정시 또는 초과근무)
                clock_out_hour = 18
                clock_out_minute = 0

                # 30% 확률로 초과근무
                if random.random() < 0.3:
                    clock_out_hour = random.randint(18, 22)
                    clock_out_minute = random.randint(0, 59)

                # 5% 확률로 조퇴
                if random.random() < 0.05:
                    clock_out_hour = random.randint(15, 17)
                    clock_out_minute = random.randint(0, 59)

                # 2% 확률로 결근
                if random.random() < 0.02:
                    continue

                clock_in = datetime.combine(date, time(clock_in_hour, clock_in_minute))
                clock_out = datetime.combine(date, time(clock_out_hour, clock_out_minute))

                # 근무 시간 계산
                work_hours = (clock_out - clock_in).total_seconds() / 3600

                # 지각/조퇴/초과근무 판정
                is_late = clock_in.time() > time(9, 0)
                is_early_leave = clock_out.time() < time(18, 0)
                is_overtime = clock_out.time() > time(18, 0)

                attendance_data.append({
                    "id": len(attendance_data) + 1,
                    "user_id": user["id"],
                    "user_name": user["name"],
                    "date": date_str,
                    "clock_in": clock_in.strftime('%Y-%m-%d %H:%M:%S'),
                    "clock_out": clock_out.strftime('%Y-%m-%d %H:%M:%S'),
                    "work_hours": round(work_hours, 2),
                    "is_late": is_late,
                    "is_early_leave": is_early_leave,
                    "is_overtime": is_overtime,
                    "status": "completed"
                })

        return attendance_data

    @staticmethod
    def get_demo_statistics() -> Optional[Dict[str, Any]]:
        """데모용 통계 데이터"""
        attendance_data = DemoAttendanceData.get_demo_attendance_data() or []

        total_records = len(attendance_data)
        late_count = sum(1 for record in attendance_data if record and record.get("is_late"))
        early_leave_count = sum(1 for record in attendance_data if record and record.get("is_early_leave"))
        overtime_count = sum(1 for record in attendance_data if record and record.get("is_overtime"))

        total_work_hours = sum(record["work_hours"] for record in attendance_data if record)
        avg_work_hours = total_work_hours / total_records if total_records > 0 else 0

        # 직원별 통계
        user_stats = {}
        for user in DemoAttendanceData.get_demo_users() or []:
            user_records = [r for r in attendance_data if r and r.get("user_id") == user["id"]]
            if user_records:
                user_stats[user["name"]] = {
                    "total_days": len(user_records),
                    "late_count": sum(1 for r in user_records if r and r.get("is_late")),
                    "early_leave_count": sum(1 for r in user_records if r and r.get("is_early_leave")),
                    "overtime_count": sum(1 for r in user_records if r and r.get("is_overtime")),
                    "avg_work_hours": sum(r["work_hours"] for r in user_records if r) / len(user_records)
                }

        return {
            "total_records": total_records,
            "late_count": late_count,
            "early_leave_count": early_leave_count,
            "overtime_count": overtime_count,
            "avg_work_hours": round(avg_work_hours, 2),
            "late_rate": round(late_count / total_records * 100, 1) if total_records > 0 else 0,
            "early_leave_rate": round(early_leave_count / total_records * 100, 1) if total_records > 0 else 0,
            "overtime_rate": round(overtime_count / total_records * 100, 1) if total_records > 0 else 0,
            "user_statistics": user_stats
        }

    @staticmethod
    def get_demo_realtime_data() -> Optional[Dict[str, Any]]:
        """실시간 데모 데이터 (오늘)"""
        today = datetime.now()
        today_str = today.strftime('%Y-%m-%d')

        # 오늘 출근한 직원들
        today_attendance = []
        for user in DemoAttendanceData.get_demo_users() or []:
            # 80% 확률로 출근
            if random.random() < 0.8:
                clock_in_hour = 9
                clock_in_minute = random.randint(-15, 30)  # 8:45 ~ 9:30

                if clock_in_minute < 0:
                    clock_in_hour -= 1
                    clock_in_minute += 60

                clock_in = datetime.combine(today, time(clock_in_hour, clock_in_minute))

                # 퇴근 여부 (현재 시간 기준)
                current_time = datetime.now()
                if current_time.hour >= 18:
                    # 퇴근 시간이 지났으면 퇴근 처리
                    clock_out_hour = random.randint(18, 21)
                    clock_out_minute = random.randint(0, 59)
                    clock_out = datetime.combine(today, time(clock_out_hour, clock_out_minute))
                    status = "completed"
                else:
                    # 아직 근무 중
                    clock_out = None
                    status = "checked_in"

                today_attendance.append({
                    "user_id": user["id"],
                    "user_name": user["name"],
                    "position": user["position"],
                    "clock_in": clock_in.strftime('%H:%M'),
                    "clock_out": clock_out.strftime('%H:%M') if clock_out else None,
                    "status": status,
                    "is_late": clock_in.time() > time(9, 0)
                })

        return {
            "date": today_str,
            "total_employees": len(DemoAttendanceData.get_demo_users() or []),
            "checked_in": len([a for a in today_attendance if a and a.get("status") == "checked_in"]),
            "completed": len([a for a in today_attendance if a and a.get("status") == "completed"]),
            "late_count": len([a for a in today_attendance if a and a.get("is_late")]),
            "attendance_list": today_attendance
        }

    @staticmethod
    def get_demo_notifications() -> Optional[List[Dict[str, Any]]]:
        """데모용 알림 데이터"""
        return [
            {
                "id": 1,
                "type": "late",
                "title": "지각 알림",
                "message": "김매니저님이 9:15에 출근하셨습니다.",
                "user_name": "김매니저",
                "time": "09:15",
                "priority": "warning"
            },
            {
                "id": 2,
                "type": "overtime",
                "title": "초과근무 알림",
                "message": "이직원님이 20:30까지 근무하셨습니다.",
                "user_name": "이직원",
                "time": "20:30",
                "priority": "info"
            },
            {
                "id": 3,
                "type": "early_leave",
                "title": "조퇴 알림",
                "message": "박주방님이 16:30에 퇴근하셨습니다.",
                "user_name": "박주방",
                "time": "16:30",
                "priority": "warning"
            }
        ]

    @staticmethod
    def get_demo_settings() -> Optional[Dict[str, Any]]:
        """데모용 설정 데이터"""
        return {
            "work_start_time": "09:00",
            "work_end_time": "18:00",
            "late_threshold_minutes": 5,
            "overtime_threshold_hours": 8,
            "auto_approval": True,
            "notification_enabled": True,
            "report_generation": "daily",
            "integration": {
                "payroll": True,
                "schedule": True,
                "analytics": True
            }
        }

    @staticmethod
    def get_full_demo_data() -> Optional[Dict[str, Any]]:
        """전체 데모 데이터"""
        return {
            "users": DemoAttendanceData.get_demo_users(),
            "attendance": DemoAttendanceData.get_demo_attendance_data(),
            "statistics": DemoAttendanceData.get_demo_statistics(),
            "realtime": DemoAttendanceData.get_demo_realtime_data(),
            "notifications": DemoAttendanceData.get_demo_notifications(),
            "settings": DemoAttendanceData.get_demo_settings()
        }
