"""
AI 예측 시스템
머신러닝 기반 예측 및 분석 기능
"""

import logging
import numpy as np

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)

class PredictionType(Enum):
    """예측 타입"""
    SALES = "sales"
    INVENTORY = "inventory"
    STAFFING = "staffing"
    CUSTOMER_FLOW = "customer_flow"
    REVENUE = "revenue"

class ModelType(Enum):
    """모델 타입"""
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    LSTM = "lstm"
    ARIMA = "arima"
    PROPHET = "prophet"

@dataclass
class PredictionResult:
    """예측 결과"""
    prediction_type: PredictionType
    model_type: ModelType
    predicted_value: float
    confidence: float
    timestamp: datetime
    features: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class ModelPerformance:
    """모델 성능"""
    model_type: ModelType
    mae: float  # Mean Absolute Error
    mse: float  # Mean Squared Error
    rmse: float  # Root Mean Squared Error
    r2_score: float  # R-squared
    accuracy: float
    last_updated: datetime

class AIPredictionEngine:
    """AI 예측 엔진"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, ModelPerformance] = {}
        self.feature_scalers: Dict[str, Any] = {}
        self.prediction_history: List[PredictionResult] = []
        
        # 기본 모델 초기화
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """기본 모델 초기화"""
        try:
            # 간단한 선형 회귀 모델 (실제로는 scikit-learn 사용)
            logger.info("AI 예측 엔진 초기화")
            
            # 더미 성능 메트릭 설정
            for model_type in ModelType:
                self.performance_metrics[model_type.value] = ModelPerformance(
                    model_type=model_type,
                    mae=0.1,
                    mse=0.01,
                    rmse=0.1,
                    r2_score=0.85,
                    accuracy=0.9,
                    last_updated=datetime.utcnow()
                )
                
        except Exception as e:
            logger.error(f"AI 예측 엔진 초기화 실패: {e}")
    
    def predict_sales(self, 
                     historical_data: List[Dict[str, Any]], 
                     days_ahead: int = 7,
                     model_type: ModelType = ModelType.LINEAR_REGRESSION) -> List[PredictionResult]:
        """매출 예측"""
        try:
            predictions = []
            
            # 더미 예측 데이터 생성
            for i in range(days_ahead):
                # 간단한 선형 트렌드 기반 예측
                base_value = 1000000  # 기본 매출
                trend_factor = 1 + (i * 0.02)  # 2% 증가 트렌드
                seasonality = 1 + 0.1 * np.sin(i * 2 * np.pi / 7)  # 주간 계절성
                noise = np.random.normal(0, 0.05)  # 5% 노이즈
                
                predicted_value = base_value * trend_factor * seasonality * (1 + noise)
                confidence = max(0.7, 0.9 - (i * 0.02))  # 시간이 지날수록 신뢰도 감소
                
                prediction = PredictionResult(
                    prediction_type=PredictionType.SALES,
                    model_type=model_type,
                    predicted_value=predicted_value,
                    confidence=confidence,
                    timestamp=datetime.utcnow() + timedelta(days=i),
                    features={
                        'trend_factor': trend_factor,
                        'seasonality': seasonality,
                        'noise': noise
                    },
                    metadata={
                        'days_ahead': i + 1,
                        'data_points': len(historical_data)
                    }
                )
                
                predictions.append(prediction)
                self.prediction_history.append(prediction)
            
            logger.info(f"매출 예측 완료: {days_ahead}일")
            return predictions
            
        except Exception as e:
            logger.error(f"매출 예측 실패: {e}")
            return []
    
    def predict_inventory_needs(self, 
                              current_inventory: Dict[str, int],
                              sales_history: List[Dict[str, Any]],
                              days_ahead: int = 7) -> Dict[str, PredictionResult]:
        """재고 필요량 예측"""
        try:
            predictions = {}
            
            for item_name, current_stock in current_inventory.items():
                # 간단한 재고 예측 로직
                avg_daily_usage = 50  # 평균 일일 사용량 (더미)
                safety_stock = 20  # 안전 재고
                
                # 예측된 필요량
                predicted_need = (avg_daily_usage * days_ahead) + safety_stock - current_stock
                predicted_need = max(0, predicted_need)  # 음수 방지
                
                # 신뢰도 계산
                confidence = 0.8 if current_stock > safety_stock else 0.6
                
                prediction = PredictionResult(
                    prediction_type=PredictionType.INVENTORY,
                    model_type=ModelType.LINEAR_REGRESSION,
                    predicted_value=predicted_need,
                    confidence=confidence,
                    timestamp=datetime.utcnow(),
                    features={
                        'current_stock': current_stock,
                        'avg_daily_usage': avg_daily_usage,
                        'safety_stock': safety_stock
                    },
                    metadata={
                        'item_name': item_name,
                        'days_ahead': days_ahead
                    }
                )
                
                predictions[item_name] = prediction
                self.prediction_history.append(prediction)
            
            logger.info(f"재고 예측 완료: {len(predictions)}개 품목")
            return predictions
            
        except Exception as e:
            logger.error(f"재고 예측 실패: {e}")
            return {}
    
    def predict_staffing_needs(self,
                             historical_data: List[Dict[str, Any]],
                             target_date: datetime) -> Optional[PredictionResult]:
        """인력 필요량 예측"""
        try:
            # 간단한 인력 예측 로직
            base_staff = 10  # 기본 인력
            day_of_week = target_date.weekday()
            
            # 요일별 인력 조정
            day_multipliers = {
                0: 1.2,  # 월요일
                1: 1.1,  # 화요일
                2: 1.0,  # 수요일
                3: 1.1,  # 목요일
                4: 1.3,  # 금요일
                5: 1.5,  # 토요일
                6: 1.4   # 일요일
            }
            
            predicted_staff = base_staff * day_multipliers.get(day_of_week, 1.0)
            confidence = 0.85
            
            prediction = PredictionResult(
                prediction_type=PredictionType.STAFFING,
                model_type=ModelType.LINEAR_REGRESSION,
                predicted_value=predicted_staff,
                confidence=confidence,
                timestamp=target_date,
                features={
                    'base_staff': base_staff,
                    'day_of_week': day_of_week,
                    'day_multiplier': day_multipliers.get(day_of_week, 1.0)
                },
                metadata={
                    'target_date': target_date.isoformat(),
                    'data_points': len(historical_data)
                }
            )
            
            self.prediction_history.append(prediction)
            logger.info(f"인력 예측 완료: {target_date.date()}")
            return prediction
            
        except Exception as e:
            logger.error(f"인력 예측 실패: {e}")
            return None
    
    def predict_customer_flow(self,
                            historical_data: List[Dict[str, Any]],
                            hours_ahead: int = 24) -> List[PredictionResult]:
        """고객 유입 예측"""
        try:
            predictions = []
            
            for hour in range(hours_ahead):
                # 시간대별 고객 유입 패턴
                hour_of_day = hour % 24
                
                # 시간대별 계수 (더미 데이터)
                hour_coefficients = {
                    6: 0.3,  7: 0.5,  8: 0.8,  9: 1.0,  10: 1.2, 11: 1.5,  # 오전
                    12: 2.0, 13: 1.8, 14: 1.5, 15: 1.3, 16: 1.4, 17: 1.6,  # 오후
                    18: 2.2, 19: 2.5, 20: 2.0, 21: 1.5, 22: 1.0, 23: 0.6,  # 저녁
                    0: 0.2,  1: 0.1,  2: 0.1,  3: 0.1,  4: 0.1,  5: 0.2   # 새벽
                }
                
                base_customers = 100
                coefficient = hour_coefficients.get(hour_of_day, 1.0)
                predicted_customers = base_customers * coefficient
                
                # 신뢰도 계산
                confidence = 0.9 if 6 <= hour_of_day <= 22 else 0.7
                
                prediction = PredictionResult(
                    prediction_type=PredictionType.CUSTOMER_FLOW,
                    model_type=ModelType.LINEAR_REGRESSION,
                    predicted_value=predicted_customers,
                    confidence=confidence,
                    timestamp=datetime.utcnow() + timedelta(hours=hour),
                    features={
                        'hour_of_day': hour_of_day,
                        'coefficient': coefficient,
                        'base_customers': base_customers
                    },
                    metadata={
                        'hours_ahead': hour + 1
                    }
                )
                
                predictions.append(prediction)
                self.prediction_history.append(prediction)
            
            logger.info(f"고객 유입 예측 완료: {hours_ahead}시간")
            return predictions
            
        except Exception as e:
            logger.error(f"고객 유입 예측 실패: {e}")
            return []
    
    def get_model_performance(self, model_type: ModelType) -> Optional[ModelPerformance]:
        """모델 성능 조회"""
        return self.performance_metrics.get(model_type.value)
    
    def update_model_performance(self, 
                               model_type: ModelType,
                               actual_values: List[float],
                               predicted_values: List[float]) -> bool:
        """모델 성능 업데이트"""
        try:
            if len(actual_values) != len(predicted_values):
                return False
            
            # 성능 메트릭 계산
            errors = [abs(a - p) for a, p in zip(actual_values, predicted_values)]
            squared_errors = [(a - p) ** 2 for a, p in zip(actual_values, predicted_values)]
            
            mae = float(np.mean(errors))
            mse = float(np.mean(squared_errors))
            rmse = float(np.sqrt(mse))
            
            # R-squared 계산
            mean_actual = float(np.mean(actual_values))
            ss_res = sum((a - p) ** 2 for a, p in zip(actual_values, predicted_values))
            ss_tot = sum((a - mean_actual) ** 2 for a in actual_values)
            r2_score = float(1 - (ss_res / ss_tot) if ss_tot != 0 else 0)
            
            # 정확도 계산 (간단한 버전)
            accuracy = float(1 - (mae / mean_actual) if mean_actual != 0 else 0)
            
            # 성능 메트릭 업데이트
            self.performance_metrics[model_type.value] = ModelPerformance(
                model_type=model_type,
                mae=mae,
                mse=mse,
                rmse=rmse,
                r2_score=r2_score,
                accuracy=accuracy,
                last_updated=datetime.utcnow()
            )
            
            logger.info(f"모델 성능 업데이트 완료: {model_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"모델 성능 업데이트 실패: {e}")
            return False
    
    def get_prediction_history(self, 
                             prediction_type: Optional[PredictionType] = None,
                             limit: int = 100) -> List[PredictionResult]:
        """예측 히스토리 조회"""
        history = self.prediction_history
        
        if prediction_type:
            history = [p for p in history if p.prediction_type == prediction_type]
        
        # 최신 순으로 정렬
        history.sort(key=lambda x: x.timestamp, reverse=True)
        
        return history[:limit]
    
    def export_predictions(self, 
                          prediction_type: Optional[PredictionType] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """예측 데이터 내보내기"""
        try:
            history = self.get_prediction_history(prediction_type)
            
            # 날짜 필터링
            if start_date:
                history = [p for p in history if p.timestamp >= start_date]
            if end_date:
                history = [p for p in history if p.timestamp <= end_date]
            
            # JSON 직렬화 가능한 형태로 변환
            export_data = []
            for prediction in history:
                export_data.append({
                    'prediction_type': prediction.prediction_type.value,
                    'model_type': prediction.model_type.value,
                    'predicted_value': prediction.predicted_value,
                    'confidence': prediction.confidence,
                    'timestamp': prediction.timestamp.isoformat(),
                    'features': prediction.features,
                    'metadata': prediction.metadata
                })
            
            return {
                'success': True,
                'predictions': export_data,
                'total_count': len(export_data),
                'export_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"예측 데이터 내보내기 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# 전역 AI 예측 엔진 인스턴스
ai_prediction_engine = AIPredictionEngine() 