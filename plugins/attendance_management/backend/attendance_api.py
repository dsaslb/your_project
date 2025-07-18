from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import jwt
from .attendance_service import AttendanceService

attendance_bp = Blueprint("attendance", __name__)
attendance_service = AttendanceService()


@attendance_bp.route("/api/attendance/check-in", methods=["POST"])
def check_in():
    """직원 출근 체크인"""
    try:
        data = request.get_json()
        employee_id = data.get("employee_id")
        location = data.get("location", "main_office")

        if not employee_id:
            return jsonify({"error": "직원 ID가 필요합니다."}), 400

        # 출근 시간 기록
        check_in_time = datetime.now()

        # 지각 여부 확인 (기본 출근시간: 9:00)
        is_late = check_in_time.time() > datetime.strptime("09:00", "%H:%M").time()

        attendance_record = {
            "employee_id": employee_id,
            "check_in_time": check_in_time.isoformat(),
            "location": location,
            "is_late": is_late,
            "status": "checked_in",
        }

        # 데이터베이스에 저장
        result = attendance_service.save_attendance_record(attendance_record)

        if result["success"]:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "출근이 기록되었습니다.",
                        "data": attendance_record,
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": result["error"]}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@attendance_bp.route("/api/attendance/check-out", methods=["POST"])
def check_out():
    """직원 퇴근 체크아웃"""
    try:
        data = request.get_json()
        employee_id = data.get("employee_id")

        if not employee_id:
            return jsonify({"error": "직원 ID가 필요합니다."}), 400

        # 퇴근 시간 기록
        check_out_time = datetime.now()

        # 근무 시간 계산
        work_hours = attendance_service.calculate_work_hours(
            employee_id, check_out_time
        )

        attendance_record = {
            "employee_id": employee_id,
            "check_out_time": check_out_time.isoformat(),
            "work_hours": work_hours,
            "status": "checked_out",
        }

        result = attendance_service.update_attendance_record(attendance_record)

        if result["success"]:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "퇴근이 기록되었습니다.",
                        "data": attendance_record,
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": result["error"]}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@attendance_bp.route("/api/attendance/report/<user_type>", methods=["GET"])
def get_attendance_report(user_type):
    """출근부 리포트 조회"""
    try:
        user_id = request.args.get("user_id")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if not user_id:
            return jsonify({"error": "사용자 ID가 필요합니다."}), 400

        # 권한 확인
        if not attendance_service.has_permission(user_id, user_type, "view_attendance"):
            return jsonify({"error": "권한이 없습니다."}), 403

        # 데이터 조회
        report_data = attendance_service.get_attendance_data(
            user_id, user_type, start_date, end_date
        )

        return jsonify({"success": True, "data": report_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@attendance_bp.route("/api/attendance/stats", methods=["GET"])
def get_attendance_stats():
    """출근 통계 조회"""
    try:
        user_id = request.args.get("user_id")
        user_type = request.args.get("user_type", "employee")

        if not user_id:
            return jsonify({"error": "사용자 ID가 필요합니다."}), 400

        # 권한 확인
        if not attendance_service.has_permission(user_id, user_type, "view_attendance"):
            return jsonify({"error": "권한이 없습니다."}), 403

        # 통계 데이터 조회
        stats_data = attendance_service.get_attendance_stats(user_id, user_type)

        return jsonify({"success": True, "data": stats_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@attendance_bp.route("/api/attendance/today", methods=["GET"])
def get_today_attendance():
    """오늘의 출근 현황"""
    try:
        user_id = request.args.get("user_id")
        user_type = request.args.get("user_type", "employee")

        if not user_id:
            return jsonify({"error": "사용자 ID가 필요합니다."}), 400

        # 오늘 출근 데이터 조회
        today_data = attendance_service.get_today_attendance(user_id, user_type)

        return jsonify({"success": True, "data": today_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@attendance_bp.route("/api/attendance/export", methods=["GET"])
def export_attendance():
    """출근 데이터 내보내기"""
    try:
        user_id = request.args.get("user_id")
        user_type = request.args.get("user_type", "employee")
        format_type = request.args.get("format", "excel")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if not user_id:
            return jsonify({"error": "사용자 ID가 필요합니다."}), 400

        # 권한 확인
        if not attendance_service.has_permission(user_id, user_type, "export_data"):
            return jsonify({"error": "내보내기 권한이 없습니다."}), 403

        # 데이터 내보내기
        export_result = attendance_service.export_attendance_data(
            user_id, user_type, format_type, start_date, end_date
        )

        if export_result["success"]:
            return jsonify({"success": True, "data": export_result["data"]}), 200
        else:
            return jsonify({"error": export_result["error"]}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
