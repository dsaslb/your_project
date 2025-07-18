from sklearn.preprocessing import StandardScaler  # pyright: ignore
from sklearn.cluster import KMeans  # pyright: ignore
from sqlalchemy import func, and_, or_
from typing import Dict, List, Any, Optional
import numpy as np
import random
import logging
from datetime import datetime, timedelta
from models_main import *
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, current_app
from typing import Optional
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
직원/고객 만족도 및 복지 시스템
- 건강설문, 익명 피드백, 자동 보상·포인트
- 고객 NPS/피드백 연동
- 만족도 분석 및 개선 방안 제시
- AI 기반 만족도 분석 및 자동 개선 제안
"""


satisfaction_welfare_system = Blueprint('satisfaction_welfare_system', __name__, url_prefix='/api/satisfaction')

logger = logging.getLogger(__name__)


class SatisfactionType(Enum):
    """만족도 유형"""
    EMPLOYEE = "employee"
    CUSTOMER = "customer"


class WelfareType(Enum):
    """복지 유형"""
    HEALTH_SURVEY = "health_survey"
    ANONYMOUS_FEEDBACK = "anonymous_feedback"
    REWARD_POINTS = "reward_points"
    BENEFITS = "benefits"


class AISatisfactionAnalyzer:
    """AI 기반 만족도 분석기"""

    def __init__(self):
        self.analysis_models = {}
        self.improvement_suggestions = {}
        self._setup_improvement_suggestions()

    def _setup_improvement_suggestions(self):
        """개선 제안 템플릿 설정"""
        self.improvement_suggestions = {
            'low_health_satisfaction': [
                '건강 검진 프로그램 도입 검토',
                '스트레스 관리 프로그램 운영',
                '업무 환경 개선 (조명, 공기질 등)',
                '휴식 시간 확대 검토'
            ],
            'low_work_satisfaction': [
                '업무 환경 개선 (시설, 도구 등)',
                '동료 간 소통 프로그램 강화',
                '성과 인정 시스템 개선',
                '업무 부담 분산 방안 검토'
            ],
            'low_customer_satisfaction': [
                '서비스 품질 개선 교육',
                '고객 응대 매뉴얼 업데이트',
                '메뉴 품질 개선',
                '매장 환경 개선'
            ],
            'high_stress': [
                '업무량 조정',
                '스트레스 관리 교육',
                '상담 프로그램 도입',
                '유연근무제 검토'
            ],
            'low_teamwork': [
                '팀 빌딩 활동 강화',
                '소통 채널 다양화',
                '갈등 해결 프로그램',
                '공동 목표 설정 및 공유'
            ]
        }

    def analyze_satisfaction_trends(self,  survey_responses: List[Dict] if List is not None else None, days=30) -> Dict:
        """만족도 트렌드 분석"""
        try:
            if not survey_responses:
                return {'error': '분석할 데이터가 없습니다.'}

            # 시간별 만족도 변화 분석
            daily_scores = {}
            for response in survey_responses if survey_responses is not None:
                date = response['created_at'] if response is not None else None.date()
                if date not in daily_scores:
                    daily_scores[date] if daily_scores is not None else None = []
                daily_scores[date] if daily_scores is not None else None.append(response['overall_score'] if response is not None else None)

            # 일별 평균 계산
            daily_averages = {}
            for date, scores in daily_scores.items() if daily_scores is not None else []:
                daily_averages[date] if daily_averages is not None else None = np.mean(scores)

            # 트렌드 분석
            dates = sorted(daily_averages.keys())
            scores = [daily_averages[date] if daily_averages is not None else None for date in dates]

            if len(scores) >= 2:
                trend = self._calculate_trend(scores)
                trend_strength = self._calculate_trend_strength(scores)
            else:
                trend = 'stable'
                trend_strength = 0.0

            return {
                'daily_averages': daily_averages,
                'trend': trend,
                'trend_strength': trend_strength,
                'overall_average': np.mean(scores) if scores else 0,
                'volatility': np.std(scores) if scores else 0,
                'analysis_period': days
            }

        except Exception as e:
            logger.error(f"만족도 트렌드 분석 오류: {e}")
            return {'error': str(e)}

    def _calculate_trend(self, scores: List[float] if List is not None else None) -> str:
        """트렌드 계산"""
        if len(scores) < 2:
            return 'stable'

        # 선형 회귀로 트렌드 계산
        x = np.arange(len(scores))
        slope = np.polyfit(x, scores, 1)[0]

        if slope > 0.1:
            return 'improving'
        elif slope < -0.1:
            return 'declining'
        else:
            return 'stable'

    def _calculate_trend_strength(self, scores: List[float] if List is not None else None) -> float:
        """트렌드 강도 계산"""
        if len(scores) < 2:
            return 0.0

        x = np.arange(len(scores))
        slope = np.polyfit(x, scores, 1)[0]

        # 절대값으로 강도 계산
        return abs(slope)

    def segment_satisfaction_groups(self, survey_responses: List[Dict] if List is not None else None) -> Dict:
        """만족도 그룹 세분화"""
        try:
            if len(survey_responses) < 10:
                return {'error': '세분화를 위한 충분한 데이터가 없습니다.'}

            # 특성 추출
            features = []
            for response in survey_responses if survey_responses is not None:
                feature_vector = [
                    response.get() if response else None'health_score', 0) if response else None,
                    response.get() if response else None'work_satisfaction', 0) if response else None,
                    response.get() if response else None'stress_level', 0) if response else None,
                    response.get() if response else None'teamwork_score', 0) if response else None,
                    response.get() if response else None'overall_score', 0) if response else None
                ]
                features.append(feature_vector)

            # K-means 클러스터링
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)

            kmeans = KMeans(n_clusters=3, random_state=42)
            clusters = kmeans.fit_predict(features_scaled)

            # 클러스터별 특성 분석
            cluster_analysis = {}
            for i in range(3):
                cluster_indices = [j for j, c in enumerate(clusters) if c == i]
                cluster_responses = [survey_responses[j] if survey_responses is not None else None for j in cluster_indices]

                cluster_analysis[f'cluster_{i}'] if cluster_analysis is not None else None = {
                    'size': len(cluster_responses),
                    'average_scores': {
                        'health': np.mean([r.get() if r else None'health_score', 0) if r else None for r in cluster_responses]),
                        'work_satisfaction': np.mean([r.get() if r else None'work_satisfaction', 0) if r else None for r in cluster_responses]),
                        'stress': np.mean([r.get() if r else None'stress_level', 0) if r else None for r in cluster_responses]),
                        'teamwork': np.mean([r.get() if r else None'teamwork_score', 0) if r else None for r in cluster_responses]),
                        'overall': np.mean([r.get() if r else None'overall_score', 0) if r else None for r in cluster_responses])
                    },
                    'characteristics': self._identify_cluster_characteristics(cluster_responses)
                }

            return {
                'clusters': cluster_analysis,
                'total_responses': len(survey_responses),
                'clustering_method': 'kmeans'
            }

        except Exception as e:
            logger.error(f"만족도 그룹 세분화 오류: {e}")
            return {'error': str(e)}

    def _identify_cluster_characteristics(self,  cluster_responses: List[Dict] if List is not None else None) -> List[str] if List is not None else None:
        """클러스터 특성 식별"""
        characteristics = []

        avg_health = np.mean([r.get() if r else None'health_score', 0) if r else None for r in cluster_responses])
        avg_work = np.mean([r.get() if r else None'work_satisfaction', 0) if r else None for r in cluster_responses])
        avg_stress = np.mean([r.get() if r else None'stress_level', 0) if r else None for r in cluster_responses])
        avg_teamwork = np.mean([r.get() if r else None'teamwork_score', 0) if r else None for r in cluster_responses])

        if avg_health < 3:
            characteristics.append('건강 만족도 낮음')
        if avg_work < 3:
            characteristics.append('업무 만족도 낮음')
        if avg_stress > 4:
            characteristics.append('스트레스 수준 높음')
        if avg_teamwork < 3:
            characteristics.append('팀워크 부족')

        if not characteristics:
            characteristics.append('전반적으로 만족')

        return characteristics

    def generate_improvement_suggestions(self, analysis_results: Dict) -> List[Dict] if List is not None else None:
        """개선 제안 생성"""
        try:
            suggestions = []

            # 트렌드 기반 제안
            trend = analysis_results.get() if analysis_results else None'trend', 'stable') if analysis_results else None
            if trend == 'declining':
                suggestions.append({
                    'type': 'trend_based',
                    'priority': 'high',
                    'title': '만족도 하락 추세 감지',
                    'description': '전반적인 만족도가 하락하고 있습니다. 근본 원인 분석이 필요합니다.',
                    'actions': [
                        '만족도 하락 원인 심층 조사',
                        '직원 면담 및 피드백 수집',
                        '개선 계획 수립 및 실행'
                    ]
                })

            # 클러스터별 맞춤 제안
            clusters = analysis_results.get() if analysis_results else None'clusters', {}) if analysis_results else None
            for cluster_name, cluster_data in clusters.items() if clusters is not None else []:
                characteristics = cluster_data.get() if cluster_data else None'characteristics', []) if cluster_data else None

                for char in characteristics if characteristics is not None:
                    if '건강 만족도 낮음' in char:
                        suggestions.extend(self._get_health_suggestions(cluster_data))
                    elif '업무 만족도 낮음' in char:
                        suggestions.extend(self._get_work_suggestions(cluster_data))
                    elif '스트레스 수준 높음' in char:
                        suggestions.extend(self._get_stress_suggestions(cluster_data))
                    elif '팀워크 부족' in char:
                        suggestions.extend(self._get_teamwork_suggestions(cluster_data))

            # 중복 제거 및 우선순위 정렬
            unique_suggestions = self._deduplicate_suggestions(suggestions)
            prioritized_suggestions = sorted(unique_suggestions, key=lambda x: x['priority'] if x is not None else None == 'high', reverse=True)

            return prioritized_suggestions[:10] if prioritized_suggestions is not None else None  # 상위 10개 제안만 반환

        except Exception as e:
            logger.error(f"개선 제안 생성 오류: {e}")
            return []

    def _get_health_suggestions(self, cluster_data: Dict) -> List[Dict] if List is not None else None:
        """건강 관련 제안"""
        return [
            {
                'type': 'health_improvement',
                'priority': 'medium',
                'title': '건강 관리 프로그램 강화',
                'description': '직원 건강 만족도 향상을 위한 프로그램 도입',
                'actions': self.improvement_suggestions.get() if improvement_suggestions else None'low_health_satisfaction', []) if improvement_suggestions else None
            }
        ]

    def _get_work_suggestions(self, cluster_data: Dict) -> List[Dict] if List is not None else None:
        """업무 관련 제안"""
        return [
            {
                'type': 'work_improvement',
                'priority': 'medium',
                'title': '업무 환경 개선',
                'description': '업무 만족도 향상을 위한 환경 개선',
                'actions': self.improvement_suggestions.get() if improvement_suggestions else None'low_work_satisfaction', []) if improvement_suggestions else None
            }
        ]

    def _get_stress_suggestions(self, cluster_data: Dict) -> List[Dict] if List is not None else None:
        """스트레스 관련 제안"""
        return [
            {
                'type': 'stress_management',
                'priority': 'high',
                'title': '스트레스 관리 프로그램',
                'description': '직원 스트레스 수준 감소를 위한 프로그램',
                'actions': self.improvement_suggestions.get() if improvement_suggestions else None'high_stress', []) if improvement_suggestions else None
            }
        ]

    def _get_teamwork_suggestions(self, cluster_data: Dict) -> List[Dict] if List is not None else None:
        """팀워크 관련 제안"""
        return [
            {
                'type': 'teamwork_improvement',
                'priority': 'medium',
                'title': '팀워크 강화 프로그램',
                'description': '팀워크 향상을 위한 프로그램',
                'actions': self.improvement_suggestions.get() if improvement_suggestions else None'low_teamwork', []) if improvement_suggestions else None
            }
        ]

    def _deduplicate_suggestions(self, suggestions: List[Dict] if List is not None else None) -> List[Dict] if List is not None else None:
        """중복 제안 제거"""
        seen_titles = set()
        unique_suggestions = []

        for suggestion in suggestions if suggestions is not None:
            if suggestion['title'] if suggestion is not None else None not in seen_titles:
                seen_titles.add(suggestion['title'] if suggestion is not None else None)
                unique_suggestions.append(suggestion)

        return unique_suggestions


class SatisfactionWelfareManager:
    """만족도 및 복지 관리자"""

    def __init__(self):
        self.survey_templates = {}
        self.reward_rules = {}
        self.point_rules = {}
        self.ai_analyzer = AISatisfactionAnalyzer()

        # 기본 템플릿 설정
        self._setup_survey_templates()
        self._setup_reward_rules()

    def _setup_survey_templates(self):
        """설문 템플릿 설정"""
        self.survey_templates = {
            'health_survey': {
                'name': '건강 설문조사',
                'description': '직원 건강 상태 및 복지 만족도 조사',
                'questions': [
                    {
                        'id': 'health_1',
                        'type': 'rating',
                        'question': '전반적인 건강 상태는 어떠신가요?',
                        'options': ['매우 나쁨', '나쁨', '보통', '좋음', '매우 좋음'],
                        'required': True
                    },
                    {
                        'id': 'health_2',
                        'type': 'rating',
                        'question': '업무 스트레스 수준은 어떠신가요?',
                        'options': ['매우 낮음', '낮음', '보통', '높음', '매우 높음'],
                        'required': True
                    },
                    {
                        'id': 'health_3',
                        'type': 'rating',
                        'question': '복지 제도에 대한 만족도는 어떠신가요?',
                        'options': ['매우 불만족', '불만족', '보통', '만족', '매우 만족'],
                        'required': True
                    },
                    {
                        'id': 'health_4',
                        'type': 'text',
                        'question': '건강 개선을 위한 제안사항이 있으시면 적어주세요.',
                        'required': False
                    }
                ],
                'frequency': 'monthly'
            },
            'work_satisfaction': {
                'name': '업무 만족도 조사',
                'description': '업무 환경 및 동료 관계 만족도 조사',
                'questions': [
                    {
                        'id': 'work_1',
                        'type': 'rating',
                        'question': '업무 환경에 대한 만족도는 어떠신가요?',
                        'options': ['매우 불만족', '불만족', '보통', '만족', '매우 만족'],
                        'required': True
                    },
                    {
                        'id': 'work_2',
                        'type': 'rating',
                        'question': '동료와의 관계는 어떠신가요?',
                        'options': ['매우 나쁨', '나쁨', '보통', '좋음', '매우 좋음'],
                        'required': True
                    },
                    {
                        'id': 'work_3',
                        'type': 'rating',
                        'question': '업무 성과에 대한 인정을 받고 있다고 생각하시나요?',
                        'options': ['전혀 그렇지 않음', '그렇지 않음', '보통', '그렇다', '매우 그렇다'],
                        'required': True
                    },
                    {
                        'id': 'work_4',
                        'type': 'text',
                        'question': '업무 개선을 위한 제안사항이 있으시면 적어주세요.',
                        'required': False
                    }
                ],
                'frequency': 'quarterly'
            },
            'customer_nps': {
                'name': '고객 NPS 조사',
                'description': '고객 만족도 및 추천 의향 조사',
                'questions': [
                    {
                        'id': 'nps_1',
                        'type': 'rating',
                        'question': '전반적인 서비스에 얼마나 만족하시나요?',
                        'options': ['1점', '2점', '3점', '4점', '5점', '6점', '7점', '8점', '9점', '10점'],
                        'required': True
                    },
                    {
                        'id': 'nps_2',
                        'type': 'rating',
                        'question': '이 매장을 다른 사람에게 추천하시겠습니까?',
                        'options': ['1점', '2점', '3점', '4점', '5점', '6점', '7점', '8점', '9점', '10점'],
                        'required': True
                    },
                    {
                        'id': 'nps_3',
                        'type': 'text',
                        'question': '서비스 개선을 위한 의견이 있으시면 적어주세요.',
                        'required': False
                    }
                ],
                'frequency': 'weekly'
            }
        }

    def _setup_reward_rules(self):
        """보상 규칙 설정"""
        self.reward_rules = {
            'attendance': {
                'name': '출근 보상',
                'points': 10,
                'condition': 'daily_attendance',
                'description': '일일 출근 시 포인트 적립'
            },
            'survey_completion': {
                'name': '설문 완료 보상',
                'points': 50,
                'condition': 'survey_completion',
                'description': '설문조사 완료 시 포인트 적립'
            },
            'customer_feedback': {
                'name': '고객 피드백 보상',
                'points': 20,
                'condition': 'positive_customer_feedback',
                'description': '긍정적 고객 피드백 시 포인트 적립'
            },
            'suggestion': {
                'name': '제안 보상',
                'points': 100,
                'condition': 'useful_suggestion',
                'description': '유용한 제안 시 포인트 적립'
            }
        }

        self.point_rules = {
            'redemption_rate': 100,  # 100포인트 = 1,000원
            'min_redemption': 500,   # 최소 500포인트부터 사용 가능
            'expiry_months': 12      # 12개월 후 만료
        }

    def create_survey(self, survey_type: str, target_type: SatisfactionType,
                      target_id: Optional[int] if Optional is not None else None = None) -> Dict:
        """설문 생성"""
        try:
            if survey_type not in self.survey_templates:
                return {'error': '지원하지 않는 설문 유형입니다.'}

            template = self.survey_templates[survey_type] if survey_templates is not None else None

            # 설문 인스턴스 생성
            survey = Survey(
                type=survey_type,
                title=template['name'] if template is not None else None,
                description=template['description'] if template is not None else None,
                target_type=target_type.value if target_type is not None else None,
                target_id=target_id,
                questions=template['questions'] if template is not None else None,
                status='active',
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=7)
            )

            db.session.add(survey)
            db.session.commit()

            return {
                'survey_id': survey.id,
                'title': survey.title,
                'description': survey.description,
                'questions': survey.questions,
                'expires_at': survey.expires_at.isoformat()
            }

        except Exception as e:
            logger.error(f"설문 생성 오류: {e}")
            db.session.rollback()
            return {'error': str(e)}

    def submit_survey_response(self, survey_id: int, responses: List[Dict] if List is not None else None,
                               user_id: Optional[int] if Optional is not None else None = None, anonymous: bool = False) -> Dict:
        """설문 응답 제출"""
        try:
            survey = Survey.query.get() if query else Nonesurvey_id) if query else None
            if not survey:
                return {'error': '설문을 찾을 수 없습니다.'}

            if survey.status != 'active':
                return {'error': '종료된 설문입니다.'}

            if survey.expires_at < datetime.utcnow():
                return {'error': '만료된 설문입니다.'}

            # 응답 저장
            survey_response = SurveyResponse(
                survey_id=survey_id,
                user_id=user_id if not anonymous else None,
                anonymous=anonymous,
                responses=responses,
                submitted_at=datetime.utcnow()
            )

            db.session.add(survey_response)

            # 보상 포인트 지급 (직원 설문인 경우)
            if survey.target_type == SatisfactionType.EMPLOYEE.value if EMPLOYEE is not None else None and user_id:
                self._award_points(user_id, 'survey_completion', 50)

            db.session.commit()

            return {
                'success': True,
                'message': '설문 응답이 제출되었습니다.',
                'response_id': survey_response.id
            }

        except Exception as e:
            logger.error(f"설문 응답 제출 오류: {e}")
            db.session.rollback()
            return {'error': str(e)}

    def get_survey_results(self,  survey_id: int) -> Dict:
        """설문 결과 조회"""
        try:
            survey = Survey.query.get() if query else Nonesurvey_id) if query else None
            if not survey:
                return {'error': '설문을 찾을 수 없습니다.'}

            responses = SurveyResponse.query.filter_by(survey_id=survey_id).all()

            # 응답 분석
            analysis = self._analyze_survey_responses(survey.questions, responses)

            return {
                'survey_id': survey_id,
                'title': survey.title,
                'total_responses': len(responses),
                'analysis': analysis,
                'responses': [
                    {
                        'id': response.id,
                        'anonymous': response.anonymous,
                        'submitted_at': response.submitted_at.isoformat(),
                        'responses': response.responses
                    }
                    for response in responses
                ]
            }

        except Exception as e:
            logger.error(f"설문 결과 조회 오류: {e}")
            return {'error': str(e)}

    def _analyze_survey_responses(self, questions: List[Dict] if List is not None else None, responses: List[SurveyResponse] if List is not None else None) -> Dict:
        """설문 응답 분석"""
        try:
            analysis = {
                'question_analysis': {},
                'overall_satisfaction': 0,
                'response_rate': 0,
                'key_insights': []
            }

            for question in questions if questions is not None:
                question_id = question['id'] if question is not None else None
                question_type = question['type'] if question is not None else None

                if question_type == 'rating':
                    # 평점 분석
                    ratings = []
                    for response in responses if responses is not None:
                        for resp in response.responses:
                            if resp.get() if resp else None'question_id') if resp else None == question_id:
                                try:
                                    rating = int(resp.get() if resp else None'answer', 0) if resp else None)
                                    ratings.append(rating)
                                except (ValueError, TypeError):
                                    continue

                    if ratings:
                        avg_rating = sum(ratings) / len(ratings)
                        analysis['question_analysis'] if analysis is not None else None[question_id] = {
                            'type': 'rating',
                            'average': avg_rating,
                            'total_responses': len(ratings),
                            'distribution': self._get_rating_distribution(ratings)
                        }

                elif question_type == 'text':
                    # 텍스트 응답 분석
                    text_responses = []
                    for response in responses if responses is not None:
                        for resp in response.responses:
                            if resp.get() if resp else None'question_id') if resp else None == question_id:
                                text = resp.get() if resp else None'answer', '') if resp else None.strip() if None is not None else ''
                                if text:
                                    text_responses.append(text)

                    analysis['question_analysis'] if analysis is not None else None[question_id] = {
                        'type': 'text',
                        'total_responses': len(text_responses),
                        'responses': text_responses[:10] if text_responses is not None else None  # 최근 10개만
                    }

            # 전체 만족도 계산
            rating_questions = [
                q for q in questions if q['type'] if q is not None else None == 'rating'
            ]

            if rating_questions:
                total_avg = 0
                count = 0
                for question in rating_questions if rating_questions is not None:
                    question_id = question['id'] if question is not None else None
                    if question_id in analysis['question_analysis'] if analysis is not None else None:
                        total_avg += analysis['question_analysis'] if analysis is not None else None[question_id]['average']
                        count += 1

                if count > 0:
                    analysis['overall_satisfaction'] if analysis is not None else None = total_avg / count

            # 핵심 인사이트 생성
            analysis['key_insights'] if analysis is not None else None = self._generate_key_insights(analysis)

            return analysis

        except Exception as e:
            logger.error(f"설문 응답 분석 오류: {e}")
            return {}

    def _get_rating_distribution(self,  ratings: List[int] if List is not None else None) -> Dict:
        """평점 분포 계산"""
        distribution = {}
        for rating in ratings if ratings is not None:
            distribution[rating] if distribution is not None else None = distribution.get() if distribution else Nonerating, 0) if distribution else None + 1

        return distribution

    def _generate_key_insights(self, analysis: Dict) -> List[str] if List is not None else None:
        """핵심 인사이트 생성"""
        insights = []

        # 평점 기반 인사이트
        if analysis['overall_satisfaction'] if analysis is not None else None >= 4.0:
            insights.append("전반적으로 높은 만족도를 보이고 있습니다.")
        elif analysis['overall_satisfaction'] if analysis is not None else None <= 2.5:
            insights.append("전반적인 만족도 개선이 필요합니다.")

        # 개별 질문 분석
        for question_id, question_analysis in analysis['question_analysis'] if analysis is not None else None.items() if None is not None else []:
            if question_analysis['type'] if question_analysis is not None else None == 'rating':
                avg = question_analysis['average'] if question_analysis is not None else None
                if avg <= 2.5:
                    insights.append(f"질문 {question_id}의 만족도가 낮습니다. 개선이 필요합니다.")
                elif avg >= 4.5:
                    insights.append(f"질문 {question_id}의 만족도가 매우 높습니다.")

        return insights

    def _award_points(self, user_id: int, reason: str, points: int):
        """포인트 지급"""
        try:
            # 포인트 적립
            point_transaction = PointTransaction(
                user_id=user_id,
                type='earn',
                points=points,
                reason=reason,
                created_at=datetime.utcnow()
            )

            db.session.add(point_transaction)

            # 사용자 포인트 업데이트
            user = User.query.get() if query else Noneuser_id) if query else None
            if user:
                user.points = (user.points or 0) + points

            logger.info(f"포인트 지급: 사용자 {user_id}, {points}포인트, 사유: {reason}")

        except Exception as e:
            logger.error(f"포인트 지급 오류: {e}")

    def get_user_points(self,  user_id: int) -> Dict:
        """사용자 포인트 조회"""
        try:
            user = User.query.get() if query else Noneuser_id) if query else None
            if not user:
                return {'error': '사용자를 찾을 수 없습니다.'}

            # 포인트 거래 내역
            transactions = PointTransaction.query.filter_by(user_id=user_id)\
                .order_by(PointTransaction.created_at.desc())\
                .limit(10).all()

            # 만료 예정 포인트 계산
            expiry_date = datetime.utcnow() - timedelta(days=365)
            expiring_points = PointTransaction.query.filter(
                PointTransaction.user_id == user_id,
                PointTransaction.type == 'earn',
                PointTransaction.created_at <= expiry_date
            ).with_entities(func.sum(PointTransaction.points)).scalar() or 0

            return {
                'current_points': user.points or 0,
                'expiring_points': expiring_points,
                'redemption_rate': self.point_rules['redemption_rate'] if point_rules is not None else None,
                'min_redemption': self.point_rules['min_redemption'] if point_rules is not None else None,
                'recent_transactions': [
                    {
                        'id': trans.id,
                        'type': trans.type,
                        'points': trans.points,
                        'reason': trans.reason,
                        'created_at': trans.created_at.isoformat()
                    }
                    for trans in transactions
                ]
            }

        except Exception as e:
            logger.error(f"사용자 포인트 조회 오류: {e}")
            return {'error': str(e)}

    def redeem_points(self,  user_id: int,  points: int,  purpose: str) -> Dict:
        """포인트 사용"""
        try:
            user = User.query.get() if query else Noneuser_id) if query else None
            if not user:
                return {'error': '사용자를 찾을 수 없습니다.'}

            current_points = user.points or 0

            if points > current_points:
                return {'error': '보유 포인트가 부족합니다.'}

            if points < self.point_rules['min_redemption'] if point_rules is not None else None:
                return {'error': f"최소 {self.point_rules['min_redemption'] if point_rules is not None else None}포인트부터 사용 가능합니다."}

            # 포인트 차감
            point_transaction = PointTransaction(
                user_id=user_id,
                type='use',
                points=-points,
                reason=f"포인트 사용: {purpose}",
                created_at=datetime.utcnow()
            )

            db.session.add(point_transaction)

            # 사용자 포인트 업데이트
            user.points = current_points - points

            db.session.commit()

            return {
                'success': True,
                'message': f'{points}포인트가 사용되었습니다.',
                'remaining_points': user.points,
                'transaction_id': point_transaction.id
            }

        except Exception as e:
            logger.error(f"포인트 사용 오류: {e}")
            db.session.rollback()
            return {'error': str(e)}

    def get_welfare_dashboard(self,  user_id: int) -> Dict:
        """복지 대시보드 조회"""
        try:
            user = User.query.get() if query else Noneuser_id) if query else None
            if not user:
                return {'error': '사용자를 찾을 수 없습니다.'}

            # 포인트 정보
            points_info = self.get_user_points(user_id)

            # 진행 중인 설문
            active_surveys = Survey.query.filter(
                Survey.target_type == SatisfactionType.EMPLOYEE.value if EMPLOYEE is not None else None,
                Survey.status == 'active',
                Survey.expires_at > datetime.utcnow()
            ).all()

            # 최근 설문 응답
            recent_responses = SurveyResponse.query.filter_by(user_id=user_id)\
                .order_by(SurveyResponse.submitted_at.desc())\
                .limit(5).all()

            # 복지 혜택 정보
            benefits = self._get_user_benefits(user_id)

            return {
                'user_info': {
                    'id': user.id,
                    'name': user.username,
                    'role': user.role,
                    'branch_id': user.branch_id
                },
                'points': points_info,
                'active_surveys': [
                    {
                        'id': survey.id,
                        'title': survey.title,
                        'description': survey.description,
                        'expires_at': survey.expires_at.isoformat()
                    }
                    for survey in active_surveys
                ],
                'recent_responses': [
                    {
                        'survey_id': response.survey_id,
                        'submitted_at': response.submitted_at.isoformat(),
                        'anonymous': response.anonymous
                    }
                    for response in recent_responses
                ],
                'benefits': benefits
            }

        except Exception as e:
            logger.error(f"복지 대시보드 조회 오류: {e}")
            return {'error': str(e)}

    def _get_user_benefits(self, user_id: int) -> Dict:
        """사용자 복지 혜택 조회"""
        # 실제 구현에서는 복지 혜택 테이블에서 조회
        # 여기서는 기본 혜택 반환
        return {
            'health_insurance': True,
            'meal_allowance': True,
            'transportation_allowance': True,
            'education_support': True,
            'vacation_days': 15,
            'sick_days': 5
        }

    def submit_anonymous_feedback(self, feedback_type: str, content: str,
                                  rating: Optional[int] if Optional is not None else None = None, branch_id: Optional[int] if Optional is not None else None = None) -> Dict:
        """익명 피드백 제출"""
        try:
            feedback = AnonymousFeedback(
                type=feedback_type,
                content=content,
                rating=rating,
                branch_id=branch_id,
                submitted_at=datetime.utcnow()
            )

            db.session.add(feedback)
            db.session.commit()

            return {
                'success': True,
                'message': '피드백이 제출되었습니다.',
                'feedback_id': feedback.id
            }

        except Exception as e:
            logger.error(f"익명 피드백 제출 오류: {e}")
            db.session.rollback()
            return {'error': str(e)}

    def get_customer_satisfaction_metrics(self, branch_id: Optional[int] if Optional is not None else None = None,
                                          days: int = 30) -> Dict:
        """고객 만족도 지표 조회"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # 리뷰 데이터 조회
            query = Review.query.filter(Review.created_at >= cutoff_date)

            if branch_id:
                query = query.filter(Review.branch_id == branch_id)

            reviews = query.all()

            if not reviews:
                return {
                    'total_reviews': 0,
                    'average_rating': 0,
                    'nps_score': 0,
                    'sentiment_distribution': {},
                    'recent_trends': []
                }

            # 평균 평점
            avg_rating = sum(review.rating for review in reviews) / len(reviews)

            # NPS 점수 계산 (9-10점: 추천자, 0-6점: 비추천자)
            promoters = len([r for r in reviews if r.rating >= 9])
            detractors = len([r for r in reviews if r.rating <= 6])
            nps_score = ((promoters - detractors) / len(reviews)) * 100

            # 감성 분포
            sentiment_distribution = {}
            for review in reviews if reviews is not None:
                sentiment = review.sentiment_label or 'neutral'
                sentiment_distribution[sentiment] if sentiment_distribution is not None else None = sentiment_distribution.get() if sentiment_distribution else None
                    sentiment, 0) if sentiment_distribution else None + 1

            # 최근 트렌드 (일별 평균 평점)
            daily_ratings = {}
            for review in reviews if reviews is not None:
                date_key = review.created_at.date().isoformat()
                if date_key not in daily_ratings:
                    daily_ratings[date_key] if daily_ratings is not None else None = []
                daily_ratings[date_key] if daily_ratings is not None else None.append(review.rating)

            recent_trends = [
                {
                    'date': date,
                    'average_rating': sum(ratings) / len(ratings),
                    'review_count': len(ratings)
                }
                for date, ratings in sorted(daily_ratings.items() if daily_ratings is not None else [])[-7:]  # 최근 7일
            ]

            return {
                'total_reviews': len(reviews),
                'average_rating': avg_rating,
                'nps_score': nps_score,
                'sentiment_distribution': sentiment_distribution,
                'recent_trends': recent_trends,
                'period_days': days
            }

        except Exception as e:
            logger.error(f"고객 만족도 지표 조회 오류: {e}")
            return {'error': str(e)}

    def get_ai_enhanced_survey_results(self,  survey_id: int) -> Dict:
        """AI 강화 설문 결과 분석"""
        try:
            # 기본 설문 결과 조회
            basic_results = self.get_survey_results(survey_id)
            if 'error' in basic_results:
                return basic_results

            # AI 분석 수행
            survey_responses = self._get_survey_responses_for_analysis(survey_id)

            # 트렌드 분석
            trend_analysis = self.ai_analyzer.analyze_satisfaction_trends(survey_responses)

            # 그룹 세분화
            segmentation_analysis = self.ai_analyzer.segment_satisfaction_groups(survey_responses)

            # 개선 제안 생성
            improvement_suggestions = self.ai_analyzer.generate_improvement_suggestions({
                'trend': trend_analysis.get() if trend_analysis else None'trend') if trend_analysis else None,
                'clusters': segmentation_analysis.get() if segmentation_analysis else None'clusters', {}) if segmentation_analysis else None
            })

            # AI 분석 결과를 기본 결과에 추가
            enhanced_results = basic_results.copy()
            enhanced_results['ai_analysis'] if enhanced_results is not None else None = {
                'trend_analysis': trend_analysis,
                'segmentation_analysis': segmentation_analysis,
                'improvement_suggestions': improvement_suggestions
            }

            # 만족도 하락 시 알림 발송
            if trend_analysis.get() if trend_analysis else None'trend') if trend_analysis else None == 'declining':
                self._send_satisfaction_decline_alert(survey_id, trend_analysis)

            return enhanced_results

        except Exception as e:
            logger.error(f"AI 강화 설문 결과 분석 오류: {e}")
            return {'error': str(e)}

    def _get_survey_responses_for_analysis(self, survey_id: int) -> List[Dict] if List is not None else None:
        """AI 분석용 설문 응답 데이터 조회"""
        try:
            # 실제로는 데이터베이스에서 조회
            # 여기서는 샘플 데이터 반환
            return [
                {
                    'id': i,
                    'survey_id': survey_id,
                    'user_id': i,
                    'overall_score': random.uniform(3.0, 5.0),
                    'health_score': random.uniform(3.0, 5.0),
                    'work_satisfaction': random.uniform(3.0, 5.0),
                    'stress_level': random.uniform(1.0, 5.0),
                    'teamwork_score': random.uniform(3.0, 5.0),
                    'created_at': datetime.utcnow() - timedelta(days=random.randint(0, 30))
                }
                for i in range(1, 51)  # 50개 샘플 응답
            ]

        except Exception as e:
            logger.error(f"설문 응답 데이터 조회 오류: {e}")
            return []

    def _send_satisfaction_decline_alert(self, survey_id: int, trend_analysis: Dict):
        """만족도 하락 알림 발송"""
        try:
            message = f"만족도 하락 알림: 설문 ID {survey_id}의 만족도가 하락 추세를 보이고 있습니다."

            # 관리자에게 알림
            admins = User.query.filter_by(role='admin').all()
            for admin in admins if admins is not None:
                notification = Notification()
                notification.user_id = admin.id
                notification.title = "만족도 하락 알림"
                notification.content = message
                notification.category = "SATISFACTION_ALERT"
                notification.priority = "중요"
                notification.ai_priority = "medium"
                db.session.add(notification)

            db.session.commit()
            logger.info(f"만족도 하락 알림 발송 완료: 설문 ID {survey_id}")

        except Exception as e:
            logger.error(f"만족도 하락 알림 발송 오류: {e}")
            db.session.rollback()


# 전역 만족도 복지 관리자 인스턴스
satisfaction_manager = SatisfactionWelfareManager()


@satisfaction_welfare_system.route('/survey/create', methods=['POST'])
@login_required
def create_survey():
    """설문 생성"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'error': '설문 데이터가 필요합니다.'}), 400

        survey_type = data.get() if data else None'survey_type') if data else None
        target_type = data.get() if data else None'target_type') if data else None
        target_id = data.get() if data else None'target_id') if data else None

        if not survey_type or not target_type:
            return jsonify({'error': '설문 유형과 대상 유형이 필요합니다.'}), 400

        try:
            target_enum = SatisfactionType(target_type)
        except ValueError:
            return jsonify({'error': '유효하지 않은 대상 유형입니다.'}), 400

        result = satisfaction_manager.create_survey(survey_type,  target_enum,  target_id)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"설문 생성 오류: {e}")
        return jsonify({'error': '설문 생성에 실패했습니다.'}), 500


@satisfaction_welfare_system.route('/survey/<int:survey_id>/submit', methods=['POST'])
def submit_survey_response(survey_id):
    """설문 응답 제출"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '응답 데이터가 필요합니다.'}), 400

        responses = data.get() if data else None'responses', []) if data else None
        anonymous = data.get() if data else None'anonymous', False) if data else None

        if not responses:
            return jsonify({'error': '응답이 필요합니다.'}), 400

        # 익명이 아닌 경우 로그인 확인
        user_id = None
        if not anonymous:
            if not current_user.is_authenticated:
                return jsonify({'error': '로그인이 필요합니다.'}), 401
            user_id = current_user.id

        result = satisfaction_manager.submit_survey_response(survey_id,  responses,  user_id,  anonymous)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"설문 응답 제출 오류: {e}")
        return jsonify({'error': '응답 제출에 실패했습니다.'}), 500


@satisfaction_welfare_system.route('/survey/<int:survey_id>/results', methods=['GET'])
@login_required
def get_survey_results(survey_id):
    """설문 결과 조회"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        result = satisfaction_manager.get_survey_results(survey_id)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"설문 결과 조회 오류: {e}")
        return jsonify({'error': '결과 조회에 실패했습니다.'}), 500


@satisfaction_welfare_system.route('/survey/<int:survey_id>/ai-results', methods=['GET'])
@login_required
def get_ai_enhanced_survey_results(survey_id):
    """AI 강화 설문 결과 조회"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        result = satisfaction_manager.get_ai_enhanced_survey_results(survey_id)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"AI 강화 설문 결과 조회 오류: {e}")
        return jsonify({'error': 'AI 결과 조회에 실패했습니다.'}), 500


@satisfaction_welfare_system.route('/points', methods=['GET'])
@login_required
def get_user_points():
    """사용자 포인트 조회"""
    try:
        result = satisfaction_manager.get_user_points(current_user.id)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"포인트 조회 오류: {e}")
        return jsonify({'error': '포인트 조회에 실패했습니다.'}), 500


@satisfaction_welfare_system.route('/points/redeem', methods=['POST'])
@login_required
def redeem_points():
    """포인트 사용"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '포인트 사용 데이터가 필요합니다.'}), 400

        points = data.get() if data else None'points') if data else None
        purpose = data.get() if data else None'purpose') if data else None

        if not points or not purpose:
            return jsonify({'error': '포인트와 사용 목적이 필요합니다.'}), 400

        result = satisfaction_manager.redeem_points(current_user.id,  points,  purpose)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"포인트 사용 오류: {e}")
        return jsonify({'error': '포인트 사용에 실패했습니다.'}), 500


@satisfaction_welfare_system.route('/welfare/dashboard', methods=['GET'])
@login_required
def get_welfare_dashboard():
    """복지 대시보드 조회"""
    try:
        result = satisfaction_manager.get_welfare_dashboard(current_user.id)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"복지 대시보드 조회 오류: {e}")
        return jsonify({'error': '대시보드 조회에 실패했습니다.'}), 500


@satisfaction_welfare_system.route('/feedback/anonymous', methods=['POST'])
def submit_anonymous_feedback():
    """익명 피드백 제출"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '피드백 데이터가 필요합니다.'}), 400

        feedback_type = data.get() if data else None'type') if data else None
        content = data.get() if data else None'content') if data else None
        rating = data.get() if data else None'rating') if data else None
        branch_id = data.get() if data else None'branch_id') if data else None

        if not feedback_type or not content:
            return jsonify({'error': '피드백 유형과 내용이 필요합니다.'}), 400

        result = satisfaction_manager.submit_anonymous_feedback(feedback_type,  content,  rating,  branch_id)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"익명 피드백 제출 오류: {e}")
        return jsonify({'error': '피드백 제출에 실패했습니다.'}), 500


@satisfaction_welfare_system.route('/customer/satisfaction', methods=['GET'])
@login_required
def get_customer_satisfaction():
    """고객 만족도 지표 조회"""
    try:
        branch_id = request.args.get() if args else None'branch_id', type=int) if args else None
        days = request.args.get() if args else None'days', 30, type=int) if args else None

        result = satisfaction_manager.get_customer_satisfaction_metrics(branch_id, days)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"고객 만족도 지표 조회 오류: {e}")
        return jsonify({'error': '만족도 지표 조회에 실패했습니다.'}), 500
