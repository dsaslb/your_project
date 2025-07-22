import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional, Union
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    from sklearn.model_selection import train_test_split, cross_val_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from scipy import stats
    from scipy.signal import find_peaks
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

@dataclass
class PredictionResult:
    """예측 결과 클래스"""
    predictions: List[float]
    confidence_intervals: List[Tuple[float, float]]
    model_name: str
    accuracy_metrics: Dict[str, float]
    feature_importance: Dict[str, float] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class TrendAnalysis:
    """트렌드 분석 결과 클래스"""
    trend_direction: str
    trend_strength: float
    seasonality: Dict[str, Any]
    cycles: List[Dict[str, Any]]
    breakpoints: List[int]
    confidence_level: float
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class PredictiveAnalytics:
    """예측 분석 및 트렌드 분석 시스템"""
    
    def __init__(self, config: Dict = None):
        self.config = config or self._get_default_config()
        self.logger = self._setup_logger()
        
        # 모델 저장소
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        
        # 예측 결과 저장소
        self.prediction_history = {}
        self.accuracy_history = {}
        
        # 트렌드 분석 결과 저장소
        self.trend_analyses = {}
        
        # 모델 성능 추적
        self.model_performance = {}
        
    def _get_default_config(self) -> Dict:
        """기본 설정 반환"""
        return {
            "prediction": {
                "models": ["linear", "random_forest", "exponential_smoothing"],
                "forecast_horizon": 30,
                "confidence_level": 0.95,
                "min_data_points": 10,
                "cross_validation_folds": 5
            },
            "trend_analysis": {
                "min_trend_length": 5,
                "seasonality_detection": True,
                "breakpoint_detection": True,
                "trend_strength_threshold": 0.3
            },
            "evaluation": {
                "metrics": ["mse", "mae", "rmse", "r2", "mape"],
                "backtesting_periods": 5,
                "rolling_window": 30
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('predictive_analytics')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def prepare_time_series_data(self, data: List[Dict], 
                                date_column: str = "timestamp",
                                value_column: str = "value") -> pd.DataFrame:
        """시계열 데이터 준비"""
        df = pd.DataFrame(data)
        
        # 날짜 컬럼 변환
        df[date_column] = pd.to_datetime(df[date_column])
        
        # 시간순 정렬
        df = df.sort_values(date_column)
        
        # 결측값 처리
        df = df.dropna(subset=[value_column])
        
        # 인덱스 설정
        df = df.set_index(date_column)
        
        # 리샘플링 (일별 데이터로 통일)
        df = df.resample('D').mean().fillna(method='ffill')
        
        self.logger.info(f"시계열 데이터 준비 완료: {len(df)}개 포인트")
        
        return df
    
    def create_features(self, df: pd.DataFrame, 
                       target_column: str = "value") -> pd.DataFrame:
        """특성 생성"""
        df = df.copy()
        
        # 시간 특성
        df['year'] = df.index.year
        df['month'] = df.index.month
        df['day'] = df.index.day
        df['day_of_week'] = df.index.dayofweek
        df['quarter'] = df.index.quarter
        
        # 지연 특성 (lag features)
        for lag in [1, 2, 3, 7, 14, 30]:
            df[f'lag_{lag}'] = df[target_column].shift(lag)
        
        # 이동평균 특성
        for window in [3, 7, 14, 30]:
            df[f'ma_{window}'] = df[target_column].rolling(window=window).mean()
            df[f'std_{window}'] = df[target_column].rolling(window=window).std()
        
        # 추세 특성
        df['trend'] = np.arange(len(df))
        
        # 계절성 특성
        df['sin_month'] = np.sin(2 * np.pi * df['month'] / 12)
        df['cos_month'] = np.cos(2 * np.pi * df['month'] / 12)
        df['sin_day_of_week'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['cos_day_of_week'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # 결측값 처리
        df = df.dropna()
        
        return df
    
    def train_prediction_model(self, df: pd.DataFrame, 
                             target_column: str = "value",
                             model_name: str = "random_forest") -> Dict:
        """예측 모델 훈련"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn이 필요합니다.")
        
        # 특성 생성
        feature_df = self.create_features(df, target_column)
        
        # 특성과 타겟 분리
        feature_columns = [col for col in feature_df.columns if col != target_column]
        X = feature_df[feature_columns]
        y = feature_df[target_column]
        
        # 데이터 분할
        train_size = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
        y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
        
        # 스케일링
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # 모델 선택 및 훈련
        if model_name == "linear":
            model = LinearRegression()
        elif model_name == "random_forest":
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        else:
            raise ValueError(f"지원하지 않는 모델: {model_name}")
        
        # 모델 훈련
        model.fit(X_train_scaled, y_train)
        
        # 예측
        y_pred_train = model.predict(X_train_scaled)
        y_pred_test = model.predict(X_test_scaled)
        
        # 성능 평가
        train_metrics = self._calculate_metrics(y_train, y_pred_train)
        test_metrics = self._calculate_metrics(y_test, y_pred_test)
        
        # 교차 검증
        cv_scores = cross_val_score(model, X_train_scaled, y_train, 
                                  cv=self.config["prediction"]["cross_validation_folds"])
        
        # 특성 중요도
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(feature_columns, model.feature_importances_))
        elif hasattr(model, 'coef_'):
            feature_importance = dict(zip(feature_columns, np.abs(model.coef_)))
        
        # 모델 저장
        self.models[model_name] = model
        self.scalers[model_name] = scaler
        self.feature_importance[model_name] = feature_importance
        
        # 성능 기록
        self.model_performance[model_name] = {
            "train_metrics": train_metrics,
            "test_metrics": test_metrics,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
            "trained_at": datetime.now().isoformat()
        }
        
        result = {
            "model_name": model_name,
            "train_metrics": train_metrics,
            "test_metrics": test_metrics,
            "cv_scores": {
                "mean": cv_scores.mean(),
                "std": cv_scores.std(),
                "scores": cv_scores.tolist()
            },
            "feature_importance": feature_importance,
            "training_samples": len(X_train),
            "test_samples": len(X_test)
        }
        
        self.logger.info(f"모델 훈련 완료: {model_name} (R² = {test_metrics['r2']:.3f})")
        
        return result
    
    def _calculate_metrics(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
        """성능 지표 계산"""
        metrics = {}
        
        metrics['mse'] = mean_squared_error(y_true, y_pred)
        metrics['mae'] = mean_absolute_error(y_true, y_pred)
        metrics['rmse'] = np.sqrt(metrics['mse'])
        metrics['r2'] = r2_score(y_true, y_pred)
        
        # MAPE 계산
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        metrics['mape'] = mape
        
        return metrics
    
    def make_prediction(self, df: pd.DataFrame, 
                       periods: int = None,
                       model_name: str = "random_forest",
                       target_column: str = "value") -> PredictionResult:
        """예측 수행"""
        if model_name not in self.models:
            raise ValueError(f"훈련되지 않은 모델: {model_name}")
        
        periods = periods or self.config["prediction"]["forecast_horizon"]
        
        # 특성 생성
        feature_df = self.create_features(df, target_column)
        
        # 특성 컬럼
        feature_columns = [col for col in feature_df.columns if col != target_column]
        X = feature_df[feature_columns]
        
        # 스케일링
        scaler = self.scalers[model_name]
        X_scaled = scaler.transform(X)
        
        # 예측
        model = self.models[model_name]
        predictions = model.predict(X_scaled)
        
        # 신뢰구간 계산 (간단한 방법)
        confidence_level = self.config["prediction"]["confidence_level"]
        std_dev = np.std(predictions)
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        margin_of_error = z_score * std_dev
        
        confidence_intervals = [
            (pred - margin_of_error, pred + margin_of_error)
            for pred in predictions
        ]
        
        # 예측 결과 생성
        result = PredictionResult(
            predictions=predictions.tolist(),
            confidence_intervals=confidence_intervals,
            model_name=model_name,
            accuracy_metrics=self.model_performance[model_name]["test_metrics"],
            feature_importance=self.feature_importance[model_name]
        )
        
        # 예측 결과 저장
        prediction_id = f"pred_{int(datetime.now().timestamp())}"
        self.prediction_history[prediction_id] = result
        
        self.logger.info(f"예측 완료: {model_name} ({periods}개 기간)")
        
        return result
    
    def analyze_trends(self, df: pd.DataFrame, 
                      target_column: str = "value") -> TrendAnalysis:
        """트렌드 분석"""
        if len(df) < self.config["trend_analysis"]["min_trend_length"]:
            raise ValueError("트렌드 분석을 위한 데이터가 부족합니다.")
        
        values = df[target_column].values
        dates = df.index
        
        # 1. 트렌드 방향 및 강도 분석
        trend_direction, trend_strength = self._analyze_trend_direction(values)
        
        # 2. 계절성 분석
        seasonality = {}
        if self.config["trend_analysis"]["seasonality_detection"]:
            seasonality = self._analyze_seasonality(df, target_column)
        
        # 3. 순환 패턴 분석
        cycles = self._analyze_cycles(values)
        
        # 4. 구조 변화점 탐지
        breakpoints = []
        if self.config["trend_analysis"]["breakpoint_detection"]:
            breakpoints = self._detect_breakpoints(values)
        
        # 5. 신뢰도 계산
        confidence_level = self._calculate_trend_confidence(values, trend_strength)
        
        # 트렌드 분석 결과 생성
        result = TrendAnalysis(
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            seasonality=seasonality,
            cycles=cycles,
            breakpoints=breakpoints,
            confidence_level=confidence_level
        )
        
        # 결과 저장
        trend_id = f"trend_{int(datetime.now().timestamp())}"
        self.trend_analyses[trend_id] = result
        
        self.logger.info(f"트렌드 분석 완료: {trend_direction} (강도: {trend_strength:.3f})")
        
        return result
    
    def _analyze_trend_direction(self, values: np.ndarray) -> Tuple[str, float]:
        """트렌드 방향 및 강도 분석"""
        x = np.arange(len(values))
        
        # 선형 회귀로 트렌드 계산
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        # 트렌드 방향
        if slope > 0.01:
            direction = "increasing"
        elif slope < -0.01:
            direction = "decreasing"
        else:
            direction = "stable"
        
        # 트렌드 강도 (R² 값 사용)
        strength = r_value ** 2
        
        return direction, strength
    
    def _analyze_seasonality(self, df: pd.DataFrame, 
                           target_column: str) -> Dict[str, Any]:
        """계절성 분석"""
        seasonality = {}
        
        # 월별 계절성
        monthly_avg = df.groupby(df.index.month)[target_column].mean()
        seasonality["monthly"] = {
            "pattern": monthly_avg.to_dict(),
            "strength": monthly_avg.std() / monthly_avg.mean() if monthly_avg.mean() != 0 else 0
        }
        
        # 요일별 계절성
        daily_avg = df.groupby(df.index.dayofweek)[target_column].mean()
        seasonality["daily"] = {
            "pattern": daily_avg.to_dict(),
            "strength": daily_avg.std() / daily_avg.mean() if daily_avg.mean() != 0 else 0
        }
        
        # 분기별 계절성
        quarterly_avg = df.groupby(df.index.quarter)[target_column].mean()
        seasonality["quarterly"] = {
            "pattern": quarterly_avg.to_dict(),
            "strength": quarterly_avg.std() / quarterly_avg.mean() if quarterly_avg.mean() != 0 else 0
        }
        
        return seasonality
    
    def _analyze_cycles(self, values: np.ndarray) -> List[Dict[str, Any]]:
        """순환 패턴 분석"""
        cycles = []
        
        if not SCIPY_AVAILABLE:
            return cycles
        
        try:
            # FFT를 사용한 주파수 분석
            fft = np.fft.fft(values)
            freqs = np.fft.fftfreq(len(values))
            
            # 주요 주파수 찾기
            power = np.abs(fft) ** 2
            significant_freqs = freqs[power > np.mean(power) + 2 * np.std(power)]
            
            for freq in significant_freqs:
                if freq > 0:  # 양의 주파수만
                    period = 1 / freq if freq != 0 else 0
                    if 2 <= period <= len(values) // 2:
                        cycles.append({
                            "period": period,
                            "frequency": freq,
                            "strength": power[np.where(freqs == freq)[0][0]]
                        })
            
            # 강도순 정렬
            cycles.sort(key=lambda x: x["strength"], reverse=True)
            
        except Exception as e:
            self.logger.warning(f"순환 패턴 분석 실패: {e}")
        
        return cycles[:5]  # 상위 5개만 반환
    
    def _detect_breakpoints(self, values: np.ndarray) -> List[int]:
        """구조 변화점 탐지"""
        breakpoints = []
        
        if len(values) < 10:
            return breakpoints
        
        try:
            # CUSUM 테스트를 사용한 변화점 탐지
            mean_val = np.mean(values)
            cusum = np.cumsum(values - mean_val)
            
            # 임계값 설정
            threshold = 2 * np.std(values)
            
            # 임계값을 넘는 지점 찾기
            for i in range(1, len(cusum)):
                if abs(cusum[i]) > threshold:
                    breakpoints.append(i)
            
            # 연속된 변화점 제거
            if breakpoints:
                filtered_breakpoints = [breakpoints[0]]
                for bp in breakpoints[1:]:
                    if bp - filtered_breakpoints[-1] > 5:  # 최소 5개 포인트 간격
                        filtered_breakpoints.append(bp)
                breakpoints = filtered_breakpoints
            
        except Exception as e:
            self.logger.warning(f"구조 변화점 탐지 실패: {e}")
        
        return breakpoints
    
    def _calculate_trend_confidence(self, values: np.ndarray, 
                                  trend_strength: float) -> float:
        """트렌드 신뢰도 계산"""
        # 데이터 길이와 변동성 기반 신뢰도 계산
        length_factor = min(len(values) / 100, 1.0)  # 최대 1.0
        variability_factor = 1.0 - (np.std(values) / np.mean(values)) if np.mean(values) != 0 else 0
        variability_factor = max(0, min(1, variability_factor))
        
        confidence = (trend_strength * 0.5 + 
                     length_factor * 0.3 + 
                     variability_factor * 0.2)
        
        return min(confidence, 1.0)
    
    def evaluate_predictions(self, actual_values: List[float], 
                           predicted_values: List[float]) -> Dict[str, float]:
        """예측 정확도 평가"""
        if len(actual_values) != len(predicted_values):
            raise ValueError("실제값과 예측값의 길이가 다릅니다.")
        
        metrics = self._calculate_metrics(
            pd.Series(actual_values), 
            np.array(predicted_values)
        )
        
        # 추가 지표
        metrics['bias'] = np.mean(np.array(predicted_values) - np.array(actual_values))
        metrics['correlation'] = np.corrcoef(actual_values, predicted_values)[0, 1]
        
        return metrics
    
    def backtest_model(self, df: pd.DataFrame, 
                      target_column: str = "value",
                      model_name: str = "random_forest",
                      periods: int = None) -> Dict:
        """모델 백테스팅"""
        periods = periods or self.config["evaluation"]["backtesting_periods"]
        
        if len(df) < periods * 2:
            raise ValueError("백테스팅을 위한 데이터가 부족합니다.")
        
        backtest_results = []
        
        for i in range(periods):
            # 훈련 데이터
            train_data = df.iloc[:-periods+i]
            test_data = df.iloc[-periods+i:-periods+i+1]
            
            if len(train_data) < 10:
                continue
            
            # 모델 훈련
            try:
                train_result = self.train_prediction_model(
                    train_data, target_column, model_name
                )
                
                # 예측
                prediction = self.make_prediction(
                    test_data, 1, model_name, target_column
                )
                
                # 실제값과 비교
                actual_value = test_data[target_column].iloc[0]
                predicted_value = prediction.predictions[0]
                
                backtest_results.append({
                    "period": i,
                    "actual": actual_value,
                    "predicted": predicted_value,
                    "error": abs(actual_value - predicted_value),
                    "error_percent": abs(actual_value - predicted_value) / actual_value * 100
                })
                
            except Exception as e:
                self.logger.warning(f"백테스팅 기간 {i} 실패: {e}")
        
        if not backtest_results:
            return {"error": "백테스팅 결과가 없습니다."}
        
        # 백테스팅 요약
        errors = [result["error"] for result in backtest_results]
        error_percents = [result["error_percent"] for result in backtest_results]
        
        summary = {
            "total_periods": len(backtest_results),
            "mean_error": np.mean(errors),
            "mean_error_percent": np.mean(error_percents),
            "max_error": np.max(errors),
            "min_error": np.min(errors),
            "std_error": np.std(errors),
            "results": backtest_results
        }
        
        return summary
    
    def get_model_performance_summary(self) -> Dict:
        """모델 성능 요약"""
        summary = {}
        
        for model_name, performance in self.model_performance.items():
            summary[model_name] = {
                "test_r2": performance["test_metrics"]["r2"],
                "test_mape": performance["test_metrics"]["mape"],
                "cv_mean": performance["cv_mean"],
                "trained_at": performance["trained_at"]
            }
        
        return summary
    
    def generate_forecast_report(self, df: pd.DataFrame,
                               target_column: str = "value",
                               forecast_periods: int = 30) -> Dict:
        """예측 리포트 생성"""
        # 트렌드 분석
        trend_analysis = self.analyze_trends(df, target_column)
        
        # 예측 수행
        prediction = self.make_prediction(df, forecast_periods, "random_forest", target_column)
        
        # 백테스팅
        backtest = self.backtest_model(df, target_column, "random_forest")
        
        # 모델 성능 요약
        performance_summary = self.get_model_performance_summary()
        
        report = {
            "report_type": "forecast",
            "generated_at": datetime.now().isoformat(),
            "data_summary": {
                "total_points": len(df),
                "date_range": {
                    "start": df.index[0].isoformat(),
                    "end": df.index[-1].isoformat()
                },
                "mean_value": float(df[target_column].mean()),
                "std_value": float(df[target_column].std())
            },
            "trend_analysis": asdict(trend_analysis),
            "prediction": {
                "forecast_periods": forecast_periods,
                "predictions": prediction.predictions,
                "confidence_intervals": prediction.confidence_intervals,
                "model_name": prediction.model_name,
                "accuracy_metrics": prediction.accuracy_metrics
            },
            "backtest_results": backtest,
            "model_performance": performance_summary,
            "recommendations": self._generate_recommendations(trend_analysis, prediction, backtest)
        }
        
        return report
    
    def _generate_recommendations(self, trend_analysis: TrendAnalysis,
                                prediction: PredictionResult,
                                backtest: Dict) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        # 트렌드 기반 권장사항
        if trend_analysis.trend_strength > 0.7:
            if trend_analysis.trend_direction == "increasing":
                recommendations.append("강한 상승 트렌드가 관찰됩니다. 성장 전략을 고려하세요.")
            elif trend_analysis.trend_direction == "decreasing":
                recommendations.append("강한 하락 트렌드가 관찰됩니다. 위험 관리에 집중하세요.")
        
        # 예측 정확도 기반 권장사항
        if prediction.accuracy_metrics["r2"] < 0.5:
            recommendations.append("예측 모델의 정확도가 낮습니다. 추가 특성이나 다른 모델을 고려하세요.")
        
        # 백테스팅 결과 기반 권장사항
        if "mean_error_percent" in backtest:
            if backtest["mean_error_percent"] > 20:
                recommendations.append("예측 오차가 높습니다. 모델을 재훈련하거나 데이터 품질을 확인하세요.")
        
        # 계절성 기반 권장사항
        if trend_analysis.seasonality:
            recommendations.append("계절성 패턴이 발견되었습니다. 계절성을 고려한 계획을 수립하세요.")
        
        return recommendations

# 사용 예시
if __name__ == "__main__":
    # 예측 분석 시스템 초기화
    analytics = PredictiveAnalytics()
    
    # 샘플 데이터 생성
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    values = 100 + np.cumsum(np.random.randn(100) * 0.5) + 10 * np.sin(2 * np.pi * np.arange(100) / 30)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'value': values
    }).set_index('timestamp')
    
    # 모델 훈련
    train_result = analytics.train_prediction_model(df, "value", "random_forest")
    print(f"모델 훈련 결과: {train_result}")
    
    # 예측 수행
    prediction = analytics.make_prediction(df, 30, "random_forest", "value")
    print(f"예측 결과: {len(prediction.predictions)}개 기간")
    
    # 트렌드 분석
    trend_analysis = analytics.analyze_trends(df, "value")
    print(f"트렌드 분석: {trend_analysis.trend_direction} (강도: {trend_analysis.trend_strength:.3f})")
    
    # 백테스팅
    backtest = analytics.backtest_model(df, "value", "random_forest")
    print(f"백테스팅 결과: 평균 오차 {backtest['mean_error_percent']:.2f}%")
    
    # 예측 리포트 생성
    report = analytics.generate_forecast_report(df, "value", 30)
    print(f"예측 리포트 생성 완료: {len(report['recommendations'])}개 권장사항") 