"""
재고 예측 AI 모델
TensorFlow 기반 재고 수요 예측 및 발주 최적화
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

class InventoryForecastingModel:
    def __init__(self, model_path='ai_models/saved_models/inventory_forecasting.h5'):
        check_tensorflow_available()
            
        self.model_path = model_path
        self.scaler = MinMaxScaler()
        self.model: Optional[Any] = None
        self.sequence_length = 14  # 2주 데이터로 다음 주 예측
        self.features = [
            'sales_volume', 'customer_count', 'day_of_week', 'month',
            'holiday', 'promotion', 'current_stock', 'reorder_point'
        ]
        
        # 로깅 설정
        self.logger = setup_ai_logging()
        
    def create_model(self, input_shape):
        """재고 예측 모델 생성"""
        check_tensorflow_available()
        
        layers_config = [
            {'type': 'Input', 'params': {'shape': input_shape}},
            {'type': 'LSTM', 'params': {'units': 64, 'return_sequences': True}},
            {'type': 'Dropout', 'params': {'rate': 0.2}},
            {'type': 'LSTM', 'params': {'units': 32, 'return_sequences': False}},
            {'type': 'Dropout', 'params': {'rate': 0.2}},
            {'type': 'Dense', 'params': {'units': 16, 'activation': 'relu'}},
            {'type': 'Dense', 'params': {'units': 1, 'activation': 'linear'}}
        ]
        
        model = create_sequential_model(layers_config)
        compile_model(model, optimizer='adam', loss='mse', metrics=['mae'])
        
        return model
    
    def generate_sample_data(self, days=365):
        """샘플 데이터 생성"""
        dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
        
        # 매출량 (계절성 + 트렌드)
        base_sales = 1000
        seasonal_factor = np.sin(2 * np.pi * np.arange(days) / 365) * 0.3
        trend_factor = np.arange(days) * 2
        noise = np.random.normal(0, 100, days)
        sales_volume = np.maximum(base_sales + seasonal_factor * base_sales + trend_factor + noise, 100)
        
        # 고객 수
        customer_count = sales_volume / 10 + np.random.normal(0, 10, days)
        
        # 기타 특성들
        day_of_week = [d.weekday() for d in dates]
        month = [d.month for d in dates]
        holiday = np.random.choice([0, 1], days, p=[0.95, 0.05])
        promotion = np.random.choice([0, 1], days, p=[0.9, 0.1])
        current_stock = np.random.uniform(500, 2000, days)
        reorder_point = np.random.uniform(200, 500, days)
        
        # 수요량 (목표 변수)
        demand = sales_volume * np.random.uniform(0.8, 1.2, days)
        
        data = pd.DataFrame({
            'date': dates,
            'sales_volume': sales_volume,
            'customer_count': customer_count,
            'day_of_week': day_of_week,
            'month': month,
            'holiday': holiday,
            'promotion': promotion,
            'current_stock': current_stock,
            'reorder_point': reorder_point,
            'demand': demand
        })
        
        return data
    
    def prepare_data(self, data):
        """데이터 전처리 및 시퀀스 생성"""
        # 특성 정규화
        scaled_data = self.scaler.fit_transform(data[self.features])
        
        X, y = [], []
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i])
            y.append(data['demand'].iloc[i])
        
        return np.array(X), np.array(y)
    
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
        self.model = self.create_model((X_train.shape[1], X_train.shape[2]))
        
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
    
    def predict_demand(self, data, days_ahead=7):
        """수요 예측"""
        check_tensorflow_available()
            
        if self.model is None:
            self.load_model()
        
        if self.model is None:
            raise RuntimeError("모델을 로드할 수 없습니다. 먼저 학습을 진행하세요.")
        
        # 최근 데이터로 시퀀스 생성
        scaled_data = self.scaler.transform(data[self.features].tail(self.sequence_length))
        sequence = scaled_data.reshape(1, self.sequence_length, len(self.features))
        
        predictions = []
        current_sequence = sequence.copy()
        
        for _ in range(days_ahead):
            # 다음 날 예측
            if self.model is not None:
                pred = self.model.predict(current_sequence, verbose=0)
                predictions.append(pred[0, 0])
            else:
                raise RuntimeError("모델이 초기화되지 않았습니다.")
            
            # 시퀀스 업데이트
            new_row = current_sequence[0, -1].copy()
            new_row[0] = pred[0, 0]  # 예측된 매출로 업데이트
            current_sequence = np.roll(current_sequence, -1, axis=1)
            current_sequence[0, -1] = new_row
        
        return np.array(predictions)
    
    def optimize_inventory(self, data, lead_time=3, safety_stock_ratio=0.2):
        """재고 최적화"""
        # 수요 예측
        demand_forecast = self.predict_demand(data, days_ahead=lead_time + 7)
        
        # 안전 재고 계산
        current_stock = data['current_stock'].iloc[-1]
        avg_demand = np.mean(demand_forecast)
        safety_stock = avg_demand * safety_stock_ratio
        
        # 발주량 계산
        lead_time_demand = np.sum(demand_forecast[:lead_time])
        reorder_quantity = max(0, lead_time_demand + safety_stock - current_stock)
        
        # 재주문 시점 계산
        days_until_reorder = max(0, int((current_stock - safety_stock) / avg_demand))
        
        return {
            'demand_forecast': demand_forecast,
            'optimal_reorder_quantity': reorder_quantity,
            'reorder_point': safety_stock,
            'days_until_reorder': days_until_reorder,
            'current_stock_level': current_stock,
            'safety_stock': safety_stock
        }
    
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
        model = InventoryForecastingModel()
        
        # 샘플 데이터로 학습
        print("재고 예측 모델 학습 시작...")
        history = model.train(epochs=50)
        
        # 예측 테스트
        test_data = model.generate_sample_data(days=100)
        demand_forecast = model.predict_demand(test_data, days_ahead=7)
        
        print(f"수요 예측: {demand_forecast}")
        
        # 재고 최적화
        optimization_result = model.optimize_inventory(test_data)
        print(f"재고 최적화 결과: {optimization_result}")
        
        # 성능 평가
        evaluation = model.evaluate(test_data)
        print(f"모델 성능 - RMSE: {evaluation['rmse']:.2f}, MAE: {evaluation['mae']:.2f}")
        
    except ImportError as e:
        print(f"TensorFlow 오류: {e}")
        print("TensorFlow를 설치하려면: pip install tensorflow")
    except Exception as e:
        print(f"오류 발생: {e}") 