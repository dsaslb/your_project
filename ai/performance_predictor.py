# -*- coding: utf-8 -*-
"""
AI 기반 성능 예측 시스템
과거 데이터를 분석하여 시스템 성능을 예측하고 최적화 방안을 제시
"""

import pandas as pd
import numpy as np
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformancePredictor:
    """AI 기반 성능 예측 클래스"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = [
            'hour', 'day_of_week', 'cpu_percent', 'memory_percent', 
            'disk_percent', 'process_count', 'network_bytes_sent', 
            'network_bytes_recv'
        ]
        self.target_columns = ['cpu_percent', 'memory_percent', 'response_time']
        self.model_path = 'ai/models/'
        self.scaler_path = 'ai/scalers/'
        
        # 디렉토리 생성
        os.makedirs(self.model_path, exist_ok=True)
        os.makedirs(self.scaler_path, exist_ok=True)
        
    def load_performance_data(self, days: int = 7) -> pd.DataFrame:
        """성능 데이터 로드"""
        try:
            conn = sqlite3.connect('data/performance_metrics.db')
            
            # 최근 N일간의 데이터 조회
            query = f"""
                SELECT * FROM performance_metrics 
                WHERE timestamp >= datetime('now', '-{days} days')
                ORDER BY timestamp
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                logger.warning("성능 데이터가 없습니다.")
                return pd.DataFrame()
                
            # 타임스탬프 파싱
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            return df
            
        except Exception as e:
            logger.error(f"성능 데이터 로드 오류: {e}")
            return pd.DataFrame()
            
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """특성 데이터 준비"""
        try:
            if df.empty:
                return pd.DataFrame(), {}
                
            # 기본 특성 선택
            features = df[self.feature_columns].copy()
            
            # 결측값 처리
            features = features.fillna(method='ffill').fillna(0)
            
            # 타겟 데이터 준비
            targets = {}
            for target in self.target_columns:
                if target in df.columns:
                    targets[target] = df[target].fillna(method='ffill').fillna(0)
                    
            return features, targets
            
        except Exception as e:
            logger.error(f"특성 데이터 준비 오류: {e}")
            return pd.DataFrame(), {}
            
    def train_models(self, features: pd.DataFrame, targets: Dict[str, pd.DataFrame]):
        """모델 훈련"""
        try:
            for target_name, target_data in targets.items():
                logger.info(f"{target_name} 모델 훈련 시작...")
                
                # 데이터 분할
                X_train, X_test, y_train, y_test = train_test_split(
                    features, target_data, test_size=0.2, random_state=42
                )
                
                # 스케일링
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # 모델 훈련
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
                
                model.fit(X_train_scaled, y_train)
                
                # 예측 및 평가
                y_pred = model.predict(X_test_scaled)
                mae = mean_absolute_error(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                
                logger.info(f"{target_name} 모델 훈련 완료 - MAE: {mae:.4f}, MSE: {mse:.4f}")
                
                # 모델 저장
                self.models[target_name] = model
                self.scalers[target_name] = scaler
                
                # 파일로 저장
                joblib.dump(model, f"{self.model_path}{target_name}_model.pkl")
                joblib.dump(scaler, f"{self.scaler_path}{target_name}_scaler.pkl")
                
        except Exception as e:
            logger.error(f"모델 훈련 오류: {e}")
            
    def load_trained_models(self):
        """저장된 모델 로드"""
        try:
            for target in self.target_columns:
                model_file = f"{self.model_path}{target}_model.pkl"
                scaler_file = f"{self.scaler_path}{target}_scaler.pkl"
                
                if os.path.exists(model_file) and os.path.exists(scaler_file):
                    self.models[target] = joblib.load(model_file)
                    self.scalers[target] = joblib.load(scaler_file)
                    logger.info(f"{target} 모델 로드 완료")
                    
        except Exception as e:
            logger.error(f"모델 로드 오류: {e}")
            
    def predict_performance(self, hours_ahead: int = 24) -> Dict[str, List[float]]:
        """미래 성능 예측"""
        try:
            if not self.models:
                logger.warning("훈련된 모델이 없습니다. 먼저 모델을 훈련하세요.")
                return {}
                
            # 현재 시간부터 미래 시간까지의 특성 생성
            current_time = datetime.now()
            future_times = []
            
            for i in range(hours_ahead):
                future_time = current_time + timedelta(hours=i)
                future_times.append({
                    'hour': future_time.hour,
                    'day_of_week': future_time.weekday(),
                    'cpu_percent': 0,  # 기본값
                    'memory_percent': 0,
                    'disk_percent': 0,
                    'process_count': 0,
                    'network_bytes_sent': 0,
                    'network_bytes_recv': 0
                })
                
            # 최근 데이터로 기본값 업데이트
            recent_data = self.load_performance_data(days=1)
            if not recent_data.empty:
                latest = recent_data.iloc[-1]
                for future_time in future_times:
                    future_time['cpu_percent'] = latest.get('cpu_percent', 0)
                    future_time['memory_percent'] = latest.get('memory_percent', 0)
                    future_time['disk_percent'] = latest.get('disk_percent', 0)
                    future_time['process_count'] = latest.get('process_count', 0)
                    future_time['network_bytes_sent'] = latest.get('network_bytes_sent', 0)
                    future_time['network_bytes_recv'] = latest.get('network_bytes_recv', 0)
                    
            # 예측 데이터프레임 생성
            future_df = pd.DataFrame(future_times)
            future_features = future_df[self.feature_columns]
            
            # 예측 실행
            predictions = {}
            for target_name, model in self.models.items():
                if target_name in self.scalers:
                    scaler = self.scalers[target_name]
                    features_scaled = scaler.transform(future_features)
                    pred = model.predict(features_scaled)
                    predictions[target_name] = pred.tolist()
                    
            return predictions
            
        except Exception as e:
            logger.error(f"성능 예측 오류: {e}")
            return {}
            
    def get_performance_trends(self) -> Dict[str, Any]:
        """성능 트렌드 분석"""
        try:
            # 최근 7일간 데이터 로드
            df = self.load_performance_data(days=7)
            
            if df.empty:
                return {'message': '분석할 데이터가 없습니다.'}
                
            trends = {}
            
            # 시간대별 평균 성능
            hourly_avg = df.groupby('hour').agg({
                'cpu_percent': 'mean',
                'memory_percent': 'mean',
                'response_time': 'mean'
            }).round(2)
            
            trends['hourly_averages'] = hourly_avg.to_dict()
            
            # 요일별 평균 성능
            daily_avg = df.groupby('day_of_week').agg({
                'cpu_percent': 'mean',
                'memory_percent': 'mean',
                'response_time': 'mean'
            }).round(2)
            
            trends['daily_averages'] = daily_avg.to_dict()
            
            # 성능 변화 추이
            recent_trend = df.tail(100).agg({
                'cpu_percent': ['mean', 'std', 'min', 'max'],
                'memory_percent': ['mean', 'std', 'min', 'max'],
                'response_time': ['mean', 'std', 'min', 'max']
            }).round(2)
            
            trends['recent_statistics'] = recent_trend.to_dict()
            
            # 성능 패턴 분석
            patterns = self._analyze_patterns(df)
            trends['patterns'] = patterns
            
            return trends
            
        except Exception as e:
            logger.error(f"트렌드 분석 오류: {e}")
            return {'error': str(e)}
            
    def _analyze_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """성능 패턴 분석"""
        try:
            patterns = {}
            
            # 피크 시간 분석
            cpu_peak_hour = df.groupby('hour')['cpu_percent'].mean().idxmax()
            memory_peak_hour = df.groupby('hour')['memory_percent'].mean().idxmax()
            
            patterns['peak_hours'] = {
                'cpu': int(cpu_peak_hour),
                'memory': int(memory_peak_hour)
            }
            
            # 성능 저하 패턴
            high_cpu_periods = df[df['cpu_percent'] > 80]
            high_memory_periods = df[df['memory_percent'] > 85]
            
            patterns['performance_issues'] = {
                'high_cpu_count': len(high_cpu_periods),
                'high_memory_count': len(high_memory_periods),
                'high_cpu_hours': high_cpu_periods['hour'].value_counts().head(3).to_dict(),
                'high_memory_hours': high_memory_periods['hour'].value_counts().head(3).to_dict()
            }
            
            # 상관관계 분석
            correlations = df[['cpu_percent', 'memory_percent', 'response_time', 'process_count']].corr()
            patterns['correlations'] = correlations.round(3).to_dict()
            
            return patterns
            
        except Exception as e:
            logger.error(f"패턴 분석 오류: {e}")
            return {}
            
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """최적화 권장사항 생성"""
        try:
            recommendations = []
            
            # 최근 데이터 분석
            df = self.load_performance_data(days=1)
            if df.empty:
                return [{'type': 'info', 'message': '최적화 권장사항을 생성할 데이터가 없습니다.'}]
                
            latest = df.iloc[-1]
            avg_performance = df.mean()
            
            # CPU 사용률 권장사항
            if latest.get('cpu_percent', 0) > 70:
                recommendations.append({
                    'type': 'warning',
                    'category': 'CPU',
                    'message': 'CPU 사용률이 높습니다. 프로세스 최적화를 고려하세요.',
                    'current_value': f"{latest.get('cpu_percent', 0):.1f}%",
                    'recommendation': '불필요한 프로세스 종료 또는 CPU 집약적 작업 스케줄링 조정'
                })
                
            # 메모리 사용률 권장사항
            if latest.get('memory_percent', 0) > 80:
                recommendations.append({
                    'type': 'warning',
                    'category': 'Memory',
                    'message': '메모리 사용률이 높습니다. 메모리 정리를 고려하세요.',
                    'current_value': f"{latest.get('memory_percent', 0):.1f}%",
                    'recommendation': '메모리 캐시 정리 또는 메모리 사용량이 많은 프로세스 확인'
                })
                
            # 응답시간 권장사항
            if latest.get('response_time', 0) > 3:
                recommendations.append({
                    'type': 'warning',
                    'category': 'Response Time',
                    'message': '응답시간이 느립니다. 성능 최적화를 고려하세요.',
                    'current_value': f"{latest.get('response_time', 0):.3f}초",
                    'recommendation': '데이터베이스 쿼리 최적화 또는 캐싱 시스템 도입'
                })
                
            # 디스크 사용률 권장사항
            if latest.get('disk_percent', 0) > 85:
                recommendations.append({
                    'type': 'warning',
                    'category': 'Disk',
                    'message': '디스크 사용률이 높습니다. 공간 정리를 고려하세요.',
                    'current_value': f"{latest.get('disk_percent', 0):.1f}%",
                    'recommendation': '불필요한 파일 삭제 또는 로그 파일 정리'
                })
                
            # 긍정적인 피드백
            if len(recommendations) == 0:
                recommendations.append({
                    'type': 'success',
                    'category': 'Overall',
                    'message': '시스템 성능이 양호합니다.',
                    'current_value': '정상',
                    'recommendation': '현재 상태를 유지하세요.'
                })
                
            return recommendations
            
        except Exception as e:
            logger.error(f"권장사항 생성 오류: {e}")
            return [{'type': 'error', 'message': f'권장사항 생성 중 오류가 발생했습니다: {e}'}]


# 전역 인스턴스
performance_predictor = PerformancePredictor()


def train_performance_models():
    """성능 예측 모델 훈련"""
    try:
        logger.info("성능 예측 모델 훈련 시작...")
        
        # 데이터 로드
        df = performance_predictor.load_performance_data(days=7)
        if df.empty:
            return {'status': 'error', 'message': '훈련할 데이터가 없습니다.'}
            
        # 특성 준비
        features, targets = performance_predictor.prepare_features(df)
        if features.empty or not targets:
            return {'status': 'error', 'message': '특성 데이터 준비 실패'}
            
        # 모델 훈련
        performance_predictor.train_models(features, targets)
        
        return {'status': 'success', 'message': '모델 훈련이 완료되었습니다.'}
        
    except Exception as e:
        logger.error(f"모델 훈련 오류: {e}")
        return {'status': 'error', 'message': str(e)}


def predict_future_performance(hours: int = 24):
    """미래 성능 예측"""
    try:
        # 모델 로드
        performance_predictor.load_trained_models()
        
        # 예측 실행
        predictions = performance_predictor.predict_performance(hours)
        
        return predictions
        
    except Exception as e:
        logger.error(f"성능 예측 오류: {e}")
        return {}


def get_performance_analysis():
    """성능 분석 결과 반환"""
    try:
        # 트렌드 분석
        trends = performance_predictor.get_performance_trends()
        
        # 권장사항 생성
        recommendations = performance_predictor.get_optimization_recommendations()
        
        return {
            'trends': trends,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"성능 분석 오류: {e}")
        return {'error': str(e)}


if __name__ == "__main__":
    # 테스트 실행
    print("AI 성능 예측 시스템 테스트...")
    
    # 모델 훈련
    result = train_performance_models()
    print(f"모델 훈련 결과: {result}")
    
    # 성능 예측
    predictions = predict_future_performance(24)
    print(f"24시간 예측: {predictions}")
    
    # 성능 분석
    analysis = get_performance_analysis()
    print(f"성능 분석: {analysis}") 