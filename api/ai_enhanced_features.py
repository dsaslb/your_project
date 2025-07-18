from flask import request
"""
AI 기능 고도화 모듈
매출/재고/고객 행동 예측, 자연어 처리 기능 제공
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor  # pyright: ignore
from sklearn.preprocessing import StandardScaler  # pyright: ignore
from sklearn.model_selection import train_test_split  # pyright: ignore
from sklearn.metrics import mean_squared_error, r2_score  # pyright: ignore
import joblib
import re
try:
    from textblob import TextBlob  # noqa  # pyright: ignore
except ImportError:
    TextBlob = None
try:
    import nltk  # noqa  # pyright: ignore
    from nltk.tokenize import word_tokenize  # noqa  # pyright: ignore
    from nltk.corpus import stopwords  # noqa  # pyright: ignore
    from nltk.stem import WordNetLemmatizer  # noqa  # pyright: ignore
except ImportError:
    nltk = None
    word_tokenize = None
    stopwords = None
    WordNetLemmatizer = None
    word_tokenize = None
    stopwords = None
    WordNetLemmatizer = None
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class AIEnhancedFeatures:
    """AI 기능 고도화 클래스"""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.nlp_models = {}
        self.prediction_cache = {}

        # NLTK 데이터 다운로드
        if nltk:
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
                nltk.download('vader_lexicon', quiet=True)
            except Exception as e:
                logger.warning(f"NLTK 데이터 다운로드 실패: {e}")

    def predict_sales(self,  historical_data: List[Dict[str, Any]], forecast_days=30) -> Dict[str, Any]:
        """매출 예측"""
        try:
            if not historical_data:
                return {'error': '데이터가 부족합니다'}

            # 데이터 전처리
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            # 특성 엔지니어링
            df['day_of_week'] = df['date'].dt.dayofweek
            df['month'] = df['date'].dt.month
            df['quarter'] = df['date'].dt.quarter
            df['year'] = df['date'].dt.year
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

            # 이동평균 추가
            df['sales_ma7'] = df['sales'].rolling(window=7).mean()
            df['sales_ma30'] = df['sales'].rolling(window=30).mean()

            # 결측값 처리
            df = df.fillna(method='bfill')

            # 특성 선택
            features = ['day_of_week', 'month', 'quarter', 'year', 'is_weekend',
                        'sales_ma7', 'sales_ma30']
            X = df[features].dropna()
            y = df['sales'].loc[X.index]

            if len(X) < 10:
                return {'error': '훈련 데이터가 부족합니다'}

            # 모델 훈련
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)

            # 예측 데이터 생성
            last_date = df['date'].max()
            future_dates = pd.date_range(start=last_date + timedelta(days=1),
                                         periods=forecast_days, freq='D')

            future_df = pd.DataFrame({'date': future_dates})
            future_df['day_of_week'] = future_df['date'].dt.dayofweek
            future_df['month'] = future_df['date'].dt.month
            future_df['quarter'] = future_df['date'].dt.quarter
            future_df['year'] = future_df['date'].dt.year
            future_df['is_weekend'] = future_df['day_of_week'].isin([5, 6]).astype(int)

            # 이동평균 계산
            last_ma7 = df['sales'].tail(7).mean()
            last_ma30 = df['sales'].tail(30).mean()

            future_df['sales_ma7'] = last_ma7
            future_df['sales_ma30'] = last_ma30

            # 예측
            X_future = future_df[features]
            predictions = model.predict(X_future)

            # 신뢰구간 계산
            confidence_interval = self._calculate_confidence_interval(predictions, 0.95)

            return {
                'predictions': [
                    {
                        'date': date.strftime('%Y-%m-%d'),
                        'predicted_sales': round(pred, 2),
                        'lower_bound': round(ci[0], 2),
                        'upper_bound': round(ci[1], 2)
                    }
                    for date, pred, ci in zip(future_dates, predictions, confidence_interval)
                ],
                'model_accuracy': round(model.score(X, y), 3),
                'total_predicted_sales': round(sum(predictions), 2)
            }

        except Exception as e:
            logger.error(f"매출 예측 오류: {e}")
            return {'error': f'예측 중 오류 발생: {str(e)}'}

    def predict_inventory_needs(self, sales_data: List[Dict[str, Any]],
                                current_inventory: Dict[str, int],
                                lead_time_days: int = 7) -> Dict[str, Any]:
        """재고 필요량 예측"""
        try:
            if not sales_data:
                return {'error': '판매 데이터가 부족합니다'}

            df = pd.DataFrame(sales_data)

            # 제품별 일일 평균 판매량 계산
            daily_sales = df.groupby(['date', 'product_id'])['quantity'].sum().reset_index()
            avg_daily_sales = daily_sales.groupby('product_id')['quantity'].mean()

            # 안전재고 계산 (표준편차의 2배)
            daily_sales_std = daily_sales.groupby('product_id')['quantity'].std()
            safety_stock = daily_sales_std * 2

            # 예측 재고 필요량
            inventory_needs = {}
            for product_id in avg_daily_sales.index:
                avg_daily = avg_daily_sales[product_id]
                safety = safety_stock.get(product_id, avg_daily * 0.5) if safety_stock else avg_daily * 0.5
                current_stock = current_inventory.get(str(product_id), 0) if current_inventory else 0

                # 리드타임 동안 필요한 재고
                lead_time_needs = avg_daily * lead_time_days
                total_needs = lead_time_needs + safety

                # 추가 주문 필요량
                reorder_quantity = max(0, total_needs - current_stock)

                inventory_needs[str(product_id)] = {
                    'current_stock': current_stock,
                    'avg_daily_sales': round(float(avg_daily), 2),  # pyright: ignore
                    'safety_stock': round(float(safety), 2),        # pyright: ignore
                    'lead_time_needs': round(float(lead_time_needs), 2),  # pyright: ignore
                    'total_needs': round(float(total_needs), 2),    # pyright: ignore
                    'reorder_quantity': round(float(reorder_quantity), 2),  # pyright: ignore
                    'days_until_stockout': round(current_stock / avg_daily, 1) if avg_daily > 0 else float('inf')
                }

            return {
                'inventory_needs': inventory_needs,
                'total_reorder_value': sum(
                    needs['reorder_quantity'] for needs in inventory_needs.values()
                )
            }

        except Exception as e:
            logger.error(f"재고 예측 오류: {e}")
            return {'error': f'재고 예측 중 오류 발생: {str(e)}'}

    def analyze_customer_behavior(self, customer_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """고객 행동 분석"""
        try:
            if not customer_data:
                return {'error': '고객 데이터가 부족합니다'}

            df = pd.DataFrame(customer_data)

            # 고객 세그먼트 분석
            customer_segments = self._segment_customers(df)

            # 구매 패턴 분석
            purchase_patterns = self._analyze_purchase_patterns(df)

            # 고객 생애 가치 (CLV) 계산
            clv_analysis = self._calculate_customer_lifetime_value(df)

            # 이탈 위험 분석
            churn_risk = self._analyze_churn_risk(df)

            return {
                'customer_segments': customer_segments,
                'purchase_patterns': purchase_patterns,
                'customer_lifetime_value': clv_analysis,
                'churn_risk': churn_risk,
                'total_customers': len(df['customer_id'].unique()),
                'avg_order_value': round(df['order_value'].mean(), 2),
                'avg_purchase_frequency': round(df.groupby('customer_id').size().mean(), 2)
            }

        except Exception as e:
            logger.error(f"고객 행동 분석 오류: {e}")
            return {'error': f'고객 행동 분석 중 오류 발생: {str(e)}'}

    def natural_language_processing(self, text: str, task: str = 'sentiment') -> Dict[str, Any]:
        """자연어 처리"""
        try:
            if not text:
                return {'error': '텍스트가 비어있습니다'}

            # 텍스트 전처리
            processed_text = self._preprocess_text(text)

            if task == 'sentiment':
                return self._analyze_sentiment(processed_text)
            elif task == 'keywords':
                return self._extract_keywords(processed_text)
            elif task == 'summary':
                return self._generate_summary(processed_text)
            elif task == 'intent':
                return self._classify_intent(processed_text)
            else:
                return {'error': f'지원하지 않는 작업: {task}'}

        except Exception as e:
            logger.error(f"자연어 처리 오류: {e}")
            return {'error': f'자연어 처리 중 오류 발생: {str(e)}'}

    def _calculate_confidence_interval(self, predictions: np.ndarray, confidence: float = 0.95) -> List[Tuple[float, float]]:
        """신뢰구간 계산"""
        std_dev = np.std(predictions)
        z_score = 1.96  # 95% 신뢰구간

        intervals = []
        for pred in predictions:
            margin_of_error = z_score * std_dev
            lower = max(0, pred - margin_of_error)
            upper = pred + margin_of_error
            intervals.append((lower, upper))

        return intervals

    def _segment_customers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """고객 세그먼트 분석"""
        customer_stats = df.groupby('customer_id').agg({
            'order_value': ['sum', 'mean', 'count'],
            'order_date': ['min', 'max']
        }).reset_index()

        customer_stats.columns = ['customer_id', 'total_spent', 'avg_order_value',
                                  'order_count', 'first_order', 'last_order']

        # RFM 분석
        customer_stats['recency'] = (pd.Timestamp.now() - customer_stats['last_order']).dt.days
        customer_stats['frequency'] = customer_stats['order_count']
        customer_stats['monetary'] = customer_stats['total_spent']

        # 세그먼트 분류
        def classify_segment(row):
            if row['recency'] <= 30 and row['frequency'] >= 5 and row['monetary'] >= 1000:
                return 'VIP'
            elif row['recency'] <= 60 and row['frequency'] >= 3:
                return 'Loyal'
            elif row['recency'] <= 90:
                return 'At Risk'
            else:
                return 'Churned'

        customer_stats['segment'] = customer_stats.apply(classify_segment, axis=1)

        return {
            'segments': customer_stats['segment'].value_counts().to_dict(),
            'segment_details': customer_stats.to_dict('records')
        }

    def _analyze_purchase_patterns(self,  df: pd.DataFrame) -> Dict[str, Any]:
        """구매 패턴 분석"""
        # 시간대별 구매 패턴
        df['hour'] = pd.to_datetime(df['order_date']).dt.hour
        hourly_pattern = df.groupby('hour')['order_value'].sum().to_dict()

        # 요일별 구매 패턴
        df['day_of_week'] = pd.to_datetime(df['order_date']).dt.day_name()
        daily_pattern = df.groupby('day_of_week')['order_value'].sum().to_dict()

        # 월별 구매 패턴
        df['month'] = pd.to_datetime(df['order_date']).dt.month
        monthly_pattern = df.groupby('month')['order_value'].sum().to_dict()

        return {
            'hourly_pattern': hourly_pattern,
            'daily_pattern': daily_pattern,
            'monthly_pattern': monthly_pattern
        }

    def _calculate_customer_lifetime_value(self, df: pd.DataFrame) -> Dict[str, Any]:
        """고객 생애 가치 계산"""
        customer_stats = df.groupby('customer_id').agg({
            'order_value': ['sum', 'mean', 'count'],
            'order_date': ['min', 'max']
        }).reset_index()

        customer_stats.columns = ['customer_id', 'total_spent', 'avg_order_value',
                                  'order_count', 'first_order', 'last_order']

        # 고객 생애 기간 계산
        customer_stats['lifetime_days'] = (customer_stats['last_order'] - customer_stats['first_order']).dt.days

        # CLV 계산 (간단한 모델)
        customer_stats['clv'] = customer_stats['total_spent'] * (customer_stats['order_count'] /
                                                                 (customer_stats['lifetime_days'] + 1))

        return {
            'avg_clv': round(float(customer_stats['clv'].mean()), 2),
            'total_clv': round(float(customer_stats['clv'].sum()), 2),
            'clv_distribution': {
                'high_value': len(customer_stats[customer_stats['clv'] > customer_stats['clv'].quantile(0.8)]),
                'medium_value': len(customer_stats[(customer_stats['clv'] > customer_stats['clv'].quantile(0.2)) &
                                                   (customer_stats['clv'] <= customer_stats['clv'].quantile(0.8))]),
                'low_value': len(customer_stats[customer_stats['clv'] <= customer_stats['clv'].quantile(0.2)])
            }
        }

    def _analyze_churn_risk(self, df: pd.DataFrame) -> Dict[str, Any]:
        """이탈 위험 분석"""
        customer_stats = df.groupby('customer_id').agg({
            'order_date': ['min', 'max', 'count']
        }).reset_index()

        customer_stats.columns = ['customer_id', 'first_order', 'last_order', 'order_count']
        customer_stats['days_since_last_order'] = (pd.Timestamp.now() - customer_stats['last_order']).dt.days

        # 이탈 위험 분류
        def classify_churn_risk(row):
            if row['days_since_last_order'] > 90:
                return 'High'
            elif row['days_since_last_order'] > 60:
                return 'Medium'
            elif row['days_since_last_order'] > 30:
                return 'Low'
            else:
                return 'Very Low'

        customer_stats['churn_risk'] = customer_stats.apply(classify_churn_risk, axis=1)

        return {
            'risk_distribution': customer_stats['churn_risk'].value_counts().to_dict(),
            'high_risk_customers': len(customer_stats[customer_stats['churn_risk'] == 'High']),
            'avg_days_since_last_order': round(customer_stats['days_since_last_order'].mean(), 1)
        }

    def _preprocess_text(self,  text: str) -> str:
        """텍스트 전처리"""
        # 소문자 변환
        text = text.lower() if text is not None else ''

        # 특수문자 제거
        text = re.sub(r'[^\w\s]', '', text)

        # 숫자 제거
        text = re.sub(r'\d+', '', text)

        # 불용어 제거
        try:
            if stopwords and word_tokenize:
                stop_words = set(stopwords.words('english'))
                words = word_tokenize(text)
                words = [word for word in words if word not in stop_words]
                text = ' '.join(words)
        except Exception:
            pass

        return text

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """감정 분석"""
        try:
            if TextBlob:
                blob = TextBlob(text)
                sentiment_score = blob.sentiment.polarity
                if sentiment_score > 0.1:
                    sentiment = 'positive'
                elif sentiment_score < -0.1:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'
                return {
                    'sentiment': sentiment,
                    'sentiment_score': round(sentiment_score, 3),
                    'subjectivity': round(blob.sentiment.subjectivity, 3)
                }
            else:
                return {'error': 'TextBlob 라이브러리가 설치되어 있지 않습니다.'}
        except Exception as e:
            return {'error': f'감정 분석 실패: {str(e)}'}

    def _extract_keywords(self, text: str) -> Dict[str, Any]:
        """키워드 추출"""
        try:
            if word_tokenize:
                words = word_tokenize(text)
            else:
                words = text.split()

            # 단어 빈도 계산
            word_freq = {}
            for word in words:
                if len(word) > 2:  # 2글자 이하 제외
                    word_freq[word] = word_freq.get(word, 0) + 1

            # 상위 키워드 추출
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

            return {
                'keywords': [{'word': word, 'frequency': freq} for word, freq in top_keywords],
                'total_words': len(words),
                'unique_words': len(word_freq)
            }
        except Exception as e:
            return {'error': f'키워드 추출 실패: {str(e)}'}

    def _generate_summary(self, text: str) -> Dict[str, Any]:
        """텍스트 요약"""
        try:
            sentences = text.split('.')
            sentences = [s.strip() for s in sentences if s and s.strip()]

            if len(sentences) <= 3:
                summary = text
            else:
                # 간단한 요약 (첫 3문장)
                summary = '. '.join(sentences[:3] if sentences is not None else None) + '.'

            return {
                'summary': summary,
                'original_length': len(text),
                'summary_length': len(summary),
                'compression_ratio': round(len(summary) / len(text), 3)
            }
        except Exception as e:
            return {'error': f'요약 생성 실패: {str(e)}'}

    def _classify_intent(self, text: str) -> Dict[str, Any]:
        """의도 분류"""
        try:
            text_lower = text.lower() if text is not None else ''

            # 의도 키워드 매칭
            intents = {
                'question': ['what', 'how', 'when', 'where', 'why', 'who', '?'],
                'complaint': ['problem', 'issue', 'error', 'wrong', 'bad', 'terrible'],
                'compliment': ['good', 'great', 'excellent', 'amazing', 'wonderful'],
                'request': ['please', 'can you', 'could you', 'would you', 'need'],
                'order': ['order', 'buy', 'purchase', 'checkout', 'cart']
            }

            detected_intents = []
            for intent, keywords in intents.items():
                if any(keyword in text_lower for keyword in keywords):
                    detected_intents.append(intent)

            if not detected_intents:
                detected_intents = ['general']

            return {
                'intents': detected_intents,
                'primary_intent': detected_intents[0] if detected_intents is not None else None,
                'confidence': 0.8 if len(detected_intents) == 1 else 0.6
            }
        except Exception as e:
            return {'error': f'의도 분류 실패: {str(e)}'}


# 전역 인스턴스
ai_enhanced_features = AIEnhancedFeatures()


def predict_sales_forecast(historical_data: List[Dict[str, Any]], forecast_days: int = 30) -> Dict[str, Any]:
    """매출 예측"""
    return ai_enhanced_features.predict_sales(historical_data,  forecast_days)


def predict_inventory_requirements(sales_data: List[Dict[str, Any]],
                                   current_inventory: Dict[str, int],
                                   lead_time_days: int = 7) -> Dict[str, Any]:
    """재고 필요량 예측"""
    return ai_enhanced_features.predict_inventory_needs(sales_data, current_inventory, lead_time_days)


def analyze_customer_behavior_patterns(customer_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """고객 행동 분석"""
    return ai_enhanced_features.analyze_customer_behavior(customer_data)


def process_natural_language(text: str, task: str = 'sentiment') -> Dict[str, Any]:
    """자연어 처리"""
    return ai_enhanced_features.natural_language_processing(text, task)
