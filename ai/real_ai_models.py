"""
실제 AI 모델 구현
TensorFlow와 scikit-learn을 사용한 실제 머신러닝 모델
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import joblib
import pickle

# TensorFlow imports
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# Scikit-learn imports
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score, classification_report
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.pipeline import Pipeline

# 기존 성능 예측 모델 import
from ai.performance_predictor import PerformancePredictor

logger = logging.getLogger(__name__)

class RealAIModelManager:
    """실제 AI 모델 관리자"""
    
    def __init__(self):
        self.models_dir = "ai/models"
        self.data_dir = "data"
        self.scalers_dir = "ai/scalers"
        
        # 디렉토리 생성
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.scalers_dir, exist_ok=True)
        
        # 모델 저장소
        self.models = {}
        self.scalers = {}
        self.model_metadata = {}
        
        # 모델 타입별 설정
        self.model_configs = {
            'sales_prediction': {
                'type': 'regression',
                'framework': 'tensorflow',
                'architecture': 'lstm',
                'features': ['timestamp', 'day_of_week', 'month', 'hour', 'previous_sales', 'temperature', 'is_holiday'],
                'target': 'sales_amount'
            },
            'customer_churn': {
                'type': 'classification',
                'framework': 'sklearn',
                'algorithm': 'random_forest',
                'features': ['visit_frequency', 'avg_order_value', 'days_since_last_visit', 'total_orders', 'customer_satisfaction'],
                'target': 'churn_probability'
            },
            'inventory_optimization': {
                'type': 'regression',
                'framework': 'sklearn',
                'algorithm': 'random_forest',
                'features': ['historical_demand', 'seasonality', 'price', 'promotion', 'competitor_price'],
                'target': 'optimal_stock'
            },
            'staff_scheduling': {
                'type': 'regression',
                'framework': 'tensorflow',
                'architecture': 'dense',
                'features': ['day_of_week', 'hour', 'historical_demand', 'weather', 'events'],
                'target': 'required_staff'
            }
        }
        
        self._load_existing_models()
    
    def _load_existing_models(self):
        """기존 모델들 로드"""
        try:
            for model_name in self.model_configs.keys():
                model_path = os.path.join(self.models_dir, f"{model_name}.pkl")
                scaler_path = os.path.join(self.scalers_dir, f"{model_name}_scaler.pkl")
                metadata_path = os.path.join(self.models_dir, f"{model_name}_metadata.json")
                
                # 모델 로드
                if self.model_configs[model_name]['framework'] == 'tensorflow':
                    model_path = os.path.join(self.models_dir, f"{model_name}.keras")
                else:
                    model_path = os.path.join(self.models_dir, f"{model_name}.pkl")
                
                if os.path.exists(model_path):
                    if self.model_configs[model_name]['framework'] == 'tensorflow':
                        self.models[model_name] = load_model(model_path)
                    else:
                        with open(model_path, 'rb') as f:
                            self.models[model_name] = pickle.load(f)
                
                # 스케일러 로드
                if os.path.exists(scaler_path):
                    with open(scaler_path, 'rb') as f:
                        self.scalers[model_name] = pickle.load(f)
                
                # 메타데이터 로드
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        self.model_metadata[model_name] = json.load(f)
                        
            logger.info(f"기존 모델 로드 완료: {len(self.models)}개")
        except Exception as e:
            logger.error(f"기존 모델 로드 실패: {e}")
    
    def generate_synthetic_data(self, model_name: str, num_samples: int = 1000) -> pd.DataFrame:
        """합성 데이터 생성"""
        config = self.model_configs[model_name]
        features = config['features']
        
        data = {}
        
        # 기본 특성 생성
        if 'timestamp' in features:
            dates = pd.date_range(start='2024-01-01', periods=num_samples, freq='h')
            data['timestamp'] = dates.astype(np.int64) // 10**9  # Unix timestamp로 변환
            data['day_of_week'] = dates.dayofweek
            data['month'] = dates.month
            data['hour'] = dates.hour
        
        if 'previous_sales' in features:
            data['previous_sales'] = np.random.normal(1000, 200, num_samples)
        
        if 'temperature' in features:
            data['temperature'] = np.random.normal(20, 10, num_samples)
        
        if 'is_holiday' in features:
            data['is_holiday'] = np.random.choice([0, 1], num_samples, p=[0.9, 0.1])
        
        if 'visit_frequency' in features:
            data['visit_frequency'] = np.random.poisson(5, num_samples)
        
        if 'avg_order_value' in features:
            data['avg_order_value'] = np.random.normal(50, 15, num_samples)
        
        if 'days_since_last_visit' in features:
            data['days_since_last_visit'] = np.random.exponential(7, num_samples)
        
        if 'total_orders' in features:
            data['total_orders'] = np.random.poisson(20, num_samples)
        
        if 'customer_satisfaction' in features:
            data['customer_satisfaction'] = np.random.uniform(1, 5, num_samples)
        
        if 'historical_demand' in features:
            data['historical_demand'] = np.random.poisson(100, num_samples)
        
        if 'seasonality' in features:
            data['seasonality'] = np.sin(np.arange(num_samples) * 2 * np.pi / 365)
        
        if 'price' in features:
            data['price'] = np.random.normal(25, 5, num_samples)
        
        if 'promotion' in features:
            data['promotion'] = np.random.choice([0, 1], num_samples, p=[0.8, 0.2])
        
        if 'competitor_price' in features:
            data['competitor_price'] = np.random.normal(23, 4, num_samples)
        
        if 'weather' in features:
            data['weather'] = np.random.choice([0, 1, 2], num_samples, p=[0.6, 0.3, 0.1])  # 0: 맑음, 1: 흐림, 2: 비
        
        if 'events' in features:
            data['events'] = np.random.choice([0, 1], num_samples, p=[0.9, 0.1])
        
        # 타겟 변수 생성 (간단한 규칙 기반)
        if config['target'] == 'sales_amount':
            base_sales = 1000
            if 'previous_sales' in data:
                base_sales = data['previous_sales'] * 0.8
            if 'temperature' in data:
                base_sales += data['temperature'] * 10
            if 'is_holiday' in data:
                base_sales *= (1 + data['is_holiday'] * 0.3)
            data['sales_amount'] = np.maximum(0, base_sales + np.random.normal(0, 100, num_samples))
        
        elif config['target'] == 'churn_probability':
            base_prob = 0.1
            if 'visit_frequency' in data:
                base_prob -= data['visit_frequency'] * 0.02
            if 'avg_order_value' in data:
                base_prob -= data['avg_order_value'] * 0.001
            if 'days_since_last_visit' in data:
                base_prob += data['days_since_last_visit'] * 0.01
            prob = np.clip(base_prob + np.random.normal(0, 0.05, num_samples), 0, 1)
            data['churn_probability'] = (prob > 0.5).astype(int)  # 이진 분류로 변환
        
        elif config['target'] == 'optimal_stock':
            base_stock = 100
            if 'historical_demand' in data:
                base_stock = data['historical_demand'] * 1.2
            if 'seasonality' in data:
                base_stock *= (1 + data['seasonality'] * 0.3)
            data['optimal_stock'] = np.maximum(0, base_stock + np.random.normal(0, 20, num_samples))
        
        elif config['target'] == 'required_staff':
            base_staff = 5
            if 'historical_demand' in data:
                base_staff = data['historical_demand'] / 20
            if 'weather' in data:
                base_staff *= (1 + data['weather'] * 0.1)
            data['required_staff'] = np.maximum(1, base_staff + np.random.normal(0, 1, num_samples))
        
        return pd.DataFrame(data)
    
    def create_tensorflow_model(self, model_name: str, input_shape: int) -> tf.keras.Model:
        """TensorFlow 모델 생성"""
        config = self.model_configs[model_name]
        
        if config['architecture'] == 'lstm':
            model = Sequential([
                layers.LSTM(64, return_sequences=True, input_shape=(input_shape, 1)),
                layers.Dropout(0.2),
                layers.LSTM(32, return_sequences=False),
                layers.Dropout(0.2),
                layers.Dense(16, activation='relu'),
                layers.Dense(1)
            ])
        elif config['architecture'] == 'dense':
            model = Sequential([
                layers.Dense(128, activation='relu', input_shape=(input_shape,)),
                layers.Dropout(0.3),
                layers.Dense(64, activation='relu'),
                layers.Dropout(0.2),
                layers.Dense(32, activation='relu'),
                layers.Dense(1)
            ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def create_sklearn_model(self, model_name: str) -> Any:
        """Scikit-learn 모델 생성"""
        config = self.model_configs[model_name]
        
        if config['algorithm'] == 'random_forest':
            if config['type'] == 'regression':
                return RandomForestRegressor(n_estimators=100, random_state=42)
            else:
                return RandomForestClassifier(n_estimators=100, random_state=42)
        elif config['algorithm'] == 'linear_regression':
            return LinearRegression()
        elif config['algorithm'] == 'logistic_regression':
            return LogisticRegression(random_state=42)
    
    def train_model(self, model_name: str, data: pd.DataFrame = None) -> Dict[str, Any]:
        """모델 학습"""
        try:
            config = self.model_configs[model_name]
            
            # 데이터 준비
            if data is None:
                data = self.generate_synthetic_data(model_name, 2000)
            
            # 특성과 타겟 분리
            feature_cols = [col for col in config['features'] if col in data.columns]
            X = data[feature_cols]
            y = data[config['target']]
            
            # 데이터 전처리
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # 모델 생성 및 학습
            if config['framework'] == 'tensorflow':
                # TensorFlow 모델
                if config['architecture'] == 'lstm':
                    # LSTM을 위한 데이터 reshape
                    X_reshaped = X_scaled.reshape((X_scaled.shape[0], X_scaled.shape[1], 1))
                    model = self.create_tensorflow_model(model_name, X_scaled.shape[1])
                    
                    # 조기 종료 콜백
                    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
                    
                    # 모델 학습
                    history = model.fit(
                        X_reshaped, y,
                        epochs=100,
                        batch_size=32,
                        validation_split=0.2,
                        callbacks=[early_stopping],
                        verbose=0
                    )
                else:
                    model = self.create_tensorflow_model(model_name, X_scaled.shape[1])
                    
                    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
                    
                    history = model.fit(
                        X_scaled, y,
                        epochs=100,
                        batch_size=32,
                        validation_split=0.2,
                        callbacks=[early_stopping],
                        verbose=0
                    )
                
                # 성능 평가
                y_pred = model.predict(X_scaled if config['architecture'] != 'lstm' else X_reshaped)
                mse = mean_squared_error(y, y_pred)
                mae = mean_absolute_error(y, y_pred)
                r2 = r2_score(y, y_pred)
                
            else:
                # Scikit-learn 모델
                X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
                
                model = self.create_sklearn_model(model_name)
                model.fit(X_train, y_train)
                
                # 성능 평가
                y_pred = model.predict(X_test)
                if config['type'] == 'regression':
                    mse = mean_squared_error(y_test, y_pred)
                    mae = mean_absolute_error(y_test, y_pred)
                    r2 = r2_score(y_test, y_pred)
                else:
                    mse = None
                    mae = None
                    r2 = accuracy_score(y_test, y_pred)
            
            # 모델 저장
            if config['framework'] == 'tensorflow':
                model_path = os.path.join(self.models_dir, f"{model_name}.keras")
            else:
                model_path = os.path.join(self.models_dir, f"{model_name}.pkl")
            scaler_path = os.path.join(self.scalers_dir, f"{model_name}_scaler.pkl")
            
            if config['framework'] == 'tensorflow':
                model.save(model_path)
            else:
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
            
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
            
            # 메타데이터 저장
            metadata = {
                'model_name': model_name,
                'framework': config['framework'],
                'type': config['type'],
                'features': feature_cols,
                'target': config['target'],
                'trained_at': datetime.now().isoformat(),
                'performance': {
                    'mse': mse,
                    'mae': mae,
                    'r2': r2
                },
                'data_samples': len(data)
            }
            
            metadata_path = os.path.join(self.models_dir, f"{model_name}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # 메모리에 로드
            self.models[model_name] = model
            self.scalers[model_name] = scaler
            self.model_metadata[model_name] = metadata
            
            logger.info(f"모델 '{model_name}' 학습 완료 - R²: {r2:.4f}")
            
            return {
                'success': True,
                'model_name': model_name,
                'performance': metadata['performance'],
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"모델 '{model_name}' 학습 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def predict(self, model_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """예측 수행"""
        try:
            if model_name not in self.models:
                return {'success': False, 'error': f'모델 {model_name}이 로드되지 않았습니다.'}
            
            config = self.model_configs[model_name]
            model = self.models[model_name]
            scaler = self.scalers[model_name]
            
            # 입력 데이터를 DataFrame으로 변환
            input_df = pd.DataFrame([input_data])
            
            # 필요한 특성만 선택
            feature_cols = [col for col in config['features'] if col in input_df.columns]
            X = input_df[feature_cols]
            
            # 스케일링
            X_scaled = scaler.transform(X)
            
            # 예측
            if config['framework'] == 'tensorflow':
                if config['architecture'] == 'lstm':
                    X_reshaped = X_scaled.reshape((X_scaled.shape[0], X_scaled.shape[1], 1))
                    prediction = model.predict(X_reshaped)[0][0]
                else:
                    prediction = model.predict(X_scaled)[0][0]
            else:
                prediction = model.predict(X_scaled)[0]
            
            return {
                'success': True,
                'model_name': model_name,
                'prediction': float(prediction),
                'input_features': input_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"예측 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_model_status(self) -> Dict[str, Any]:
        """모델 상태 조회"""
        status = {}
        
        for model_name in self.model_configs.keys():
            if model_name in self.models:
                metadata = self.model_metadata.get(model_name, {})
                status[model_name] = {
                    'loaded': True,
                    'framework': self.model_configs[model_name]['framework'],
                    'type': self.model_configs[model_name]['type'],
                    'trained_at': metadata.get('trained_at', 'Unknown'),
                    'performance': metadata.get('performance', {}),
                    'features': metadata.get('features', [])
                }
            else:
                status[model_name] = {
                    'loaded': False,
                    'framework': self.model_configs[model_name]['framework'],
                    'type': self.model_configs[model_name]['type']
                }
        
        return status
    
    def retrain_model(self, model_name: str) -> Dict[str, Any]:
        """모델 재학습"""
        return self.train_model(model_name)
    
    def delete_model(self, model_name: str) -> Dict[str, Any]:
        """모델 삭제"""
        try:
            # 파일 삭제
            model_path = os.path.join(self.models_dir, f"{model_name}.pkl")
            scaler_path = os.path.join(self.scalers_dir, f"{model_name}_scaler.pkl")
            metadata_path = os.path.join(self.models_dir, f"{model_name}_metadata.json")
            
            for path in [model_path, scaler_path, metadata_path]:
                if os.path.exists(path):
                    os.remove(path)
            
            # 메모리에서 제거
            if model_name in self.models:
                del self.models[model_name]
            if model_name in self.scalers:
                del self.scalers[model_name]
            if model_name in self.model_metadata:
                del self.model_metadata[model_name]
            
            return {
                'success': True,
                'message': f'모델 {model_name}이 삭제되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"모델 삭제 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# 전역 인스턴스
ai_model_manager = RealAIModelManager() 