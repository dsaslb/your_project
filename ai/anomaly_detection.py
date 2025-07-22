import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional, Union
import json
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.neighbors import LocalOutlierFactor
    from sklearn.svm import OneClassSVM
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from scipy import stats
    from scipy.signal import find_peaks
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

class AnomalyDetectionSystem:
    """이상 탐지 및 패턴 인식 시스템"""
    
    def __init__(self, config_path: str = "anomaly_config.json"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.models = {}
        self.scalers = {}
        self.thresholds = {}
        self.patterns = {}
        self.detection_history = []
        
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
            "statistical_detection": {
                "z_score_threshold": 3.0,
                "iqr_multiplier": 1.5,
                "percentile_threshold": 0.95
            },
            "ml_detection": {
                "isolation_forest": {
                    "contamination": 0.1,
                    "random_state": 42
                },
                "local_outlier_factor": {
                    "contamination": 0.1,
                    "n_neighbors": 20
                },
                "one_class_svm": {
                    "nu": 0.1,
                    "kernel": "rbf"
                }
            },
            "time_series_detection": {
                "window_size": 10,
                "threshold_multiplier": 2.0,
                "min_anomaly_duration": 3
            },
            "pattern_detection": {
                "min_pattern_length": 3,
                "similarity_threshold": 0.8,
                "max_patterns": 100
            },
            "alerting": {
                "min_confidence": 0.7,
                "cooldown_period": 300,  # 5분
                "max_alerts_per_hour": 10
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('anomaly_detection')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def detect_statistical_anomalies(self, data: np.ndarray, method: str = "z_score") -> Dict[str, Any]:
        """통계적 이상 탐지"""
        if len(data) == 0:
            return {"anomalies": [], "scores": [], "method": method}
        
        anomalies = []
        scores = []
        
        if method == "z_score":
            # Z-score 기반 이상 탐지
            mean = np.mean(data)
            std = np.std(data)
            threshold = self.config["statistical_detection"]["z_score_threshold"]
            
            if std > 0:
                z_scores = np.abs((data - mean) / std)
                anomalies = z_scores > threshold
                scores = z_scores
            else:
                anomalies = np.zeros(len(data), dtype=bool)
                scores = np.zeros(len(data))
        
        elif method == "iqr":
            # IQR 기반 이상 탐지
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            multiplier = self.config["statistical_detection"]["iqr_multiplier"]
            
            lower_bound = q1 - multiplier * iqr
            upper_bound = q3 + multiplier * iqr
            
            anomalies = (data < lower_bound) | (data > upper_bound)
            scores = np.maximum((lower_bound - data) / iqr, (data - upper_bound) / iqr)
            scores = np.maximum(scores, 0)
        
        elif method == "percentile":
            # 백분위수 기반 이상 탐지
            threshold = self.config["statistical_detection"]["percentile_threshold"]
            upper_threshold = np.percentile(data, threshold * 100)
            lower_threshold = np.percentile(data, (1 - threshold) * 100)
            
            anomalies = (data > upper_threshold) | (data < lower_threshold)
            scores = np.maximum(data / upper_threshold, lower_threshold / data)
            scores = np.maximum(scores, 1)
        
        else:
            raise ValueError(f"지원하지 않는 방법: {method}")
        
        return {
            "anomalies": anomalies.tolist(),
            "scores": scores.tolist(),
            "method": method,
            "threshold": threshold if method == "z_score" else None
        }
    
    def train_ml_anomaly_detector(self, data: np.ndarray, method: str = "isolation_forest") -> Dict[str, Any]:
        """머신러닝 기반 이상 탐지기 훈련"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn이 필요합니다.")
        
        if len(data) == 0:
            raise ValueError("훈련 데이터가 비어있습니다.")
        
        # 데이터 준비
        if data.ndim == 1:
            X = data.reshape(-1, 1)
        else:
            X = data
        
        # 스케일링
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers[method] = scaler
        
        # 모델 선택 및 훈련
        if method == "isolation_forest":
            config = self.config["ml_detection"]["isolation_forest"]
            model = IsolationForest(
                contamination=config["contamination"],
                random_state=config["random_state"]
            )
        elif method == "local_outlier_factor":
            config = self.config["ml_detection"]["local_outlier_factor"]
            model = LocalOutlierFactor(
                contamination=config["contamination"],
                n_neighbors=config["n_neighbors"],
                novelty=True
            )
        elif method == "one_class_svm":
            config = self.config["ml_detection"]["one_class_svm"]
            model = OneClassSVM(
                nu=config["nu"],
                kernel=config["kernel"]
            )
        else:
            raise ValueError(f"지원하지 않는 방법: {method}")
        
        # 모델 훈련
        model.fit(X_scaled)
        self.models[method] = model
        
        # 훈련 데이터에 대한 예측
        if method == "local_outlier_factor":
            # LOF는 novelty=True일 때 predict가 다르게 작동
            predictions = model.predict(X_scaled)
        else:
            predictions = model.predict(X_scaled)
        
        # 점수 계산
        if hasattr(model, 'score_samples'):
            scores = model.score_samples(X_scaled)
        elif hasattr(model, 'decision_function'):
            scores = model.decision_function(X_scaled)
        else:
            scores = np.zeros(len(X_scaled))
        
        # 이상 탐지 결과
        anomalies = predictions == -1
        
        results = {
            "method": method,
            "anomalies_detected": np.sum(anomalies),
            "anomaly_rate": np.mean(anomalies),
            "model_trained": True,
            "training_samples": len(X_scaled)
        }
        
        self.logger.info(f"{method} 모델 훈련 완료: {results['anomalies_detected']}개 이상 탐지")
        return results
    
    def detect_ml_anomalies(self, data: np.ndarray, method: str = "isolation_forest") -> Dict[str, Any]:
        """머신러닝 기반 이상 탐지"""
        if method not in self.models:
            raise ValueError(f"훈련되지 않은 모델: {method}")
        
        if len(data) == 0:
            return {"anomalies": [], "scores": [], "method": method}
        
        # 데이터 준비
        if data.ndim == 1:
            X = data.reshape(-1, 1)
        else:
            X = data
        
        # 스케일링
        scaler = self.scalers.get(method)
        if scaler:
            X_scaled = scaler.transform(X)
        else:
            X_scaled = X
        
        # 예측
        model = self.models[method]
        predictions = model.predict(X_scaled)
        
        # 점수 계산
        if hasattr(model, 'score_samples'):
            scores = model.score_samples(X_scaled)
        elif hasattr(model, 'decision_function'):
            scores = model.decision_function(X_scaled)
        else:
            scores = np.zeros(len(X_scaled))
        
        # 이상 탐지 결과
        anomalies = predictions == -1
        
        return {
            "anomalies": anomalies.tolist(),
            "scores": scores.tolist(),
            "method": method,
            "anomaly_count": np.sum(anomalies)
        }
    
    def detect_time_series_anomalies(self, data: np.ndarray, timestamps: List = None) -> Dict[str, Any]:
        """시계열 이상 탐지"""
        if len(data) == 0:
            return {"anomalies": [], "scores": [], "method": "time_series"}
        
        window_size = self.config["time_series_detection"]["window_size"]
        threshold_multiplier = self.config["time_series_detection"]["threshold_multiplier"]
        min_duration = self.config["time_series_detection"]["min_anomaly_duration"]
        
        anomalies = np.zeros(len(data), dtype=bool)
        scores = np.zeros(len(data))
        
        # 이동 평균과 표준편차 계산
        for i in range(window_size, len(data)):
            window = data[i-window_size:i]
            mean = np.mean(window)
            std = np.std(window)
            
            if std > 0:
                current_value = data[i]
                z_score = abs(current_value - mean) / std
                scores[i] = z_score
                
                if z_score > threshold_multiplier:
                    anomalies[i] = True
        
        # 최소 지속 시간 필터링
        if min_duration > 1:
            filtered_anomalies = np.zeros_like(anomalies)
            for i in range(len(anomalies)):
                if i < min_duration - 1:
                    continue
                
                # 연속된 이상 탐지 확인
                if np.sum(anomalies[i-min_duration+1:i+1]) >= min_duration:
                    filtered_anomalies[i] = True
            
            anomalies = filtered_anomalies
        
        return {
            "anomalies": anomalies.tolist(),
            "scores": scores.tolist(),
            "method": "time_series",
            "window_size": window_size,
            "anomaly_count": np.sum(anomalies)
        }
    
    def detect_patterns(self, data: np.ndarray, pattern_length: int = None) -> Dict[str, Any]:
        """패턴 탐지"""
        if len(data) < 3:
            return {"patterns": [], "method": "pattern_detection"}
        
        if pattern_length is None:
            pattern_length = self.config["pattern_detection"]["min_pattern_length"]
        
        max_patterns = self.config["pattern_detection"]["max_patterns"]
        similarity_threshold = self.config["pattern_detection"]["similarity_threshold"]
        
        patterns = []
        pattern_counts = {}
        
        # 모든 가능한 패턴 추출
        for i in range(len(data) - pattern_length + 1):
            pattern = data[i:i+pattern_length]
            pattern_key = tuple(pattern)
            
            if pattern_key in pattern_counts:
                pattern_counts[pattern_key] += 1
            else:
                pattern_counts[pattern_key] = 1
        
        # 빈도순으로 정렬
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        
        # 상위 패턴 선택
        for pattern, count in sorted_patterns[:max_patterns]:
            if count > 1:  # 최소 2번 이상 나타나는 패턴만
                patterns.append({
                    "pattern": list(pattern),
                    "frequency": count,
                    "length": len(pattern)
                })
        
        # 패턴 유사성 분석
        similar_patterns = self._find_similar_patterns(patterns, similarity_threshold)
        
        return {
            "patterns": patterns,
            "similar_patterns": similar_patterns,
            "method": "pattern_detection",
            "total_patterns": len(patterns)
        }
    
    def _find_similar_patterns(self, patterns: List[Dict], threshold: float) -> List[List[int]]:
        """유사한 패턴 찾기"""
        similar_groups = []
        used_patterns = set()
        
        for i, pattern1 in enumerate(patterns):
            if i in used_patterns:
                continue
            
            similar_group = [i]
            used_patterns.add(i)
            
            for j, pattern2 in enumerate(patterns[i+1:], i+1):
                if j in used_patterns:
                    continue
                
                # 패턴 유사도 계산
                similarity = self._calculate_pattern_similarity(
                    pattern1["pattern"], pattern2["pattern"]
                )
                
                if similarity >= threshold:
                    similar_group.append(j)
                    used_patterns.add(j)
            
            if len(similar_group) > 1:
                similar_groups.append(similar_group)
        
        return similar_groups
    
    def _calculate_pattern_similarity(self, pattern1: List, pattern2: List) -> float:
        """패턴 유사도 계산"""
        if len(pattern1) != len(pattern2):
            return 0.0
        
        # 정규화된 유클리드 거리 기반 유사도
        pattern1_norm = np.array(pattern1) / (np.linalg.norm(pattern1) + 1e-8)
        pattern2_norm = np.array(pattern2) / (np.linalg.norm(pattern2) + 1e-8)
        
        distance = np.linalg.norm(pattern1_norm - pattern2_norm)
        similarity = 1.0 / (1.0 + distance)
        
        return similarity
    
    def detect_peaks_and_valleys(self, data: np.ndarray, prominence: float = None) -> Dict[str, Any]:
        """피크와 골 탐지"""
        if not SCIPY_AVAILABLE:
            return {"peaks": [], "valleys": [], "method": "peaks_valleys"}
        
        if len(data) == 0:
            return {"peaks": [], "valleys": [], "method": "peaks_valleys"}
        
        if prominence is None:
            prominence = np.std(data) * 0.5
        
        # 피크 탐지
        peaks, peak_properties = find_peaks(data, prominence=prominence)
        
        # 골 탐지 (데이터를 뒤집어서 피크 탐지)
        valleys, valley_properties = find_peaks(-data, prominence=prominence)
        
        return {
            "peaks": peaks.tolist(),
            "valleys": valleys.tolist(),
            "peak_heights": data[peaks].tolist() if len(peaks) > 0 else [],
            "valley_heights": data[valleys].tolist() if len(valleys) > 0 else [],
            "method": "peaks_valleys",
            "prominence": prominence
        }
    
    def cluster_anomalies(self, data: np.ndarray, anomalies: np.ndarray) -> Dict[str, Any]:
        """이상 클러스터링"""
        if not SKLEARN_AVAILABLE:
            return {"clusters": [], "method": "clustering"}
        
        if len(data) == 0 or np.sum(anomalies) == 0:
            return {"clusters": [], "method": "clustering"}
        
        # 이상 데이터만 추출
        anomaly_data = data[anomalies]
        
        if len(anomaly_data) < 2:
            return {"clusters": [], "method": "clustering"}
        
        # 데이터 준비
        if anomaly_data.ndim == 1:
            X = anomaly_data.reshape(-1, 1)
        else:
            X = anomaly_data
        
        # 스케일링
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # DBSCAN 클러스터링
        clustering = DBSCAN(eps=0.5, min_samples=2)
        cluster_labels = clustering.fit_predict(X_scaled)
        
        # 클러스터 정보 수집
        clusters = []
        for cluster_id in set(cluster_labels):
            if cluster_id == -1:  # 노이즈
                continue
            
            cluster_indices = np.where(cluster_labels == cluster_id)[0]
            cluster_data = anomaly_data[cluster_indices]
            
            clusters.append({
                "cluster_id": int(cluster_id),
                "size": len(cluster_indices),
                "center": np.mean(cluster_data, axis=0).tolist(),
                "indices": cluster_indices.tolist()
            })
        
        # 실루엣 점수 계산
        if len(set(cluster_labels)) > 1 and -1 not in cluster_labels:
            silhouette_avg = silhouette_score(X_scaled, cluster_labels)
        else:
            silhouette_avg = 0.0
        
        return {
            "clusters": clusters,
            "method": "clustering",
            "silhouette_score": silhouette_avg,
            "noise_points": np.sum(cluster_labels == -1)
        }
    
    def comprehensive_anomaly_detection(self, data: np.ndarray, 
                                     methods: List[str] = None) -> Dict[str, Any]:
        """종합 이상 탐지"""
        if methods is None:
            methods = ["statistical", "ml", "time_series"]
        
        results = {
            "data_length": len(data),
            "methods_used": methods,
            "detection_results": {},
            "combined_anomalies": [],
            "confidence_scores": []
        }
        
        # 각 방법으로 이상 탐지
        for method in methods:
            try:
                if method == "statistical":
                    result = self.detect_statistical_anomalies(data, "z_score")
                elif method == "ml" and "isolation_forest" in self.models:
                    result = self.detect_ml_anomalies(data, "isolation_forest")
                elif method == "time_series":
                    result = self.detect_time_series_anomalies(data)
                else:
                    continue
                
                results["detection_results"][method] = result
                
            except Exception as e:
                self.logger.warning(f"{method} 이상 탐지 실패: {e}")
                continue
        
        # 결과 통합
        if results["detection_results"]:
            combined_anomalies = np.zeros(len(data), dtype=bool)
            confidence_scores = np.zeros(len(data))
            
            for method, result in results["detection_results"].items():
                if "anomalies" in result:
                    anomalies = np.array(result["anomalies"])
                    combined_anomalies |= anomalies
                    
                    # 신뢰도 점수 누적
                    if "scores" in result:
                        scores = np.array(result["scores"])
                        confidence_scores += scores * anomalies
            
            # 신뢰도 정규화
            if np.sum(combined_anomalies) > 0:
                confidence_scores[combined_anomalies] /= np.sum(combined_anomalies)
            
            results["combined_anomalies"] = combined_anomalies.tolist()
            results["confidence_scores"] = confidence_scores.tolist()
            results["total_anomalies"] = np.sum(combined_anomalies)
        
        return results
    
    def generate_alert(self, anomaly_result: Dict[str, Any], 
                      alert_type: str = "anomaly") -> Dict[str, Any]:
        """알림 생성"""
        min_confidence = self.config["alerting"]["min_confidence"]
        cooldown_period = self.config["alerting"]["cooldown_period"]
        
        # 신뢰도 확인
        confidence = 0.0
        if "confidence_scores" in anomaly_result:
            confidence = np.max(anomaly_result["confidence_scores"])
        elif "scores" in anomaly_result:
            confidence = np.max(anomaly_result["scores"])
        
        if confidence < min_confidence:
            return {"alert_generated": False, "reason": "low_confidence"}
        
        # 쿨다운 확인
        current_time = datetime.now()
        recent_alerts = [
            alert for alert in self.detection_history
            if (current_time - alert["timestamp"]).total_seconds() < cooldown_period
        ]
        
        if len(recent_alerts) >= self.config["alerting"]["max_alerts_per_hour"]:
            return {"alert_generated": False, "reason": "rate_limit"}
        
        # 알림 생성
        alert = {
            "alert_id": f"anomaly_{len(self.detection_history)}",
            "alert_type": alert_type,
            "timestamp": current_time.isoformat(),
            "confidence": confidence,
            "anomaly_count": anomaly_result.get("total_anomalies", 0),
            "methods_used": anomaly_result.get("methods_used", []),
            "data_length": anomaly_result.get("data_length", 0)
        }
        
        self.detection_history.append(alert)
        
        return {
            "alert_generated": True,
            "alert": alert
        }
    
    def save_model(self, filepath: str):
        """모델 저장"""
        import joblib
        
        model_data = {
            "models": self.models,
            "scalers": self.scalers,
            "thresholds": self.thresholds,
            "config": self.config,
            "detection_history": self.detection_history
        }
        
        joblib.dump(model_data, filepath)
        self.logger.info(f"모델 저장 완료: {filepath}")
    
    def load_model(self, filepath: str):
        """모델 로드"""
        import joblib
        
        model_data = joblib.load(filepath)
        
        self.models = model_data.get("models", {})
        self.scalers = model_data.get("scalers", {})
        self.thresholds = model_data.get("thresholds", {})
        self.config.update(model_data.get("config", {}))
        self.detection_history = model_data.get("detection_history", [])
        
        self.logger.info(f"모델 로드 완료: {filepath}")
    
    def generate_report(self) -> Dict[str, Any]:
        """이상 탐지 리포트 생성"""
        report = {
            "system_info": {
                "sklearn_available": SKLEARN_AVAILABLE,
                "scipy_available": SCIPY_AVAILABLE,
                "trained_models": list(self.models.keys()),
                "config": self.config
            },
            "detection_history": {
                "total_alerts": len(self.detection_history),
                "recent_alerts": self.detection_history[-10:] if self.detection_history else []
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return report

# 사용 예시
if __name__ == "__main__":
    # 이상 탐지 시스템 초기화
    detector = AnomalyDetectionSystem()
    
    # 샘플 데이터 생성
    np.random.seed(42)
    normal_data = np.random.normal(0, 1, 1000)
    anomaly_data = np.random.normal(5, 1, 50)  # 이상 데이터
    data = np.concatenate([normal_data, anomaly_data])
    
    # 통계적 이상 탐지
    stat_result = detector.detect_statistical_anomalies(data, "z_score")
    print(f"통계적 이상 탐지: {np.sum(stat_result['anomalies'])}개 이상")
    
    # 머신러닝 기반 이상 탐지
    if SKLEARN_AVAILABLE:
        ml_result = detector.train_ml_anomaly_detector(data, "isolation_forest")
        print(f"ML 이상 탐지 훈련: {ml_result['anomalies_detected']}개 이상")
        
        detection_result = detector.detect_ml_anomalies(data, "isolation_forest")
        print(f"ML 이상 탐지: {detection_result['anomaly_count']}개 이상")
    
    # 시계열 이상 탐지
    ts_result = detector.detect_time_series_anomalies(data)
    print(f"시계열 이상 탐지: {ts_result['anomaly_count']}개 이상")
    
    # 종합 이상 탐지
    comprehensive_result = detector.comprehensive_anomaly_detection(data)
    print(f"종합 이상 탐지: {comprehensive_result['total_anomalies']}개 이상")
    
    # 알림 생성
    alert_result = detector.generate_alert(comprehensive_result)
    print(f"알림 생성: {alert_result['alert_generated']}")
    
    # 리포트 생성
    report = detector.generate_report()
    print("이상 탐지 리포트 생성 완료") 