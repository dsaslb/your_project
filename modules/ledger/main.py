#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
가계부 모듈 - 정기지출/수입 관리
"""

from flask import Blueprint, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 생성
ledger_bp = Blueprint('ledger', __name__, url_prefix='/api/ledger')

# 기존 앱의 데이터베이스 인스턴스 사용
from extensions import db

def init_db(app):
    """데이터베이스 초기화"""
    with app.app_context():
        db.create_all()
        logger.info("가계부 데이터베이스 테이블 생성 완료")

class LedgerItem(db.Model):
    """가계부 항목 모델"""
    __tablename__ = 'ledger_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    item_type = db.Column(db.String(20), nullable=False)  # 'income' 또는 'expense'
    category = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # 'daily', 'weekly', 'monthly', 'yearly'
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    memo = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'amount': self.amount,
            'item_type': self.item_type,
            'category': self.category,
            'frequency': self.frequency,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'memo': self.memo,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class LedgerTransaction(db.Model):
    """실제 거래 내역 모델"""
    __tablename__ = 'ledger_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('ledger_items.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    memo = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'user_id': self.user_id,
            'amount': self.amount,
            'transaction_date': self.transaction_date.isoformat(),
            'memo': self.memo,
            'created_at': self.created_at.isoformat()
        }

class LedgerService:
    """가계부 서비스 클래스"""
    
    @staticmethod
    def get_user_items(user_id: int) -> List[Dict]:
        """사용자의 모든 가계부 항목 조회"""
        try:
            items = LedgerItem.query.filter_by(user_id=user_id, is_active=True).all()
            return [item.to_dict() for item in items]
        except Exception as e:
            logger.error(f"가계부 항목 조회 실패: {e}")
            return []
    
    @staticmethod
    def create_item(user_id: int, data: Dict) -> Dict:
        """새 가계부 항목 생성"""
        try:
            item = LedgerItem(
                user_id=user_id,
                name=data['name'],
                amount=data['amount'],
                item_type=data['item_type'],
                category=data['category'],
                frequency=data['frequency'],
                start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
                end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
                memo=data.get('memo', '')
            )
            db.session.add(item)
            db.session.commit()
            return item.to_dict()
        except Exception as e:
            logger.error(f"가계부 항목 생성 실패: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def update_item(item_id: int, user_id: int, data: Dict) -> Dict:
        """가계부 항목 수정"""
        try:
            item = LedgerItem.query.filter_by(id=item_id, user_id=user_id).first()
            if not item:
                return None
            
            for key, value in data.items():
                if hasattr(item, key):
                    if key in ['start_date', 'end_date'] and value:
                        setattr(item, key, datetime.strptime(value, '%Y-%m-%d').date())
                    else:
                        setattr(item, key, value)
            
            item.updated_at = datetime.utcnow()
            db.session.commit()
            return item.to_dict()
        except Exception as e:
            logger.error(f"가계부 항목 수정 실패: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def delete_item(item_id: int, user_id: int) -> bool:
        """가계부 항목 삭제 (비활성화)"""
        try:
            item = LedgerItem.query.filter_by(id=item_id, user_id=user_id).first()
            if not item:
                return False
            
            item.is_active = False
            item.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"가계부 항목 삭제 실패: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_monthly_summary(user_id: int, year: int, month: int) -> Dict:
        """월별 요약 정보"""
        try:
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
            
            # 수입 항목들
            income_items = LedgerItem.query.filter_by(
                user_id=user_id, 
                item_type='income', 
                is_active=True
            ).all()
            
            # 지출 항목들
            expense_items = LedgerItem.query.filter_by(
                user_id=user_id, 
                item_type='expense', 
                is_active=True
            ).all()
            
            # 월별 수입 계산
            total_income = 0
            income_details = []
            for item in income_items:
                monthly_amount = LedgerService._calculate_monthly_amount(item, year, month)
                total_income += monthly_amount
                income_details.append({
                    'name': item.name,
                    'amount': monthly_amount,
                    'category': item.category
                })
            
            # 월별 지출 계산
            total_expense = 0
            expense_details = []
            for item in expense_items:
                monthly_amount = LedgerService._calculate_monthly_amount(item, year, month)
                total_expense += monthly_amount
                expense_details.append({
                    'name': item.name,
                    'amount': monthly_amount,
                    'category': item.category
                })
            
            balance = total_income - total_expense
            
            return {
                'year': year,
                'month': month,
                'total_income': total_income,
                'total_expense': total_expense,
                'balance': balance,
                'income_details': income_details,
                'expense_details': expense_details
            }
            
        except Exception as e:
            logger.error(f"월별 요약 계산 실패: {e}")
            return {}
    
    @staticmethod
    def _calculate_monthly_amount(item: LedgerItem, year: int, month: int) -> float:
        """항목의 월별 금액 계산"""
        try:
            if item.frequency == 'monthly':
                return item.amount
            elif item.frequency == 'weekly':
                # 해당 월의 주 수 계산
                start_date = datetime(year, month, 1).date()
                if month == 12:
                    end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
                
                weeks = ((end_date - start_date).days + 1) // 7
                return item.amount * weeks
            elif item.frequency == 'yearly':
                # 연간 금액을 12로 나누기
                return item.amount / 12
            elif item.frequency == 'daily':
                # 해당 월의 일 수
                start_date = datetime(year, month, 1).date()
                if month == 12:
                    end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
                
                days = (end_date - start_date).days + 1
                return item.amount * days
            else:
                return item.amount
        except Exception as e:
            logger.error(f"월별 금액 계산 실패: {e}")
            return 0.0
    
    @staticmethod
    def get_upcoming_payments(user_id: int, days: int = 30) -> List[Dict]:
        """다가오는 결제 예정일 조회"""
        try:
            today = datetime.now().date()
            end_date = today + timedelta(days=days)
            
            items = LedgerItem.query.filter_by(
                user_id=user_id, 
                is_active=True
            ).all()
            
            upcoming = []
            for item in items:
                next_payment = LedgerService._get_next_payment_date(item, today)
                if next_payment and next_payment <= end_date:
                    upcoming.append({
                        'item': item.to_dict(),
                        'next_payment_date': next_payment.isoformat(),
                        'days_until': (next_payment - today).days
                    })
            
            # 결제일 순으로 정렬
            upcoming.sort(key=lambda x: x['next_payment_date'])
            return upcoming
            
        except Exception as e:
            logger.error(f"다가오는 결제 조회 실패: {e}")
            return []
    
    @staticmethod
    def _get_next_payment_date(item: LedgerItem, from_date: datetime.date) -> datetime.date:
        """다음 결제일 계산"""
        try:
            if item.start_date > from_date:
                return item.start_date
            
            if item.frequency == 'monthly':
                # 월별 결제일 계산
                current_date = item.start_date
                while current_date <= from_date:
                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)
                return current_date
            
            elif item.frequency == 'weekly':
                # 주별 결제일 계산
                days_diff = (from_date - item.start_date).days
                weeks_passed = days_diff // 7
                next_week = weeks_passed + 1
                return item.start_date + timedelta(weeks=next_week)
            
            elif item.frequency == 'yearly':
                # 연간 결제일 계산
                current_date = item.start_date
                while current_date <= from_date:
                    current_date = current_date.replace(year=current_date.year + 1)
                return current_date
            
            elif item.frequency == 'daily':
                # 일일 결제는 매일
                return from_date + timedelta(days=1)
            
            else:
                return item.start_date
                
        except Exception as e:
            logger.error(f"다음 결제일 계산 실패: {e}")
            return None

# API 엔드포인트들
@ledger_bp.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        "status": "healthy",
        "module": "ledger",
        "timestamp": datetime.now().isoformat()
    })

@ledger_bp.route('/items', methods=['GET'])
def get_items():
    """사용자의 가계부 항목 조회"""
    try:
        # TODO: 실제 사용자 ID는 JWT에서 추출
        user_id = request.args.get('user_id', 1, type=int)
        items = LedgerService.get_user_items(user_id)
        return jsonify({
            "success": True,
            "items": items
        })
    except Exception as e:
        logger.error(f"항목 조회 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@ledger_bp.route('/items', methods=['POST'])
def create_item():
    """새 가계부 항목 생성"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)  # TODO: JWT에서 추출
        
        # 필수 필드 검증
        required_fields = ['name', 'amount', 'item_type', 'category', 'frequency', 'start_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "error": f"{field} 필드는 필수입니다."}), 400
        
        item = LedgerService.create_item(user_id, data)
        if item:
            return jsonify({"success": True, "item": item}), 201
        else:
            return jsonify({"success": False, "error": "항목 생성 실패"}), 500
            
    except Exception as e:
        logger.error(f"항목 생성 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@ledger_bp.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """가계부 항목 수정"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)  # TODO: JWT에서 추출
        
        item = LedgerService.update_item(item_id, user_id, data)
        if item:
            return jsonify({"success": True, "item": item})
        else:
            return jsonify({"success": False, "error": "항목을 찾을 수 없습니다."}), 404
            
    except Exception as e:
        logger.error(f"항목 수정 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@ledger_bp.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """가계부 항목 삭제"""
    try:
        user_id = request.args.get('user_id', 1, type=int)  # TODO: JWT에서 추출
        
        success = LedgerService.delete_item(item_id, user_id)
        if success:
            return jsonify({"success": True, "message": "항목이 삭제되었습니다."})
        else:
            return jsonify({"success": False, "error": "항목을 찾을 수 없습니다."}), 404
            
    except Exception as e:
        logger.error(f"항목 삭제 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@ledger_bp.route('/summary/<int:year>/<int:month>', methods=['GET'])
def get_monthly_summary(year, month):
    """월별 요약 정보"""
    try:
        user_id = request.args.get('user_id', 1, type=int)  # TODO: JWT에서 추출
        
        summary = LedgerService.get_monthly_summary(user_id, year, month)
        return jsonify({
            "success": True,
            "summary": summary
        })
    except Exception as e:
        logger.error(f"월별 요약 조회 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@ledger_bp.route('/upcoming', methods=['GET'])
def get_upcoming_payments():
    """다가오는 결제 예정일"""
    try:
        user_id = request.args.get('user_id', 1, type=int)  # TODO: JWT에서 추출
        days = request.args.get('days', 30, type=int)
        
        upcoming = LedgerService.get_upcoming_payments(user_id, days)
        return jsonify({
            "success": True,
            "upcoming": upcoming
        })
    except Exception as e:
        logger.error(f"다가오는 결제 조회 실패: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@ledger_bp.route('/categories', methods=['GET'])
def get_categories():
    """카테고리 목록"""
    categories = {
        'income': ['급여', '용돈', '투자수익', '부업수입', '기타수입'],
        'expense': ['주거비', '통신비', '교통비', '식비', '의료비', '교육비', '문화생활', '구독서비스', '기타지출']
    }
    return jsonify({
        "success": True,
        "categories": categories
    })

# 페이지 라우트
@ledger_bp.route('/dashboard')
def ledger_dashboard():
    """가계부 대시보드 페이지"""
    return render_template('ledger/dashboard.html')

@ledger_bp.route('/add')
def add_item_page():
    """항목 추가 페이지"""
    return render_template('ledger/add_item.html')

@ledger_bp.route('/edit/<int:item_id>')
def edit_item_page(item_id):
    """항목 편집 페이지"""
    return render_template('ledger/edit_item.html', item_id=item_id) 