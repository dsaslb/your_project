"""
고객 분석 AI 모델
TensorFlow 기반 고객 행동 분석 및 세그먼테이션
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
import joblib
import os
from datetime import datetime, timedelta
import logging
from typing import Optional, List, Dict, Any, Union, Tuple, TYPE_CHECKING

# TensorFlow 공통 유틸리티 사용
from .tensorflow_utils import (
    TENSORFLOW_AVAILABLE, tf, check_tensorflow_available,
    create_sequential_model, create_callbacks, compile_model,
    load_model_safely, save_model_safely, setup_ai_logging
)

class CustomerAnalyticsModel:
    def __init__(self, model_path='ai_models/saved_models/customer_analytics.h5'):
        check_tensorflow_available()
            
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.model: Optional[Any] = None
        self.clustering_model: Optional[KMeans] = None
        self.features = [
            'total_spent', 'visit_frequency', 'avg_order_value', 
            'days_since_last_visit', 'total_orders', 'preferred_time',
            'weekend_visits_ratio', 'promotion_response_rate'
        ]
        
        # 로깅 설정
        self.logger = setup_ai_logging()
        
    def create_model(self, input_shape):
        """고객 행동 예측 모델 생성"""
        check_tensorflow_available()
        
        layers_config = [
            {'type': 'Input', 'params': {'shape': input_shape}},
            {'type': 'Dense', 'params': {'units': 128, 'activation': 'relu'}},
            {'type': 'Dropout', 'params': {'rate': 0.3}},
            {'type': 'Dense', 'params': {'units': 64, 'activation': 'relu'}},
            {'type': 'Dropout', 'params': {'rate': 0.2}},
            {'type': 'Dense', 'params': {'units': 32, 'activation': 'relu'}},
            {'type': 'Dense', 'params': {'units': 1, 'activation': 'sigmoid'}}
        ]
        
        model = create_sequential_model(layers_config)
        compile_model(model, optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', 'precision', 'recall'])
        
        return model
    
    def generate_sample_data(self, n_customers=1000):
        """샘플 고객 데이터 생성"""
        np.random.seed(42)
        
        # 고객별 특성 생성
        total_spent = np.random.exponential(500, n_customers)  # 지수 분포
        visit_frequency = np.random.poisson(8, n_customers)  # 포아송 분포
        avg_order_value = np.random.normal(25, 8, n_customers)
        days_since_last_visit = np.random.exponential(30, n_customers)
        total_orders = np.random.poisson(12, n_customers)
        preferred_time = np.random.uniform(0, 24, n_customers)
        weekend_visits_ratio = np.random.beta(2, 5, n_customers)
        promotion_response_rate = np.random.beta(3, 7, n_customers)
        
        # 이탈 여부 (목표 변수)
        churn_probability = (
            0.3 * (days_since_last_visit > 60) +
            0.2 * (visit_frequency < 5) +
            0.2 * (total_spent < 300) +
            0.1 * (promotion_response_rate < 0.3) +
            np.random.normal(0, 0.1, n_customers)
        )
        churn = (churn_probability > 0.5).astype(int)
        
        data = pd.DataFrame({
            'customer_id': range(1, n_customers + 1),
            'total_spent': total_spent,
            'visit_frequency': visit_frequency,
            'avg_order_value': avg_order_value,
            'days_since_last_visit': days_since_last_visit,
            'total_orders': total_orders,
            'preferred_time': preferred_time,
            'weekend_visits_ratio': weekend_visits_ratio,
            'promotion_response_rate': promotion_response_rate,
            'churn': churn
        })
        
        return data
    
    def prepare_data(self, data):
        """데이터 전처리"""
        # 특성 정규화
        scaled_features = self.scaler.fit_transform(data[self.features])
        
        # 목표 변수
        target = data['churn'].values
        
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
        callbacks = create_callbacks(self.model_path.replace('.h5', '.keras'), monitor='val_accuracy', patience=10)
        
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
    
    def predict_churn(self, data):
        """고객 이탈 예측"""
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
            return predictions.flatten()
        else:
            raise RuntimeError("모델이 초기화되지 않았습니다.")
    
    def segment_customers(self, data, n_clusters=4):
        """고객 세그먼테이션"""
        # 데이터 전처리
        scaled_data = self.scaler.fit_transform(data[self.features])
        
        # K-means 클러스터링
        self.clustering_model = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = self.clustering_model.fit_predict(scaled_data)
        
        # 클러스터 특성 분석
        cluster_centers = self.clustering_model.cluster_centers_
        
        # 세그먼트별 특성 분석
        segments = {}
        for i in range(n_clusters):
            segment_data = data[cluster_labels == i]
            segments[f'segment_{i}'] = {
                'size': len(segment_data),
                'avg_total_spent': segment_data['total_spent'].mean(),
                'avg_visit_frequency': segment_data['visit_frequency'].mean(),
                'avg_order_value': segment_data['avg_order_value'].mean(),
                'churn_rate': segment_data['churn'].mean() if 'churn' in segment_data.columns else 0
            }
        
        return {
            'cluster_labels': cluster_labels,
            'cluster_centers': cluster_centers,
            'segments': segments,
            'silhouette_score': silhouette_score(scaled_data, cluster_labels)
        }
    
    def analyze_customer_lifetime_value(self, data):
        """고객 생애 가치 분석"""
        # CLV 계산 (간단한 버전)
        clv = (
            data['avg_order_value'] * 
            data['visit_frequency'] * 
            (1 / (1 + data['days_since_last_visit'] / 365))  # 할인율 적용
        )
        
        # 고객 등급 분류
        clv_quantiles = np.percentile(clv, [25, 50, 75])
        
        customer_tiers = []
        for value in clv:
            if value >= clv_quantiles[2]:
                customer_tiers.append('VIP')
            elif value >= clv_quantiles[1]:
                customer_tiers.append('Regular')
            elif value >= clv_quantiles[0]:
                customer_tiers.append('Occasional')
            else:
                customer_tiers.append('At Risk')
        
        return {
            'customer_lifetime_value': clv,
            'customer_tiers': customer_tiers,
            'tier_distribution': pd.Series(customer_tiers).value_counts().to_dict()
        }
    
    def recommend_retention_strategies(self, data, churn_predictions):
        """고객 유지 전략 추천"""
        high_risk_customers = data[churn_predictions > 0.7]
        
        strategies = {
            'high_risk_customers': len(high_risk_customers),
            'recommendations': []
        }
        
        if len(high_risk_customers) > 0:
            # 고객 특성에 따른 맞춤 전략
            for _, customer in high_risk_customers.iterrows():
                strategy = {
                    'customer_id': customer['customer_id'],
                    'churn_probability': churn_predictions[data['customer_id'] == customer['customer_id']][0],
                    'recommendations': []
                }
                
                # 맞춤 전략 생성
                if customer['days_since_last_visit'] > 30:
                    strategy['recommendations'].append('재방문 유도 이메일 발송')
                
                if customer['total_spent'] < 500:
                    strategy['recommendations'].append('첫 구매 할인 쿠폰 제공')
                
                if customer['promotion_response_rate'] > 0.5:
                    strategy['recommendations'].append('개인화된 프로모션 제공')
                
                if customer['visit_frequency'] < 5:
                    strategy['recommendations'].append('로열티 프로그램 가입 유도')
                
                strategies['recommendations'].append(strategy)
        
        return strategies
    
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
            predictions_binary = (predictions > 0.5).astype(int)
        else:
            raise RuntimeError("모델이 초기화되지 않았습니다.")
        
        # 성능 메트릭 계산
        accuracy = np.mean(predictions_binary.flatten() == y_test)
        precision = np.sum((predictions_binary.flatten() == 1) & (y_test == 1)) / np.sum(predictions_binary.flatten() == 1)
        recall = np.sum((predictions_binary.flatten() == 1) & (y_test == 1)) / np.sum(y_test == 1)
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'predictions': predictions.flatten(),
            'actual': y_test
        }

# 사용 예시
if __name__ == "__main__":
    try:
        # 모델 인스턴스 생성
        model = CustomerAnalyticsModel()
        
        # 샘플 데이터로 학습
        print("고객 분석 모델 학습 시작...")
        history = model.train(epochs=50)
        
        # 예측 테스트
        test_data = model.generate_sample_data(n_customers=200)
        churn_predictions = model.predict_churn(test_data)
        
        print(f"이탈 예측 완료: {len(churn_predictions)}명의 고객")
        
        # 고객 세그먼테이션
        segmentation_result = model.segment_customers(test_data)
        print(f"세그먼테이션 결과: {segmentation_result['segments']}")
        
        # 고객 생애 가치 분석
        clv_result = model.analyze_customer_lifetime_value(test_data)
        print(f"고객 등급 분포: {clv_result['tier_distribution']}")
        
        # 유지 전략 추천
        retention_strategies = model.recommend_retention_strategies(test_data, churn_predictions)
        print(f"고위험 고객 수: {retention_strategies['high_risk_customers']}")
        
        # 성능 평가
        evaluation = model.evaluate(test_data)
        print(f"모델 성능 - 정확도: {evaluation['accuracy']:.3f}, 정밀도: {evaluation['precision']:.3f}")
        
    except ImportError as e:
        print(f"TensorFlow 오류: {e}")
        print("TensorFlow를 설치하려면: pip install tensorflow")
    except Exception as e:
        print(f"오류 발생: {e}") 