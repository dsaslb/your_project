from models_main import Brand, BrandPlugin, Module
from extensions import db
from core.backend.central_data_layer import central_data  # pyright: ignore
from core.backend.integrated_module_system import integrated_system, IntegrationEvent, IntegrationEventData  # pyright: ignore
import json
from datetime import datetime, timedelta
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, render_template
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
통합 연동 모듈 API
모든 모듈이 중앙 데이터를 공유하고 실시간으로 연동되는 API
"""


from utils.auth_utils import admin_required, permission_required  # noqa  # pyright: ignore

# Blueprint 생성
integrated_api_bp = Blueprint('integrated_api', __name__, url_prefix='/api/integrated')
integrated_module_api = Blueprint('integrated_module_api', __name__)


@integrated_api_bp.route('/dashboard')
@login_required
def get_integrated_dashboard():
    """통합 대시보드 데이터"""
    try:
        user_id = current_user.id
        dashboard_data = integrated_system.get_management_dashboard(user_id)

        return jsonify({
            "success": True,
            "data": dashboard_data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500  # noqa  # pyright: ignore


@integrated_api_bp.route('/data/<int:branch_id>')
@login_required
def get_integrated_data(branch_id):
    """통합 데이터 조회"""
    try:
        data_types = request.args.get('types', '').split(',')
        if data_types == ['']:
            data_types = []

        integrated_data = integrated_system.get_integrated_data(branch_id,  data_types)  # noqa  # pyright: ignore

        return jsonify({
            "success": True,
            "data": integrated_data,
            "branch_id": branch_id
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@integrated_api_bp.route('/efficiency/<int:branch_id>')
@login_required
def get_efficiency_analysis(branch_id):
    """효율성 분석 조회"""
    try:
        period = request.args.get('period', 'month')
        efficiency_data = integrated_system.get_efficiency_analysis(branch_id,  period)

        return jsonify({
            "success": True,
            "data": efficiency_data,
            "branch_id": branch_id,
            "period": period
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@integrated_api_bp.route('/attendance/record', methods=['POST'])
@login_required
def record_attendance():
    """출퇴근 기록 (통합 연동)"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id', current_user.id) if data else current_user.id
        branch_id = data.get('branch_id', 1) if data else 1
        action = data.get('action') if data else None  # 'clock_in' or 'clock_out'

        # 중앙 데이터에 출퇴근 기록
        with central_data.lock:
            with central_data.db_path.parent / "central_data.db" as conn:
                cursor = conn.cursor()

                today = datetime.now().strftime('%Y-%m-%d')
                current_time = datetime.now()

                if action == 'clock_in':
                    # 출근 기록
                    cursor.execute("""
                        INSERT INTO attendance (employee_id, branch_id, date, clock_in, status)
                        VALUES (?, ?, ?, ?, ?)
                    """, (employee_id, branch_id, today, current_time, 'checked_in'))

                    # 지각 여부 확인
                    is_late = current_time.time() > datetime.min.time().replace(hour=9, minute=0)

                    attendance_data = {
                        'employee_id': employee_id,
                        'branch_id': branch_id,
                        'date': today,
                        'clock_in': current_time.isoformat(),
                        'is_late': is_late,
                        'status': 'checked_in'
                    }

                elif action == 'clock_out':
                    # 퇴근 기록
                    cursor.execute("""
                        UPDATE attendance 
                        SET clock_out = ?, status = 'completed'
                        WHERE employee_id = ? AND date = ? AND clock_out IS NULL
                    """, (current_time, employee_id, today))

                    # 근무 시간 계산
                    cursor.execute("""
                        SELECT clock_in, clock_out FROM attendance
                        WHERE employee_id = ? AND date = ?
                    """, (employee_id, today))

                    result = cursor.fetchone()
                    if result:
                        clock_in = datetime.fromisoformat(result[0] if result is not None else None)
                        work_hours = (current_time - clock_in).total_seconds() / 3600
                        is_overtime = work_hours > 8

                        cursor.execute("""
                            UPDATE attendance 
                            SET work_hours = ?, is_overtime = ?
                            WHERE employee_id = ? AND date = ?
                        """, (work_hours, is_overtime, employee_id, today))

                        attendance_data = {
                            'employee_id': employee_id,
                            'branch_id': branch_id,
                            'date': today,
                            'clock_in': result[0] if result is not None else None,
                            'clock_out': current_time.isoformat(),
                            'work_hours': work_hours,
                            'is_overtime': is_overtime,
                            'status': 'completed'
                        }
                    else:
                        return jsonify({"success": False, "error": "출근 기록을 찾을 수 없습니다."}), 400

                conn.commit()

                # 통합 이벤트 발생
                integrated_system.emit_event(IntegrationEventData(
                    event_type=IntegrationEvent.ATTENDANCE_RECORDED,
                    module_id="attendance_management",
                    data=attendance_data,
                    timestamp=current_time,
                    user_id=employee_id,
                    branch_id=branch_id
                ))

                return jsonify({
                    "success": True,
                    "message": f"{'출근' if action == 'clock_in' else '퇴근'}이 기록되었습니다.",
                    "data": attendance_data
                })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@integrated_api_bp.route('/sales/record', methods=['POST'])
@login_required
def record_sales():
    """매출 기록 (통합 연동)"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id', current_user.id) if data else current_user.id
        branch_id = data.get('branch_id', 1) if data else 1
        amount = data.get('amount') if data else None
        category = data.get('category', '일반') if data else '일반'

        if not amount:
            return jsonify({"success": False, "error": "매출 금액이 필요합니다."}), 400

        # 중앙 데이터에 매출 기록
        with central_data.lock:
            with central_data.db_path.parent / "central_data.db" as conn:
                cursor = conn.cursor()

                today = datetime.now().strftime('%Y-%m-%d')
                current_time = datetime.now()

                cursor.execute("""
                    INSERT INTO sales (branch_id, employee_id, date, amount, category, payment_method, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (branch_id, employee_id, today, amount, category, 'card', 'completed'))

                conn.commit()

                sales_data = {
                    'branch_id': branch_id,
                    'employee_id': employee_id,
                    'date': today,
                    'amount': amount,
                    'category': category,
                    'created_at': current_time.isoformat()
                }

                # 통합 이벤트 발생
                integrated_system.emit_event(IntegrationEventData(
                    event_type=IntegrationEvent.SALES_RECORDED,
                    module_id="sales_management",
                    data=sales_data,
                    timestamp=current_time,
                    user_id=employee_id,
                    branch_id=branch_id
                ))

                return jsonify({
                    "success": True,
                    "message": "매출이 기록되었습니다.",
                    "data": sales_data
                })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@integrated_api_bp.route('/payroll/calculate', methods=['POST'])
@login_required
@admin_required
def calculate_payroll():
    """급여 계산 (통합 연동)"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id') if data else None
        branch_id = data.get('branch_id', 1) if data else 1
        year = data.get('year', datetime.now().year) if data else datetime.now().year
        month = data.get('month', datetime.now().month) if data else datetime.now().month

        if not employee_id:
            return jsonify({"success": False, "error": "직원 ID가 필요합니다."}), 400

        # 출퇴근 데이터 조회
        attendance_data = central_data.get_attendance_data(
            employee_id=employee_id,
            branch_id=branch_id,
            date_from=f"{year}-{month:02d}-01",
            date_to=f"{year}-{month:02d}-31"
        )

        # 직원 정보 조회
        employees = central_data.get_employees(employee_id=employee_id)
        if not employees:
            return jsonify({"success": False, "error": "직원을 찾을 수 없습니다."}), 400

        employee = employees[0] if employees is not None else None
        base_salary = employee.get('monthly_salary', 2500000) if employee else 2500000

        # 근무 시간 계산
        total_work_hours = sum(att.get('work_hours', 0) for att in attendance_data)
        attendance_days = len(attendance_data)

        # 초과근무 수당 계산
        standard_hours = 160  # 월 160시간 기준
        overtime_hours = max(0, total_work_hours - standard_hours)
        overtime_pay = overtime_hours * 15000  # 시간당 15,000원

        # 성과 보너스 (매출 기반)
        sales_data = central_data.get_sales_data(
            employee_id=employee_id,
            branch_id=branch_id,
            date_from=f"{year}-{month:02d}-01",
            date_to=f"{year}-{month:02d}-31"
        )

        total_sales = sum(sale.get('amount', 0) for sale in sales_data)
        bonus = total_sales * 0.05  # 매출의 5% 보너스

        # 공제
        deduction = base_salary * 0.1  # 기본급의 10% 공제

        # 실수령액 계산
        net_salary = base_salary + overtime_pay + bonus - deduction

        # 중앙 데이터에 급여 기록
        with central_data.lock:
            with central_data.db_path.parent / "central_data.db" as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT OR REPLACE INTO payroll 
                    (employee_id, branch_id, year, month, base_salary, overtime_pay, bonus, deduction, net_salary, work_hours, attendance_days)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (employee_id, branch_id, year, month, base_salary, overtime_pay, bonus, deduction, net_salary, total_work_hours, attendance_days))

                conn.commit()

                payroll_data = {
                    'employee_id': employee_id,
                    'branch_id': branch_id,
                    'year': year,
                    'month': month,
                    'base_salary': base_salary,
                    'overtime_pay': overtime_pay,
                    'bonus': bonus,
                    'deduction': deduction,
                    'net_salary': net_salary,
                    'work_hours': total_work_hours,
                    'attendance_days': attendance_days
                }

                # 통합 이벤트 발생
                integrated_system.emit_event(IntegrationEventData(
                    event_type=IntegrationEvent.PAYROLL_CALCULATED,
                    module_id="payroll_management",
                    data=payroll_data,
                    timestamp=datetime.now(),
                    user_id=employee_id,
                    branch_id=branch_id
                ))

                return jsonify({
                    "success": True,
                    "message": "급여가 계산되었습니다.",
                    "data": payroll_data
                })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@integrated_api_bp.route('/analytics/generate', methods=['POST'])
@login_required
@admin_required
def generate_analytics():
    """통합 분석 생성"""
    try:
        data = request.get_json()
        branch_id = data.get('branch_id', 1) if data else 1
        period = data.get('period', 'month') if data else 'month'

        # 통합 분석 실행
        analytics_result = integrated_system.get_efficiency_analysis(branch_id,  period)

        # 분석 결과 저장
        central_data.save_analytics_result(
            branch_id=branch_id,
            analysis_type="integrated",
            period=period,
            data=analytics_result,
            insights=analytics_result.get('insights', []) if analytics_result else [],
            recommendations=analytics_result.get('recommendations', []) if analytics_result else []
        )

        # 분석 완료 이벤트 발생
        integrated_system.emit_event(IntegrationEventData(
            event_type=IntegrationEvent.ANALYTICS_GENERATED,
            module_id="analytics_module",
            data={"branch_id": branch_id, "analytics": analytics_result},
            timestamp=datetime.now(),
            branch_id=branch_id
        ))

        return jsonify({
            "success": True,
            "message": "통합 분석이 생성되었습니다.",
            "data": analytics_result
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@integrated_api_bp.route('/notifications')
@login_required
def get_notifications():
    """알림 목록 조회"""
    try:
        user_id = current_user.id
        is_read = request.args.get('is_read') if args else None
        if is_read is not None:
            is_read = is_read.lower() if is_read is not None else '' == 'true'

        notifications = central_data.get_notifications(user_id=user_id,  is_read=is_read)

        return jsonify({
            "success": True,
            "data": notifications
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@integrated_api_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """알림 읽음 처리"""
    try:
        with central_data.lock:
            with central_data.db_path.parent / "central_data.db" as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE notifications 
                    SET is_read = TRUE 
                    WHERE id = ? AND user_id = ?
                """, (notification_id, current_user.id))
                conn.commit()

        return jsonify({
            "success": True,
            "message": "알림이 읽음 처리되었습니다."
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@integrated_api_bp.route('/realtime/stream')
@login_required
def realtime_stream():
    """실시간 데이터 스트림"""
    try:
        branch_id = request.args.get('branch_id', 1, type=int) if args else 1

        # 실시간 데이터 조회
        realtime_data = {
            "timestamp": datetime.now().isoformat(),
            "branch_id": branch_id,
            "attendance": {
                "current_employees": len(central_data.get_attendance_data(branch_id=branch_id)),
                "late_count": sum(1 for att in central_data.get_attendance_data(branch_id=branch_id) if att.get('is_late'))
            },
            "sales": {
                "today_sales": sum(sale.get('amount', 0) for sale in central_data.get_sales_data(branch_id=branch_id)),
                "sales_count": len(central_data.get_sales_data(branch_id=branch_id))
            },
            "notifications": {
                "unread_count": len(central_data.get_notifications(user_id=current_user.id, is_read=False))
            }
        }

        return jsonify({
            "success": True,
            "data": realtime_data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@integrated_api_bp.route('/demo/integrated-scenario')
@login_required
def demo_integrated_scenario():
    """통합 시나리오 데모"""
    try:
        # 시나리오: 출퇴근 → 매출 → 급여/효율 분석 → 개선 사항 리포트 → 관리자 알림

        # 1. 출퇴근 기록
        attendance_event = IntegrationEventData(
            event_type=IntegrationEvent.ATTENDANCE_RECORDED,
            module_id="attendance_management",
            data={
                'employee_id': 1,
                'branch_id': 1,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'clock_in': datetime.now().isoformat(),
                'work_hours': 8.5,
                'is_late': False,
                'is_overtime': True,
                'status': 'completed'
            },
            timestamp=datetime.now(),
            user_id=1,
            branch_id=1
        )
        integrated_system.emit_event(attendance_event)

        # 2. 매출 기록
        sales_event = IntegrationEventData(
            event_type=IntegrationEvent.SALES_RECORDED,
            module_id="sales_management",
            data={
                'branch_id': 1,
                'employee_id': 1,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'amount': 150000,
                'category': '음료',
                'created_at': datetime.now().isoformat()
            },
            timestamp=datetime.now(),
            user_id=1,
            branch_id=1
        )
        integrated_system.emit_event(sales_event)

        # 3. 급여 계산
        payroll_event = IntegrationEventData(
            event_type=IntegrationEvent.PAYROLL_CALCULATED,
            module_id="payroll_management",
            data={
                'employee_id': 1,
                'branch_id': 1,
                'year': datetime.now().year,
                'month': datetime.now().month,
                'base_salary': 3000000,
                'overtime_pay': 75000,
                'bonus': 7500,
                'deduction': 300000,
                'net_salary': 2782500,
                'work_hours': 170,
                'attendance_days': 22
            },
            timestamp=datetime.now(),
            user_id=1,
            branch_id=1
        )
        integrated_system.emit_event(payroll_event)

        # 4. 통합 분석 생성
        analytics_result = integrated_system.get_efficiency_analysis(1,  "month")

        analytics_event = IntegrationEventData(
            event_type=IntegrationEvent.ANALYTICS_GENERATED,
            module_id="analytics_module",
            data={
                'branch_id': 1,
                'analytics': analytics_result
            },
            timestamp=datetime.now(),
            branch_id=1
        )
        integrated_system.emit_event(analytics_event)

        # 5. 관리자 알림 생성
        central_data.create_notification(
            user_id=1,
            title="통합 시나리오 데모 완료",
            message="출퇴근 → 매출 → 급여 → 분석 → 알림 시나리오가 성공적으로 실행되었습니다.",
            notification_type="info",
            priority="normal"
        )

        return jsonify({
            "success": True,
            "message": "통합 시나리오 데모가 실행되었습니다.",
            "scenario": [
                "1. 출퇴근 기록 → 매장/직원 정보 자동 조회",
                "2. 매출 기록 → 출퇴근 데이터와 연동하여 효율성 분석",
                "3. 급여 계산 → 매출 대비 인건비 비율 자동 계산",
                "4. 통합 분석 → 개선 사항 자동 생성",
                "5. 관리자 알림 → 실시간 보고서 전달"
            ],
            "data": {
                "attendance_recorded": True,
                "sales_recorded": True,
                "payroll_calculated": True,
                "analytics_generated": True,
                "notification_sent": True
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@integrated_api_bp.route('/status')
@login_required
def get_system_status():
    """시스템 상태 조회"""
    try:
        status = {
            "system_running": integrated_system.running,
            "modules_registered": len(integrated_system.module_registry),
            "event_handlers": len(integrated_system.event_handlers),
            "analysis_cache_size": len(integrated_system.analysis_cache),
            "last_updated": datetime.now().isoformat()
        }

        return jsonify({
            "success": True,
            "data": status
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@integrated_module_api.route('/api/modules/<module_id>/brands', methods=['GET'])
@login_required
def get_module_applied_brands(module_id):
    """
    특정 모듈이 적용된 브랜드 목록 조회
    """
    try:
        # 해당 모듈이 적용된 브랜드 목록 조회
        brand_plugins = BrandPlugin.query.filter_by(code=module_id).all()
        brands = [Brand.query.get(bp.brand_id) for bp in brand_plugins if bp.brand_id]
        brand_list = [
            {"id": b.id, "name": b.name, "code": b.code}
            for b in brands if b is not None
        ]
        return jsonify({"success": True, "brands": brand_list})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@integrated_module_api.route('/api/modules/<module_id>/brands', methods=['POST'])
@login_required
def apply_module_to_brand(module_id):
    """
    브랜드에 모듈(플러그인) 적용/해제
    body: {brand_code, apply}
    """
    data = request.get_json()
    brand_code = data.get('brand_code') if data else None
    apply = data.get('apply', True) if data else True
    if not brand_code:
        return jsonify({"success": False, "error": "brand_code가 필요합니다."}), 400
    try:
        brand = Brand.query.filter_by(code=brand_code).first()
        if not brand:
            return jsonify({"success": False, "error": "해당 브랜드를 찾을 수 없습니다."}), 404
        # 권한 체크(브랜드 관리자 이상만)
        if not (current_user.is_admin() or current_user.role in ["admin", "brand_admin", "super_admin"] or getattr(current_user, 'brand_id', None) == brand.id):
            return jsonify({"success": False, "error": "권한이 없습니다."}), 403
        if apply:
            # 이미 적용되어 있으면 무시
            exists = BrandPlugin.query.filter_by(brand_id=brand.id, code=module_id).first()
            if exists:
                pass
            else:
                # 모듈 정보 확인
                module = Module.query.filter_by(id=module_id).first()
                if not module:
                    return jsonify({"success": False, "error": "해당 모듈을 찾을 수 없습니다."}), 404
                new_bp = BrandPlugin(brand_id=brand.id, name=module.name, code=module_id,
                                     description=module.description, version=module.version, is_active=True)
                db.session.add(new_bp)
                db.session.commit()
        else:
            # 적용 해제(삭제)
            bp = BrandPlugin.query.filter_by(brand_id=brand.id, code=module_id).first()
            if bp:
                db.session.delete(bp)
                db.session.commit()
        # 적용된 브랜드 목록 반환
        brand_plugins = BrandPlugin.query.filter_by(code=module_id).all()
        applied_brands = [bp.brand_id for bp in brand_plugins if bp.brand_id]
        return jsonify({"success": True, "applied_brands": applied_brands})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})
