from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models_main import Brand, Branch, Staff, ImprovementRequest, Order
from extensions import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

admin_brand_api = Blueprint('admin_brand_api', __name__, url_prefix='/api/admin/brand')

@admin_brand_api.route('/<int:brand_id>/sales', methods=['GET'])
@login_required
def get_brand_sales(brand_id):
    """브랜드별 매출 데이터 조회"""
    try:
        # 권한 확인
        if not current_user.is_admin():
            return jsonify({'error': '권한이 없습니다.'}), 403

        # 브랜드 존재 확인
        brand = Brand.query.get_or_404(brand_id)
        
        # 기간 필터링 (기본값: 최근 30일)
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 브랜드에 속한 매장들의 매출 데이터 조회
        # 실제 운영에서는 Order 테이블에서 매출 데이터를 조회해야 함
        # 현재는 샘플 데이터 반환
        sample_sales = [
            {
                'id': 1,
                'amount': 1500000,
                'date': (end_date - timedelta(days=1)).isoformat(),
                'store_name': '샘플매장1'
            },
            {
                'id': 2,
                'amount': 2000000,
                'date': (end_date - timedelta(days=2)).isoformat(),
                'store_name': '샘플매장2'
            },
            {
                'id': 3,
                'amount': 1800000,
                'date': (end_date - timedelta(days=3)).isoformat(),
                'store_name': '샘플매장3'
            }
        ]
        
        return jsonify({
            'success': True,
            'sales': sample_sales,
            'total_amount': sum(sale['amount'] for sale in sample_sales),
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"브랜드 매출 조회 오류: {str(e)}")
        return jsonify({'error': '매출 데이터를 불러오는 중 오류가 발생했습니다.'}), 500

@admin_brand_api.route('/<int:brand_id>/improvements', methods=['GET'])
@login_required
def get_brand_improvements(brand_id):
    """브랜드별 개선요청 데이터 조회"""
    try:
        # 권한 확인
        if not current_user.is_admin():
            return jsonify({'error': '권한이 없습니다.'}), 403

        # 브랜드 존재 확인
        brand = Brand.query.get_or_404(brand_id)
        
        # 브랜드에 속한 개선요청 조회
        improvements = ImprovementRequest.query.filter_by(brand_id=brand_id).order_by(
            ImprovementRequest.created_at.desc()
        ).all()
        
        improvement_list = []
        for improvement in improvements:
            improvement_list.append({
                'id': improvement.id,
                'title': improvement.title,
                'category': improvement.category,
                'priority': improvement.priority,
                'status': improvement.status,
                'created_at': improvement.created_at.isoformat() if improvement.created_at else None
            })
        
        return jsonify({
            'success': True,
            'improvements': improvement_list,
            'total_count': len(improvement_list)
        })
        
    except Exception as e:
        logger.error(f"브랜드 개선요청 조회 오류: {str(e)}")
        return jsonify({'error': '개선요청 데이터를 불러오는 중 오류가 발생했습니다.'}), 500 