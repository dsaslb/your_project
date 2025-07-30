"""
고급 AI 분석 엔진
엔터프라이즈급 비즈니스 인텔리전스 및 예측 분석
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedAIEngine:
    """고급 AI 분석 엔진"""
    
    def __init__(self, config_path: str = "ai/ai_config.json"):
        self.config = self._load_config(config_path)
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.performance_metrics = {}
        self.predictions_cache = {}
        
    def _load_config(self, config_path: str) -> Dict:
        """AI 설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"설정 파일을 찾을 수 없습니다: {config_path}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """기본 설정 반환"""
        return {
            "models": {
                "sales_prediction": {
                    "type": "gradient_boosting",
                    "params": {
                        "n_estimators": 100,
                        "learning_rate": 0.1,
                        "max_depth": 6
                    }
                },
                "customer_churn": {
                    "type": "random_forest",
                    "params": {
                        "n_estimators": 200,
                        "max_depth": 10,
                        "random_state": 42
                    }
                },
                "inventory_optimization": {
                    "type": "linear_regression",
                    "params": {}
                }
            },
            "scaling": "standard",
            "cross_validation_folds": 5,
            "test_size": 0.2,
            "random_state": 42
        }
    
    def prepare_data(self, data: pd.DataFrame, target_column: str) -> Tuple[np.ndarray, np.ndarray]:
        """데이터 전처리"""
        logger.info("데이터 전처리 시작...")
        
        # 결측값 처리
        data = data.fillna(data.mean())
        
        # 범주형 변수 인코딩
        categorical_columns = data.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if col != target_column:
                data[col] = pd.Categorical(data[col]).codes
        
        # 특성과 타겟 분리
        X = data.drop(columns=[target_column])
        y = data[target_column]
        
        # 스케일링
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        self.scalers[target_column] = scaler
        
        logger.info(f"데이터 전처리 완료: {X.shape[0]} 샘플, {X.shape[1]} 특성")
        return X_scaled, y.values
    
    def train_model(self, model_name: str, X: np.ndarray, y: np.ndarray) -> Any:
        """모델 훈련"""
        logger.info(f"{model_name} 모델 훈련 시작...")
        
        model_config = self.config["models"].get(model_name, {})
        model_type = model_config.get("type", "random_forest")
        params = model_config.get("params", {})
        
        # 모델 선택
        if model_type == "random_forest":
            model = RandomForestRegressor(**params)
        elif model_type == "gradient_boosting":
            model = GradientBoostingRegressor(**params)
        elif model_type == "linear_regression":
            model = LinearRegression(**params)
        elif model_type == "ridge":
            model = Ridge(**params)
        elif model_type == "lasso":
            model = Lasso(**params)
        else:
            raise ValueError(f"지원하지 않는 모델 타입: {model_type}")
        
        # 교차 검증
        cv_scores = cross_val_score(
            model, X, y, 
            cv=self.config["cross_validation_folds"],
            scoring='r2'
        )
        
        # 모델 훈련
        model.fit(X, y)
        
        # 성능 평가
        y_pred = model.predict(X)
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        
        # 결과 저장
        self.models[model_name] = model
        self.performance_metrics[model_name] = {
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
            "mse": mse,
            "r2": r2,
            "mae": mae
        }
        
        # 특성 중요도 저장
        if hasattr(model, 'feature_importances_'):
            self.feature_importance[model_name] = model.feature_importances_
        
        logger.info(f"{model_name} 모델 훈련 완료 - R²: {r2:.4f}")
        return model
    
    def predict(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """예측 수행"""
        if model_name not in self.models:
            raise ValueError(f"모델이 훈련되지 않았습니다: {model_name}")
        
        # 스케일링 적용
        if model_name in self.scalers:
            X = self.scalers[model_name].transform(X)
        
        predictions = self.models[model_name].predict(X)
        
        # 캐시에 저장
        cache_key = f"{model_name}_{hash(str(X))}"
        self.predictions_cache[cache_key] = predictions
        
        return predictions
    
    def analyze_feature_importance(self, model_name: str, feature_names: List[str]) -> Dict:
        """특성 중요도 분석"""
        if model_name not in self.feature_importance:
            return {}
        
        importance = self.feature_importance[model_name]
        feature_importance_dict = dict(zip(feature_names, importance))
        
        # 중요도 순으로 정렬
        sorted_features = sorted(
            feature_importance_dict.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return {
            "feature_importance": dict(sorted_features),
            "top_features": sorted_features[:10],
            "total_importance": sum(importance)
        }
    
    def get_model_performance(self, model_name: str) -> Dict:
        """모델 성능 정보 반환"""
        if model_name not in self.performance_metrics:
            return {}
        
        return self.performance_metrics[model_name]
    
    def save_model(self, model_name: str, filepath: str):
        """모델 저장"""
        if model_name not in self.models:
            raise ValueError(f"모델이 훈련되지 않았습니다: {model_name}")
        
        model_data = {
            "model": self.models[model_name],
            "scaler": self.scalers.get(model_name),
            "performance": self.performance_metrics.get(model_name, {}),
            "feature_importance": self.feature_importance.get(model_name, {}),
            "config": self.config
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"모델 저장 완료: {filepath}")
    
    def load_model(self, model_name: str, filepath: str):
        """모델 로드"""
        model_data = joblib.load(filepath)
        
        self.models[model_name] = model_data["model"]
        if model_data["scaler"]:
            self.scalers[model_name] = model_data["scaler"]
        self.performance_metrics[model_name] = model_data["performance"]
        self.feature_importance[model_name] = model_data["feature_importance"]
        
        logger.info(f"모델 로드 완료: {filepath}")
    
    def generate_report(self, model_name: str) -> Dict:
        """AI 분석 리포트 생성"""
        if model_name not in self.models:
            return {"error": "모델이 훈련되지 않았습니다"}
        
        performance = self.performance_metrics[model_name]
        
        report = {
            "model_name": model_name,
            "training_date": datetime.now().isoformat(),
            "performance_metrics": performance,
            "model_type": type(self.models[model_name]).__name__,
            "feature_count": len(self.feature_importance.get(model_name, [])),
            "recommendations": self._generate_recommendations(performance)
        }
        
        return report
    
    def _generate_recommendations(self, performance: Dict) -> List[str]:
        """성능 기반 권장사항 생성"""
        recommendations = []
        
        if performance.get("r2", 0) < 0.7:
            recommendations.append("모델 성능이 낮습니다. 더 많은 데이터나 특성 엔지니어링을 고려하세요.")
        
        if performance.get("cv_std", 0) > 0.1:
            recommendations.append("교차 검증 표준편차가 높습니다. 모델 안정성을 개선하세요.")
        
        if performance.get("mae", 0) > 0.5:
            recommendations.append("평균 절대 오차가 높습니다. 모델 파라미터를 조정하세요.")
        
        if not recommendations:
            recommendations.append("모델 성능이 양호합니다. 현재 설정을 유지하세요.")
        
        return recommendations

class BusinessIntelligenceAI:
    """비즈니스 인텔리전스 AI"""
    
    def __init__(self):
        self.ai_engine = AdvancedAIEngine()
        self.business_metrics = {}
        
    def analyze_sales_trends(self, sales_data: pd.DataFrame) -> Dict:
        """매출 트렌드 분석"""
        logger.info("매출 트렌드 분석 시작...")
        
        # 시계열 특성 생성
        sales_data['date'] = pd.to_datetime(sales_data['date'])
        sales_data['month'] = sales_data['date'].dt.month
        sales_data['quarter'] = sales_data['date'].dt.quarter
        sales_data['year'] = sales_data['date'].dt.year
        sales_data['day_of_week'] = sales_data['date'].dt.dayofweek
        
        # 데이터 준비
        X, y = self.ai_engine.prepare_data(sales_data, 'sales_amount')
        
        # 모델 훈련
        model = self.ai_engine.train_model("sales_prediction", X, y)
        
        # 특성 중요도 분석
        feature_names = sales_data.drop(columns=['sales_amount', 'date']).columns.tolist()
        importance_analysis = self.ai_engine.analyze_feature_importance("sales_prediction", feature_names)
        
        # 트렌드 분석
        trends = self._analyze_trends(sales_data)
        
        return {
            "model_performance": self.ai_engine.get_model_performance("sales_prediction"),
            "feature_importance": importance_analysis,
            "trends": trends,
            "predictions": self._generate_sales_predictions(sales_data)
        }
    
    def predict_customer_churn(self, customer_data: pd.DataFrame) -> Dict:
        """고객 이탈 예측"""
        logger.info("고객 이탈 예측 시작...")
        
        # 데이터 준비
        X, y = self.ai_engine.prepare_data(customer_data, 'churn')
        
        # 모델 훈련
        model = self.ai_engine.train_model("customer_churn", X, y)
        
        # 고위험 고객 식별
        predictions = self.ai_engine.predict("customer_churn", X)
        high_risk_customers = customer_data[predictions > 0.7]
        
        return {
            "model_performance": self.ai_engine.get_model_performance("customer_churn"),
            "high_risk_customers": high_risk_customers,
            "churn_probability": predictions.tolist(),
            "recommendations": self._generate_churn_recommendations(high_risk_customers)
        }
    
    def optimize_inventory(self, inventory_data: pd.DataFrame) -> Dict:
        """재고 최적화"""
        logger.info("재고 최적화 분석 시작...")
        
        # 데이터 준비
        X, y = self.ai_engine.prepare_data(inventory_data, 'optimal_stock')
        
        # 모델 훈련
        model = self.ai_engine.train_model("inventory_optimization", X, y)
        
        # 최적 재고량 계산
        optimal_stock = self.ai_engine.predict("inventory_optimization", X)
        
        return {
            "model_performance": self.ai_engine.get_model_performance("inventory_optimization"),
            "optimal_stock_levels": optimal_stock.tolist(),
            "cost_savings": self._calculate_cost_savings(inventory_data, optimal_stock),
            "recommendations": self._generate_inventory_recommendations(inventory_data, optimal_stock)
        }
    
    def _analyze_trends(self, data: pd.DataFrame) -> Dict:
        """트렌드 분석"""
        trends = {}
        
        # 월별 트렌드
        monthly_trend = data.groupby('month')['sales_amount'].mean()
        trends['monthly'] = monthly_trend.to_dict()
        
        # 분기별 트렌드
        quarterly_trend = data.groupby('quarter')['sales_amount'].mean()
        trends['quarterly'] = quarterly_trend.to_dict()
        
        # 성장률 계산
        if len(data) > 1:
            growth_rate = ((data['sales_amount'].iloc[-1] - data['sales_amount'].iloc[0]) / 
                          data['sales_amount'].iloc[0]) * 100
            trends['growth_rate'] = growth_rate
        
        return trends
    
    def _generate_sales_predictions(self, data: pd.DataFrame) -> Dict:
        """매출 예측 생성"""
        # 향후 3개월 예측
        future_dates = pd.date_range(
            start=data['date'].max() + timedelta(days=1),
            periods=90,
            freq='D'
        )
        
        # 예측 데이터 준비
        future_data = pd.DataFrame({
            'date': future_dates,
            'month': future_dates.month,
            'quarter': future_dates.quarter,
            'year': future_dates.year,
            'day_of_week': future_dates.dayofweek
        })
        
        # 기타 특성들은 평균값으로 설정
        for col in data.columns:
            if col not in ['date', 'sales_amount']:
                future_data[col] = data[col].mean()
        
        # 예측 수행
        X_future, _ = self.ai_engine.prepare_data(future_data, 'sales_amount')
        predictions = self.ai_engine.predict("sales_prediction", X_future)
        
        return {
            "future_dates": future_dates.strftime('%Y-%m-%d').tolist(),
            "predictions": predictions.tolist(),
            "confidence_interval": self._calculate_confidence_interval(predictions)
        }
    
    def _generate_churn_recommendations(self, high_risk_customers: pd.DataFrame) -> List[str]:
        """이탈 방지 권장사항"""
        recommendations = []
        
        if len(high_risk_customers) > 0:
            recommendations.append(f"고위험 고객 {len(high_risk_customers)}명에게 특별 관리 필요")
            recommendations.append("고객 만족도 조사 실시")
            recommendations.append("충성도 프로그램 도입 고려")
            recommendations.append("개인화된 마케팅 캠페인 실행")
        
        return recommendations
    
    def _calculate_cost_savings(self, current_data: pd.DataFrame, optimal_stock: np.ndarray) -> float:
        """비용 절감 계산"""
        current_stock = current_data['current_stock'].sum()
        optimal_stock_total = optimal_stock.sum()
        
        # 재고 보관 비용 (가정: 단위당 10원)
        storage_cost_per_unit = 10
        cost_savings = (current_stock - optimal_stock_total) * storage_cost_per_unit
        
        return max(0, cost_savings)
    
    def _generate_inventory_recommendations(self, data: pd.DataFrame, optimal_stock: np.ndarray) -> List[str]:
        """재고 최적화 권장사항"""
        recommendations = []
        
        overstocked = data[data['current_stock'] > optimal_stock]
        understocked = data[data['current_stock'] < optimal_stock]
        
        if len(overstocked) > 0:
            recommendations.append(f"과잉 재고 제품 {len(overstocked)}개 - 할인 판매 고려")
        
        if len(understocked) > 0:
            recommendations.append(f"부족 재고 제품 {len(understocked)}개 - 발주 필요")
        
        recommendations.append("자동 재고 관리 시스템 도입 권장")
        
        return recommendations
    
    def _calculate_confidence_interval(self, predictions: np.ndarray, confidence: float = 0.95) -> Dict:
        """신뢰구간 계산"""
        mean_pred = np.mean(predictions)
        std_pred = np.std(predictions)
        
        # 95% 신뢰구간
        z_score = 1.96  # 95% 신뢰수준
        margin_of_error = z_score * (std_pred / np.sqrt(len(predictions)))
        
        return {
            "lower_bound": mean_pred - margin_of_error,
            "upper_bound": mean_pred + margin_of_error,
            "confidence_level": confidence
        }

# 사용 예시
if __name__ == "__main__":
    # AI 엔진 초기화
    bi_ai = BusinessIntelligenceAI()
    
    # 샘플 데이터 생성
    np.random.seed(42)
    n_samples = 1000
    
    # 매출 데이터
    sales_data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=n_samples, freq='D'),
        'sales_amount': np.random.normal(1000, 200, n_samples),
        'customer_count': np.random.poisson(50, n_samples),
        'product_price': np.random.uniform(10, 100, n_samples),
        'marketing_budget': np.random.uniform(100, 1000, n_samples)
    })
    
    # 매출 트렌드 분석
    sales_analysis = bi_ai.analyze_sales_trends(sales_data)
    print("매출 분석 완료:", sales_analysis['model_performance']['r2'])
    
    # 고객 이탈 데이터
    customer_data = pd.DataFrame({
        'tenure': np.random.exponential(5, n_samples),
        'monthly_charges': np.random.normal(50, 15, n_samples),
        'total_charges': np.random.normal(1000, 300, n_samples),
        'contract_type': np.random.choice(['Month-to-month', 'One year', 'Two year'], n_samples),
        'churn': np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    })
    
    # 고객 이탈 예측
    churn_analysis = bi_ai.predict_customer_churn(customer_data)
    print("이탈 예측 완료:", len(churn_analysis['high_risk_customers']), "명의 고위험 고객")
    
    # 재고 데이터
    inventory_data = pd.DataFrame({
        'current_stock': np.random.poisson(100, n_samples),
        'demand': np.random.poisson(80, n_samples),
        'lead_time': np.random.exponential(7, n_samples),
        'holding_cost': np.random.uniform(5, 20, n_samples),
        'optimal_stock': np.random.poisson(90, n_samples)
    })
    
    # 재고 최적화
    inventory_analysis = bi_ai.optimize_inventory(inventory_data)
    print("재고 최적화 완료:", inventory_analysis['cost_savings'], "원 절감") 