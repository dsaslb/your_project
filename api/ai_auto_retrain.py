from extensions import redis_client  # pyright: ignore
from models_main import Order, User, Notification, SystemLog, db  # pyright: ignore
import os
import joblib
import pickle
from dataclasses import dataclass, asdict
import aiohttp
import asyncio
from collections import defaultdict
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import threading
import time
import json
import logging
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, current_app
from typing import Optional
query = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore
"""
AI 모델 자동 재훈련 시스템
성능 저하 감지 시 자동으로 모델을 재훈련하는 시스템
"""


# 데이터베이스 모델 import

logger = logging.getLogger(__name__)

ai_auto_retrain_bp = Blueprint('ai_auto_retrain', __name__)


# 1. 잘못된 타입힌트, 삼항연산자, 문법 오류, 정의되지 않은 클래스/변수, 잘못된 대입 등 표준 파이썬 문법으로 수정
# 2. ORM 동적 속성 접근 등 실행에 영향 없는 부분은 # pyright: ignore로 무시
# 3. 의미 없는 경고/실행에 영향 없는 부분은 무시 주석 추가
# 4. 전체 코드 스타일 일관성 유지
# 5. 주요 변경점마다 한글 설명 주석 추가

# --- 주요 클래스 정의 오류 수정 ---
# RetrainTask는 dataclass로만 정의, 서비스 클래스 별도 분리
@dataclass
class RetrainTask:
    model_name: Optional[str]
    triggered_at: Optional[str]
    reason: Optional[str]
    priority: Optional[str]
    status: str
    progress: float
    estimated_time: Optional[int]
    result: Optional[Dict[str, Any]]

class AIAutoRetrainService:
    """AI 자동 재훈련 서비스"""
    def __init__(self):
        self.retrain_queue = []
        self.active_tasks = {}
        self.completed_tasks = []
        self.retrain_config = {
            'auto_retrain_enabled': True,
            'drift_threshold': 0.2,
            'performance_threshold': 0.7,
            'max_concurrent_tasks': 2,
            'retrain_interval_hours': 24,
            'backup_models': True
        }
        self.model_backups = {}
        self._start_retrain_worker()

    def _start_retrain_worker(self):
        def retrain_worker():
            while True:
                try:
                    task_data = redis_client.brpop('ai_retrain_queue', timeout=1)
                    if task_data:
                        task_json = task_data[1]
                        if task_json is not None:
                            task = json.loads(task_json)
                            self._execute_retrain_task(task)
                        else:
                            logger.warning("task_data[1]가 None입니다. 재훈련 작업을 실행하지 않습니다.")  # noqa
                    self._cleanup_completed_tasks()
                    time.sleep(5)
                except Exception as e:
                    logger.error(f"재훈련 워커 오류: {e}")
                    time.sleep(10)
        # AI 자동 재훈련 워커 비활성화됨 (서버는 계속 실행)
        # thread = threading.Thread(target=retrain_worker, daemon=True)
        # thread.start()
        logger.info("AI 자동 재훈련 워커 비활성화됨")

    def _execute_retrain_task(self, task_data: Optional[Dict[str, Any]]):
        try:
            model_name = ''  # 미리 초기화
            if task_data is not None and task_data.get('model_name') is not None:
                model_name = str(task_data['model_name'])
            reason = str(task_data['reason']) if task_data is not None and task_data.get('reason') is not None else ''
            priority = str(task_data['priority']) if task_data is not None and task_data.get('priority') is not None else ''
            triggered_at = str(task_data['triggered_at']) if task_data is not None and task_data.get('triggered_at') is not None else ''
            task = RetrainTask(
                model_name=model_name,
                triggered_at=triggered_at,
                reason=reason,
                priority=priority,
                status='running',
                progress=0.0,
                estimated_time=None,
                result=None
            )
            if model_name:
                self.active_tasks[model_name] = task
            logger.info(f"재훈련 작업 시작: {model_name} ({reason})")
            if hasattr(self, 'retrain_config') and self.retrain_config.get('backup_models', False):
                if model_name:
                    self._backup_model(model_name)
            if model_name:
                result: dict[str, Any] = self._retrain_model(model_name, task)  # type: ignore
            else:
                result = {'success': False, 'error': 'model_name이 None입니다.'}
            if result is not None and result.get('success', False):
                task.status = 'completed'
            else:
                task.status = 'failed'
            task.progress = 100.0
            task.result = result
            self.completed_tasks.append(task)
            if model_name in self.active_tasks:
                del self.active_tasks[model_name]
            self._send_retrain_notification(task)
            logger.info(f"재훈련 작업 완료: {model_name} - {task.status}")
        except Exception as e:
            logger.error(f"재훈련 작업 실행 실패: {e}")
            model_name = locals().get('model_name', '')  # 혹시라도 unbound 방지
            if model_name and model_name in self.active_tasks:
                task = self.active_tasks[model_name]
                task.status = 'failed'
                task.result = {'error': str(e)}
                self.completed_tasks.append(task)
                del self.active_tasks[model_name]

    def _retrain_model(self, model_name: str, task: RetrainTask) -> dict[str, Any]:
        try:
            if 'sales_forecast' in model_name:
                return self._retrain_sales_model(task)
            elif 'inventory' in model_name:
                return self._retrain_inventory_model(task)
            elif 'customer' in model_name:
                return self._retrain_customer_model(task)
            elif 'staff' in model_name:
                return self._retrain_staff_model(task)
            else:
                return {'success': False, 'error': f'알 수 없는 모델: {model_name}'}
        except Exception as e:
            logger.error(f"모델 재훈련 실패 {model_name}: {e}")
            return {'success': False, 'error': str(e)}

    # --- 잘못된 타입힌트, 삼항연산자, 문법 오류 등 일괄 수정 ---
    def _retrain_sales_model(self, task: RetrainTask) -> Dict[str, Any]:
        try:
            task.progress = 10
            task.estimated_time = 15
            sales_data = self._collect_sales_data()
            if sales_data.empty:
                return {'success': False, 'error': '훈련 데이터가 부족합니다.'}
            task.progress = 40
            features = self._engineer_sales_features(sales_data)
            task.progress = 60
            model_result = self._train_sales_model(features)
            task.progress = 80
            performance = self._evaluate_model_performance(model_result)
            task.progress = 90
            self._save_model('sales_forecast', model_result['model'] if model_result is not None else None)
            task.progress = 100
            return {
                'success': True,
                'accuracy': model_result['accuracy'] if model_result is not None else None,
                'training_samples': len(sales_data),
                'performance': performance,
                'training_time': model_result['training_time'] if model_result is not None and 'training_time' in model_result else None
            }
        except Exception as e:
            logger.error(f"매출 모델 재훈련 실패: {e}")
            return {'success': False, 'error': str(e)}

    def _retrain_inventory_model(self, task: RetrainTask) -> Dict[str, Any]:
        try:
            task.progress = 10
            task.estimated_time = 10
            inventory_data = self._collect_inventory_data()
            if inventory_data.empty:
                return {'success': False, 'error': '재고 데이터가 부족합니다.'}
            task.progress = 60
            model_result = self._train_inventory_model(inventory_data)
            task.progress = 90
            self._save_model('inventory_prediction', model_result['model'] if model_result is not None else None)
            task.progress = 100
            return {
                'success': True,
                'accuracy': model_result['accuracy'] if model_result is not None else None,
                'training_samples': len(inventory_data),
                'training_time': model_result['training_time'] if model_result is not None and 'training_time' in model_result else None
            }
        except Exception as e:
            logger.error(f"재고 모델 재훈련 실패: {e}")
            return {'success': False, 'error': str(e)}

    def _retrain_customer_model(self, task: RetrainTask) -> Dict[str, Any]:
        try:
            task.progress = 10
            task.estimated_time = 12
            customer_data = self._collect_customer_data()
            if customer_data.empty:
                return {'success': False, 'error': '고객 데이터가 부족합니다.'}
            task.progress = 60
            model_result = self._train_customer_model(customer_data)
            task.progress = 90
            self._save_model('customer_churn', model_result['model'] if model_result is not None else None)
            task.progress = 100
            return {
                'success': True,
                'accuracy': model_result['accuracy'] if model_result is not None else None,
                'training_samples': len(customer_data),
                'training_time': model_result['training_time'] if model_result is not None and 'training_time' in model_result else None
            }
        except Exception as e:
            logger.error(f"고객 모델 재훈련 실패: {e}")
            return {'success': False, 'error': str(e)}

    def _retrain_staff_model(self, task: RetrainTask) -> Dict[str, Any]:
        try:
            task.progress = 10
            task.estimated_time = 8
            staff_data = self._collect_staff_data()
            if staff_data.empty:
                return {'success': False, 'error': '직원 데이터가 부족합니다.'}
            task.progress = 60
            model_result = self._train_staff_model(staff_data)
            task.progress = 90
            self._save_model('staff_scheduling', model_result['model'] if model_result is not None else None)
            task.progress = 100
            return {
                'success': True,
                'accuracy': model_result['accuracy'] if model_result is not None else None,
                'training_samples': len(staff_data),
                'training_time': model_result['training_time'] if model_result is not None and 'training_time' in model_result else None
            }
        except Exception as e:
            logger.error(f"직원 모델 재훈련 실패: {e}")
            return {'success': False, 'error': str(e)}

    def _collect_sales_data(self) -> pd.DataFrame:
        """매출 데이터 수집"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            orders = db.session.query(Order).filter(
                Order.created_at >= start_date,  # pyright: ignore
                Order.created_at <= end_date     # pyright: ignore
            ).all()
            data = []
            if orders is not None:
                for order in orders:
                    data.append({
                        'date': order.created_at.date(),  # pyright: ignore
                        'sales_amount': getattr(order, 'total_amount', 0),  # pyright: ignore
                        'order_count': 1,
                        'day_of_week': order.created_at.weekday(),  # pyright: ignore
                        'month': order.created_at.month,  # pyright: ignore
                        'season': self._get_season(order.created_at.month),
                        'holiday': self._is_holiday(order.created_at.date()),
                        'weather': self._get_weather_score(order.created_at.date())
                    })
            df = pd.DataFrame(data)
            daily_sales = df.groupby('date').agg({
                'sales_amount': 'sum',
                'order_count': 'sum',
                'day_of_week': 'first',
                'month': 'first',
                'season': 'first',
                'holiday': 'first',
                'weather': 'first'
            }).reset_index()
            daily_sales['previous_sales'] = daily_sales['sales_amount'].shift(1)
            daily_sales['sales_7d_avg'] = daily_sales['sales_amount'].rolling(7).mean()
            daily_sales['sales_30d_avg'] = daily_sales['sales_amount'].rolling(30).mean()
            return daily_sales.dropna()
        except Exception as e:
            logger.error(f"매출 데이터 수집 실패: {e}")
            return pd.DataFrame()

    def _collect_inventory_data(self) -> pd.DataFrame:
        """재고 데이터 수집"""
        try:
            from models_main import InventoryItem
            inventory_items = db.session.query(InventoryItem).all()
            data = []
            if inventory_items is not None:
                for item in inventory_items:
                    avg_daily_sales = np.random.randint(1, 10)
                    data.append({
                        'item_id': item.id,  # pyright: ignore
                        'item_name': item.name,  # pyright: ignore
                        'current_stock': item.current_stock,  # pyright: ignore
                        'avg_daily_sales': avg_daily_sales,
                        'lead_time_days': np.random.randint(1, 7),
                        'seasonality_factor': self._get_seasonality_factor(item.name)  # pyright: ignore
                    })
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"재고 데이터 수집 실패: {e}")
            return pd.DataFrame()

    def _collect_customer_data(self) -> pd.DataFrame:
        """고객 데이터 수집"""
        try:
            users = db.session.query(User).filter(
                User.role == 'customer'  # pyright: ignore
            ).all()
            data = []
            if users is not None:
                for user in users:
                    user_orders = db.session.query(Order).filter(
                        Order.user_id == user.id  # pyright: ignore
                    ).order_by(Order.created_at.desc()).all()
                    if user_orders:
                        visit_frequency = len(user_orders) / max(1, (datetime.now() - user_orders[-1].created_at).days)  # pyright: ignore
                        avg_order_value = sum(getattr(o, 'total_amount', 0) for o in user_orders) / len(user_orders)
                        last_visit_days = (datetime.now() - user_orders[0].created_at).days  # pyright: ignore
                        data.append({
                            'user_id': user.id,  # pyright: ignore
                            'visit_frequency': visit_frequency,
                            'avg_order_value': avg_order_value,
                            'last_visit_days': last_visit_days,
                            'total_orders': len(user_orders)
                        })
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"고객 데이터 수집 실패: {e}")
            return pd.DataFrame()

    def _collect_staff_data(self) -> pd.DataFrame:
        """직원 데이터 수집"""
        try:
            from models_main import Schedule
            # 쿼리에서 work_date 필터를 제거하고, 파이썬에서 work_date가 있는 경우만 필터링
            schedules = db.session.query(Schedule).all()
            data = []
            if schedules is not None:
                for schedule in schedules:
                    work_date = getattr(schedule, 'work_date', None)
                    if work_date is None:
                        continue
                    # 90일 이내만 필터링
                    if work_date < datetime.now() - timedelta(days=90):
                        continue
                    day_orders = db.session.query(Order).filter(
                        Order.created_at >= work_date,  # pyright: ignore
                        Order.created_at < work_date + timedelta(days=1)  # pyright: ignore
                    ).count()
                    data.append({
                        'date': work_date.date(),
                        'required_staff': getattr(schedule, 'required_staff', 1),
                        'actual_staff': getattr(schedule, 'actual_staff', 1),
                        'day_of_week': work_date.weekday(),
                        'month': work_date.month,
                        'season': self._get_season(work_date.month),
                        'historical_demand': day_orders
                    })
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"직원 데이터 수집 실패: {e}")
            return pd.DataFrame()

    def _engineer_sales_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """매출 특성 엔지니어링"""
        try:
            # 추가 특성 생성
            if df is not None:
                df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
                df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
                df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
                df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

            # 계절성 인코딩
            season_mapping = {'spring': 0, 'summer': 1, 'autumn': 2, 'winter': 3}
            df['season_encoded'] = df['season'].map(season_mapping)

            return df

        except Exception as e:
            logger.error(f"특성 엔지니어링 실패: {e}")
            return df  # noqa

    def _train_sales_model(self, features: pd.DataFrame) -> Dict[str, Any]:  # noqa
        """매출 모델 훈련"""
        try:
            from sklearn.ensemble import GradientBoostingRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error, r2_score
            import time

            start_time = time.time()

            # 특성 선택
            feature_cols = ['day_of_week', 'month', 'season_encoded', 'holiday', 'weather',
                            'previous_sales', 'sales_7d_avg', 'day_of_week_sin', 'day_of_week_cos',
                            'month_sin', 'month_cos']

            X = features[feature_cols] if features is not None else None
            y = features['sales_amount'] if features is not None else None

            # 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # 모델 훈련
            model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )

            model.fit(X_train, y_train)

            # 예측 및 평가
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            training_time = time.time() - start_time

            return {
                'model': model,
                'accuracy': r2,
                'mse': mse,
                'training_time': training_time,
                'feature_importance': dict(zip(feature_cols, model.feature_importances_))
            }

        except Exception as e:
            logger.error(f"매출 모델 훈련 실패: {e}")
            raise

    def _train_inventory_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """재고 모델 훈련"""
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error, r2_score
            import time

            start_time = time.time()

            # 특성 선택
            feature_cols = ['current_stock', 'avg_daily_sales', 'lead_time_days', 'seasonality_factor']

            X = df[feature_cols] if df is not None else None
            y = df['current_stock'] if df is not None else None  # 현재 재고를 타겟으로 사용

            # 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # 모델 훈련
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )

            model.fit(X_train, y_train)

            # 예측 및 평가
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            training_time = time.time() - start_time

            return {
                'model': model,
                'accuracy': r2,
                'mse': mse,
                'training_time': training_time,
                'feature_importance': dict(zip(feature_cols, model.feature_importances_))
            }

        except Exception as e:
            logger.error(f"재고 모델 훈련 실패: {e}")
            raise

    def _train_customer_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """고객 모델 훈련"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, classification_report
            import time

            start_time = time.time()

            # 특성 선택
            feature_cols = ['visit_frequency', 'avg_order_value', 'last_visit_days', 'total_orders']

            X = df[feature_cols] if df is not None else None

            # 이탈 여부 생성 (시뮬레이션)
            if df is not None:
                y = (df['last_visit_days'] > 30).astype(int)
            else:
                y = None

            # 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # 모델 훈련
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )

            model.fit(X_train, y_train)

            # 예측 및 평가
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            training_time = time.time() - start_time

            return {
                'model': model,
                'accuracy': accuracy,
                'training_time': training_time,
                'feature_importance': dict(zip(feature_cols, model.feature_importances_))
            }

        except Exception as e:
            logger.error(f"고객 모델 훈련 실패: {e}")
            raise

    def _train_staff_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """직원 모델 훈련"""
        try:
            from sklearn.linear_model import Ridge
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error, r2_score
            import time

            start_time = time.time()

            # 특성 선택
            feature_cols = ['day_of_week', 'month', 'season_encoded', 'historical_demand']

            # 계절성 인코딩
            season_mapping = {'spring': 0, 'summer': 1, 'autumn': 2, 'winter': 3}
            df['season_encoded'] = df['season'].map(season_mapping)

            X = df[feature_cols] if df is not None else None
            y = df['required_staff'] if df is not None else None

            # 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # 모델 훈련
            model = Ridge(alpha=1.0)
            model.fit(X_train, y_train)

            # 예측 및 평가
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            training_time = time.time() - start_time

            return {
                'model': model,
                'accuracy': r2,
                'mse': mse,
                'training_time': training_time
            }

        except Exception as e:
            logger.error(f"직원 모델 훈련 실패: {e}")
            raise

    def _evaluate_model_performance(self, model_result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """모델 성능 평가"""
        try:
            if model_result is None:
                return None
            return {
                'accuracy': model_result['accuracy'] if 'accuracy' in model_result else None,
                'training_time': model_result['training_time'] if 'training_time' in model_result else 0,
                'feature_importance': model_result['feature_importance'] if 'feature_importance' in model_result else {},
                'model_size': self._get_model_size(model_result['model'] if 'model' in model_result else None)
            }

        except Exception as e:
            logger.error(f"모델 성능 평가 실패: {e}")
            return {}

    def _get_model_size(self, model) -> int:
        """모델 크기 계산 (바이트)"""
        try:
            import sys
            return sys.getsizeof(pickle.dumps(model))
        except:
            return 0

    def _save_model(self, model_name: str, model):
        """모델 저장"""
        try:
            # 모델 디렉토리 생성
            model_dir = f"data/ai_models/{model_name}"
            os.makedirs(model_dir, exist_ok=True)

            # 모델 파일 저장
            model_path = f"{model_dir}/model.pkl"
            joblib.dump(model, model_path)

            # 메타데이터 저장
            metadata = {
                'model_name': model_name,
                'created_at': datetime.now().isoformat(),
                'version': '1.0'
            }

            metadata_path = f"{model_dir}/metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"모델 저장 완료: {model_path}")

        except Exception as e:
            logger.error(f"모델 저장 실패: {e}")
            raise

    def _backup_model(self,  model_name: str):
        """모델 백업"""
        try:
            model_dir = f"data/ai_models/{model_name}"
            backup_dir = f"data/ai_models/backups/{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            if os.path.exists(model_dir):
                import shutil
                shutil.copytree(model_dir, backup_dir)
                self.model_backups[model_name] = backup_dir

                logger.info(f"모델 백업 완료: {backup_dir}")

        except Exception as e:
            logger.error(f"모델 백업 실패: {e}")

    def _send_retrain_notification(self,  task: RetrainTask):
        try:
            if task.status == 'completed':
                title = f"AI 모델 재훈련 완료 - {task.model_name}"
                acc = 0.0
                if task.result and isinstance(task.result, dict):
                    acc = float(task.result.get('accuracy', 0))
                message = f"모델 재훈련이 성공적으로 완료되었습니다. 정확도: {acc * 100:.1f}%"
                priority = 'medium'
            else:
                title = f"AI 모델 재훈련 실패 - {task.model_name}"
                err = ''
                if task.result and isinstance(task.result, dict):
                    err = str(task.result.get('error', '알 수 없는 오류'))
                message = f"모델 재훈련에 실패했습니다: {err}"
                priority = 'high'
            # Notification 객체 대신 dict로 생성 후 db에 직접 추가 (파라미터 오류 방지)
            notification = dict(
                user_id=1,  # 관리자
                title=title,
                message=message,
                type='ai_retrain_completed',
                priority=priority,
                data=json.dumps(asdict(task))
            )
            db.session.add(Notification(**notification))
            db.session.commit()
        except Exception as e:
            logger.error(f"재훈련 알림 전송 실패: {e}")

    def _cleanup_completed_tasks(self):
        """완료된 작업 정리"""
        try:
            # 7일 이상 된 완료된 작업 제거
            cutoff_date = datetime.now() - timedelta(days=7)
            self.completed_tasks = [
                task for task in self.completed_tasks
                if datetime.fromisoformat(task.triggered_at) > cutoff_date
            ]

        except Exception as e:
            logger.error(f"완료된 작업 정리 실패: {e}")

    # 헬퍼 메서드들
    def _get_season(self,  month: int) -> str:
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'

    def _is_holiday(self, date) -> int:
        holidays = [1, 1, 3, 1, 5, 5, 6, 6, 8, 15, 10, 3, 10, 9, 12, 25]
        return 1 if date.month in holidays else 0

    def _get_weather_score(self, date) -> float:
        return np.random.uniform(0.3, 1.0)

    def _get_seasonality_factor(self, item_name: str) -> float:
        return np.random.uniform(0.8, 1.2)

    def get_retrain_status(self) -> Optional[Dict[str, Any]]:
        """재훈련 상태 조회"""
        try:
            return {
                'success': True,
                'active_tasks': len(self.active_tasks),
                'completed_tasks': len(self.completed_tasks),
                'config': self.retrain_config,
                'active_tasks_detail': [
                    {
                        'model_name': task.model_name,
                        'progress': task.progress,
                        'estimated_time': task.estimated_time,
                        'reason': task.reason
                    }
                    for task in self.active_tasks.values()
                ],
                'recent_completed': [
                    {
                        'model_name': task.model_name,
                        'status': task.status,
                        'completed_at': task.triggered_at,
                        'result': task.result
                    }
                    for task in self.completed_tasks[-5:]
                ]
            }
        except Exception as e:
            logger.error(f"재훈련 상태 조회 실패: {e}")
            return {'error': f'상태 조회 실패: {str(e)}'}


# 전역 서비스 인스턴스
ai_retrain_service = AIAutoRetrainService()

# API 엔드포인트들


@ai_auto_retrain_bp.route('/api/ai/retrain/status', methods=['GET'])
@login_required
def get_retrain_status():
    """재훈련 상태 조회"""
    try:
        result = ai_retrain_service.get_retrain_status()
        return jsonify(result)
    except Exception as e:
        logger.error(f"재훈련 상태 조회 API 오류: {e}")
        return jsonify({'error': '상태 조회에 실패했습니다.'}), 500


@ai_auto_retrain_bp.route('/api/ai/retrain/manual', methods=['POST'])
@login_required
def trigger_manual_retrain():
    """수동 재훈련 트리거"""
    try:
        data = request.get_json()
        model_name = data.get('model_name') if data else None

        if not model_name:
            return jsonify({'error': '모델명이 필요합니다.'}), 400

        # 재훈련 작업 생성
        retrain_task = {
            'model_name': model_name,
            'triggered_at': datetime.now().isoformat(),
            'reason': 'manual',
            'priority': 'medium'
        }

        # Redis에 작업 추가
        redis_client.lpush('ai_retrain_queue', json.dumps(retrain_task))

        return jsonify({
            'success': True,
            'message': f'{model_name} 모델 재훈련이 시작되었습니다.',
            'task_id': f"{model_name}_{int(time.time())}"
        })

    except Exception as e:
        logger.error(f"수동 재훈련 트리거 API 오류: {e}")
        return jsonify({'error': '재훈련 시작에 실패했습니다.'}), 500
