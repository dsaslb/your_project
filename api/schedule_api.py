"""
직원 마스터 데이터 API (새로운 아키텍처)
운영 데이터(스케줄, 출퇴근 기록)는 프론트엔드에서만 관리
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models_main import User, Staff, Branch, Brand, db
from utils.role_required import role_required
from utils.logger import logger
from datetime import datetime, date, time
from sqlalchemy import and_, or_

schedule_api = Blueprint('schedule_api', __name__)

@schedule_api.route('/api/employees/master', methods=['GET'])
@login_required
@role_required(['admin', 'super_admin', 'brand_manager', 'store_manager'])
def get_employee_master_data():
    """직원 마스터 데이터 조회 (계정, 이름, 연락처, 직책 등 기본 정보만)"""
    try:
        # 검색 파라미터
        search = request.args.get('search', '')
        department = request.args.get('department', '')
        status = request.args.get('status', '')
        branch_id = request.args.get('branch_id', '')
        brand_id = request.args.get('brand_id', '')
        
        # 기본 쿼리 - 직원 역할만 필터링
        query = db.session.query(
            User.id,
            User.username,
            User.email,
            User.phone,
            User.role,
            User.status,
            User.created_at,
            Staff.name.label('employee_name'),
            Staff.department,
            Staff.position,
            Staff.hire_date,
            Branch.name.label('store_name'),
            Branch.id.label('store_id'),
            Brand.name.label('brand_name'),
            Brand.id.label('brand_id')
        ).join(
            Staff, User.id == Staff.user_id
        ).join(
            Branch, User.branch_id == Branch.id
        ).join(
            Brand, Branch.brand_id == Brand.id
        ).filter(
            User.role.in_(['employee', 'manager', 'store_manager'])
        )
        
        # 권한에 따른 필터링
        if current_user.role == 'store_manager':
            # 매장 관리자는 자신의 매장 직원만 조회
            query = query.filter(User.branch_id == current_user.branch_id)
        elif current_user.role == 'brand_manager':
            # 브랜드 관리자는 자신의 브랜드 직원만 조회
            query = query.filter(Branch.brand_id == current_user.brand_id)
        
        # 검색 필터
        if search:
            query = query.filter(
                or_(
                    Staff.name.contains(search),
                    User.email.contains(search),
                    User.phone.contains(search),
                    Staff.position.contains(search)
                )
            )
        
        # 부서 필터
        if department:
            query = query.filter(Staff.department == department)
        
        # 상태 필터
        if status:
            query = query.filter(User.status == status)
        
        # 매장 필터
        if branch_id:
            query = query.filter(User.branch_id == int(branch_id))
        
        # 브랜드 필터
        if brand_id:
            query = query.filter(Branch.brand_id == int(brand_id))
        
        # 정렬
        query = query.order_by(Staff.name)
        
        # 결과 조회
        employees = query.all()
        
        # 응답 데이터 구성
        employee_list = []
        for emp in employees:
            employee_list.append({
                'id': emp.id,
                'username': emp.username,
                'email': emp.email,
                'phone': emp.phone,
                'role': emp.role,
                'status': emp.status,
                'name': emp.employee_name,
                'department': emp.department,
                'position': emp.position,
                'hire_date': emp.hire_date.isoformat() if emp.hire_date else None,
                'store_name': emp.store_name,
                'store_id': emp.store_id,
                'brand_name': emp.brand_name,
                'brand_id': emp.brand_id,
                'created_at': emp.created_at.isoformat() if emp.created_at else None
            })
        
        return jsonify({
            'success': True,
            'message': '직원 마스터 데이터 조회 성공',
            'employees': employee_list,
            'total': len(employee_list)
        })
        
    except Exception as e:
        logger.error(f"직원 마스터 데이터 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': '직원 마스터 데이터 조회 실패',
            'error': str(e)
        }), 500

@schedule_api.route('/api/stores/master', methods=['GET'])
@login_required
@role_required(['admin', 'super_admin', 'brand_manager', 'store_manager'])
def get_store_master_data():
    """매장 마스터 데이터 조회"""
    try:
        # 검색 파라미터
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        brand_id = request.args.get('brand_id', '')
        
        # 기본 쿼리
        query = db.session.query(
            Branch.id,
            Branch.name,
            Branch.code,
            Branch.address,
            Branch.phone,
            Branch.status,
            Branch.created_at,
            Brand.name.label('brand_name'),
            Brand.id.label('brand_id')
        ).join(
            Brand, Branch.brand_id == Brand.id
        )
        
        # 권한에 따른 필터링
        if current_user.role == 'store_manager':
            # 매장 관리자는 자신의 매장만 조회
            query = query.filter(Branch.id == current_user.branch_id)
        elif current_user.role == 'brand_manager':
            # 브랜드 관리자는 자신의 브랜드 매장만 조회
            query = query.filter(Branch.brand_id == current_user.brand_id)
        
        # 검색 필터
        if search:
            query = query.filter(
                or_(
                    Branch.name.contains(search),
                    Branch.code.contains(search),
                    Branch.address.contains(search)
                )
            )
        
        # 상태 필터
        if status:
            query = query.filter(Branch.status == status)
        
        # 브랜드 필터
        if brand_id:
            query = query.filter(Branch.brand_id == int(brand_id))
        
        # 정렬
        query = query.order_by(Branch.name)
        
        # 결과 조회
        stores = query.all()
        
        # 응답 데이터 구성
        store_list = []
        for store in stores:
            store_list.append({
                'id': store.id,
                'name': store.name,
                'code': store.code,
                'address': store.address,
                'phone': store.phone,
                'status': store.status,
                'brand_name': store.brand_name,
                'brand_id': store.brand_id,
                'created_at': store.created_at.isoformat() if store.created_at else None
            })
        
        return jsonify({
            'success': True,
            'message': '매장 마스터 데이터 조회 성공',
            'stores': store_list,
            'total': len(store_list)
        })
        
    except Exception as e:
        logger.error(f"매장 마스터 데이터 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': '매장 마스터 데이터 조회 실패',
            'error': str(e)
        }), 500

@schedule_api.route('/api/ai-reports/summary', methods=['POST'])
@login_required
@role_required(['admin', 'super_admin', 'brand_manager', 'store_manager'])
def submit_ai_report_summary():
    """매장에서 생성된 AI 리포트 요약을 상위 관리자에게 제출"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['store_id', 'report_date', 'summary_data']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'필수 필드 누락: {field}'
                }), 400
        
        # 권한 검증
        if current_user.role == 'store_manager':
            if data['store_id'] != current_user.branch_id:
                return jsonify({
                    'success': False,
                    'message': '자신의 매장 리포트만 제출 가능합니다'
                }), 403
        elif current_user.role == 'brand_manager':
            # 브랜드 관리자는 자신의 브랜드 매장 리포트만 확인 가능
            store = Branch.query.get(data['store_id'])
            if not store or store.brand_id != current_user.brand_id:
                return jsonify({
                    'success': False,
                    'message': '권한이 없습니다'
                }), 403
        
        # 여기서는 실제로 데이터베이스에 저장하지 않고, 
        # 요약 리포트만 로깅하고 성공 응답을 반환
        logger.info(f"AI 리포트 요약 제출: 매장 {data['store_id']}, 날짜 {data['report_date']}")
        
        return jsonify({
            'success': True,
            'message': 'AI 리포트 요약 제출 성공',
            'report_id': f"report_{data['store_id']}_{data['report_date']}"
        })
        
    except Exception as e:
        logger.error(f"AI 리포트 요약 제출 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'AI 리포트 요약 제출 실패',
            'error': str(e)
        }), 500

@schedule_api.route('/api/ai-reports/brand-summary', methods=['GET'])
@login_required
@role_required(['admin', 'super_admin', 'brand_manager'])
def get_brand_ai_reports():
    """브랜드별 AI 리포트 요약 조회"""
    try:
        brand_id = request.args.get('brand_id')
        
        if not brand_id:
            return jsonify({
                'success': False,
                'message': '브랜드 ID가 필요합니다'
            }), 400
        
        # 권한 검증
        if current_user.role == 'brand_manager' and int(brand_id) != current_user.brand_id:
            return jsonify({
                'success': False,
                'message': '자신의 브랜드 리포트만 조회 가능합니다'
            }), 403
        
        # 실제로는 데이터베이스에서 브랜드별 요약 리포트를 조회
        # 현재는 샘플 데이터 반환
        sample_reports = [
            {
                'store_id': 1,
                'store_name': '강남점',
                'report_date': '2024-01-15',
                'issues': ['월요일 오후 인원 과다', '화요일 저녁 인원 부족'],
                'improvements': ['월요일 오후 인원 20% 감축', '화요일 저녁 인원 2명 추가'],
                'efficiency_score': 75
            },
            {
                'store_id': 2,
                'store_name': '홍대점',
                'report_date': '2024-01-15',
                'issues': ['주말 인원 부족'],
                'improvements': ['주말 인원 3명 추가'],
                'efficiency_score': 85
            }
        ]
        
        return jsonify({
            'success': True,
            'message': '브랜드 AI 리포트 요약 조회 성공',
            'reports': sample_reports,
            'brand_id': brand_id
        })
        
    except Exception as e:
        logger.error(f"브랜드 AI 리포트 요약 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': '브랜드 AI 리포트 요약 조회 실패',
            'error': str(e)
        }), 500

@schedule_api.route('/api/ai-reports/industry-summary', methods=['GET'])
@login_required
@role_required(['admin', 'super_admin'])
def get_industry_ai_reports():
    """업종별 AI 리포트 요약 조회"""
    try:
        industry_id = request.args.get('industry_id')
        
        if not industry_id:
            return jsonify({
                'success': False,
                'message': '업종 ID가 필요합니다'
            }), 400
        
        # 실제로는 데이터베이스에서 업종별 요약 리포트를 조회
        # 현재는 샘플 데이터 반환
        sample_reports = [
            {
                'brand_id': 1,
                'brand_name': '스타벅스',
                'total_stores': 15,
                'avg_efficiency_score': 78,
                'common_issues': ['주말 인원 부족', '평일 오후 인원 과다'],
                'recommendations': ['주말 인원 배치 최적화', '평일 오후 인원 조정']
            },
            {
                'brand_id': 2,
                'brand_name': '투썸플레이스',
                'total_stores': 8,
                'avg_efficiency_score': 82,
                'common_issues': ['저녁 시간대 인원 부족'],
                'recommendations': ['저녁 시간대 인원 증가']
            }
        ]
        
        return jsonify({
            'success': True,
            'message': '업종 AI 리포트 요약 조회 성공',
            'reports': sample_reports,
            'industry_id': industry_id
        })
        
    except Exception as e:
        logger.error(f"업종 AI 리포트 요약 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': '업종 AI 리포트 요약 조회 실패',
            'error': str(e)
        }), 500
