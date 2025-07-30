"""
모델 배포 및 관리 시스템
ML 모델의 배포, 버전 관리, A/B 테스트, 롤백을 지원하는 엔터프라이즈급 시스템
"""

import logging
import json
import yaml
import pickle
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import os
import shutil
import tempfile
from pathlib import Path
import uuid
import hashlib
import asyncio
import aiohttp
from aiohttp import web
import threading
import time
import queue
import subprocess
import docker
from docker.errors import DockerException
import requests
from requests.exceptions import RequestException
import psutil
import schedule

# ML 라이브러리
try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentStatus(Enum):
    """배포 상태"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    ACTIVE = "active"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    INACTIVE = "inactive"

class ModelVersion(Enum):
    """모델 버전"""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"

class ABTestType(Enum):
    """A/B 테스트 타입"""
    TRAFFIC_SPLIT = "traffic_split"
    FEATURE_FLAG = "feature_flag"
    GRADUAL_ROLLOUT = "gradual_rollout"

@dataclass
class DeployedModel:
    """배포된 모델"""
    id: str
    name: str
    version: str
    model_path: str
    endpoint_url: str
    status: DeploymentStatus
    deployment_config: Dict[str, Any]
    performance_metrics: Dict[str, float]
    created_at: datetime
    updated_at: datetime
    traffic_percentage: float = 100.0
    health_check_url: Optional[str] = None
    rollback_version: Optional[str] = None

@dataclass
class ABTest:
    """A/B 테스트"""
    id: str
    name: str
    description: str
    test_type: ABTestType
    model_a_id: str
    model_b_id: str
    traffic_split: Dict[str, float]  # {'A': 50, 'B': 50}
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool = True
    results: Dict[str, Any] = None
    created_at: datetime = None

@dataclass
class ModelEndpoint:
    """모델 엔드포인트"""
    id: str
    name: str
    url: str
    port: int
    health_check_url: str
    model_id: str
    is_active: bool = True
    created_at: datetime = None

class ModelDeploymentManager:
    """모델 배포 및 관리 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.deployed_models: Dict[str, DeployedModel] = {}
        self.ab_tests: Dict[str, ABTest] = {}
        self.endpoints: Dict[str, ModelEndpoint] = {}
        self.docker_client = None
        self.deployment_queue = queue.Queue()
        self.monitoring_thread = None
        self.is_running = False
        
        self._setup_directories()
        self._initialize_docker()
        self._load_existing_deployments()
        self._start_monitoring()
    
    def _setup_directories(self):
        """디렉토리 설정"""
        self.base_dir = Path(self.config.get('base_dir', './model_deployment'))
        self.models_dir = self.base_dir / 'models'
        self.endpoints_dir = self.base_dir / 'endpoints'
        self.logs_dir = self.base_dir / 'logs'
        self.docker_dir = self.base_dir / 'docker'
        self.monitoring_dir = self.base_dir / 'monitoring'
        
        for directory in [self.models_dir, self.endpoints_dir, self.logs_dir, self.docker_dir, self.monitoring_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _initialize_docker(self):
        """Docker 클라이언트 초기화"""
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker 클라이언트 초기화 완료")
        except DockerException as e:
            logger.warning(f"Docker 클라이언트 초기화 실패: {e}")
            self.docker_client = None
    
    def _load_existing_deployments(self):
        """기존 배포 정보 로드"""
        try:
            deployments_file = self.base_dir / 'deployments.json'
            if deployments_file.exists():
                with open(deployments_file, 'r') as f:
                    deployments_data = json.load(f)
                
                for deployment_data in deployments_data:
                    deployment = DeployedModel(**deployment_data)
                    self.deployed_models[deployment.id] = deployment
                
                logger.info(f"{len(self.deployed_models)}개의 배포된 모델 로드 완료")
        except Exception as e:
            logger.error(f"배포 정보 로드 오류: {e}")
    
    def _start_monitoring(self):
        """모니터링 시작"""
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_worker, daemon=True)
        self.monitoring_thread.start()
    
    def _monitoring_worker(self):
        """모니터링 워커"""
        while self.is_running:
            try:
                # 배포된 모델들의 상태 확인
                for model_id, model in self.deployed_models.items():
                    if model.status == DeploymentStatus.ACTIVE:
                        self._check_model_health(model)
                
                # A/B 테스트 결과 수집
                for test_id, test in self.ab_tests.items():
                    if test.is_active:
                        self._collect_ab_test_results(test)
                
                time.sleep(30)  # 30초마다 체크
                
            except Exception as e:
                logger.error(f"모니터링 워커 오류: {e}")
    
    def deploy_model(self, model_config: Dict[str, Any]) -> str:
        """모델 배포"""
        try:
            deployment_id = str(uuid.uuid4())
            
            # 모델 파일 경로 확인
            model_path = Path(model_config['model_path'])
            if not model_path.exists():
                raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {model_path}")
            
            # 배포 설정
            deployment_config = {
                'replicas': model_config.get('replicas', 1),
                'cpu_limit': model_config.get('cpu_limit', '1'),
                'memory_limit': model_config.get('memory_limit', '1Gi'),
                'port': model_config.get('port', 8080),
                'health_check_path': model_config.get('health_check_path', '/health'),
                'environment': model_config.get('environment', {}),
                'volumes': model_config.get('volumes', []),
                'network': model_config.get('network', 'bridge'),
            }
            
            # 모델 복사
            model_dest = self.models_dir / deployment_id / model_path.name
            model_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(model_path, model_dest)
            
            # Docker 이미지 빌드
            if self.docker_client:
                image_name = f"model-{deployment_id}"
                self._build_docker_image(image_name, model_dest, deployment_config)
            
            # 엔드포인트 생성
            endpoint_url = self._create_endpoint(deployment_id, deployment_config)
            
            # 배포된 모델 정보 생성
            deployed_model = DeployedModel(
                id=deployment_id,
                name=model_config['name'],
                version=model_config['version'],
                model_path=str(model_dest),
                endpoint_url=endpoint_url,
                status=DeploymentStatus.DEPLOYING,
                deployment_config=deployment_config,
                performance_metrics={},
                created_at=datetime.now(),
                updated_at=datetime.now(),
                health_check_url=f"{endpoint_url}{deployment_config['health_check_path']}"
            )
            
            self.deployed_models[deployment_id] = deployed_model
            
            # 배포 큐에 추가
            self.deployment_queue.put(deployment_id)
            
            # 배포 정보 저장
            self._save_deployments()
            
            logger.info(f"모델 배포 시작: {deployment_id}")
            return deployment_id
            
        except Exception as e:
            logger.error(f"모델 배포 오류: {e}")
            raise
    
    def _build_docker_image(self, image_name: str, model_path: Path, config: Dict[str, Any]):
        """Docker 이미지 빌드"""
        try:
            # Dockerfile 생성
            dockerfile_content = self._generate_dockerfile(model_path, config)
            dockerfile_path = self.docker_dir / f"Dockerfile.{image_name}"
            
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            
            # 이미지 빌드
            image, logs = self.docker_client.images.build(
                path=str(self.docker_dir),
                dockerfile=f"Dockerfile.{image_name}",
                tag=image_name,
                rm=True
            )
            
            logger.info(f"Docker 이미지 빌드 완료: {image_name}")
            
        except Exception as e:
            logger.error(f"Docker 이미지 빌드 오류: {e}")
            raise
    
    def _generate_dockerfile(self, model_path: Path, config: Dict[str, Any]) -> str:
        """Dockerfile 생성"""
        return f"""
FROM python:3.9-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 모델 파일 복사
COPY {model_path.name} /app/model.pkl

# 서비스 코드 복사
COPY model_service.py .

# 포트 노출
EXPOSE {config['port']}

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{config['port']}{config['health_check_path']} || exit 1

# 서비스 시작
CMD ["python", "model_service.py"]
"""
    
    def _create_endpoint(self, deployment_id: str, config: Dict[str, Any]) -> str:
        """엔드포인트 생성"""
        try:
            # 포트 할당
            port = self._allocate_port()
            
            # 엔드포인트 정보 생성
            endpoint = ModelEndpoint(
                id=str(uuid.uuid4()),
                name=f"endpoint-{deployment_id}",
                url=f"http://localhost:{port}",
                port=port,
                health_check_url=f"http://localhost:{port}{config['health_check_path']}",
                model_id=deployment_id,
                created_at=datetime.now()
            )
            
            self.endpoints[endpoint.id] = endpoint
            
            # Docker 컨테이너 실행
            if self.docker_client:
                self._run_docker_container(deployment_id, port, config)
            
            return endpoint.url
            
        except Exception as e:
            logger.error(f"엔드포인트 생성 오류: {e}")
            raise
    
    def _allocate_port(self) -> int:
        """포트 할당"""
        # 사용 중인 포트 확인
        used_ports = set()
        for endpoint in self.endpoints.values():
            used_ports.add(endpoint.port)
        
        # 사용 가능한 포트 찾기
        base_port = 8080
        for i in range(1000):
            port = base_port + i
            if port not in used_ports:
                return port
        
        raise RuntimeError("사용 가능한 포트가 없습니다")
    
    def _run_docker_container(self, deployment_id: str, port: int, config: Dict[str, Any]):
        """Docker 컨테이너 실행"""
        try:
            container = self.docker_client.containers.run(
                f"model-{deployment_id}",
                detach=True,
                ports={f"{config['port']}/tcp": port},
                environment=config.get('environment', {}),
                volumes=config.get('volumes', []),
                network=config.get('network', 'bridge'),
                name=f"model-{deployment_id}",
                restart_policy={"Name": "unless-stopped"}
            )
            
            logger.info(f"Docker 컨테이너 실행 완료: {container.id}")
            
        except Exception as e:
            logger.error(f"Docker 컨테이너 실행 오류: {e}")
            raise
    
    def _check_model_health(self, model: DeployedModel):
        """모델 헬스 체크"""
        try:
            if not model.health_check_url:
                return
            
            response = requests.get(model.health_check_url, timeout=10)
            
            if response.status_code == 200:
                # 성능 메트릭 업데이트
                health_data = response.json()
                model.performance_metrics.update(health_data.get('metrics', {}))
                model.updated_at = datetime.now()
            else:
                logger.warning(f"모델 헬스 체크 실패: {model.id}")
                
        except RequestException as e:
            logger.error(f"모델 헬스 체크 오류: {model.id} - {e}")
    
    def predict(self, model_id: str, data: Union[Dict, List, np.ndarray]) -> Any:
        """모델 예측"""
        try:
            model = self.deployed_models.get(model_id)
            if not model or model.status != DeploymentStatus.ACTIVE:
                raise ValueError(f"활성 모델을 찾을 수 없습니다: {model_id}")
            
            # A/B 테스트 확인
            ab_test = self._get_active_ab_test(model_id)
            if ab_test:
                return self._predict_with_ab_test(ab_test, data)
            
            # 일반 예측
            return self._make_prediction(model.endpoint_url, data)
            
        except Exception as e:
            logger.error(f"예측 오류: {e}")
            raise
    
    def _make_prediction(self, endpoint_url: str, data: Union[Dict, List, np.ndarray]) -> Any:
        """예측 요청"""
        try:
            # 데이터 전처리
            if isinstance(data, np.ndarray):
                data = data.tolist()
            elif isinstance(data, pd.DataFrame):
                data = data.to_dict('records')
            
            # API 요청
            response = requests.post(
                f"{endpoint_url}/predict",
                json={'data': data},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['prediction']
            else:
                raise RuntimeError(f"예측 요청 실패: {response.status_code}")
                
        except Exception as e:
            logger.error(f"예측 요청 오류: {e}")
            raise
    
    def create_ab_test(self, test_config: Dict[str, Any]) -> str:
        """A/B 테스트 생성"""
        try:
            test_id = str(uuid.uuid4())
            
            # 모델 존재 확인
            model_a = self.deployed_models.get(test_config['model_a_id'])
            model_b = self.deployed_models.get(test_config['model_b_id'])
            
            if not model_a or not model_b:
                raise ValueError("모델을 찾을 수 없습니다")
            
            ab_test = ABTest(
                id=test_id,
                name=test_config['name'],
                description=test_config.get('description', ''),
                test_type=ABTestType(test_config['test_type']),
                model_a_id=test_config['model_a_id'],
                model_b_id=test_config['model_b_id'],
                traffic_split=test_config['traffic_split'],
                start_date=datetime.now(),
                is_active=True,
                results={
                    'model_a': {'predictions': 0, 'accuracy': 0.0, 'latency': 0.0},
                    'model_b': {'predictions': 0, 'accuracy': 0.0, 'latency': 0.0}
                },
                created_at=datetime.now()
            )
            
            self.ab_tests[test_id] = ab_test
            self._save_ab_tests()
            
            logger.info(f"A/B 테스트 생성 완료: {test_id}")
            return test_id
            
        except Exception as e:
            logger.error(f"A/B 테스트 생성 오류: {e}")
            raise
    
    def _get_active_ab_test(self, model_id: str) -> Optional[ABTest]:
        """활성 A/B 테스트 조회"""
        for test in self.ab_tests.values():
            if (test.is_active and 
                (test.model_a_id == model_id or test.model_b_id == model_id)):
                return test
        return None
    
    def _predict_with_ab_test(self, ab_test: ABTest, data: Union[Dict, List, np.ndarray]) -> Any:
        """A/B 테스트를 통한 예측"""
        try:
            # 트래픽 분할
            import random
            split = random.random() * 100
            
            if split < ab_test.traffic_split.get('A', 50):
                # 모델 A 사용
                model = self.deployed_models[ab_test.model_a_id]
                result = self._make_prediction(model.endpoint_url, data)
                self._update_ab_test_results(ab_test, 'A', result)
            else:
                # 모델 B 사용
                model = self.deployed_models[ab_test.model_b_id]
                result = self._make_prediction(model.endpoint_url, data)
                self._update_ab_test_results(ab_test, 'B', result)
            
            return result
            
        except Exception as e:
            logger.error(f"A/B 테스트 예측 오류: {e}")
            raise
    
    def _update_ab_test_results(self, ab_test: ABTest, model_variant: str, prediction: Any):
        """A/B 테스트 결과 업데이트"""
        try:
            model_key = 'model_a' if model_variant == 'A' else 'model_b'
            ab_test.results[model_key]['predictions'] += 1
            
            # 여기서 실제 메트릭 계산 로직을 추가할 수 있습니다
            # 예: 정확도, 지연 시간 등
            
        except Exception as e:
            logger.error(f"A/B 테스트 결과 업데이트 오류: {e}")
    
    def _collect_ab_test_results(self, ab_test: ABTest):
        """A/B 테스트 결과 수집"""
        try:
            # 주기적으로 결과를 수집하고 분석
            # 실제 구현에서는 더 복잡한 메트릭 수집 로직이 필요합니다
            pass
            
        except Exception as e:
            logger.error(f"A/B 테스트 결과 수집 오류: {e}")
    
    def rollback_model(self, model_id: str) -> bool:
        """모델 롤백"""
        try:
            model = self.deployed_models.get(model_id)
            if not model:
                raise ValueError(f"모델을 찾을 수 없습니다: {model_id}")
            
            if not model.rollback_version:
                raise ValueError("롤백 버전이 없습니다")
            
            # 롤백 버전으로 복원
            rollback_model = self._get_model_by_version(model.name, model.rollback_version)
            if not rollback_model:
                raise ValueError(f"롤백 모델을 찾을 수 없습니다: {model.rollback_version}")
            
            # 현재 모델 비활성화
            model.status = DeploymentStatus.ROLLING_BACK
            
            # 롤백 모델 활성화
            rollback_model.status = DeploymentStatus.ACTIVE
            rollback_model.rollback_version = model.version  # 현재 버전을 롤백 버전으로 설정
            
            self._save_deployments()
            
            logger.info(f"모델 롤백 완료: {model_id} -> {model.rollback_version}")
            return True
            
        except Exception as e:
            logger.error(f"모델 롤백 오류: {e}")
            return False
    
    def _get_model_by_version(self, name: str, version: str) -> Optional[DeployedModel]:
        """버전으로 모델 조회"""
        for model in self.deployed_models.values():
            if model.name == name and model.version == version:
                return model
        return None
    
    def update_model_traffic(self, model_id: str, traffic_percentage: float) -> bool:
        """모델 트래픽 비율 업데이트"""
        try:
            model = self.deployed_models.get(model_id)
            if not model:
                raise ValueError(f"모델을 찾을 수 없습니다: {model_id}")
            
            model.traffic_percentage = max(0.0, min(100.0, traffic_percentage))
            model.updated_at = datetime.now()
            
            self._save_deployments()
            
            logger.info(f"모델 트래픽 업데이트: {model_id} -> {traffic_percentage}%")
            return True
            
        except Exception as e:
            logger.error(f"모델 트래픽 업데이트 오류: {e}")
            return False
    
    def get_deployment_status(self, model_id: str) -> Dict[str, Any]:
        """배포 상태 조회"""
        try:
            model = self.deployed_models.get(model_id)
            if not model:
                return {'error': '모델을 찾을 수 없습니다'}
            
            # 헬스 체크
            health_status = 'healthy'
            try:
                if model.health_check_url:
                    response = requests.get(model.health_check_url, timeout=5)
                    health_status = 'healthy' if response.status_code == 200 else 'unhealthy'
            except:
                health_status = 'unhealthy'
            
            return {
                'model_id': model_id,
                'name': model.name,
                'version': model.version,
                'status': model.status.value,
                'health_status': health_status,
                'endpoint_url': model.endpoint_url,
                'traffic_percentage': model.traffic_percentage,
                'performance_metrics': model.performance_metrics,
                'created_at': model.created_at.isoformat(),
                'updated_at': model.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"배포 상태 조회 오류: {e}")
            return {'error': str(e)}
    
    def get_ab_test_results(self, test_id: str) -> Dict[str, Any]:
        """A/B 테스트 결과 조회"""
        try:
            test = self.ab_tests.get(test_id)
            if not test:
                return {'error': 'A/B 테스트를 찾을 수 없습니다'}
            
            return {
                'test_id': test_id,
                'name': test.name,
                'description': test.description,
                'test_type': test.test_type.value,
                'model_a_id': test.model_a_id,
                'model_b_id': test.model_b_id,
                'traffic_split': test.traffic_split,
                'is_active': test.is_active,
                'results': test.results,
                'start_date': test.start_date.isoformat(),
                'end_date': test.end_date.isoformat() if test.end_date else None
            }
            
        except Exception as e:
            logger.error(f"A/B 테스트 결과 조회 오류: {e}")
            return {'error': str(e)}
    
    def stop_ab_test(self, test_id: str) -> bool:
        """A/B 테스트 중지"""
        try:
            test = self.ab_tests.get(test_id)
            if not test:
                raise ValueError(f"A/B 테스트를 찾을 수 없습니다: {test_id}")
            
            test.is_active = False
            test.end_date = datetime.now()
            
            self._save_ab_tests()
            
            logger.info(f"A/B 테스트 중지 완료: {test_id}")
            return True
            
        except Exception as e:
            logger.error(f"A/B 테스트 중지 오류: {e}")
            return False
    
    def _save_deployments(self):
        """배포 정보 저장"""
        try:
            deployments_data = [asdict(model) for model in self.deployed_models.values()]
            
            with open(self.base_dir / 'deployments.json', 'w') as f:
                json.dump(deployments_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"배포 정보 저장 오류: {e}")
    
    def _save_ab_tests(self):
        """A/B 테스트 정보 저장"""
        try:
            tests_data = [asdict(test) for test in self.ab_tests.values()]
            
            with open(self.base_dir / 'ab_tests.json', 'w') as f:
                json.dump(tests_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"A/B 테스트 정보 저장 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        self.is_running = False
        
        # Docker 컨테이너 정리
        if self.docker_client:
            try:
                for model in self.deployed_models.values():
                    container_name = f"model-{model.id}"
                    try:
                        container = self.docker_client.containers.get(container_name)
                        container.stop()
                        container.remove()
                    except:
                        pass
            except Exception as e:
                logger.error(f"Docker 컨테이너 정리 오류: {e}")
        
        logger.info('모델 배포 관리 서비스 정리 완료')

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'base_dir': './model_deployment',
        'docker_enabled': True
    }
    
    # 모델 배포 관리자 생성
    deployment_manager = ModelDeploymentManager(config)
    
    # 모델 배포
    model_config = {
        'name': '고객 이탈 예측',
        'version': '1.0.0',
        'model_path': './ml_pipeline/models/model.pkl',
        'replicas': 2,
        'cpu_limit': '1',
        'memory_limit': '1Gi',
        'port': 8080
    }
    
    deployment_id = deployment_manager.deploy_model(model_config)
    print(f"모델 배포 완료: {deployment_id}")
    
    # 예측
    data = {
        'age': 35,
        'income': 50000,
        'usage_frequency': 10,
        'support_calls': 2
    }
    
    prediction = deployment_manager.predict(deployment_id, data)
    print(f"예측 결과: {prediction}")
    
    # 배포 상태 조회
    status = deployment_manager.get_deployment_status(deployment_id)
    print(f"배포 상태: {status}") 