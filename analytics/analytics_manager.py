import os
import json
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import uuid
import logging
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalyticsConfig:
    """분석 시스템 설정 클래스"""
    data_dir: str
    model_dir: str = "models"
    cache_dir: str = "cache"
    max_cache_size: int = 1000
    prediction_horizon: int = 30
    update_frequency: int = 3600
    enable_ml: bool = True
    enable_realtime: bool = True

@dataclass
class AnalysisResult:
    """분석 결과 정보"""
    analysis_id: str
    name: str
    type: str
    data_source: str
    parameters: Dict[str, Any]
    results: Dict[str, Any]
    accuracy: Optional[float] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class PredictionModel:
    """예측 모델 정보"""
    model_id: str
    name: str
    type: str
    algorithm: str
    features: List[str]
    target: str
    accuracy: float
    model_data: Dict[str, Any]
    created_at: datetime = None
    last_updated: datetime = None

@dataclass
class AnalyticsInsight:
    """분석 인사이트 정보"""
    insight_id: str
    title: str
    description: str
    category: str
    confidence: float
    impact: str
    recommendations: List[str]
    data_sources: List[str]
    created_at: datetime = None

@dataclass
class RealTimeMetric:
    """실시간 메트릭 정보"""
    metric_id: str
    name: str
    value: float
    unit: str
    trend: str
    threshold: Optional[float] = None
    alert_level: str = "normal"
    timestamp: datetime = None

class AnalyticsManager:
    """데이터 분석 관리자 클래스"""
    
    def __init__(self, config: AnalyticsConfig):
        self.config = config
        self.analysis_results: Dict[str, AnalysisResult] = {}
        self.prediction_models: Dict[str, PredictionModel] = {}
        self.insights: List[AnalyticsInsight] = []
        self.realtime_metrics: List[RealTimeMetric] = []
        self.cache: Dict[str, Any] = {}
        
        # 설정 디렉토리 생성
        os.makedirs(config.data_dir, exist_ok=True)
        os.makedirs(os.path.join(config.data_dir, config.model_dir), exist_ok=True)
        os.makedirs(os.path.join(config.data_dir, config.cache_dir), exist_ok=True)
        
        # 데이터베이스 초기화
        self.init_database()
        
        # 기본 모델 생성
        self.create_default_models()
        
        # 기존 데이터 로드
        self.load_data()
    
    def init_database(self):
        """분석 데이터베이스 초기화"""
        db_path = os.path.join(self.config.data_dir, 'analytics.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 분석 결과 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                analysis_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                data_source TEXT NOT NULL,
                parameters TEXT NOT NULL,
                results TEXT NOT NULL,
                accuracy REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # 예측 모델 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prediction_models (
                model_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                algorithm TEXT NOT NULL,
                features TEXT NOT NULL,
                target TEXT NOT NULL,
                accuracy REAL NOT NULL,
                model_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_updated TEXT NOT NULL
            )
        ''')
        
        # 인사이트 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                insight_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                confidence REAL NOT NULL,
                impact TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                data_sources TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # 실시간 메트릭 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS realtime_metrics (
                metric_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                trend TEXT NOT NULL,
                threshold REAL,
                alert_level TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_default_models(self):
        """기본 예측 모델 생성"""
        self.create_prediction_model(
            name="매출 예측 모델",
            model_type="sales",
            algorithm="linear_regression",
            features=["month", "day_of_week", "holiday", "promotion"],
            target="sales_amount"
        )
        
        self.create_prediction_model(
            name="재고 예측 모델",
            model_type="inventory",
            algorithm="linear_regression",
            features=["current_stock", "sales_rate", "lead_time", "seasonality"],
            target="required_stock"
        )
    
    def create_prediction_model(self, name: str, model_type: str, algorithm: str,
                               features: List[str], target: str) -> str:
        """예측 모델 생성"""
        model_id = str(uuid.uuid4())
        
        model = PredictionModel(
            model_id=model_id,
            name=name,
            type=model_type,
            algorithm=algorithm,
            features=features,
            target=target,
            accuracy=0.0,
            model_data={},
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        
        self.prediction_models[model_id] = model
        self._save_prediction_model(model)
        
        logger.info(f"예측 모델 생성: {name}")
        return model_id
    
    def analyze_trends(self, data_source: str, metric: str, 
                      time_period: str = "30d") -> AnalysisResult:
        """트렌드 분석"""
        analysis_id = str(uuid.uuid4())
        
        # 모의 데이터 생성
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                            end=datetime.now(), freq='D')
        values = np.random.normal(100, 20, len(dates)) + np.linspace(0, 50, len(dates))
        
        # 트렌드 계산
        slope, intercept = np.polyfit(range(len(values)), values, 1)
        trend_direction = "up" if slope > 0 else "down"
        trend_strength = abs(slope)
        
        results = {
            "trend_direction": trend_direction,
            "trend_strength": float(trend_strength),
            "slope": float(slope),
            "intercept": float(intercept),
            "data_points": len(values),
            "mean_value": float(np.mean(values)),
            "std_value": float(np.std(values)),
            "min_value": float(np.min(values)),
            "max_value": float(np.max(values))
        }
        
        analysis = AnalysisResult(
            analysis_id=analysis_id,
            name=f"{metric} 트렌드 분석",
            type="trend",
            data_source=data_source,
            parameters={"metric": metric, "time_period": time_period},
            results=results,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.analysis_results[analysis_id] = analysis
        self._save_analysis_result(analysis)
        
        return analysis
    
    def predict_sales(self, days_ahead: int = 30) -> Dict[str, Any]:
        """매출 예측"""
        # 모의 데이터 생성
        dates = pd.date_range(start=datetime.now() - timedelta(days=90), 
                            end=datetime.now(), freq='D')
        
        # 기본 매출 패턴
        base_sales = 1000
        trend = np.linspace(0, 200, len(dates))
        seasonality = 50 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)
        noise = np.random.normal(0, 50, len(dates))
        
        historical_sales = base_sales + trend + seasonality + noise
        
        # 특성 생성
        features = []
        for i in range(len(dates)):
            feature_vector = [
                dates[i].month,
                dates[i].weekday(),
                1 if dates[i].weekday() in [5, 6] else 0,
                1 if i % 30 < 7 else 0
            ]
            features.append(feature_vector)
        
        # 모델 훈련
        model = LinearRegression()
        model.fit(features, historical_sales)
        
        # 미래 예측
        future_dates = pd.date_range(start=datetime.now(), 
                                   periods=days_ahead, freq='D')
        future_features = []
        
        for i, date in enumerate(future_dates):
            feature_vector = [
                date.month,
                date.weekday(),
                1 if date.weekday() in [5, 6] else 0,
                1 if i < 7 else 0
            ]
            future_features.append(feature_vector)
        
        predictions = model.predict(future_features)
        
        return {
            "predictions": predictions.tolist(),
            "dates": [d.strftime('%Y-%m-%d') for d in future_dates],
            "model_accuracy": r2_score(historical_sales, model.predict(features)),
            "total_predicted_sales": float(np.sum(predictions)),
            "avg_daily_sales": float(np.mean(predictions))
        }
    
    def analyze_correlations(self, data_source: str, 
                           variables: List[str]) -> AnalysisResult:
        """상관관계 분석"""
        analysis_id = str(uuid.uuid4())
        
        # 모의 데이터 생성
        n_samples = 100
        data = {}
        
        for var in variables:
            if var == "sales":
                data[var] = np.random.normal(1000, 200, n_samples)
            elif var == "advertising":
                data[var] = np.random.normal(500, 100, n_samples)
            elif var == "price":
                data[var] = np.random.normal(50, 10, n_samples)
            elif var == "customer_satisfaction":
                data[var] = np.random.normal(4.0, 0.5, n_samples)
            else:
                data[var] = np.random.normal(0, 1, n_samples)
        
        # 상관관계 계산
        df = pd.DataFrame(data)
        correlation_matrix = df.corr()
        
        # 강한 상관관계 찾기
        strong_correlations = []
        for i in range(len(variables)):
            for j in range(i+1, len(variables)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        "variable1": variables[i],
                        "variable2": variables[j],
                        "correlation": float(corr_value),
                        "strength": "strong" if abs(corr_value) > 0.8 else "moderate"
                    })
        
        results = {
            "correlation_matrix": correlation_matrix.to_dict(),
            "strong_correlations": strong_correlations,
            "variables": variables,
            "sample_size": n_samples
        }
        
        analysis = AnalysisResult(
            analysis_id=analysis_id,
            name="상관관계 분석",
            type="correlation",
            data_source=data_source,
            parameters={"variables": variables},
            results=results,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.analysis_results[analysis_id] = analysis
        self._save_analysis_result(analysis)
        
        return analysis
    
    def perform_clustering(self, data_source: str, features: List[str],
                          n_clusters: int = 3) -> AnalysisResult:
        """클러스터링 분석"""
        analysis_id = str(uuid.uuid4())
        
        # 모의 고객 데이터 생성
        n_customers = 200
        data = {}
        
        for feature in features:
            if feature == "purchase_frequency":
                data[feature] = np.random.exponential(5, n_customers)
            elif feature == "avg_order_value":
                data[feature] = np.random.normal(100, 30, n_customers)
            elif feature == "customer_lifetime":
                data[feature] = np.random.normal(24, 8, n_customers)
            else:
                data[feature] = np.random.normal(0, 1, n_customers)
        
        # 데이터 정규화
        df = pd.DataFrame(data)
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df)
        
        # K-means 클러스터링
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(scaled_data)
        
        # 클러스터 특성 분석
        df['cluster'] = clusters
        cluster_characteristics = {}
        
        for cluster_id in range(n_clusters):
            cluster_data = df[df['cluster'] == cluster_id]
            characteristics = {}
            
            for feature in features:
                characteristics[feature] = {
                    "mean": float(cluster_data[feature].mean()),
                    "std": float(cluster_data[feature].std()),
                    "min": float(cluster_data[feature].min()),
                    "max": float(cluster_data[feature].max())
                }
            
            cluster_characteristics[f"cluster_{cluster_id}"] = {
                "size": len(cluster_data),
                "percentage": len(cluster_data) / len(df) * 100,
                "characteristics": characteristics
            }
        
        results = {
            "n_clusters": n_clusters,
            "cluster_assignments": clusters.tolist(),
            "cluster_centers": kmeans.cluster_centers_.tolist(),
            "cluster_characteristics": cluster_characteristics,
            "inertia": float(kmeans.inertia_),
            "features": features
        }
        
        analysis = AnalysisResult(
            analysis_id=analysis_id,
            name="고객 세그먼트 분석",
            type="clustering",
            data_source=data_source,
            parameters={"features": features, "n_clusters": n_clusters},
            results=results,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.analysis_results[analysis_id] = analysis
        self._save_analysis_result(analysis)
        
        return analysis
    
    def detect_anomalies(self, data_source: str, metric: str,
                        threshold: float = 2.0) -> AnalysisResult:
        """이상 탐지"""
        analysis_id = str(uuid.uuid4())
        
        # 모의 시계열 데이터 생성
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                            end=datetime.now(), freq='D')
        values = np.random.normal(100, 20, len(dates))
        
        # 이상값 추가
        anomaly_indices = [5, 15, 25]
        for idx in anomaly_indices:
            values[idx] += np.random.normal(100, 30)
        
        # 이상 탐지 (Z-score 기반)
        mean_val = np.mean(values)
        std_val = np.std(values)
        z_scores = np.abs((values - mean_val) / std_val)
        
        anomalies = []
        for i, z_score in enumerate(z_scores):
            if z_score > threshold:
                anomalies.append({
                    "index": i,
                    "date": dates[i].strftime('%Y-%m-%d'),
                    "value": float(values[i]),
                    "z_score": float(z_score),
                    "severity": "high" if z_score > 3 else "medium"
                })
        
        results = {
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "threshold": threshold,
            "mean_value": float(mean_val),
            "std_value": float(std_val),
            "data_points": len(values),
            "anomaly_percentage": len(anomalies) / len(values) * 100
        }
        
        analysis = AnalysisResult(
            analysis_id=analysis_id,
            name=f"{metric} 이상 탐지",
            type="anomaly",
            data_source=data_source,
            parameters={"metric": metric, "threshold": threshold},
            results=results,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.analysis_results[analysis_id] = analysis
        self._save_analysis_result(analysis)
        
        return analysis
    
    def generate_insights(self) -> List[AnalyticsInsight]:
        """자동 인사이트 생성"""
        insights = []
        
        # 매출 트렌드 인사이트
        sales_trend = self.analyze_trends("sales", "daily_sales")
        if sales_trend.results["trend_direction"] == "up":
            insights.append(AnalyticsInsight(
                insight_id=str(uuid.uuid4()),
                title="매출 상승 트렌드 감지",
                description="최근 30일간 매출이 지속적으로 상승하고 있습니다.",
                category="sales",
                confidence=0.85,
                impact="high",
                recommendations=[
                    "재고 수준을 적절히 유지하세요",
                    "성공적인 마케팅 전략을 계속 유지하세요",
                    "고객 만족도 모니터링을 강화하세요"
                ],
                data_sources=["sales_data"],
                created_at=datetime.utcnow()
            ))
        
        # 고객 세그먼트 인사이트
        clustering_result = self.perform_clustering("customer", 
                                                   ["purchase_frequency", "avg_order_value"])
        
        high_value_cluster = None
        for cluster_id, cluster_info in clustering_result.results["cluster_characteristics"].items():
            if cluster_info["characteristics"]["avg_order_value"]["mean"] > 120:
                high_value_cluster = cluster_id
                break
        
        if high_value_cluster:
            insights.append(AnalyticsInsight(
                insight_id=str(uuid.uuid4()),
                title="고가치 고객 세그먼트 발견",
                description="평균 주문 금액이 높은 고객 세그먼트가 확인되었습니다.",
                category="customer",
                confidence=0.78,
                impact="medium",
                recommendations=[
                    "고가치 고객을 위한 VIP 프로그램 개발",
                    "개인화된 마케팅 캠페인 실행",
                    "고가치 고객의 이탈 방지 전략 수립"
                ],
                data_sources=["customer_data"],
                created_at=datetime.utcnow()
            ))
        
        self.insights.extend(insights)
        for insight in insights:
            self._save_insight(insight)
        
        return insights
    
    def update_realtime_metrics(self):
        """실시간 메트릭 업데이트"""
        current_time = datetime.utcnow()
        
        metrics = [
            RealTimeMetric(
                metric_id=str(uuid.uuid4()),
                name="실시간 매출",
                value=np.random.normal(1000, 100),
                unit="원",
                trend="up" if np.random.random() > 0.5 else "down",
                threshold=800,
                alert_level="normal",
                timestamp=current_time
            ),
            RealTimeMetric(
                metric_id=str(uuid.uuid4()),
                name="활성 사용자",
                value=np.random.normal(150, 20),
                unit="명",
                trend="stable",
                threshold=100,
                alert_level="normal",
                timestamp=current_time
            ),
            RealTimeMetric(
                metric_id=str(uuid.uuid4()),
                name="시스템 응답 시간",
                value=np.random.normal(200, 50),
                unit="ms",
                trend="down" if np.random.random() > 0.7 else "up",
                threshold=500,
                alert_level="warning" if np.random.random() > 0.8 else "normal",
                timestamp=current_time
            )
        ]
        
        # 이전 메트릭 제거 (최근 100개만 유지)
        self.realtime_metrics = metrics + self.realtime_metrics[:97]
        
        # 데이터베이스에 저장
        for metric in metrics:
            self._save_realtime_metric(metric)
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """분석 요약 정보"""
        return {
            "total_analyses": len(self.analysis_results),
            "total_models": len(self.prediction_models),
            "total_insights": len(self.insights),
            "realtime_metrics": len(self.realtime_metrics),
            "analysis_types": {
                "trend": len([a for a in self.analysis_results.values() if a.type == "trend"]),
                "prediction": len([a for a in self.analysis_results.values() if a.type == "prediction"]),
                "correlation": len([a for a in self.analysis_results.values() if a.type == "correlation"]),
                "clustering": len([a for a in self.analysis_results.values() if a.type == "clustering"]),
                "anomaly": len([a for a in self.analysis_results.values() if a.type == "anomaly"])
            },
            "insight_categories": {
                "sales": len([i for i in self.insights if i.category == "sales"]),
                "customer": len([i for i in self.insights if i.category == "customer"]),
                "anomaly": len([i for i in self.insights if i.category == "anomaly"])
            },
            "model_accuracy": {
                model.name: model.accuracy 
                for model in self.prediction_models.values()
            }
        }
    
    def load_data(self):
        """데이터 로드"""
        try:
            self._load_analysis_results()
            self._load_prediction_models()
            self._load_insights()
            self._load_realtime_metrics()
            
            logger.info(f"분석 데이터 로드 완료: {len(self.analysis_results)}개 분석, {len(self.prediction_models)}개 모델")
            
        except Exception as e:
            logger.error(f"분석 데이터 로드 오류: {str(e)}")
    
    # 데이터베이스 저장 메서드들
    def _save_analysis_result(self, analysis: AnalysisResult):
        """분석 결과를 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'analytics.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO analysis_results 
            (analysis_id, name, type, data_source, parameters, results, 
             accuracy, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis.analysis_id,
            analysis.name,
            analysis.type,
            analysis.data_source,
            json.dumps(analysis.parameters),
            json.dumps(analysis.results),
            analysis.accuracy,
            analysis.created_at.isoformat(),
            analysis.updated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_prediction_model(self, model: PredictionModel):
        """예측 모델을 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'analytics.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO prediction_models 
            (model_id, name, type, algorithm, features, target, accuracy, 
             model_data, created_at, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            model.model_id,
            model.name,
            model.type,
            model.algorithm,
            json.dumps(model.features),
            model.target,
            model.accuracy,
            json.dumps(model.model_data),
            model.created_at.isoformat(),
            model.last_updated.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_insight(self, insight: AnalyticsInsight):
        """인사이트를 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'analytics.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO insights 
            (insight_id, title, description, category, confidence, impact, 
             recommendations, data_sources, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            insight.insight_id,
            insight.title,
            insight.description,
            insight.category,
            insight.confidence,
            insight.impact,
            json.dumps(insight.recommendations),
            json.dumps(insight.data_sources),
            insight.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_realtime_metric(self, metric: RealTimeMetric):
        """실시간 메트릭을 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'analytics.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO realtime_metrics 
            (metric_id, name, value, unit, trend, threshold, alert_level, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metric.metric_id,
            metric.name,
            metric.value,
            metric.unit,
            metric.trend,
            metric.threshold,
            metric.alert_level,
            metric.timestamp.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _load_analysis_results(self):
        """데이터베이스에서 분석 결과 로드"""
        db_path = os.path.join(self.config.data_dir, 'analytics.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM analysis_results')
        rows = cursor.fetchall()
        
        for row in rows:
            analysis = AnalysisResult(
                analysis_id=row[0],
                name=row[1],
                type=row[2],
                data_source=row[3],
                parameters=json.loads(row[4]),
                results=json.loads(row[5]),
                accuracy=row[6],
                created_at=datetime.fromisoformat(row[7]),
                updated_at=datetime.fromisoformat(row[8])
            )
            self.analysis_results[analysis.analysis_id] = analysis
        
        conn.close()
    
    def _load_prediction_models(self):
        """데이터베이스에서 예측 모델 로드"""
        db_path = os.path.join(self.config.data_dir, 'analytics.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM prediction_models')
        rows = cursor.fetchall()
        
        for row in rows:
            model = PredictionModel(
                model_id=row[0],
                name=row[1],
                type=row[2],
                algorithm=row[3],
                features=json.loads(row[4]),
                target=row[5],
                accuracy=row[6],
                model_data=json.loads(row[7]),
                created_at=datetime.fromisoformat(row[8]),
                last_updated=datetime.fromisoformat(row[9])
            )
            self.prediction_models[model.model_id] = model
        
        conn.close()
    
    def _load_insights(self):
        """데이터베이스에서 인사이트 로드"""
        db_path = os.path.join(self.config.data_dir, 'analytics.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM insights ORDER BY created_at DESC LIMIT 100')
        rows = cursor.fetchall()
        
        for row in rows:
            insight = AnalyticsInsight(
                insight_id=row[0],
                title=row[1],
                description=row[2],
                category=row[3],
                confidence=row[4],
                impact=row[5],
                recommendations=json.loads(row[6]),
                data_sources=json.loads(row[7]),
                created_at=datetime.fromisoformat(row[8])
            )
            self.insights.append(insight)
        
        conn.close()
    
    def _load_realtime_metrics(self):
        """데이터베이스에서 실시간 메트릭 로드"""
        db_path = os.path.join(self.config.data_dir, 'analytics.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM realtime_metrics ORDER BY timestamp DESC LIMIT 100')
        rows = cursor.fetchall()
        
        for row in rows:
            metric = RealTimeMetric(
                metric_id=row[0],
                name=row[1],
                value=row[2],
                unit=row[3],
                trend=row[4],
                threshold=row[5],
                alert_level=row[6],
                timestamp=datetime.fromisoformat(row[7])
            )
            self.realtime_metrics.append(metric)
        
        conn.close() 