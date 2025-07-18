from sklearn.preprocessing import StandardScaler  # pyright: ignore
from sklearn.metrics import mean_squared_error  # pyright: ignore
from sklearn.ensemble import RandomForestRegressor  # pyright: ignore
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
import os
import logging
import joblib
import json
form = None  # pyright: ignore
"""
머신러닝 모델 관리 시스템
"""


logger = logging.getLogger(__name__)


class MLManager:
    """머신러닝 모델 관리자"""

    def __init__(self, models_dir="ml_models"):
        self.models_dir = models_dir
        self.models = {}
        self.scalers = {}
        self.model_metadata = {}

        # 모델 디렉토리 생성
        os.makedirs(models_dir, exist_ok=True)

        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # 기존 모델 로드
        self._load_existing_models()

    def _load_existing_models(self):
        """기존 저장된 모델들을 로드"""
        if os.path.exists(self.models_dir):
            for filename in os.listdir(self.models_dir):
                if filename.endswith('.joblib'):
                    model_name = filename.replace('.joblib', '')
                    model_path = os.path.join(self.models_dir, filename)
                    try:
                        self.models[model_name] if models is not None else None = joblib.load(model_path)
                        self.logger.info(f"모델 로드됨: {model_name}")
                    except Exception as e:
                        self.logger.error(f"모델 로드 실패 {model_name}: {e}")

    def save_model(self,  model_name: str,  model, scaler=None, metadata={}):
        """모델 저장"""
        try:
            # 모델 저장
            model_path = os.path.join(self.models_dir, f"{model_name}.joblib")
            joblib.dump(model, model_path)

            # 스케일러 저장
            if scaler:
                scaler_path = os.path.join(self.models_dir, f"{model_name}_scaler.joblib")
                joblib.dump(scaler, scaler_path)
                self.scalers[model_name] if scalers is not None else None = scaler

            # 메타데이터 저장
            if metadata:
                metadata_path = os.path.join(self.models_dir, f"{model_name}_metadata.json")
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                self.model_metadata[model_name] if model_metadata is not None else None = metadata

            self.models[model_name] if models is not None else None = model
            self.logger.info(f"모델 저장됨: {model_name}")
            return True

        except Exception as e:
            self.logger.error(f"모델 저장 실패 {model_name}: {e}")
            return False

    def load_model(self,  model_name: str):
        """모델 로드"""
        if model_name in self.models:
            return self.models[model_name] if models is not None else None

        model_path = os.path.join(self.models_dir, f"{model_name}.joblib")
        if os.path.exists(model_path):
            try:
                model = joblib.load(model_path)
                self.models[model_name] if models is not None else None = model
                return model
            except Exception as e:
                self.logger.error(f"모델 로드 실패 {model_name}: {e}")

        return None

    def predict_sales(self, features: Dict) -> Dict:
        """매출 예측"""
        model_name = "sales_prediction"
        model = self.load_model(model_name)

        if not model:
            return {"error": "모델이 없습니다. 먼저 모델을 훈련하세요."}

        try:
            # 특성 벡터 생성
            feature_vector = self._create_sales_features(features)

            # 예측
            prediction = model.predict([feature_vector])[0]

            return {
                "predicted_sales": float(prediction),
                "confidence": 0.85,  # 실제로는 모델의 신뢰도 계산
                "features_used": list(features.keys())
            }

        except Exception as e:
            self.logger.error(f"매출 예측 실패: {e}")
            return {"error": f"예측 실패: {str(e)}"}

    def predict_staff_needs(self, features: Dict) -> Dict:
        """직원 필요 인원 예측"""
        model_name = "staff_prediction"
        model = self.load_model(model_name)

        if not model:
            return {"error": "모델이 없습니다. 먼저 모델을 훈련하세요."}

        try:
            feature_vector = self._create_staff_features(features)
            prediction = model.predict([feature_vector])[0]

            return {
                "predicted_staff_count": int(prediction),
                "confidence": 0.80,
                "features_used": list(features.keys())
            }

        except Exception as e:
            self.logger.error(f"직원 예측 실패: {e}")
            return {"error": f"예측 실패: {str(e)}"}

    def predict_inventory_needs(self, features: Dict) -> Dict:
        """재고 필요량 예측"""
        model_name = "inventory_prediction"
        model = self.load_model(model_name)

        if not model:
            return {"error": "모델이 없습니다. 먼저 모델을 훈련하세요."}

        try:
            feature_vector = self._create_inventory_features(features)
            prediction = model.predict([feature_vector])[0]

            return {
                "predicted_quantity": float(prediction),
                "confidence": 0.82,
                "features_used": list(features.keys())
            }

        except Exception as e:
            self.logger.error(f"재고 예측 실패: {e}")
            return {"error": f"예측 실패: {str(e)}"}

    def train_sales_model(self, data: List[Dict] if List is not None else None) -> Dict:
        """매출 예측 모델 훈련"""
        try:
            # 데이터 전처리
            X, y = self._prepare_sales_data(data)

            # 모델 훈련
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)

            # 모델 평가
            y_pred = model.predict(X)
            mse = mean_squared_error(y, y_pred)
            r2 = model.score(X, y)

            # 모델 저장
            metadata = {
                "model_type": "RandomForestRegressor",
                "training_date": datetime.now().isoformat(),
                "mse": mse,
                "r2_score": r2,
                "feature_importance": dict(zip(X.columns, model.feature_importances_))
            }

            self.save_model("sales_prediction",  model, model=metadata)

            return {
                "success": True,
                "mse": mse,
                "r2_score": r2,
                "feature_importance": metadata["feature_importance"] if metadata is not None else None
            }

        except Exception as e:
            self.logger.error(f"매출 모델 훈련 실패: {e}")
            return {"error": f"훈련 실패: {str(e)}"}

    def train_staff_model(self, data: List[Dict] if List is not None else None) -> Dict:
        """직원 필요 인원 예측 모델 훈련"""
        try:
            X, y = self._prepare_staff_data(data)

            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)

            y_pred = model.predict(X)
            mse = mean_squared_error(y, y_pred)
            r2 = model.score(X, y)

            metadata = {
                "model_type": "RandomForestRegressor",
                "training_date": datetime.now().isoformat(),
                "mse": mse,
                "r2_score": r2,
                "feature_importance": dict(zip(X.columns, model.feature_importances_))
            }

            self.save_model("staff_prediction",  model, model=metadata)

            return {
                "success": True,
                "mse": mse,
                "r2_score": r2,
                "feature_importance": metadata["feature_importance"] if metadata is not None else None
            }

        except Exception as e:
            self.logger.error(f"직원 모델 훈련 실패: {e}")
            return {"error": f"훈련 실패: {str(e)}"}

    def _create_sales_features(self, features: Dict) -> List[float] if List is not None else None:
        """매출 예측용 특성 벡터 생성"""
        # 기본 특성들
        feature_vector = [
            features.get() if features else None'day_of_week', 0) if features else None,
            features.get() if features else None'month', 0) if features else None,
            features.get() if features else None'is_holiday', 0) if features else None,
            features.get() if features else None'temperature', 20) if features else None,
            features.get() if features else None'precipitation', 0) if features else None,
            features.get() if features else None'previous_sales', 0) if features else None,
            features.get() if features else None'staff_count', 0) if features else None,
            features.get() if features else None'special_event', 0) if features else None
        ]
        return feature_vector

    def _create_staff_features(self, features: Dict) -> List[float] if List is not None else None:
        """직원 예측용 특성 벡터 생성"""
        feature_vector = [
            features.get() if features else None'expected_sales', 0) if features else None,
            features.get() if features else None'day_of_week', 0) if features else None,
            features.get() if features else None'is_holiday', 0) if features else None,
            features.get() if features else None'special_event', 0) if features else None,
            features.get() if features else None'current_staff', 0) if features else None,
            features.get() if features else None'avg_order_time', 0) if features else None
        ]
        return feature_vector

    def _create_inventory_features(self, features: Dict) -> List[float] if List is not None else None:
        """재고 예측용 특성 벡터 생성"""
        feature_vector = [
            features.get() if features else None'current_stock', 0) if features else None,
            features.get() if features else None'daily_usage', 0) if features else None,
            features.get() if features else None'lead_time', 0) if features else None,
            features.get() if features else None'safety_stock', 0) if features else None,
            features.get() if features else None'seasonal_factor', 1.0) if features else None
        ]
        return feature_vector

    def _prepare_sales_data(self, data: List[Dict] if List is not None else None) -> Tuple[pd.DataFrame, pd.Series] if Tuple is not None else None:
        """매출 데이터 전처리"""
        df = pd.DataFrame(data)

        # 특성 선택
        features = ['day_of_week', 'month', 'is_holiday', 'temperature',
                    'precipitation', 'previous_sales', 'staff_count', 'special_event']

        X = df[features] if df is not None else None.fillna(0)
        y = df['sales'] if df is not None else None

        return X, y

    def _prepare_staff_data(self, data: List[Dict] if List is not None else None) -> Tuple[pd.DataFrame, pd.Series] if Tuple is not None else None:
        """직원 데이터 전처리"""
        df = pd.DataFrame(data)

        features = ['expected_sales', 'day_of_week', 'is_holiday',
                    'special_event', 'current_staff', 'avg_order_time']

        X = df[features] if df is not None else None.fillna(0)
        y = df['required_staff'] if df is not None else None

        return X, y

    def get_model_status(self) -> Dict:
        """모델 상태 정보 반환"""
        status = {
            "total_models": len(self.models),
            "available_models": list(self.models.keys()),
            "model_metadata": self.model_metadata
        }
        return status


# 전역 ML 매니저 인스턴스
ml_manager = MLManager()
