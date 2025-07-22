import re
import json
import logging
from typing import Dict, List, Tuple, Any, Optional
from collections import Counter
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.pipeline import Pipeline
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    from nltk.sentiment import SentimentIntensityAnalyzer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

class NLPProcessor:
    """자연어 처리 시스템"""
    
    def __init__(self, config_path: str = "nlp_config.json"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.models = {}
        self.vectorizers = {}
        self.stop_words = set()
        self.stemmer = None
        self.lemmatizer = None
        self.sentiment_analyzer = None
        
        self._initialize_nlp_tools()
    
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
            "preprocessing": {
                "remove_punctuation": True,
                "remove_numbers": False,
                "remove_stopwords": True,
                "lowercase": True,
                "stemming": True,
                "lemmatization": False,
                "min_word_length": 2
            },
            "vectorization": {
                "method": "tfidf",
                "max_features": 5000,
                "ngram_range": (1, 2),
                "min_df": 2,
                "max_df": 0.95
            },
            "sentiment_analysis": {
                "method": "vader",
                "threshold": 0.1
            },
            "keyword_extraction": {
                "method": "tfidf",
                "top_k": 10
            },
            "text_classification": {
                "models": ["naive_bayes", "logistic_regression", "random_forest"],
                "test_size": 0.2,
                "random_state": 42
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('nlp_processor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_nlp_tools(self):
        """NLP 도구 초기화"""
        if NLTK_AVAILABLE:
            try:
                # NLTK 데이터 다운로드
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
                nltk.download('vader_lexicon', quiet=True)
                
                # 도구 초기화
                self.stop_words = set(stopwords.words('english'))
                self.stemmer = PorterStemmer()
                self.lemmatizer = WordNetLemmatizer()
                self.sentiment_analyzer = SentimentIntensityAnalyzer()
                
                self.logger.info("NLTK 도구 초기화 완료")
            except Exception as e:
                self.logger.warning(f"NLTK 초기화 실패: {e}")
        else:
            self.logger.warning("NLTK를 사용할 수 없습니다.")
    
    def preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        if not text or not isinstance(text, str):
            return ""
        
        # 소문자 변환
        if self.config["preprocessing"]["lowercase"]:
            text = text.lower()
        
        # 구두점 제거
        if self.config["preprocessing"]["remove_punctuation"]:
            text = re.sub(r'[^\w\s]', '', text)
        
        # 숫자 제거
        if self.config["preprocessing"]["remove_numbers"]:
            text = re.sub(r'\d+', '', text)
        
        # 토큰화
        tokens = word_tokenize(text) if NLTK_AVAILABLE else text.split()
        
        # 필터링
        filtered_tokens = []
        for token in tokens:
            # 최소 길이 확인
            if len(token) < self.config["preprocessing"]["min_word_length"]:
                continue
            
            # 불용어 제거
            if self.config["preprocessing"]["remove_stopwords"] and token in self.stop_words:
                continue
            
            # 어간 추출
            if self.config["preprocessing"]["stemming"] and self.stemmer:
                token = self.stemmer.stem(token)
            
            # 표제어 추출
            if self.config["preprocessing"]["lemmatization"] and self.lemmatizer:
                token = self.lemmatizer.lemmatize(token)
            
            filtered_tokens.append(token)
        
        return ' '.join(filtered_tokens)
    
    def preprocess_documents(self, documents: List[str]) -> List[str]:
        """문서 목록 전처리"""
        self.logger.info(f"문서 전처리 시작: {len(documents)}개")
        
        processed_docs = []
        for i, doc in enumerate(documents):
            processed_doc = self.preprocess_text(doc)
            processed_docs.append(processed_doc)
            
            if (i + 1) % 100 == 0:
                self.logger.info(f"전처리 진행률: {i + 1}/{len(documents)}")
        
        self.logger.info("문서 전처리 완료")
        return processed_docs
    
    def extract_keywords(self, text: str, method: str = "tfidf", top_k: int = 10) -> List[Tuple[str, float]]:
        """키워드 추출"""
        if not text:
            return []
        
        processed_text = self.preprocess_text(text)
        if not processed_text:
            return []
        
        if method == "tfidf":
            return self._extract_keywords_tfidf(processed_text, top_k)
        elif method == "frequency":
            return self._extract_keywords_frequency(processed_text, top_k)
        else:
            raise ValueError(f"지원하지 않는 방법: {method}")
    
    def _extract_keywords_tfidf(self, text: str, top_k: int) -> List[Tuple[str, float]]:
        """TF-IDF 기반 키워드 추출"""
        if not SKLEARN_AVAILABLE:
            return self._extract_keywords_frequency(text, top_k)
        
        # 단일 문서용 TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=top_k * 2,
            ngram_range=(1, 1),
            stop_words='english'
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # 점수와 단어를 함께 정렬
            word_scores = list(zip(feature_names, tfidf_scores))
            word_scores.sort(key=lambda x: x[1], reverse=True)
            
            return word_scores[:top_k]
        except Exception as e:
            self.logger.warning(f"TF-IDF 키워드 추출 실패: {e}")
            return self._extract_keywords_frequency(text, top_k)
    
    def _extract_keywords_frequency(self, text: str, top_k: int) -> List[Tuple[str, float]]:
        """빈도 기반 키워드 추출"""
        tokens = text.split()
        word_freq = Counter(tokens)
        
        # 빈도 정규화
        total_words = len(tokens)
        word_scores = [(word, freq / total_words) for word, freq in word_freq.most_common(top_k)]
        
        return word_scores
    
    def analyze_sentiment(self, text: str, method: str = "vader") -> Dict[str, Any]:
        """감정 분석"""
        if not text:
            return {"sentiment": "neutral", "score": 0.0, "confidence": 0.0}
        
        if method == "vader" and NLTK_AVAILABLE and self.sentiment_analyzer:
            return self._analyze_sentiment_vader(text)
        elif method == "rule_based":
            return self._analyze_sentiment_rule_based(text)
        else:
            raise ValueError(f"지원하지 않는 방법: {method}")
    
    def _analyze_sentiment_vader(self, text: str) -> Dict[str, Any]:
        """VADER 감정 분석"""
        scores = self.sentiment_analyzer.polarity_scores(text)
        
        # 감정 결정
        compound_score = scores['compound']
        threshold = self.config["sentiment_analysis"]["threshold"]
        
        if compound_score >= threshold:
            sentiment = "positive"
        elif compound_score <= -threshold:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "score": compound_score,
            "confidence": abs(compound_score),
            "details": scores
        }
    
    def _analyze_sentiment_rule_based(self, text: str) -> Dict[str, Any]:
        """규칙 기반 감정 분석"""
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'happy', 'joy', 'pleased', 'satisfied'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'dislike', 'hate',
            'angry', 'sad', 'disappointed', 'frustrated', 'upset'
        }
        
        tokens = text.lower().split()
        positive_count = sum(1 for token in tokens if token in positive_words)
        negative_count = sum(1 for token in tokens if token in negative_words)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return {"sentiment": "neutral", "score": 0.0, "confidence": 0.0}
        
        score = (positive_count - negative_count) / total_sentiment_words
        confidence = total_sentiment_words / len(tokens)
        
        if score > 0.1:
            sentiment = "positive"
        elif score < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "score": score,
            "confidence": confidence
        }
    
    def classify_text(self, text: str, model_name: str = None) -> Dict[str, Any]:
        """텍스트 분류"""
        if not text or not self.models:
            return {"prediction": "unknown", "confidence": 0.0}
        
        if model_name is None:
            # 첫 번째 모델 사용
            model_name = list(self.models.keys())[0]
        
        if model_name not in self.models:
            raise ValueError(f"모델을 찾을 수 없습니다: {model_name}")
        
        model = self.models[model_name]
        vectorizer = self.vectorizers.get(model_name)
        
        if not vectorizer:
            raise ValueError(f"벡터라이저를 찾을 수 없습니다: {model_name}")
        
        # 텍스트 전처리 및 벡터화
        processed_text = self.preprocess_text(text)
        text_vector = vectorizer.transform([processed_text])
        
        # 예측
        prediction = model.predict(text_vector)[0]
        confidence = model.predict_proba(text_vector).max()
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "model": model_name
        }
    
    def train_text_classifier(self, texts: List[str], labels: List[str], 
                            model_name: str = "naive_bayes") -> Dict[str, Any]:
        """텍스트 분류기 훈련"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn이 필요합니다.")
        
        if len(texts) != len(labels):
            raise ValueError("텍스트와 라벨의 개수가 일치하지 않습니다.")
        
        self.logger.info(f"텍스트 분류기 훈련 시작: {len(texts)}개 샘플")
        
        # 데이터 전처리
        processed_texts = self.preprocess_documents(texts)
        
        # 훈련/테스트 분할
        test_size = self.config["text_classification"]["test_size"]
        random_state = self.config["text_classification"]["random_state"]
        
        X_train, X_test, y_train, y_test = train_test_split(
            processed_texts, labels, test_size=test_size, random_state=random_state
        )
        
        # 벡터화
        vectorizer_config = self.config["vectorization"]
        if vectorizer_config["method"] == "tfidf":
            vectorizer = TfidfVectorizer(
                max_features=vectorizer_config["max_features"],
                ngram_range=vectorizer_config["ngram_range"],
                min_df=vectorizer_config["min_df"],
                max_df=vectorizer_config["max_df"]
            )
        else:
            vectorizer = CountVectorizer(
                max_features=vectorizer_config["max_features"],
                ngram_range=vectorizer_config["ngram_range"],
                min_df=vectorizer_config["min_df"],
                max_df=vectorizer_config["max_df"]
            )
        
        # 모델 선택
        if model_name == "naive_bayes":
            model = MultinomialNB()
        elif model_name == "logistic_regression":
            model = LogisticRegression(random_state=random_state)
        elif model_name == "random_forest":
            model = RandomForestClassifier(random_state=random_state)
        else:
            raise ValueError(f"지원하지 않는 모델: {model_name}")
        
        # 파이프라인 생성 및 훈련
        pipeline = Pipeline([
            ('vectorizer', vectorizer),
            ('classifier', model)
        ])
        
        pipeline.fit(X_train, y_train)
        
        # 평가
        y_pred = pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # 교차 검증
        cv_scores = cross_val_score(pipeline, processed_texts, labels, cv=5)
        
        # 모델 저장
        self.models[model_name] = pipeline.named_steps['classifier']
        self.vectorizers[model_name] = pipeline.named_steps['vectorizer']
        
        results = {
            "model_name": model_name,
            "accuracy": accuracy,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
            "classification_report": classification_report(y_test, y_pred, output_dict=True)
        }
        
        self.logger.info(f"텍스트 분류기 훈련 완료: 정확도 {accuracy:.3f}")
        return results
    
    def summarize_text(self, text: str, max_sentences: int = 3) -> str:
        """텍스트 요약"""
        if not text:
            return ""
        
        # 문장 분리
        sentences = sent_tokenize(text) if NLTK_AVAILABLE else text.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= max_sentences:
            return text
        
        # 문장 점수 계산 (간단한 방법)
        sentence_scores = []
        for sentence in sentences:
            # 문장 길이, 키워드 빈도 등으로 점수 계산
            processed_sentence = self.preprocess_text(sentence)
            tokens = processed_sentence.split()
            
            # 키워드 추출
            keywords = self.extract_keywords(sentence, method="frequency", top_k=5)
            keyword_words = set(word for word, _ in keywords)
            
            # 점수 계산
            score = len(tokens)  # 문장 길이
            score += sum(2 for token in tokens if token in keyword_words)  # 키워드 보너스
            
            sentence_scores.append((sentence, score))
        
        # 점수로 정렬하고 상위 문장 선택
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        selected_sentences = sentence_scores[:max_sentences]
        
        # 원래 순서로 정렬
        selected_sentences.sort(key=lambda x: sentences.index(x[0]))
        
        summary = '. '.join(sentence for sentence, _ in selected_sentences)
        return summary + '.' if not summary.endswith('.') else summary
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """개체명 추출 (간단한 규칙 기반)"""
        if not text:
            return {}
        
        entities = {
            "emails": [],
            "urls": [],
            "phone_numbers": [],
            "dates": []
        }
        
        # 이메일 추출
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities["emails"] = re.findall(email_pattern, text)
        
        # URL 추출
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        entities["urls"] = re.findall(url_pattern, text)
        
        # 전화번호 추출
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        entities["phone_numbers"] = re.findall(phone_pattern, text)
        
        # 날짜 추출 (간단한 패턴)
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        entities["dates"] = re.findall(date_pattern, text)
        
        return entities
    
    def calculate_text_similarity(self, text1: str, text2: str, method: str = "cosine") -> float:
        """텍스트 유사도 계산"""
        if not text1 or not text2:
            return 0.0
        
        if method == "cosine":
            return self._cosine_similarity(text1, text2)
        elif method == "jaccard":
            return self._jaccard_similarity(text1, text2)
        else:
            raise ValueError(f"지원하지 않는 방법: {method}")
    
    def _cosine_similarity(self, text1: str, text2: str) -> float:
        """코사인 유사도"""
        if not SKLEARN_AVAILABLE:
            return self._jaccard_similarity(text1, text2)
        
        # 텍스트 전처리
        processed_text1 = self.preprocess_text(text1)
        processed_text2 = self.preprocess_text(text2)
        
        # TF-IDF 벡터화
        vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = vectorizer.fit_transform([processed_text1, processed_text2])
            
            # 코사인 유사도 계산
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity
        except Exception as e:
            self.logger.warning(f"코사인 유사도 계산 실패: {e}")
            return self._jaccard_similarity(text1, text2)
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """자카드 유사도"""
        # 텍스트 전처리
        processed_text1 = self.preprocess_text(text1)
        processed_text2 = self.preprocess_text(text2)
        
        # 토큰화
        tokens1 = set(processed_text1.split())
        tokens2 = set(processed_text2.split())
        
        # 자카드 유사도 계산
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        
        return intersection / union if union > 0 else 0.0
    
    def save_model(self, model_name: str, filepath: str):
        """모델 저장"""
        if model_name not in self.models:
            raise ValueError(f"모델을 찾을 수 없습니다: {model_name}")
        
        import joblib
        
        model_data = {
            "model": self.models[model_name],
            "vectorizer": self.vectorizers.get(model_name),
            "config": self.config,
            "created_at": datetime.now().isoformat()
        }
        
        joblib.dump(model_data, filepath)
        self.logger.info(f"모델 저장 완료: {filepath}")
    
    def load_model(self, filepath: str) -> str:
        """모델 로드"""
        import joblib
        
        model_data = joblib.load(filepath)
        
        # 모델 복원
        for key, value in model_data.items():
            if key == "model":
                # 모델 이름 추정
                model_name = "loaded_model"
                self.models[model_name] = value
            elif key == "vectorizer":
                self.vectorizers[model_name] = value
            elif key == "config":
                self.config.update(value)
        
        self.logger.info(f"모델 로드 완료: {filepath}")
        return model_name
    
    def generate_report(self, texts: List[str] = None) -> Dict[str, Any]:
        """NLP 분석 리포트 생성"""
        report = {
            "nlp_processor_info": {
                "nltk_available": NLTK_AVAILABLE,
                "sklearn_available": SKLEARN_AVAILABLE,
                "models_trained": len(self.models),
                "config": self.config
            },
            "generated_at": datetime.now().isoformat()
        }
        
        if texts:
            # 텍스트 분석 통계
            total_chars = sum(len(text) for text in texts)
            total_words = sum(len(text.split()) for text in texts)
            avg_text_length = total_chars / len(texts) if texts else 0
            
            report["text_statistics"] = {
                "total_texts": len(texts),
                "total_characters": total_chars,
                "total_words": total_words,
                "average_text_length": avg_text_length
            }
        
        return report

# 사용 예시
if __name__ == "__main__":
    # NLP 프로세서 초기화
    nlp = NLPProcessor()
    
    # 샘플 텍스트
    sample_texts = [
        "I love this product! It's amazing and works perfectly.",
        "This is terrible. I hate it and want a refund.",
        "The service was okay, nothing special but not bad either.",
        "Excellent customer support and fast delivery. Highly recommended!",
        "Poor quality product, very disappointed with the purchase."
    ]
    
    # 텍스트 전처리
    processed_texts = nlp.preprocess_documents(sample_texts)
    print("전처리된 텍스트:", processed_texts[:2])
    
    # 감정 분석
    for text in sample_texts[:3]:
        sentiment = nlp.analyze_sentiment(text)
        print(f"텍스트: {text[:50]}...")
        print(f"감정: {sentiment['sentiment']}, 점수: {sentiment['score']:.3f}")
    
    # 키워드 추출
    keywords = nlp.extract_keywords(sample_texts[0], top_k=5)
    print("키워드:", keywords)
    
    # 텍스트 분류기 훈련 (라벨이 있는 경우)
    labels = ["positive", "negative", "neutral", "positive", "negative"]
    if SKLEARN_AVAILABLE:
        results = nlp.train_text_classifier(sample_texts, labels)
        print("분류기 훈련 결과:", results)
    
    # 텍스트 요약
    long_text = "This is a very long text that contains multiple sentences. " \
                "It talks about various topics and provides detailed information. " \
                "The goal is to create a summary that captures the main points. " \
                "This should be reduced to just a few key sentences."
    
    summary = nlp.summarize_text(long_text, max_sentences=2)
    print("요약:", summary) 