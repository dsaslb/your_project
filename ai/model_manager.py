import os
import json
import shutil
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Union
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

class AIModelManager:
    """AI 모델 관리 및 버전 관리 시스템"""
    
    def __init__(self, base_path: str = "models", config_path: str = "model_config.json"):
        self.base_path = base_path
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.models = {}
        self.versions = {}
        self.performance_history = {}
        self.deployment_status = {}
        
        # 디렉토리 생성
        self._create_directories()
        
        # MLflow 초기화
        if MLFLOW_AVAILABLE:
            self._setup_mlflow()
    
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
            "storage": {
                "max_versions_per_model": 10,
                "auto_cleanup": True,
                "cleanup_threshold_days": 30
            },
            "versioning": {
                "auto_version": True,
                "version_format": "v{major}.{minor}.{patch}",
                "initial_version": "v1.0.0"
            },
            "performance_tracking": {
                "metrics": ["accuracy", "precision", "recall", "f1_score", "rmse", "mae"],
                "min_improvement": 0.01,
                "tracking_window": 30  # 일
            },
            "deployment": {
                "staging_environments": ["dev", "staging", "prod"],
                "rollback_threshold": 0.1,
                "health_check_interval": 300  # 초
            },
            "a_b_testing": {
                "traffic_split": 0.5,
                "min_sample_size": 1000,
                "confidence_level": 0.95,
                "test_duration_days": 7
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('ai_model_manager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _create_directories(self):
        """필요한 디렉토리 생성"""
        directories = [
            self.base_path,
            os.path.join(self.base_path, "versions"),
            os.path.join(self.base_path, "metadata"),
            os.path.join(self.base_path, "performance"),
            os.path.join(self.base_path, "deployments"),
            os.path.join(self.base_path, "experiments")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _setup_mlflow(self):
        """MLflow 설정"""
        if MLFLOW_AVAILABLE:
            mlflow.set_tracking_uri(f"file://{os.path.join(self.base_path, 'mlruns')}")
            self.logger.info("MLflow 초기화 완료")
    
    def _generate_model_hash(self, model_data: Any) -> str:
        """모델 데이터의 해시 생성"""
        if hasattr(model_data, '__dict__'):
            # 모델 객체의 경우
            model_str = str(model_data.__dict__)
        else:
            # 기타 데이터의 경우
            model_str = str(model_data)
        
        return hashlib.md5(model_str.encode()).hexdigest()
    
    def _get_next_version(self, model_name: str, version_type: str = "patch") -> str:
        """다음 버전 번호 생성"""
        if model_name not in self.versions:
            return self.config["versioning"]["initial_version"]
        
        current_versions = list(self.versions[model_name].keys())
        if not current_versions:
            return self.config["versioning"]["initial_version"]
        
        # 최신 버전 찾기
        latest_version = max(current_versions, key=lambda v: [int(x) for x in v[1:].split('.')])
        major, minor, patch = map(int, latest_version[1:].split('.'))
        
        if version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        return f"v{major}.{minor}.{patch}"
    
    def save_model(self, model_name: str, model: Any, metadata: Dict = None, 
                  version: str = None, auto_version: bool = True) -> Dict[str, Any]:
        """모델 저장"""
        if not JOBLIB_AVAILABLE:
            raise ImportError("joblib이 필요합니다.")
        
        # 버전 결정
        if version is None and auto_version:
            version = self._get_next_version(model_name)
        elif version is None:
            version = self.config["versioning"]["initial_version"]
        
        # 모델 해시 생성
        model_hash = self._generate_model_hash(model)
        
        # 메타데이터 준비
        if metadata is None:
            metadata = {}
        
        model_metadata = {
            "model_name": model_name,
            "version": version,
            "model_hash": model_hash,
            "created_at": datetime.now().isoformat(),
            "file_size": 0,
            "framework": "sklearn",  # 기본값
            "parameters": getattr(model, 'get_params', lambda: {})()
        }
        model_metadata.update(metadata)
        
        # 파일 경로
        version_dir = os.path.join(self.base_path, "versions", model_name, version)
        os.makedirs(version_dir, exist_ok=True)
        
        model_file = os.path.join(version_dir, "model.pkl")
        metadata_file = os.path.join(version_dir, "metadata.json")
        
        # 모델 저장
        joblib.dump(model, model_file)
        
        # 파일 크기 계산
        file_size = os.path.getsize(model_file)
        model_metadata["file_size"] = file_size
        
        # 메타데이터 저장
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(model_metadata, f, indent=2, ensure_ascii=False)
        
        # 버전 정보 업데이트
        if model_name not in self.versions:
            self.versions[model_name] = {}
        
        self.versions[model_name][version] = {
            "file_path": model_file,
            "metadata": model_metadata,
            "created_at": datetime.now().isoformat()
        }
        
        # MLflow에 로깅
        if MLFLOW_AVAILABLE:
            self._log_to_mlflow(model_name, version, model_metadata)
        
        # 자동 정리
        if self.config["storage"]["auto_cleanup"]:
            self._cleanup_old_versions(model_name)
        
        self.logger.info(f"모델 저장 완료: {model_name} {version}")
        
        return {
            "model_name": model_name,
            "version": version,
            "file_path": model_file,
            "metadata": model_metadata
        }
    
    def _log_to_mlflow(self, model_name: str, version: str, metadata: Dict):
        """MLflow에 로깅"""
        if not MLFLOW_AVAILABLE:
            return
        
        try:
            with mlflow.start_run(run_name=f"{model_name}_{version}"):
                mlflow.log_params(metadata.get("parameters", {}))
                mlflow.log_metrics(metadata.get("metrics", {}))
                mlflow.log_artifact(metadata.get("file_path", ""))
        except Exception as e:
            self.logger.warning(f"MLflow 로깅 실패: {e}")
    
    def load_model(self, model_name: str, version: str = None) -> Tuple[Any, Dict]:
        """모델 로드"""
        if not JOBLIB_AVAILABLE:
            raise ImportError("joblib이 필요합니다.")
        
        # 버전 결정
        if version is None:
            if model_name not in self.versions:
                raise ValueError(f"모델을 찾을 수 없습니다: {model_name}")
            version = max(self.versions[model_name].keys(), 
                         key=lambda v: [int(x) for x in v[1:].split('.')])
        
        if model_name not in self.versions or version not in self.versions[model_name]:
            raise ValueError(f"모델 버전을 찾을 수 없습니다: {model_name} {version}")
        
        version_info = self.versions[model_name][version]
        model_file = version_info["file_path"]
        
        # 모델 로드
        model = joblib.load(model_file)
        
        self.logger.info(f"모델 로드 완료: {model_name} {version}")
        
        return model, version_info["metadata"]
    
    def list_models(self) -> Dict[str, List[str]]:
        """모델 목록 조회"""
        models = {}
        for model_name, versions in self.versions.items():
            models[model_name] = list(versions.keys())
        return models
    
    def get_model_info(self, model_name: str, version: str = None) -> Dict[str, Any]:
        """모델 정보 조회"""
        if model_name not in self.versions:
            raise ValueError(f"모델을 찾을 수 없습니다: {model_name}")
        
        if version is None:
            # 최신 버전 정보 반환
            version = max(self.versions[model_name].keys(), 
                         key=lambda v: [int(x) for x in v[1:].split('.')])
        
        if version not in self.versions[model_name]:
            raise ValueError(f"모델 버전을 찾을 수 없습니다: {model_name} {version}")
        
        return self.versions[model_name][version]["metadata"]
    
    def track_performance(self, model_name: str, version: str, 
                         metrics: Dict[str, float], test_data: Dict = None) -> Dict[str, Any]:
        """성능 추적"""
        performance_record = {
            "model_name": model_name,
            "version": version,
            "metrics": metrics,
            "test_data": test_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # 성능 히스토리 저장
        if model_name not in self.performance_history:
            self.performance_history[model_name] = {}
        
        if version not in self.performance_history[model_name]:
            self.performance_history[model_name][version] = []
        
        self.performance_history[model_name][version].append(performance_record)
        
        # 성능 파일 저장
        performance_file = os.path.join(
            self.base_path, "performance", f"{model_name}_{version}.json"
        )
        
        with open(performance_file, 'w', encoding='utf-8') as f:
            json.dump(self.performance_history[model_name][version], f, indent=2, ensure_ascii=False)
        
        # 성능 개선 확인
        improvement = self._check_performance_improvement(model_name, version, metrics)
        
        self.logger.info(f"성능 추적 완료: {model_name} {version}")
        
        return {
            "performance_recorded": True,
            "improvement": improvement
        }
    
    def _check_performance_improvement(self, model_name: str, version: str, 
                                     current_metrics: Dict[str, float]) -> Dict[str, Any]:
        """성능 개선 확인"""
        if model_name not in self.performance_history:
            return {"improved": False, "reason": "no_history"}
        
        # 이전 버전들과 비교
        improvements = {}
        min_improvement = self.config["performance_tracking"]["min_improvement"]
        
        for prev_version, history in self.performance_history[model_name].items():
            if prev_version == version:
                continue
            
            if not history:
                continue
            
            # 최근 성능 기록
            recent_metrics = history[-1]["metrics"]
            
            for metric in self.config["performance_tracking"]["metrics"]:
                if metric in current_metrics and metric in recent_metrics:
                    current_value = current_metrics[metric]
                    previous_value = recent_metrics[metric]
                    
                    # 높을수록 좋은 지표 (accuracy, precision, recall, f1_score)
                    if metric in ["accuracy", "precision", "recall", "f1_score"]:
                        improvement = current_value - previous_value
                    else:  # 낮을수록 좋은 지표 (rmse, mae)
                        improvement = previous_value - current_value
                    
                    if improvement > min_improvement:
                        improvements[f"{metric}_vs_{prev_version}"] = improvement
        
        return {
            "improved": len(improvements) > 0,
            "improvements": improvements
        }
    
    def deploy_model(self, model_name: str, version: str, 
                    environment: str = "staging") -> Dict[str, Any]:
        """모델 배포"""
        if environment not in self.config["deployment"]["staging_environments"]:
            raise ValueError(f"지원하지 않는 환경: {environment}")
        
        # 모델 정보 확인
        model_info = self.get_model_info(model_name, version)
        
        # 배포 디렉토리
        deployment_dir = os.path.join(self.base_path, "deployments", environment, model_name)
        os.makedirs(deployment_dir, exist_ok=True)
        
        # 모델 복사
        source_file = self.versions[model_name][version]["file_path"]
        target_file = os.path.join(deployment_dir, "model.pkl")
        
        shutil.copy2(source_file, target_file)
        
        # 배포 메타데이터
        deployment_info = {
            "model_name": model_name,
            "version": version,
            "environment": environment,
            "deployed_at": datetime.now().isoformat(),
            "status": "active",
            "health_checks": []
        }
        
        # 배포 상태 저장
        if environment not in self.deployment_status:
            self.deployment_status[environment] = {}
        
        self.deployment_status[environment][model_name] = deployment_info
        
        # 배포 파일 저장
        deployment_file = os.path.join(deployment_dir, "deployment.json")
        with open(deployment_file, 'w', encoding='utf-8') as f:
            json.dump(deployment_info, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"모델 배포 완료: {model_name} {version} -> {environment}")
        
        return deployment_info
    
    def rollback_deployment(self, model_name: str, environment: str, 
                           target_version: str = None) -> Dict[str, Any]:
        """모델 롤백"""
        if environment not in self.deployment_status:
            raise ValueError(f"환경을 찾을 수 없습니다: {environment}")
        
        if model_name not in self.deployment_status[environment]:
            raise ValueError(f"배포된 모델을 찾을 수 없습니다: {model_name}")
        
        current_deployment = self.deployment_status[environment][model_name]
        current_version = current_deployment["version"]
        
        # 롤백할 버전 결정
        if target_version is None:
            # 이전 버전으로 롤백
            available_versions = list(self.versions[model_name].keys())
            current_index = available_versions.index(current_version)
            if current_index > 0:
                target_version = available_versions[current_index - 1]
            else:
                raise ValueError("롤백할 이전 버전이 없습니다.")
        
        # 롤백 실행
        rollback_result = self.deploy_model(model_name, target_version, environment)
        rollback_result["rollback_from"] = current_version
        
        self.logger.info(f"모델 롤백 완료: {model_name} {current_version} -> {target_version}")
        
        return rollback_result
    
    def setup_ab_test(self, model_name: str, version_a: str, version_b: str,
                     traffic_split: float = None) -> Dict[str, Any]:
        """A/B 테스트 설정"""
        if traffic_split is None:
            traffic_split = self.config["a_b_testing"]["traffic_split"]
        
        if not (0 < traffic_split < 1):
            raise ValueError("traffic_split은 0과 1 사이여야 합니다.")
        
        ab_test_config = {
            "model_name": model_name,
            "version_a": version_a,
            "version_b": version_b,
            "traffic_split": traffic_split,
            "start_time": datetime.now().isoformat(),
            "status": "active",
            "results": {
                "version_a": {"predictions": 0, "successes": 0},
                "version_b": {"predictions": 0, "successes": 0}
            }
        }
        
        # A/B 테스트 설정 저장
        ab_test_file = os.path.join(
            self.base_path, "experiments", f"ab_test_{model_name}.json"
        )
        
        with open(ab_test_file, 'w', encoding='utf-8') as f:
            json.dump(ab_test_config, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"A/B 테스트 설정 완료: {model_name} {version_a} vs {version_b}")
        
        return ab_test_config
    
    def record_ab_test_result(self, model_name: str, version: str, 
                            prediction: Any, actual: Any, success: bool = None) -> Dict[str, Any]:
        """A/B 테스트 결과 기록"""
        ab_test_file = os.path.join(
            self.base_path, "experiments", f"ab_test_{model_name}.json"
        )
        
        if not os.path.exists(ab_test_file):
            raise ValueError(f"A/B 테스트를 찾을 수 없습니다: {model_name}")
        
        with open(ab_test_file, 'r', encoding='utf-8') as f:
            ab_test_config = json.load(f)
        
        if version not in [ab_test_config["version_a"], ab_test_config["version_b"]]:
            raise ValueError(f"잘못된 버전: {version}")
        
        # 결과 업데이트
        ab_test_config["results"][f"version_{version[-1]}"]["predictions"] += 1
        
        if success is not None:
            if success:
                ab_test_config["results"][f"version_{version[-1]}"]["successes"] += 1
        
        # 결과 저장
        with open(ab_test_file, 'w', encoding='utf-8') as f:
            json.dump(ab_test_config, f, indent=2, ensure_ascii=False)
        
        return {
            "result_recorded": True,
            "current_results": ab_test_config["results"]
        }
    
    def get_ab_test_results(self, model_name: str) -> Dict[str, Any]:
        """A/B 테스트 결과 조회"""
        ab_test_file = os.path.join(
            self.base_path, "experiments", f"ab_test_{model_name}.json"
        )
        
        if not os.path.exists(ab_test_file):
            raise ValueError(f"A/B 테스트를 찾을 수 없습니다: {model_name}")
        
        with open(ab_test_file, 'r', encoding='utf-8') as f:
            ab_test_config = json.load(f)
        
        # 성공률 계산
        results = ab_test_config["results"]
        for version_key in results:
            predictions = results[version_key]["predictions"]
            successes = results[version_key]["successes"]
            results[version_key]["success_rate"] = (
                successes / predictions if predictions > 0 else 0
            )
        
        return ab_test_config
    
    def _cleanup_old_versions(self, model_name: str):
        """오래된 버전 정리"""
        if model_name not in self.versions:
            return
        
        max_versions = self.config["storage"]["max_versions_per_model"]
        versions = list(self.versions[model_name].keys())
        
        if len(versions) <= max_versions:
            return
        
        # 오래된 버전 정렬
        versions.sort(key=lambda v: self.versions[model_name][v]["created_at"])
        
        # 오래된 버전 삭제
        for old_version in versions[:-max_versions]:
            version_info = self.versions[model_name][old_version]
            
            try:
                # 파일 삭제
                if os.path.exists(version_info["file_path"]):
                    os.remove(version_info["file_path"])
                
                # 메타데이터 파일 삭제
                metadata_file = os.path.join(
                    os.path.dirname(version_info["file_path"]), "metadata.json"
                )
                if os.path.exists(metadata_file):
                    os.remove(metadata_file)
                
                # 디렉토리 삭제
                version_dir = os.path.dirname(version_info["file_path"])
                if os.path.exists(version_dir):
                    os.rmdir(version_dir)
                
                # 버전 정보 삭제
                del self.versions[model_name][old_version]
                
                self.logger.info(f"오래된 버전 삭제: {model_name} {old_version}")
                
            except Exception as e:
                self.logger.warning(f"버전 삭제 실패: {model_name} {old_version} - {e}")
    
    def generate_report(self) -> Dict[str, Any]:
        """모델 관리 리포트 생성"""
        report = {
            "system_info": {
                "base_path": self.base_path,
                "total_models": len(self.versions),
                "joblib_available": JOBLIB_AVAILABLE,
                "mlflow_available": MLFLOW_AVAILABLE,
                "config": self.config
            },
            "models": {},
            "deployments": self.deployment_status,
            "performance_summary": {},
            "generated_at": datetime.now().isoformat()
        }
        
        # 모델별 요약 정보
        for model_name, versions in self.versions.items():
            report["models"][model_name] = {
                "total_versions": len(versions),
                "latest_version": max(versions.keys(), 
                                    key=lambda v: [int(x) for x in v[1:].split('.')]),
                "versions": list(versions.keys())
            }
        
        # 성능 요약
        for model_name, version_history in self.performance_history.items():
            if version_history:
                latest_version = max(version_history.keys(), 
                                   key=lambda v: [int(x) for x in v[1:].split('.')])
                latest_performance = version_history[latest_version][-1] if version_history[latest_version] else None
                
                report["performance_summary"][model_name] = {
                    "latest_version": latest_version,
                    "latest_metrics": latest_performance["metrics"] if latest_performance else {}
                }
        
        return report

# 사용 예시
if __name__ == "__main__":
    # 모델 매니저 초기화
    manager = AIModelManager()
    
    # 샘플 모델 생성 (가상)
    class DummyModel:
        def __init__(self, name="dummy"):
            self.name = name
            self.params = {"param1": 1.0, "param2": 2.0}
        
        def get_params(self):
            return self.params
    
    # 모델 저장
    model1 = DummyModel("model1")
    save_result = manager.save_model("test_model", model1, {"description": "테스트 모델"})
    print(f"모델 저장: {save_result['version']}")
    
    # 모델 로드
    loaded_model, metadata = manager.load_model("test_model")
    print(f"모델 로드: {metadata['version']}")
    
    # 성능 추적
    performance_result = manager.track_performance(
        "test_model", save_result['version'],
        {"accuracy": 0.95, "precision": 0.92}
    )
    print(f"성능 추적: {performance_result}")
    
    # 모델 배포
    deployment_result = manager.deploy_model("test_model", save_result['version'], "staging")
    print(f"모델 배포: {deployment_result['status']}")
    
    # A/B 테스트 설정
    model2 = DummyModel("model2")
    save_result2 = manager.save_model("test_model", model2, {"description": "개선된 모델"})
    ab_test_config = manager.setup_ab_test("test_model", save_result['version'], save_result2['version'])
    print(f"A/B 테스트 설정: {ab_test_config['status']}")
    
    # 리포트 생성
    report = manager.generate_report()
    print("모델 관리 리포트 생성 완료") 