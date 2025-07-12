#!/usr/bin/env python3
"""
고도화된 AI 예측 시스템 API
실시간 예측, 모델 관리, 자동 학습, 예측 정확도 분석 등의 고급 기능을 제공
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, timedelta
import logging
import threading
import time
import json
import numpy as np
from typing import Dict, List, Any, Optional
from collections import deque
import sqlite3
import os
import random

logger = logging.getLogger(__name__)

# 블루프린트 생성
advanced_ai_prediction_bp = Blueprint('advanced_ai_prediction', __name__, url_prefix='/api/advanced-ai')

class AdvancedAIPredictionSystem:
    """고도화된 AI 예측 시스템"""
    
    def __init__(self):
        self.models = {
            'sales': self._create_dummy_model('sales'),
            'inventory': self._create_dummy_model('inventory'),
            'staffing': self._create_dummy_model('staffing'),
            'customer_flow': self._create_dummy_model('customer_flow'),
            'revenue': self._create_dummy_model('revenue')
        }
        self.prediction_history = deque(maxlen=10000)
        self.model_performance = {}
        self.auto_learning_active = False
        self.auto_learning_thread = None
        self.db_path = 'advanced_ai_prediction.db'
        self._init_database()
        self._initialize_model_performance()
    
    def _init_database(self):
        """AI 예측 데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 예측 결과 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    prediction_type TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    predicted_value REAL,
                    actual_value REAL,
                    confidence REAL,
                    features TEXT,
                    metadata TEXT,
                    accuracy REAL
                )
            ''')
            
            # 모델 성능 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    mae REAL,
                    mse REAL,
                    rmse REAL,
                    r2_score REAL,
                    accuracy REAL,
                    training_samples INTEGER,
                    test_samples INTEGER
                )
            ''')
            
            # 자동 학습 이력 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auto_learning_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    action TEXT NOT NULL,
                    performance_before REAL,
                    performance_after REAL,
                    improvement REAL,
                    training_data_size INTEGER,
                    description TEXT
                )
            ''')
            
            # 예측 인사이트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prediction_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    insight_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    confidence REAL,
                    impact_score REAL,
                    recommendations TEXT,
                    data_sources TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("고도화된 AI 예측 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def _create_dummy_model(self, model_type: str) -> Dict[str, Any]:
        """더미 모델 생성"""
        return {
            'type': model_type,
            'version': '1.0.0',
            'last_trained': datetime.now().isoformat(),
            'accuracy': random.uniform(0.75, 0.95),
            'status': 'active',
            'parameters': {
                'learning_rate': 0.01,
                'epochs': 100,
                'batch_size': 32
            }
        }
    
    def _initialize_model_performance(self):
        """모델 성능 초기화"""
        for model_type in self.models.keys():
            self.model_performance[model_type] = {
                'mae': random.uniform(0.05, 0.15),
                'mse': random.uniform(0.01, 0.03),
                'rmse': random.uniform(0.1, 0.17),
                'r2_score': random.uniform(0.7, 0.9),
                'accuracy': random.uniform(0.75, 0.95),
                'last_updated': datetime.now().isoformat(),
                'training_samples': random.randint(1000, 5000),
                'test_samples': random.randint(200, 1000)
            }
    
    def start_auto_learning(self):
        """자동 학습 시작"""
        if self.auto_learning_active:
            return {"status": "already_running"}
            
        self.auto_learning_active = True
        self.auto_learning_thread = threading.Thread(target=self._auto_learning_loop, daemon=True)
        self.auto_learning_thread.start()
        
        logger.info("AI 자동 학습 시작")
        return {"status": "started"}
    
    def stop_auto_learning(self):
        """자동 학습 중지"""
        self.auto_learning_active = False
        if self.auto_learning_thread:
            self.auto_learning_thread.join(timeout=5)
            
        logger.info("AI 자동 학습 중지")
        return {"status": "stopped"}
    
    def _auto_learning_loop(self):
        """자동 학습 루프"""
        while self.auto_learning_active:
            try:
                # 각 모델에 대해 자동 학습 수행
                for model_type in self.models.keys():
                    self._train_model(model_type)
                
                # 성능 개선 체크
                self._check_performance_improvements()
                
                # 새로운 인사이트 생성
                self._generate_insights()
                
                time.sleep(3600)  # 1시간마다 학습
                
            except Exception as e:
                logger.error(f"자동 학습 루프 오류: {e}")
                time.sleep(7200)  # 오류 시 2시간 대기
    
    def _train_model(self, model_type: str):
        """모델 학습"""
        try:
            # 더미 학습 과정
            old_accuracy = self.model_performance[model_type]['accuracy']
            
            # 학습 시뮬레이션
            time.sleep(1)  # 학습 시간 시뮬레이션
            
            # 성능 개선 시뮬레이션
            improvement = random.uniform(-0.02, 0.05)  # -2% ~ +5% 개선
            new_accuracy = max(0.5, min(0.99, old_accuracy + improvement))
            
            # 성능 업데이트
            self.model_performance[model_type].update({
                'accuracy': new_accuracy,
                'last_updated': datetime.now().isoformat(),
                'training_samples': self.model_performance[model_type]['training_samples'] + random.randint(50, 200)
            })
            
            # 모델 버전 업데이트
            current_version = self.models[model_type]['version']
            major, minor, patch = map(int, current_version.split('.'))
            patch += 1
            if patch > 99:
                patch = 0
                minor += 1
            if minor > 99:
                minor = 0
                major += 1
            
            self.models[model_type].update({
                'version': f"{major}.{minor}.{patch}",
                'last_trained': datetime.now().isoformat()
            })
            
            # 학습 이력 저장
            self._save_auto_learning_history(model_type, 'train', old_accuracy, new_accuracy, improvement)
            
            logger.info(f"모델 {model_type} 학습 완료: {old_accuracy:.3f} -> {new_accuracy:.3f}")
            
        except Exception as e:
            logger.error(f"모델 {model_type} 학습 실패: {e}")
    
    def _check_performance_improvements(self):
        """성능 개선 체크"""
        try:
            for model_type, performance in self.model_performance.items():
                if performance['accuracy'] < 0.7:  # 정확도가 70% 미만인 경우
                    # 추가 학습 수행
                    self._train_model(model_type)
                    
                    # 알림 생성
                    self._create_alert(f"모델 {model_type}의 성능이 저하되어 추가 학습을 수행했습니다.")
        
        except Exception as e:
            logger.error(f"성능 개선 체크 실패: {e}")
    
    def _generate_insights(self):
        """예측 인사이트 생성"""
        try:
            insights = [
                {
                    'type': 'trend_analysis',
                    'title': '매출 증가 트렌드 감지',
                    'description': '최근 7일간 매출이 평균 15% 증가하는 트렌드가 감지되었습니다.',
                    'confidence': 0.85,
                    'impact_score': 0.8,
                    'recommendations': ['재고 확보', '인력 배치 최적화'],
                    'data_sources': ['sales_data', 'customer_flow']
                },
                {
                    'type': 'anomaly_detection',
                    'title': '비정상적인 고객 유입 패턴',
                    'description': '평소 대비 30% 증가한 고객 유입이 감지되었습니다.',
                    'confidence': 0.9,
                    'impact_score': 0.7,
                    'recommendations': ['서비스 품질 모니터링', '대기 시간 관리'],
                    'data_sources': ['customer_flow', 'service_metrics']
                },
                {
                    'type': 'seasonal_pattern',
                    'title': '주말 매출 패턴 분석',
                    'description': '주말 매출이 평일 대비 평균 40% 높은 패턴이 확인되었습니다.',
                    'confidence': 0.95,
                    'impact_score': 0.6,
                    'recommendations': ['주말 인력 배치 증가', '주말 특별 메뉴 고려'],
                    'data_sources': ['sales_data', 'staffing_data']
                }
            ]
            
            for insight in insights:
                insight['timestamp'] = datetime.now().isoformat()
                self._save_insight(insight)
            
        except Exception as e:
            logger.error(f"인사이트 생성 실패: {e}")
    
    def _create_alert(self, message: str):
        """알림 생성"""
        try:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'type': 'ai_model_alert',
                'severity': 'warning',
                'message': message
            }
            
            # 실제로는 알림 시스템에 전송
            logger.warning(f"AI 모델 알림: {message}")
            
        except Exception as e:
            logger.error(f"알림 생성 실패: {e}")
    
    def predict_sales_advanced(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """고도화된 매출 예측"""
        try:
            predictions = []
            
            for day in range(days_ahead):
                # 고급 예측 로직 (계절성, 트렌드, 외부 요인 고려)
                base_sales = 1000000
                
                # 계절성 요인
                day_of_week = (datetime.now() + timedelta(days=day)).weekday()
                day_multiplier = {
                    0: 0.8,   # 월요일
                    1: 0.9,   # 화요일
                    2: 1.0,   # 수요일
                    3: 1.1,   # 목요일
                    4: 1.3,   # 금요일
                    5: 1.5,   # 토요일
                    6: 1.4    # 일요일
                }.get(day_of_week, 1.0)
                
                # 트렌드 요인
                trend_factor = 1 + (day * 0.01)  # 1% 일일 증가
                
                # 외부 요인 (날씨, 이벤트 등)
                external_factor = random.uniform(0.9, 1.1)
                
                # 예측값 계산
                predicted_sales = base_sales * day_multiplier * trend_factor * external_factor
                
                # 신뢰도 계산
                confidence = max(0.6, 0.9 - (day * 0.03))
                
                prediction = {
                    'timestamp': (datetime.now() + timedelta(days=day)).isoformat(),
                    'prediction_type': 'sales',
                    'model_type': 'advanced_lstm',
                    'predicted_value': predicted_sales,
                    'confidence': confidence,
                    'features': {
                        'day_of_week': day_of_week,
                        'day_multiplier': day_multiplier,
                        'trend_factor': trend_factor,
                        'external_factor': external_factor
                    },
                    'metadata': {
                        'days_ahead': day + 1,
                        'model_version': self.models['sales']['version']
                    }
                }
                
                predictions.append(prediction)
                self.prediction_history.append(prediction)
            
            # 예측 결과 저장
            for prediction in predictions:
                self._save_prediction(prediction)
            
            return predictions
            
        except Exception as e:
            logger.error(f"고도화된 매출 예측 실패: {e}")
            return []
    
    def predict_inventory_advanced(self, items: List[str]) -> Dict[str, Dict[str, Any]]:
        """고도화된 재고 예측"""
        try:
            predictions = {}
            
            for item in items:
                # 고급 재고 예측 로직
                current_stock = random.randint(50, 200)
                daily_consumption = random.uniform(10, 30)
                lead_time = random.randint(1, 7)
                safety_stock = daily_consumption * 2
                
                # 예측된 필요량
                predicted_need = (daily_consumption * lead_time) + safety_stock - current_stock
                predicted_need = max(0, predicted_need)
                
                # 재고 부족 위험도 계산
                days_until_stockout = current_stock / daily_consumption if daily_consumption > 0 else float('inf')
                risk_level = 'low' if days_until_stockout > 7 else 'medium' if days_until_stockout > 3 else 'high'
                
                # 신뢰도 계산
                confidence = 0.9 if current_stock > safety_stock else 0.7
                
                prediction = {
                    'timestamp': datetime.now().isoformat(),
                    'prediction_type': 'inventory',
                    'model_type': 'advanced_random_forest',
                    'predicted_value': predicted_need,
                    'confidence': confidence,
                    'features': {
                        'current_stock': current_stock,
                        'daily_consumption': daily_consumption,
                        'lead_time': lead_time,
                        'safety_stock': safety_stock,
                        'days_until_stockout': days_until_stockout,
                        'risk_level': risk_level
                    },
                    'metadata': {
                        'item_name': item,
                        'model_version': self.models['inventory']['version']
                    }
                }
                
                predictions[item] = prediction
                self.prediction_history.append(prediction)
            
            # 예측 결과 저장
            for prediction in predictions.values():
                self._save_prediction(prediction)
            
            return predictions
            
        except Exception as e:
            logger.error(f"고도화된 재고 예측 실패: {e}")
            return {}
    
    def predict_staffing_advanced(self, target_date: datetime) -> Dict[str, Any]:
        """고도화된 인력 예측"""
        try:
            # 고급 인력 예측 로직
            day_of_week = target_date.weekday()
            month = target_date.month
            
            # 기본 인력
            base_staff = 10
            
            # 요일별 조정
            day_multipliers = {
                0: 1.1,  # 월요일
                1: 1.0,  # 화요일
                2: 1.0,  # 수요일
                3: 1.1,  # 목요일
                4: 1.3,  # 금요일
                5: 1.5,  # 토요일
                6: 1.4   # 일요일
            }
            
            # 계절성 조정
            seasonal_multipliers = {
                12: 1.2, 1: 1.2,   # 12월, 1월 (성수기)
                7: 1.3, 8: 1.3,   # 7월, 8월 (성수기)
                2: 0.9, 3: 0.9,   # 2월, 3월 (비수기)
                9: 1.0, 10: 1.0, 11: 1.0  # 평상시
            }
            
            day_multiplier = day_multipliers.get(day_of_week, 1.0)
            seasonal_multiplier = seasonal_multipliers.get(month, 1.0)
            
            predicted_staff = base_staff * day_multiplier * seasonal_multiplier
            confidence = 0.85
            
            prediction = {
                'timestamp': target_date.isoformat(),
                'prediction_type': 'staffing',
                'model_type': 'advanced_gradient_boosting',
                'predicted_value': predicted_staff,
                'confidence': confidence,
                'features': {
                    'base_staff': base_staff,
                    'day_of_week': day_of_week,
                    'day_multiplier': day_multiplier,
                    'month': month,
                    'seasonal_multiplier': seasonal_multiplier
                },
                'metadata': {
                    'target_date': target_date.isoformat(),
                    'model_version': self.models['staffing']['version']
                }
            }
            
            self.prediction_history.append(prediction)
            self._save_prediction(prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"고도화된 인력 예측 실패: {e}")
            return {}
    
    def get_prediction_accuracy(self, prediction_type: str, days_back: int = 30) -> Dict[str, Any]:
        """예측 정확도 분석"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # 실제값과 예측값 비교 (더미 데이터)
            actual_values = []
            predicted_values = []
            
            for i in range(days_back):
                # 더미 실제값과 예측값 생성
                actual = random.uniform(800000, 1200000)
                predicted = actual * random.uniform(0.9, 1.1)
                
                actual_values.append(actual)
                predicted_values.append(predicted)
            
            # 정확도 메트릭 계산
            errors = [abs(a - p) for a, p in zip(actual_values, predicted_values)]
            mae = np.mean(errors)
            mse = np.mean([(a - p) ** 2 for a, p in zip(actual_values, predicted_values)])
            rmse = np.sqrt(mse)
            
            # R-squared 계산
            mean_actual = np.mean(actual_values)
            ss_res = sum((a - p) ** 2 for a, p in zip(actual_values, predicted_values))
            ss_tot = sum((a - mean_actual) ** 2 for a in actual_values)
            r2_score = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # 정확도 계산
            accuracy = 1 - (mae / mean_actual) if mean_actual != 0 else 0
            
            return {
                'prediction_type': prediction_type,
                'days_analyzed': days_back,
                'metrics': {
                    'mae': float(mae),
                    'mse': float(mse),
                    'rmse': float(rmse),
                    'r2_score': float(r2_score),
                    'accuracy': float(accuracy)
                },
                'data_points': len(actual_values),
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"예측 정확도 분석 실패: {e}")
            return {}
    
    def _save_prediction(self, prediction: Dict[str, Any]):
        """예측 결과를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO predictions (
                    timestamp, prediction_type, model_type, predicted_value,
                    confidence, features, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction['timestamp'],
                prediction['prediction_type'],
                prediction['model_type'],
                prediction['predicted_value'],
                prediction['confidence'],
                json.dumps(prediction.get('features', {})),
                json.dumps(prediction.get('metadata', {}))
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"예측 결과 저장 실패: {e}")
    
    def _save_auto_learning_history(self, model_type: str, action: str, 
                                   performance_before: float, performance_after: float, 
                                   improvement: float):
        """자동 학습 이력을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO auto_learning_history (
                    timestamp, model_type, action, performance_before,
                    performance_after, improvement, training_data_size, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                model_type,
                action,
                performance_before,
                performance_after,
                improvement,
                self.model_performance[model_type]['training_samples'],
                f"자동 학습으로 성능이 {improvement:.3f} 개선되었습니다."
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"자동 학습 이력 저장 실패: {e}")
    
    def _save_insight(self, insight: Dict[str, Any]):
        """인사이트를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO prediction_insights (
                    timestamp, insight_type, title, description,
                    confidence, impact_score, recommendations, data_sources
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight['timestamp'],
                insight['type'],
                insight['title'],
                insight['description'],
                insight['confidence'],
                insight['impact_score'],
                json.dumps(insight['recommendations']),
                json.dumps(insight['data_sources'])
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"인사이트 저장 실패: {e}")
    
    def get_models_status(self) -> Dict[str, Any]:
        """모델 상태 조회"""
        return {
            'models': self.models,
            'performance': self.model_performance,
            'auto_learning_active': self.auto_learning_active,
            'total_predictions': len(self.prediction_history),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_recent_predictions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """최근 예측 결과 조회"""
        return list(self.prediction_history)[-limit:]
    
    def get_auto_learning_history(self) -> List[Dict[str, Any]]:
        """자동 학습 이력 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM auto_learning_history 
                ORDER BY timestamp DESC LIMIT 20
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'model_type': row[2],
                    'action': row[3],
                    'performance_before': row[4],
                    'performance_after': row[5],
                    'improvement': row[6],
                    'training_data_size': row[7],
                    'description': row[8]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"자동 학습 이력 조회 실패: {e}")
            return []
    
    def get_insights(self, insight_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """인사이트 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if insight_type:
                cursor.execute('''
                    SELECT * FROM prediction_insights 
                    WHERE insight_type = ? 
                    ORDER BY timestamp DESC LIMIT 10
                ''', (insight_type,))
            else:
                cursor.execute('''
                    SELECT * FROM prediction_insights 
                    ORDER BY timestamp DESC LIMIT 10
                ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            insights = []
            for row in rows:
                insights.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'insight_type': row[2],
                    'title': row[3],
                    'description': row[4],
                    'confidence': row[5],
                    'impact_score': row[6],
                    'recommendations': json.loads(row[7]) if row[7] else [],
                    'data_sources': json.loads(row[8]) if row[8] else []
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"인사이트 조회 실패: {e}")
            return []

# 전역 인스턴스 생성
advanced_ai_prediction_system = AdvancedAIPredictionSystem()

# API 엔드포인트들
@advanced_ai_prediction_bp.route('/start-auto-learning', methods=['POST'])
def start_auto_learning():
    """자동 학습 시작"""
    try:
        result = advanced_ai_prediction_system.start_auto_learning()
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"자동 학습 시작 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_ai_prediction_bp.route('/stop-auto-learning', methods=['POST'])
def stop_auto_learning():
    """자동 학습 중지"""
    try:
        result = advanced_ai_prediction_system.stop_auto_learning()
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"자동 학습 중지 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_ai_prediction_bp.route('/predict/sales', methods=['POST'])
def predict_sales_advanced():
    """고도화된 매출 예측"""
    try:
        data = request.get_json() or {}
        days_ahead = data.get('days_ahead', 7)
        
        predictions = advanced_ai_prediction_system.predict_sales_advanced(days_ahead)
        
        return jsonify({
            'success': True,
            'data': {
                'predictions': predictions,
                'total_predictions': len(predictions)
            }
        })
    except Exception as e:
        logger.error(f"고도화된 매출 예측 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_ai_prediction_bp.route('/predict/inventory', methods=['POST'])
def predict_inventory_advanced():
    """고도화된 재고 예측"""
    try:
        data = request.get_json() or {}
        items = data.get('items', ['item1', 'item2', 'item3'])
        
        predictions = advanced_ai_prediction_system.predict_inventory_advanced(items)
        
        return jsonify({
            'success': True,
            'data': {
                'predictions': predictions,
                'total_items': len(predictions)
            }
        })
    except Exception as e:
        logger.error(f"고도화된 재고 예측 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_ai_prediction_bp.route('/predict/staffing', methods=['POST'])
def predict_staffing_advanced():
    """고도화된 인력 예측"""
    try:
        data = request.get_json() or {}
        target_date_str = data.get('target_date')
        
        if not target_date_str:
            target_date = datetime.now() + timedelta(days=7)
        else:
            target_date = datetime.fromisoformat(target_date_str.replace('Z', '+00:00'))
        
        prediction = advanced_ai_prediction_system.predict_staffing_advanced(target_date)
        
        return jsonify({
            'success': True,
            'data': prediction
        })
    except Exception as e:
        logger.error(f"고도화된 인력 예측 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_ai_prediction_bp.route('/accuracy/<prediction_type>', methods=['GET'])
def get_prediction_accuracy(prediction_type: str):
    """예측 정확도 분석"""
    try:
        days_back = request.args.get('days_back', 30, type=int)
        
        accuracy_data = advanced_ai_prediction_system.get_prediction_accuracy(prediction_type, days_back)
        
        return jsonify({
            'success': True,
            'data': accuracy_data
        })
    except Exception as e:
        logger.error(f"예측 정확도 분석 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_ai_prediction_bp.route('/models/status', methods=['GET'])
def get_models_status():
    """모델 상태 조회"""
    try:
        status = advanced_ai_prediction_system.get_models_status()
        
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logger.error(f"모델 상태 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_ai_prediction_bp.route('/predictions/recent', methods=['GET'])
def get_recent_predictions():
    """최근 예측 결과 조회"""
    try:
        limit = request.args.get('limit', 50, type=int)
        predictions = advanced_ai_prediction_system.get_recent_predictions(limit)
        
        return jsonify({
            'success': True,
            'data': {
                'predictions': predictions,
                'count': len(predictions)
            }
        })
    except Exception as e:
        logger.error(f"최근 예측 결과 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_ai_prediction_bp.route('/auto-learning/history', methods=['GET'])
def get_auto_learning_history():
    """자동 학습 이력 조회"""
    try:
        history = advanced_ai_prediction_system.get_auto_learning_history()
        
        return jsonify({
            'success': True,
            'data': {
                'history': history,
                'count': len(history)
            }
        })
    except Exception as e:
        logger.error(f"자동 학습 이력 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_ai_prediction_bp.route('/insights', methods=['GET'])
def get_insights():
    """인사이트 조회"""
    try:
        insight_type = request.args.get('type')
        insights = advanced_ai_prediction_system.get_insights(insight_type)
        
        return jsonify({
            'success': True,
            'data': {
                'insights': insights,
                'count': len(insights)
            }
        })
    except Exception as e:
        logger.error(f"인사이트 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_ai_prediction_bp.route('/dashboard', methods=['GET'])
def get_ai_dashboard():
    """AI 예측 대시보드 데이터"""
    try:
        # 모델 상태
        models_status = advanced_ai_prediction_system.get_models_status()
        
        # 최근 예측
        recent_predictions = advanced_ai_prediction_system.get_recent_predictions(10)
        
        # 자동 학습 이력
        learning_history = advanced_ai_prediction_system.get_auto_learning_history()
        
        # 인사이트
        insights = advanced_ai_prediction_system.get_insights()
        
        # 예측 정확도
        sales_accuracy = advanced_ai_prediction_system.get_prediction_accuracy('sales', 30)
        
        dashboard_data = {
            'models_status': models_status,
            'recent_predictions': recent_predictions,
            'learning_summary': {
                'active': models_status['auto_learning_active'],
                'recent_improvements': len([h for h in learning_history if h['improvement'] > 0]),
                'total_models': len(models_status['models'])
            },
            'insights_summary': {
                'total_insights': len(insights),
                'high_confidence_insights': len([i for i in insights if i['confidence'] > 0.8]),
                'high_impact_insights': len([i for i in insights if i['impact_score'] > 0.7])
            },
            'accuracy_summary': {
                'sales_accuracy': sales_accuracy.get('metrics', {}).get('accuracy', 0),
                'overall_accuracy': np.mean([
                    models_status['performance'][model]['accuracy'] 
                    for model in models_status['performance']
                ])
            },
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        logger.error(f"AI 대시보드 데이터 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 