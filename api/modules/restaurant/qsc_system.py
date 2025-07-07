from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from models import db
from api.gateway import token_required, role_required
from datetime import datetime, timedelta
import json

qsc_system = Blueprint('qsc_system', __name__)

# QSC 점검 항목 모델 (임시)
class QSCItem(db.Model):
    __tablename__ = 'qsc_items'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # quality, service, cleanliness
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    points = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QSCInspection(db.Model):
    __tablename__ = 'qsc_inspections'
    
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, nullable=False)
    inspector_id = db.Column(db.Integer, nullable=False)
    inspection_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    total_points = db.Column(db.Integer, default=0)
    earned_points = db.Column(db.Integer, default=0)
    score = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QSCInspectionDetail(db.Model):
    __tablename__ = 'qsc_inspection_details'
    
    id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('qsc_inspections.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('qsc_items.id'), nullable=False)
    is_passed = db.Column(db.Boolean, nullable=False)
    points_earned = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    photos = db.Column(db.Text)  # JSON array of photo URLs

# QSC 점검 항목 조회
@qsc_system.route('/qsc/items', methods=['GET'])
@token_required
def get_qsc_items(current_user):
    """QSC 점검 항목 조회"""
    try:
        category = request.args.get('category')
        
        query = QSCItem.query.filter_by(is_active=True)
        
        if category:
            query = query.filter(QSCItem.category == category)
        
        items = query.order_by(QSCItem.category, QSCItem.title).all()
        
        result = []
        for item in items:
            result.append({
                'id': item.id,
                'category': item.category,
                'title': item.title,
                'description': item.description,
                'points': item.points
            })
        
        return jsonify({'items': result}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get QSC items error: {str(e)}")
        return jsonify({'message': 'QSC 항목 조회 중 오류가 발생했습니다'}), 500

# QSC 점검 생성
@qsc_system.route('/qsc/inspections', methods=['POST'])
@token_required
@role_required(['super_admin', 'brand_manager', 'store_manager'])
def create_qsc_inspection(current_user):
    """QSC 점검 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['store_id', 'inspection_date', 'category', 'items']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} 필드는 필수입니다'}), 400
        
        # 권한 확인
        if current_user.role == 'store_manager':
            if data['store_id'] != current_user.store_id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403
        elif current_user.role == 'brand_manager':
            # 브랜드 관리자는 자신의 브랜드 매장만 점검 가능
            pass  # TODO: 브랜드 ID 확인 로직 추가
        
        # 점검 생성
        inspection = QSCInspection(
            store_id=data['store_id'],
            inspector_id=current_user.id,
            inspection_date=datetime.strptime(data['inspection_date'], '%Y-%m-%d').date(),
            category=data['category'],
            notes=data.get('notes')
        )
        
        db.session.add(inspection)
        db.session.flush()  # ID 생성
        
        # 점검 상세 항목 처리
        total_points = 0
        earned_points = 0
        
        for item_data in data['items']:
            item = QSCItem.query.get(item_data['item_id'])
            if not item:
                continue
            
            is_passed = item_data.get('is_passed', False)
            points_earned = item.points if is_passed else 0
            
            detail = QSCInspectionDetail(
                inspection_id=inspection.id,
                item_id=item.id,
                is_passed=is_passed,
                points_earned=points_earned,
                notes=item_data.get('notes'),
                photos=json.dumps(item_data.get('photos', []))
            )
            
            db.session.add(detail)
            total_points += item.points
            earned_points += points_earned
        
        # 점수 계산
        inspection.total_points = total_points
        inspection.earned_points = earned_points
        inspection.score = (earned_points / total_points * 100) if total_points > 0 else 0
        
        db.session.commit()
        
        return jsonify({
            'message': 'QSC 점검이 생성되었습니다',
            'inspection': {
                'id': inspection.id,
                'store_id': inspection.store_id,
                'category': inspection.category,
                'score': round(inspection.score, 2),
                'total_points': inspection.total_points,
                'earned_points': inspection.earned_points
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create QSC inspection error: {str(e)}")
        return jsonify({'message': 'QSC 점검 생성 중 오류가 발생했습니다'}), 500

# QSC 점검 목록 조회
@qsc_system.route('/qsc/inspections', methods=['GET'])
@token_required
def get_qsc_inspections(current_user):
    """QSC 점검 목록 조회"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        store_id = request.args.get('store_id')
        category = request.args.get('category')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = QSCInspection.query
        
        # 권한별 필터
        if current_user.role == 'store_manager':
            query = query.filter(QSCInspection.store_id == current_user.store_id)
        elif current_user.role == 'brand_manager':
            # 브랜드 관리자는 자신의 브랜드 매장 점검만 조회
            pass  # TODO: 브랜드 ID 필터 추가
        
        # 필터 적용
        if store_id:
            query = query.filter(QSCInspection.store_id == store_id)
        if category:
            query = query.filter(QSCInspection.category == category)
        if start_date:
            query = query.filter(QSCInspection.inspection_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(QSCInspection.inspection_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        # 최신순 정렬
        query = query.order_by(QSCInspection.inspection_date.desc())
        
        # 페이지네이션
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        inspections = []
        for inspection in pagination.items:
            inspections.append({
                'id': inspection.id,
                'store_id': inspection.store_id,
                'inspector_id': inspection.inspector_id,
                'inspection_date': inspection.inspection_date.isoformat(),
                'category': inspection.category,
                'score': round(inspection.score, 2),
                'total_points': inspection.total_points,
                'earned_points': inspection.earned_points,
                'notes': inspection.notes,
                'created_at': inspection.created_at.isoformat() if inspection.created_at else None
            })
        
        return jsonify({
            'inspections': inspections,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get QSC inspections error: {str(e)}")
        return jsonify({'message': 'QSC 점검 목록 조회 중 오류가 발생했습니다'}), 500

# QSC 점검 상세 조회
@qsc_system.route('/qsc/inspections/<int:inspection_id>', methods=['GET'])
@token_required
def get_qsc_inspection(current_user, inspection_id):
    """QSC 점검 상세 조회"""
    try:
        inspection = QSCInspection.query.get_or_404(inspection_id)
        
        # 권한 확인
        if current_user.role == 'store_manager':
            if inspection.store_id != current_user.store_id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403
        
        # 점검 상세 항목 조회
        details = QSCInspectionDetail.query.filter_by(inspection_id=inspection_id).all()
        
        detail_items = []
        for detail in details:
            item = QSCItem.query.get(detail.item_id)
            detail_items.append({
                'id': detail.id,
                'item_id': detail.item_id,
                'item_title': item.title if item else 'Unknown',
                'item_description': item.description if item else '',
                'item_points': item.points if item else 0,
                'is_passed': detail.is_passed,
                'points_earned': detail.points_earned,
                'notes': detail.notes,
                'photos': json.loads(detail.photos) if detail.photos else []
            })
        
        return jsonify({
            'id': inspection.id,
            'store_id': inspection.store_id,
            'inspector_id': inspection.inspector_id,
            'inspection_date': inspection.inspection_date.isoformat(),
            'category': inspection.category,
            'score': round(inspection.score, 2),
            'total_points': inspection.total_points,
            'earned_points': inspection.earned_points,
            'notes': inspection.notes,
            'created_at': inspection.created_at.isoformat() if inspection.created_at else None,
            'details': detail_items
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get QSC inspection error: {str(e)}")
        return jsonify({'message': 'QSC 점검 조회 중 오류가 발생했습니다'}), 500

# QSC 점검 통계
@qsc_system.route('/qsc/stats', methods=['GET'])
@token_required
def get_qsc_stats(current_user):
    """QSC 점검 통계"""
    try:
        query = QSCInspection.query
        
        # 권한별 필터
        if current_user.role == 'store_manager':
            query = query.filter(QSCInspection.store_id == current_user.store_id)
        elif current_user.role == 'brand_manager':
            # 브랜드 관리자는 자신의 브랜드 매장 점검만 조회
            pass  # TODO: 브랜드 ID 필터 추가
        
        total_inspections = query.count()
        
        # 카테고리별 통계
        category_stats = {}
        for category in ['quality', 'service', 'cleanliness']:
            category_query = query.filter(QSCInspection.category == category)
            count = category_query.count()
            avg_score = db.session.query(db.func.avg(QSCInspection.score)).filter(
                QSCInspection.category == category
            ).scalar() or 0
            
            category_stats[category] = {
                'count': count,
                'avg_score': round(avg_score, 2)
            }
        
        # 최근 30일 통계
        thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
        recent_inspections = query.filter(
            QSCInspection.inspection_date >= thirty_days_ago
        ).count()
        
        # 평균 점수
        overall_avg_score = db.session.query(db.func.avg(QSCInspection.score)).scalar() or 0
        
        return jsonify({
            'total_inspections': total_inspections,
            'recent_inspections': recent_inspections,
            'overall_avg_score': round(overall_avg_score, 2),
            'category_stats': category_stats
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get QSC stats error: {str(e)}")
        return jsonify({'message': 'QSC 통계 조회 중 오류가 발생했습니다'}), 500 