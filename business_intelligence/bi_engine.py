"""
비즈니스 인텔리전스 엔진
엔터프라이즈급 BI 분석 및 리포트 시스템
"""

import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import uuid
import hashlib

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """분석 타입"""
    TREND = "trend"
    COMPARISON = "comparison"
    CORRELATION = "correlation"
    FORECAST = "forecast"
    CLUSTERING = "clustering"
    ANOMALY = "anomaly"
    SEGMENTATION = "segmentation"

class ChartType(Enum):
    """차트 타입"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    BOX = "box"
    HISTOGRAM = "histogram"
    DASHBOARD = "dashboard"

@dataclass
class AnalysisRequest:
    """분석 요청"""
    id: str
    analysis_type: AnalysisType
    data_source: str
    dimensions: List[str]
    metrics: List[str]
    filters: Dict[str, Any]
    time_range: Dict[str, Any]
    chart_type: ChartType
    created_at: datetime
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

@dataclass
class ReportTemplate:
    """리포트 템플릿"""
    id: str
    name: str
    description: str
    analyses: List[Dict[str, Any]]
    layout: Dict[str, Any]
    schedule: Optional[Dict[str, Any]] = None
    recipients: List[str] = []
    created_at: datetime = None
    updated_at: datetime = None

class BusinessIntelligenceEngine:
    """비즈니스 인텔리전스 엔진"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_connection = None
        self.redis_client = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.analysis_requests: Dict[str, AnalysisRequest] = {}
        self.report_templates: Dict[str, ReportTemplate] = {}
        self.cache_ttl = 3600  # 1시간
        
        self._initialize_connections()
        self._load_report_templates()
    
    def _initialize_connections(self):
        """연결 초기화"""
        try:
            # PostgreSQL 연결
            self.db_connection = psycopg2.connect(
                host=self.config['database']['host'],
                port=self.config['database']['port'],
                database=self.config['database']['name'],
                user=self.config['database']['user'],
                password=self.config['database']['password']
            )
            
            # Redis 연결
            self.redis_client = redis.Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                db=self.config['redis']['db'],
                decode_responses=True
            )
            
            logger.info("BI 엔진 연결 초기화 완료")
            
        except Exception as e:
            logger.error(f"연결 초기화 오류: {e}")
            raise
    
    def _load_report_templates(self):
        """리포트 템플릿 로드"""
        try:
            # 기본 리포트 템플릿 정의
            self.report_templates = {
                'sales_dashboard': ReportTemplate(
                    id='sales_dashboard',
                    name='매출 대시보드',
                    description='일일/월간 매출 분석 대시보드',
                    analyses=[
                        {
                            'id': 'daily_sales_trend',
                            'name': '일일 매출 트렌드',
                            'type': AnalysisType.TREND,
                            'data_source': 'agg_daily_sales',
                            'dimensions': ['time_id'],
                            'metrics': ['total_sales'],
                            'chart_type': ChartType.LINE
                        },
                        {
                            'id': 'sales_by_category',
                            'name': '카테고리별 매출',
                            'type': AnalysisType.COMPARISON,
                            'data_source': 'fact_sales',
                            'dimensions': ['product_id'],
                            'metrics': ['total_amount'],
                            'chart_type': ChartType.PIE
                        },
                        {
                            'id': 'customer_segmentation',
                            'name': '고객 세분화',
                            'type': AnalysisType.SEGMENTATION,
                            'data_source': 'agg_user_behavior',
                            'dimensions': ['user_id'],
                            'metrics': ['total_sessions', 'avg_session_duration'],
                            'chart_type': ChartType.SCATTER
                        }
                    ],
                    layout={
                        'rows': 2,
                        'cols': 2,
                        'charts': [
                            {'id': 'daily_sales_trend', 'row': 1, 'col': 1, 'width': 2},
                            {'id': 'sales_by_category', 'row': 1, 'col': 2, 'width': 1},
                            {'id': 'customer_segmentation', 'row': 2, 'col': 1, 'width': 2}
                        ]
                    }
                ),
                
                'user_behavior_report': ReportTemplate(
                    id='user_behavior_report',
                    name='사용자 행동 리포트',
                    description='사용자 행동 패턴 분석',
                    analyses=[
                        {
                            'id': 'session_duration_analysis',
                            'name': '세션 지속시간 분석',
                            'type': AnalysisType.TREND,
                            'data_source': 'fact_user_activity',
                            'dimensions': ['time_id'],
                            'metrics': ['session_duration'],
                            'chart_type': ChartType.BOX
                        },
                        {
                            'id': 'page_views_heatmap',
                            'name': '페이지뷰 히트맵',
                            'type': AnalysisType.CORRELATION,
                            'data_source': 'fact_user_activity',
                            'dimensions': ['time_id', 'activity_type'],
                            'metrics': ['page_views'],
                            'chart_type': ChartType.HEATMAP
                        }
                    ],
                    layout={
                        'rows': 1,
                        'cols': 2,
                        'charts': [
                            {'id': 'session_duration_analysis', 'row': 1, 'col': 1, 'width': 1},
                            {'id': 'page_views_heatmap', 'row': 1, 'col': 2, 'width': 1}
                        ]
                    }
                )
            }
            
            logger.info(f"{len(self.report_templates)}개의 리포트 템플릿 로드 완료")
            
        except Exception as e:
            logger.error(f"리포트 템플릿 로드 오류: {e}")
    
    def create_analysis(self, analysis_type: AnalysisType, data_source: str,
                       dimensions: List[str], metrics: List[str],
                       filters: Dict[str, Any] = None,
                       time_range: Dict[str, Any] = None,
                       chart_type: ChartType = ChartType.LINE) -> str:
        """분석 요청 생성"""
        try:
            analysis_id = str(uuid.uuid4())
            
            request = AnalysisRequest(
                id=analysis_id,
                analysis_type=analysis_type,
                data_source=data_source,
                dimensions=dimensions,
                metrics=metrics,
                filters=filters or {},
                time_range=time_range or {},
                chart_type=chart_type,
                created_at=datetime.now()
            )
            
            self.analysis_requests[analysis_id] = request
            
            # 비동기로 분석 실행
            self.executor.submit(self._execute_analysis, analysis_id)
            
            logger.info(f"분석 요청 생성: {analysis_id} ({analysis_type.value})")
            return analysis_id
            
        except Exception as e:
            logger.error(f"분석 요청 생성 오류: {e}")
            raise
    
    def _execute_analysis(self, analysis_id: str):
        """분석 실행"""
        request = self.analysis_requests[analysis_id]
        
        try:
            request.status = "running"
            
            # 데이터 조회
            data = self._fetch_data(request)
            
            # 분석 수행
            if request.analysis_type == AnalysisType.TREND:
                result = self._perform_trend_analysis(data, request)
            elif request.analysis_type == AnalysisType.COMPARISON:
                result = self._perform_comparison_analysis(data, request)
            elif request.analysis_type == AnalysisType.CORRELATION:
                result = self._perform_correlation_analysis(data, request)
            elif request.analysis_type == AnalysisType.FORECAST:
                result = self._perform_forecast_analysis(data, request)
            elif request.analysis_type == AnalysisType.CLUSTERING:
                result = self._perform_clustering_analysis(data, request)
            elif request.analysis_type == AnalysisType.ANOMALY:
                result = self._perform_anomaly_analysis(data, request)
            elif request.analysis_type == AnalysisType.SEGMENTATION:
                result = self._perform_segmentation_analysis(data, request)
            else:
                raise ValueError(f"지원하지 않는 분석 타입: {request.analysis_type}")
            
            # 차트 생성
            chart = self._create_chart(data, request, result)
            
            request.result = {
                'data': data.to_dict('records'),
                'analysis': result,
                'chart': chart,
                'summary': self._generate_summary(result, request.analysis_type)
            }
            
            request.status = "completed"
            
            # 결과 캐시
            self._cache_result(analysis_id, request.result)
            
            logger.info(f"분석 완료: {analysis_id}")
            
        except Exception as e:
            request.status = "failed"
            request.error_message = str(e)
            logger.error(f"분석 실패: {analysis_id} - {e}")
    
    def _fetch_data(self, request: AnalysisRequest) -> pd.DataFrame:
        """데이터 조회"""
        try:
            # 캐시 확인
            cache_key = self._generate_cache_key(request)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return pd.DataFrame(json.loads(cached_data))
            
            # SQL 쿼리 생성
            sql = self._build_query(request)
            
            # 데이터 조회
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql)
                data = pd.DataFrame(cursor.fetchall())
            
            # 데이터 캐시
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                data.to_json()
            )
            
            return data
            
        except Exception as e:
            logger.error(f"데이터 조회 오류: {e}")
            raise
    
    def _build_query(self, request: AnalysisRequest) -> str:
        """SQL 쿼리 생성"""
        try:
            # 기본 SELECT 절
            select_clause = ", ".join(request.dimensions + request.metrics)
            
            # FROM 절
            from_clause = f"FROM {request.data_source}"
            
            # WHERE 절
            where_conditions = []
            
            # 필터 조건
            for key, value in request.filters.items():
                if isinstance(value, list):
                    where_conditions.append(f"{key} IN ({','.join([f\"'{v}'\" for v in value])})")
                else:
                    where_conditions.append(f"{key} = '{value}'")
            
            # 시간 범위 조건
            if request.time_range:
                start_date = request.time_range.get('start_date')
                end_date = request.time_range.get('end_date')
                
                if start_date:
                    where_conditions.append(f"time_id >= '{start_date}'")
                if end_date:
                    where_conditions.append(f"time_id <= '{end_date}'")
            
            where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
            
            # GROUP BY 절
            group_by_clause = f"GROUP BY {', '.join(request.dimensions)}" if request.dimensions else ""
            
            # ORDER BY 절
            order_by_clause = f"ORDER BY {', '.join(request.dimensions)}"
            
            # 최종 쿼리
            sql = f"""
            SELECT {select_clause}
            {from_clause}
            {where_clause}
            {group_by_clause}
            {order_by_clause}
            """
            
            return sql
            
        except Exception as e:
            logger.error(f"쿼리 생성 오류: {e}")
            raise
    
    def _perform_trend_analysis(self, data: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """트렌드 분석"""
        try:
            result = {
                'trend_direction': 'stable',
                'growth_rate': 0.0,
                'seasonality': False,
                'outliers': []
            }
            
            if len(data) < 2:
                return result
            
            # 주요 메트릭 선택
            metric = request.metrics[0] if request.metrics else data.columns[-1]
            
            # 트렌드 방향 계산
            values = data[metric].values
            if len(values) >= 2:
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                first_avg = np.mean(first_half)
                second_avg = np.mean(second_half)
                
                if second_avg > first_avg * 1.1:
                    result['trend_direction'] = 'increasing'
                elif second_avg < first_avg * 0.9:
                    result['trend_direction'] = 'decreasing'
                
                # 성장률 계산
                if first_avg > 0:
                    result['growth_rate'] = ((second_avg - first_avg) / first_avg) * 100
            
            # 이상치 탐지
            z_scores = np.abs(stats.zscore(values))
            outliers = np.where(z_scores > 2)[0]
            result['outliers'] = outliers.tolist()
            
            return result
            
        except Exception as e:
            logger.error(f"트렌드 분석 오류: {e}")
            raise
    
    def _perform_comparison_analysis(self, data: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """비교 분석"""
        try:
            result = {
                'top_performers': [],
                'bottom_performers': [],
                'distribution': {},
                'insights': []
            }
            
            if len(data) == 0:
                return result
            
            # 주요 메트릭 선택
            metric = request.metrics[0] if request.metrics else data.columns[-1]
            dimension = request.dimensions[0] if request.dimensions else data.columns[0]
            
            # 상위/하위 성과자
            sorted_data = data.sort_values(metric, ascending=False)
            result['top_performers'] = sorted_data.head(5)[[dimension, metric]].to_dict('records')
            result['bottom_performers'] = sorted_data.tail(5)[[dimension, metric]].to_dict('records')
            
            # 분포 분석
            result['distribution'] = {
                'mean': float(data[metric].mean()),
                'median': float(data[metric].median()),
                'std': float(data[metric].std()),
                'min': float(data[metric].min()),
                'max': float(data[metric].max())
            }
            
            # 인사이트 생성
            if len(data) > 1:
                top_avg = sorted_data.head(len(data)//4)[metric].mean()
                bottom_avg = sorted_data.tail(len(data)//4)[metric].mean()
                
                if top_avg > bottom_avg * 2:
                    result['insights'].append("상위 25%와 하위 25% 간 성과 차이가 큽니다")
                
                if data[metric].std() > data[metric].mean() * 0.5:
                    result['insights'].append("데이터 변동성이 높습니다")
            
            return result
            
        except Exception as e:
            logger.error(f"비교 분석 오류: {e}")
            raise
    
    def _perform_correlation_analysis(self, data: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """상관관계 분석"""
        try:
            result = {
                'correlation_matrix': {},
                'strong_correlations': [],
                'weak_correlations': [],
                'insights': []
            }
            
            if len(data) < 2:
                return result
            
            # 수치형 컬럼만 선택
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            
            if len(numeric_columns) < 2:
                return result
            
            # 상관관계 계산
            correlation_matrix = data[numeric_columns].corr()
            result['correlation_matrix'] = correlation_matrix.to_dict()
            
            # 강한 상관관계 찾기
            for i in range(len(numeric_columns)):
                for j in range(i+1, len(numeric_columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    
                    if abs(corr_value) > 0.7:
                        result['strong_correlations'].append({
                            'variable1': numeric_columns[i],
                            'variable2': numeric_columns[j],
                            'correlation': float(corr_value)
                        })
                    elif abs(corr_value) < 0.1:
                        result['weak_correlations'].append({
                            'variable1': numeric_columns[i],
                            'variable2': numeric_columns[j],
                            'correlation': float(corr_value)
                        })
            
            # 인사이트 생성
            if result['strong_correlations']:
                result['insights'].append(f"{len(result['strong_correlations'])}개의 강한 상관관계가 발견되었습니다")
            
            if result['weak_correlations']:
                result['insights'].append(f"{len(result['weak_correlations'])}개의 약한 상관관계가 발견되었습니다")
            
            return result
            
        except Exception as e:
            logger.error(f"상관관계 분석 오류: {e}")
            raise
    
    def _perform_forecast_analysis(self, data: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """예측 분석"""
        try:
            result = {
                'forecast_values': [],
                'confidence_intervals': [],
                'accuracy_metrics': {},
                'next_periods': 7
            }
            
            if len(data) < 10:
                return result
            
            # 주요 메트릭 선택
            metric = request.metrics[0] if request.metrics else data.columns[-1]
            values = data[metric].values
            
            # 시계열 예측 (간단한 선형 회귀)
            X = np.arange(len(values)).reshape(-1, 1)
            y = values
            
            model = LinearRegression()
            model.fit(X, y)
            
            # 미래 예측
            future_X = np.arange(len(values), len(values) + result['next_periods']).reshape(-1, 1)
            future_predictions = model.predict(future_X)
            
            result['forecast_values'] = future_predictions.tolist()
            
            # 신뢰구간 계산 (간단한 방법)
            residuals = y - model.predict(X)
            std_residuals = np.std(residuals)
            
            confidence_intervals = []
            for pred in future_predictions:
                confidence_intervals.append({
                    'lower': float(pred - 1.96 * std_residuals),
                    'upper': float(pred + 1.96 * std_residuals)
                })
            
            result['confidence_intervals'] = confidence_intervals
            
            # 정확도 메트릭
            result['accuracy_metrics'] = {
                'r2_score': float(model.score(X, y)),
                'mean_absolute_error': float(np.mean(np.abs(residuals))),
                'root_mean_square_error': float(np.sqrt(np.mean(residuals**2)))
            }
            
            return result
            
        except Exception as e:
            logger.error(f"예측 분석 오류: {e}")
            raise
    
    def _perform_clustering_analysis(self, data: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """클러스터링 분석"""
        try:
            result = {
                'clusters': [],
                'cluster_centers': [],
                'cluster_sizes': [],
                'silhouette_score': 0.0
            }
            
            if len(data) < 3:
                return result
            
            # 수치형 컬럼만 선택
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            
            if len(numeric_columns) < 2:
                return result
            
            # 데이터 정규화
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(data[numeric_columns])
            
            # K-means 클러스터링
            n_clusters = min(5, len(data) // 2)  # 최대 5개 클러스터
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(scaled_data)
            
            # 결과 저장
            data_with_clusters = data.copy()
            data_with_clusters['cluster'] = cluster_labels
            
            for i in range(n_clusters):
                cluster_data = data_with_clusters[data_with_clusters['cluster'] == i]
                result['clusters'].append({
                    'cluster_id': i,
                    'size': len(cluster_data),
                    'data': cluster_data.drop('cluster', axis=1).to_dict('records')
                })
            
            result['cluster_centers'] = kmeans.cluster_centers_.tolist()
            result['cluster_sizes'] = [len(data_with_clusters[data_with_clusters['cluster'] == i]) for i in range(n_clusters)]
            
            return result
            
        except Exception as e:
            logger.error(f"클러스터링 분석 오류: {e}")
            raise
    
    def _perform_anomaly_analysis(self, data: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """이상치 분석"""
        try:
            result = {
                'anomalies': [],
                'anomaly_count': 0,
                'anomaly_percentage': 0.0,
                'threshold': 2.0
            }
            
            if len(data) < 3:
                return result
            
            # 주요 메트릭 선택
            metric = request.metrics[0] if request.metrics else data.columns[-1]
            values = data[metric].values
            
            # Z-score 기반 이상치 탐지
            z_scores = np.abs(stats.zscore(values))
            anomaly_indices = np.where(z_scores > result['threshold'])[0]
            
            result['anomaly_count'] = len(anomaly_indices)
            result['anomaly_percentage'] = (len(anomaly_indices) / len(values)) * 100
            
            for idx in anomaly_indices:
                result['anomalies'].append({
                    'index': int(idx),
                    'value': float(values[idx]),
                    'z_score': float(z_scores[idx]),
                    'timestamp': data.iloc[idx].get('time_id', str(idx))
                })
            
            return result
            
        except Exception as e:
            logger.error(f"이상치 분석 오류: {e}")
            raise
    
    def _perform_segmentation_analysis(self, data: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """세분화 분석"""
        try:
            result = {
                'segments': [],
                'segment_characteristics': {},
                'segment_sizes': {},
                'insights': []
            }
            
            if len(data) < 10:
                return result
            
            # 주요 메트릭 선택
            metrics = request.metrics[:2] if len(request.metrics) >= 2 else [data.columns[-1]]
            
            if len(metrics) < 2:
                return result
            
            # 2D 공간에서 세분화
            x_values = data[metrics[0]].values
            y_values = data[metrics[1]].values
            
            # 사분위수 기반 세분화
            x_quartiles = np.percentile(x_values, [25, 50, 75])
            y_quartiles = np.percentile(y_values, [25, 50, 75])
            
            segments = []
            for i, row in data.iterrows():
                x_val = row[metrics[0]]
                y_val = row[metrics[1]]
                
                # 세그먼트 결정
                if x_val <= x_quartiles[0]:
                    x_seg = 'low'
                elif x_val <= x_quartiles[1]:
                    x_seg = 'medium_low'
                elif x_val <= x_quartiles[2]:
                    x_seg = 'medium_high'
                else:
                    x_seg = 'high'
                
                if y_val <= y_quartiles[0]:
                    y_seg = 'low'
                elif y_val <= y_quartiles[1]:
                    y_seg = 'medium_low'
                elif y_val <= y_quartiles[2]:
                    y_seg = 'medium_high'
                else:
                    y_seg = 'high'
                
                segment = f"{x_seg}_{y_seg}"
                segments.append(segment)
            
            data_with_segments = data.copy()
            data_with_segments['segment'] = segments
            
            # 세그먼트별 특성 분석
            for segment in set(segments):
                segment_data = data_with_segments[data_with_segments['segment'] == segment]
                
                result['segments'].append({
                    'segment_id': segment,
                    'size': len(segment_data),
                    'data': segment_data.drop('segment', axis=1).to_dict('records')
                })
                
                result['segment_characteristics'][segment] = {
                    'size': len(segment_data),
                    'percentage': (len(segment_data) / len(data)) * 100,
                    'avg_values': {metric: float(segment_data[metric].mean()) for metric in metrics}
                }
            
            # 인사이트 생성
            largest_segment = max(result['segment_characteristics'].items(), key=lambda x: x[1]['size'])
            result['insights'].append(f"가장 큰 세그먼트: {largest_segment[0]} ({largest_segment[1]['percentage']:.1f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"세분화 분석 오류: {e}")
            raise
    
    def _create_chart(self, data: pd.DataFrame, request: AnalysisRequest, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """차트 생성"""
        try:
            chart_config = {
                'type': request.chart_type.value,
                'data': data.to_dict('records'),
                'layout': self._get_chart_layout(request),
                'config': {'displayModeBar': False}
            }
            
            # 차트 타입별 특별 처리
            if request.chart_type == ChartType.DASHBOARD:
                chart_config = self._create_dashboard_chart(data, request, analysis_result)
            
            return chart_config
            
        except Exception as e:
            logger.error(f"차트 생성 오류: {e}")
            raise
    
    def _get_chart_layout(self, request: AnalysisRequest) -> Dict[str, Any]:
        """차트 레이아웃 설정"""
        return {
            'title': f"{request.analysis_type.value.title()} Analysis",
            'xaxis': {'title': request.dimensions[0] if request.dimensions else 'Index'},
            'yaxis': {'title': request.metrics[0] if request.metrics else 'Value'},
            'height': 400,
            'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50}
        }
    
    def _create_dashboard_chart(self, data: pd.DataFrame, request: AnalysisRequest, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """대시보드 차트 생성"""
        try:
            # 여러 차트를 조합한 대시보드
            charts = []
            
            # 메인 차트
            main_chart = {
                'type': 'line',
                'data': data.to_dict('records'),
                'layout': self._get_chart_layout(request)
            }
            charts.append(main_chart)
            
            # 요약 통계
            if request.metrics:
                metric = request.metrics[0]
                summary_stats = {
                    'type': 'table',
                    'data': {
                        'headers': ['Metric', 'Value'],
                        'rows': [
                            ['Mean', f"{data[metric].mean():.2f}"],
                            ['Median', f"{data[metric].median():.2f}"],
                            ['Std Dev', f"{data[metric].std():.2f}"],
                            ['Min', f"{data[metric].min():.2f}"],
                            ['Max', f"{data[metric].max():.2f}"]
                        ]
                    }
                }
                charts.append(summary_stats)
            
            return {
                'type': 'dashboard',
                'charts': charts,
                'layout': {'grid': '2x2'}
            }
            
        except Exception as e:
            logger.error(f"대시보드 차트 생성 오류: {e}")
            raise
    
    def _generate_summary(self, analysis_result: Dict[str, Any], analysis_type: AnalysisType) -> str:
        """분석 요약 생성"""
        try:
            if analysis_type == AnalysisType.TREND:
                direction = analysis_result.get('trend_direction', 'stable')
                growth_rate = analysis_result.get('growth_rate', 0)
                return f"트렌드는 {direction}하며, 성장률은 {growth_rate:.1f}%입니다."
            
            elif analysis_type == AnalysisType.COMPARISON:
                top_count = len(analysis_result.get('top_performers', []))
                return f"상위 {top_count}개 항목이 전체 성과의 상당 부분을 차지합니다."
            
            elif analysis_type == AnalysisType.CORRELATION:
                strong_count = len(analysis_result.get('strong_correlations', []))
                return f"{strong_count}개의 강한 상관관계가 발견되었습니다."
            
            elif analysis_type == AnalysisType.FORECAST:
                r2_score = analysis_result.get('accuracy_metrics', {}).get('r2_score', 0)
                return f"예측 모델의 정확도는 {r2_score:.2f}입니다."
            
            elif analysis_type == AnalysisType.CLUSTERING:
                cluster_count = len(analysis_result.get('clusters', []))
                return f"{cluster_count}개의 클러스터로 데이터가 그룹화되었습니다."
            
            elif analysis_type == AnalysisType.ANOMALY:
                anomaly_count = analysis_result.get('anomaly_count', 0)
                return f"{anomaly_count}개의 이상치가 발견되었습니다."
            
            elif analysis_type == AnalysisType.SEGMENTATION:
                segment_count = len(analysis_result.get('segments', []))
                return f"{segment_count}개의 세그먼트로 고객이 분류되었습니다."
            
            return "분석이 완료되었습니다."
            
        except Exception as e:
            logger.error(f"요약 생성 오류: {e}")
            return "분석 요약을 생성할 수 없습니다."
    
    def _generate_cache_key(self, request: AnalysisRequest) -> str:
        """캐시 키 생성"""
        key_data = {
            'analysis_type': request.analysis_type.value,
            'data_source': request.data_source,
            'dimensions': request.dimensions,
            'metrics': request.metrics,
            'filters': request.filters,
            'time_range': request.time_range
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return f"bi_analysis:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def _cache_result(self, analysis_id: str, result: Dict[str, Any]):
        """결과 캐시"""
        try:
            cache_key = f"bi_result:{analysis_id}"
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(result)
            )
        except Exception as e:
            logger.error(f"결과 캐시 오류: {e}")
    
    def get_analysis_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """분석 결과 조회"""
        try:
            request = self.analysis_requests.get(analysis_id)
            if not request:
                return None
            
            if request.status == "completed":
                return request.result
            elif request.status == "failed":
                return {"error": request.error_message}
            else:
                return {"status": request.status}
                
        except Exception as e:
            logger.error(f"분석 결과 조회 오류: {e}")
            raise
    
    def create_report(self, template_id: str, parameters: Dict[str, Any] = None) -> str:
        """리포트 생성"""
        try:
            template = self.report_templates.get(template_id)
            if not template:
                raise ValueError(f"템플릿을 찾을 수 없습니다: {template_id}")
            
            report_id = str(uuid.uuid4())
            
            # 각 분석 실행
            analysis_results = []
            for analysis in template.analyses:
                analysis_id = self.create_analysis(
                    analysis_type=AnalysisType(analysis['type']),
                    data_source=analysis['data_source'],
                    dimensions=analysis['dimensions'],
                    metrics=analysis['metrics'],
                    chart_type=ChartType(analysis['chart_type'])
                )
                analysis_results.append({
                    'analysis_id': analysis_id,
                    'config': analysis
                })
            
            # 리포트 정보 저장
            report_data = {
                'id': report_id,
                'template_id': template_id,
                'analysis_results': analysis_results,
                'parameters': parameters or {},
                'created_at': datetime.now().isoformat(),
                'status': 'generating'
            }
            
            self.redis_client.setex(
                f"report:{report_id}",
                86400,  # 24시간
                json.dumps(report_data)
            )
            
            logger.info(f"리포트 생성 시작: {report_id}")
            return report_id
            
        except Exception as e:
            logger.error(f"리포트 생성 오류: {e}")
            raise
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """리포트 조회"""
        try:
            report_data = self.redis_client.get(f"report:{report_id}")
            if not report_data:
                return None
            
            report = json.loads(report_data)
            
            # 분석 결과 수집
            completed_analyses = []
            for analysis_result in report['analysis_results']:
                analysis_data = self.get_analysis_result(analysis_result['analysis_id'])
                if analysis_data and 'error' not in analysis_data:
                    completed_analyses.append({
                        'config': analysis_result['config'],
                        'result': analysis_data
                    })
            
            return {
                'id': report_id,
                'analyses': completed_analyses,
                'created_at': report['created_at'],
                'status': 'completed' if completed_analyses else 'generating'
            }
            
        except Exception as e:
            logger.error(f"리포트 조회 오류: {e}")
            raise
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """사용 가능한 템플릿 목록"""
        try:
            return [
                {
                    'id': template.id,
                    'name': template.name,
                    'description': template.description,
                    'analysis_count': len(template.analyses)
                }
                for template in self.report_templates.values()
            ]
        except Exception as e:
            logger.error(f"템플릿 목록 조회 오류: {e}")
            raise

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'your_program_warehouse',
            'user': 'postgres',
            'password': 'password'
        },
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 2
        }
    }
    
    # BI 엔진 생성
    bi_engine = BusinessIntelligenceEngine(config)
    
    # 분석 요청
    analysis_id = bi_engine.create_analysis(
        analysis_type=AnalysisType.TREND,
        data_source='agg_daily_sales',
        dimensions=['time_id'],
        metrics=['total_sales'],
        time_range={'start_date': '2025-01-01', 'end_date': '2025-01-31'},
        chart_type=ChartType.LINE
    )
    
    print(f"분석 요청 생성: {analysis_id}")
    
    # 사용 가능한 템플릿
    templates = bi_engine.get_available_templates()
    print(f"사용 가능한 템플릿: {templates}") 