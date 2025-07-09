"""
직원 최적화 AI 모델
TensorFlow 기반 직원 스케줄링 및 성과 최적화
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import joblib
import os
from datetime import datetime, timedelta
import logging
from typing import Optional, List, Dict, Any, Union

# TensorFlow 공통 유틸리티 사용
from .tensorflow_utils import (
    TENSORFLOW_AVAILABLE, tf, check_tensorflow_available,
    create_sequential_model, create_callbacks, compile_model,
    load_model_safely, save_model_safely, setup_ai_logging
)

class StaffOptimizationModel:
    def __init__(self, model_path='ai_models/saved_models/staff_optimization.h5'):
        check_tensorflow_available()
            
        self.model_path = model_path
        self.scaler = MinMaxScaler()
        self.model: Optional[Any] = None
        self.features = [
            'customer_count', 'sales_volume', 'day_of_week', 'month', 
            'holiday', 'weather_score', 'staff_count', 'avg_order_value'
        ]
        
        # 로깅 설정
        self.logger = setup_ai_logging()
        
    def create_model(self, input_shape):
        """직원 최적화 모델 생성"""
        check_tensorflow_available()
        
        layers_config = [
            {'type': 'Input', 'params': {'shape': input_shape}},
            {'type': 'Dense', 'params': {'units': 128, 'activation': 'relu'}},
            {'type': 'Dropout', 'params': {'rate': 0.3}},
            {'type': 'Dense', 'params': {'units': 64, 'activation': 'relu'}},
            {'type': 'Dropout', 'params': {'rate': 0.2}},
            {'type': 'Dense', 'params': {'units': 32, 'activation': 'relu'}},
            {'type': 'Dense', 'params': {'units': 1, 'activation': 'linear'}}
        ]
        
        model = create_sequential_model(layers_config)
        compile_model(model, optimizer='adam', loss='mse', metrics=['mae'])
        
        return model
    
    def generate_sample_data(self, days=365):
        """샘플 데이터 생성"""
        dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
        
        # 고객 수 (계절성 + 트렌드)
        base_customers = 200
        seasonal_factor = np.sin(2 * np.pi * np.arange(days) / 365) * 0.4
        trend_factor = np.arange(days) * 0.5
        noise = np.random.normal(0, 20, days)
        customer_count = np.maximum(base_customers + seasonal_factor * base_customers + trend_factor + noise, 50)
        
        # 매출량
        sales_volume = customer_count * np.random.uniform(15, 25, days)
        
        # 기타 특성들
        day_of_week = [d.weekday() for d in dates]
        month = [d.month for d in dates]
        holiday = np.random.choice([0, 1], days, p=[0.95, 0.05])  # 5% 확률로 휴일
        weather_score = np.random.uniform(0.3, 1.0, days)  # 날씨 점수
        staff_count = np.random.randint(3, 12, days)  # 현재 직원 수
        avg_order_value = np.random.uniform(12, 18, days)  # 평균 주문 금액
        
        # 최적 직원 수 (목표 변수)
        optimal_staff = np.ceil(customer_count / 25 + np.random.normal(0, 0.5, days))
        optimal_staff = np.maximum(optimal_staff, 3)  # 최소 3명
        
        data = pd.DataFrame({
            'date': dates,
            'customer_count': customer_count,
            'sales_volume': sales_volume,
            'day_of_week': day_of_week,
            'month': month,
            'holiday': holiday,
            'weather_score': weather_score,
            'staff_count': staff_count,
            'avg_order_value': avg_order_value,
            'optimal_staff': optimal_staff
        })
        
        return data
    
    def prepare_data(self, data):
        """데이터 전처리"""
        # 특성 정규화
        scaled_features = self.scaler.fit_transform(data[self.features])
        
        # 목표 변수
        target = data['optimal_staff'].values
        
        return scaled_features, target
    
    def train(self, data=None, epochs=100, batch_size=32):
        """모델 학습"""
        check_tensorflow_available()
        
        if data is None:
            data = self.generate_sample_data()
        
        self.logger.info("데이터 전처리 시작...")
        X, y = self.prepare_data(data)
        
        # 학습/검증 데이터 분할
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        self.logger.info(f"학습 데이터: {X_train.shape}, 검증 데이터: {X_val.shape}")
        
        # 모델 생성
        self.model = self.create_model((X_train.shape[1],))
        
        # 콜백 설정
        callbacks = create_callbacks(self.model_path.replace('.h5', '.keras'), monitor='val_loss', patience=10)
        
        self.logger.info("모델 학습 시작...")
        if self.model is not None:
            history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )
        else:
            raise RuntimeError("모델 생성에 실패했습니다.")
        
        # 스케일러 저장
        scaler_path = self.model_path.replace('.h5', '_scaler.pkl')
        joblib.dump(self.scaler, scaler_path)
        
        self.logger.info("모델 학습 완료!")
        return history
    
    def predict_optimal_staff(self, data):
        """최적 직원 수 예측"""
        check_tensorflow_available()
            
        if self.model is None:
            self.load_model()
        
        if self.model is None:
            raise RuntimeError("모델을 로드할 수 없습니다. 먼저 학습을 진행하세요.")
        
        # 데이터 전처리
        scaled_data = self.scaler.transform(data[self.features])
        
        # 예측
        if self.model is not None:
            predictions = self.model.predict(scaled_data)
            return np.ceil(predictions.flatten())  # 올림하여 정수로 변환
        else:
            raise RuntimeError("모델이 초기화되지 않았습니다.")
    
    def optimize_schedule(self, staff_data, constraints=None):
        """직원 스케줄 최적화"""
        if constraints is None:
            constraints = {
                'min_staff': 3,
                'max_staff': 15,
                'max_hours_per_day': 8,
                'min_break_hours': 1
            }
        
        # 최적 직원 수 예측
        optimal_staff = self.predict_optimal_staff(staff_data)
        
        # 제약 조건 적용
        optimal_staff = np.clip(optimal_staff, constraints['min_staff'], constraints['max_staff'])
        
        return {
            'optimal_staff_count': optimal_staff,
            'recommended_shifts': self._generate_shifts(optimal_staff, constraints),
            'efficiency_score': self._calculate_efficiency(staff_data, optimal_staff)
        }
    
    def _generate_shifts(self, staff_count, constraints):
        """근무 시간대 생성"""
        shifts = []
        for i, count in enumerate(staff_count):
            # 간단한 2교대 시스템
            morning_shift = max(1, int(count * 0.6))
            evening_shift = count - morning_shift
            
            shifts.append({
                'date': i,
                'morning_shift': morning_shift,
                'evening_shift': evening_shift,
                'total_staff': count
            })
        
        return shifts
    
    def _calculate_efficiency(self, data, optimal_staff):
        """효율성 점수 계산"""
        current_staff = data['staff_count'].values
        customer_count = data['customer_count'].values
        
        # 고객 대비 직원 비율 효율성
        efficiency = 1 - np.abs(optimal_staff - current_staff) / np.maximum(optimal_staff, 1)
        
        return np.mean(efficiency)
    
    def load_model(self):
        """저장된 모델 로드"""
        check_tensorflow_available()
        
        keras_path = self.model_path.replace('.h5', '.keras')
        if os.path.exists(keras_path):
            self.model = load_model_safely(keras_path)
            scaler_path = keras_path.replace('.keras', '_scaler.pkl')
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
            self.logger.info("모델 로드 완료")
        else:
            raise FileNotFoundError("모델 파일을 찾을 수 없습니다. 먼저 학습을 진행하세요.")
    
    def evaluate(self, test_data):
        """모델 성능 평가"""
        check_tensorflow_available()
            
        if self.model is None:
            self.load_model()
        
        if self.model is None:
            raise RuntimeError("모델을 로드할 수 없습니다. 먼저 학습을 진행하세요.")
        
        X_test, y_test = self.prepare_data(test_data)
        if self.model is not None:
            predictions = self.model.predict(X_test)
        else:
            raise RuntimeError("모델이 초기화되지 않았습니다.")
        
        mse = mean_squared_error(y_test, predictions.flatten())
        mae = np.mean(np.abs(y_test - predictions.flatten()))
        rmse = np.sqrt(mse)
        
        return {
            'mse': mse,
            'mae': mae,
            'rmse': rmse,
            'predictions': predictions.flatten(),
            'actual': y_test
        }

# 사용 예시
if __name__ == "__main__":
    try:
        # 모델 인스턴스 생성
        model = StaffOptimizationModel()
        
        # 샘플 데이터로 학습
        print("직원 최적화 모델 학습 시작...")
        history = model.train(epochs=50)
        
        # 예측 테스트
        test_data = model.generate_sample_data(days=30)
        optimal_staff = model.predict_optimal_staff(test_data)
        
        print(f"최적 직원 수 예측: {optimal_staff}")
        
        # 스케줄 최적화
        optimization_result = model.optimize_schedule(test_data)
        print(f"최적화 결과: {optimization_result}")
        
        # 성능 평가
        evaluation = model.evaluate(test_data)
        print(f"모델 성능 - RMSE: {evaluation['rmse']:.2f}, MAE: {evaluation['mae']:.2f}")
        
    except ImportError as e:
        print(f"TensorFlow 오류: {e}")
        print("TensorFlow를 설치하려면: pip install tensorflow")
    except Exception as e:
        print(f"오류 발생: {e}") 