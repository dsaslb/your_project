import numpy as np
import pandas as pd
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrendAnalysis:
    """트렌드 분석 결과"""
    metric: str
    trend: str  # 'increasing', 'decreasing', 'stable'
    slope: float
    confidence: float
    prediction_next_hour: float
    prediction_next_day: float

@dataclass
class AnomalyDetection:
    """이상 탐지 결과"""
    metric: str
    timestamp: float
    value: float
    threshold: float
    severity: str  # 'low', 'medium', 'high'
    description: str

@dataclass
class UserBehaviorAnalysis:
    """사용자 행동 분석 결과"""
    user_id: str
    session_count: int
    avg_session_duration: float
    favorite_pages: List[str]
    peak_activity_hours: List[int]
    error_rate: float
    engagement_score: float

@dataclass
class PerformancePrediction:
    """성능 예측 결과"""
    metric: str
    prediction_time: float
    predicted_value: float
    confidence_interval: Tuple[float, float]
    factors: Dict[str, float]

class AdvancedAnalytics:
    """고급 분석 시스템"""
    
    def __init__(self, db_path: str = "data/monitoring.db"):
        self.db_path = db_path
        self.scaler = StandardScaler()
        self.models = {}
        self.anomaly_thresholds = {}
        
    def load_metrics_data(self, hours: int = 168) -> pd.DataFrame:
        """메트릭 데이터 로드 (기본값: 7일)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cutoff_time = time.time() - (hours * 3600)
                
                query = '''
                    SELECT timestamp, cpu_percent, memory_percent, disk_usage_percent,
                           network_sent, network_recv, active_connections, active_users,
                           request_count, error_count, response_time_avg
                    FROM system_metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp
                '''
                
                df = pd.read_sql_query(query, conn, params=(cutoff_time,))
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                df.set_index('datetime', inplace=True)
                
                return df
        except Exception as e:
            logger.error(f"메트릭 데이터 로드 실패: {e}")
            return pd.DataFrame()
    
    def load_user_activity_data(self, hours: int = 168) -> pd.DataFrame:
        """사용자 활동 데이터 로드"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cutoff_time = time.time() - (hours * 3600)
                
                query = '''
                    SELECT user_id, session_id, action, page, timestamp, duration,
                           ip_address, user_agent, success, error_message
                    FROM user_activities
                    WHERE timestamp >= ?
                    ORDER BY timestamp
                '''
                
                df = pd.read_sql_query(query, conn, params=(cutoff_time,))
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                
                return df
        except Exception as e:
            logger.error(f"사용자 활동 데이터 로드 실패: {e}")
            return pd.DataFrame()
    
    def analyze_trends(self, df: pd.DataFrame) -> List[TrendAnalysis]:
        """트렌드 분석"""
        trends = []
        metrics = ['cpu_percent', 'memory_percent', 'disk_usage_percent', 
                  'active_users', 'request_count', 'response_time_avg']
        
        for metric in metrics:
            if metric not in df.columns:
                continue
                
            # 시계열 데이터 준비
            y = df[metric].values
            X = np.arange(len(y)).reshape(-1, 1)
            
            # 선형 회귀 모델
            model = LinearRegression()
            model.fit(X, y)
            
            # 트렌드 방향 결정
            slope = model.coef_[0]
            if slope > 0.01:
                trend = 'increasing'
            elif slope < -0.01:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            # 신뢰도 계산 (R² 점수)
            confidence = r2_score(y, model.predict(X))
            
            # 예측
            next_hour_idx = len(y)
            next_day_idx = len(y) + 24
            
            prediction_next_hour = model.predict([[next_hour_idx]])[0]
            prediction_next_day = model.predict([[next_day_idx]])[0]
            
            trends.append(TrendAnalysis(
                metric=metric,
                trend=trend,
                slope=slope,
                confidence=confidence,
                prediction_next_hour=prediction_next_hour,
                prediction_next_day=prediction_next_day
            ))
        
        return trends
    
    def detect_anomalies(self, df: pd.DataFrame) -> List[AnomalyDetection]:
        """이상 탐지"""
        anomalies = []
        metrics = ['cpu_percent', 'memory_percent', 'disk_usage_percent', 
                  'response_time_avg']
        
        for metric in metrics:
            if metric not in df.columns:
                continue
            
            values = df[metric].values
            
            # 통계적 임계값 계산 (3-시그마 규칙)
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            upper_threshold = mean_val + (3 * std_val)
            lower_threshold = mean_val - (3 * std_val)
            
            # 이상값 탐지
            for i, value in enumerate(values):
                if value > upper_threshold or value < lower_threshold:
                    # 심각도 결정
                    deviation = abs(value - mean_val) / std_val
                    if deviation > 4:
                        severity = 'high'
                    elif deviation > 3:
                        severity = 'medium'
                    else:
                        severity = 'low'
                    
                    description = f"{metric} 값이 평균에서 {deviation:.1f} 표준편차 벗어남"
                    
                    anomalies.append(AnomalyDetection(
                        metric=metric,
                        timestamp=df.index[i].timestamp(),
                        value=value,
                        threshold=upper_threshold if value > upper_threshold else lower_threshold,
                        severity=severity,
                        description=description
                    ))
        
        return anomalies
    
    def analyze_user_behavior(self, df: pd.DataFrame) -> List[UserBehaviorAnalysis]:
        """사용자 행동 분석"""
        if df.empty:
            return []
        
        user_analyses = []
        unique_users = df['user_id'].unique()
        
        for user_id in unique_users:
            user_data = df[df['user_id'] == user_id]
            
            # 세션 수 계산
            session_count = user_data['session_id'].nunique()
            
            # 평균 세션 지속 시간
            avg_session_duration = user_data['duration'].mean()
            
            # 선호 페이지 분석
            page_counts = user_data['page'].value_counts()
            favorite_pages = page_counts.head(5).index.tolist()
            
            # 피크 활동 시간 분석
            user_data['hour'] = user_data['datetime'].dt.hour
            hour_counts = user_data['hour'].value_counts()
            peak_activity_hours = hour_counts.head(3).index.tolist()
            
            # 에러율 계산
            total_actions = len(user_data)
            error_actions = len(user_data[~user_data['success']])
            error_rate = (error_actions / total_actions * 100) if total_actions > 0 else 0
            
            # 참여도 점수 계산
            engagement_score = self._calculate_engagement_score(user_data)
            
            user_analyses.append(UserBehaviorAnalysis(
                user_id=user_id,
                session_count=session_count,
                avg_session_duration=avg_session_duration,
                favorite_pages=favorite_pages,
                peak_activity_hours=peak_activity_hours,
                error_rate=error_rate,
                engagement_score=engagement_score
            ))
        
        return user_analyses
    
    def _calculate_engagement_score(self, user_data: pd.DataFrame) -> float:
        """참여도 점수 계산"""
        # 세션 수 (가중치: 0.3)
        session_score = min(user_data['session_id'].nunique() / 10, 1.0) * 0.3
        
        # 평균 세션 지속 시간 (가중치: 0.2)
        avg_duration = user_data['duration'].mean()
        duration_score = min(avg_duration / 300, 1.0) * 0.2  # 5분을 최대값으로
        
        # 활동 빈도 (가중치: 0.3)
        total_actions = len(user_data)
        frequency_score = min(total_actions / 100, 1.0) * 0.3
        
        # 페이지 다양성 (가중치: 0.2)
        unique_pages = user_data['page'].nunique()
        diversity_score = min(unique_pages / 10, 1.0) * 0.2
        
        return session_score + duration_score + frequency_score + diversity_score
    
    def predict_performance(self, df: pd.DataFrame, metric: str, hours_ahead: int = 24) -> PerformancePrediction:
        """성능 예측"""
        if metric not in df.columns or df.empty:
            return None
        
        # 특성 엔지니어링
        df_features = df.copy()
        df_features['hour'] = df_features.index.hour
        df_features['day_of_week'] = df_features.index.dayofweek
        df_features['is_weekend'] = df_features['day_of_week'].isin([5, 6]).astype(int)
        
        # 이동 평균 특성
        for window in [1, 3, 6, 12]:
            df_features[f'{metric}_ma_{window}'] = df_features[metric].rolling(window=window).mean()
        
        # 시차 특성
        for lag in [1, 2, 3, 6]:
            df_features[f'{metric}_lag_{lag}'] = df_features[metric].shift(lag)
        
        # NaN 값 제거
        df_features = df_features.dropna()
        
        if len(df_features) < 24:  # 최소 데이터 요구사항
            return None
        
        # 특성 선택
        feature_columns = [col for col in df_features.columns if col != metric and not col.startswith('timestamp')]
        X = df_features[feature_columns]
        y = df_features[metric]
        
        # 데이터 분할
        split_idx = int(len(df_features) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # 모델 훈련
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # 예측
        last_features = X.iloc[-1:].values
        prediction = model.predict(last_features)[0]
        
        # 신뢰 구간 계산 (간단한 방법)
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        std_error = np.sqrt(mse)
        
        confidence_interval = (prediction - 2*std_error, prediction + 2*std_error)
        
        # 중요도 요인
        feature_importance = dict(zip(feature_columns, model.feature_importances_))
        top_factors = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5])
        
        return PerformancePrediction(
            metric=metric,
            prediction_time=time.time() + (hours_ahead * 3600),
            predicted_value=prediction,
            confidence_interval=confidence_interval,
            factors=top_factors
        )
    
    def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """성능 보고서 생성"""
        # 데이터 로드
        metrics_df = self.load_metrics_data(hours)
        activity_df = self.load_user_activity_data(hours)
        
        if metrics_df.empty:
            return {"error": "데이터가 없습니다"}
        
        # 분석 수행
        trends = self.analyze_trends(metrics_df)
        anomalies = self.detect_anomalies(metrics_df)
        user_behaviors = self.analyze_user_behavior(activity_df)
        
        # 예측 수행
        predictions = {}
        for metric in ['cpu_percent', 'memory_percent', 'active_users', 'response_time_avg']:
            if metric in metrics_df.columns:
                pred = self.predict_performance(metrics_df, metric)
                if pred:
                    predictions[metric] = pred
        
        # 요약 통계
        summary_stats = {
            'total_requests': metrics_df['request_count'].sum(),
            'total_errors': metrics_df['error_count'].sum(),
            'avg_cpu_usage': metrics_df['cpu_percent'].mean(),
            'avg_memory_usage': metrics_df['memory_percent'].mean(),
            'avg_response_time': metrics_df['response_time_avg'].mean(),
            'peak_active_users': metrics_df['active_users'].max(),
            'total_anomalies': len(anomalies),
            'total_users_analyzed': len(user_behaviors)
        }
        
        # 시간대별 분석
        hourly_stats = metrics_df.resample('H').agg({
            'cpu_percent': 'mean',
            'memory_percent': 'mean',
            'active_users': 'mean',
            'request_count': 'sum',
            'error_count': 'sum'
        }).fillna(0)
        
        return {
            'summary': summary_stats,
            'trends': [asdict(trend) for trend in trends],
            'anomalies': [asdict(anomaly) for anomaly in anomalies],
            'user_behaviors': [asdict(behavior) for behavior in user_behaviors],
            'predictions': {k: asdict(v) for k, v in predictions.items()},
            'hourly_stats': hourly_stats.to_dict('index'),
            'report_generated_at': datetime.now().isoformat()
        }
    
    def create_visualizations(self, hours: int = 24, save_path: str = "static/reports/"):
        """시각화 생성"""
        import os
        os.makedirs(save_path, exist_ok=True)
        
        # 데이터 로드
        metrics_df = self.load_metrics_data(hours)
        activity_df = self.load_user_activity_data(hours)
        
        if metrics_df.empty:
            return {"error": "시각화할 데이터가 없습니다"}
        
        # 스타일 설정
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. 시스템 메트릭 시계열
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('시스템 성능 메트릭', fontsize=16)
        
        metrics_to_plot = ['cpu_percent', 'memory_percent', 'active_users', 'response_time_avg']
        titles = ['CPU 사용률 (%)', '메모리 사용률 (%)', '활성 사용자 수', '평균 응답 시간 (초)']
        
        for i, (metric, title) in enumerate(zip(metrics_to_plot, titles)):
            if metric in metrics_df.columns:
                ax = axes[i//2, i%2]
                metrics_df[metric].plot(ax=ax, linewidth=2)
                ax.set_title(title)
                ax.set_xlabel('시간')
                ax.set_ylabel('값')
                ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{save_path}system_metrics.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 사용자 활동 히트맵
        if not activity_df.empty:
            activity_df['hour'] = activity_df['datetime'].dt.hour
            activity_df['day_of_week'] = activity_df['datetime'].dt.dayofweek
            
            activity_pivot = activity_df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
            
            plt.figure(figsize=(12, 6))
            sns.heatmap(activity_pivot, annot=True, fmt='d', cmap='YlOrRd')
            plt.title('사용자 활동 히트맵 (요일별/시간별)')
            plt.xlabel('시간')
            plt.ylabel('요일 (0=월요일, 6=일요일)')
            plt.savefig(f"{save_path}user_activity_heatmap.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. 에러율 분석
        if 'error_count' in metrics_df.columns and 'request_count' in metrics_df.columns:
            metrics_df['error_rate'] = (metrics_df['error_count'] / metrics_df['request_count'] * 100).fillna(0)
            
            plt.figure(figsize=(12, 6))
            metrics_df['error_rate'].plot(linewidth=2, color='red')
            plt.title('에러율 추이')
            plt.xlabel('시간')
            plt.ylabel('에러율 (%)')
            plt.grid(True, alpha=0.3)
            plt.savefig(f"{save_path}error_rate.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # 4. 상관관계 분석
        correlation_metrics = ['cpu_percent', 'memory_percent', 'active_users', 'response_time_avg']
        correlation_df = metrics_df[correlation_metrics].corr()
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(correlation_df, annot=True, cmap='coolwarm', center=0, vmin=-1, vmax=1)
        plt.title('메트릭 간 상관관계')
        plt.savefig(f"{save_path}correlation_matrix.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        return {
            "visualizations_created": [
                "system_metrics.png",
                "user_activity_heatmap.png", 
                "error_rate.png",
                "correlation_matrix.png"
            ],
            "save_path": save_path
        }
    
    def get_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """성능 최적화 권장사항 생성"""
        recommendations = []
        
        # CPU 사용률 관련
        avg_cpu = report['summary']['avg_cpu_usage']
        if avg_cpu > 80:
            recommendations.append("CPU 사용률이 높습니다. 서버 리소스를 확장하거나 애플리케이션 최적화를 고려하세요.")
        elif avg_cpu < 20:
            recommendations.append("CPU 사용률이 낮습니다. 서버 리소스를 줄여 비용을 절약할 수 있습니다.")
        
        # 메모리 사용률 관련
        avg_memory = report['summary']['avg_memory_usage']
        if avg_memory > 85:
            recommendations.append("메모리 사용률이 높습니다. 메모리 누수를 확인하거나 메모리를 증설하세요.")
        
        # 응답 시간 관련
        avg_response_time = report['summary']['avg_response_time']
        if avg_response_time > 2.0:
            recommendations.append("응답 시간이 느립니다. 데이터베이스 쿼리 최적화나 캐싱을 고려하세요.")
        
        # 에러율 관련
        total_requests = report['summary']['total_requests']
        total_errors = report['summary']['total_errors']
        if total_requests > 0:
            error_rate = (total_errors / total_requests) * 100
            if error_rate > 5:
                recommendations.append("에러율이 높습니다. 로그를 확인하여 문제를 해결하세요.")
        
        # 트렌드 기반 권장사항
        for trend in report['trends']:
            if trend['metric'] == 'cpu_percent' and trend['trend'] == 'increasing':
                recommendations.append("CPU 사용률이 증가 추세입니다. 미리 리소스를 확장하세요.")
            elif trend['metric'] == 'active_users' and trend['trend'] == 'increasing':
                recommendations.append("사용자 수가 증가 추세입니다. 확장성을 고려한 아키텍처 검토가 필요합니다.")
        
        # 이상 탐지 기반 권장사항
        high_severity_anomalies = [a for a in report['anomalies'] if a['severity'] == 'high']
        if high_severity_anomalies:
            recommendations.append(f"심각한 이상이 {len(high_severity_anomalies)}건 발생했습니다. 즉시 조사가 필요합니다.")
        
        return recommendations
    
    def get_user_activity_summary(self, hours: int = 24) -> Dict[str, Any]:
        """사용자 활동 요약 조회"""
        try:
            df = self.load_user_activity_data(hours)
            
            if df.empty:
                return {
                    'total_users': 0,
                    'total_sessions': 0,
                    'avg_session_duration': 0,
                    'peak_hour': 0,
                    'most_visited_page': '',
                    'error_rate': 0
                }
            
            # 기본 통계
            total_users = df['user_id'].nunique()
            total_sessions = df['session_id'].nunique()
            avg_session_duration = df['duration'].mean()
            
            # 피크 시간
            df['hour'] = pd.to_datetime(df['timestamp'], unit='s').dt.hour
            peak_hour = df['hour'].mode().iloc[0] if not df['hour'].mode().empty else 0
            
            # 가장 많이 방문한 페이지
            most_visited_page = df['page'].mode().iloc[0] if not df['page'].mode().empty else ''
            
            # 에러율
            error_rate = (df['success'] == False).mean() * 100
            
            return {
                'total_users': int(total_users),
                'total_sessions': int(total_sessions),
                'avg_session_duration': round(avg_session_duration, 2),
                'peak_hour': int(peak_hour),
                'most_visited_page': most_visited_page,
                'error_rate': round(error_rate, 2)
            }
        except Exception as e:
            logger.error(f"사용자 활동 요약 조회 실패: {e}")
            return {
                'total_users': 0,
                'total_sessions': 0,
                'avg_session_duration': 0,
                'peak_hour': 0,
                'most_visited_page': '',
                'error_rate': 0
            }
    
    def get_user_activity_trends(self, hours: int = 24) -> Dict[str, Any]:
        """사용자 활동 트렌드 조회"""
        try:
            df = self.load_user_activity_data(hours)
            
            if df.empty:
                return {
                    'hourly_users': [],
                    'hourly_sessions': [],
                    'page_visits': []
                }
            
            # 시간별 사용자 수
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            df['hour'] = df['datetime'].dt.strftime('%Y-%m-%d %H:00:00')
            
            hourly_users = df.groupby('hour')['user_id'].nunique().reset_index()
            hourly_sessions = df.groupby('hour')['session_id'].nunique().reset_index()
            
            # 페이지별 방문 수
            page_visits = df['page'].value_counts().head(10).reset_index()
            page_visits.columns = ['page', 'visits']
            
            return {
                'hourly_users': hourly_users.to_dict('records'),
                'hourly_sessions': hourly_sessions.to_dict('records'),
                'page_visits': page_visits.to_dict('records')
            }
        except Exception as e:
            logger.error(f"사용자 활동 트렌드 조회 실패: {e}")
            return {
                'hourly_users': [],
                'hourly_sessions': [],
                'page_visits': []
            }
    
    def get_alert_trends(self, hours: int = 24) -> Dict[str, Any]:
        """알림 트렌드 조회"""
        try:
            # 실제로는 알림 데이터베이스에서 조회해야 함
            # 여기서는 예시 데이터 반환
            return {
                'hourly_alerts': [
                    {'hour': '2024-01-01 10:00:00', 'critical': 2, 'warning': 5, 'info': 10},
                    {'hour': '2024-01-01 11:00:00', 'critical': 1, 'warning': 3, 'info': 8},
                    {'hour': '2024-01-01 12:00:00', 'critical': 0, 'warning': 2, 'info': 6}
                ],
                'alert_types': [
                    {'type': 'CPU High', 'count': 10},
                    {'type': 'Memory High', 'count': 8},
                    {'type': 'Disk Full', 'count': 5}
                ]
            }
        except Exception as e:
            logger.error(f"알림 트렌드 조회 실패: {e}")
            return {
                'hourly_alerts': [],
                'alert_types': []
            }
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """성능 트렌드 조회"""
        try:
            df = self.load_metrics_data(hours)
            
            if df.empty:
                return {
                    'cpu_trend': [],
                    'memory_trend': [],
                    'response_time_trend': []
                }
            
            # 시간별 평균값 계산
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            df['hour'] = df['datetime'].dt.strftime('%Y-%m-%d %H:00:00')
            
            cpu_trend = df.groupby('hour')['cpu_percent'].mean().reset_index()
            memory_trend = df.groupby('hour')['memory_percent'].mean().reset_index()
            response_time_trend = df.groupby('hour')['response_time_avg'].mean().reset_index()
            
            return {
                'cpu_trend': cpu_trend.to_dict('records'),
                'memory_trend': memory_trend.to_dict('records'),
                'response_time_trend': response_time_trend.to_dict('records')
            }
        except Exception as e:
            logger.error(f"성능 트렌드 조회 실패: {e}")
            return {
                'cpu_trend': [],
                'memory_trend': [],
                'response_time_trend': []
            }
    
    def get_usage_patterns(self, days: int = 7) -> Dict[str, Any]:
        """사용 패턴 분석"""
        try:
            df = self.load_metrics_data(days * 24)
            
            if df.empty:
                return {
                    'daily_patterns': [],
                    'hourly_patterns': [],
                    'peak_usage': {}
                }
            
            # 일별 패턴
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            df['day'] = df['datetime'].dt.strftime('%Y-%m-%d')
            df['hour'] = df['datetime'].dt.hour
            
            daily_patterns = df.groupby('day').agg({
                'cpu_percent': 'mean',
                'memory_percent': 'mean',
                'active_users': 'mean'
            }).reset_index()
            
            # 시간별 패턴
            hourly_patterns = df.groupby('hour').agg({
                'cpu_percent': 'mean',
                'memory_percent': 'mean',
                'active_users': 'mean'
            }).reset_index()
            
            # 피크 사용량
            peak_usage = {
                'cpu_peak_hour': int(hourly_patterns.loc[hourly_patterns['cpu_percent'].idxmax(), 'hour']),
                'memory_peak_hour': int(hourly_patterns.loc[hourly_patterns['memory_percent'].idxmax(), 'hour']),
                'user_peak_hour': int(hourly_patterns.loc[hourly_patterns['active_users'].idxmax(), 'hour'])
            }
            
            return {
                'daily_patterns': daily_patterns.to_dict('records'),
                'hourly_patterns': hourly_patterns.to_dict('records'),
                'peak_usage': peak_usage
            }
        except Exception as e:
            logger.error(f"사용 패턴 분석 실패: {e}")
            return {
                'daily_patterns': [],
                'hourly_patterns': [],
                'peak_usage': {}
            }
    
    def get_performance_bottlenecks(self, days: int = 7) -> List[Dict[str, Any]]:
        """성능 병목 분석"""
        try:
            df = self.load_metrics_data(days * 24)
            
            if df.empty:
                return []
            
            bottlenecks = []
            
            # CPU 병목
            cpu_threshold = 80
            cpu_bottlenecks = df[df['cpu_percent'] > cpu_threshold]
            if not cpu_bottlenecks.empty:
                bottlenecks.append({
                    'type': 'CPU',
                    'severity': 'high' if cpu_bottlenecks['cpu_percent'].mean() > 90 else 'medium',
                    'frequency': len(cpu_bottlenecks),
                    'avg_value': round(cpu_bottlenecks['cpu_percent'].mean(), 2),
                    'max_value': round(cpu_bottlenecks['cpu_percent'].max(), 2)
                })
            
            # 메모리 병목
            memory_threshold = 85
            memory_bottlenecks = df[df['memory_percent'] > memory_threshold]
            if not memory_bottlenecks.empty:
                bottlenecks.append({
                    'type': 'Memory',
                    'severity': 'high' if memory_bottlenecks['memory_percent'].mean() > 95 else 'medium',
                    'frequency': len(memory_bottlenecks),
                    'avg_value': round(memory_bottlenecks['memory_percent'].mean(), 2),
                    'max_value': round(memory_bottlenecks['memory_percent'].max(), 2)
                })
            
            # 응답 시간 병목
            response_threshold = 2.0
            response_bottlenecks = df[df['response_time_avg'] > response_threshold]
            if not response_bottlenecks.empty:
                bottlenecks.append({
                    'type': 'Response Time',
                    'severity': 'high' if response_bottlenecks['response_time_avg'].mean() > 5.0 else 'medium',
                    'frequency': len(response_bottlenecks),
                    'avg_value': round(response_bottlenecks['response_time_avg'].mean(), 2),
                    'max_value': round(response_bottlenecks['response_time_avg'].max(), 2)
                })
            
            return bottlenecks
        except Exception as e:
            logger.error(f"성능 병목 분석 실패: {e}")
            return []
    
    def get_user_behavior_analysis(self, days: int = 7) -> Dict[str, Any]:
        """사용자 행동 분석"""
        try:
            df = self.load_user_activity_data(days * 24)
            
            if df.empty:
                return {
                    'session_analysis': {},
                    'page_analysis': {},
                    'error_analysis': {}
                }
            
            # 세션 분석
            session_analysis = {
                'avg_duration': round(df['duration'].mean(), 2),
                'total_sessions': df['session_id'].nunique(),
                'unique_users': df['user_id'].nunique()
            }
            
            # 페이지 분석
            page_analysis = df['page'].value_counts().head(10).to_dict()
            
            # 에러 분석
            error_analysis = {
                'total_errors': len(df[df['success'] == False]),
                'error_rate': round((df['success'] == False).mean() * 100, 2),
                'common_errors': df[df['success'] == False]['error_message'].value_counts().head(5).to_dict()
            }
            
            return {
                'session_analysis': session_analysis,
                'page_analysis': page_analysis,
                'error_analysis': error_analysis
            }
        except Exception as e:
            logger.error(f"사용자 행동 분석 실패: {e}")
            return {
                'session_analysis': {},
                'page_analysis': {},
                'error_analysis': {}
            }
    
    def get_system_predictions(self, days: int = 7) -> Dict[str, Any]:
        """시스템 예측 분석"""
        try:
            df = self.load_metrics_data(days * 24)
            
            if df.empty:
                return {
                    'cpu_prediction': {},
                    'memory_prediction': {},
                    'user_prediction': {}
                }
            
            # 간단한 선형 예측 (실제로는 더 정교한 모델 사용)
            predictions = {}
            
            for metric in ['cpu_percent', 'memory_percent', 'active_users']:
                if metric in df.columns:
                    values = df[metric].dropna()
                    if len(values) > 1:
                        # 간단한 선형 트렌드
                        x = range(len(values))
                        slope = np.polyfit(x, values, 1)[0]
                        
                        # 다음 24시간 예측
                        next_24h = values.iloc[-1] + slope * 24
                        
                        predictions[f'{metric}_prediction'] = {
                            'current_value': round(values.iloc[-1], 2),
                            'predicted_24h': round(max(0, next_24h), 2),
                            'trend': 'increasing' if slope > 0 else 'decreasing',
                            'confidence': 0.7  # 예시 값
                        }
            
            return predictions
        except Exception as e:
            logger.error(f"시스템 예측 분석 실패: {e}")
            return {
                'cpu_prediction': {},
                'memory_prediction': {},
                'user_prediction': {}
            }
    
    def get_real_time_user_activity(self) -> Dict[str, Any]:
        """실시간 사용자 활동"""
        try:
            # 실제로는 실시간 데이터베이스에서 조회
            # 여기서는 예시 데이터 반환
            return {
                'active_users': 25,
                'current_sessions': 30,
                'recent_actions': [
                    {'user': 'user1', 'action': 'login', 'time': '2분 전'},
                    {'user': 'user2', 'action': 'dashboard_view', 'time': '1분 전'},
                    {'user': 'user3', 'action': 'report_generate', 'time': '30초 전'}
                ]
            }
        except Exception as e:
            logger.error(f"실시간 사용자 활동 조회 실패: {e}")
            return {
                'active_users': 0,
                'current_sessions': 0,
                'recent_actions': []
            }

# 전역 분석 인스턴스
analytics = AdvancedAnalytics()