from utils.alert_notifier import send_alert  # pyright: ignore
import os
from dataclasses import dataclass, asdict
import numpy as np
import statistics
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import threading
import time
import json
import logging
from typing import Optional
config = None  # pyright: ignore
form = None  # pyright: ignore
#!/usr/bin/env python3
"""
운영 데이터 기반 성능 분석 및 튜닝 시스템
실제 운영 환경에서 수집된 데이터를 분석하여 성능 최적화 방안을 제시
"""


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """성능 메트릭 데이터 클래스"""
    timestamp: datetime
    metric_type: str
    value: float
    plugin_id: Optional[str] if Optional is not None else None = None
    component: Optional[str] if Optional is not None else None = None
    metadata: Optional[Dict[str, Any] if Optional is not None else None] = None


@dataclass
class PerformanceAnalysis:
    """성능 분석 결과"""
    analysis_id: str
    timestamp: datetime
    period: str
    metrics_summary: Dict[str, Any] if Dict is not None else None
    bottlenecks: List[Dict[str, Any] if List is not None else None]
    recommendations: List[Dict[str, Any] if List is not None else None]
    trends: Dict[str, Any] if Dict is not None else None
    health_score: float


class PerformanceAnalytics:
    """운영 데이터 기반 성능 분석 시스템"""

    def __init__(self):
        self.metrics_storage = {
            'response_times': deque(maxlen=10000),
            'memory_usage': deque(maxlen=1000),
            'cpu_usage': deque(maxlen=1000),
            'error_rates': deque(maxlen=1000),
            'throughput': deque(maxlen=1000),
            'plugin_metrics': defaultdict(lambda: deque(maxlen=1000))
        }

        # 분석 결과 저장
        self.analysis_results = deque(maxlen=100)

        # 성능 임계값
        self.thresholds = {
            'response_time': {
                'warning': 2.0,  # 2초
                'critical': 5.0  # 5초
            },
            'memory_usage': {
                'warning': 80.0,  # 80%
                'critical': 95.0  # 95%
            },
            'cpu_usage': {
                'warning': 85.0,  # 85%
                'critical': 95.0  # 95%
            },
            'error_rate': {
                'warning': 5.0,   # 5%
                'critical': 15.0  # 15%
            }
        }

        # 분석 설정
        self.analysis_config = {
            'analysis_interval': 3600,  # 1시간
            'trend_period': 24,         # 24시간
            'min_data_points': 100,
            'enable_auto_analysis': True
        }

        # 백그라운드 분석 스레드
        self.analysis_thread = None
        self.running = False

    def start_analytics(self) -> Dict[str, Any] if Dict is not None else None:
        """성능 분석 시스템 시작"""
        logger.info("성능 분석 시스템 시작")

        try:
            self.running = True
            self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
            self.analysis_thread.start()

            return {
                'status': 'success',
                'message': '성능 분석 시스템이 시작되었습니다',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"성능 분석 시스템 시작 실패: {e}")
            return {
                'status': 'error',
                'message': f'성능 분석 시스템 시작 실패: {e}'
            }

    def stop_analytics(self) -> Dict[str, Any] if Dict is not None else None:
        """성능 분석 시스템 중지"""
        logger.info("성능 분석 시스템 중지")

        try:
            self.running = False
            if self.analysis_thread:
                self.analysis_thread.join(timeout=10)

            return {
                'status': 'success',
                'message': '성능 분석 시스템이 중지되었습니다',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"성능 분석 시스템 중지 실패: {e}")
            return {
                'status': 'error',
                'message': f'성능 분석 시스템 중지 실패: {e}'
            }

    def collect_metric(self, metric_type: str, value: float,
                       plugin_id: Optional[str] if Optional is not None else None = None,
                       component: Optional[str] if Optional is not None else None = None,
                       metadata: Optional[Dict[str, Any] if Optional is not None else None] = None) -> None:
        """성능 메트릭 수집"""
        try:
            metric = PerformanceMetric(
                timestamp=datetime.now(),
                metric_type=metric_type,
                value=value,
                plugin_id=plugin_id,
                component=component,
                metadata=metadata
            )

            # 메트릭 저장
            if metric_type in self.metrics_storage:
                self.metrics_storage[metric_type].append(metric)

            # 플러그인별 메트릭 저장
            if plugin_id:
                self.metrics_storage['plugin_metrics'][plugin_id].append(metric)

        except Exception as e:
            logger.error(f"메트릭 수집 실패: {e}")

    def analyze_performance(self, period_hours: int = 24) -> PerformanceAnalysis:
        """성능 분석 수행"""
        logger.info(f"성능 분석 시작 (기간: {period_hours}시간)")

        try:
            # 분석 기간 설정
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=period_hours)

            # 메트릭 필터링
            filtered_metrics = self._filter_metrics_by_period(start_time, end_time)

            # 메트릭 요약 계산
            metrics_summary = self._calculate_metrics_summary(filtered_metrics)

            # 병목 지점 식별
            bottlenecks = self._identify_bottlenecks(filtered_metrics)

            # 최적화 권장사항 생성
            recommendations = self._generate_recommendations(metrics_summary, bottlenecks)

            # 트렌드 분석
            trends = self._analyze_trends(filtered_metrics)

            # 시스템 건강도 점수 계산
            health_score = self._calculate_health_score(metrics_summary)

            # 분석 결과 생성
            analysis = PerformanceAnalysis(
                analysis_id=f"analysis_{int(time.time())}",
                timestamp=datetime.now(),
                period=f"{period_hours}h",
                metrics_summary=metrics_summary,
                bottlenecks=bottlenecks,
                recommendations=recommendations,
                trends=trends,
                health_score=health_score
            )

            # 분석 결과 저장
            self.analysis_results.append(analysis)

            logger.info(f"성능 분석 완료 (건강도 점수: {health_score:.2f})")
            return analysis

        except Exception as e:
            logger.error(f"성능 분석 실패: {e}")
            raise

    def get_performance_report(self, analysis_id: Optional[str] if Optional is not None else None = None) -> Dict[str, Any] if Dict is not None else None:
        """성능 리포트 조회"""
        try:
            if analysis_id:
                # 특정 분석 결과 조회
                for analysis in self.analysis_results:
                    if analysis.analysis_id == analysis_id:
                        return self._format_analysis_report(analysis)
                return {'error': '분석 결과를 찾을 수 없습니다'}
            else:
                # 최신 분석 결과 조회
                if self.analysis_results:
                    latest_analysis = self.analysis_results[-1]
                    return self._format_analysis_report(latest_analysis)
                else:
                    # 실시간 분석 수행
                    analysis = self.analyze_performance()
                    return self._format_analysis_report(analysis)

        except Exception as e:
            logger.error(f"성능 리포트 조회 실패: {e}")
            return {'error': str(e)}

    def get_optimization_suggestions(self) -> List[Dict[str, Any] if List is not None else None]:
        """최적화 제안사항 조회"""
        try:
            suggestions = []

            # 최신 분석 결과 기반 제안
            if self.analysis_results:
                latest_analysis = self.analysis_results[-1]
                metrics_summary = latest_analysis.metrics_summary if latest_analysis else {}
                thresholds = self.thresholds

                # 응답 시간 최적화 제안
                avg_response_time = metrics_summary.get('avg_response_time', 0)
                if avg_response_time > thresholds['response_time']['warning']:
                    suggestions.append({
                        'type': 'response_time_optimization',
                        'priority': 'high' if avg_response_time > thresholds['response_time']['critical'] else 'medium',
                        'description': f'평균 응답 시간이 {avg_response_time:.2f}초로 높습니다. 캐싱 및 데이터베이스 최적화를 권장합니다.',
                        'actions': [
                            '데이터베이스 쿼리 최적화',
                            'Redis 캐싱 활성화',
                            'API 응답 압축 적용'
                        ]
                    })

                # 메모리 사용량 최적화 제안
                avg_memory_usage = metrics_summary.get('avg_memory_usage', 0)
                if avg_memory_usage > thresholds['memory_usage']['warning']:
                    suggestions.append({
                        'type': 'memory_optimization',
                        'priority': 'high' if avg_memory_usage > thresholds['memory_usage']['critical'] else 'medium',
                        'description': f'메모리 사용량이 {avg_memory_usage:.1f}%로 높습니다. 메모리 누수 검사 및 최적화를 권장합니다.',
                        'actions': [
                            '메모리 누수 검사',
                            '불필요한 객체 정리',
                            '메모리 사용량 모니터링 강화'
                        ]
                    })

                # CPU 사용량 최적화 제안
                avg_cpu_usage = metrics_summary.get('avg_cpu_usage', 0)
                if avg_cpu_usage > thresholds['cpu_usage']['warning']:
                    suggestions.append({
                        'type': 'cpu_optimization',
                        'priority': 'high' if avg_cpu_usage > thresholds['cpu_usage']['critical'] else 'medium',
                        'description': f'CPU 사용량이 {avg_cpu_usage:.1f}%로 높습니다. 비동기 처리 및 스케줄링 최적화를 권장합니다.',
                        'actions': [
                            '비동기 작업 활성화',
                            '백그라운드 작업 분산',
                            'CPU 집약적 작업 최적화'
                        ]
                    })

                # 에러율 최적화 제안
                avg_error_rate = metrics_summary.get('avg_error_rate', 0)
                if avg_error_rate > thresholds['error_rate']['warning']:
                    suggestions.append({
                        'type': 'error_rate_optimization',
                        'priority': 'high' if avg_error_rate > thresholds['error_rate']['critical'] else 'medium',
                        'description': f'에러율이 {avg_error_rate:.2f}%로 높습니다. 에러 처리 및 로깅 개선을 권장합니다.',
                        'actions': [
                            '에러 로그 분석',
                            '예외 처리 강화',
                            '서킷 브레이커 패턴 적용'
                        ]
                    })

            return suggestions

        except Exception as e:
            logger.error(f"최적화 제안 조회 실패: {e}")
            return []

    def _analysis_loop(self) -> None:
        """분석 루프"""
        while self.running:
            try:
                if self.analysis_config['enable_auto_analysis']:
                    # 자동 분석 수행
                    self.analyze_performance()

                time.sleep(self.analysis_config['analysis_interval'])

            except Exception as e:
                logger.error(f"분석 루프 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기

    def _filter_metrics_by_period(self, start_time: datetime, end_time: datetime) -> Dict[str, List[PerformanceMetric] if Dict is not None else None]:
        """기간별 메트릭 필터링"""
        filtered_metrics = defaultdict(list)

        for metric_type, metrics in self.metrics_storage.items():
            if metric_type == 'plugin_metrics':
                continue

            for metric in metrics:
                if start_time <= metric.timestamp <= end_time:
                    filtered_metrics[metric_type].append(metric)

        # 플러그인별 메트릭도 필터링
        for plugin_id, metrics in self.metrics_storage['plugin_metrics'].items():
            for metric in metrics:
                if start_time <= metric.timestamp <= end_time:
                    filtered_metrics[f'plugin_{plugin_id}'].append(metric)

        return filtered_metrics

    def _calculate_metrics_summary(self, filtered_metrics: Dict[str, List[PerformanceMetric] if Dict is not None else None]) -> Dict[str, Any] if Dict is not None else None:
        """메트릭 요약 계산"""
        summary = {}

        for metric_type, metrics in filtered_metrics.items():
            if not metrics:
                continue

            values = [m.value for m in metrics]

            summary[metric_type] = {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': statistics.mean(values),
                'median': statistics.median(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                'p95': np.percentile(values, 95) if len(values) > 0 else 0,
                'p99': np.percentile(values, 99) if len(values) > 0 else 0
            }

        # 전체 시스템 요약
        if 'response_times' in summary:
            summary['avg_response_time'] = summary['response_times']['avg']
        if 'memory_usage' in summary:
            summary['avg_memory_usage'] = summary['memory_usage']['avg']
        if 'cpu_usage' in summary:
            summary['avg_cpu_usage'] = summary['cpu_usage']['avg']
        if 'error_rates' in summary:
            summary['avg_error_rate'] = summary['error_rates']['avg']

        return summary

    def _identify_bottlenecks(self, filtered_metrics: Dict[str, List[PerformanceMetric] if Dict is not None else None]) -> List[Dict[str, Any] if List is not None else None]:
        """병목 지점 식별"""
        bottlenecks = []
        for metric_type, metrics in filtered_metrics.items():
            if not metrics:
                continue
            values = [m.value for m in metrics]
            avg_value = statistics.mean(values)
            if metric_type in self.thresholds:
                threshold = self.thresholds[metric_type]
                if avg_value > threshold['critical']:
                    bottleneck = {
                        'type': metric_type,
                        'severity': 'critical',
                        'avg_value': avg_value,
                        'threshold': threshold['critical'],
                        'description': f'{metric_type}이 임계값을 크게 초과합니다',
                        'suggestions': self._get_bottleneck_suggestions(metric_type, 'critical')
                    }
                    bottlenecks.append(bottleneck)
                    send_alert(f'{metric_type} 평균값 {avg_value:.2f} (임계값 {threshold["critical"]}) 초과', level='critical')
                elif avg_value > threshold['warning']:
                    bottleneck = {
                        'type': metric_type,
                        'severity': 'warning',
                        'avg_value': avg_value,
                        'threshold': threshold['warning'],
                        'description': f'{metric_type}이 임계값을 초과합니다',
                        'suggestions': self._get_bottleneck_suggestions(metric_type, 'warning')
                    }
                    bottlenecks.append(bottleneck)
                    send_alert(f'{metric_type} 평균값 {avg_value:.2f} (임계값 {threshold["warning"]}) 초과', level='warning')
        return bottlenecks

    def _generate_recommendations(self, metrics_summary: Dict[str, Any] if Dict is not None else None,
                                  bottlenecks: List[Dict[str, Any] if List is not None else None]) -> List[Dict[str, Any] if List is not None else None]:
        """최적화 권장사항 생성"""
        recommendations = []

        # 병목 지점 기반 권장사항
        for bottleneck in bottlenecks:
            recommendations.extend(bottleneck.get('suggestions', []))

        # 메트릭 요약 기반 권장사항
        if 'avg_response_time' in metrics_summary:
            response_time = metrics_summary['avg_response_time']
            if response_time > 3.0:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'high',
                    'title': '응답 시간 최적화',
                    'description': 'API 응답 시간을 개선하기 위한 권장사항',
                    'actions': [
                        '데이터베이스 인덱스 최적화',
                        'API 응답 캐싱 구현',
                        '비동기 처리 도입'
                    ]
                })

        return recommendations

    def _analyze_trends(self, filtered_metrics: Dict[str, List[PerformanceMetric] if Dict is not None else None]) -> Dict[str, Any] if Dict is not None else None:
        """트렌드 분석"""
        trends = {}

        for metric_type, metrics in filtered_metrics.items():
            if len(metrics) < 10:  # 최소 데이터 포인트 필요
                continue

            # 시간순 정렬
            sorted_metrics = sorted(metrics, key=lambda x: x.timestamp)
            values = [m.value for m in sorted_metrics]

            # 선형 회귀로 트렌드 계산
            if len(values) > 1:
                x = np.arange(len(values))
                slope, intercept = np.polyfit(x, values, 1)

                trends[metric_type] = {
                    'slope': slope,
                    'trend': 'increasing' if slope > 0.01 else 'decreasing' if slope < -0.01 else 'stable',
                    'change_rate': slope * 100,  # 시간당 변화율
                    'volatility': statistics.stdev(values) if len(values) > 1 else 0
                }

        return trends

    def _calculate_health_score(self, metrics_summary: Dict[str, Any] if Dict is not None else None) -> float:
        """시스템 건강도 점수 계산 (0-100)"""
        score = 100.0

        # 응답 시간 점수
        if 'avg_response_time' in metrics_summary:
            response_time = metrics_summary['avg_response_time']
            if response_time > self.thresholds['response_time']['critical']:
                score -= 30
            elif response_time > self.thresholds['response_time']['warning']:
                score -= 15

        # 메모리 사용량 점수
        if 'avg_memory_usage' in metrics_summary:
            memory_usage = metrics_summary['avg_memory_usage']
            if memory_usage > self.thresholds['memory_usage']['critical']:
                score -= 25
            elif memory_usage > self.thresholds['memory_usage']['warning']:
                score -= 10

        # CPU 사용량 점수
        if 'avg_cpu_usage' in metrics_summary:
            cpu_usage = metrics_summary['avg_cpu_usage']
            if cpu_usage > self.thresholds['cpu_usage']['critical']:
                score -= 25
            elif cpu_usage > self.thresholds['cpu_usage']['warning']:
                score -= 10

        # 에러율 점수
        if 'avg_error_rate' in metrics_summary:
            error_rate = metrics_summary['avg_error_rate']
            if error_rate > self.thresholds['error_rate']['critical']:
                score -= 20
            elif error_rate > self.thresholds['error_rate']['warning']:
                score -= 10

        return max(0.0, score)

    def _get_bottleneck_suggestions(self, metric_type: str, severity: str) -> List[Dict[str, Any] if List is not None else None]:
        """병목 지점별 제안사항"""
        suggestions = {
            'response_time': {
                'critical': [
                    {'action': '데이터베이스 쿼리 최적화', 'priority': 'immediate'},
                    {'action': 'API 응답 캐싱 구현', 'priority': 'high'},
                    {'action': '서버 리소스 확장', 'priority': 'high'}
                ],
                'warning': [
                    {'action': '쿼리 인덱스 검토', 'priority': 'medium'},
                    {'action': '응답 압축 적용', 'priority': 'medium'}
                ]
            },
            'memory_usage': {
                'critical': [
                    {'action': '메모리 누수 검사', 'priority': 'immediate'},
                    {'action': '불필요한 객체 정리', 'priority': 'high'},
                    {'action': '메모리 확장', 'priority': 'high'}
                ],
                'warning': [
                    {'action': '메모리 사용량 모니터링', 'priority': 'medium'},
                    {'action': '가비지 컬렉션 최적화', 'priority': 'medium'}
                ]
            },
            'cpu_usage': {
                'critical': [
                    {'action': 'CPU 집약적 작업 분산', 'priority': 'immediate'},
                    {'action': '비동기 처리 도입', 'priority': 'high'},
                    {'action': '서버 스케일링', 'priority': 'high'}
                ],
                'warning': [
                    {'action': '백그라운드 작업 최적화', 'priority': 'medium'},
                    {'action': '스케줄링 개선', 'priority': 'medium'}
                ]
            },
            'error_rate': {
                'critical': [
                    {'action': '에러 로그 분석', 'priority': 'immediate'},
                    {'action': '예외 처리 강화', 'priority': 'high'},
                    {'action': '서킷 브레이커 패턴 적용', 'priority': 'high'}
                ],
                'warning': [
                    {'action': '에러 모니터링 강화', 'priority': 'medium'},
                    {'action': '로깅 개선', 'priority': 'medium'}
                ]
            }
        }

        return suggestions.get(metric_type, {}).get(severity, [])

    def _format_analysis_report(self, analysis: PerformanceAnalysis) -> Dict[str, Any] if Dict is not None else None:
        """분석 리포트 포맷팅"""
        return {
            'analysis_id': analysis.analysis_id,
            'timestamp': analysis.timestamp.isoformat(),
            'period': analysis.period,
            'health_score': analysis.health_score,
            'metrics_summary': analysis.metrics_summary,
            'bottlenecks': analysis.bottlenecks,
            'recommendations': analysis.recommendations,
            'trends': analysis.trends,
            'summary': {
                'total_bottlenecks': len(analysis.bottlenecks),
                'critical_issues': len([b for b in analysis.bottlenecks if b['severity'] == 'critical']),
                'total_recommendations': len(analysis.recommendations),
                'overall_status': 'healthy' if analysis.health_score >= 80 else 'warning' if analysis.health_score >= 60 else 'critical'
            }
        }
