from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.employee import UserInfo, EmployeeSchedule, EmployeeAttendance
from datetime import datetime, timedelta
import json

schedule_report = Blueprint('schedule_report', __name__)

@schedule_report.route('/schedule/reports/summary', methods=['GET'])
@login_required
def get_schedule_summary_report():
    """스케줄 요약 리포트 조회 (브랜드/업종 관리자용)"""
    try:
        # 권한 확인 (브랜드 관리자 또는 업종 관리자)
        if not (current_user.is_brand_admin or current_user.is_industry_admin):
            return jsonify({'error': '권한이 없습니다'}), 403
        
        # 쿼리 파라미터
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        branch_id = request.args.get('branch_id')
        
        # 날짜 기본값 설정
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # 날짜 변환
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # 직원 목록 조회 (권한에 따라 필터링)
        query = UserInfo.query
        
        if current_user.is_brand_admin:
            # 브랜드 관리자는 해당 브랜드의 직원만 조회
            query = query.join(UserInfo.user).filter(
                User.user.brand_id == current_user.brand_id
            )
        elif current_user.is_industry_admin:
            # 업종 관리자는 해당 업종의 직원만 조회
            query = query.join(UserInfo.user).join(User.brand).filter(
                Brand.industry_id == current_user.industry_id
            )
        
        if branch_id:
            query = query.join(UserInfo.user).filter(
                User.user.branch_id == branch_id
            )
        
        employees = query.all()
        
        # 리포트 데이터 생성
        report_data = {
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_employees': len(employees),
                'active_employees': len([e for e in employees if e.status == 'active']),
                'total_work_hours': 0,
                'average_work_hours': 0,
                'attendance_rate': 0
            },
            'employees': []
        }
        
        total_hours = 0
        total_attendance = 0
        
        for employee in employees:
            # 스케줄 데이터 조회
            schedules = EmployeeSchedule.query.filter(
                EmployeeSchedule.employee_id == employee.id,
                EmployeeSchedule.date >= start_dt,
                EmployeeSchedule.date <= end_dt
            ).all()
            
            # 출퇴근 데이터 조회
            attendance_records = EmployeeAttendance.query.filter(
                EmployeeAttendance.employee_id == employee.id,
                EmployeeAttendance.date >= start_dt,
                EmployeeAttendance.date <= end_dt
            ).all()
            
            # 직원별 통계 계산
            employee_hours = sum([att.total_hours or 0 for att in attendance_records])
            attendance_count = len([att for att in attendance_records if att.status == 'present'])
            schedule_count = len(schedules)
            
            total_hours += employee_hours
            total_attendance += attendance_count
            
            employee_data = {
                'id': employee.id,
                'employee_number': employee.employee_number,
                'name': employee.user.name if employee.user else 'Unknown',
                'position': employee.position,
                'department': employee.department,
                'status': employee.status,
                'work_hours': employee_hours,
                'attendance_rate': (attendance_count / schedule_count * 100) if schedule_count > 0 else 0,
                'schedules_count': schedule_count,
                'attendance_count': attendance_count
            }
            
            report_data['employees'].append(employee_data)
        
        # 전체 통계 업데이트
        if report_data['summary']['total_employees'] > 0:
            report_data['summary']['total_work_hours'] = total_hours
            report_data['summary']['average_work_hours'] = total_hours / report_data['summary']['total_employees']
            report_data['summary']['attendance_rate'] = (total_attendance / (len(employees) * (end_dt - start_dt).days)) * 100 if (end_dt - start_dt).days > 0 else 0
        
        return jsonify({
            'success': True,
            'data': report_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@schedule_report.route('/schedule/reports/detailed', methods=['GET'])
@login_required
def get_schedule_detailed_report():
    """스케줄 상세 리포트 조회 (브랜드/업종 관리자용)"""
    try:
        # 권한 확인
        if not (current_user.is_brand_admin or current_user.is_industry_admin):
            return jsonify({'error': '권한이 없습니다'}), 403
        
        # 쿼리 파라미터
        employee_id = request.args.get('employee_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not employee_id:
            return jsonify({'error': '직원 ID가 필요합니다'}), 400
        
        # 날짜 기본값 설정
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # 날짜 변환
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # 직원 정보 조회
        employee = UserInfo.query.get_or_404(employee_id)
        
        # 권한 확인 (해당 직원에 대한 접근 권한)
        if current_user.is_brand_admin:
            if employee.user.brand_id != current_user.brand_id:
                return jsonify({'error': '권한이 없습니다'}), 403
        elif current_user.is_industry_admin:
            if employee.user.brand.industry_id != current_user.industry_id:
                return jsonify({'error': '권한이 없습니다'}), 403
        
        # 스케줄 데이터 조회
        schedules = EmployeeSchedule.query.filter(
            EmployeeSchedule.employee_id == employee_id,
            EmployeeSchedule.date >= start_dt,
            EmployeeSchedule.date <= end_dt
        ).order_by(EmployeeSchedule.date).all()
        
        # 출퇴근 데이터 조회
        attendance_records = EmployeeAttendance.query.filter(
            EmployeeAttendance.employee_id == employee_id,
            EmployeeAttendance.date >= start_dt,
            EmployeeAttendance.date <= end_dt
        ).order_by(EmployeeAttendance.date).all()
        
        # 상세 리포트 데이터 생성
        detailed_data = {
            'employee': employee.to_dict(),
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'schedules': [schedule.to_dict() for schedule in schedules],
            'attendance': [att.to_dict() for att in attendance_records],
            'summary': {
                'total_schedules': len(schedules),
                'total_attendance': len(attendance_records),
                'total_work_hours': sum([att.total_hours or 0 for att in attendance_records]),
                'attendance_rate': len([att for att in attendance_records if att.status == 'present']) / len(schedules) * 100 if schedules else 0
            }
        }
        
        return jsonify({
            'success': True,
            'data': detailed_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@schedule_report.route('/schedule/reports/export', methods=['GET'])
@login_required
def export_schedule_report():
    """스케줄 리포트 내보내기 (JSON 형식)"""
    try:
        # 권한 확인
        if not (current_user.is_brand_admin or current_user.is_industry_admin):
            return jsonify({'error': '권한이 없습니다'}), 403
        
        # 요약 리포트 데이터 가져오기
        summary_response = get_schedule_summary_report()
        summary_data = summary_response.get_json()
        
        if not summary_data.get('success'):
            return summary_response
        
        # 내보내기 데이터 구성
        export_data = {
            'export_info': {
                'exported_at': datetime.now().isoformat(),
                'exported_by': current_user.username,
                'user_role': 'brand_admin' if current_user.is_brand_admin else 'industry_admin'
            },
            'report_data': summary_data['data']
        }
        
        return jsonify({
            'success': True,
            'data': export_data,
            'message': '리포트 내보내기가 완료되었습니다'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
