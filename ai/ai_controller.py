import asyncio
import threading
import queue
import time
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

# AI 모듈들 import
try:
    from .prediction_engine import AIPredictionEngine
    from .nlp_processor import NLPProcessor
    from .anomaly_detection import AnomalyDetectionSystem
    from .model_manager import AIModelManager
    from .recommendation_system import RecommendationSystem
    AI_MODULES_AVAILABLE = True
except ImportError:
    AI_MODULES_AVAILABLE = False

@dataclass
class AIRequest:
    """AI 요청 데이터 클래스"""
    request_id: str
    request_type: str
    data: Any
    parameters: Dict
    priority: int = 1
    timestamp: str = None
    callback: Callable = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class AIResponse:
    """AI 응답 데이터 클래스"""
    request_id: str
    success: bool
    result: Any
    error_message: str = None
    processing_time: float = 0.0
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class AIController:
    """AI 시스템 통합 컨트롤러"""
    
    def __init__(self, config_path: str = "ai_controller_config.json"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        
        # AI 모듈들
        self.prediction_engine = None
        self.nlp_processor = None
        self.anomaly_detector = None
        self.model_manager = None
        self.recommendation_system = None
        
        # 처리 큐
        self.request_queue = queue.PriorityQueue()
        self.response_queue = queue.Queue()
        
        # 상태 관리
        self.is_running = False
        self.processing_thread = None
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_processing_time": 0.0,
            "active_requests": 0
        }
        
        # 워크플로우 정의
        self.workflows = {}
        
        # 초기화
        self._initialize_modules()
        self._setup_workflows()
    
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
            "modules": {
                "prediction_engine": {
                    "enabled": True,
                    "config_path": "ai_config.json"
                },
                "nlp_processor": {
                    "enabled": True,
                    "config_path": "nlp_config.json"
                },
                "anomaly_detection": {
                    "enabled": True,
                    "config_path": "anomaly_config.json"
                },
                "model_manager": {
                    "enabled": True,
                    "base_path": "models"
                },
                "recommendation_system": {
                    "enabled": True,
                    "config_path": "recommendation_config.json"
                }
            },
            "processing": {
                "max_concurrent_requests": 10,
                "request_timeout": 300,  # 5분
                "batch_size": 100,
                "enable_async": True
            },
            "monitoring": {
                "enable_metrics": True,
                "metrics_interval": 60,  # 1분
                "enable_health_checks": True,
                "health_check_interval": 300  # 5분
            },
            "workflows": {
                "auto_retry": True,
                "max_retries": 3,
                "retry_delay": 5  # 초
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('ai_controller')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_modules(self):
        """AI 모듈들 초기화"""
        if not AI_MODULES_AVAILABLE:
            self.logger.warning("AI 모듈들을 사용할 수 없습니다.")
            return
        
        modules_config = self.config["modules"]
        
        # 예측 엔진 초기화
        if modules_config["prediction_engine"]["enabled"]:
            try:
                self.prediction_engine = AIPredictionEngine(
                    modules_config["prediction_engine"]["config_path"]
                )
                self.logger.info("예측 엔진 초기화 완료")
            except Exception as e:
                self.logger.error(f"예측 엔진 초기화 실패: {e}")
        
        # NLP 프로세서 초기화
        if modules_config["nlp_processor"]["enabled"]:
            try:
                self.nlp_processor = NLPProcessor(
                    modules_config["nlp_processor"]["config_path"]
                )
                self.logger.info("NLP 프로세서 초기화 완료")
            except Exception as e:
                self.logger.error(f"NLP 프로세서 초기화 실패: {e}")
        
        # 이상 탐지 시스템 초기화
        if modules_config["anomaly_detection"]["enabled"]:
            try:
                self.anomaly_detector = AnomalyDetectionSystem(
                    modules_config["anomaly_detection"]["config_path"]
                )
                self.logger.info("이상 탐지 시스템 초기화 완료")
            except Exception as e:
                self.logger.error(f"이상 탐지 시스템 초기화 실패: {e}")
        
        # 모델 매니저 초기화
        if modules_config["model_manager"]["enabled"]:
            try:
                self.model_manager = AIModelManager(
                    modules_config["model_manager"]["base_path"]
                )
                self.logger.info("모델 매니저 초기화 완료")
            except Exception as e:
                self.logger.error(f"모델 매니저 초기화 실패: {e}")
        
        # 추천 시스템 초기화
        if modules_config["recommendation_system"]["enabled"]:
            try:
                self.recommendation_system = RecommendationSystem(
                    modules_config["recommendation_system"]["config_path"]
                )
                self.logger.info("추천 시스템 초기화 완료")
            except Exception as e:
                self.logger.error(f"추천 시스템 초기화 실패: {e}")
    
    def _setup_workflows(self):
        """워크플로우 설정"""
        # 텍스트 분석 워크플로우
        self.workflows["text_analysis"] = [
            "preprocess_text",
            "extract_keywords",
            "analyze_sentiment",
            "classify_text"
        ]
        
        # 예측 분석 워크플로우
        self.workflows["prediction_analysis"] = [
            "prepare_data",
            "train_models",
            "hyperparameter_tuning",
            "generate_report"
        ]
        
        # 이상 탐지 워크플로우
        self.workflows["anomaly_detection"] = [
            "detect_statistical_anomalies",
            "detect_ml_anomalies",
            "detect_time_series_anomalies",
            "generate_alert"
        ]
        
        # 추천 시스템 워크플로우
        self.workflows["recommendation"] = [
            "load_data",
            "train_collaborative_filtering",
            "train_content_based_filtering",
            "get_hybrid_recommendations"
        ]
    
    def start(self):
        """AI 컨트롤러 시작"""
        if self.is_running:
            self.logger.warning("AI 컨트롤러가 이미 실행 중입니다.")
            return
        
        self.is_running = True
        self.processing_thread = threading.Thread(target=self._processing_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        # 모니터링 시작
        if self.config["monitoring"]["enable_metrics"]:
            self._start_metrics_collection()
        
        if self.config["monitoring"]["enable_health_checks"]:
            self._start_health_checks()
        
        self.logger.info("AI 컨트롤러 시작됨")
    
    def stop(self):
        """AI 컨트롤러 중지"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.processing_thread:
            self.processing_thread.join(timeout=10)
        
        self.logger.info("AI 컨트롤러 중지됨")
    
    def _processing_loop(self):
        """요청 처리 루프"""
        while self.is_running:
            try:
                # 요청 대기
                priority, request = self.request_queue.get(timeout=1)
                self.stats["active_requests"] += 1
                
                # 요청 처리
                response = self._process_request(request)
                
                # 응답 큐에 추가
                self.response_queue.put(response)
                
                # 콜백 실행
                if request.callback:
                    try:
                        request.callback(response)
                    except Exception as e:
                        self.logger.error(f"콜백 실행 실패: {e}")
                
                self.stats["active_requests"] -= 1
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"요청 처리 중 오류: {e}")
                self.stats["active_requests"] -= 1
    
    def _process_request(self, request: AIRequest) -> AIResponse:
        """개별 요청 처리"""
        start_time = time.time()
        
        try:
            result = None
            
            if request.request_type == "text_analysis":
                result = self._process_text_analysis(request.data, request.parameters)
            elif request.request_type == "prediction":
                result = self._process_prediction(request.data, request.parameters)
            elif request.request_type == "anomaly_detection":
                result = self._process_anomaly_detection(request.data, request.parameters)
            elif request.request_type == "recommendation":
                result = self._process_recommendation(request.data, request.parameters)
            elif request.request_type == "workflow":
                result = self._process_workflow(request.data, request.parameters)
            else:
                raise ValueError(f"지원하지 않는 요청 타입: {request.request_type}")
            
            processing_time = time.time() - start_time
            
            # 통계 업데이트
            self.stats["total_requests"] += 1
            self.stats["successful_requests"] += 1
            self.stats["average_processing_time"] = (
                (self.stats["average_processing_time"] * (self.stats["successful_requests"] - 1) + processing_time) /
                self.stats["successful_requests"]
            )
            
            return AIResponse(
                request_id=request.request_id,
                success=True,
                result=result,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            # 통계 업데이트
            self.stats["total_requests"] += 1
            self.stats["failed_requests"] += 1
            
            self.logger.error(f"요청 처리 실패: {request.request_id} - {e}")
            
            return AIResponse(
                request_id=request.request_id,
                success=False,
                result=None,
                error_message=str(e),
                processing_time=processing_time
            )
    
    def _process_text_analysis(self, data: str, parameters: Dict) -> Dict:
        """텍스트 분석 처리"""
        if not self.nlp_processor:
            raise ValueError("NLP 프로세서가 초기화되지 않았습니다.")
        
        results = {}
        
        # 텍스트 전처리
        if parameters.get("preprocess", True):
            results["preprocessed_text"] = self.nlp_processor.preprocess_text(data)
        
        # 키워드 추출
        if parameters.get("extract_keywords", True):
            results["keywords"] = self.nlp_processor.extract_keywords(
                data, 
                method=parameters.get("keyword_method", "tfidf"),
                top_k=parameters.get("top_k", 10)
            )
        
        # 감정 분석
        if parameters.get("sentiment_analysis", True):
            results["sentiment"] = self.nlp_processor.analyze_sentiment(
                data, 
                method=parameters.get("sentiment_method", "vader")
            )
        
        # 텍스트 분류
        if parameters.get("text_classification", False) and self.nlp_processor.models:
            results["classification"] = self.nlp_processor.classify_text(data)
        
        # 개체명 추출
        if parameters.get("entity_extraction", True):
            results["entities"] = self.nlp_processor.extract_entities(data)
        
        return results
    
    def _process_prediction(self, data: pd.DataFrame, parameters: Dict) -> Dict:
        """예측 처리"""
        if not self.prediction_engine:
            raise ValueError("예측 엔진이 초기화되지 않았습니다.")
        
        target_column = parameters.get("target_column")
        task_type = parameters.get("task_type", "regression")
        
        if not target_column:
            raise ValueError("target_column이 필요합니다.")
        
        # 데이터 준비
        X, y, features = self.prediction_engine.prepare_data(data, target_column, task_type)
        
        results = {
            "features": features,
            "data_shape": X.shape
        }
        
        # 모델 훈련
        if parameters.get("train_models", True):
            model_results = self.prediction_engine.train_models(X, y, task_type)
            results["model_results"] = model_results
        
        # 하이퍼파라미터 튜닝
        if parameters.get("hyperparameter_tuning", False):
            model_name = parameters.get("tuning_model", "random_forest")
            tuning_result = self.prediction_engine.hyperparameter_tuning(X, y, model_name, task_type)
            results["tuning_result"] = tuning_result
        
        # 예측
        if parameters.get("make_prediction", False):
            prediction_data = parameters.get("prediction_data")
            if prediction_data is not None:
                pred = self.prediction_engine.predict(prediction_data, task_type=task_type)
                results["prediction"] = pred.tolist()
        
        # 리포트 생성
        if parameters.get("generate_report", True):
            report = self.prediction_engine.generate_report(task_type)
            results["report"] = report
        
        return results
    
    def _process_anomaly_detection(self, data: np.ndarray, parameters: Dict) -> Dict:
        """이상 탐지 처리"""
        if not self.anomaly_detector:
            raise ValueError("이상 탐지 시스템이 초기화되지 않았습니다.")
        
        methods = parameters.get("methods", ["statistical", "ml", "time_series"])
        
        results = {}
        
        # 통계적 이상 탐지
        if "statistical" in methods:
            stat_method = parameters.get("statistical_method", "z_score")
            stat_result = self.anomaly_detector.detect_statistical_anomalies(data, stat_method)
            results["statistical"] = stat_result
        
        # 머신러닝 기반 이상 탐지
        if "ml" in methods:
            ml_method = parameters.get("ml_method", "isolation_forest")
            if ml_method not in self.anomaly_detector.models:
                # 모델 훈련
                self.anomaly_detector.train_ml_anomaly_detector(data, ml_method)
            
            ml_result = self.anomaly_detector.detect_ml_anomalies(data, ml_method)
            results["ml"] = ml_result
        
        # 시계열 이상 탐지
        if "time_series" in methods:
            ts_result = self.anomaly_detector.detect_time_series_anomalies(data)
            results["time_series"] = ts_result
        
        # 종합 이상 탐지
        if parameters.get("comprehensive", True):
            comprehensive_result = self.anomaly_detector.comprehensive_anomaly_detection(data, methods)
            results["comprehensive"] = comprehensive_result
        
        # 알림 생성
        if parameters.get("generate_alert", True):
            alert_result = self.anomaly_detector.generate_alert(results.get("comprehensive", results))
            results["alert"] = alert_result
        
        return results
    
    def _process_recommendation(self, data: Dict, parameters: Dict) -> Dict:
        """추천 처리"""
        if not self.recommendation_system:
            raise ValueError("추천 시스템이 초기화되지 않았습니다.")
        
        user_id = data.get("user_id")
        if not user_id:
            raise ValueError("user_id가 필요합니다.")
        
        results = {}
        
        # 데이터 로드
        if "interactions_data" in data:
            interactions_df = pd.DataFrame(data["interactions_data"])
            items_data = pd.DataFrame(data.get("items_data", []))
            self.recommendation_system.load_data(interactions_df, item_data=items_data)
        
        # 모델 훈련
        if parameters.get("train_collaborative", True):
            cf_result = self.recommendation_system.train_collaborative_filtering("user_based")
            results["collaborative_training"] = cf_result
        
        if parameters.get("train_content_based", True):
            cb_result = self.recommendation_system.train_content_based_filtering()
            results["content_based_training"] = cb_result
        
        # 추천 생성
        n_recommendations = parameters.get("n_recommendations", 10)
        context = data.get("context")
        
        recommendations = self.recommendation_system.get_personalized_recommendations(
            user_id, context, n_recommendations
        )
        results["recommendations"] = recommendations
        
        # 상호작용 기록
        if "interaction" in data:
            interaction = data["interaction"]
            self.recommendation_system.record_interaction(
                user_id,
                interaction["item_id"],
                interaction.get("type", "view"),
                interaction.get("rating")
            )
        
        return results
    
    def _process_workflow(self, workflow_name: str, parameters: Dict) -> Dict:
        """워크플로우 처리"""
        if workflow_name not in self.workflows:
            raise ValueError(f"워크플로우를 찾을 수 없습니다: {workflow_name}")
        
        workflow_steps = self.workflows[workflow_name]
        results = {}
        
        for step in workflow_steps:
            try:
                if step == "preprocess_text":
                    results[step] = self.nlp_processor.preprocess_text(parameters.get("text", ""))
                elif step == "extract_keywords":
                    results[step] = self.nlp_processor.extract_keywords(parameters.get("text", ""))
                elif step == "analyze_sentiment":
                    results[step] = self.nlp_processor.analyze_sentiment(parameters.get("text", ""))
                elif step == "classify_text":
                    results[step] = self.nlp_processor.classify_text(parameters.get("text", ""))
                # 추가 워크플로우 단계들...
                
            except Exception as e:
                self.logger.error(f"워크플로우 단계 실패: {step} - {e}")
                results[f"{step}_error"] = str(e)
        
        return results
    
    def submit_request(self, request_type: str, data: Any, parameters: Dict = None, 
                      priority: int = 1, callback: Callable = None) -> str:
        """요청 제출"""
        if not self.is_running:
            raise RuntimeError("AI 컨트롤러가 실행되지 않았습니다.")
        
        request_id = f"req_{int(time.time() * 1000)}"
        
        request = AIRequest(
            request_id=request_id,
            request_type=request_type,
            data=data,
            parameters=parameters or {},
            priority=priority,
            callback=callback
        )
        
        # 우선순위 큐에 추가 (낮은 숫자가 높은 우선순위)
        self.request_queue.put((priority, request))
        
        self.logger.info(f"요청 제출: {request_id} ({request_type})")
        
        return request_id
    
    def get_response(self, timeout: float = 5.0) -> Optional[AIResponse]:
        """응답 가져오기"""
        try:
            return self.response_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_all_responses(self) -> List[AIResponse]:
        """모든 응답 가져오기"""
        responses = []
        while not self.response_queue.empty():
            responses.append(self.response_queue.get_nowait())
        return responses
    
    def _start_metrics_collection(self):
        """메트릭 수집 시작"""
        def collect_metrics():
            while self.is_running:
                try:
                    # 메트릭 수집 및 저장
                    metrics = {
                        "timestamp": datetime.now().isoformat(),
                        "stats": self.stats.copy(),
                        "queue_size": self.request_queue.qsize(),
                        "response_queue_size": self.response_queue.qsize()
                    }
                    
                    # 메트릭 저장 (파일 또는 데이터베이스)
                    self._save_metrics(metrics)
                    
                    time.sleep(self.config["monitoring"]["metrics_interval"])
                    
                except Exception as e:
                    self.logger.error(f"메트릭 수집 실패: {e}")
        
        metrics_thread = threading.Thread(target=collect_metrics)
        metrics_thread.daemon = True
        metrics_thread.start()
    
    def _start_health_checks(self):
        """헬스 체크 시작"""
        def health_check():
            while self.is_running:
                try:
                    health_status = self._check_health()
                    
                    if not health_status["healthy"]:
                        self.logger.warning(f"헬스 체크 실패: {health_status['issues']}")
                    
                    time.sleep(self.config["monitoring"]["health_check_interval"])
                    
                except Exception as e:
                    self.logger.error(f"헬스 체크 실패: {e}")
        
        health_thread = threading.Thread(target=health_check)
        health_thread.daemon = True
        health_thread.start()
    
    def _check_health(self) -> Dict[str, Any]:
        """헬스 체크 수행"""
        issues = []
        
        # 모듈 상태 확인
        if not self.prediction_engine:
            issues.append("prediction_engine_not_available")
        
        if not self.nlp_processor:
            issues.append("nlp_processor_not_available")
        
        if not self.anomaly_detector:
            issues.append("anomaly_detector_not_available")
        
        if not self.model_manager:
            issues.append("model_manager_not_available")
        
        if not self.recommendation_system:
            issues.append("recommendation_system_not_available")
        
        # 큐 상태 확인
        if self.request_queue.qsize() > 1000:
            issues.append("request_queue_overflow")
        
        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "timestamp": datetime.now().isoformat()
        }
    
    def _save_metrics(self, metrics: Dict):
        """메트릭 저장"""
        # 간단한 파일 기반 저장
        metrics_file = "ai_metrics.json"
        try:
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"메트릭 저장 실패: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return {
            "is_running": self.is_running,
            "stats": self.stats.copy(),
            "queue_sizes": {
                "request_queue": self.request_queue.qsize(),
                "response_queue": self.response_queue.qsize()
            },
            "modules": {
                "prediction_engine": self.prediction_engine is not None,
                "nlp_processor": self.nlp_processor is not None,
                "anomaly_detector": self.anomaly_detector is not None,
                "model_manager": self.model_manager is not None,
                "recommendation_system": self.recommendation_system is not None
            },
            "health": self._check_health(),
            "timestamp": datetime.now().isoformat()
        }
    
    def save_state(self, filepath: str):
        """상태 저장"""
        state = {
            "stats": self.stats,
            "config": self.config,
            "workflows": self.workflows,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"상태 저장 완료: {filepath}")
    
    def load_state(self, filepath: str):
        """상태 로드"""
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        self.stats = state.get("stats", self.stats)
        self.config.update(state.get("config", {}))
        self.workflows.update(state.get("workflows", {}))
        
        self.logger.info(f"상태 로드 완료: {filepath}")

# 사용 예시
if __name__ == "__main__":
    # AI 컨트롤러 초기화
    controller = AIController()
    
    # 컨트롤러 시작
    controller.start()
    
    # 텍스트 분석 요청
    text_data = "I love this product! It's amazing and works perfectly."
    request_id = controller.submit_request(
        "text_analysis",
        text_data,
        {
            "preprocess": True,
            "extract_keywords": True,
            "sentiment_analysis": True,
            "entity_extraction": True
        }
    )
    
    # 응답 대기
    response = controller.get_response(timeout=10.0)
    if response and response.success:
        print(f"텍스트 분석 결과: {response.result}")
    
    # 예측 요청
    import numpy as np
    import pandas as pd
    
    # 샘플 데이터
    np.random.seed(42)
    data = pd.DataFrame({
        'feature_1': np.random.randn(100),
        'feature_2': np.random.randn(100),
        'target': np.random.randn(100)
    })
    
    request_id = controller.submit_request(
        "prediction",
        data,
        {
            "target_column": "target",
            "task_type": "regression",
            "train_models": True,
            "generate_report": True
        }
    )
    
    # 응답 대기
    response = controller.get_response(timeout=30.0)
    if response and response.success:
        print(f"예측 결과: {response.result}")
    
    # 상태 조회
    status = controller.get_status()
    print(f"시스템 상태: {status}")
    
    # 컨트롤러 중지
    controller.stop() 