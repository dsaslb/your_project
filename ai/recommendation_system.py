import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional, Union
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import NMF, TruncatedSVD
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from scipy.sparse import csr_matrix
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

class RecommendationSystem:
    """실시간 AI 추천 시스템"""
    
    def __init__(self, config_path: str = "recommendation_config.json"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        
        # 데이터 저장소
        self.user_item_matrix = None
        self.user_profiles = {}
        self.item_profiles = {}
        self.user_similarities = {}
        self.item_similarities = {}
        
        # 실시간 업데이트를 위한 캐시
        self.recommendation_cache = {}
        self.interaction_history = []
        self.user_preferences = defaultdict(dict)
        
        # 모델들
        self.collaborative_model = None
        self.content_model = None
        self.hybrid_model = None
        
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
            "collaborative_filtering": {
                "method": "user_based",
                "similarity_metric": "cosine",
                "min_common_items": 3,
                "max_neighbors": 50
            },
            "content_based_filtering": {
                "method": "tfidf",
                "max_features": 1000,
                "min_df": 2,
                "max_df": 0.8
            },
            "hybrid_recommendation": {
                "collaborative_weight": 0.6,
                "content_weight": 0.4,
                "ensemble_method": "weighted_average"
            },
            "real_time_updates": {
                "cache_ttl": 300,  # 5분
                "update_threshold": 10,
                "batch_update_interval": 3600  # 1시간
            },
            "personalization": {
                "preference_decay": 0.95,
                "context_weight": 0.3,
                "diversity_factor": 0.1
            },
            "evaluation": {
                "test_size": 0.2,
                "metrics": ["precision", "recall", "ndcg", "diversity"]
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('recommendation_system')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def load_data(self, interactions_data: pd.DataFrame, 
                  user_data: pd.DataFrame = None, 
                  item_data: pd.DataFrame = None):
        """데이터 로드 및 전처리"""
        self.logger.info(f"데이터 로드 시작: {len(interactions_data)}개 상호작용")
        
        # 상호작용 데이터 전처리
        if 'rating' not in interactions_data.columns:
            interactions_data['rating'] = 1.0  # 암시적 피드백
        
        # 사용자-아이템 매트릭스 생성
        self.user_item_matrix = interactions_data.pivot_table(
            index='user_id', 
            columns='item_id', 
            values='rating', 
            fill_value=0
        )
        
        # 사용자 및 아이템 프로필 생성
        if user_data is not None:
            self._create_user_profiles(user_data)
        
        if item_data is not None:
            self._create_item_profiles(item_data)
        
        self.logger.info(f"데이터 로드 완료: {self.user_item_matrix.shape}")
    
    def _create_user_profiles(self, user_data: pd.DataFrame):
        """사용자 프로필 생성"""
        for _, user in user_data.iterrows():
            user_id = user['user_id']
            self.user_profiles[user_id] = {
                'demographics': user.to_dict(),
                'preferences': {},
                'activity_level': 0
            }
    
    def _create_item_profiles(self, item_data: pd.DataFrame):
        """아이템 프로필 생성"""
        for _, item in item_data.iterrows():
            item_id = item['item_id']
            self.item_profiles[item_id] = {
                'attributes': item.to_dict(),
                'category': item.get('category', 'unknown'),
                'tags': item.get('tags', '').split(',') if item.get('tags') else []
            }
    
    def train_collaborative_filtering(self, method: str = "user_based") -> Dict[str, Any]:
        """협업 필터링 모델 훈련"""
        if self.user_item_matrix is None:
            raise ValueError("데이터가 로드되지 않았습니다.")
        
        self.logger.info(f"협업 필터링 훈련 시작: {method}")
        
        if method == "user_based":
            return self._train_user_based_cf()
        elif method == "item_based":
            return self._train_item_based_cf()
        elif method == "matrix_factorization":
            return self._train_matrix_factorization()
        else:
            raise ValueError(f"지원하지 않는 방법: {method}")
    
    def _train_user_based_cf(self) -> Dict[str, Any]:
        """사용자 기반 협업 필터링"""
        # 사용자 간 유사도 계산
        user_similarities = cosine_similarity(self.user_item_matrix)
        
        # 유사도 매트릭스를 딕셔너리로 변환
        for i, user_id in enumerate(self.user_item_matrix.index):
            self.user_similarities[user_id] = {}
            for j, other_user_id in enumerate(self.user_item_matrix.index):
                if i != j:
                    self.user_similarities[user_id][other_user_id] = user_similarities[i, j]
        
        self.collaborative_model = {
            "method": "user_based",
            "similarities": self.user_similarities,
            "trained_at": datetime.now().isoformat()
        }
        
        return {
            "method": "user_based",
            "users_processed": len(self.user_item_matrix),
            "similarity_matrix_shape": user_similarities.shape
        }
    
    def _train_item_based_cf(self) -> Dict[str, Any]:
        """아이템 기반 협업 필터링"""
        # 아이템 간 유사도 계산
        item_similarities = cosine_similarity(self.user_item_matrix.T)
        
        # 유사도 매트릭스를 딕셔너리로 변환
        for i, item_id in enumerate(self.user_item_matrix.columns):
            self.item_similarities[item_id] = {}
            for j, other_item_id in enumerate(self.user_item_matrix.columns):
                if i != j:
                    self.item_similarities[item_id][other_item_id] = item_similarities[i, j]
        
        self.collaborative_model = {
            "method": "item_based",
            "similarities": self.item_similarities,
            "trained_at": datetime.now().isoformat()
        }
        
        return {
            "method": "item_based",
            "items_processed": len(self.user_item_matrix.columns),
            "similarity_matrix_shape": item_similarities.shape
        }
    
    def _train_matrix_factorization(self) -> Dict[str, Any]:
        """행렬 분해 기반 협업 필터링"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn이 필요합니다.")
        
        # NMF 또는 SVD 사용
        n_components = min(50, min(self.user_item_matrix.shape))
        
        try:
            # NMF 시도
            nmf = NMF(n_components=n_components, random_state=42)
            user_factors = nmf.fit_transform(self.user_item_matrix)
            item_factors = nmf.components_
            method = "nmf"
        except:
            # SVD 사용
            svd = TruncatedSVD(n_components=n_components, random_state=42)
            user_factors = svd.fit_transform(self.user_item_matrix)
            item_factors = svd.components_
            method = "svd"
        
        self.collaborative_model = {
            "method": "matrix_factorization",
            "algorithm": method,
            "user_factors": user_factors,
            "item_factors": item_factors,
            "n_components": n_components,
            "trained_at": datetime.now().isoformat()
        }
        
        return {
            "method": "matrix_factorization",
            "algorithm": method,
            "n_components": n_components,
            "reconstruction_error": getattr(svd, 'explained_variance_ratio_', None)
        }
    
    def train_content_based_filtering(self) -> Dict[str, Any]:
        """콘텐츠 기반 필터링 모델 훈련"""
        if not self.item_profiles:
            raise ValueError("아이템 프로필이 없습니다.")
        
        self.logger.info("콘텐츠 기반 필터링 훈련 시작")
        
        # 아이템 특성 추출
        item_features = []
        item_ids = []
        
        for item_id, profile in self.item_profiles.items():
            features = []
            
            # 카테고리
            features.append(profile.get('category', 'unknown'))
            
            # 태그
            features.extend(profile.get('tags', []))
            
            # 기타 속성들
            for key, value in profile.get('attributes', {}).items():
                if key not in ['item_id', 'category', 'tags']:
                    features.append(str(value))
            
            item_features.append(' '.join(features))
            item_ids.append(item_id)
        
        # TF-IDF 벡터화
        if SKLEARN_AVAILABLE:
            vectorizer = TfidfVectorizer(
                max_features=self.config["content_based_filtering"]["max_features"],
                min_df=self.config["content_based_filtering"]["min_df"],
                max_df=self.config["content_based_filtering"]["max_df"]
            )
            
            tfidf_matrix = vectorizer.fit_transform(item_features)
            
            self.content_model = {
                "vectorizer": vectorizer,
                "tfidf_matrix": tfidf_matrix,
                "item_ids": item_ids,
                "trained_at": datetime.now().isoformat()
            }
            
            return {
                "method": "content_based",
                "items_processed": len(item_ids),
                "features": tfidf_matrix.shape[1]
            }
        else:
            raise ImportError("scikit-learn이 필요합니다.")
    
    def get_user_based_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[Dict]:
        """사용자 기반 추천"""
        if self.collaborative_model is None or self.collaborative_model["method"] != "user_based":
            raise ValueError("사용자 기반 협업 필터링 모델이 훈련되지 않았습니다.")
        
        if user_id not in self.user_similarities:
            return []
        
        # 유사한 사용자 찾기
        similar_users = sorted(
            self.user_similarities[user_id].items(),
            key=lambda x: x[1],
            reverse=True
        )[:self.config["collaborative_filtering"]["max_neighbors"]]
        
        # 추천 점수 계산
        item_scores = defaultdict(float)
        user_ratings = self.user_item_matrix.loc[user_id]
        
        for similar_user_id, similarity in similar_users:
            if similarity <= 0:
                continue
            
            similar_user_ratings = self.user_item_matrix.loc[similar_user_id]
            
            for item_id in similar_user_ratings.index:
                if user_ratings[item_id] == 0:  # 아직 평가하지 않은 아이템
                    item_scores[item_id] += similarity * similar_user_ratings[item_id]
        
        # 상위 추천 아이템 선택
        recommendations = []
        for item_id, score in sorted(item_scores.items(), key=lambda x: x[1], reverse=True):
            if len(recommendations) >= n_recommendations:
                break
            
            recommendations.append({
                "item_id": item_id,
                "score": score,
                "method": "user_based_cf"
            })
        
        return recommendations
    
    def get_item_based_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[Dict]:
        """아이템 기반 추천"""
        if self.collaborative_model is None or self.collaborative_model["method"] != "item_based":
            raise ValueError("아이템 기반 협업 필터링 모델이 훈련되지 않았습니다.")
        
        if user_id not in self.user_item_matrix.index:
            return []
        
        user_ratings = self.user_item_matrix.loc[user_id]
        rated_items = user_ratings[user_ratings > 0].index
        
        # 추천 점수 계산
        item_scores = defaultdict(float)
        
        for rated_item in rated_items:
            if rated_item not in self.item_similarities:
                continue
            
            rating = user_ratings[rated_item]
            
            for similar_item, similarity in self.item_similarities[rated_item].items():
                if user_ratings[similar_item] == 0:  # 아직 평가하지 않은 아이템
                    item_scores[similar_item] += similarity * rating
        
        # 상위 추천 아이템 선택
        recommendations = []
        for item_id, score in sorted(item_scores.items(), key=lambda x: x[1], reverse=True):
            if len(recommendations) >= n_recommendations:
                break
            
            recommendations.append({
                "item_id": item_id,
                "score": score,
                "method": "item_based_cf"
            })
        
        return recommendations
    
    def get_content_based_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[Dict]:
        """콘텐츠 기반 추천"""
        if self.content_model is None:
            raise ValueError("콘텐츠 기반 필터링 모델이 훈련되지 않았습니다.")
        
        if user_id not in self.user_item_matrix.index:
            return []
        
        # 사용자가 평가한 아이템들의 특성 벡터 계산
        user_ratings = self.user_item_matrix.loc[user_id]
        rated_items = user_ratings[user_ratings > 0]
        
        if len(rated_items) == 0:
            return []
        
        # 사용자 프로필 벡터 계산
        user_profile = np.zeros(self.content_model["tfidf_matrix"].shape[1])
        
        for item_id, rating in rated_items.items():
            if item_id in self.content_model["item_ids"]:
                item_idx = self.content_model["item_ids"].index(item_id)
                item_vector = self.content_model["tfidf_matrix"][item_idx].toarray().flatten()
                user_profile += rating * item_vector
        
        # 모든 아이템과의 유사도 계산
        item_scores = {}
        for i, item_id in enumerate(self.content_model["item_ids"]):
            if user_ratings[item_id] == 0:  # 아직 평가하지 않은 아이템
                item_vector = self.content_model["tfidf_matrix"][i].toarray().flatten()
                similarity = np.dot(user_profile, item_vector) / (
                    np.linalg.norm(user_profile) * np.linalg.norm(item_vector) + 1e-8
                )
                item_scores[item_id] = similarity
        
        # 상위 추천 아이템 선택
        recommendations = []
        for item_id, score in sorted(item_scores.items(), key=lambda x: x[1], reverse=True):
            if len(recommendations) >= n_recommendations:
                break
            
            recommendations.append({
                "item_id": item_id,
                "score": score,
                "method": "content_based"
            })
        
        return recommendations
    
    def get_hybrid_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[Dict]:
        """하이브리드 추천"""
        collaborative_weight = self.config["hybrid_recommendation"]["collaborative_weight"]
        content_weight = self.config["hybrid_recommendation"]["content_weight"]
        
        # 각 방법으로 추천 가져오기
        collaborative_recs = []
        content_recs = []
        
        try:
            if self.collaborative_model and self.collaborative_model["method"] == "user_based":
                collaborative_recs = self.get_user_based_recommendations(user_id, n_recommendations)
        except:
            pass
        
        try:
            if self.content_model:
                content_recs = self.get_content_based_recommendations(user_id, n_recommendations)
        except:
            pass
        
        # 하이브리드 점수 계산
        hybrid_scores = defaultdict(float)
        
        for rec in collaborative_recs:
            hybrid_scores[rec["item_id"]] += collaborative_weight * rec["score"]
        
        for rec in content_recs:
            hybrid_scores[rec["item_id"]] += content_weight * rec["score"]
        
        # 상위 추천 아이템 선택
        recommendations = []
        for item_id, score in sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True):
            if len(recommendations) >= n_recommendations:
                break
            
            recommendations.append({
                "item_id": item_id,
                "score": score,
                "method": "hybrid"
            })
        
        return recommendations
    
    def record_interaction(self, user_id: str, item_id: str, 
                          interaction_type: str = "view", rating: float = None):
        """사용자 상호작용 기록"""
        interaction = {
            "user_id": user_id,
            "item_id": item_id,
            "interaction_type": interaction_type,
            "rating": rating,
            "timestamp": datetime.now().isoformat()
        }
        
        self.interaction_history.append(interaction)
        
        # 사용자 선호도 업데이트
        if item_id not in self.user_preferences[user_id]:
            self.user_preferences[user_id][item_id] = {
                "interactions": 0,
                "total_rating": 0,
                "last_interaction": None
            }
        
        pref = self.user_preferences[user_id][item_id]
        pref["interactions"] += 1
        if rating:
            pref["total_rating"] += rating
        pref["last_interaction"] = interaction["timestamp"]
        
        # 캐시 무효화
        cache_key = f"{user_id}_recommendations"
        if cache_key in self.recommendation_cache:
            del self.recommendation_cache[cache_key]
        
        self.logger.info(f"상호작용 기록: {user_id} -> {item_id} ({interaction_type})")
    
    def get_personalized_recommendations(self, user_id: str, 
                                       context: Dict = None, 
                                       n_recommendations: int = 10) -> List[Dict]:
        """개인화된 추천"""
        # 기본 추천 가져오기
        if self.collaborative_model and self.content_model:
            recommendations = self.get_hybrid_recommendations(user_id, n_recommendations * 2)
        elif self.collaborative_model:
            recommendations = self.get_user_based_recommendations(user_id, n_recommendations * 2)
        elif self.content_model:
            recommendations = self.get_content_based_recommendations(user_id, n_recommendations * 2)
        else:
            return []
        
        # 개인화 적용
        personalized_recs = []
        
        for rec in recommendations:
            item_id = rec["item_id"]
            score = rec["score"]
            
            # 사용자 선호도 가중치
            if user_id in self.user_preferences and item_id in self.user_preferences[user_id]:
                pref = self.user_preferences[user_id][item_id]
                interaction_weight = min(pref["interactions"] * 0.1, 1.0)
                score *= (1 + interaction_weight)
            
            # 컨텍스트 가중치
            if context and self.item_profiles.get(item_id):
                context_weight = self._calculate_context_weight(context, self.item_profiles[item_id])
                score *= (1 + self.config["personalization"]["context_weight"] * context_weight)
            
            personalized_recs.append({
                "item_id": item_id,
                "score": score,
                "method": rec["method"]
            })
        
        # 다양성 적용
        diverse_recs = self._apply_diversity(personalized_recs, n_recommendations)
        
        return diverse_recs[:n_recommendations]
    
    def _calculate_context_weight(self, context: Dict, item_profile: Dict) -> float:
        """컨텍스트 가중치 계산"""
        weight = 0.0
        
        # 시간대 매칭
        if 'time_of_day' in context and 'category' in item_profile:
            # 간단한 시간대 기반 가중치
            time_weight = 0.1
            weight += time_weight
        
        # 위치 매칭
        if 'location' in context and 'category' in item_profile:
            # 위치 기반 가중치
            location_weight = 0.2
            weight += location_weight
        
        return weight
    
    def _apply_diversity(self, recommendations: List[Dict], n_recommendations: int) -> List[Dict]:
        """다양성 적용"""
        if len(recommendations) <= n_recommendations:
            return recommendations
        
        diverse_recs = []
        used_categories = set()
        diversity_factor = self.config["personalization"]["diversity_factor"]
        
        for rec in recommendations:
            item_id = rec["item_id"]
            category = self.item_profiles.get(item_id, {}).get('category', 'unknown')
            
            # 다양성 보너스
            if category not in used_categories:
                rec["score"] *= (1 + diversity_factor)
                used_categories.add(category)
            
            diverse_recs.append(rec)
        
        # 점수로 재정렬
        diverse_recs.sort(key=lambda x: x["score"], reverse=True)
        
        return diverse_recs[:n_recommendations]
    
    def evaluate_recommendations(self, test_data: pd.DataFrame) -> Dict[str, float]:
        """추천 시스템 평가"""
        if test_data.empty:
            return {}
        
        metrics = {}
        
        # 정밀도와 재현율 계산
        total_recommendations = 0
        total_relevant = 0
        total_correct = 0
        
        for user_id in test_data['user_id'].unique():
            user_test_items = set(test_data[test_data['user_id'] == user_id]['item_id'])
            
            # 추천 가져오기
            try:
                recommendations = self.get_personalized_recommendations(user_id, n_recommendations=10)
                recommended_items = {rec['item_id'] for rec in recommendations}
                
                total_recommendations += len(recommended_items)
                total_relevant += len(user_test_items)
                total_correct += len(recommended_items & user_test_items)
                
            except Exception as e:
                self.logger.warning(f"사용자 {user_id} 추천 평가 실패: {e}")
                continue
        
        if total_recommendations > 0:
            metrics["precision"] = total_correct / total_recommendations
        
        if total_relevant > 0:
            metrics["recall"] = total_correct / total_relevant
        
        if metrics.get("precision", 0) + metrics.get("recall", 0) > 0:
            metrics["f1_score"] = 2 * metrics["precision"] * metrics["recall"] / (
                metrics["precision"] + metrics["recall"]
            )
        
        return metrics
    
    def save_model(self, filepath: str):
        """모델 저장"""
        if not JOBLIB_AVAILABLE:
            raise ImportError("joblib이 필요합니다.")
        
        model_data = {
            "collaborative_model": self.collaborative_model,
            "content_model": self.content_model,
            "user_profiles": self.user_profiles,
            "item_profiles": self.item_profiles,
            "user_similarities": self.user_similarities,
            "item_similarities": self.item_similarities,
            "user_preferences": dict(self.user_preferences),
            "config": self.config
        }
        
        joblib.dump(model_data, filepath)
        self.logger.info(f"모델 저장 완료: {filepath}")
    
    def load_model(self, filepath: str):
        """모델 로드"""
        if not JOBLIB_AVAILABLE:
            raise ImportError("joblib이 필요합니다.")
        
        model_data = joblib.load(filepath)
        
        self.collaborative_model = model_data.get("collaborative_model")
        self.content_model = model_data.get("content_model")
        self.user_profiles = model_data.get("user_profiles", {})
        self.item_profiles = model_data.get("item_profiles", {})
        self.user_similarities = model_data.get("user_similarities", {})
        self.item_similarities = model_data.get("item_similarities", {})
        self.user_preferences = defaultdict(dict, model_data.get("user_preferences", {}))
        self.config.update(model_data.get("config", {}))
        
        self.logger.info(f"모델 로드 완료: {filepath}")
    
    def generate_report(self) -> Dict[str, Any]:
        """추천 시스템 리포트 생성"""
        report = {
            "system_info": {
                "sklearn_available": SKLEARN_AVAILABLE,
                "scipy_available": SCIPY_AVAILABLE,
                "config": self.config
            },
            "data_summary": {
                "total_users": len(self.user_profiles) if self.user_profiles else 0,
                "total_items": len(self.item_profiles) if self.item_profiles else 0,
                "total_interactions": len(self.interaction_history)
            },
            "model_status": {
                "collaborative_model": self.collaborative_model is not None,
                "content_model": self.content_model is not None,
                "user_item_matrix_shape": self.user_item_matrix.shape if self.user_item_matrix is not None else None
            },
            "recent_interactions": self.interaction_history[-10:] if self.interaction_history else [],
            "generated_at": datetime.now().isoformat()
        }
        
        return report

# 사용 예시
if __name__ == "__main__":
    # 추천 시스템 초기화
    recommender = RecommendationSystem()
    
    # 샘플 데이터 생성
    np.random.seed(42)
    n_users = 100
    n_items = 50
    
    # 상호작용 데이터
    interactions = []
    for user_id in range(n_users):
        n_interactions = np.random.randint(5, 20)
        items = np.random.choice(n_items, n_interactions, replace=False)
        for item_id in items:
            interactions.append({
                'user_id': f'user_{user_id}',
                'item_id': f'item_{item_id}',
                'rating': np.random.randint(1, 6)
            })
    
    interactions_df = pd.DataFrame(interactions)
    
    # 아이템 데이터
    items_data = []
    categories = ['electronics', 'books', 'clothing', 'food', 'sports']
    for item_id in range(n_items):
        items_data.append({
            'item_id': f'item_{item_id}',
            'category': np.random.choice(categories),
            'tags': f'tag1,tag2,tag{np.random.randint(3, 10)}'
        })
    
    items_df = pd.DataFrame(items_data)
    
    # 데이터 로드
    recommender.load_data(interactions_df, item_data=items_df)
    
    # 모델 훈련
    cf_result = recommender.train_collaborative_filtering("user_based")
    print(f"협업 필터링 훈련: {cf_result}")
    
    cb_result = recommender.train_content_based_filtering()
    print(f"콘텐츠 기반 필터링 훈련: {cb_result}")
    
    # 추천 생성
    user_id = "user_0"
    recommendations = recommender.get_personalized_recommendations(user_id, n_recommendations=5)
    print(f"개인화된 추천 ({user_id}): {recommendations}")
    
    # 상호작용 기록
    recommender.record_interaction(user_id, "item_10", "view", 4.0)
    
    # 평가
    test_data = interactions_df.sample(frac=0.2)
    evaluation = recommender.evaluate_recommendations(test_data)
    print(f"추천 시스템 평가: {evaluation}")
    
    # 리포트 생성
    report = recommender.generate_report()
    print("추천 시스템 리포트 생성 완료") 