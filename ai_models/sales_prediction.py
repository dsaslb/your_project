import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
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

class SalesPredictionModel:
    def __init__(self, model_path='ai_models/saved_models/sales_prediction.h5'):
        check_tensorflow_available()
            
        self.model_path = model_path
        self.scaler = MinMaxScaler()
        self.model: Optional[Any] = None
        self.sequence_length = 30  # 30일 데이터로 다음 날 예측
        self.features = ['sales', 'staff_count', 'inventory_level', 'customer_count', 'day_of_week', 'month']
        
        # 로깅 설정
        self.logger = setup_ai_logging()
        
    def create_model(self, input_shape):
        """LSTM 기반 매출 예측 모델 생성"""
        check_tensorflow_available()
        
        layers_config = [
            {'type': 'Input', 'params': {'shape': input_shape}},
            {'type': 'LSTM', 'params': {'units': 128, 'return_sequences': True}},
            {'type': 'Dropout', 'params': {'rate': 0.2}},
            {'type': 'LSTM', 'params': {'units': 64, 'return_sequences': False}},
            {'type': 'Dropout', 'params': {'rate': 0.2}},
            {'type': 'Dense', 'params': {'units': 32, 'activation': 'relu'}},
            {'type': 'Dense', 'params': {'units': 1, 'activation': 'linear'}}
        ]
        
        model = create_sequential_model(layers_config)
        compile_model(model, optimizer='adam', loss='mse', metrics=['mae'])
        
        return model
    
    def prepare_data(self, data):
        """데이터 전처리 및 시퀀스 생성"""
        # 특성 정규화
        scaled_data = self.scaler.fit_transform(data[self.features])
        
        X, y = [], []
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i])
            y.append(scaled_data[i, 0])  # sales는 첫 번째 컬럼
        
        return np.array(X), np.array(y)
    
    def generate_sample_data(self, days=365):
        """샘플 데이터 생성 (실제 환경에서는 DB에서 가져옴)"""
        dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
        
        # 계절성과 트렌드를 반영한 매출 데이터 생성
        base_sales = 1000000  # 기본 매출
        seasonal_factor = np.sin(2 * np.pi * np.arange(days) / 365) * 0.3  # 계절성
        trend_factor = np.arange(days) * 1000  # 상승 트렌드
        noise = np.random.normal(0, 50000, days)  # 노이즈
        
        sales = base_sales + seasonal_factor * base_sales + trend_factor + noise
        sales = np.maximum(sales, 500000)  # 최소 매출 보장
        
        # 관련 특성들 생성
        staff_count = np.random.randint(5, 15, days)
        inventory_level = np.random.uniform(70, 95, days)
        customer_count = sales / 50000 + np.random.normal(0, 10, days)
        day_of_week = [d.weekday() for d in dates]
        month = [d.month for d in dates]
        
        data = pd.DataFrame({
            'date': dates,
            'sales': sales,
            'staff_count': staff_count,
            'inventory_level': inventory_level,
            'customer_count': customer_count,
            'day_of_week': day_of_week,
            'month': month
        })
        
        return data
    
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
    
    def predict(self, data, days_ahead=7):
        """매출 예측"""
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
            
            # 시퀀스 업데이트 (실제 환경에서는 새로운 데이터로 업데이트)
            new_row = current_sequence[0, -1].copy()
            new_row[0] = pred[0, 0]  # 예측된 매출로 업데이트
            current_sequence = np.roll(current_sequence, -1, axis=1)
            current_sequence[0, -1] = new_row
        
        # 예측값을 원래 스케일로 변환
        predictions_rescaled = []
        for pred in predictions:
            # 예측값을 원래 형태로 변환
            dummy_array = np.zeros((1, len(self.features)))
            dummy_array[0, 0] = pred
            rescaled = self.scaler.inverse_transform(dummy_array)
            predictions_rescaled.append(rescaled[0, 0])
        
        return predictions_rescaled
    
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
        
        # 스케일 역변환
        y_test_rescaled = self.scaler.inverse_transform(
            np.column_stack([y_test, np.zeros_like(y_test)])
        )[:, 0]
        pred_rescaled = self.scaler.inverse_transform(
            np.column_stack([predictions.flatten(), np.zeros_like(predictions.flatten())])
        )[:, 0]
        
        mse = mean_squared_error(y_test_rescaled, pred_rescaled)
        mae = mean_absolute_error(y_test_rescaled, pred_rescaled)
        rmse = np.sqrt(mse)
        
        return {
            'mse': mse,
            'mae': mae,
            'rmse': rmse,
            'predictions': pred_rescaled,
            'actual': y_test_rescaled
        }

# 사용 예시
if __name__ == "__main__":
    try:
        # 모델 인스턴스 생성
        model = SalesPredictionModel()
        
        # 샘플 데이터로 학습
        print("모델 학습 시작...")
        history = model.train(epochs=50)
        
        # 예측 테스트
        test_data = model.generate_sample_data(days=100)
        predictions = model.predict(test_data, days_ahead=7)
        
        print(f"다음 7일 매출 예측: {predictions}")
        
        # 성능 평가
        evaluation = model.evaluate(test_data)
        print(f"모델 성능 - RMSE: {evaluation['rmse']:.2f}, MAE: {evaluation['mae']:.2f}")
        
    except ImportError as e:
        print(f"TensorFlow 오류: {e}")
        print("TensorFlow를 설치하려면: pip install tensorflow")
    except Exception as e:
        print(f"오류 발생: {e}") 