"""
머신러닝 파이프라인 시스템
데이터 수집, 전처리, 모델 학습, 평가, 배포를 자동화하는 엔터프라이즈급 ML 파이프라인
"""

import logging
import json
import yaml
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import joblib
import os
import shutil
import tempfile
from pathlib import Path
import uuid
import hashlib
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import queue
import time
import warnings
warnings.filterwarnings('ignore')

# ML 라이브러리
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVC, SVR
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    classification_report, confusion_matrix, roc_auc_score
)
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import xgboost as xgb
import lightgbm as lgb
import optuna
from optuna.samplers import TPESampler

# 딥러닝 라이브러리
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, callbacks
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, Dataset
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """모델 타입"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"

class AlgorithmType(Enum):
    """알고리즘 타입"""
    # 전통적 ML
    RANDOM_FOREST = "random_forest"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    LINEAR_REGRESSION = "linear_regression"
    LOGISTIC_REGRESSION = "logistic_regression"
    SVM = "svm"
    KMEANS = "kmeans"
    
    # 딥러닝
    NEURAL_NETWORK = "neural_network"
    CNN = "cnn"
    RNN = "rnn"
    LSTM = "lstm"
    TRANSFORMER = "transformer"

class PipelineStage(Enum):
    """파이프라인 단계"""
    DATA_COLLECTION = "data_collection"
    DATA_PREPROCESSING = "data_preprocessing"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_TRAINING = "model_training"
    MODEL_EVALUATION = "model_evaluation"
    MODEL_DEPLOYMENT = "model_deployment"
    MODEL_MONITORING = "model_monitoring"

@dataclass
class ModelConfig:
    """모델 설정"""
    id: str
    name: str
    model_type: ModelType
    algorithm: AlgorithmType
    hyperparameters: Dict[str, Any]
    feature_columns: List[str]
    target_column: str
    test_size: float = 0.2
    random_state: int = 42
    cross_validation_folds: int = 5
    optimization_trials: int = 100
    created_at: datetime = None

@dataclass
class TrainingResult:
    """학습 결과"""
    model_id: str
    model_path: str
    metrics: Dict[str, float]
    hyperparameters: Dict[str, Any]
    feature_importance: Dict[str, float]
    training_time: float
    model_size: int
    created_at: datetime = None

@dataclass
class PipelineConfig:
    """파이프라인 설정"""
    pipeline_id: str
    name: str
    description: str
    stages: List[PipelineStage]
    data_source: Dict[str, Any]
    preprocessing_config: Dict[str, Any]
    model_configs: List[ModelConfig]
    evaluation_metrics: List[str]
    deployment_config: Dict[str, Any]
    monitoring_config: Dict[str, Any]
    created_at: datetime = None

class MLPipeline:
    """머신러닝 파이프라인 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pipelines: Dict[str, PipelineConfig] = {}
        self.models: Dict[str, Any] = {}
        self.results: Dict[str, TrainingResult] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.process_executor = ProcessPoolExecutor(max_workers=2)
        self.training_queue = queue.Queue()
        self.is_running = False
        
        self._setup_directories()
        self._load_existing_pipelines()
        self._start_training_worker()
    
    def _setup_directories(self):
        """디렉토리 설정"""
        self.base_dir = Path(self.config.get('base_dir', './ml_pipeline'))
        self.data_dir = self.base_dir / 'data'
        self.models_dir = self.base_dir / 'models'
        self.results_dir = self.base_dir / 'results'
        self.logs_dir = self.base_dir / 'logs'
        self.temp_dir = self.base_dir / 'temp'
        
        for directory in [self.data_dir, self.models_dir, self.results_dir, self.logs_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_existing_pipelines(self):
        """기존 파이프라인 로드"""
        try:
            pipeline_file = self.base_dir / 'pipelines.json'
            if pipeline_file.exists():
                with open(pipeline_file, 'r') as f:
                    pipelines_data = json.load(f)
                
                for pipeline_data in pipelines_data:
                    pipeline = PipelineConfig(**pipeline_data)
                    self.pipelines[pipeline.pipeline_id] = pipeline
                
                logger.info(f"{len(self.pipelines)}개의 파이프라인 로드 완료")
        except Exception as e:
            logger.error(f"파이프라인 로드 오류: {e}")
    
    def _start_training_worker(self):
        """학습 워커 시작"""
        self.is_running = True
        self.training_thread = threading.Thread(target=self._training_worker, daemon=True)
        self.training_thread.start()
    
    def _training_worker(self):
        """학습 워커"""
        while self.is_running:
            try:
                task = self.training_queue.get(timeout=1)
                if task is None:
                    break
                
                pipeline_id, model_config = task
                self._train_model(pipeline_id, model_config)
                self.training_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"학습 워커 오류: {e}")
    
    def create_pipeline(self, config: Dict[str, Any]) -> str:
        """파이프라인 생성"""
        try:
            pipeline_id = str(uuid.uuid4())
            
            pipeline = PipelineConfig(
                pipeline_id=pipeline_id,
                name=config['name'],
                description=config.get('description', ''),
                stages=config['stages'],
                data_source=config['data_source'],
                preprocessing_config=config.get('preprocessing_config', {}),
                model_configs=[],
                evaluation_metrics=config.get('evaluation_metrics', ['accuracy', 'precision', 'recall', 'f1']),
                deployment_config=config.get('deployment_config', {}),
                monitoring_config=config.get('monitoring_config', {}),
                created_at=datetime.now()
            )
            
            self.pipelines[pipeline_id] = pipeline
            self._save_pipelines()
            
            logger.info(f"파이프라인 생성 완료: {pipeline_id}")
            return pipeline_id
            
        except Exception as e:
            logger.error(f"파이프라인 생성 오류: {e}")
            raise
    
    def add_model_to_pipeline(self, pipeline_id: str, model_config: Dict[str, Any]) -> str:
        """파이프라인에 모델 추가"""
        try:
            pipeline = self.pipelines.get(pipeline_id)
            if not pipeline:
                raise ValueError(f"파이프라인을 찾을 수 없습니다: {pipeline_id}")
            
            model_id = str(uuid.uuid4())
            
            model = ModelConfig(
                id=model_id,
                name=model_config['name'],
                model_type=ModelType(model_config['model_type']),
                algorithm=AlgorithmType(model_config['algorithm']),
                hyperparameters=model_config.get('hyperparameters', {}),
                feature_columns=model_config['feature_columns'],
                target_column=model_config['target_column'],
                test_size=model_config.get('test_size', 0.2),
                random_state=model_config.get('random_state', 42),
                cross_validation_folds=model_config.get('cross_validation_folds', 5),
                optimization_trials=model_config.get('optimization_trials', 100),
                created_at=datetime.now()
            )
            
            pipeline.model_configs.append(model)
            self._save_pipelines()
            
            logger.info(f"모델 추가 완료: {model_id}")
            return model_id
            
        except Exception as e:
            logger.error(f"모델 추가 오류: {e}")
            raise
    
    def run_pipeline(self, pipeline_id: str, async_mode: bool = True) -> Union[str, Dict[str, Any]]:
        """파이프라인 실행"""
        try:
            pipeline = self.pipelines.get(pipeline_id)
            if not pipeline:
                raise ValueError(f"파이프라인을 찾을 수 없습니다: {pipeline_id}")
            
            if async_mode:
                # 비동기 실행
                for model_config in pipeline.model_configs:
                    self.training_queue.put((pipeline_id, model_config))
                
                return f"파이프라인 {pipeline_id} 비동기 실행 시작"
            else:
                # 동기 실행
                results = {}
                for model_config in pipeline.model_configs:
                    result = self._train_model(pipeline_id, model_config)
                    results[model_config.id] = result
                
                return results
                
        except Exception as e:
            logger.error(f"파이프라인 실행 오류: {e}")
            raise
    
    def _train_model(self, pipeline_id: str, model_config: ModelConfig) -> TrainingResult:
        """모델 학습"""
        start_time = time.time()
        
        try:
            logger.info(f"모델 학습 시작: {model_config.name}")
            
            # 1. 데이터 로드
            data = self._load_data(pipeline_id)
            
            # 2. 데이터 전처리
            processed_data = self._preprocess_data(data, model_config)
            
            # 3. 모델 생성
            model = self._create_model(model_config)
            
            # 4. 하이퍼파라미터 최적화
            if model_config.optimization_trials > 0:
                model = self._optimize_hyperparameters(model, processed_data, model_config)
            
            # 5. 모델 학습
            model = self._train_model_final(model, processed_data, model_config)
            
            # 6. 모델 평가
            metrics = self._evaluate_model(model, processed_data, model_config)
            
            # 7. 모델 저장
            model_path = self._save_model(model, model_config)
            
            # 8. 특성 중요도 계산
            feature_importance = self._calculate_feature_importance(model, model_config)
            
            training_time = time.time() - start_time
            model_size = self._get_model_size(model_path)
            
            result = TrainingResult(
                model_id=model_config.id,
                model_path=str(model_path),
                metrics=metrics,
                hyperparameters=model_config.hyperparameters,
                feature_importance=feature_importance,
                training_time=training_time,
                model_size=model_size,
                created_at=datetime.now()
            )
            
            self.results[model_config.id] = result
            self._save_results()
            
            logger.info(f"모델 학습 완료: {model_config.name} (시간: {training_time:.2f}초)")
            return result
            
        except Exception as e:
            logger.error(f"모델 학습 오류: {e}")
            raise
    
    def _load_data(self, pipeline_id: str) -> pd.DataFrame:
        """데이터 로드"""
        try:
            pipeline = self.pipelines[pipeline_id]
            data_source = pipeline.data_source
            
            if data_source['type'] == 'file':
                file_path = data_source['path']
                file_format = data_source.get('format', 'csv')
                
                if file_format == 'csv':
                    data = pd.read_csv(file_path)
                elif file_format == 'excel':
                    data = pd.read_excel(file_path)
                elif file_format == 'json':
                    data = pd.read_json(file_path)
                else:
                    raise ValueError(f"지원하지 않는 파일 형식: {file_format}")
                    
            elif data_source['type'] == 'database':
                # 데이터베이스에서 로드
                data = self._load_from_database(data_source)
                
            elif data_source['type'] == 'api':
                # API에서 로드
                data = self._load_from_api(data_source)
                
            else:
                raise ValueError(f"지원하지 않는 데이터 소스: {data_source['type']}")
            
            logger.info(f"데이터 로드 완료: {len(data)} 행, {len(data.columns)} 열")
            return data
            
        except Exception as e:
            logger.error(f"데이터 로드 오류: {e}")
            raise
    
    def _preprocess_data(self, data: pd.DataFrame, model_config: ModelConfig) -> Dict[str, Any]:
        """데이터 전처리"""
        try:
            # 특성과 타겟 분리
            X = data[model_config.feature_columns]
            y = data[model_config.target_column]
            
            # 결측값 처리
            X = self._handle_missing_values(X)
            
            # 범주형 변수 인코딩
            X = self._encode_categorical_features(X)
            
            # 특성 스케일링
            X = self._scale_features(X)
            
            # 훈련/테스트 분할
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, 
                test_size=model_config.test_size, 
                random_state=model_config.random_state
            )
            
            return {
                'X_train': X_train,
                'X_test': X_test,
                'y_train': y_train,
                'y_test': y_test,
                'feature_names': X.columns.tolist()
            }
            
        except Exception as e:
            logger.error(f"데이터 전처리 오류: {e}")
            raise
    
    def _handle_missing_values(self, X: pd.DataFrame) -> pd.DataFrame:
        """결측값 처리"""
        try:
            # 수치형 변수: 중앙값으로 대체
            numeric_columns = X.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                imputer = SimpleImputer(strategy='median')
                X[numeric_columns] = imputer.fit_transform(X[numeric_columns])
            
            # 범주형 변수: 최빈값으로 대체
            categorical_columns = X.select_dtypes(include=['object']).columns
            if len(categorical_columns) > 0:
                imputer = SimpleImputer(strategy='most_frequent')
                X[categorical_columns] = imputer.fit_transform(X[categorical_columns])
            
            return X
            
        except Exception as e:
            logger.error(f"결측값 처리 오류: {e}")
            raise
    
    def _encode_categorical_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """범주형 변수 인코딩"""
        try:
            categorical_columns = X.select_dtypes(include=['object']).columns
            
            for column in categorical_columns:
                # 레이블 인코딩
                le = LabelEncoder()
                X[column] = le.fit_transform(X[column].astype(str))
            
            return X
            
        except Exception as e:
            logger.error(f"범주형 변수 인코딩 오류: {e}")
            raise
    
    def _scale_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """특성 스케일링"""
        try:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            return pd.DataFrame(X_scaled, columns=X.columns)
            
        except Exception as e:
            logger.error(f"특성 스케일링 오류: {e}")
            raise
    
    def _create_model(self, model_config: ModelConfig) -> Any:
        """모델 생성"""
        try:
            algorithm = model_config.algorithm
            hyperparams = model_config.hyperparameters
            
            if algorithm == AlgorithmType.RANDOM_FOREST:
                if model_config.model_type == ModelType.CLASSIFICATION:
                    model = RandomForestClassifier(**hyperparams)
                else:
                    model = RandomForestRegressor(**hyperparams)
                    
            elif algorithm == AlgorithmType.XGBOOST:
                if model_config.model_type == ModelType.CLASSIFICATION:
                    model = xgb.XGBClassifier(**hyperparams)
                else:
                    model = xgb.XGBRegressor(**hyperparams)
                    
            elif algorithm == AlgorithmType.LIGHTGBM:
                if model_config.model_type == ModelType.CLASSIFICATION:
                    model = lgb.LGBMClassifier(**hyperparams)
                else:
                    model = lgb.LGBMRegressor(**hyperparams)
                    
            elif algorithm == AlgorithmType.LINEAR_REGRESSION:
                model = LinearRegression(**hyperparams)
                
            elif algorithm == AlgorithmType.LOGISTIC_REGRESSION:
                model = LogisticRegression(**hyperparams)
                
            elif algorithm == AlgorithmType.SVM:
                if model_config.model_type == ModelType.CLASSIFICATION:
                    model = SVC(**hyperparams)
                else:
                    model = SVR(**hyperparams)
                    
            elif algorithm == AlgorithmType.NEURAL_NETWORK and TENSORFLOW_AVAILABLE:
                model = self._create_neural_network(model_config)
                
            else:
                raise ValueError(f"지원하지 않는 알고리즘: {algorithm}")
            
            return model
            
        except Exception as e:
            logger.error(f"모델 생성 오류: {e}")
            raise
    
    def _create_neural_network(self, model_config: ModelConfig) -> keras.Model:
        """신경망 모델 생성"""
        try:
            model = models.Sequential()
            
            # 입력 레이어
            model.add(layers.Dense(128, activation='relu', input_shape=(len(model_config.feature_columns),)))
            model.add(layers.Dropout(0.3))
            
            # 은닉 레이어
            model.add(layers.Dense(64, activation='relu'))
            model.add(layers.Dropout(0.2))
            model.add(layers.Dense(32, activation='relu'))
            
            # 출력 레이어
            if model_config.model_type == ModelType.CLASSIFICATION:
                model.add(layers.Dense(1, activation='sigmoid'))
                model.compile(
                    optimizer='adam',
                    loss='binary_crossentropy',
                    metrics=['accuracy']
                )
            else:
                model.add(layers.Dense(1))
                model.compile(
                    optimizer='adam',
                    loss='mse',
                    metrics=['mae']
                )
            
            return model
            
        except Exception as e:
            logger.error(f"신경망 모델 생성 오류: {e}")
            raise
    
    def _optimize_hyperparameters(self, model: Any, data: Dict[str, Any], model_config: ModelConfig) -> Any:
        """하이퍼파라미터 최적화"""
        try:
            def objective(trial):
                # 하이퍼파라미터 범위 정의
                if isinstance(model, RandomForestClassifier) or isinstance(model, RandomForestRegressor):
                    params = {
                        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                        'max_depth': trial.suggest_int('max_depth', 3, 20),
                        'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                        'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
                    }
                elif isinstance(model, xgb.XGBClassifier) or isinstance(model, xgb.XGBRegressor):
                    params = {
                        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                        'max_depth': trial.suggest_int('max_depth', 3, 10),
                        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                    }
                else:
                    return model
                
                # 모델 생성 및 학습
                optimized_model = self._create_model_with_params(model_config, params)
                scores = cross_val_score(
                    optimized_model, 
                    data['X_train'], 
                    data['y_train'], 
                    cv=model_config.cross_validation_folds,
                    scoring='accuracy' if model_config.model_type == ModelType.CLASSIFICATION else 'r2'
                )
                
                return scores.mean()
            
            # Optuna로 최적화
            study = optuna.create_study(direction='maximize', sampler=TPESampler())
            study.optimize(objective, n_trials=model_config.optimization_trials)
            
            # 최적 하이퍼파라미터로 모델 재생성
            best_params = study.best_params
            model_config.hyperparameters.update(best_params)
            
            return self._create_model(model_config)
            
        except Exception as e:
            logger.error(f"하이퍼파라미터 최적화 오류: {e}")
            return model
    
    def _create_model_with_params(self, model_config: ModelConfig, params: Dict[str, Any]) -> Any:
        """파라미터로 모델 생성"""
        try:
            temp_config = ModelConfig(
                id=model_config.id,
                name=model_config.name,
                model_type=model_config.model_type,
                algorithm=model_config.algorithm,
                hyperparameters=params,
                feature_columns=model_config.feature_columns,
                target_column=model_config.target_column,
                created_at=model_config.created_at
            )
            
            return self._create_model(temp_config)
            
        except Exception as e:
            logger.error(f"파라미터로 모델 생성 오류: {e}")
            raise
    
    def _train_model_final(self, model: Any, data: Dict[str, Any], model_config: ModelConfig) -> Any:
        """최종 모델 학습"""
        try:
            if TENSORFLOW_AVAILABLE and isinstance(model, keras.Model):
                # 신경망 학습
                early_stopping = callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                )
                
                model.fit(
                    data['X_train'],
                    data['y_train'],
                    epochs=100,
                    batch_size=32,
                    validation_split=0.2,
                    callbacks=[early_stopping],
                    verbose=0
                )
            else:
                # 전통적 ML 모델 학습
                model.fit(data['X_train'], data['y_train'])
            
            return model
            
        except Exception as e:
            logger.error(f"모델 학습 오류: {e}")
            raise
    
    def _evaluate_model(self, model: Any, data: Dict[str, Any], model_config: ModelConfig) -> Dict[str, float]:
        """모델 평가"""
        try:
            y_pred = model.predict(data['X_test'])
            
            if model_config.model_type == ModelType.CLASSIFICATION:
                # 분류 모델 평가
                metrics = {
                    'accuracy': accuracy_score(data['y_test'], y_pred),
                    'precision': precision_score(data['y_test'], y_pred, average='weighted'),
                    'recall': recall_score(data['y_test'], y_pred, average='weighted'),
                    'f1_score': f1_score(data['y_test'], y_pred, average='weighted'),
                }
                
                # 이진 분류인 경우 ROC AUC 추가
                if len(np.unique(data['y_test'])) == 2:
                    try:
                        y_pred_proba = model.predict_proba(data['X_test'])[:, 1]
                        metrics['roc_auc'] = roc_auc_score(data['y_test'], y_pred_proba)
                    except:
                        pass
                        
            else:
                # 회귀 모델 평가
                metrics = {
                    'mse': mean_squared_error(data['y_test'], y_pred),
                    'rmse': np.sqrt(mean_squared_error(data['y_test'], y_pred)),
                    'mae': mean_absolute_error(data['y_test'], y_pred),
                    'r2_score': r2_score(data['y_test'], y_pred),
                }
            
            return metrics
            
        except Exception as e:
            logger.error(f"모델 평가 오류: {e}")
            raise
    
    def _calculate_feature_importance(self, model: Any, model_config: ModelConfig) -> Dict[str, float]:
        """특성 중요도 계산"""
        try:
            feature_importance = {}
            
            if hasattr(model, 'feature_importances_'):
                # 트리 기반 모델
                importance = model.feature_importances_
                feature_names = model_config.feature_columns
                
                for name, importance_value in zip(feature_names, importance):
                    feature_importance[name] = float(importance_value)
                    
            elif hasattr(model, 'coef_'):
                # 선형 모델
                coef = model.coef_[0] if len(model.coef_.shape) > 1 else model.coef_
                feature_names = model_config.feature_columns
                
                for name, coef_value in zip(feature_names, coef):
                    feature_importance[name] = float(abs(coef_value))
            
            return feature_importance
            
        except Exception as e:
            logger.error(f"특성 중요도 계산 오류: {e}")
            return {}
    
    def _save_model(self, model: Any, model_config: ModelConfig) -> Path:
        """모델 저장"""
        try:
            model_dir = self.models_dir / model_config.id
            model_dir.mkdir(exist_ok=True)
            
            model_path = model_dir / 'model.pkl'
            
            if TENSORFLOW_AVAILABLE and isinstance(model, keras.Model):
                # TensorFlow 모델 저장
                model.save(str(model_dir / 'model.h5'))
                # 메타데이터 저장
                with open(model_path, 'wb') as f:
                    pickle.dump({
                        'model_type': 'tensorflow',
                        'model_path': str(model_dir / 'model.h5'),
                        'config': model_config
                    }, f)
            else:
                # 전통적 ML 모델 저장
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
            
            return model_path
            
        except Exception as e:
            logger.error(f"모델 저장 오류: {e}")
            raise
    
    def _get_model_size(self, model_path: Path) -> int:
        """모델 크기 계산"""
        try:
            return model_path.stat().st_size
        except:
            return 0
    
    def _save_pipelines(self):
        """파이프라인 저장"""
        try:
            pipelines_data = [asdict(pipeline) for pipeline in self.pipelines.values()]
            
            with open(self.base_dir / 'pipelines.json', 'w') as f:
                json.dump(pipelines_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"파이프라인 저장 오류: {e}")
    
    def _save_results(self):
        """결과 저장"""
        try:
            results_data = [asdict(result) for result in self.results.values()]
            
            with open(self.results_dir / 'results.json', 'w') as f:
                json.dump(results_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"결과 저장 오류: {e}")
    
    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """파이프라인 상태 조회"""
        try:
            pipeline = self.pipelines.get(pipeline_id)
            if not pipeline:
                return {'error': '파이프라인을 찾을 수 없습니다'}
            
            results = []
            for model_config in pipeline.model_configs:
                result = self.results.get(model_config.id)
                if result:
                    results.append({
                        'model_id': model_config.id,
                        'model_name': model_config.name,
                        'status': 'completed',
                        'metrics': result.metrics,
                        'training_time': result.training_time
                    })
                else:
                    results.append({
                        'model_id': model_config.id,
                        'model_name': model_config.name,
                        'status': 'pending'
                    })
            
            return {
                'pipeline_id': pipeline_id,
                'name': pipeline.name,
                'status': 'completed' if all(r['status'] == 'completed' for r in results) else 'running',
                'models': results,
                'created_at': pipeline.created_at.isoformat() if pipeline.created_at else None
            }
            
        except Exception as e:
            logger.error(f"파이프라인 상태 조회 오류: {e}")
            return {'error': str(e)}
    
    def get_best_model(self, pipeline_id: str, metric: str = 'accuracy') -> Optional[TrainingResult]:
        """최고 성능 모델 조회"""
        try:
            pipeline = self.pipelines.get(pipeline_id)
            if not pipeline:
                return None
            
            best_result = None
            best_score = -1
            
            for model_config in pipeline.model_configs:
                result = self.results.get(model_config.id)
                if result and metric in result.metrics:
                    score = result.metrics[metric]
                    if score > best_score:
                        best_score = score
                        best_result = result
            
            return best_result
            
        except Exception as e:
            logger.error(f"최고 성능 모델 조회 오류: {e}")
            return None
    
    def destroy(self):
        """서비스 정리"""
        self.is_running = False
        self.training_queue.put(None)
        self.executor.shutdown()
        self.process_executor.shutdown()
        logger.info('ML 파이프라인 서비스 정리 완료')

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'base_dir': './ml_pipeline',
        'max_workers': 4,
        'process_workers': 2
    }
    
    # ML 파이프라인 생성
    pipeline = MLPipeline(config)
    
    # 파이프라인 생성
    pipeline_config = {
        'name': '고객 이탈 예측',
        'description': '고객 이탈을 예측하는 ML 파이프라인',
        'stages': [PipelineStage.DATA_PREPROCESSING, PipelineStage.MODEL_TRAINING, PipelineStage.MODEL_EVALUATION],
        'data_source': {
            'type': 'file',
            'path': './data/customer_churn.csv',
            'format': 'csv'
        },
        'evaluation_metrics': ['accuracy', 'precision', 'recall', 'f1_score']
    }
    
    pipeline_id = pipeline.create_pipeline(pipeline_config)
    
    # 모델 추가
    model_config = {
        'name': 'Random Forest',
        'model_type': 'classification',
        'algorithm': 'random_forest',
        'hyperparameters': {
            'n_estimators': 100,
            'max_depth': 10,
            'random_state': 42
        },
        'feature_columns': ['age', 'income', 'usage_frequency', 'support_calls'],
        'target_column': 'churned',
        'optimization_trials': 50
    }
    
    model_id = pipeline.add_model_to_pipeline(pipeline_id, model_config)
    
    # 파이프라인 실행
    result = pipeline.run_pipeline(pipeline_id, async_mode=False)
    print(f"파이프라인 실행 결과: {result}")
    
    # 최고 성능 모델 조회
    best_model = pipeline.get_best_model(pipeline_id, 'accuracy')
    if best_model:
        print(f"최고 성능 모델: {best_model.model_id}")
        print(f"정확도: {best_model.metrics['accuracy']:.4f}") 