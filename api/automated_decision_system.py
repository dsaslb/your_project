from extensions import redis_client
from models_main import Order, User, InventoryItem, Schedule, Notification, SystemLog, db
import aiohttp
import asyncio
from dataclasses import dataclass, asdict
from collections import defaultdict
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import time
import json
import logging
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, current_app
from typing import Optional
query = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore
"""
자동화된 의사결정 시스템
AI 기반 인사이트를 바탕으로 한 자동화된 의사결정 및 실행 시스템
"""


# 데이터베이스 모델 import

logger = logging.getLogger(__name__)

automated_decision_bp = Blueprint('automated_decision', __name__)


@dataclass
class DecisionRule:
    """의사결정 규칙 데이터 클래스"""
    rule_id: str
    name: str
    category: str  # 'inventory', 'pricing', 'staffing', 'marketing', 'operations'
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    priority: int
    is_active: bool
    created_at: datetime
    last_executed: Optional[datetime]


@dataclass
class AutomatedDecision:
    """자동화된 의사결정 데이터 클래스"""
    decision_id: str
    rule_id: str
    rule_name: str
    category: str
    trigger_data: Optional[Dict[str, Any]]
    decision_result: Optional[Dict[str, Any]]
    confidence: float
    executed_actions: List[Dict[str, Any]]
    status: str  # 'pending', 'executing', 'completed', 'failed'
    created_at: datetime
    completed_at: Optional[datetime]


@dataclass
class BusinessAction:
    """비즈니스 액션 데이터 클래스"""
    action_id: str
    action_type: str  # 'inventory_order', 'price_adjustment', 'staff_schedule', 'marketing_campaign'
    parameters: Optional[Dict[str, Any]]
    estimated_impact: Optional[Dict[str, Any]]
    cost: float
    priority: str
    status: str  # 'pending', 'approved', 'rejected', 'executed'
    created_at: datetime
    executed_at: Optional[datetime]


class AutomatedDecisionSystem:
    """자동화된 의사결정 시스템"""

    def __init__(self):
        self.decision_rules = {}
        self.active_decisions = {}
        self.action_queue = []
        self.system_config = {
            'auto_execution_enabled': True,
            'approval_threshold': 0.8,  # 80% 이상 신뢰도면 자동 실행
            'max_concurrent_actions': 5,
            'decision_timeout': 300,  # 5분
            'retry_attempts': 3
        }

        # 기본 규칙 초기화
        self._initialize_default_rules()

        # 의사결정 엔진 시작
        self._start_decision_engine()

    def _initialize_default_rules(self):
        """기본 의사결정 규칙 초기화"""
        try:
            # 재고 관리 규칙
            self.decision_rules['low_stock_alert'] = DecisionRule(
                rule_id='low_stock_alert',
                name='재고 부족 자동 주문',
                category='inventory',
                conditions=[
                    {
                        'metric': 'current_stock',
                        'operator': '<',
                        'value': 'reorder_point',
                        'threshold': 0.1
                    }
                ],
                actions=[
                    {
                        'type': 'inventory_order',
                        'parameters': {
                            'quantity': 'reorder_quantity',
                            'priority': 'high'
                        }
                    },
                    {
                        'type': 'notification',
                        'parameters': {
                            'message': '재고 부족으로 자동 주문이 실행되었습니다.',
                            'priority': 'high'
                        }
                    }
                ],
                priority=1,
                is_active=True,
                created_at=datetime.now(),
                last_executed=None
            )

            # 가격 최적화 규칙
            self.decision_rules['price_optimization'] = DecisionRule(
                rule_id='price_optimization',
                name='수요 기반 가격 최적화',
                category='pricing',
                conditions=[
                    {
                        'metric': 'demand_trend',
                        'operator': '>',
                        'value': 0.2,
                        'threshold': 0.7
                    },
                    {
                        'metric': 'competitor_price',
                        'operator': '<',
                        'value': 'our_price',
                        'threshold': 0.1
                    }
                ],
                actions=[
                    {
                        'type': 'price_adjustment',
                        'parameters': {
                            'adjustment_type': 'increase',
                            'percentage': 0.05,
                            'max_increase': 0.15
                        }
                    }
                ],
                priority=2,
                is_active=True,
                created_at=datetime.now(),
                last_executed=None
            )

            # 인력 스케줄링 규칙
            self.decision_rules['staff_optimization'] = DecisionRule(
                rule_id='staff_optimization',
                name='수요 기반 인력 최적화',
                category='staffing',
                conditions=[
                    {
                        'metric': 'predicted_demand',
                        'operator': '>',
                        'value': 'current_staff_capacity',
                        'threshold': 0.2
                    }
                ],
                actions=[
                    {
                        'type': 'staff_schedule',
                        'parameters': {
                            'action': 'increase_staff',
                            'hours': 'peak_hours',
                            'duration': 'demand_period'
                        }
                    }
                ],
                priority=3,
                is_active=True,
                created_at=datetime.now(),
                last_executed=None
            )

            # 마케팅 캠페인 규칙
            self.decision_rules['marketing_opportunity'] = DecisionRule(
                rule_id='marketing_opportunity',
                name='고객 이탈 방지 캠페인',
                category='marketing',
                conditions=[
                    {
                        'metric': 'customer_churn_risk',
                        'operator': '>',
                        'value': 0.7,
                        'threshold': 0.8
                    }
                ],
                actions=[
                    {
                        'type': 'marketing_campaign',
                        'parameters': {
                            'campaign_type': 'retention',
                            'target_audience': 'high_risk_customers',
                            'offer_type': 'discount'
                        }
                    }
                ],
                priority=4,
                is_active=True,
                created_at=datetime.now(),
                last_executed=None
            )

            logger.info("기본 의사결정 규칙 초기화 완료")

        except Exception as e:
            logger.error(f"기본 규칙 초기화 실패: {e}")

    def _start_decision_engine(self):
        """의사결정 엔진 시작"""
        def decision_engine():
            while True:
                try:
                    # 새로운 데이터 확인
                    self._check_for_decisions()

                    # 대기 중인 액션 실행
                    self._execute_pending_actions()

                    # 완료된 의사결정 정리
                    self._cleanup_completed_decisions()

                    time.sleep(30)  # 30초마다 체크

                except Exception as e:
                    logger.error(f"의사결정 엔진 오류: {e}")
                    time.sleep(60)

        import threading
        # 자동화된 의사결정 엔진 비활성화됨 (서버는 계속 실행)
        # thread = threading.Thread(target=decision_engine, daemon=True)
        # thread.start()
        logger.info("자동화된 의사결정 엔진 비활성화됨")

    def _check_for_decisions(self):
        """의사결정 필요성 확인"""
        try:
            # 현재 비즈니스 상태 분석
            business_state = self._analyze_business_state()

            # 각 규칙에 대해 조건 확인
            for rule_id, rule in self.decision_rules.items():
                if not rule.is_active:
                    continue

                # 조건 충족 여부 확인
                if self._evaluate_conditions(rule.conditions, business_state):
                    # 의사결정 생성
                    decision = self._create_decision(rule, business_state)

                    # 의사결정 실행
                    self._execute_decision(decision)

        except Exception as e:
            logger.error(f"의사결정 확인 실패: {e}")

    def _analyze_business_state(self) -> Dict[str, Any]:
        """비즈니스 상태 분석"""
        try:
            # 재고 상태
            inventory_state = self._analyze_inventory_state()

            # 매출 상태
            sales_state = self._analyze_sales_state()

            # 고객 상태
            customer_state = self._analyze_customer_state()

            # 운영 상태
            operations_state = self._analyze_operations_state()

            return {
                'inventory': inventory_state,
                'sales': sales_state,
                'customer': customer_state,
                'operations': operations_state,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"비즈니스 상태 분석 실패: {e}")
            return {}

    def _analyze_inventory_state(self) -> Dict[str, Any]:
        """재고 상태 분석"""
        try:
            inventory_items = db.session.query(InventoryItem).all()

            low_stock_items = []
            overstock_items = []
            total_value = 0

            for item in inventory_items:
                total_value += item.current_stock * (item.unit_price or 0)

                if item.current_stock < (item.reorder_point or 10):
                    low_stock_items.append({
                        'item_id': item.id,
                        'name': item.name,
                        'current_stock': item.current_stock,
                        'reorder_point': item.reorder_point or 10,
                        'reorder_quantity': item.reorder_quantity or 20
                    })

                if item.current_stock > (item.max_stock or 100):
                    overstock_items.append({
                        'item_id': item.id,
                        'name': item.name,
                        'current_stock': item.current_stock,
                        'max_stock': item.max_stock or 100
                    })

            return {
                'total_items': len(inventory_items),
                'low_stock_count': len(low_stock_items),
                'overstock_count': len(overstock_items),
                'total_value': total_value,
                'low_stock_items': low_stock_items,
                'overstock_items': overstock_items
            }

        except Exception as e:
            logger.error(f"재고 상태 분석 실패: {e}")
            return {}

    def _analyze_sales_state(self) -> Dict[str, Any]:
        """매출 상태 분석"""
        try:
            # 최근 7일 매출 데이터
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)

            orders = db.session.query(Order).filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            ).all()

            daily_sales = defaultdict(float)
            for order in orders:
                date = order.created_at.date()
                daily_sales[date] += order.total_amount or 0

            sales_values = list(daily_sales.values())
            avg_daily_sales = np.mean(sales_values) if sales_values else 0
            sales_trend = self._calculate_trend(sales_values)

            return {
                'total_orders': len(orders),
                'total_sales': sum(sales_values),
                'avg_daily_sales': avg_daily_sales,
                'sales_trend': sales_trend,
                'daily_sales': dict(daily_sales)
            }

        except Exception as e:
            logger.error(f"매출 상태 분석 실패: {e}")
            return {}

    def _analyze_customer_state(self) -> Dict[str, Any]:
        """고객 상태 분석"""
        try:
            customers = db.session.query(User).filter(
                User.role == 'customer'
            ).all()

            # 고객 행동 분석
            customer_orders = defaultdict(list)
            for customer in customers:
                orders = db.session.query(Order).filter(
                    Order.user_id == customer.id
                ).order_by(Order.created_at.desc()).all()
                customer_orders[customer.id] = orders

            # 이탈 위험 고객 식별
            churn_risk_customers = []
            for customer_id, orders in customer_orders.items():
                if orders:
                    last_order_date = orders[0].created_at
                    days_since_last_order = (datetime.now() - last_order_date).days

                    if days_since_last_order > 30:
                        churn_risk_customers.append({
                            'customer_id': customer_id,
                            'days_since_last_order': days_since_last_order,
                            'total_orders': len(orders),
                            'total_spent': sum(o.total_amount or 0 for o in orders)
                        })

            return {
                'total_customers': len(customers),
                'churn_risk_count': len(churn_risk_customers),
                'churn_risk_customers': churn_risk_customers,
                'avg_orders_per_customer': len(customer_orders) / len(customers) if customers else 0
            }

        except Exception as e:
            logger.error(f"고객 상태 분석 실패: {e}")
            return {}

    def _analyze_operations_state(self) -> Dict[str, Any]:
        """운영 상태 분석"""
        try:
            # 스케줄 분석
            schedules = db.session.query(Schedule).filter(
                Schedule.work_date >= datetime.now().date()
            ).all()

            total_required = sum(s.required_staff or 0 for s in schedules)
            total_actual = sum(s.actual_staff or 0 for s in schedules)
            efficiency_ratio = total_actual / total_required if total_required > 0 else 1.0

            return {
                'total_schedules': len(schedules),
                'total_required_staff': total_required,
                'total_actual_staff': total_actual,
                'efficiency_ratio': efficiency_ratio,
                'staffing_gap': total_required - total_actual
            }

        except Exception as e:
            logger.error(f"운영 상태 분석 실패: {e}")
            return {}

    def _evaluate_conditions(self, conditions: List[Dict[str, Any]], business_state: Optional[Dict[str, Any]]) -> bool:
        """조건 평가"""
        try:
            for condition in conditions:
                metric = condition['metric']
                operator = condition['operator']
                value = condition['value']
                threshold = condition.get('threshold', 0.5)

                # 메트릭 값 추출
                metric_value = self._extract_metric_value(metric, business_state)

                # 조건 평가
                if not self._evaluate_condition(metric_value, operator, value, threshold):
                    return False

            return True

        except Exception as e:
            logger.error(f"조건 평가 실패: {e}")
            return False

    def _extract_metric_value(self, metric: str, business_state: Optional[Dict[str, Any]]) -> Any:
        """메트릭 값 추출"""
        try:
            if not business_state:
                return 0
            if metric == 'current_stock':
                return business_state.get('inventory', {}).get('low_stock_count', 0)
            elif metric == 'reorder_point':
                return 5  # 임계값
            elif metric == 'demand_trend':
                return business_state.get('sales', {}).get('sales_trend', 0)
            elif metric == 'competitor_price':
                return 10000  # 시뮬레이션
            elif metric == 'our_price':
                return 12000  # 시뮬레이션
            elif metric == 'predicted_demand':
                return business_state.get('sales', {}).get('avg_daily_sales', 0)
            elif metric == 'current_staff_capacity':
                return business_state.get('operations', {}).get('total_actual_staff', 0)
            elif metric == 'customer_churn_risk':
                return business_state.get('customer', {}).get('churn_risk_count', 0)
            else:
                return 0
        except Exception as e:
            logger.error(f"메트릭 값 추출 실패: {e}")
            return 0

    def _evaluate_condition(self, metric_value: Any, operator: str, value: Any, threshold: float) -> bool:
        """단일 조건 평가"""
        try:
            if operator == '<':
                return metric_value < value
            elif operator == '>':
                return metric_value > value
            elif operator == '==':
                return metric_value == value
            elif operator == '>=':
                return metric_value >= value
            elif operator == '<=':
                return metric_value <= value
            else:
                return False

        except Exception as e:
            logger.error(f"조건 평가 실패: {e}")
            return False

    def _create_decision(self, rule: 'DecisionRule', business_state: Optional[Dict[str, Any]]) -> 'AutomatedDecision':
        """의사결정 생성"""
        try:
            decision_id = f"decision_{rule.rule_id}_{int(time.time())}"
            decision_result = self._calculate_decision_result(rule, business_state)
            decision = AutomatedDecision(
                decision_id=decision_id,
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                trigger_data=business_state,
                decision_result=decision_result,
                confidence=decision_result.get('confidence', 0.5) if decision_result else 0.5,
                executed_actions=[],
                status='pending',
                created_at=datetime.now(),
                completed_at=None
            )
            self.active_decisions[decision_id] = decision
            return decision
        except Exception as e:
            logger.error(f"의사결정 생성 실패: {e}")
            return None

    def _calculate_decision_result(self, rule: 'DecisionRule', business_state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """의사결정 결과 계산"""
        try:
            result = {
                'confidence': 0.8,
                'estimated_impact': {},
                'recommended_actions': []
            }
            if rule.category == 'inventory':
                result.update(self._calculate_inventory_decision(rule, business_state))
            elif rule.category == 'pricing':
                result.update(self._calculate_pricing_decision(rule, business_state))
            elif rule.category == 'staffing':
                result.update(self._calculate_staffing_decision(rule, business_state))
            elif rule.category == 'marketing':
                result.update(self._calculate_marketing_decision(rule, business_state))
            return result
        except Exception as e:
            logger.error(f"의사결정 결과 계산 실패: {e}")
            return {'confidence': 0.5, 'estimated_impact': {}, 'recommended_actions': []}

    def _calculate_inventory_decision(self, rule: 'DecisionRule', business_state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """재고 의사결정 계산"""
        try:
            inventory_state = business_state.get('inventory', {}) if business_state else {}
            low_stock_items = inventory_state.get('low_stock_items', []) if inventory_state else []
            total_order_value = sum(
                item.get('reorder_quantity', 0) * 1000  # 단가 시뮬레이션
                for item in low_stock_items if item is not None
            )
            return {
                'confidence': 0.9,
                'estimated_impact': {
                    'order_value': total_order_value,
                    'items_to_order': len(low_stock_items),
                    'stockout_prevention': True
                },
                'recommended_actions': [
                    f'{len(low_stock_items)}개 품목 재주문',
                    '긴급 배송 요청',
                    '대체 공급업체 검토'
                ]
            }
        except Exception as e:
            logger.error(f"재고 의사결정 계산 실패: {e}")
            return {}

    def _calculate_pricing_decision(self, rule: 'DecisionRule', business_state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """가격 의사결정 계산"""
        try:
            sales_state = business_state.get('sales', {}) if business_state else {}
            sales_trend = sales_state.get('sales_trend', 0) if sales_state else 0
            price_increase = 0.05
            estimated_revenue_impact = sales_state.get('avg_daily_sales', 0) * price_increase * 30
            return {
                'confidence': 0.7,
                'estimated_impact': {
                    'price_increase': price_increase,
                    'revenue_impact': estimated_revenue_impact,
                    'customer_impact': 'low'
                },
                'recommended_actions': [
                    '단계적 가격 인상',
                    '프리미엄 메뉴 강화',
                    '고객 커뮤니케이션'
                ]
            }
        except Exception as e:
            logger.error(f"가격 의사결정 계산 실패: {e}")
            return {}

    def _calculate_staffing_decision(self, rule: 'DecisionRule', business_state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """인력 의사결정 계산"""
        try:
            operations_state = business_state.get('operations', {}) if business_state else {}
            staffing_gap = operations_state.get('staffing_gap', 0) if operations_state else 0
            hourly_wage = 15000
            additional_cost = staffing_gap * 8 * hourly_wage * 30
            return {
                'confidence': 0.8,
                'estimated_impact': {
                    'staffing_gap': staffing_gap,
                    'additional_cost': additional_cost,
                    'service_improvement': True
                },
                'recommended_actions': [
                    f'{staffing_gap}명 추가 인력 배치',
                    '시간당 인력 조정',
                    '업무 효율성 개선'
                ]
            }
        except Exception as e:
            logger.error(f"인력 의사결정 계산 실패: {e}")
            return {}

    def _calculate_marketing_decision(self, rule: 'DecisionRule', business_state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """마케팅 의사결정 계산"""
        try:
            customer_state = business_state.get('customer', {}) if business_state else {}
            churn_risk_count = customer_state.get('churn_risk_count', 0) if customer_state else 0
            # 캠페인 비용 및 효과 추정
            campaign_cost = churn_risk_count * 5000  # 고객당 5,000원
            estimated_retention = churn_risk_count * 0.3  # 30% 유지율
            revenue_impact = estimated_retention * 50000  # 고객당 5만원 매출

            return {
                'confidence': 0.6,
                'estimated_impact': {
                    'campaign_cost': campaign_cost,
                    'estimated_retention': estimated_retention,
                    'revenue_impact': revenue_impact,
                    'roi': (revenue_impact - campaign_cost) / campaign_cost if campaign_cost > 0 else 0
                },
                'recommended_actions': [
                    '개인화된 할인 쿠폰 발송',
                    '고객 만족도 조사',
                    '로열티 프로그램 강화'
                ]
            }
        except Exception as e:
            logger.error(f"마케팅 의사결정 계산 실패: {e}")
            return {}

    def _execute_decision(self, decision: AutomatedDecision):
        """의사결정 실행"""
        try:
            if not decision:
                return

            decision.status = 'executing'

            # 신뢰도 체크
            if decision.confidence < self.system_config['approval_threshold']:
                # 수동 승인 필요
                self._request_manual_approval(decision)
                return

            # 액션 실행
            for action in decision.decision_result.get('recommended_actions', []):
                business_action = self._create_business_action(decision, action)
                if business_action:
                    self.action_queue.append(business_action)

            decision.status = 'completed'
            decision.completed_at = datetime.now()

            # 로그 기록
            self._log_decision_execution(decision)

        except Exception as e:
            logger.error(f"의사결정 실행 실패: {e}")
            decision.status = 'failed'

    def _create_business_action(self, decision: AutomatedDecision, action: str) -> BusinessAction:
        """비즈니스 액션 생성"""
        try:
            action_id = f"action_{decision.decision_id}_{int(time.time())}"

            # 액션 타입 결정
            action_type = self._determine_action_type(action)

            # 파라미터 추출
            parameters = self._extract_action_parameters(action, decision)

            # 비용 추정
            cost = self._estimate_action_cost(action_type, parameters)

            business_action = BusinessAction(
                action_id=action_id,
                action_type=action_type,
                parameters=parameters,
                estimated_impact=decision.decision_result.get('estimated_impact', {}),
                cost=cost,
                priority='medium',
                status='pending',
                created_at=datetime.now(),
                executed_at=None
            )

            return business_action

        except Exception as e:
            logger.error(f"비즈니스 액션 생성 실패: {e}")
            return None

    def _determine_action_type(self, action: str) -> str:
        """액션 타입 결정"""
        if '재주문' in action or '주문' in action:
            return 'inventory_order'
        elif '가격' in action or '인상' in action:
            return 'price_adjustment'
        elif '인력' in action or '배치' in action:
            return 'staff_schedule'
        elif '캠페인' in action or '쿠폰' in action:
            return 'marketing_campaign'
        else:
            return 'general_action'

    def _extract_action_parameters(self, action: str, decision: AutomatedDecision) -> Dict[str, Any]:
        """액션 파라미터 추출"""
        try:
            parameters = {'action_description': action}

            if decision.category == 'inventory':
                inventory_state = decision.trigger_data.get('inventory', {}) if decision.trigger_data else {}
                parameters.update({
                    'items_to_order': inventory_state.get('low_stock_items', []),
                    'priority': 'high'
                })
            elif decision.category == 'pricing':
                parameters.update({
                    'adjustment_type': 'increase',
                    'percentage': 0.05
                })
            elif decision.category == 'staffing':
                operations_state = decision.trigger_data.get('operations', {}) if decision.trigger_data else {}
                parameters.update({
                    'staffing_gap': operations_state.get('staffing_gap', 0),
                    'duration': 'immediate'
                })
            elif decision.category == 'marketing':
                customer_state = decision.trigger_data.get('customer', {}) if decision.trigger_data else {}
                parameters.update({
                    'target_customers': customer_state.get('churn_risk_customers', []),
                    'campaign_type': 'retention'
                })

            return parameters

        except Exception as e:
            logger.error(f"액션 파라미터 추출 실패: {e}")
            return {'action_description': action}

    def _estimate_action_cost(self, action_type: str, parameters: Dict[str, Any]) -> float:
        """액션 비용 추정"""
        try:
            if action_type == 'inventory_order':
                items = parameters.get('items_to_order', [])
                return sum(item.get('reorder_quantity', 0) * 1000 for item in items)
            elif action_type == 'price_adjustment':
                return 0  # 가격 조정은 직접 비용 없음
            elif action_type == 'staff_schedule':
                staffing_gap = parameters.get('staffing_gap', 0)
                return staffing_gap * 8 * 15000 * 30  # 월 비용
            elif action_type == 'marketing_campaign':
                target_customers = parameters.get('target_customers', [])
                return len(target_customers) * 5000  # 고객당 5,000원
            else:
                return 0

        except Exception as e:
            logger.error(f"액션 비용 추정 실패: {e}")
            return 0

    def _request_manual_approval(self, decision: AutomatedDecision):
        """수동 승인 요청"""
        try:
            notification = Notification(
                user_id=1,  # 관리자
                title=f'의사결정 승인 요청 - {decision.rule_name}',
                message=f'신뢰도 {decision.confidence*100:.1f}%로 수동 승인이 필요합니다.',
                type='decision_approval',
                priority='high',
                data=json.dumps(asdict(decision))
            )

            db.session.add(notification)
            db.session.commit()

            logger.info(f"수동 승인 요청: {decision.decision_id}")

        except Exception as e:
            logger.error(f"수동 승인 요청 실패: {e}")

    def _execute_pending_actions(self):
        """대기 중인 액션 실행"""
        try:
            # 실행 가능한 액션 수 제한
            max_actions = self.system_config['max_concurrent_actions']
            actions_to_execute = self.action_queue[:max_actions]

            for action in actions_to_execute:
                try:
                    self._execute_business_action(action)
                    self.action_queue.remove(action)
                except Exception as e:
                    logger.error(f"액션 실행 실패 {action.action_id}: {e}")
                    action.status = 'failed'

        except Exception as e:
            logger.error(f"대기 중인 액션 실행 실패: {e}")

    def _execute_business_action(self, action: BusinessAction):
        """비즈니스 액션 실행"""
        try:
            action.status = 'executing'

            # 액션 타입별 실행
            if action.action_type == 'inventory_order':
                self._execute_inventory_order(action)
            elif action.action_type == 'price_adjustment':
                self._execute_price_adjustment(action)
            elif action.action_type == 'staff_schedule':
                self._execute_staff_schedule(action)
            elif action.action_type == 'marketing_campaign':
                self._execute_marketing_campaign(action)

            action.status = 'executed'
            action.executed_at = datetime.now()

            # 실행 로그 기록
            self._log_action_execution(action)

        except Exception as e:
            logger.error(f"비즈니스 액션 실행 실패: {e}")
            action.status = 'failed'

    def _execute_inventory_order(self, action: BusinessAction):
        """재고 주문 실행"""
        try:
            items = action.parameters.get('items_to_order', [])

            for item in items:
                # 실제 주문 로직 (시뮬레이션)
                logger.info(f"재고 주문 실행: {item['name']} - {item['reorder_quantity']}개")

                # 알림 전송
                notification = Notification(
                    user_id=1,
                    title=f"자동 재고 주문 - {item['name']}",
                    message=f"{item['name']} {item['reorder_quantity']}개 자동 주문이 실행되었습니다.",
                    type='inventory_order',
                    priority='medium'
                )
                db.session.add(notification)

            db.session.commit()

        except Exception as e:
            logger.error(f"재고 주문 실행 실패: {e}")

    def _execute_price_adjustment(self, action: BusinessAction):
        """가격 조정 실행"""
        try:
            adjustment_type = action.parameters.get('adjustment_type', 'increase')
            percentage = action.parameters.get('percentage', 0.05)

            logger.info(f"가격 조정 실행: {adjustment_type} {percentage*100}%")

            # 알림 전송
            notification = Notification(
                user_id=1,
                title="자동 가격 조정",
                message=f"가격이 {adjustment_type} {percentage*100}% 조정되었습니다.",
                type='price_adjustment',
                priority='medium'
            )
            db.session.add(notification)
            db.session.commit()

        except Exception as e:
            logger.error(f"가격 조정 실행 실패: {e}")

    def _execute_staff_schedule(self, action: BusinessAction):
        """인력 스케줄 실행"""
        try:
            staffing_gap = action.parameters.get('staffing_gap', 0)

            logger.info(f"인력 스케줄 조정: {staffing_gap}명 추가")

            # 알림 전송
            notification = Notification(
                user_id=1,
                title="자동 인력 스케줄 조정",
                message=f"{staffing_gap}명의 추가 인력이 배치되었습니다.",
                type='staff_schedule',
                priority='medium'
            )
            db.session.add(notification)
            db.session.commit()

        except Exception as e:
            logger.error(f"인력 스케줄 실행 실패: {e}")

    def _execute_marketing_campaign(self, action: BusinessAction):
        """마케팅 캠페인 실행"""
        try:
            target_customers = action.parameters.get('target_customers', [])
            campaign_type = action.parameters.get('campaign_type', 'retention')

            logger.info(f"마케팅 캠페인 실행: {campaign_type} - {len(target_customers)}명 대상")

            # 알림 전송
            notification = Notification(
                user_id=1,
                title="자동 마케팅 캠페인",
                message=f"{campaign_type} 캠페인이 {len(target_customers)}명에게 실행되었습니다.",
                type='marketing_campaign',
                priority='medium'
            )
            db.session.add(notification)
            db.session.commit()

        except Exception as e:
            logger.error(f"마케팅 캠페인 실행 실패: {e}")

    def _log_decision_execution(self, decision: AutomatedDecision):
        """의사결정 실행 로그"""
        try:
            system_log = SystemLog(
                level='info',
                message=f'자동화된 의사결정 실행: {decision.rule_name}',
                category='automated_decision',
                data=json.dumps(asdict(decision))
            )
            db.session.add(system_log)
            db.session.commit()

        except Exception as e:
            logger.error(f"의사결정 로그 기록 실패: {e}")

    def _log_action_execution(self, action: BusinessAction):
        """액션 실행 로그"""
        try:
            system_log = SystemLog(
                level='info',
                message=f'비즈니스 액션 실행: {action.action_type}',
                category='business_action',
                data=json.dumps(asdict(action))
            )
            db.session.add(system_log)
            db.session.commit()

        except Exception as e:
            logger.error(f"액션 로그 기록 실패: {e}")

    def _cleanup_completed_decisions(self):
        """완료된 의사결정 정리"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)

            completed_decisions = [
                decision_id for decision_id, decision in self.active_decisions.items()
                if decision.status in ['completed', 'failed'] and decision.created_at < cutoff_time
            ]

            for decision_id in completed_decisions:
                del self.active_decisions[decision_id]

        except Exception as e:
            logger.error(f"완료된 의사결정 정리 실패: {e}")

    def _calculate_trend(self, values: List[float]) -> float:
        """트렌드 계산"""
        if len(values) < 2:
            return 0.0

        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        return slope / np.mean(values) if np.mean(values) > 0 else 0.0

    def get_decision_status(self) -> Dict[str, Any]:
        """의사결정 상태 조회"""
        try:
            return {
                'success': True,
                'active_decisions': len(self.active_decisions),
                'pending_actions': len(self.action_queue),
                'system_config': self.system_config,
                'recent_decisions': [
                    {
                        'decision_id': decision.decision_id,
                        'rule_name': decision.rule_name,
                        'category': decision.category,
                        'status': decision.status,
                        'confidence': decision.confidence,
                        'created_at': decision.created_at.isoformat()
                    }
                    for decision in list(self.active_decisions.values())[-10:]  # 최근 10개
                ],
                'action_queue_summary': {
                    'total_actions': len(self.action_queue),
                    'action_types': Counter(action.action_type for action in self.action_queue)
                }
            }

        except Exception as e:
            logger.error(f"의사결정 상태 조회 실패: {e}")
            return {'error': f'상태 조회 실패: {str(e)}'}


# 전역 서비스 인스턴스
automated_decision_service = AutomatedDecisionSystem()

# API 엔드포인트들


@automated_decision_bp.route('/api/automated-decision/status', methods=['GET'])
@login_required
def get_decision_status():
    """의사결정 상태 조회"""
    try:
        result = automated_decision_service.get_decision_status()
        return jsonify(result)
    except Exception as e:
        logger.error(f"의사결정 상태 조회 API 오류: {e}")
        return jsonify({'error': '상태 조회에 실패했습니다.'}), 500


@automated_decision_bp.route('/api/automated-decision/rules', methods=['GET'])
@login_required
def get_decision_rules():
    """의사결정 규칙 조회"""
    try:
        rules = [
            {
                'rule_id': rule.rule_id,
                'name': rule.name,
                'category': rule.category,
                'conditions': rule.conditions,
                'actions': rule.actions,
                'priority': rule.priority,
                'is_active': rule.is_active,
                'created_at': rule.created_at.isoformat(),
                'last_executed': rule.last_executed.isoformat() if rule.last_executed else None
            }
            for rule in automated_decision_service.decision_rules.values()
        ]

        return jsonify({
            'success': True,
            'rules': rules,
            'total_rules': len(rules)
        })

    except Exception as e:
        logger.error(f"의사결정 규칙 조회 API 오류: {e}")
        return jsonify({'error': '규칙 조회에 실패했습니다.'}), 500


@automated_decision_bp.route('/api/automated-decision/rules/<rule_id>/toggle', methods=['POST'])
@login_required
def toggle_decision_rule(rule_id):
    """의사결정 규칙 활성화/비활성화"""
    try:
        if rule_id in automated_decision_service.decision_rules:
            rule = automated_decision_service.decision_rules[rule_id]
            rule.is_active = not rule.is_active

            return jsonify({
                'success': True,
                'message': f'규칙이 {"활성화" if rule.is_active else "비활성화"}되었습니다.',
                'is_active': rule.is_active
            })
        else:
            return jsonify({'error': '규칙을 찾을 수 없습니다.'}), 404

    except Exception as e:
        logger.error(f"의사결정 규칙 토글 API 오류: {e}")
        return jsonify({'error': '규칙 토글에 실패했습니다.'}), 500
