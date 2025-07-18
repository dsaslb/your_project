from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional


class AttendanceService:
    def __init__(self):
        self.data_file = "data/attendance_records.json"
        self.ensure_data_file()

    def ensure_data_file(self):
        """데이터 파일이 존재하는지 확인하고 없으면 생성"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def load_attendance_data(self) -> List[Dict]:
        """출근 데이터 로드"""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_attendance_data(self, data: List[Dict]):
        """출근 데이터 저장"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_attendance_record(self, record: Dict) -> Dict:
        """출근 기록 저장"""
        try:
            data = self.load_attendance_data()

            # 중복 체크 (같은 날짜에 이미 출근 기록이 있는지)
            today = datetime.now().strftime("%Y-%m-%d")
            existing_record = next(
                (
                    r
                    for r in data
                    if r.get("employee_id") == record["employee_id"]
                    and r.get("date", "").startswith(today)
                ),
                None,
            )

            if existing_record:
                return {"success": False, "error": "이미 오늘 출근 기록이 있습니다."}

            # 새 기록 추가
            record["id"] = f"att_{len(data) + 1}"
            record["date"] = datetime.now().strftime("%Y-%m-%d")
            data.append(record)

            self.save_attendance_data(data)
            return {"success": True, "data": record}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_attendance_record(self, record: Dict) -> Dict:
        """출근 기록 업데이트 (퇴근)"""
        try:
            data = self.load_attendance_data()

            # 오늘 출근 기록 찾기
            today = datetime.now().strftime("%Y-%m-%d")
            existing_record = next(
                (
                    r
                    for r in data
                    if r.get("employee_id") == record["employee_id"]
                    and r.get("date", "").startswith(today)
                ),
                None,
            )

            if not existing_record:
                return {"success": False, "error": "출근 기록을 찾을 수 없습니다."}

            # 퇴근 정보 업데이트
            existing_record.update(record)
            existing_record["status"] = "checked_out"

            self.save_attendance_data(data)
            return {"success": True, "data": existing_record}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def calculate_work_hours(self, employee_id: str, check_out_time: datetime) -> float:
        """근무 시간 계산"""
        try:
            data = self.load_attendance_data()
            today = datetime.now().strftime("%Y-%m-%d")

            # 오늘 출근 기록 찾기
            record = next(
                (
                    r
                    for r in data
                    if r.get("employee_id") == employee_id
                    and r.get("date", "").startswith(today)
                ),
                None,
            )

            if not record or not record.get("check_in_time"):
                return 0.0

            # 출근 시간 파싱
            check_in_time = datetime.fromisoformat(record["check_in_time"])

            # 근무 시간 계산 (시간 단위)
            work_duration = check_out_time - check_in_time
            work_hours = work_duration.total_seconds() / 3600

            return round(work_hours, 2)

        except Exception as e:
            print(f"근무 시간 계산 오류: {e}")
            return 0.0

    def has_permission(self, user_id: str, user_type: str, permission: str) -> bool:
        """권한 확인"""
        # 권한 매트릭스 정의
        permission_matrix = {
            "admin": {
                "attendance": ["view_all", "edit_all", "delete_all", "export_data"],
                "reports": ["view_all", "create_all", "export_all"],
                "settings": ["view_all", "edit_all"],
            },
            "brand_manager": {
                "attendance": ["view_brand", "edit_brand", "export_brand"],
                "reports": ["view_brand", "create_brand", "export_brand"],
                "settings": ["view_brand", "edit_brand"],
            },
            "store_manager": {
                "attendance": ["view_store", "edit_store", "export_store"],
                "reports": ["view_store", "create_store", "export_store"],
                "settings": ["view_store", "edit_store"],
            },
            "supervisor": {
                "attendance": ["view_team", "edit_team"],
                "reports": ["view_team", "create_team"],
                "settings": ["view_team"],
            },
            "employee": {
                "attendance": ["view_own", "check_in", "check_out"],
                "reports": ["view_own"],
                "settings": [],
            },
        }

        # 권한 확인
        if user_type in permission_matrix:
            if "attendance" in permission_matrix[user_type]:
                return permission in permission_matrix[user_type]["attendance"]

        return False

    def get_attendance_data(
        self,
        user_id: str,
        user_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict:
        """출근 데이터 조회"""
        try:
            data = self.load_attendance_data()

            # 날짜 필터링
            if start_date:
                data = [r for r in data if r.get("date", "") >= start_date]
            if end_date:
                data = [r for r in data if r.get("date", "") <= end_date]

            # 권한에 따른 필터링
            if user_type == "employee":
                # 직원은 자신의 데이터만 조회
                data = [r for r in data if r.get("employee_id") == user_id]
            elif user_type in ["supervisor", "store_manager", "brand_manager"]:
                # 관리자는 팀/매장/브랜드 데이터 조회 (실제로는 더 복잡한 로직 필요)
                pass  # 현재는 모든 데이터 반환

            return {
                "records": data,
                "total_count": len(data),
                "filtered_by": {
                    "user_type": user_type,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            }

        except Exception as e:
            return {"error": str(e)}

    def get_attendance_stats(self, user_id: str, user_type: str) -> Dict:
        """출근 통계 조회"""
        try:
            data = self.load_attendance_data()

            # 권한에 따른 필터링
            if user_type == "employee":
                data = [r for r in data if r.get("employee_id") == user_id]

            # 통계 계산
            total_records = len(data)
            present_count = len([r for r in data if r.get("status") == "checked_out"])
            late_count = len([r for r in data if r.get("is_late", False)])
            absent_count = total_records - present_count

            # 평균 근무 시간
            work_hours = [r.get("work_hours", 0) for r in data if r.get("work_hours")]
            avg_work_hours = sum(work_hours) / len(work_hours) if work_hours else 0

            # 정시 출근률
            on_time_rate = (
                ((total_records - late_count) / total_records * 100)
                if total_records > 0
                else 0
            )

            return {
                "total_records": total_records,
                "present_count": present_count,
                "late_count": late_count,
                "absent_count": absent_count,
                "average_work_hours": round(avg_work_hours, 2),
                "on_time_rate": round(on_time_rate, 1),
                "period": "all_time",
            }

        except Exception as e:
            return {"error": str(e)}

    def get_today_attendance(self, user_id: str, user_type: str) -> Dict:
        """오늘의 출근 현황"""
        try:
            data = self.load_attendance_data()
            today = datetime.now().strftime("%Y-%m-%d")

            # 오늘 데이터만 필터링
            today_data = [r for r in data if r.get("date", "").startswith(today)]

            # 권한에 따른 필터링
            if user_type == "employee":
                today_data = [r for r in today_data if r.get("employee_id") == user_id]

            # 통계 계산
            total_employees = len(set(r.get("employee_id") for r in today_data))
            present_today = len(
                [r for r in today_data if r.get("status") == "checked_out"]
            )
            late_count = len([r for r in today_data if r.get("is_late", False)])

            # 평균 근무 시간
            work_hours = [
                r.get("work_hours", 0) for r in today_data if r.get("work_hours")
            ]
            avg_work_hours = sum(work_hours) / len(work_hours) if work_hours else 0

            # 총 초과근무 시간 (8시간 초과)
            overtime_hours = sum([max(0, h - 8) for h in work_hours])

            return {
                "records": today_data,
                "statistics": {
                    "total_employees": total_employees,
                    "present_today": present_today,
                    "late_count": late_count,
                    "average_work_hours": round(avg_work_hours, 2),
                    "total_overtime": round(overtime_hours, 2),
                    "on_time_rate": round(
                        (
                            ((total_employees - late_count) / total_employees * 100)
                            if total_employees > 0
                            else 0
                        ),
                        1,
                    ),
                },
            }

        except Exception as e:
            return {"error": str(e)}

    def export_attendance_data(
        self,
        user_id: str,
        user_type: str,
        format_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict:
        """출근 데이터 내보내기"""
        try:
            # 데이터 조회
            data_result = self.get_attendance_data(
                user_id, user_type, start_date, end_date
            )

            if "error" in data_result:
                return {"success": False, "error": data_result["error"]}

            records = data_result["records"]

            # 형식에 따른 내보내기
            if format_type == "excel":
                # Excel 형식으로 변환 (실제로는 pandas 사용)
                export_data = {
                    "format": "excel",
                    "filename": f'attendance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                    "data": records,
                    "columns": [
                        "id",
                        "employee_id",
                        "date",
                        "check_in_time",
                        "check_out_time",
                        "work_hours",
                        "is_late",
                        "status",
                    ],
                }
            elif format_type == "csv":
                # CSV 형식으로 변환
                export_data = {
                    "format": "csv",
                    "filename": f'attendance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    "data": records,
                    "columns": [
                        "id",
                        "employee_id",
                        "date",
                        "check_in_time",
                        "check_out_time",
                        "work_hours",
                        "is_late",
                        "status",
                    ],
                }
            else:
                return {"success": False, "error": "지원하지 않는 형식입니다."}

            return {"success": True, "data": export_data}

        except Exception as e:
            return {"success": False, "error": str(e)}
