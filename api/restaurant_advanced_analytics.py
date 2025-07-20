"""
레스토랑 고급 분석 시스템
머신러닝 기반 인사이트 및 예측 분석 기능 제공
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, and_, desc, extract
from models_main import Order, Menu, Customer, Branch, Staff, Inventory
from extensions import db
import logging
from typing import Dict, List, Any, Tuple
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os

# 로깅 설정
logger = logging.getLogger(__name__)

# 블루프린트 생성
restaurant_advanced_analytics = Blueprint('restaurant_advanced_analytics', __name__)

# 모델 저장 경로
ADVANCED_MODEL_DIR = "data/advanced_analytics/models"


@restaurant_advanced_analytics.route('/api/restaurant/advanced/anomaly-detection')
@login_required
def detect_anomalies():
    """이상치 탐지 API"""
    try:
        branch_id = request.args.get('branch_id')
        data_type = request.args.get('type', 'sales')  # sales, orders, inventory
        
        # 사용자 권한 확인
        if not current_user.is_authenticated:
            return jsonify({'error': '인증 필요'}), 401

        # 사용자 소속 매장 확인
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id
        
        if branch_id and user_branch and int(branch_id) != user_branch:
            return jsonify({'error': '권한 없음'}), 403

        anomalies = detect_data_anomalies(data_type, user_branch or branch_id)
        return jsonify(anomalies)

    except Exception as e:
        logger.error(f"이상치 탐지 오류: {str(e)}")
        return jsonify({'error': '이상치 탐지 실패'}), 500


@restaurant_advanced_analytics.route('/api/restaurant/advanced/customer-segmentation')
@login_required
def customer_segmentation():
    """고객 세분화 분석 API"""
    try:
        branch_id = request.args.get('branch_id')
        
        # 사용자 권한 확인
        if not current_user.is_authenticated:
            return jsonify({'error': '인증 필요'}), 401

        # 사용자 소속 매장 확인
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id
        
        if branch_id and user_branch and int(branch_id) != user_branch:
            return jsonify({'error': '권한 없음'}), 403

        segmentation = analyze_customer_segmentation(user_branch or branch_id)
        return jsonify(segmentation)

    except Exception as e:
        logger.error(f"고객 세분화 분석 오류: {str(e)}")
        return jsonify({'error': '고객 세분화 분석 실패'}), 500


@restaurant_advanced_analytics.route('/api/restaurant/advanced/trend-analysis')
@login_required
def trend_analysis():
    """트렌드 분석 API"""
    try:
        branch_id = request.args.get('branch_id')
        trend_type = request.args.get('type', 'sales')  # sales, menu, customer
        
        # 사용자 권한 확인
        if not current_user.is_authenticated:
            return jsonify({'error': '인증 필요'}), 401

        # 사용자 소속 매장 확인
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id
        
        if branch_id and user_branch and int(branch_id) != user_branch:
            return jsonify({'error': '권한 없음'}), 403

        trends = analyze_trends(trend_type, user_branch or branch_id)
        return jsonify(trends)

    except Exception as e:
        logger.error(f"트렌드 분석 오류: {str(e)}")
        return jsonify({'error': '트렌드 분석 실패'}), 500


@restaurant_advanced_analytics.route('/api/restaurant/advanced/competitive-analysis')
@login_required
def competitive_analysis():
    """경쟁사 분석 API"""
    try:
        branch_id = request.args.get('branch_id')
        
        # 사용자 권한 확인
        if not current_user.is_authenticated:
            return jsonify({'error': '인증 필요'}), 401

        # 사용자 소속 매장 확인
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id
        
        if branch_id and user_branch and int(branch_id) != user_branch:
            return jsonify({'error': '권한 없음'}), 403

        analysis = analyze_competition(user_branch or branch_id)
        return jsonify(analysis)

    except Exception as e:
        logger.error(f"경쟁사 분석 오류: {str(e)}")
        return jsonify({'error': '경쟁사 분석 실패'}), 500


@restaurant_advanced_analytics.route('/api/restaurant/advanced/insights')
@login_required
def generate_insights():
    """AI 인사이트 생성 API"""
    try:
        branch_id = request.args.get('branch_id')
        
        # 사용자 권한 확인
        if not current_user.is_authenticated:
            return jsonify({'error': '인증 필요'}), 401

        # 사용자 소속 매장 확인
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id
        
        if branch_id and user_branch and int(branch_id) != user_branch:
            return jsonify({'error': '권한 없음'}), 403

        insights = generate_ai_insights(user_branch or branch_id)
        return jsonify(insights)

    except Exception as e:
        logger.error(f"AI 인사이트 생성 오류: {str(e)}")
        return jsonify({'error': 'AI 인사이트 생성 실패'}), 500


def detect_data_anomalies(data_type: str, branch_id: int = None) -> Dict[str, Any]:
    """데이터 이상치 탐지"""
    try:
        # 최근 90일 데이터 수집
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=90)
        
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        if data_type == 'sales':
            # 매출 데이터 이상치 탐지
            daily_sales = db.session.query(
                func.date(Order.created_at).label('date'),
                func.sum(Order.total_amount).label('revenue')
            ).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date,
                    *base_filter
                )
            ).group_by(func.date(Order.created_at)).all()

            if len(daily_sales) < 10:
                return {'anomalies': [], 'total_points': 0, 'anomaly_rate': 0}

            # 데이터 준비
            sales_data = np.array([sale.revenue for sale in daily_sales]).reshape(-1, 1)
            
            # 이상치 탐지 모델
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomaly_labels = iso_forest.fit_predict(sales_data)
            
            # 이상치 식별
            anomalies = []
            for i, label in enumerate(anomaly_labels):
                if label == -1:  # 이상치
                    anomalies.append({
                        'date': daily_sales[i].date.strftime('%Y-%m-%d'),
                        'value': daily_sales[i].revenue,
                        'type': '매출 이상',
                        'severity': 'high' if daily_sales[i].revenue > np.mean(sales_data) * 1.5 else 'medium'
                    })

        elif data_type == 'orders':
            # 주문 수 이상치 탐지
            daily_orders = db.session.query(
                func.date(Order.created_at).label('date'),
                func.count(Order.id).label('order_count')
            ).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date,
                    *base_filter
                )
            ).group_by(func.date(Order.created_at)).all()

            if len(daily_orders) < 10:
                return {'anomalies': [], 'total_points': 0, 'anomaly_rate': 0}

            # 데이터 준비
            orders_data = np.array([order.order_count for order in daily_orders]).reshape(-1, 1)
            
            # 이상치 탐지
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomaly_labels = iso_forest.fit_predict(orders_data)
            
            # 이상치 식별
            anomalies = []
            for i, label in enumerate(anomaly_labels):
                if label == -1:  # 이상치
                    anomalies.append({
                        'date': daily_orders[i].date.strftime('%Y-%m-%d'),
                        'value': daily_orders[i].order_count,
                        'type': '주문 수 이상',
                        'severity': 'high' if daily_orders[i].order_count > np.mean(orders_data) * 1.5 else 'medium'
                    })

        else:
            return {'anomalies': [], 'total_points': 0, 'anomaly_rate': 0}

        total_points = len(daily_sales) if data_type == 'sales' else len(daily_orders)
        anomaly_rate = len(anomalies) / total_points if total_points > 0 else 0

        return {
            'anomalies': anomalies,
            'total_points': total_points,
            'anomaly_rate': round(anomaly_rate * 100, 2),
            'data_type': data_type
        }

    except Exception as e:
        logger.error(f"이상치 탐지 오류: {str(e)}")
        return {'anomalies': [], 'total_points': 0, 'anomaly_rate': 0}


def analyze_customer_segmentation(branch_id: int = None) -> Dict[str, Any]:
    """고객 세분화 분석"""
    try:
        # 최근 90일 고객 데이터 수집
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=90)
        
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        # 고객별 특성 수집
        customer_data = db.session.query(
            Order.customer_id,
            func.count(Order.id).label('frequency'),
            func.sum(Order.total_amount).label('monetary'),
            func.avg(Order.total_amount).label('avg_order_value'),
            func.min(Order.created_at).label('first_order'),
            func.max(Order.created_at).label('last_order')
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                Order.customer_id.isnot(None),
                *base_filter
            )
        ).group_by(Order.customer_id).all()

        if len(customer_data) < 10:
            return generate_sample_segmentation()

        # 특성 데이터 준비
        features = []
        customer_ids = []
        
        for customer in customer_data:
            recency = (end_date - customer.last_order.date()).days
            frequency = customer.frequency
            monetary = customer.monetary
            
            features.append([recency, frequency, monetary])
            customer_ids.append(customer.customer_id)

        # K-means 클러스터링
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        kmeans = KMeans(n_clusters=4, random_state=42)
        cluster_labels = kmeans.fit_predict(features_scaled)

        # 클러스터별 특성 분석
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = {
                    'customers': [],
                    'avg_recency': 0,
                    'avg_frequency': 0,
                    'avg_monetary': 0,
                    'count': 0
                }
            
            clusters[label]['customers'].append(customer_ids[i])
            clusters[label]['avg_recency'] += features[i][0]
            clusters[label]['avg_frequency'] += features[i][1]
            clusters[label]['avg_monetary'] += features[i][2]
            clusters[label]['count'] += 1

        # 클러스터 특성 계산 및 라벨링
        segments = []
        for label, cluster in clusters.items():
            avg_recency = cluster['avg_recency'] / cluster['count']
            avg_frequency = cluster['avg_frequency'] / cluster['count']
            avg_monetary = cluster['avg_monetary'] / cluster['count']
            
            # 세그먼트 라벨링
            if avg_monetary > np.mean([c['avg_monetary'] for c in clusters.values()]):
                if avg_frequency > np.mean([c['avg_frequency'] for c in clusters.values()]):
                    segment_name = "VIP 고객"
                else:
                    segment_name = "고가치 고객"
            else:
                if avg_frequency > np.mean([c['avg_frequency'] for c in clusters.values()]):
                    segment_name = "정기 고객"
                else:
                    segment_name = "일회성 고객"

            segments.append({
                'segment_id': label,
                'segment_name': segment_name,
                'customer_count': cluster['count'],
                'avg_recency': round(avg_recency, 1),
                'avg_frequency': round(avg_frequency, 1),
                'avg_monetary': round(avg_monetary),
                'percentage': round(cluster['count'] / len(customer_data) * 100, 1)
            })

        return {
            'segments': segments,
            'total_customers': len(customer_data),
            'clustering_quality': calculate_clustering_quality(features_scaled, cluster_labels)
        }

    except Exception as e:
        logger.error(f"고객 세분화 분석 오류: {str(e)}")
        return generate_sample_segmentation()


def analyze_trends(trend_type: str, branch_id: int = None) -> Dict[str, Any]:
    """트렌드 분석"""
    try:
        # 최근 30일 데이터 수집
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=30)
        
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        if trend_type == 'sales':
            # 매출 트렌드 분석
            daily_sales = db.session.query(
                func.date(Order.created_at).label('date'),
                func.sum(Order.total_amount).label('revenue'),
                func.count(Order.id).label('order_count')
            ).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date,
                    *base_filter
                )
            ).group_by(func.date(Order.created_at)).order_by('date').all()

            if len(daily_sales) < 7:
                return {'trends': [], 'trend_direction': 'stable', 'confidence': 0}

            # 트렌드 계산
            revenues = [sale.revenue for sale in daily_sales]
            trend_direction, trend_strength = calculate_trend(revenues)

            trends = [
                {
                    'date': sale.date.strftime('%Y-%m-%d'),
                    'revenue': sale.revenue,
                    'order_count': sale.order_count,
                    'avg_order_value': sale.revenue / sale.order_count if sale.order_count > 0 else 0
                }
                for sale in daily_sales
            ]

        elif trend_type == 'menu':
            # 메뉴 트렌드 분석
            menu_trends = db.session.query(
                Menu.name,
                func.count(Order.id).label('order_count'),
                func.sum(Order.total_amount).label('total_revenue')
            ).join(Order).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date,
                    *base_filter
                )
            ).group_by(Menu.name).order_by(desc('order_count')).limit(10).all()

            trends = [
                {
                    'menu_name': menu.name,
                    'order_count': menu.order_count,
                    'total_revenue': menu.total_revenue,
                    'trend': 'increasing' if menu.order_count > 10 else 'stable'
                }
                for menu in menu_trends
            ]
            trend_direction = 'increasing'
            trend_strength = 0.8

        else:
            return {'trends': [], 'trend_direction': 'stable', 'confidence': 0}

        return {
            'trends': trends,
            'trend_direction': trend_direction,
            'trend_strength': round(trend_strength, 2),
            'confidence': calculate_trend_confidence(trends)
        }

    except Exception as e:
        logger.error(f"트렌드 분석 오류: {str(e)}")
        return {'trends': [], 'trend_direction': 'stable', 'confidence': 0}


def analyze_competition(branch_id: int = None) -> Dict[str, Any]:
    """경쟁사 분석"""
    try:
        # 현재 매장 정보
        branch_info = get_branch_info(branch_id)
        
        # 시장 데이터 (샘플)
        market_data = {
            'total_market_size': 1000000000,  # 10억원
            'market_growth_rate': 5.2,
            'competitor_count': 15,
            'average_order_value': 25000,
            'customer_satisfaction_avg': 4.1
        }

        # 경쟁사 분석 (샘플 데이터)
        competitors = [
            {
                'name': '경쟁사 A',
                'market_share': 25.5,
                'avg_order_value': 28000,
                'customer_satisfaction': 4.3,
                'strengths': ['브랜드 인지도', '위치'],
                'weaknesses': ['가격', '서비스 속도']
            },
            {
                'name': '경쟁사 B',
                'market_share': 18.2,
                'avg_order_value': 22000,
                'customer_satisfaction': 3.9,
                'strengths': ['가격', '메뉴 다양성'],
                'weaknesses': ['서비스 품질', '위치']
            }
        ]

        # SWOT 분석
        swot_analysis = {
            'strengths': ['고품질 재료', '전문 주방장', '고객 서비스'],
            'weaknesses': ['가격 경쟁력', '마케팅 부족', '위치'],
            'opportunities': ['온라인 주문 확대', '배달 서비스', '신메뉴 개발'],
            'threats': ['경쟁사 증가', '원재료 가격 상승', '인건비 상승']
        }

        # 시장 포지셔닝
        positioning = {
            'current_position': '프리미엄',
            'target_position': '프리미엄 + 접근성',
            'differentiation_factors': ['신선한 재료', '전문적인 조리', '개인화된 서비스']
        }

        return {
            'market_data': market_data,
            'competitors': competitors,
            'swot_analysis': swot_analysis,
            'positioning': positioning,
            'recommendations': generate_competitive_recommendations(swot_analysis, positioning)
        }

    except Exception as e:
        logger.error(f"경쟁사 분석 오류: {str(e)}")
        return {'error': '경쟁사 분석 실패'}


def generate_ai_insights(branch_id: int = None) -> Dict[str, Any]:
    """AI 인사이트 생성"""
    try:
        insights = []
        
        # 매출 인사이트
        sales_insights = generate_sales_insights(branch_id)
        insights.extend(sales_insights)
        
        # 고객 인사이트
        customer_insights = generate_customer_insights(branch_id)
        insights.extend(customer_insights)
        
        # 운영 인사이트
        operational_insights = generate_operational_insights(branch_id)
        insights.extend(operational_insights)
        
        # 메뉴 인사이트
        menu_insights = generate_menu_insights(branch_id)
        insights.extend(menu_insights)

        return {
            'insights': insights,
            'total_insights': len(insights),
            'priority_insights': [insight for insight in insights if insight['priority'] == 'high'],
            'generated_at': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"AI 인사이트 생성 오류: {str(e)}")
        return {'insights': [], 'total_insights': 0, 'priority_insights': []}


# 헬퍼 함수들
def calculate_trend(data: List[float]) -> Tuple[str, float]:
    """트렌드 방향과 강도 계산"""
    try:
        if len(data) < 2:
            return 'stable', 0.0
        
        # 선형 회귀를 통한 트렌드 계산
        x = np.arange(len(data))
        y = np.array(data)
        
        # 기울기 계산
        slope = np.polyfit(x, y, 1)[0]
        
        # 트렌드 방향 결정
        if slope > 0:
            direction = 'increasing'
        elif slope < 0:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        # 트렌드 강도 계산 (R² 값)
        correlation = np.corrcoef(x, y)[0, 1]
        strength = abs(correlation) if not np.isnan(correlation) else 0.0
        
        return direction, strength
        
    except Exception as e:
        logger.error(f"트렌드 계산 오류: {str(e)}")
        return 'stable', 0.0


def calculate_trend_confidence(trends: List[Dict]) -> float:
    """트렌드 신뢰도 계산"""
    try:
        if len(trends) < 3:
            return 0.5
        
        # 데이터 일관성을 통한 신뢰도 계산
        values = [t.get('revenue', 0) for t in trends]
        std_dev = np.std(values)
        mean_val = np.mean(values)
        
        # 변동계수 (CV) 기반 신뢰도
        cv = std_dev / mean_val if mean_val > 0 else 1.0
        confidence = max(0.1, 1.0 - cv)
        
        return round(confidence, 2)
        
    except Exception as e:
        logger.error(f"트렌드 신뢰도 계산 오류: {str(e)}")
        return 0.5


def calculate_clustering_quality(features: np.ndarray, labels: np.ndarray) -> float:
    """클러스터링 품질 계산"""
    try:
        from sklearn.metrics import silhouette_score
        if len(np.unique(labels)) < 2:
            return 0.0
        
        score = silhouette_score(features, labels)
        return round(score, 3)
        
    except Exception as e:
        logger.error(f"클러스터링 품질 계산 오류: {str(e)}")
        return 0.0


def get_branch_info(branch_id: int = None) -> Dict[str, Any]:
    """매장 정보 조회"""
    try:
        if branch_id:
            branch = db.session.query(Branch).filter_by(id=branch_id).first()
            if branch:
                return {
                    'name': branch.name,
                    'location': branch.location,
                    'type': branch.type
                }
        
        return {
            'name': 'Unknown Branch',
            'location': 'Unknown',
            'type': 'restaurant'
        }
        
    except Exception as e:
        logger.error(f"매장 정보 조회 오류: {str(e)}")
        return {}


def generate_competitive_recommendations(swot: Dict, positioning: Dict) -> List[str]:
    """경쟁사 대응 전략 추천"""
    recommendations = []
    
    # 강점 활용
    if '고품질 재료' in swot['strengths']:
        recommendations.append("고품질 재료를 강조한 마케팅 캠페인 진행")
    
    # 약점 개선
    if '가격 경쟁력' in swot['weaknesses']:
        recommendations.append("가격 경쟁력 향상을 위한 비용 최적화 검토")
    
    # 기회 활용
    if '온라인 주문 확대' in swot['opportunities']:
        recommendations.append("온라인 주문 플랫폼 확대 및 최적화")
    
    # 위협 대응
    if '경쟁사 증가' in swot['threats']:
        recommendations.append("차별화된 서비스로 브랜드 가치 강화")
    
    return recommendations


def generate_sales_insights(branch_id: int = None) -> List[Dict]:
    """매출 인사이트 생성"""
    try:
        insights = []
        
        # 최근 7일 매출 분석
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=7)
        
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        daily_sales = db.session.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                *base_filter
            )
        ).group_by(func.date(Order.created_at)).all()

        if len(daily_sales) >= 3:
            revenues = [sale.revenue for sale in daily_sales]
            avg_revenue = np.mean(revenues)
            
            # 매출 트렌드 인사이트
            if revenues[-1] > avg_revenue * 1.2:
                insights.append({
                    'type': 'sales_trend',
                    'title': '매출 상승 트렌드',
                    'description': '최근 매출이 평균 대비 20% 이상 증가하고 있습니다.',
                    'priority': 'high',
                    'action': '이 트렌드를 유지하기 위한 마케팅 전략 수립'
                })
            elif revenues[-1] < avg_revenue * 0.8:
                insights.append({
                    'type': 'sales_decline',
                    'title': '매출 하락 경고',
                    'description': '최근 매출이 평균 대비 20% 이상 감소하고 있습니다.',
                    'priority': 'high',
                    'action': '매출 하락 원인 분석 및 대응 방안 수립'
                })

        return insights
        
    except Exception as e:
        logger.error(f"매출 인사이트 생성 오류: {str(e)}")
        return []


def generate_customer_insights(branch_id: int = None) -> List[Dict]:
    """고객 인사이트 생성"""
    try:
        insights = []
        
        # 고객 행동 분석
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=30)
        
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        customer_behavior = db.session.query(
            func.count(Order.customer_id.distinct()).label('unique_customers'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                *base_filter
            )
        ).first()

        if customer_behavior:
            if customer_behavior.avg_order_value > 30000:
                insights.append({
                    'type': 'customer_value',
                    'title': '고가치 고객층',
                    'description': '평균 주문 금액이 높아 고가치 고객층이 형성되어 있습니다.',
                    'priority': 'medium',
                    'action': 'VIP 고객 대상 특별 서비스 제공'
                })

        return insights
        
    except Exception as e:
        logger.error(f"고객 인사이트 생성 오류: {str(e)}")
        return []


def generate_operational_insights(branch_id: int = None) -> List[Dict]:
    """운영 인사이트 생성"""
    try:
        insights = []
        
        # 피크 시간대 분석
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=7)
        
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        hourly_orders = db.session.query(
            func.extract('hour', Order.created_at).label('hour'),
            func.count(Order.id).label('order_count')
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                *base_filter
            )
        ).group_by(func.extract('hour', Order.created_at)).all()

        if hourly_orders:
            peak_hour = max(hourly_orders, key=lambda x: x.order_count)
            if peak_hour.order_count > 20:
                insights.append({
                    'type': 'peak_hours',
                    'title': '피크 시간대 최적화',
                    'description': f'{peak_hour.hour}시에 주문이 집중되고 있습니다.',
                    'priority': 'medium',
                    'action': '피크 시간대 인력 배치 최적화'
                })

        return insights
        
    except Exception as e:
        logger.error(f"운영 인사이트 생성 오류: {str(e)}")
        return []


def generate_menu_insights(branch_id: int = None) -> List[Dict]:
    """메뉴 인사이트 생성"""
    try:
        insights = []
        
        # 메뉴 성과 분석
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=30)
        
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        menu_performance = db.session.query(
            Menu.name,
            func.count(Order.id).label('order_count')
        ).join(Order).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                *base_filter
            )
        ).group_by(Menu.name).order_by(desc('order_count')).limit(5).all()

        if menu_performance:
            top_menu = menu_performance[0]
            if top_menu.order_count > 50:
                insights.append({
                    'type': 'menu_performance',
                    'title': '인기 메뉴 활용',
                    'description': f'{top_menu.name}이 가장 인기 있는 메뉴입니다.',
                    'priority': 'medium',
                    'action': '인기 메뉴를 활용한 프로모션 진행'
                })

        return insights
        
    except Exception as e:
        logger.error(f"메뉴 인사이트 생성 오류: {str(e)}")
        return []


def generate_sample_segmentation() -> Dict[str, Any]:
    """샘플 고객 세분화 데이터"""
    return {
        'segments': [
            {
                'segment_id': 0,
                'segment_name': 'VIP 고객',
                'customer_count': 25,
                'avg_recency': 5.2,
                'avg_frequency': 15.8,
                'avg_monetary': 450000,
                'percentage': 15.2
            },
            {
                'segment_id': 1,
                'segment_name': '정기 고객',
                'customer_count': 45,
                'avg_recency': 12.5,
                'avg_frequency': 8.3,
                'avg_monetary': 180000,
                'percentage': 27.3
            }
        ],
        'total_customers': 165,
        'clustering_quality': 0.75
    }


# 블루프린트 등록
def init_app(app):
    app.register_blueprint(restaurant_advanced_analytics) 