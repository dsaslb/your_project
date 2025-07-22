import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVR, SVC
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.feature_selection import SelectKBest, f_regression, f_classif
import joblib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Union
import warnings
warnings.filterwarnings('ignore')

class AIPredictionEngine:
    """고급 AI 예측 및 분석 엔진"""
    
    def __init__(self, config_path: str = "ai_config.json"):
        self.config = self._load_config(config_path)
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.model_metadata = {}
        self.logger = self._setup_logger()
        
    def _load_config(self, config_path: str) -> Dict:
        """설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """기본 설정 반환"""
        return {
            "models": {
                "regression": ["linear", "random_forest", "gradient_boosting", "svr", "neural_network"],
                "classification": ["logistic", "random_forest", "gradient_boosting", "svc", "neural_network"]
            },
            "hyperparameters": {
                "random_forest": {
                    "n_estimators": [100, 200, 300],
                    "max_depth": [10, 20, None],
                    "min_samples_split": [2, 5, 10]
                },
                "gradient_boosting": {
                    "n_estimators": [100, 200],
                    "learning_rate": [0.01, 0.1, 0.2],
                    "max_depth": [3, 5, 7]
                },
                "neural_network": {
                    "hidden_layer_sizes": [(50,), (100,), (50, 25)],
                    "learning_rate_init": [0.001, 0.01],
                    "max_iter": [500, 1000]
                }
            },
            "feature_selection": {
                "method": "k_best",
                "k": 10
            },
            "scaling": "standard",
            "cross_validation": {
                "folds": 5,
                "scoring": "auto"
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('ai_prediction_engine')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def prepare_data(self, data: pd.DataFrame, target_column: str, 
                    task_type: str = "regression") -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """데이터 전처리 및 준비"""
        self.logger.info(f"데이터 준비 시작: {data.shape}, 타겟: {target_column}")
        
        # 결측값 처리
        data = data.dropna()
        
        # 특성과 타겟 분리
        X = data.drop(columns=[target_column])
        y = data[target_column]
        
        # 범주형 변수 처리
        categorical_columns = X.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            X = pd.get_dummies(X, columns=categorical_columns)
        
        # 특성 선택
        if self.config["feature_selection"]["method"] == "k_best":
            k = min(self.config["feature_selection"]["k"], X.shape[1])
            if task_type == "regression":
                selector = SelectKBest(score_func=f_regression, k=k)
            else:
                selector = SelectKBest(score_func=f_classif, k=k)
            
            X_selected = selector.fit_transform(X, y)
            selected_features = X.columns[selector.get_support()].tolist()
            self.feature_selectors[f"{task_type}_selector"] = selector
        else:
            X_selected = X.values
            selected_features = X.columns.tolist()
        
        # 스케일링
        if self.config["scaling"] == "standard":
            scaler = StandardScaler()
        else:
            scaler = MinMaxScaler()
        
        X_scaled = scaler.fit_transform(X_selected)
        self.scalers[f"{task_type}_scaler"] = scaler
        
        self.logger.info(f"데이터 준비 완료: {X_scaled.shape}, 선택된 특성: {len(selected_features)}")
        
        return X_scaled, y.values, selected_features
    
    def create_models(self, task_type: str = "regression") -> Dict[str, Any]:
        """모델 생성"""
        models = {}
        
        if task_type == "regression":
            models["linear"] = LinearRegression()
            models["random_forest"] = RandomForestRegressor(random_state=42)
            models["gradient_boosting"] = GradientBoostingRegressor(random_state=42)
            models["svr"] = SVR()
            models["neural_network"] = MLPRegressor(random_state=42, max_iter=1000)
        else:
            models["logistic"] = LogisticRegression(random_state=42)
            models["random_forest"] = RandomForestClassifier(random_state=42)
            models["gradient_boosting"] = GradientBoostingRegressor(random_state=42)
            models["svc"] = SVC(random_state=42)
            models["neural_network"] = MLPClassifier(random_state=42, max_iter=1000)
        
        return models
    
    def train_models(self, X: np.ndarray, y: np.ndarray, 
                    task_type: str = "regression") -> Dict[str, Dict]:
        """모델 훈련 및 평가"""
        self.logger.info(f"모델 훈련 시작: {task_type}")
        
        models = self.create_models(task_type)
        results = {}
        
        for name, model in models.items():
            self.logger.info(f"{name} 모델 훈련 중...")
            
            # 교차 검증
            cv_scores = cross_val_score(model, X, y, cv=self.config["cross_validation"]["folds"])
            
            # 전체 데이터로 훈련
            model.fit(X, y)
            
            # 예측
            y_pred = model.predict(X)
            
            # 평가
            if task_type == "regression":
                mse = mean_squared_error(y, y_pred)
                r2 = r2_score(y, y_pred)
                score = {
                    "mse": mse,
                    "rmse": np.sqrt(mse),
                    "r2": r2,
                    "cv_mean": cv_scores.mean(),
                    "cv_std": cv_scores.std()
                }
            else:
                accuracy = accuracy_score(y, y_pred)
                score = {
                    "accuracy": accuracy,
                    "cv_mean": cv_scores.mean(),
                    "cv_std": cv_scores.std()
                }
            
            results[name] = {
                "model": model,
                "scores": score,
                "predictions": y_pred
            }
            
            self.logger.info(f"{name} 모델 완료: {score}")
        
        self.models[task_type] = results
        return results
    
    def hyperparameter_tuning(self, X: np.ndarray, y: np.ndarray, 
                            model_name: str, task_type: str = "regression") -> Dict:
        """하이퍼파라미터 튜닝"""
        self.logger.info(f"{model_name} 하이퍼파라미터 튜닝 시작")
        
        if model_name not in self.config["hyperparameters"]:
            self.logger.warning(f"{model_name}의 하이퍼파라미터 설정이 없습니다.")
            return {}
        
        # 기본 모델 생성
        base_models = self.create_models(task_type)
        base_model = base_models[model_name]
        
        # 그리드 서치
        grid_search = GridSearchCV(
            base_model,
            self.config["hyperparameters"][model_name],
            cv=self.config["cross_validation"]["folds"],
            scoring='neg_mean_squared_error' if task_type == "regression" else 'accuracy',
            n_jobs=-1
        )
        
        grid_search.fit(X, y)
        
        best_model = grid_search.best_estimator_
        best_params = grid_search.best_params_
        best_score = grid_search.best_score_
        
        self.logger.info(f"최적 하이퍼파라미터: {best_params}")
        self.logger.info(f"최적 점수: {best_score}")
        
        return {
            "best_model": best_model,
            "best_params": best_params,
            "best_score": best_score,
            "cv_results": grid_search.cv_results_
        }
    
    def ensemble_prediction(self, X: np.ndarray, task_type: str = "regression") -> np.ndarray:
        """앙상블 예측"""
        if task_type not in self.models:
            raise ValueError(f"{task_type} 모델이 훈련되지 않았습니다.")
        
        predictions = []
        weights = []
        
        for name, result in self.models[task_type].items():
            model = result["model"]
            pred = model.predict(X)
            predictions.append(pred)
            
            # 가중치 계산 (성능 기반)
            if task_type == "regression":
                weight = result["scores"]["r2"]
            else:
                weight = result["scores"]["accuracy"]
            weights.append(max(weight, 0))  # 음수 가중치 방지
        
        # 가중치 정규화
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        # 가중 평균 계산
        ensemble_pred = np.average(predictions, axis=0, weights=weights)
        
        return ensemble_pred
    
    def time_series_forecast(self, data: pd.Series, periods: int = 30, 
                           method: str = "auto") -> pd.Series:
        """시계열 예측"""
        self.logger.info(f"시계열 예측 시작: {periods} 기간")
        
        if method == "auto":
            # 자동으로 최적 방법 선택
            if len(data) < 50:
                method = "simple"
            elif len(data) < 200:
                method = "moving_average"
            else:
                method = "exponential_smoothing"
        
        if method == "simple":
            # 단순 평균
            forecast = pd.Series([data.mean()] * periods)
        elif method == "moving_average":
            # 이동 평균
            window = min(20, len(data) // 4)
            ma = data.rolling(window=window).mean().iloc[-1]
            trend = (data.iloc[-1] - data.iloc[-window]) / window if window > 1 else 0
            forecast_values = []
            for i in range(periods):
                forecast_values.append(ma + trend * (i + 1))
            forecast = pd.Series(forecast_values)
        elif method == "exponential_smoothing":
            # 지수 평활
            alpha = 0.3
            forecast_values = []
            last_value = data.iloc[-1]
            trend = (data.iloc[-1] - data.iloc[-10]) / 10 if len(data) > 10 else 0
            
            for i in range(periods):
                next_value = alpha * last_value + (1 - alpha) * (last_value + trend)
                forecast_values.append(next_value)
                last_value = next_value
            
            forecast = pd.Series(forecast_values)
        else:
            raise ValueError(f"지원하지 않는 방법: {method}")
        
        return forecast
    
    def feature_importance_analysis(self, task_type: str = "regression") -> Dict:
        """특성 중요도 분석"""
        if task_type not in self.models:
            raise ValueError(f"{task_type} 모델이 훈련되지 않았습니다.")
        
        importance_analysis = {}
        
        for name, result in self.models[task_type].items():
            model = result["model"]
            
            if hasattr(model, 'feature_importances_'):
                importance_analysis[name] = {
                    "feature_importances": model.feature_importances_.tolist(),
                    "feature_names": getattr(self, 'feature_names', [])
                }
            elif hasattr(model, 'coef_'):
                importance_analysis[name] = {
                    "feature_importances": np.abs(model.coef_).tolist(),
                    "feature_names": getattr(self, 'feature_names', [])
                }
        
        return importance_analysis
    
    def save_model(self, model_name: str, task_type: str, filepath: str):
        """모델 저장"""
        if task_type not in self.models or model_name not in self.models[task_type]:
            raise ValueError(f"모델을 찾을 수 없습니다: {task_type}/{model_name}")
        
        model_data = {
            "model": self.models[task_type][model_name]["model"],
            "scaler": self.scalers.get(f"{task_type}_scaler"),
            "feature_selector": self.feature_selectors.get(f"{task_type}_selector"),
            "metadata": {
                "task_type": task_type,
                "model_name": model_name,
                "scores": self.models[task_type][model_name]["scores"],
                "created_at": datetime.now().isoformat()
            }
        }
        
        joblib.dump(model_data, filepath)
        self.logger.info(f"모델 저장 완료: {filepath}")
    
    def load_model(self, filepath: str) -> Dict:
        """모델 로드"""
        model_data = joblib.load(filepath)
        self.logger.info(f"모델 로드 완료: {filepath}")
        return model_data
    
    def predict(self, X: np.ndarray, model_name: str = None, 
               task_type: str = "regression", use_ensemble: bool = False) -> np.ndarray:
        """예측 수행"""
        if use_ensemble:
            return self.ensemble_prediction(X, task_type)
        
        if model_name is None:
            # 최고 성능 모델 선택
            best_model = None
            best_score = -float('inf')
            
            for name, result in self.models[task_type].items():
                if task_type == "regression":
                    score = result["scores"]["r2"]
                else:
                    score = result["scores"]["accuracy"]
                
                if score > best_score:
                    best_score = score
                    best_model = name
            
            model_name = best_model
        
        if task_type not in self.models or model_name not in self.models[task_type]:
            raise ValueError(f"모델을 찾을 수 없습니다: {task_type}/{model_name}")
        
        model = self.models[task_type][model_name]["model"]
        return model.predict(X)
    
    def generate_report(self, task_type: str = "regression") -> Dict:
        """분석 리포트 생성"""
        if task_type not in self.models:
            raise ValueError(f"{task_type} 모델이 훈련되지 않았습니다.")
        
        report = {
            "task_type": task_type,
            "models_trained": len(self.models[task_type]),
            "best_model": None,
            "model_comparison": {},
            "feature_importance": self.feature_importance_analysis(task_type),
            "generated_at": datetime.now().isoformat()
        }
        
        # 모델 비교
        best_score = -float('inf')
        for name, result in self.models[task_type].items():
            if task_type == "regression":
                score = result["scores"]["r2"]
            else:
                score = result["scores"]["accuracy"]
            
            report["model_comparison"][name] = result["scores"]
            
            if score > best_score:
                best_score = score
                report["best_model"] = name
        
        return report

# 사용 예시
if __name__ == "__main__":
    # 엔진 초기화
    engine = AIPredictionEngine()
    
    # 샘플 데이터 생성
    np.random.seed(42)
    n_samples = 1000
    X = np.random.randn(n_samples, 10)
    y = 2 * X[:, 0] + 1.5 * X[:, 1] + 0.5 * X[:, 2] + np.random.randn(n_samples) * 0.1
    
    data = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(10)])
    data['target'] = y
    
    # 데이터 준비
    X_processed, y_processed, features = engine.prepare_data(data, 'target', 'regression')
    
    # 모델 훈련
    results = engine.train_models(X_processed, y_processed, 'regression')
    
    # 하이퍼파라미터 튜닝
    tuning_result = engine.hyperparameter_tuning(X_processed, y_processed, 'random_forest', 'regression')
    
    # 앙상블 예측
    ensemble_pred = engine.ensemble_prediction(X_processed, 'regression')
    
    # 리포트 생성
    report = engine.generate_report('regression')
    print("분석 리포트:", json.dumps(report, indent=2, ensure_ascii=False)) 