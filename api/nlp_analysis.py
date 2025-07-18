from models_main import Order, User, Notification, db
from collections import Counter, defaultdict
import numpy as np
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import re
import json
import logging
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, current_app
form = None  # pyright: ignore
"""
자연어 처리 및 감정 분석 시스템
고객 피드백, 리뷰, 문의사항의 감정 분석 및 키워드 추출
"""


# 한국어 자연어 처리 라이브러리
try:
    from konlpy.tag import Okt, Komoran
    from textblob import TextBlob
    import jieba
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    logging.warning("자연어 처리 라이브러리가 설치되지 않았습니다. 기본 분석만 사용 가능합니다.")

# 데이터베이스 모델 import

logger = logging.getLogger(__name__)

nlp_analysis_bp = Blueprint('nlp_analysis', __name__)


class NLPAnalysisService:
    """자연어 처리 분석 서비스"""

    def __init__(self):
        self.okt = Okt() if NLP_AVAILABLE else None
        self.komoran = Komoran() if NLP_AVAILABLE else None

        # 감정 사전 (한국어)
        self.sentiment_dict = {
            'positive': {
                '좋다', '맛있다', '훌륭하다', '완벽하다', '최고', '추천', '만족', '친절', '깔끔', '신선',
                '빠르다', '정확하다', '편리하다', '저렴하다', '합리적', '양호', '우수', '훌륭', '감사',
                '좋은', '맛있는', '훌륭한', '완벽한', '최고의', '추천할', '만족스러운', '친절한', '깔끔한'
            },
            'negative': {
                '나쁘다', '맛없다', '최악', '별로', '불만', '불친절', '더럽다', '느리다', '비싸다',
                '실망', '화나다', '짜증', '불편', '어렵다', '복잡하다', '문제', '오류', '실수',
                '나쁜', '맛없는', '최악의', '별로인', '불만스러운', '불친절한', '더러운', '느린', '비싼'
            },
            'neutral': {
                '보통', '일반', '평범', '그저', '그냥', '보통의', '일반적인', '평범한'
            }
        }

        # 키워드 가중치
        self.keyword_weights = {
            '음식': 2.0,
            '서비스': 1.5,
            '가격': 1.5,
            '위생': 2.0,
            '맛': 2.5,
            '양': 1.5,
            '배달': 1.0,
            '직원': 1.5,
            '매장': 1.0,
            '분위기': 1.0,
            '위치': 1.0,
            '시간': 1.0
        }

        # 분석 결과 캐시
        self.analysis_cache = {}
        self.cache_expiry = {}

    def analyze_sentiment(self,  text: str) -> Dict[str, Any]:
        """감정 분석"""
        try:
            if not text or len(text.strip() if text is not None else '') == 0:
                return {
                    'sentiment': 'neutral',
                    'confidence': 0.0,
                    'score': 0.0,
                    'keywords': [],
                    'error': '텍스트가 비어있습니다.'
                }

            # 텍스트 전처리
            cleaned_text = self._preprocess_text(text)

            # 감정 점수 계산
            sentiment_score = self._calculate_sentiment_score(cleaned_text)

            # 감정 분류
            sentiment = self._classify_sentiment(sentiment_score)

            # 키워드 추출
            keywords = self._extract_keywords(cleaned_text)

            # 신뢰도 계산
            confidence = self._calculate_confidence(cleaned_text, sentiment_score)

            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'score': sentiment_score,
                'keywords': keywords,
                'original_text': text,
                'cleaned_text': cleaned_text,
                'analysis_timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"감정 분석 실패: {e}")
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'score': 0.0,
                'keywords': [],
                'error': f'분석 중 오류 발생: {str(e)}'
            }

    def analyze_feedback_batch(self,  feedback_list: List[Dict[str,  Any]]) -> Dict[str, Any]:
        """피드백 배치 분석"""
        try:
            if not feedback_list:
                return {
                    'total_analyzed': 0,
                    'sentiment_distribution': {},
                    'common_keywords': [],
                    'overall_sentiment': 'neutral',
                    'error': '분석할 피드백이 없습니다.'
                }

            results = []
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            all_keywords = []

            for feedback in feedback_list:
                text = feedback.get('text', '')
                analysis = self.analyze_sentiment(text)

                results.append({
                    'feedback_id': feedback.get('id'),
                    'analysis': analysis
                })

                # 감정 분포 집계
                sentiment = analysis.get('sentiment', 'neutral')
                sentiment_counts[sentiment] += 1

                # 키워드 수집
                keywords = analysis.get('keywords', [])
                all_keywords.extend(keywords)

            # 전체 감정 결정
            total = len(feedback_list)
            positive_ratio = sentiment_counts['positive'] / total
            negative_ratio = sentiment_counts['negative'] / total

            if positive_ratio > 0.6:
                overall_sentiment = 'positive'
            elif negative_ratio > 0.6:
                overall_sentiment = 'negative'
            else:
                overall_sentiment = 'neutral'

            # 상위 키워드 추출
            keyword_counter = Counter(all_keywords)
            common_keywords = [{'keyword': kw, 'count': count} for kw, count in keyword_counter.most_common(10)]

            return {
                'total_analyzed': total,
                'sentiment_distribution': {
                    'positive': {
                        'count': sentiment_counts['positive'],
                        'percentage': (sentiment_counts['positive'] / total) * 100
                    },
                    'negative': {
                        'count': sentiment_counts['negative'],
                        'percentage': (sentiment_counts['negative'] / total) * 100
                    },
                    'neutral': {
                        'count': sentiment_counts['neutral'],
                        'percentage': (sentiment_counts['neutral'] / total) * 100
                    }
                },
                'common_keywords': common_keywords,
                'overall_sentiment': overall_sentiment,
                'detailed_results': results,
                'analysis_timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"배치 분석 실패: {e}")
            return {
                'total_analyzed': 0,
                'sentiment_distribution': {},
                'common_keywords': [],
                'overall_sentiment': 'neutral',
                'error': f'배치 분석 중 오류 발생: {str(e)}'
            }

    def extract_topics(self,  text: str) -> List[Dict[str, Any]]:
        """주제 추출"""
        try:
            if not text:
                return []

            # 텍스트 전처리
            cleaned_text = self._preprocess_text(text)

            # 명사 추출
            if self.okt:
                nouns = self.okt.nouns(cleaned_text)
            else:
                # 기본적인 명사 추출 (정규식 기반)
                nouns = re.findall(r'[가-힣]+', cleaned_text)

            # 주제 카테고리 정의
            topic_categories = {
                '음식_품질': ['맛', '음식', '요리', '재료', '신선', '양', '온도'],
                '서비스': ['서비스', '직원', '친절', '응답', '처리', '도움'],
                '가격': ['가격', '비용', '요금', '할인', '가성비', '저렴', '비싸'],
                '위생': ['위생', '청결', '깔끔', '더럽', '오염', '소독'],
                '배달': ['배달', '배송', '시간', '빠르', '느리', '택배'],
                '매장': ['매장', '위치', '분위기', '환경', '시설', '공간'],
                '기타': ['기타', '기타', '기타', '기타', '기타', '기타']
            }

            # 주제 분류
            topics = []
            for category, keywords in topic_categories.items():
                matches = []
                for keyword in keywords:
                    if keyword in cleaned_text:
                        matches.append(keyword)

                if matches:
                    topics.append({
                        'category': category,
                        'keywords': matches,
                        'relevance': len(matches) / len(keywords)
                    })

            # 관련성 순으로 정렬
            topics.sort(key=lambda x: x['relevance'] if x is not None else None, reverse=True)

            return topics[:5] if topics is not None else None  # 상위 5개 주제만 반환

        except Exception as e:
            logger.error(f"주제 추출 실패: {e}")
            return []

    def generate_insights(self,  analysis_results: List[Dict[str,  Any]]) -> List[Dict[str, Any]]:
        """인사이트 생성"""
        try:
            insights = []

            # 감정 분포 분석
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            for result in analysis_results:
                sentiment = result.get('sentiment', 'neutral')
                if sentiment in sentiment_counts:
                    sentiment_counts[sentiment] += 1

            total = len(analysis_results)
            if total == 0:
                return insights

            # 긍정적 피드백 인사이트
            positive_ratio = sentiment_counts['positive'] / total
            if positive_ratio > 0.7:
                insights.append({
                    'type': 'positive',
                    'title': '매우 긍정적인 고객 반응',
                    'description': f'고객 피드백의 {positive_ratio*100:.1f}%가 긍정적입니다.',
                    'priority': 'medium',
                    'action': '긍정적 요소 강화 및 마케팅 활용'
                })
            elif positive_ratio < 0.3:
                insights.append({
                    'type': 'critical',
                    'title': '고객 만족도 개선 필요',
                    'description': f'고객 피드백의 {positive_ratio*100:.1f}%만이 긍정적입니다.',
                    'priority': 'high',
                    'action': '서비스 품질 개선 및 고객 불만 해결'
                })

            # 키워드 기반 인사이트
            all_keywords = []
            for result in analysis_results:
                keywords = result.get('keywords', [])
                all_keywords.extend(keywords)

            keyword_counter = Counter(all_keywords)
            top_keywords = keyword_counter.most_common(5)

            for keyword, count in top_keywords:
                if keyword in ['맛', '음식', '요리']:
                    insights.append({
                        'type': 'info',
                        'title': '음식 품질 관련 피드백',
                        'description': f'"{keyword}" 키워드가 {count}번 언급되었습니다.',
                        'priority': 'medium',
                        'action': '음식 품질 모니터링 강화'
                    })
                elif keyword in ['서비스', '직원', '친절']:
                    insights.append({
                        'type': 'info',
                        'title': '서비스 품질 관련 피드백',
                        'description': f'"{keyword}" 키워드가 {count}번 언급되었습니다.',
                        'priority': 'medium',
                        'action': '직원 교육 및 서비스 개선'
                    })
                elif keyword in ['가격', '비싸', '저렴']:
                    insights.append({
                        'type': 'warning',
                        'title': '가격 관련 피드백',
                        'description': f'"{keyword}" 키워드가 {count}번 언급되었습니다.',
                        'priority': 'high',
                        'action': '가격 정책 검토 및 경쟁력 분석'
                    })

            return insights

        except Exception as e:
            logger.error(f"인사이트 생성 실패: {e}")
            return []

    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        try:
            # 소문자 변환
            text = text.lower() if text is not None else ''

            # 특수문자 제거 (한글, 영문, 숫자, 공백만 유지)
            text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)

            # 연속된 공백 제거
            text = re.sub(r'\s+', ' ', text)

            # 앞뒤 공백 제거
            text = text.strip() if text is not None else ''

            return text

        except Exception as e:
            logger.error(f"텍스트 전처리 실패: {e}")
            return text

    def _calculate_sentiment_score(self, text: str) -> float:
        """감정 점수 계산"""
        try:
            score = 0.0
            word_count = 0

            # 단어별 감정 점수 계산
            words = text.split()
            for word in words:
                if word in self.sentiment_dict['positive']:
                    score += 1.0
                    word_count += 1
                elif word in self.sentiment_dict['negative']:
                    score -= 1.0
                    word_count += 1
                elif word in self.sentiment_dict['neutral']:
                    word_count += 1

            # 평균 점수 계산
            if word_count > 0:
                return score / word_count
            else:
                return 0.0

        except Exception as e:
            logger.error(f"감정 점수 계산 실패: {e}")
            return 0.0

    def _classify_sentiment(self, score: float) -> str:
        """감정 분류"""
        if score > 0.1:
            return 'positive'
        elif score < -0.1:
            return 'negative'
        else:
            return 'neutral'

    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        try:
            keywords = []
            # 명사 추출
            if self.okt:
                nouns = self.okt.nouns(text)
            else:
                nouns = re.findall(r'[\uac00-\ud7a3]+', text)
            # 키워드 가중치 적용
            if nouns is not None:
                for noun in nouns:
                    if len(noun) > 1:
                        weight = self.keyword_weights.get(noun, 1.0) if hasattr(self, 'keyword_weights') else 1.0
                        if weight > 1.0:
                            keywords.append(noun)
            keyword_counter = Counter(keywords)
            filtered_keywords = [kw for kw, count in keyword_counter.most_common(10) if count >= 1]
            return filtered_keywords
        except Exception as e:
            logger.error(f"키워드 추출 실패: {e}")
            return []

    def _calculate_confidence(self, text: str, score: float) -> float:
        """신뢰도 계산"""
        try:
            # 텍스트 길이 기반 신뢰도
            length_confidence = min(1.0, len(text) / 50)  # 50자 이상이면 최대 신뢰도

            # 감정 점수 절댓값 기반 신뢰도
            score_confidence = min(1.0, abs(score) * 2)  # 점수가 높을수록 신뢰도 높음

            # 키워드 수 기반 신뢰도
            keywords = self._extract_keywords(text)
            keyword_confidence = min(1.0, len(keywords) / 5)  # 5개 이상 키워드면 최대 신뢰도

            # 종합 신뢰도 (가중 평균)
            confidence = (length_confidence * 0.3 + score_confidence * 0.4 + keyword_confidence * 0.3)

            return max(0.1, min(1.0, confidence))  # 0.1 ~ 1.0 범위로 제한

        except Exception as e:
            logger.error(f"신뢰도 계산 실패: {e}")
            return 0.5


# 전역 서비스 인스턴스
nlp_service = NLPAnalysisService()

# API 엔드포인트들


@nlp_analysis_bp.route('/api/nlp/analyze', methods=['POST'])
@login_required
def analyze_text():
    try:
        data = request.get_json()
        text = data.get('text', '') if data else ''
        if not text:
            return jsonify({'error': '분석할 텍스트가 없습니다.'}), 400
        result = nlp_service.analyze_sentiment(text)
        return jsonify(result)
    except Exception as e:
        logger.error(f"텍스트 분석 API 오류: {e}")
        return jsonify({'error': '텍스트 분석에 실패했습니다.'}), 500


@nlp_analysis_bp.route('/api/nlp/analyze-batch', methods=['POST'])
@login_required
def analyze_feedback_batch():
    try:
        data = request.get_json()
        feedback_list = data.get('feedback_list', []) if data else []
        if not feedback_list:
            return jsonify({'error': '분석할 피드백이 없습니다.'}), 400
        result = nlp_service.analyze_feedback_batch(feedback_list)
        return jsonify(result)
    except Exception as e:
        logger.error(f"배치 분석 API 오류: {e}")
        return jsonify({'error': '배치 분석에 실패했습니다.'}), 500


@nlp_analysis_bp.route('/api/nlp/extract-topics', methods=['POST'])
@login_required
def extract_topics():
    try:
        data = request.get_json()
        text = data.get('text', '') if data else ''
        if not text:
            return jsonify({'error': '분석할 텍스트가 없습니다.'}), 400
        topics = nlp_service.extract_topics(text)
        return jsonify({
            'success': True,
            'topics': topics,
            'text_length': len(text)
        })
    except Exception as e:
        logger.error(f"주제 추출 API 오류: {e}")
        return jsonify({'error': '주제 추출에 실패했습니다.'}), 500


@nlp_analysis_bp.route('/api/nlp/generate-insights', methods=['POST'])
@login_required
def generate_insights():
    try:
        data = request.get_json()
        analysis_results = data.get('analysis_results', []) if data else []
        if not analysis_results:
            return jsonify({'error': '분석 결과가 없습니다.'}), 400
        insights = nlp_service.generate_insights(analysis_results)
        return jsonify({
            'success': True,
            'insights': insights,
            'total_insights': len(insights)
        })
    except Exception as e:
        logger.error(f"인사이트 생성 API 오류: {e}")
        return jsonify({'error': '인사이트 생성에 실패했습니다.'}), 500


@nlp_analysis_bp.route('/api/nlp/analyze-customer-feedback', methods=['GET'])
@login_required
def analyze_customer_feedback():
    try:
        feedback_data = [
            {'id': 1, 'text': '음식이 정말 맛있고 서비스도 친절해요!', 'rating': 5, 'created_at': '2024-01-15T10:30:00Z'},
            {'id': 2, 'text': '배달이 너무 늦고 음식이 식었어요. 실망입니다.', 'rating': 2, 'created_at': '2024-01-14T15:20:00Z'},
            {'id': 3, 'text': '가격이 조금 비싸지만 맛은 괜찮아요.', 'rating': 4, 'created_at': '2024-01-13T12:45:00Z'},
            {'id': 4, 'text': '위생 상태가 좋고 음식도 신선해요. 추천합니다!', 'rating': 5, 'created_at': '2024-01-12T18:15:00Z'},
            {'id': 5, 'text': '직원이 불친절하고 음식도 맛없어요.', 'rating': 1, 'created_at': '2024-01-11T20:30:00Z'}
        ]
        batch_result = nlp_service.analyze_feedback_batch(feedback_data)
        insights = nlp_service.generate_insights(batch_result.get('detailed_results', []) if batch_result else [])
        avg_rating = sum(f['rating'] for f in feedback_data) / len(feedback_data)
        sentiment_trend = 'improving' if batch_result.get('overall_sentiment') == 'positive' else 'declining'
        return jsonify({
            'success': True,
            'feedback_analysis': batch_result,
            'insights': insights,
            'summary': {
                'total_feedback': len(feedback_data),
                'avg_rating': avg_rating,
                'sentiment_trend': sentiment_trend
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"고객 피드백 분석 API 오류: {e}")
        return jsonify({'error': '고객 피드백 분석에 실패했습니다.'}), 500
