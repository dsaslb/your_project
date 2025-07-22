import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

@dataclass
class KPIMetric:
    """KPI 메트릭 클래스"""
    name: str
    value: float
    target: float = None
    unit: str = ""
    trend: str = "neutral"  # up, down, neutral
    change_percent: float = 0.0
    status: str = "normal"  # normal, warning, critical
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

@dataclass
class DashboardConfig:
    """대시보드 설정 클래스"""
    refresh_interval: int = 60  # 초
    max_data_points: int = 1000
    enable_real_time: bool = True
    enable_predictions: bool = True
    enable_alerts: bool = True
    chart_types: List[str] = None
    kpi_thresholds: Dict = None
    
    def __post_init__(self):
        if self.chart_types is None:
            self.chart_types = ["line", "bar", "pie", "scatter", "heatmap"]
        if self.kpi_thresholds is None:
            self.kpi_thresholds = {
                "warning": 0.8,
                "critical": 0.6
            }

class BusinessIntelligence:
    """고급 비즈니스 인텔리전스 시스템"""
    
    def __init__(self, config: DashboardConfig = None):
        self.config = config or DashboardConfig()
        self.logger = self._setup_logger()
        
        # 데이터 저장소
        self.kpi_data = {}
        self.trend_data = {}
        self.prediction_data = {}
        self.alert_data = []
        
        # 대시보드 상태
        self.is_running = False
        self.last_refresh = datetime.now()
        
        # 분석 모듈들
        self.analyzers = {}
        self.predictors = {}
        self.alerters = {}
        
        # 차트 템플릿
        self.chart_templates = {}
        
        self._setup_default_analyzers()
        self._setup_default_predictors()
        self._setup_default_alerters()
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('business_intelligence')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_default_analyzers(self):
        """기본 분석기 설정"""
        self.analyzers = {
            "trend": self._analyze_trend,
            "seasonal": self._analyze_seasonal,
            "correlation": self._analyze_correlation,
            "distribution": self._analyze_distribution,
            "anomaly": self._analyze_anomaly
        }
    
    def _setup_default_predictors(self):
        """기본 예측기 설정"""
        self.predictors = {
            "linear": self._predict_linear,
            "exponential": self._predict_exponential,
            "seasonal": self._predict_seasonal,
            "moving_average": self._predict_moving_average
        }
    
    def _setup_default_alerters(self):
        """기본 알림기 설정"""
        self.alerters = {
            "threshold": self._alert_threshold,
            "trend": self._alert_trend,
            "anomaly": self._alert_anomaly
        }
    
    def add_kpi(self, name: str, value: float, target: float = None, 
                unit: str = "", category: str = "general"):
        """KPI 추가"""
        if category not in self.kpi_data:
            self.kpi_data[category] = {}
        
        # 이전 값과 비교하여 트렌드 계산
        trend = "neutral"
        change_percent = 0.0
        
        if name in self.kpi_data[category]:
            prev_value = self.kpi_data[category][name].value
            if prev_value != 0:
                change_percent = ((value - prev_value) / prev_value) * 100
                trend = "up" if change_percent > 0 else "down" if change_percent < 0 else "neutral"
        
        # 상태 결정
        status = "normal"
        if target is not None:
            achievement_rate = value / target if target != 0 else 0
            if achievement_rate < self.config.kpi_thresholds["critical"]:
                status = "critical"
            elif achievement_rate < self.config.kpi_thresholds["warning"]:
                status = "warning"
        
        kpi = KPIMetric(
            name=name,
            value=value,
            target=target,
            unit=unit,
            trend=trend,
            change_percent=change_percent,
            status=status
        )
        
        self.kpi_data[category][name] = kpi
        
        self.logger.info(f"KPI 추가: {category}/{name} = {value}{unit}")
    
    def get_kpi_dashboard(self, category: str = None) -> Dict:
        """KPI 대시보드 데이터 조회"""
        if category:
            kpis = self.kpi_data.get(category, {})
        else:
            kpis = {}
            for cat_data in self.kpi_data.values():
                kpis.update(cat_data)
        
        # KPI 요약 통계
        total_kpis = len(kpis)
        normal_count = sum(1 for kpi in kpis.values() if kpi.status == "normal")
        warning_count = sum(1 for kpi in kpis.values() if kpi.status == "warning")
        critical_count = sum(1 for kpi in kpis.values() if kpi.status == "critical")
        
        # 평균 성과율
        achievement_rates = []
        for kpi in kpis.values():
            if kpi.target is not None and kpi.target != 0:
                achievement_rates.append(kpi.value / kpi.target)
        
        avg_achievement = np.mean(achievement_rates) if achievement_rates else 0
        
        return {
            "kpis": {name: asdict(kpi) for name, kpi in kpis.items()},
            "summary": {
                "total_kpis": total_kpis,
                "normal_count": normal_count,
                "warning_count": warning_count,
                "critical_count": critical_count,
                "avg_achievement": avg_achievement,
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def add_trend_data(self, metric_name: str, data: List[Dict]):
        """트렌드 데이터 추가"""
        df = pd.DataFrame(data)
        
        if metric_name not in self.trend_data:
            self.trend_data[metric_name] = []
        
        self.trend_data[metric_name].extend(data)
        
        # 최대 데이터 포인트 제한
        if len(self.trend_data[metric_name]) > self.config.max_data_points:
            self.trend_data[metric_name] = self.trend_data[metric_name][-self.config.max_data_points:]
        
        self.logger.info(f"트렌드 데이터 추가: {metric_name} ({len(data)}개 포인트)")
    
    def analyze_trend(self, metric_name: str, analysis_type: str = "trend") -> Dict:
        """트렌드 분석"""
        if metric_name not in self.trend_data:
            return {"error": "데이터가 없습니다."}
        
        data = self.trend_data[metric_name]
        df = pd.DataFrame(data)
        
        if analysis_type in self.analyzers:
            result = self.analyzers[analysis_type](df, metric_name)
        else:
            result = {"error": f"지원하지 않는 분석 타입: {analysis_type}"}
        
        return result
    
    def _analyze_trend(self, df: pd.DataFrame, metric_name: str) -> Dict:
        """트렌드 분석"""
        if 'value' not in df.columns or 'timestamp' not in df.columns:
            return {"error": "필수 컬럼이 없습니다."}
        
        # 시간순 정렬
        df = df.sort_values('timestamp')
        
        # 선형 회귀로 트렌드 계산
        x = np.arange(len(df))
        y = df['value'].values
        
        if len(x) < 2:
            return {"error": "데이터 포인트가 부족합니다."}
        
        slope, intercept = np.polyfit(x, y, 1)
        
        # 트렌드 방향
        if slope > 0.01:
            trend_direction = "increasing"
        elif slope < -0.01:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        
        # 변화율 계산
        if len(y) > 1:
            change_rate = ((y[-1] - y[0]) / y[0]) * 100 if y[0] != 0 else 0
        else:
            change_rate = 0
        
        return {
            "trend_direction": trend_direction,
            "slope": slope,
            "change_rate": change_rate,
            "data_points": len(df),
            "current_value": y[-1] if len(y) > 0 else None,
            "start_value": y[0] if len(y) > 0 else None
        }
    
    def _analyze_seasonal(self, df: pd.DataFrame, metric_name: str) -> Dict:
        """계절성 분석"""
        if 'value' not in df.columns or 'timestamp' not in df.columns:
            return {"error": "필수 컬럼이 없습니다."}
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        
        # 시간대별 평균
        hourly_avg = df.groupby('hour')['value'].mean().to_dict()
        
        # 요일별 평균
        daily_avg = df.groupby('day_of_week')['value'].mean().to_dict()
        
        # 월별 평균
        monthly_avg = df.groupby('month')['value'].mean().to_dict()
        
        return {
            "hourly_pattern": hourly_avg,
            "daily_pattern": daily_avg,
            "monthly_pattern": monthly_avg,
            "has_seasonality": len(set(hourly_avg.values())) > 1
        }
    
    def _analyze_correlation(self, df: pd.DataFrame, metric_name: str) -> Dict:
        """상관관계 분석"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) < 2:
            return {"error": "상관관계 분석을 위한 숫자 컬럼이 부족합니다."}
        
        correlation_matrix = df[numeric_columns].corr()
        
        # 강한 상관관계 찾기
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        "variable1": correlation_matrix.columns[i],
                        "variable2": correlation_matrix.columns[j],
                        "correlation": corr_value
                    })
        
        return {
            "correlation_matrix": correlation_matrix.to_dict(),
            "strong_correlations": strong_correlations
        }
    
    def _analyze_distribution(self, df: pd.DataFrame, metric_name: str) -> Dict:
        """분포 분석"""
        if 'value' not in df.columns:
            return {"error": "value 컬럼이 없습니다."}
        
        values = df['value'].dropna()
        
        if len(values) == 0:
            return {"error": "분석할 데이터가 없습니다."}
        
        return {
            "mean": float(values.mean()),
            "median": float(values.median()),
            "std": float(values.std()),
            "min": float(values.min()),
            "max": float(values.max()),
            "quartiles": {
                "q1": float(values.quantile(0.25)),
                "q2": float(values.quantile(0.5)),
                "q3": float(values.quantile(0.75))
            },
            "skewness": float(values.skew()),
            "kurtosis": float(values.kurtosis())
        }
    
    def _analyze_anomaly(self, df: pd.DataFrame, metric_name: str) -> Dict:
        """이상치 분석"""
        if 'value' not in df.columns:
            return {"error": "value 컬럼이 없습니다."}
        
        values = df['value'].dropna()
        
        if len(values) < 3:
            return {"error": "이상치 분석을 위한 데이터가 부족합니다."}
        
        # IQR 방법으로 이상치 탐지
        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = values[(values < lower_bound) | (values > upper_bound)]
        
        return {
            "outlier_count": len(outliers),
            "outlier_percentage": (len(outliers) / len(values)) * 100,
            "outlier_values": outliers.tolist(),
            "bounds": {
                "lower": float(lower_bound),
                "upper": float(upper_bound)
            }
        }
    
    def predict_metric(self, metric_name: str, periods: int = 30, 
                      method: str = "linear") -> Dict:
        """메트릭 예측"""
        if metric_name not in self.trend_data:
            return {"error": "예측할 데이터가 없습니다."}
        
        data = self.trend_data[metric_name]
        df = pd.DataFrame(data)
        
        if method in self.predictors:
            result = self.predictors[method](df, periods)
        else:
            result = {"error": f"지원하지 않는 예측 방법: {method}"}
        
        # 예측 결과 저장
        self.prediction_data[metric_name] = {
            "method": method,
            "periods": periods,
            "prediction": result,
            "created_at": datetime.now().isoformat()
        }
        
        return result
    
    def _predict_linear(self, df: pd.DataFrame, periods: int) -> Dict:
        """선형 예측"""
        if 'value' not in df.columns:
            return {"error": "value 컬럼이 없습니다."}
        
        values = df['value'].dropna()
        
        if len(values) < 2:
            return {"error": "예측을 위한 데이터가 부족합니다."}
        
        x = np.arange(len(values))
        y = values.values
        
        # 선형 회귀
        slope, intercept = np.polyfit(x, y, 1)
        
        # 예측
        future_x = np.arange(len(values), len(values) + periods)
        predictions = slope * future_x + intercept
        
        return {
            "predictions": predictions.tolist(),
            "slope": slope,
            "intercept": intercept,
            "confidence": 0.8  # 간단한 신뢰도
        }
    
    def _predict_exponential(self, df: pd.DataFrame, periods: int) -> Dict:
        """지수 예측"""
        if 'value' not in df.columns:
            return {"error": "value 컬럼이 없습니다."}
        
        values = df['value'].dropna()
        
        if len(values) < 2:
            return {"error": "예측을 위한 데이터가 부족합니다."}
        
        # 지수 평활
        alpha = 0.3
        predictions = []
        last_value = values.iloc[-1]
        
        for i in range(periods):
            next_value = last_value * (1 + alpha)
            predictions.append(next_value)
            last_value = next_value
        
        return {
            "predictions": predictions,
            "alpha": alpha,
            "confidence": 0.7
        }
    
    def _predict_seasonal(self, df: pd.DataFrame, periods: int) -> Dict:
        """계절성 예측"""
        if 'value' not in df.columns or 'timestamp' not in df.columns:
            return {"error": "필수 컬럼이 없습니다."}
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        
        # 시간대별 평균 계산
        hourly_avg = df.groupby('hour')['value'].mean()
        
        # 예측 (24시간 주기 반복)
        predictions = []
        for i in range(periods):
            hour = (df['timestamp'].iloc[-1].hour + i + 1) % 24
            predictions.append(hourly_avg.get(hour, hourly_avg.mean()))
        
        return {
            "predictions": predictions,
            "seasonal_pattern": hourly_avg.to_dict(),
            "confidence": 0.6
        }
    
    def _predict_moving_average(self, df: pd.DataFrame, periods: int) -> Dict:
        """이동평균 예측"""
        if 'value' not in df.columns:
            return {"error": "value 컬럼이 없습니다."}
        
        values = df['value'].dropna()
        
        if len(values) < 5:
            return {"error": "이동평균을 위한 데이터가 부족합니다."}
        
        # 이동평균 계산
        window = min(5, len(values) // 2)
        ma = values.rolling(window=window).mean().iloc[-1]
        
        # 단순한 예측 (마지막 이동평균값 사용)
        predictions = [ma] * periods
        
        return {
            "predictions": predictions,
            "window_size": window,
            "confidence": 0.5
        }
    
    def create_chart(self, chart_type: str, data: Dict, config: Dict = None) -> Dict:
        """차트 생성"""
        if not PLOTLY_AVAILABLE:
            return {"error": "Plotly를 사용할 수 없습니다."}
        
        if config is None:
            config = {}
        
        try:
            if chart_type == "line":
                chart = self._create_line_chart(data, config)
            elif chart_type == "bar":
                chart = self._create_bar_chart(data, config)
            elif chart_type == "pie":
                chart = self._create_pie_chart(data, config)
            elif chart_type == "scatter":
                chart = self._create_scatter_chart(data, config)
            elif chart_type == "heatmap":
                chart = self._create_heatmap_chart(data, config)
            else:
                return {"error": f"지원하지 않는 차트 타입: {chart_type}"}
            
            return {
                "chart_type": chart_type,
                "chart_data": chart,
                "config": config
            }
            
        except Exception as e:
            return {"error": f"차트 생성 실패: {str(e)}"}
    
    def _create_line_chart(self, data: Dict, config: Dict) -> Dict:
        """선 차트 생성"""
        x = data.get('x', [])
        y = data.get('y', [])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines+markers',
            name=config.get('name', 'Data'),
            line=dict(color=config.get('color', 'blue'))
        ))
        
        fig.update_layout(
            title=config.get('title', 'Line Chart'),
            xaxis_title=config.get('xaxis_title', 'X'),
            yaxis_title=config.get('yaxis_title', 'Y')
        )
        
        return json.loads(fig.to_json())
    
    def _create_bar_chart(self, data: Dict, config: Dict) -> Dict:
        """막대 차트 생성"""
        x = data.get('x', [])
        y = data.get('y', [])
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=x,
            y=y,
            name=config.get('name', 'Data'),
            marker_color=config.get('color', 'blue')
        ))
        
        fig.update_layout(
            title=config.get('title', 'Bar Chart'),
            xaxis_title=config.get('xaxis_title', 'X'),
            yaxis_title=config.get('yaxis_title', 'Y')
        )
        
        return json.loads(fig.to_json())
    
    def _create_pie_chart(self, data: Dict, config: Dict) -> Dict:
        """파이 차트 생성"""
        labels = data.get('labels', [])
        values = data.get('values', [])
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=config.get('hole', 0)
        )])
        
        fig.update_layout(
            title=config.get('title', 'Pie Chart')
        )
        
        return json.loads(fig.to_json())
    
    def _create_scatter_chart(self, data: Dict, config: Dict) -> Dict:
        """산점도 차트 생성"""
        x = data.get('x', [])
        y = data.get('y', [])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='markers',
            name=config.get('name', 'Data'),
            marker=dict(
                size=config.get('marker_size', 8),
                color=config.get('color', 'blue')
            )
        ))
        
        fig.update_layout(
            title=config.get('title', 'Scatter Chart'),
            xaxis_title=config.get('xaxis_title', 'X'),
            yaxis_title=config.get('yaxis_title', 'Y')
        )
        
        return json.loads(fig.to_json())
    
    def _create_heatmap_chart(self, data: Dict, config: Dict) -> Dict:
        """히트맵 차트 생성"""
        z = data.get('z', [])
        x = data.get('x', [])
        y = data.get('y', [])
        
        fig = go.Figure(data=go.Heatmap(
            z=z,
            x=x,
            y=y,
            colorscale=config.get('colorscale', 'Viridis')
        ))
        
        fig.update_layout(
            title=config.get('title', 'Heatmap Chart'),
            xaxis_title=config.get('xaxis_title', 'X'),
            yaxis_title=config.get('yaxis_title', 'Y')
        )
        
        return json.loads(fig.to_json())
    
    def add_alert(self, alert_type: str, metric_name: str, condition: str, 
                  threshold: float, message: str):
        """알림 추가"""
        alert = {
            "id": f"alert_{len(self.alert_data)}",
            "type": alert_type,
            "metric_name": metric_name,
            "condition": condition,
            "threshold": threshold,
            "message": message,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.alert_data.append(alert)
        self.logger.info(f"알림 추가: {alert_type} - {metric_name}")
    
    def check_alerts(self) -> List[Dict]:
        """알림 확인"""
        triggered_alerts = []
        
        for alert in self.alert_data:
            if alert["status"] != "active":
                continue
            
            metric_name = alert["metric_name"]
            if metric_name in self.kpi_data:
                # 모든 카테고리에서 메트릭 찾기
                current_value = None
                for category_data in self.kpi_data.values():
                    if metric_name in category_data:
                        current_value = category_data[metric_name].value
                        break
                
                if current_value is not None:
                    triggered = False
                    condition = alert["condition"]
                    threshold = alert["threshold"]
                    
                    if condition == "greater_than" and current_value > threshold:
                        triggered = True
                    elif condition == "less_than" and current_value < threshold:
                        triggered = True
                    elif condition == "equals" and current_value == threshold:
                        triggered = True
                    
                    if triggered:
                        alert_copy = alert.copy()
                        alert_copy["current_value"] = current_value
                        alert_copy["triggered_at"] = datetime.now().isoformat()
                        triggered_alerts.append(alert_copy)
        
        return triggered_alerts
    
    def _alert_threshold(self, metric_name: str, value: float, threshold: float) -> bool:
        """임계값 알림"""
        return value > threshold
    
    def _alert_trend(self, metric_name: str, trend_data: Dict) -> bool:
        """트렌드 알림"""
        if trend_data.get("trend_direction") == "decreasing":
            return True
        return False
    
    def _alert_anomaly(self, metric_name: str, anomaly_data: Dict) -> bool:
        """이상치 알림"""
        outlier_percentage = anomaly_data.get("outlier_percentage", 0)
        return outlier_percentage > 10  # 10% 이상이면 알림
    
    def get_dashboard_data(self) -> Dict:
        """대시보드 데이터 조회"""
        return {
            "kpi_dashboard": self.get_kpi_dashboard(),
            "trends": {
                metric: self.analyze_trend(metric, "trend")
                for metric in self.trend_data.keys()
            },
            "predictions": self.prediction_data,
            "alerts": self.check_alerts(),
            "last_updated": datetime.now().isoformat()
        }
    
    def export_report(self, report_type: str = "summary") -> Dict:
        """리포트 내보내기"""
        if report_type == "summary":
            return self._export_summary_report()
        elif report_type == "detailed":
            return self._export_detailed_report()
        elif report_type == "trend":
            return self._export_trend_report()
        else:
            return {"error": f"지원하지 않는 리포트 타입: {report_type}"}
    
    def _export_summary_report(self) -> Dict:
        """요약 리포트"""
        kpi_dashboard = self.get_kpi_dashboard()
        
        return {
            "report_type": "summary",
            "generated_at": datetime.now().isoformat(),
            "kpi_summary": kpi_dashboard["summary"],
            "top_kpis": list(kpi_dashboard["kpis"].keys())[:5],
            "alert_count": len(self.check_alerts()),
            "trend_count": len(self.trend_data),
            "prediction_count": len(self.prediction_data)
        }
    
    def _export_detailed_report(self) -> Dict:
        """상세 리포트"""
        return {
            "report_type": "detailed",
            "generated_at": datetime.now().isoformat(),
            "kpi_dashboard": self.get_kpi_dashboard(),
            "trend_analyses": {
                metric: self.analyze_trend(metric, "trend")
                for metric in self.trend_data.keys()
            },
            "predictions": self.prediction_data,
            "alerts": self.alert_data,
            "active_alerts": self.check_alerts()
        }
    
    def _export_trend_report(self) -> Dict:
        """트렌드 리포트"""
        trend_analyses = {}
        
        for metric in self.trend_data.keys():
            trend_analyses[metric] = {
                "trend": self.analyze_trend(metric, "trend"),
                "seasonal": self.analyze_trend(metric, "seasonal"),
                "distribution": self.analyze_trend(metric, "distribution"),
                "anomaly": self.analyze_trend(metric, "anomaly")
            }
        
        return {
            "report_type": "trend",
            "generated_at": datetime.now().isoformat(),
            "trend_analyses": trend_analyses,
            "predictions": self.prediction_data
        }

# 사용 예시
if __name__ == "__main__":
    # BI 시스템 초기화
    config = DashboardConfig(
        refresh_interval=30,
        enable_real_time=True,
        enable_predictions=True
    )
    
    bi = BusinessIntelligence(config)
    
    # KPI 추가
    bi.add_kpi("매출", 1000000, 1200000, "원", "sales")
    bi.add_kpi("고객 수", 500, 600, "명", "customers")
    bi.add_kpi("평균 주문액", 2000, 2500, "원", "sales")
    
    # 트렌드 데이터 추가
    trend_data = [
        {"timestamp": "2024-01-01", "value": 100},
        {"timestamp": "2024-01-02", "value": 110},
        {"timestamp": "2024-01-03", "value": 105},
        {"timestamp": "2024-01-04", "value": 120},
        {"timestamp": "2024-01-05", "value": 115}
    ]
    bi.add_trend_data("daily_sales", trend_data)
    
    # 트렌드 분석
    trend_analysis = bi.analyze_trend("daily_sales", "trend")
    print(f"트렌드 분석: {trend_analysis}")
    
    # 예측
    prediction = bi.predict_metric("daily_sales", periods=7, method="linear")
    print(f"예측 결과: {prediction}")
    
    # 알림 추가
    bi.add_alert("threshold", "매출", "less_than", 800000, "매출이 목표의 80% 미만입니다.")
    
    # 대시보드 데이터 조회
    dashboard_data = bi.get_dashboard_data()
    print(f"대시보드 데이터: {dashboard_data}")
    
    # 리포트 생성
    report = bi.export_report("summary")
    print(f"요약 리포트: {report}") 