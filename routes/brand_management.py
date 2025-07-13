"""
브랜드별 관리 시스템
브랜드별 현황 및 개선 사항 관리
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models import User, Brand, Branch, Staff, SystemLog, AIDiagnosis, ImprovementRequest
from extensions import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

brand_management_bp = Blueprint('brand_management', __name__, url_prefix='/admin/brand-management')

@brand_management_bp.route('/', methods=['GET'])
@login_required
def brand_management_page():
    """브랜드별 관리 페이지"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    return render_template('admin/brand_management.html')

@brand_management_bp.route('/api/brands', methods=['GET'])
@login_required
def get_brands():
    """브랜드 목록 조회"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        brands = Brand.query.all()
        brand_list = []
        
        for brand in brands:
            # 브랜드 관리자 정보
            admin = User.query.get(brand.admin_id) if brand.admin_id else None
            
            # 매장 수
            branch_count = Branch.query.filter_by(brand_id=brand.id).count()
            
            # 직원 수
            staff_count = Staff.query.join(Branch).filter(Branch.brand_id == brand.id).count()
            
            # 최근 AI 진단 수
            recent_diagnoses = AIDiagnosis.query.filter_by(brand_id=brand.id).count()
            
            # 개선 요청 수
            improvement_requests = ImprovementRequest.query.filter_by(brand_id=brand.id).count()
            
            brand_list.append({
                'brand_id': brand.id,
                'brand_name': brand.name,
                'brand_code': brand.code,
                'admin_name': admin.name if admin else '미지정',
                'admin_email': admin.email if admin else '미지정',
                'status': brand.status,
                'branch_count': branch_count,
                'staff_count': staff_count,
                'recent_diagnoses': recent_diagnoses,
                'improvement_requests': improvement_requests,
                'created_at': brand.created_at.isoformat(),
                'updated_at': brand.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'brands': brand_list,
            'total_count': len(brand_list)
        })
        
    except Exception as e:
        logger.error(f"브랜드 목록 조회 오류: {str(e)}")
        return jsonify({'error': '데이터 조회 중 오류가 발생했습니다.'}), 500

@brand_management_bp.route('/api/brand/<int:brand_id>/details', methods=['GET'])
@login_required
def get_brand_details(brand_id):
    """브랜드 상세 정보 조회"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        brand = Brand.query.get(brand_id)
        if not brand:
            return jsonify({'error': '브랜드를 찾을 수 없습니다.'}), 404
        
        # 브랜드 관리자 정보
        admin = User.query.get(brand.admin_id) if brand.admin_id else None
        
        # 매장 목록
        branches = Branch.query.filter_by(brand_id=brand.id).all()
        branch_list = []
        
        for branch in branches:
            # 매장별 직원 수
            staff_count = Staff.query.filter_by(branch_id=branch.id).count()
            
            branch_list.append({
                'branch_id': branch.id,
                'branch_name': branch.name,
                'store_code': branch.store_code,
                'address': branch.address,
                'phone': branch.phone,
                'status': branch.status,
                'staff_count': staff_count,
                'created_at': branch.created_at.isoformat()
            })
        
        # AI 진단 목록
        diagnoses = AIDiagnosis.query.filter_by(brand_id=brand.id).order_by(AIDiagnosis.created_at.desc()).limit(10).all()
        diagnosis_list = []
        
        for diagnosis in diagnoses:
            diagnosis_list.append({
                'diagnosis_id': diagnosis.id,
                'title': diagnosis.title,
                'diagnosis_type': diagnosis.diagnosis_type,
                'severity': diagnosis.severity,
                'status': diagnosis.status,
                'priority': diagnosis.priority,
                'created_at': diagnosis.created_at.isoformat()
            })
        
        # 개선 요청 목록
        improvements = ImprovementRequest.query.filter_by(brand_id=brand.id).order_by(ImprovementRequest.created_at.desc()).limit(10).all()
        improvement_list = []
        
        for improvement in improvements:
            improvement_list.append({
                'request_id': improvement.id,
                'title': improvement.title,
                'category': improvement.category,
                'priority': improvement.priority,
                'status': improvement.status,
                'created_at': improvement.created_at.isoformat()
            })
        
        # 통계 정보
        stats = {
            'total_branches': len(branches),
            'total_staff': sum([b['staff_count'] for b in branch_list]),
            'active_branches': len([b for b in branch_list if b['status'] == 'active']),
            'pending_diagnoses': len([d for d in diagnosis_list if d['status'] == 'pending']),
            'pending_improvements': len([i for i in improvement_list if i['status'] == 'pending'])
        }
        
        return jsonify({
            'success': True,
            'brand': {
                'brand_id': brand.id,
                'brand_name': brand.name,
                'brand_code': brand.code,
                'description': brand.description,
                'admin_name': admin.name if admin else '미지정',
                'admin_email': admin.email if admin else '미지정',
                'status': brand.status,
                'created_at': brand.created_at.isoformat()
            },
            'branches': branch_list,
            'diagnoses': diagnosis_list,
            'improvements': improvement_list,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"브랜드 상세 정보 조회 오류: {str(e)}")
        return jsonify({'error': '데이터 조회 중 오류가 발생했습니다.'}), 500

@brand_management_bp.route('/api/brand/<int:brand_id>/update', methods=['PUT'])
@login_required
def update_brand(brand_id):
    """브랜드 정보 업데이트"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        data = request.get_json()
        brand = Brand.query.get(brand_id)
        
        if not brand:
            return jsonify({'error': '브랜드를 찾을 수 없습니다.'}), 404
        
        # 업데이트 가능한 필드들
        if 'name' in data:
            brand.name = data['name']
        if 'description' in data:
            brand.description = data['description']
        if 'status' in data:
            brand.status = data['status']
        if 'admin_id' in data:
            brand.admin_id = data['admin_id']
        
        brand.updated_at = datetime.utcnow()
        
        # 시스템 로그 기록
        log = SystemLog(
            user=current_user,  # pyright: ignore
            action='brand_update',  # pyright: ignore
            detail=f'브랜드 정보 업데이트: {brand.name}',  # pyright: ignore
            ip=request.remote_addr  # pyright: ignore
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{brand.name} 브랜드 정보가 업데이트되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"브랜드 업데이트 오류: {str(e)}")
        return jsonify({'error': '브랜드 업데이트 중 오류가 발생했습니다.'}), 500

@brand_management_bp.route('/api/brand/<int:brand_id>/analytics', methods=['GET'])
@login_required
def get_brand_analytics(brand_id):
    """브랜드 분석 데이터"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        # 최근 30일 데이터
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=30)
        
        # AI 진단 통계
        diagnoses = AIDiagnosis.query.filter(
            AIDiagnosis.brand_id == brand_id,
            AIDiagnosis.created_at >= start_date
        ).all()
        
        diagnosis_stats = {
            'total': len(diagnoses),
            'by_severity': {
                'low': len([d for d in diagnoses if d.severity == 'low']),
                'medium': len([d for d in diagnoses if d.severity == 'medium']),
                'high': len([d for d in diagnoses if d.severity == 'high']),
                'critical': len([d for d in diagnoses if d.severity == 'critical'])
            },
            'by_status': {
                'pending': len([d for d in diagnoses if d.status == 'pending']),
                'reviewed': len([d for d in diagnoses if d.status == 'reviewed']),
                'implemented': len([d for d in diagnoses if d.status == 'implemented']),
                'resolved': len([d for d in diagnoses if d.status == 'resolved'])
            }
        }
        
        # 개선 요청 통계
        improvements = ImprovementRequest.query.filter(
            ImprovementRequest.brand_id == brand_id,
            ImprovementRequest.created_at >= start_date
        ).all()
        
        improvement_stats = {
            'total': len(improvements),
            'by_category': {
                'system': len([i for i in improvements if i.category == 'system']),
                'process': len([i for i in improvements if i.category == 'process']),
                'equipment': len([i for i in improvements if i.category == 'equipment']),
                'training': len([i for i in improvements if i.category == 'training']),
                'other': len([i for i in improvements if i.category == 'other'])
            },
            'by_status': {
                'pending': len([i for i in improvements if i.status == 'pending']),
                'under_review': len([i for i in improvements if i.status == 'under_review']),
                'approved': len([i for i in improvements if i.status == 'approved']),
                'rejected': len([i for i in improvements if i.status == 'rejected']),
                'implemented': len([i for i in improvements if i.status == 'implemented'])
            }
        }
        
        # 매장별 직원 분포
        branches = Branch.query.filter_by(brand_id=brand_id).all()
        branch_staff_distribution = []
        
        for branch in branches:
            staff_count = Staff.query.filter_by(branch_id=branch.id).count()
            branch_staff_distribution.append({
                'branch_name': branch.name,
                'staff_count': staff_count
            })
        
        return jsonify({
            'success': True,
            'analytics': {
                'diagnosis_stats': diagnosis_stats,
                'improvement_stats': improvement_stats,
                'branch_staff_distribution': branch_staff_distribution,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }
        })
        
    except Exception as e:
        logger.error(f"브랜드 분석 데이터 조회 오류: {str(e)}")
        return jsonify({'error': '분석 데이터 조회 중 오류가 발생했습니다.'}), 500 