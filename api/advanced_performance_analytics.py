#!/usr/bin/env python3
"""
고도화된 성능 분석 API
실시간 성능 모니터링, 이력 분석, 예측, 알림, 자동 튜닝 등의 고급 기능을 제공
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, timedelta
import logging
import threading
import time
import json
import psutil
from typing import Dict, List, Any, Optional
from collections import deque
import sqlite3
import os

logger = logging.getLogger(__name__)

# 블루프린트 생성
advanced_performance_bp = Blueprint('advanced_performance', __name__, url_prefix='/api/advanced-performance')

class AdvancedPerformanceAnalytics:
    """고도화된 성능 분석 시스템"""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=10000)  # 최근 10000개 메트릭 저장
        self.alerts = deque(maxlen=1000)  # 최근 1000개 알림 저장
        self.performance_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 2000.0,  # ms
            'error_rate': 5.0,  # %
            'active_connections': 1000
        }
        self.monitoring_active = False
        self.monitoring_thread = None
        self.db_path = 'performance_analytics.db'
        self._init_database()
        
    def _init_database(self):
        """성능 분석 데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 성능 메트릭 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    network_io_sent REAL,
                    network_io_recv REAL,
                    active_connections INTEGER,
                    response_time REAL,
                    error_rate REAL,
                    active_requests INTEGER,
                    cache_hit_rate REAL,
                    database_connections INTEGER,
                    plugin_count INTEGER,
                    system_load REAL
                )
            ''')
            
            # 성능 알림 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metric_name TEXT,
                    metric_value REAL,
                    threshold_value REAL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TEXT
                )
            ''')
            
            # 성능 예측 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    prediction_type TEXT NOT NULL,
                    predicted_value REAL,
                    confidence REAL,
                    time_horizon TEXT,
                    factors TEXT
                )
            ''')
            
            # 성능 튜닝 이력 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_tuning_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    tuning_type TEXT NOT NULL,
                    before_value REAL,
                    after_value REAL,
                    improvement REAL,
                    description TEXT,
                    applied BOOLEAN DEFAULT FALSE
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("성능 분석 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def start_monitoring(self):
        """실시간 모니터링 시작"""
        if self.monitoring_active:
            return {"status": "already_running"}
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("고도화된 성능 분석 모니터링 시작")
        return {"status": "started"}
    
    def stop_monitoring(self):
        """실시간 모니터링 중지"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
            
        logger.info("고도화된 성능 분석 모니터링 중지")
        return {"status": "stopped"}
    
    def _monitoring_loop(self):
        """실시간 모니터링 루프"""
        while self.monitoring_active:
            try:
                # 성능 메트릭 수집
                metrics = self._collect_performance_metrics()
                self.metrics_history.append(metrics)
                
                # 데이터베이스에 저장
                self._save_metrics_to_db(metrics)
                
                # 알림 체크
                self._check_alerts(metrics)
                
                # 성능 예측
                self._generate_predictions()
                
                # 자동 튜닝 체크
                self._check_auto_tuning(metrics)
                
                time.sleep(30)  # 30초마다 업데이트
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(60)
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 수집"""
        try:
            # 시스템 메트릭
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # 네트워크 연결 수
            connections = len(psutil.net_connections())
            
            # 프로세스 수
            process_count = len(psutil.pids())
            
            # 시스템 로드 (Unix/Linux에서만 사용 가능)
            try:
                system_load = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
            except:
                system_load = 0
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': cpu_usage,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'network_io_sent': network.bytes_sent if network else 0,
                'network_io_recv': network.bytes_recv if network else 0,
                'active_connections': connections,
                'response_time': self._get_avg_response_time(),
                'error_rate': self._get_error_rate(),
                'active_requests': self._get_active_requests(),
                'cache_hit_rate': self._get_cache_hit_rate(),
                'database_connections': self._get_db_connections(),
                'plugin_count': self._get_plugin_count(),
                'system_load': system_load
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"성능 메트릭 수집 실패: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _get_avg_response_time(self) -> float:
        """평균 응답 시간 계산"""
        try:
            # 실제로는 실제 API 응답 시간을 측정해야 함
            # 여기서는 더미 데이터 반환
            import random
            return random.uniform(50, 500)
        except:
            return 0.0
    
    def _get_error_rate(self) -> float:
        """오류율 계산"""
        try:
            # 실제로는 실제 오류율을 계산해야 함
            import random
            return random.uniform(0, 2)
        except:
            return 0.0
    
    def _get_active_requests(self) -> int:
        """활성 요청 수"""
        try:
            # 실제로는 실제 활성 요청 수를 계산해야 함
            import random
            return random.randint(0, 100)
        except:
            return 0
    
    def _get_cache_hit_rate(self) -> float:
        """캐시 히트율"""
        try:
            # 실제로는 실제 캐시 히트율을 계산해야 함
            import random
            return random.uniform(60, 95)
        except:
            return 0.0
    
    def _get_db_connections(self) -> int:
        """데이터베이스 연결 수"""
        try:
            # 실제로는 실제 DB 연결 수를 계산해야 함
            import random
            return random.randint(5, 20)
        except:
            return 0
    
    def _get_plugin_count(self) -> int:
        """플러그인 수"""
        try:
            # 실제로는 실제 플러그인 수를 계산해야 함
            return 3  # 현재 테스트 환경의 플러그인 수
        except:
            return 0
    
    def _save_metrics_to_db(self, metrics: Dict[str, Any]):
        """메트릭을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics (
                    timestamp, cpu_usage, memory_usage, disk_usage,
                    network_io_sent, network_io_recv, active_connections,
                    response_time, error_rate, active_requests,
                    cache_hit_rate, database_connections, plugin_count, system_load
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.get('timestamp'),
                metrics.get('cpu_usage'),
                metrics.get('memory_usage'),
                metrics.get('disk_usage'),
                metrics.get('network_io_sent'),
                metrics.get('network_io_recv'),
                metrics.get('active_connections'),
                metrics.get('response_time'),
                metrics.get('error_rate'),
                metrics.get('active_requests'),
                metrics.get('cache_hit_rate'),
                metrics.get('database_connections'),
                metrics.get('plugin_count'),
                metrics.get('system_load')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"메트릭 저장 실패: {e}")
    
    def _check_alerts(self, metrics: Dict[str, Any]):
        """성능 알림 체크"""
        try:
            alerts = []
            
            # CPU 사용률 체크
            if metrics.get('cpu_usage', 0) > self.performance_thresholds['cpu_usage']:
                alerts.append({
                    'type': 'cpu_usage',
                    'severity': 'warning' if metrics['cpu_usage'] < 95 else 'critical',
                    'message': f'CPU 사용률이 높습니다: {metrics["cpu_usage"]:.1f}%',
                    'metric_name': 'cpu_usage',
                    'metric_value': metrics['cpu_usage'],
                    'threshold_value': self.performance_thresholds['cpu_usage']
                })
            
            # 메모리 사용률 체크
            if metrics.get('memory_usage', 0) > self.performance_thresholds['memory_usage']:
                alerts.append({
                    'type': 'memory_usage',
                    'severity': 'warning' if metrics['memory_usage'] < 95 else 'critical',
                    'message': f'메모리 사용률이 높습니다: {metrics["memory_usage"]:.1f}%',
                    'metric_name': 'memory_usage',
                    'metric_value': metrics['memory_usage'],
                    'threshold_value': self.performance_thresholds['memory_usage']
                })
            
            # 디스크 사용률 체크
            if metrics.get('disk_usage', 0) > self.performance_thresholds['disk_usage']:
                alerts.append({
                    'type': 'disk_usage',
                    'severity': 'warning' if metrics['disk_usage'] < 95 else 'critical',
                    'message': f'디스크 사용률이 높습니다: {metrics["disk_usage"]:.1f}%',
                    'metric_name': 'disk_usage',
                    'metric_value': metrics['disk_usage'],
                    'threshold_value': self.performance_thresholds['disk_usage']
                })
            
            # 응답 시간 체크
            if metrics.get('response_time', 0) > self.performance_thresholds['response_time']:
                alerts.append({
                    'type': 'response_time',
                    'severity': 'warning',
                    'message': f'응답 시간이 느립니다: {metrics["response_time"]:.1f}ms',
                    'metric_name': 'response_time',
                    'metric_value': metrics['response_time'],
                    'threshold_value': self.performance_thresholds['response_time']
                })
            
            # 오류율 체크
            if metrics.get('error_rate', 0) > self.performance_thresholds['error_rate']:
                alerts.append({
                    'type': 'error_rate',
                    'severity': 'critical',
                    'message': f'오류율이 높습니다: {metrics["error_rate"]:.1f}%',
                    'metric_name': 'error_rate',
                    'metric_value': metrics['error_rate'],
                    'threshold_value': self.performance_thresholds['error_rate']
                })
            
            # 알림 저장
            for alert in alerts:
                alert['timestamp'] = datetime.now().isoformat()
                self.alerts.append(alert)
                self._save_alert_to_db(alert)
            
        except Exception as e:
            logger.error(f"알림 체크 실패: {e}")
    
    def _save_alert_to_db(self, alert: Dict[str, Any]):
        """알림을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_alerts (
                    timestamp, alert_type, severity, message,
                    metric_name, metric_value, threshold_value
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert['timestamp'],
                alert['type'],
                alert['severity'],
                alert['message'],
                alert.get('metric_name'),
                alert.get('metric_value'),
                alert.get('threshold_value')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"알림 저장 실패: {e}")
    
    def _generate_predictions(self):
        """성능 예측 생성"""
        try:
            if len(self.metrics_history) < 10:
                return
            
            # 최근 메트릭 데이터로 예측
            recent_metrics = list(self.metrics_history)[-10:]
            
            # CPU 사용률 예측
            cpu_values = [m.get('cpu_usage', 0) for m in recent_metrics]
            cpu_trend = self._calculate_trend(cpu_values)
            cpu_prediction = self._predict_next_value(cpu_values, cpu_trend)
            
            # 메모리 사용률 예측
            memory_values = [m.get('memory_usage', 0) for m in recent_metrics]
            memory_trend = self._calculate_trend(memory_values)
            memory_prediction = self._predict_next_value(memory_values, memory_trend)
            
            predictions = [
                {
                    'timestamp': datetime.now().isoformat(),
                    'prediction_type': 'cpu_usage',
                    'predicted_value': cpu_prediction,
                    'confidence': 0.8,
                    'time_horizon': '1h',
                    'factors': json.dumps({'trend': cpu_trend, 'recent_values': cpu_values[-5:]})
                },
                {
                    'timestamp': datetime.now().isoformat(),
                    'prediction_type': 'memory_usage',
                    'predicted_value': memory_prediction,
                    'confidence': 0.7,
                    'time_horizon': '1h',
                    'factors': json.dumps({'trend': memory_trend, 'recent_values': memory_values[-5:]})
                }
            ]
            
            # 예측 결과 저장
            for prediction in predictions:
                self._save_prediction_to_db(prediction)
            
        except Exception as e:
            logger.error(f"성능 예측 생성 실패: {e}")
    
    def _calculate_trend(self, values: List[float]) -> float:
        """트렌드 계산 (선형 회귀)"""
        try:
            if len(values) < 2:
                return 0.0
            
            n = len(values)
            x_sum = sum(range(n))
            y_sum = sum(values)
            xy_sum = sum(i * val for i, val in enumerate(values))
            x2_sum = sum(i * i for i in range(n))
            
            slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
            return slope
            
        except:
            return 0.0
    
    def _predict_next_value(self, values: List[float], trend: float) -> float:
        """다음 값 예측"""
        try:
            if not values:
                return 0.0
            
            last_value = values[-1]
            predicted = last_value + trend
            
            # 예측값이 현실적인 범위 내에 있도록 제한
            if predicted < 0:
                predicted = 0
            elif predicted > 100:
                predicted = 100
            
            return predicted
            
        except:
            return 0.0
    
    def _save_prediction_to_db(self, prediction: Dict[str, Any]):
        """예측 결과를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_predictions (
                    timestamp, prediction_type, predicted_value,
                    confidence, time_horizon, factors
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                prediction['timestamp'],
                prediction['prediction_type'],
                prediction['predicted_value'],
                prediction['confidence'],
                prediction['time_horizon'],
                prediction['factors']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"예측 결과 저장 실패: {e}")
    
    def _check_auto_tuning(self, metrics: Dict[str, Any]):
        """자동 튜닝 체크"""
        try:
            # CPU 사용률이 지속적으로 높은 경우
            if metrics.get('cpu_usage', 0) > 90:
                tuning_suggestion = {
                    'timestamp': datetime.now().isoformat(),
                    'tuning_type': 'cpu_optimization',
                    'before_value': metrics['cpu_usage'],
                    'after_value': metrics['cpu_usage'] * 0.8,  # 예상 개선값
                    'improvement': 20.0,
                    'description': 'CPU 사용률 최적화를 위한 워크로드 분산 및 캐시 최적화 권장',
                    'applied': False
                }
                self._save_tuning_suggestion(tuning_suggestion)
            
            # 메모리 사용률이 높은 경우
            if metrics.get('memory_usage', 0) > 85:
                tuning_suggestion = {
                    'timestamp': datetime.now().isoformat(),
                    'tuning_type': 'memory_optimization',
                    'before_value': metrics['memory_usage'],
                    'after_value': metrics['memory_usage'] * 0.85,
                    'improvement': 15.0,
                    'description': '메모리 사용률 최적화를 위한 가비지 컬렉션 및 메모리 정리 권장',
                    'applied': False
                }
                self._save_tuning_suggestion(tuning_suggestion)
            
            # 응답 시간이 느린 경우
            if metrics.get('response_time', 0) > 1000:
                tuning_suggestion = {
                    'timestamp': datetime.now().isoformat(),
                    'tuning_type': 'response_time_optimization',
                    'before_value': metrics['response_time'],
                    'after_value': metrics['response_time'] * 0.6,
                    'improvement': 40.0,
                    'description': '응답 시간 최적화를 위한 데이터베이스 쿼리 최적화 및 캐싱 강화 권장',
                    'applied': False
                }
                self._save_tuning_suggestion(tuning_suggestion)
            
        except Exception as e:
            logger.error(f"자동 튜닝 체크 실패: {e}")
    
    def _save_tuning_suggestion(self, suggestion: Dict[str, Any]):
        """튜닝 제안을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_tuning_history (
                    timestamp, tuning_type, before_value, after_value,
                    improvement, description, applied
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                suggestion['timestamp'],
                suggestion['tuning_type'],
                suggestion['before_value'],
                suggestion['after_value'],
                suggestion['improvement'],
                suggestion['description'],
                suggestion['applied']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"튜닝 제안 저장 실패: {e}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """현재 성능 메트릭 조회"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return {}
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """성능 메트릭 이력 조회"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            history = []
            
            for metrics in self.metrics_history:
                if datetime.fromisoformat(metrics['timestamp']) >= cutoff_time:
                    history.append(metrics)
            
            return history
            
        except Exception as e:
            logger.error(f"메트릭 이력 조회 실패: {e}")
            return []
    
    def get_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """알림 조회"""
        try:
            alerts = list(self.alerts)
            
            if severity:
                alerts = [alert for alert in alerts if alert.get('severity') == severity]
            
            return alerts
            
        except Exception as e:
            logger.error(f"알림 조회 실패: {e}")
            return []
    
    def get_predictions(self, prediction_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """예측 결과 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if prediction_type:
                cursor.execute('''
                    SELECT * FROM performance_predictions 
                    WHERE prediction_type = ? 
                    ORDER BY timestamp DESC LIMIT 10
                ''', (prediction_type,))
            else:
                cursor.execute('''
                    SELECT * FROM performance_predictions 
                    ORDER BY timestamp DESC LIMIT 20
                ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            predictions = []
            for row in rows:
                predictions.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'prediction_type': row[2],
                    'predicted_value': row[3],
                    'confidence': row[4],
                    'time_horizon': row[5],
                    'factors': json.loads(row[6]) if row[6] else {}
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"예측 결과 조회 실패: {e}")
            return []
    
    def get_tuning_suggestions(self) -> List[Dict[str, Any]]:
        """튜닝 제안 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM performance_tuning_history 
                WHERE applied = FALSE 
                ORDER BY timestamp DESC LIMIT 10
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            suggestions = []
            for row in rows:
                suggestions.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'tuning_type': row[2],
                    'before_value': row[3],
                    'after_value': row[4],
                    'improvement': row[5],
                    'description': row[6],
                    'applied': bool(row[7])
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"튜닝 제안 조회 실패: {e}")
            return []
    
    def update_thresholds(self, thresholds: Dict[str, float]):
        """성능 임계치 업데이트"""
        try:
            self.performance_thresholds.update(thresholds)
            logger.info(f"성능 임계치 업데이트: {thresholds}")
            return {"success": True, "message": "임계치가 업데이트되었습니다"}
            
        except Exception as e:
            logger.error(f"임계치 업데이트 실패: {e}")
            return {"success": False, "error": str(e)}

# 전역 인스턴스 생성
advanced_performance_analytics = AdvancedPerformanceAnalytics()

# API 엔드포인트들
@advanced_performance_bp.route('/start', methods=['POST'])
def start_analytics():
    """성능 분석 시작"""
    try:
        result = advanced_performance_analytics.start_monitoring()
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"성능 분석 시작 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_performance_bp.route('/stop', methods=['POST'])
def stop_analytics():
    """성능 분석 중지"""
    try:
        result = advanced_performance_analytics.stop_monitoring()
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"성능 분석 중지 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_performance_bp.route('/metrics/current', methods=['GET'])
def get_current_metrics():
    """현재 성능 메트릭 조회"""
    try:
        metrics = advanced_performance_analytics.get_current_metrics()
        return jsonify({
            'success': True,
            'data': metrics
        })
    except Exception as e:
        logger.error(f"현재 메트릭 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_performance_bp.route('/metrics/history', methods=['GET'])
def get_metrics_history():
    """성능 메트릭 이력 조회"""
    try:
        hours = request.args.get('hours', 24, type=int)
        history = advanced_performance_analytics.get_metrics_history(hours)
        return jsonify({
            'success': True,
            'data': {
                'history': history,
                'count': len(history),
                'hours': hours
            }
        })
    except Exception as e:
        logger.error(f"메트릭 이력 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_performance_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """성능 알림 조회"""
    try:
        severity = request.args.get('severity')
        alerts = advanced_performance_analytics.get_alerts(severity)
        return jsonify({
            'success': True,
            'data': {
                'alerts': alerts,
                'count': len(alerts),
                'critical_count': len([a for a in alerts if a.get('severity') == 'critical']),
                'warning_count': len([a for a in alerts if a.get('severity') == 'warning'])
            }
        })
    except Exception as e:
        logger.error(f"알림 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_performance_bp.route('/predictions', methods=['GET'])
def get_predictions():
    """성능 예측 조회"""
    try:
        prediction_type = request.args.get('type')
        predictions = advanced_performance_analytics.get_predictions(prediction_type)
        return jsonify({
            'success': True,
            'data': {
                'predictions': predictions,
                'count': len(predictions)
            }
        })
    except Exception as e:
        logger.error(f"예측 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_performance_bp.route('/tuning/suggestions', methods=['GET'])
def get_tuning_suggestions():
    """튜닝 제안 조회"""
    try:
        suggestions = advanced_performance_analytics.get_tuning_suggestions()
        return jsonify({
            'success': True,
            'data': {
                'suggestions': suggestions,
                'count': len(suggestions)
            }
        })
    except Exception as e:
        logger.error(f"튜닝 제안 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_performance_bp.route('/thresholds', methods=['GET', 'PUT'])
def manage_thresholds():
    """성능 임계치 관리"""
    try:
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'data': advanced_performance_analytics.performance_thresholds
            })
        elif request.method == 'PUT':
            thresholds = request.get_json()
            result = advanced_performance_analytics.update_thresholds(thresholds)
            return jsonify(result)
            
    except Exception as e:
        logger.error(f"임계치 관리 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_performance_bp.route('/dashboard', methods=['GET'])
def get_analytics_dashboard():
    """성능 분석 대시보드 데이터"""
    try:
        current_metrics = advanced_performance_analytics.get_current_metrics()
        recent_alerts = advanced_performance_analytics.get_alerts()
        recent_predictions = advanced_performance_analytics.get_predictions()
        tuning_suggestions = advanced_performance_analytics.get_tuning_suggestions()
        
        dashboard_data = {
            'current_metrics': current_metrics,
            'alerts_summary': {
                'total': len(recent_alerts),
                'critical': len([a for a in recent_alerts if a.get('severity') == 'critical']),
                'warning': len([a for a in recent_alerts if a.get('severity') == 'warning'])
            },
            'predictions_summary': {
                'total': len(recent_predictions),
                'cpu_predictions': len([p for p in recent_predictions if p.get('prediction_type') == 'cpu_usage']),
                'memory_predictions': len([p for p in recent_predictions if p.get('prediction_type') == 'memory_usage'])
            },
            'tuning_summary': {
                'total_suggestions': len(tuning_suggestions),
                'applied_suggestions': len([s for s in tuning_suggestions if s.get('applied')]),
                'pending_suggestions': len([s for s in tuning_suggestions if not s.get('applied')])
            },
            'monitoring_status': {
                'active': advanced_performance_analytics.monitoring_active,
                'last_update': datetime.now().isoformat()
            }
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        logger.error(f"대시보드 데이터 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 