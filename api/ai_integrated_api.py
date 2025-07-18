from .system_monitoring_advanced import get_system_status, set_monitoring_threshold  # pyright: ignore
from .ai_enhanced_features import (  # pyright: ignore
    predict_sales_forecast,
    predict_inventory_requirements,
    analyze_customer_behavior_patterns,
    process_natural_language
)
from .performance_optimization import get_performance_metrics, cache_result, run_async  # pyright: ignore
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, current_app
args = None  # pyright: ignore
form = None  # pyright: ignore
"""
통합 AI API 엔드포인트
모든 AI 기능을 하나의 API로 통합
"""


# AI 모듈들 import

logger = logging.getLogger(__name__)

ai_integrated_bp = Blueprint('ai_integrated', __name__)


class IntegratedAIService:
    """통합 AI 서비스 클래스"""

    def __init__(self):
        self.cache_enabled = True
        self.rate_limits = {
            'predictions': 100,  # 시간당 100회
            'analysis': 200,     # 시간당 200회
            'monitoring': 50     # 시간당 50회
        }
        self.request_counts = {}

    def analyze_business_data(self, data_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """비즈니스 데이터 종합 분석"""
        try:
            analysis_result: Dict[str, Any] = {
                'timestamp': datetime.now().isoformat(),
                'data_type': data_type,
                'analysis': {},
                'recommendations': []
            }

            analysis: Dict[str, Any] = analysis_result['analysis']
            if data_type == 'sales':
                # 매출 데이터 분석
                if 'historical_data' in data:
                    sales_forecast = predict_sales_forecast(
                        data['historical_data'],
                        data.get('forecast_days', 30)
                    )
                    analysis['sales_forecast'] = sales_forecast
                # 고객 행동 분석
                if 'customer_data' in data:
                    customer_analysis = analyze_customer_behavior_patterns(data['customer_data'])
                    analysis['customer_behavior'] = customer_analysis
            elif data_type == 'inventory':
                # 재고 분석
                if 'sales_data' in data and 'current_inventory' in data:
                    inventory_analysis = predict_inventory_requirements(
                        data['sales_data'],
                        data['current_inventory'],
                        data.get('lead_time_days', 7)
                    )
                    analysis['inventory_needs'] = inventory_analysis
            elif data_type == 'feedback':
                # 고객 피드백 분석
                if 'feedback_text' in data:
                    nlp_analysis = process_natural_language(
                        data['feedback_text'],
                        data.get('task', 'sentiment')
                    )
                    analysis['nlp_analysis'] = nlp_analysis
            elif data_type == 'performance':
                # 성능 분석
                performance_metrics = get_performance_metrics()
                analysis['performance'] = performance_metrics
            elif data_type == 'system':
                # 시스템 상태 분석
                system_status = get_system_status()
                analysis['system_status'] = system_status
            else:
                return {'error': f'지원하지 않는 데이터 타입: {data_type}'}

            # 종합 권장사항 생성
            analysis_result['recommendations'] = self._generate_recommendations(
                data_type, analysis
            )
            return analysis_result
        except Exception as e:
            logger.error(f"비즈니스 데이터 분석 오류: {e}")
            return {'error': f'분석 중 오류 발생: {str(e)}'}

    def get_comprehensive_dashboard(self) -> Dict[str, Any]:
        """종합 대시보드 데이터"""
        try:
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'performance': get_performance_metrics(),
                'system_status': get_system_status(),
                'ai_insights': self._generate_ai_insights(),
                'alerts': self._get_active_alerts(),
                'recommendations': self._get_system_recommendations()
            }

            return dashboard_data

        except Exception as e:
            logger.error(f"종합 대시보드 생성 오류: {e}")
            return {'error': f'대시보드 생성 중 오류 발생: {str(e)}'}

    def execute_ai_workflow(self, workflow_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """AI 워크플로우 실행"""
        try:
            if workflow_type == 'sales_optimization':
                return self._execute_sales_optimization_workflow(parameters)
            elif workflow_type == 'inventory_management':
                return self._execute_inventory_management_workflow(parameters)
            elif workflow_type == 'customer_retention':
                return self._execute_customer_retention_workflow(parameters)
            elif workflow_type == 'system_optimization':
                return self._execute_system_optimization_workflow(parameters)
            else:
                return {'error': f'지원하지 않는 워크플로우: {workflow_type}'}

        except Exception as e:
            logger.error(f"AI 워크플로우 실행 오류: {e}")
            return {'error': f'워크플로우 실행 중 오류 발생: {str(e)}'}

    def _generate_recommendations(self, data_type: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """권장사항 생성"""
        recommendations = []

        try:
            if data_type == 'sales':
                # 매출 관련 권장사항
                if 'sales_forecast' in analysis:
                    forecast = analysis['sales_forecast']
                    if 'total_predicted_sales' in forecast:
                        predicted_sales = forecast['total_predicted_sales']
                        if predicted_sales > 10000:
                            recommendations.append({
                                'type': 'positive',
                                'title': '매출 예측 긍정적',
                                'description': f'향후 30일 매출이 {predicted_sales:,.0f}원으로 예측됩니다.',
                                'priority': 'medium',
                                'action': 'marketing_boost'
                            })
                        else:
                            recommendations.append({
                                'type': 'warning',
                                'title': '매출 개선 필요',
                                'description': '매출 예측이 낮습니다. 마케팅 전략 재검토가 필요합니다.',
                                'priority': 'high',
                                'action': 'review_strategy'
                            })

                if 'customer_behavior' in analysis:
                    behavior = analysis['customer_behavior']
                    if 'churn_risk' in behavior:
                        high_risk = behavior['churn_risk'].get('high_risk_customers', 0)
                        if high_risk > 10:
                            recommendations.append({
                                'type': 'critical',
                                'title': '고객 이탈 위험',
                                'description': f'{high_risk}명의 고객이 이탈 위험에 있습니다.',
                                'priority': 'critical',
                                'action': 'customer_retention_campaign'
                            })

            elif data_type == 'inventory':
                # 재고 관련 권장사항
                if 'inventory_needs' in analysis:
                    inventory = analysis['inventory_needs']
                    if 'total_reorder_value' in inventory:
                        reorder_value = inventory['total_reorder_value']
                        if reorder_value > 500000:
                            recommendations.append({
                                'type': 'warning',
                                'title': '대량 재고 주문 필요',
                                'description': f'{reorder_value:,.0f}원 상당의 재고 주문이 필요합니다.',
                                'priority': 'high',
                                'action': 'place_order'
                            })

            elif data_type == 'performance':
                # 성능 관련 권장사항
                if 'performance' in analysis:
                    perf = analysis['performance']
                    if 'memory_usage' in perf:
                        memory_usage = perf['memory_usage']['percent']
                        if memory_usage > 80:
                            recommendations.append({
                                'type': 'warning',
                                'title': '메모리 사용률 높음',
                                'description': f'메모리 사용률이 {memory_usage}%입니다.',
                                'priority': 'medium',
                                'action': 'optimize_memory'
                            })

            elif data_type == 'system':
                # 시스템 관련 권장사항
                if 'system_status' in analysis:
                    system = analysis['system_status']
                    if 'anomalies' in system:
                        anomalies = system['anomalies']
                        if anomalies.get('total_anomalies', 0) > 0:
                            recommendations.append({
                                'type': 'critical',
                                'title': '시스템 이상 감지',
                                'description': f'{anomalies["total_anomalies"]}개의 이상이 감지되었습니다.',
                                'priority': 'critical',
                                'action': 'system_maintenance'
                            })

        except Exception as e:
            logger.error(f"권장사항 생성 오류: {e}")
            recommendations.append({
                'type': 'error',
                'title': '권장사항 생성 실패',
                'description': '권장사항 생성 중 오류가 발생했습니다.',
                'priority': 'low',
                'action': 'none'
            })

        return recommendations

    def _generate_ai_insights(self) -> Dict[str, Any]:
        """AI 인사이트 생성"""
        try:
            insights = {
                'business_health': 'good',
                'key_metrics': {},
                'trends': {},
                'predictions': {}
            }

            # 성능 메트릭 분석
            perf_metrics = get_performance_metrics()
            if 'memory_usage' in perf_metrics:
                memory_usage = perf_metrics['memory_usage']['percent']
                insights['key_metrics']['memory_usage'] = memory_usage
                insights['business_health'] = 'warning' if memory_usage > 80 else 'good'

            # 시스템 상태 분석
            system_status = get_system_status()
            if 'anomalies' in system_status:
                anomalies = system_status['anomalies']
                insights['key_metrics']['anomalies'] = anomalies.get('total_anomalies', 0)
                if anomalies.get('total_anomalies', 0) > 0:
                    insights['business_health'] = 'critical'

            return insights

        except Exception as e:
            logger.error(f"AI 인사이트 생성 오류: {e}")
            return {'error': str(e)}

    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """활성 알림 조회"""
        try:
            alerts = []

            # 시스템 상태 확인
            system_status = get_system_status()
            if 'anomalies' in system_status:
                anomalies = system_status['anomalies']
                for anomaly in anomalies.get('anomalies', []) if anomalies else []:
                    alerts.append({
                        'type': anomaly['type'],
                        'severity': anomaly['severity'],
                        'message': f"{anomaly['type']}: {anomaly['value']}%",
                        'timestamp': anomaly['timestamp']
                    })

            return alerts

        except Exception as e:
            logger.error(f"활성 알림 조회 오류: {e}")
            return []

    def _get_system_recommendations(self) -> List[Dict[str, Any]]:
        """시스템 권장사항 조회"""
        try:
            recommendations = []

            # 성능 메트릭 기반 권장사항
            perf_metrics = get_performance_metrics()
            if 'memory_usage' in perf_metrics:
                memory_usage = perf_metrics['memory_usage']['percent']
                if memory_usage > 85:
                    recommendations.append({
                        'type': 'performance',
                        'title': '메모리 최적화 필요',
                        'description': '메모리 사용률이 높습니다. 캐시 정리나 메모리 최적화를 고려하세요.',
                        'priority': 'high'
                    })

            # 시스템 상태 기반 권장사항
            system_status = get_system_status()
            if 'health_checks' in system_status:
                health_checks = system_status['health_checks']
                for check_name, check_result in health_checks.items():
                    if check_result.get('status') == 'unhealthy':
                        recommendations.append({
                            'type': 'system',
                            'title': f'{check_name} 상태 불량',
                            'description': f'{check_name} 서비스에 문제가 있습니다.',
                            'priority': 'critical'
                        })

            return recommendations

        except Exception as e:
            logger.error(f"시스템 권장사항 조회 오류: {e}")
            return []

    def _execute_sales_optimization_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """매출 최적화 워크플로우"""
        try:
            workflow_result: Dict[str, Any] = {
                'workflow_type': 'sales_optimization',
                'timestamp': datetime.now().isoformat(),
                'steps': []
            }

            # 1단계: 매출 예측
            if 'historical_data' in parameters:
                sales_forecast = predict_sales_forecast(
                    parameters['historical_data'],
                    parameters.get('forecast_days', 30)
                )
                workflow_result['steps'].append({
                    'step': 'sales_forecast',
                    'result': sales_forecast
                })

            # 2단계: 고객 행동 분석
            if 'customer_data' in parameters:
                customer_analysis = analyze_customer_behavior_patterns(parameters['customer_data'])
                workflow_result['steps'].append({
                    'step': 'customer_analysis',
                    'result': customer_analysis
                })

            # 3단계: 최적화 권장사항
            optimization_recommendations = self._generate_sales_optimization_recommendations(
                workflow_result['steps']
            )
            workflow_result['steps'].append({
                'step': 'optimization_recommendations',
                'result': optimization_recommendations
            })

            return workflow_result

        except Exception as e:
            logger.error(f"매출 최적화 워크플로우 오류: {e}")
            return {'error': str(e)}

    def _execute_inventory_management_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """재고 관리 워크플로우"""
        try:
            workflow_result: Dict[str, Any] = {
                'workflow_type': 'inventory_management',
                'timestamp': datetime.now().isoformat(),
                'steps': []
            }

            # 1단계: 재고 필요량 예측
            if 'sales_data' in parameters and 'current_inventory' in parameters:
                inventory_analysis = predict_inventory_requirements(
                    parameters['sales_data'],
                    parameters['current_inventory'],
                    parameters.get('lead_time_days', 7)
                )
                workflow_result['steps'].append({
                    'step': 'inventory_analysis',
                    'result': inventory_analysis
                })

            # 2단계: 재고 최적화 권장사항
            inventory_recommendations = self._generate_inventory_recommendations(
                workflow_result['steps']
            )
            workflow_result['steps'].append({
                'step': 'inventory_recommendations',
                'result': inventory_recommendations
            })

            return workflow_result

        except Exception as e:
            logger.error(f"재고 관리 워크플로우 오류: {e}")
            return {'error': str(e)}

    def _execute_customer_retention_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """고객 유지 워크플로우"""
        try:
            workflow_result: Dict[str, Any] = {
                'workflow_type': 'customer_retention',
                'timestamp': datetime.now().isoformat(),
                'steps': []
            }

            # 1단계: 고객 행동 분석
            if 'customer_data' in parameters:
                customer_analysis = analyze_customer_behavior_patterns(parameters['customer_data'])
                workflow_result['steps'].append({
                    'step': 'customer_analysis',
                    'result': customer_analysis
                })

            # 2단계: 이탈 위험 고객 식별
            churn_analysis = self._analyze_churn_risk(parameters.get('customer_data', []))
            workflow_result['steps'].append({
                'step': 'churn_analysis',
                'result': churn_analysis
            })

            # 3단계: 고객 유지 전략
            retention_strategy = self._generate_retention_strategy(workflow_result['steps'])
            workflow_result['steps'].append({
                'step': 'retention_strategy',
                'result': retention_strategy
            })

            return workflow_result

        except Exception as e:
            logger.error(f"고객 유지 워크플로우 오류: {e}")
            return {'error': str(e)}

    def _execute_system_optimization_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """시스템 최적화 워크플로우"""
        try:
            workflow_result: Dict[str, Any] = {
                'workflow_type': 'system_optimization',
                'timestamp': datetime.now().isoformat(),
                'steps': []
            }

            # 1단계: 시스템 상태 분석
            system_status = get_system_status()
            workflow_result['steps'].append({
                'step': 'system_analysis',
                'result': system_status
            })

            # 2단계: 성능 메트릭 분석
            performance_metrics = get_performance_metrics()
            workflow_result['steps'].append({
                'step': 'performance_analysis',
                'result': performance_metrics
            })

            # 3단계: 최적화 권장사항
            optimization_recommendations = self._generate_system_optimization_recommendations(
                workflow_result['steps']
            )
            workflow_result['steps'].append({
                'step': 'optimization_recommendations',
                'result': optimization_recommendations
            })

            return workflow_result

        except Exception as e:
            logger.error(f"시스템 최적화 워크플로우 오류: {e}")
            return {'error': str(e)}

    def _generate_sales_optimization_recommendations(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """매출 최적화 권장사항 생성"""
        recommendations = []

        for step in steps:
            if step['step'] == 'sales_forecast':
                forecast = step['result']
                if 'total_predicted_sales' in forecast:
                    predicted_sales = forecast['total_predicted_sales']
                    if predicted_sales < 5000:
                        recommendations.append({
                            'type': 'warning',
                            'title': '매출 개선 필요',
                            'description': f'예측 매출이 {predicted_sales:,.0f}원으로 낮습니다.',
                            'priority': 'high',
                            'action': 'marketing_boost'
                        })

            elif step['step'] == 'customer_analysis':
                analysis = step['result']
                if 'churn_risk' in analysis:
                    churn = analysis['churn_risk']
                    high_risk = churn.get('high_risk_customers', 0)
                    if high_risk > 5:
                        recommendations.append({
                            'type': 'critical',
                            'title': '고객 이탈 위험',
                            'description': f'{high_risk}명의 고객이 이탈 위험에 있습니다.',
                            'priority': 'critical',
                            'action': 'customer_retention_campaign'
                        })

        return recommendations

    def _generate_inventory_recommendations(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """재고 권장사항 생성"""
        recommendations = []

        for step in steps:
            if step['step'] == 'inventory_analysis':
                analysis = step['result']
                if 'total_reorder_value' in analysis:
                    reorder_value = analysis['total_reorder_value']
                    if reorder_value > 100000:
                        recommendations.append({
                            'type': 'warning',
                            'title': '대량 주문 필요',
                            'description': f'{reorder_value:,.0f}원 상당의 재고 주문이 필요합니다.',
                            'priority': 'high',
                            'action': 'place_order'
                        })

        return recommendations

    def _analyze_churn_risk(self, customer_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """이탈 위험 분석"""
        try:
            if not customer_data:
                return {'high_risk_customers': 0, 'risk_factors': []}

            analysis = analyze_customer_behavior_patterns(customer_data)
            return analysis.get('churn_risk', {})

        except Exception as e:
            logger.error(f"이탈 위험 분석 오류: {e}")
            return {'error': str(e)}

    def _generate_retention_strategy(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """고객 유지 전략 생성"""
        try:
            strategy = {
                'strategy_type': 'customer_retention',
                'target_customers': 0,
                'retention_programs': [],
                'expected_impact': 'medium'
            }

            for step in steps:
                if step['step'] == 'churn_analysis':
                    churn_data = step['result']
                    if 'high_risk_customers' in churn_data:
                        strategy['target_customers'] = churn_data['high_risk_customers']
                        strategy['retention_programs'] = [
                            '개인화된 할인 혜택',
                            '충성도 프로그램',
                            '고객 만족도 조사',
                            '맞춤형 마케팅'
                        ]

            return strategy

        except Exception as e:
            logger.error(f"고객 유지 전략 생성 오류: {e}")
            return {'error': str(e)}

    def _generate_system_optimization_recommendations(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """시스템 최적화 권장사항 생성"""
        recommendations = []

        for step in steps:
            if step['step'] == 'performance_analysis':
                perf = step['result']
                if 'memory_usage' in perf:
                    memory_usage = perf['memory_usage']['percent']
                    if memory_usage > 80:
                        recommendations.append({
                            'type': 'warning',
                            'title': '메모리 사용률 높음',
                            'description': f'메모리 사용률이 {memory_usage}%입니다.',
                            'priority': 'medium',
                            'action': 'optimize_memory'
                        })

            elif step['step'] == 'system_analysis':
                system = step['result']
                if 'anomalies' in system:
                    anomalies = system['anomalies']
                    if anomalies.get('total_anomalies', 0) > 0:
                        recommendations.append({
                            'type': 'maintenance',
                            'title': '시스템 점검 필요',
                            'description': f'{anomalies["total_anomalies"]}개의 이상이 감지되었습니다.',
                            'priority': 'high',
                            'action': 'system_maintenance'
                        })

        return recommendations


# 전역 인스턴스
integrated_ai_service = IntegratedAIService()


@ai_integrated_bp.route('/api/ai/analyze', methods=['POST'])
@login_required
def analyze_business_data():
    """비즈니스 데이터 종합 분석"""
    try:
        data = request.get_json() or {}
        data_type = data.get('data_type')
        analysis_data = data.get('data', {})

        if not data_type:
            return jsonify({'error': 'data_type이 필요합니다'}), 400

        result = integrated_ai_service.analyze_business_data(data_type,  analysis_data)

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        logger.error(f"비즈니스 데이터 분석 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': '분석 중 오류가 발생했습니다'
        }), 500


@ai_integrated_bp.route('/api/ai/dashboard', methods=['GET'])
@login_required
def get_comprehensive_dashboard():
    """종합 AI 대시보드"""
    try:
        dashboard_data = integrated_ai_service.get_comprehensive_dashboard()

        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        })

    except Exception as e:
        logger.error(f"종합 대시보드 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': '대시보드 생성 중 오류가 발생했습니다'
        }), 500


@ai_integrated_bp.route('/api/ai/workflow', methods=['POST'])
@login_required
def execute_ai_workflow():
    """AI 워크플로우 실행"""
    try:
        data = request.get_json() or {}
        workflow_type = data.get('workflow_type')
        parameters = data.get('parameters', {})

        if not workflow_type:
            return jsonify({'error': 'workflow_type이 필요합니다'}), 400

        result = integrated_ai_service.execute_ai_workflow(workflow_type,  parameters)

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        logger.error(f"AI 워크플로우 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': '워크플로우 실행 중 오류가 발생했습니다'
        }), 500


@ai_integrated_bp.route('/api/ai/insights', methods=['GET'])
@login_required
def get_ai_insights():
    """AI 인사이트 조회"""
    try:
        insights = integrated_ai_service._generate_ai_insights()

        return jsonify({
            'success': True,
            'insights': insights
        })

    except Exception as e:
        logger.error(f"AI 인사이트 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': '인사이트 생성 중 오류가 발생했습니다'
        }), 500


@ai_integrated_bp.route('/api/ai/recommendations', methods=['GET'])
@login_required
def get_ai_recommendations():
    """AI 권장사항 조회"""
    try:
        data_type = request.args.get('type', 'all')

        if data_type == 'all':
            recommendations = integrated_ai_service._get_system_recommendations()
        else:
            # 특정 타입의 권장사항 생성
            analysis = {}
            recommendations = integrated_ai_service._generate_recommendations(data_type, analysis)

        return jsonify({
            'success': True,
            'recommendations': recommendations
        })

    except Exception as e:
        logger.error(f"AI 권장사항 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': '권장사항 생성 중 오류가 발생했습니다'
        }), 500


@ai_integrated_bp.route('/api/ai/alerts', methods=['GET'])
@login_required
def get_ai_alerts():
    """AI 알림 조회"""
    try:
        alerts = integrated_ai_service._get_active_alerts()

        return jsonify({
            'success': True,
            'alerts': alerts,
            'count': len(alerts)
        })

    except Exception as e:
        logger.error(f"AI 알림 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': '알림 조회 중 오류가 발생했습니다'
        }), 500


@ai_integrated_bp.route('/api/ai/status', methods=['GET'])
@login_required
def get_ai_status():
    """AI 시스템 상태 조회"""
    try:
        status = {
            'timestamp': datetime.now().isoformat(),
            'cache_enabled': integrated_ai_service.cache_enabled,
            'rate_limits': integrated_ai_service.rate_limits,
            'request_counts': integrated_ai_service.request_counts,
            'system_health': 'healthy'
        }

        return jsonify({
            'success': True,
            'status': status
        })

    except Exception as e:
        logger.error(f"AI 상태 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': '상태 조회 중 오류가 발생했습니다'
        }), 500
