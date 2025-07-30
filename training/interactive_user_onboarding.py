#!/usr/bin/env python3
"""
🎓 Your Program 대화형 사용자 온보딩 시스템

신규 사용자가 플랫폼을 효과적으로 학습하고 활용할 수 있도록
단계별 가이드와 실습을 제공하는 인터랙티브 온보딩 시스템입니다.

주요 기능:
- 역할별 맞춤형 온보딩 경로
- 실시간 진행률 추적
- 인터랙티브 튜토리얼
- 실습 환경 제공
- 성과 평가 및 인증
- 지속적인 학습 지원
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import sqlite3
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class OnboardingStep:
    """온보딩 단계 정의"""
    step_id: str
    title: str
    description: str
    content_type: str  # 'tutorial', 'practice', 'quiz', 'demo'
    content_data: Dict[str, Any]
    estimated_time: int  # 분
    prerequisites: List[str]
    completion_criteria: Dict[str, Any]
    is_optional: bool = False

@dataclass
class UserProgress:
    """사용자 진행 상황"""
    user_id: str
    user_role: str
    current_step: str
    completed_steps: List[str]
    start_time: datetime
    last_activity: datetime
    total_time_spent: int  # 분
    quiz_scores: Dict[str, float]
    practice_results: Dict[str, bool]
    overall_progress: float  # 0-100%
    certification_earned: List[str]

@dataclass
class LearningPath:
    """학습 경로 정의"""
    path_id: str
    path_name: str
    target_role: str
    description: str
    total_steps: int
    estimated_duration: int  # 분
    difficulty_level: str  # 'beginner', 'intermediate', 'advanced'
    steps: List[OnboardingStep]
    prerequisites: List[str]

class OnboardingManager:
    """온보딩 관리 클래스"""
    
    def __init__(self, db_path: str = "training/onboarding.db"):
        self.db_path = db_path
        self.init_database()
        self.learning_paths = self._load_learning_paths()
        self.websocket_connections: Dict[str, WebSocket] = {}
        
    def init_database(self):
        """데이터베이스 초기화"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 사용자 진행상황 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                user_id TEXT PRIMARY KEY,
                user_role TEXT NOT NULL,
                current_step TEXT,
                completed_steps TEXT,
                start_time TEXT,
                last_activity TEXT,
                total_time_spent INTEGER DEFAULT 0,
                quiz_scores TEXT,
                practice_results TEXT,
                overall_progress REAL DEFAULT 0.0,
                certification_earned TEXT
            )
        """)
        
        # 학습 세션 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                step_id TEXT,
                start_time TEXT,
                end_time TEXT,
                duration INTEGER,
                success BOOLEAN,
                feedback TEXT,
                FOREIGN KEY (user_id) REFERENCES user_progress (user_id)
            )
        """)
        
        # 피드백 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                feedback_id TEXT PRIMARY KEY,
                user_id TEXT,
                step_id TEXT,
                rating INTEGER,
                comment TEXT,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES user_progress (user_id)
            )
        """)
        
        conn.commit()
        conn.close()
        
    def _load_learning_paths(self) -> Dict[str, LearningPath]:
        """학습 경로 로드"""
        paths = {}
        
        # 관리자 학습 경로
        admin_steps = [
            OnboardingStep(
                step_id="admin_welcome",
                title="🎯 관리자 환영 및 개요",
                description="Your Program 플랫폼의 관리자 역할과 책임을 이해합니다.",
                content_type="tutorial",
                content_data={
                    "video_url": "/static/videos/admin_welcome.mp4",
                    "slides": [
                        {
                            "title": "Your Program에 오신 것을 환영합니다!",
                            "content": "엔터프라이즈급 통합 플랫폼의 관리자로서 중요한 역할을 담당하게 됩니다.",
                            "image": "/static/images/welcome_admin.png"
                        },
                        {
                            "title": "관리자 주요 책임",
                            "content": "• 시스템 운영 및 모니터링\n• 사용자 관리 및 권한 설정\n• 보안 정책 수립 및 관리\n• 성능 최적화 및 문제 해결",
                            "image": "/static/images/admin_responsibilities.png"
                        },
                        {
                            "title": "플랫폼 아키텍처 개요",
                            "content": "• 6개 핵심 마이크로서비스\n• AI/ML 통합 분석 엔진\n• 실시간 보안 모니터링\n• 확장 가능한 클라우드 인프라",
                            "image": "/static/images/architecture_overview.png"
                        }
                    ]
                },
                estimated_time=15,
                prerequisites=[],
                completion_criteria={"slides_viewed": 3, "video_watched": True}
            ),
            OnboardingStep(
                step_id="admin_dashboard_tour",
                title="🎛️ 관리자 대시보드 둘러보기",
                description="실시간 운영 대시보드의 주요 기능과 메트릭을 학습합니다.",
                content_type="demo",
                content_data={
                    "interactive_demo": True,
                    "demo_url": "http://localhost:9000",
                    "guided_steps": [
                        {
                            "target": "#system-score",
                            "title": "시스템 종합 점수",
                            "description": "현재 시스템의 전반적인 건강 상태를 100점 만점으로 표시합니다.",
                            "action": "click"
                        },
                        {
                            "target": "#system-chart",
                            "title": "실시간 시스템 메트릭",
                            "description": "CPU, 메모리, 응답시간 등의 실시간 성능 지표를 모니터링합니다.",
                            "action": "hover"
                        },
                        {
                            "target": "#optimization-container",
                            "title": "자동 최적화 큐",
                            "description": "AI가 자동으로 감지한 최적화 작업들을 확인하고 승인할 수 있습니다.",
                            "action": "scroll"
                        }
                    ]
                },
                estimated_time=20,
                prerequisites=["admin_welcome"],
                completion_criteria={"demo_completed": True, "steps_followed": 3}
            ),
            OnboardingStep(
                step_id="admin_user_management",
                title="👥 사용자 관리 실습",
                description="신규 사용자 추가, 권한 설정, 그룹 관리를 실습합니다.",
                content_type="practice",
                content_data={
                    "practice_environment": "sandbox",
                    "tasks": [
                        {
                            "task_id": "create_user",
                            "title": "신규 사용자 생성",
                            "description": "테스트 사용자 'john.doe@company.com'을 생성하세요.",
                            "instructions": [
                                "Admin 메뉴 > 사용자 관리 클릭",
                                "'+ 새 사용자' 버튼 클릭",
                                "이메일, 이름, 역할 입력",
                                "'저장' 버튼 클릭"
                            ],
                            "validation": {
                                "endpoint": "/api/admin/users",
                                "method": "GET",
                                "check": "user_exists",
                                "params": {"email": "john.doe@company.com"}
                            }
                        },
                        {
                            "task_id": "assign_permissions",
                            "title": "권한 할당",
                            "description": "생성한 사용자에게 '데이터 분석' 권한을 부여하세요.",
                            "instructions": [
                                "사용자 목록에서 'john.doe' 클릭",
                                "'권한 편집' 탭 선택",
                                "'데이터 분석' 권한 체크",
                                "'적용' 버튼 클릭"
                            ],
                            "validation": {
                                "endpoint": "/api/admin/users/permissions",
                                "method": "GET",
                                "check": "has_permission",
                                "params": {"user_id": "john.doe@company.com", "permission": "data_analysis"}
                            }
                        }
                    ]
                },
                estimated_time=25,
                prerequisites=["admin_dashboard_tour"],
                completion_criteria={"tasks_completed": 2, "practice_score": 80}
            ),
            OnboardingStep(
                step_id="admin_security_setup",
                title="🔒 보안 설정 및 모니터링",
                description="보안 정책 설정과 실시간 위협 모니터링을 학습합니다.",
                content_type="tutorial",
                content_data={
                    "interactive_content": True,
                    "sections": [
                        {
                            "title": "보안 정책 기본 원칙",
                            "content": "• 최소 권한 원칙\n• 다중 인증 (MFA)\n• 정기적인 권한 검토\n• 감사 로그 유지",
                            "quiz": {
                                "question": "다음 중 보안 정책의 핵심 원칙이 아닌 것은?",
                                "options": [
                                    "최소 권한 원칙",
                                    "모든 사용자에게 관리자 권한 부여",
                                    "다중 인증 사용",
                                    "정기적인 권한 검토"
                                ],
                                "correct": 1,
                                "explanation": "모든 사용자에게 관리자 권한을 부여하는 것은 보안상 매우 위험합니다."
                            }
                        },
                        {
                            "title": "실시간 위협 모니터링",
                            "content": "AI 기반 보안 모니터링 시스템이 다음과 같은 위협을 실시간으로 탐지합니다:\n• SQL 인젝션 시도\n• 크로스사이트 스크립팅(XSS)\n• 브루트 포스 공격\n• 비정상적인 접근 패턴",
                            "demo_link": "http://localhost:8007/security/dashboard"
                        }
                    ]
                },
                estimated_time=30,
                prerequisites=["admin_user_management"],
                completion_criteria={"sections_completed": 2, "quiz_passed": True}
            ),
            OnboardingStep(
                step_id="admin_performance_optimization",
                title="⚡ 성능 최적화 및 스케일링",
                description="시스템 성능 모니터링과 자동 최적화 기능을 학습합니다.",
                content_type="demo",
                content_data={
                    "live_demo": True,
                    "scenarios": [
                        {
                            "scenario_name": "높은 CPU 사용률 대응",
                            "description": "CPU 사용률이 85%를 초과했을 때의 자동 대응 과정을 시뮬레이션합니다.",
                            "steps": [
                                "CPU 사용률 급증 감지",
                                "자동 스케일링 트리거",
                                "추가 인스턴스 배포",
                                "로드 밸런싱 재구성",
                                "성능 복구 확인"
                            ],
                            "expected_outcome": "CPU 사용률 60% 이하로 안정화"
                        },
                        {
                            "scenario_name": "메모리 누수 감지 및 대응",
                            "description": "메모리 누수 패턴 감지 시 자동 복구 과정을 학습합니다.",
                            "steps": [
                                "메모리 사용 패턴 분석",
                                "누수 서비스 식별",
                                "자동 재시작 실행",
                                "가비지 컬렉션 강제 실행",
                                "메모리 사용량 정상화 확인"
                            ],
                            "expected_outcome": "메모리 사용률 정상 범위 복구"
                        }
                    ]
                },
                estimated_time=35,
                prerequisites=["admin_security_setup"],
                completion_criteria={"scenarios_completed": 2, "understanding_verified": True}
            ),
            OnboardingStep(
                step_id="admin_final_assessment",
                title="🎓 관리자 인증 평가",
                description="관리자 과정의 최종 평가를 통해 인증을 획득합니다.",
                content_type="quiz",
                content_data={
                    "certification_quiz": True,
                    "passing_score": 80,
                    "time_limit": 30,  # 분
                    "questions": [
                        {
                            "type": "multiple_choice",
                            "question": "시스템 CPU 사용률이 90%를 지속적으로 유지할 때 가장 적절한 대응책은?",
                            "options": [
                                "시스템 재부팅",
                                "자동 스케일링 트리거",
                                "사용자 접근 차단",
                                "로그 파일 삭제"
                            ],
                            "correct": 1,
                            "points": 10
                        },
                        {
                            "type": "multiple_select",
                            "question": "다음 중 보안 모니터링에서 감지해야 할 위협은? (복수 선택)",
                            "options": [
                                "SQL 인젝션 시도",
                                "정상적인 사용자 로그인",
                                "브루트 포스 공격",
                                "XSS 공격 시도"
                            ],
                            "correct": [0, 2, 3],
                            "points": 15
                        },
                        {
                            "type": "scenario",
                            "question": "새로운 직원이 입사했습니다. 마케팅 팀 소속으로 고객 데이터 조회 권한이 필요합니다. 어떤 순서로 계정을 설정하시겠습니까?",
                            "scenario_steps": [
                                "사용자 계정 생성",
                                "마케팅 그룹에 추가",
                                "고객 데이터 조회 권한 부여",
                                "임시 비밀번호 발급",
                                "MFA 설정 안내"
                            ],
                            "correct_order": [0, 3, 1, 2, 4],
                            "points": 20
                        }
                    ]
                },
                estimated_time=30,
                prerequisites=["admin_performance_optimization"],
                completion_criteria={"quiz_score": 80, "certification_earned": "admin_certified"}
            )
        ]
        
        paths["admin"] = LearningPath(
            path_id="admin",
            path_name="관리자 마스터 과정",
            target_role="administrator",
            description="시스템 관리자를 위한 종합적인 학습 과정입니다.",
            total_steps=len(admin_steps),
            estimated_duration=155,  # 총 소요 시간 (분)
            difficulty_level="advanced",
            steps=admin_steps,
            prerequisites=[]
        )
        
        # 일반 사용자 학습 경로
        user_steps = [
            OnboardingStep(
                step_id="user_welcome",
                title="👋 Your Program에 오신 것을 환영합니다!",
                description="플랫폼의 주요 기능과 사용법을 알아봅니다.",
                content_type="tutorial",
                content_data={
                    "welcome_video": "/static/videos/user_welcome.mp4",
                    "key_features": [
                        "📊 실시간 데이터 분석",
                        "🤖 AI 기반 인사이트",
                        "📈 비즈니스 대시보드",
                        "🔒 강화된 보안",
                        "📱 모바일 최적화",
                        "🌐 다국어 지원"
                    ],
                    "navigation_guide": {
                        "dashboard": "메인 대시보드에서 핵심 정보를 한눈에 확인",
                        "analytics": "데이터 분석 도구로 비즈니스 인사이트 도출",
                        "reports": "다양한 형태의 보고서 생성 및 공유",
                        "settings": "개인 설정 및 알림 구성"
                    }
                },
                estimated_time=10,
                prerequisites=[],
                completion_criteria={"video_watched": True, "features_reviewed": 6}
            ),
            OnboardingStep(
                step_id="user_dashboard_basics",
                title="📊 대시보드 기본 사용법",
                description="메인 대시보드의 위젯과 차트를 활용하는 방법을 학습합니다.",
                content_type="practice",
                content_data={
                    "interactive_practice": True,
                    "practice_tasks": [
                        {
                            "task": "대시보드에서 오늘의 핵심 지표 확인하기",
                            "instructions": "대시보드 상단의 KPI 카드들을 클릭하여 상세 정보를 확인하세요.",
                            "success_criteria": "3개 이상의 KPI 카드 클릭"
                        },
                        {
                            "task": "시간 범위 필터 사용하기",
                            "instructions": "우측 상단의 날짜 선택기를 사용하여 지난 7일 데이터로 변경하세요.",
                            "success_criteria": "시간 범위 변경 완료"
                        },
                        {
                            "task": "차트 상호작용 체험하기",
                            "instructions": "매출 트렌드 차트에서 특정 구간을 드래그하여 확대해보세요.",
                            "success_criteria": "차트 줌 기능 사용"
                        }
                    ]
                },
                estimated_time=15,
                prerequisites=["user_welcome"],
                completion_criteria={"tasks_completed": 3}
            ),
            OnboardingStep(
                step_id="user_data_analysis",
                title="🔍 데이터 분석 첫걸음",
                description="기본적인 데이터 필터링과 정렬 방법을 익힙니다.",
                content_type="tutorial",
                content_data={
                    "step_by_step": [
                        {
                            "title": "데이터 테이블 이해하기",
                            "content": "데이터 테이블의 각 컬럼과 행이 의미하는 바를 파악합니다.",
                            "interactive_element": "table_exploration"
                        },
                        {
                            "title": "필터 적용하기",
                            "content": "조건에 맞는 데이터만 표시하도록 필터를 설정합니다.",
                            "interactive_element": "filter_practice"
                        },
                        {
                            "title": "정렬 및 그룹화",
                            "content": "데이터를 의미있는 순서로 정렬하고 그룹별로 묶어봅니다.",
                            "interactive_element": "sort_group_practice"
                        }
                    ]
                },
                estimated_time=20,
                prerequisites=["user_dashboard_basics"],
                completion_criteria={"steps_completed": 3, "practice_score": 70}
            ),
            OnboardingStep(
                step_id="user_reports_creation",
                title="📝 나만의 보고서 만들기",
                description="커스텀 보고서를 생성하고 공유하는 방법을 학습합니다.",
                content_type="practice",
                content_data={
                    "guided_creation": True,
                    "report_templates": [
                        {
                            "name": "일일 매출 리포트",
                            "description": "하루 동안의 매출 현황을 요약한 보고서",
                            "required_fields": ["날짜", "총매출", "거래건수", "평균거래금액"],
                            "chart_types": ["line", "bar", "pie"]
                        },
                        {
                            "name": "고객 분석 리포트",
                            "description": "고객 세그먼트별 행동 패턴 분석",
                            "required_fields": ["고객세그먼트", "방문횟수", "구매전환율", "평균주문금액"],
                            "chart_types": ["scatter", "heatmap", "bar"]
                        }
                    ],
                    "creation_steps": [
                        "보고서 템플릿 선택",
                        "데이터 소스 연결",
                        "필드 매핑 설정",
                        "차트 타입 선택",
                        "스타일 커스터마이징",
                        "미리보기 및 저장"
                    ]
                },
                estimated_time=25,
                prerequisites=["user_data_analysis"],
                completion_criteria={"report_created": True, "report_shared": True}
            ),
            OnboardingStep(
                step_id="user_mobile_app",
                title="📱 모바일 앱 활용하기",
                description="모바일에서 핵심 기능을 사용하는 방법을 익힙니다.",
                content_type="demo",
                content_data={
                    "mobile_simulation": True,
                    "app_features": [
                        {
                            "feature": "푸시 알림 설정",
                            "description": "중요한 지표 변화를 실시간으로 받아보세요",
                            "demo_steps": [
                                "설정 메뉴 열기",
                                "알림 설정 선택",
                                "알림 유형별 ON/OFF 설정",
                                "알림 시간 설정"
                            ]
                        },
                        {
                            "feature": "오프라인 모드",
                            "description": "인터넷이 없어도 저장된 데이터를 확인할 수 있습니다",
                            "demo_steps": [
                                "중요 보고서 오프라인 저장",
                                "연결 끊김 시뮬레이션",
                                "오프라인 데이터 확인",
                                "연결 복구 시 동기화"
                            ]
                        }
                    ]
                },
                estimated_time=15,
                prerequisites=["user_reports_creation"],
                completion_criteria={"mobile_features_tested": 2}
            ),
            OnboardingStep(
                step_id="user_final_quiz",
                title="🎯 사용자 실력 확인 퀴즈",
                description="학습한 내용을 바탕으로 실력을 확인해봅니다.",
                content_type="quiz",
                content_data={
                    "quiz_type": "skill_assessment",
                    "passing_score": 70,
                    "questions": [
                        {
                            "type": "practical",
                            "question": "매출이 전주 대비 20% 이상 증가한 제품을 찾으려면 어떤 필터를 사용해야 할까요?",
                            "options": [
                                "날짜 필터: 지난 주, 증가율 필터: >20%",
                                "제품명 필터: 전체, 정렬: 매출 높은 순",
                                "고객 필터: 신규 고객, 날짜: 이번 주",
                                "카테고리 필터: 전체, 통화: 원화"
                            ],
                            "correct": 0,
                            "points": 20
                        },
                        {
                            "type": "scenario",
                            "question": "월간 보고서를 CEO에게 공유해야 합니다. 가장 적절한 방법은?",
                            "options": [
                                "스크린샷을 찍어서 이메일로 전송",
                                "보고서 PDF로 내보내기 후 공유",
                                "화면을 직접 보여주기",
                                "데이터를 Excel로 복사해서 전송"
                            ],
                            "correct": 1,
                            "points": 15
                        }
                    ]
                },
                estimated_time=15,
                prerequisites=["user_mobile_app"],
                completion_criteria={"quiz_score": 70, "certificate_earned": True}
            )
        ]
        
        paths["user"] = LearningPath(
            path_id="user",
            path_name="사용자 기본 과정",
            target_role="user",
            description="일반 사용자를 위한 기본 활용 과정입니다.",
            total_steps=len(user_steps),
            estimated_duration=100,  # 총 소요 시간 (분)
            difficulty_level="beginner",
            steps=user_steps,
            prerequisites=[]
        )
        
        return paths
    
    async def start_onboarding(self, user_id: str, user_role: str) -> Dict[str, Any]:
        """사용자 온보딩 시작"""
        if user_role not in self.learning_paths:
            raise ValueError(f"지원하지 않는 사용자 역할: {user_role}")
        
        # 기존 진행상황 확인
        existing_progress = self.get_user_progress(user_id)
        if existing_progress:
            logger.info(f"기존 온보딩 진행상황 발견: {user_id}")
            return {
                "status": "resumed",
                "message": "기존 진행상황에서 계속 진행합니다.",
                "progress": existing_progress
            }
        
        # 새로운 온보딩 시작
        learning_path = self.learning_paths[user_role]
        first_step = learning_path.steps[0].step_id
        
        progress = UserProgress(
            user_id=user_id,
            user_role=user_role,
            current_step=first_step,
            completed_steps=[],
            start_time=datetime.now(),
            last_activity=datetime.now(),
            total_time_spent=0,
            quiz_scores={},
            practice_results={},
            overall_progress=0.0,
            certification_earned=[]
        )
        
        self.save_user_progress(progress)
        
        logger.info(f"새로운 온보딩 시작: {user_id} ({user_role})")
        
        return {
            "status": "started",
            "message": f"{learning_path.path_name} 과정을 시작합니다.",
            "learning_path": asdict(learning_path),
            "current_step": asdict(learning_path.steps[0]),
            "progress": asdict(progress)
        }
    
    async def get_current_step(self, user_id: str) -> Dict[str, Any]:
        """현재 학습 단계 조회"""
        progress = self.get_user_progress(user_id)
        if not progress:
            return {"error": "온보딩 진행상황을 찾을 수 없습니다."}
        
        learning_path = self.learning_paths[progress.user_role]
        current_step = None
        
        for step in learning_path.steps:
            if step.step_id == progress.current_step:
                current_step = step
                break
        
        if not current_step:
            return {"error": "현재 단계를 찾을 수 없습니다."}
        
        return {
            "step": asdict(current_step),
            "progress": asdict(progress),
            "learning_path_info": {
                "path_name": learning_path.path_name,
                "total_steps": learning_path.total_steps,
                "estimated_duration": learning_path.estimated_duration
            }
        }
    
    async def complete_step(self, user_id: str, step_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """학습 단계 완료 처리"""
        progress = self.get_user_progress(user_id)
        if not progress:
            return {"error": "온보딩 진행상황을 찾을 수 없습니다."}
        
        learning_path = self.learning_paths[progress.user_role]
        current_step = None
        next_step = None
        
        # 현재 단계 찾기
        for i, step in enumerate(learning_path.steps):
            if step.step_id == step_id:
                current_step = step
                if i + 1 < len(learning_path.steps):
                    next_step = learning_path.steps[i + 1]
                break
        
        if not current_step:
            return {"error": "단계를 찾을 수 없습니다."}
        
        # 완료 조건 검증
        if not self._validate_completion(current_step, completion_data):
            return {"error": "완료 조건을 만족하지 않습니다.", "criteria": current_step.completion_criteria}
        
        # 진행상황 업데이트
        if step_id not in progress.completed_steps:
            progress.completed_steps.append(step_id)
        
        # 퀴즈 점수 저장
        if current_step.content_type == "quiz" and "quiz_score" in completion_data:
            progress.quiz_scores[step_id] = completion_data["quiz_score"]
        
        # 실습 결과 저장
        if current_step.content_type == "practice" and "practice_success" in completion_data:
            progress.practice_results[step_id] = completion_data["practice_success"]
        
        # 인증 획득 확인
        if "certification_earned" in completion_data:
            if completion_data["certification_earned"] not in progress.certification_earned:
                progress.certification_earned.append(completion_data["certification_earned"])
        
        # 다음 단계로 이동
        if next_step:
            progress.current_step = next_step.step_id
        
        # 전체 진행률 계산
        progress.overall_progress = (len(progress.completed_steps) / learning_path.total_steps) * 100
        progress.last_activity = datetime.now()
        
        # 시간 추가
        if "time_spent" in completion_data:
            progress.total_time_spent += completion_data["time_spent"]
        
        self.save_user_progress(progress)
        
        # 학습 세션 기록
        await self._record_learning_session(user_id, step_id, completion_data)
        
        # 완료 응답 생성
        response = {
            "status": "completed",
            "message": f"'{current_step.title}' 단계를 완료했습니다!",
            "progress": asdict(progress)
        }
        
        if next_step:
            response["next_step"] = asdict(next_step)
        else:
            response["course_completed"] = True
            response["message"] += f" 🎉 {learning_path.path_name} 과정을 모두 완료했습니다!"
            
            # 최종 인증서 발급
            if progress.certification_earned:
                response["certifications"] = progress.certification_earned
        
        # WebSocket으로 실시간 업데이트
        if user_id in self.websocket_connections:
            await self.websocket_connections[user_id].send_text(json.dumps({
                "type": "step_completed",
                "data": response
            }))
        
        logger.info(f"단계 완료: {user_id} - {step_id}")
        
        return response
    
    def _validate_completion(self, step: OnboardingStep, completion_data: Dict[str, Any]) -> bool:
        """완료 조건 검증"""
        criteria = step.completion_criteria
        
        for key, required_value in criteria.items():
            if key not in completion_data:
                return False
            
            actual_value = completion_data[key]
            
            # 숫자 비교 (최소값)
            if isinstance(required_value, (int, float)):
                if actual_value < required_value:
                    return False
            
            # 불린 값 비교
            elif isinstance(required_value, bool):
                if actual_value != required_value:
                    return False
            
            # 문자열 비교
            elif isinstance(required_value, str):
                if actual_value != required_value:
                    return False
        
        return True
    
    async def _record_learning_session(self, user_id: str, step_id: str, completion_data: Dict[str, Any]):
        """학습 세션 기록"""
        session_id = f"{user_id}_{step_id}_{int(time.time())}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO learning_sessions 
            (session_id, user_id, step_id, start_time, end_time, duration, success, feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            user_id,
            step_id,
            completion_data.get("start_time", datetime.now().isoformat()),
            datetime.now().isoformat(),
            completion_data.get("time_spent", 0),
            completion_data.get("success", True),
            completion_data.get("feedback", "")
        ))
        
        conn.commit()
        conn.close()
    
    def get_user_progress(self, user_id: str) -> Optional[UserProgress]:
        """사용자 진행상황 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM user_progress WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if not row:
            return None
        
        return UserProgress(
            user_id=row[0],
            user_role=row[1],
            current_step=row[2],
            completed_steps=json.loads(row[3]) if row[3] else [],
            start_time=datetime.fromisoformat(row[4]),
            last_activity=datetime.fromisoformat(row[5]),
            total_time_spent=row[6],
            quiz_scores=json.loads(row[7]) if row[7] else {},
            practice_results=json.loads(row[8]) if row[8] else {},
            overall_progress=row[9],
            certification_earned=json.loads(row[10]) if row[10] else []
        )
    
    def save_user_progress(self, progress: UserProgress):
        """사용자 진행상황 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_progress 
            (user_id, user_role, current_step, completed_steps, start_time, 
             last_activity, total_time_spent, quiz_scores, practice_results, 
             overall_progress, certification_earned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            progress.user_id,
            progress.user_role,
            progress.current_step,
            json.dumps(progress.completed_steps),
            progress.start_time.isoformat(),
            progress.last_activity.isoformat(),
            progress.total_time_spent,
            json.dumps(progress.quiz_scores),
            json.dumps(progress.practice_results),
            progress.overall_progress,
            json.dumps(progress.certification_earned)
        ))
        
        conn.commit()
        conn.close()
    
    async def get_learning_analytics(self) -> Dict[str, Any]:
        """학습 분석 데이터 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 전체 통계
        cursor.execute("SELECT COUNT(*) FROM user_progress")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(overall_progress) FROM user_progress")
        avg_progress = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM user_progress WHERE overall_progress = 100")
        completed_users = cursor.fetchone()[0]
        
        # 역할별 통계
        cursor.execute("""
            SELECT user_role, COUNT(*), AVG(overall_progress), AVG(total_time_spent)
            FROM user_progress 
            GROUP BY user_role
        """)
        role_stats = {}
        for row in cursor.fetchall():
            role_stats[row[0]] = {
                "user_count": row[1],
                "avg_progress": row[2],
                "avg_time_spent": row[3]
            }
        
        # 단계별 완료율
        cursor.execute("""
            SELECT step_id, COUNT(*) as completion_count
            FROM learning_sessions 
            WHERE success = 1
            GROUP BY step_id
        """)
        step_completion_rates = {}
        for row in cursor.fetchall():
            step_completion_rates[row[0]] = row[1]
        
        conn.close()
        
        return {
            "total_users": total_users,
            "average_progress": avg_progress,
            "completion_rate": (completed_users / total_users * 100) if total_users > 0 else 0,
            "role_statistics": role_stats,
            "step_completion_rates": step_completion_rates,
            "generated_at": datetime.now().isoformat()
        }

# Pydantic 모델들
class OnboardingStartRequest(BaseModel):
    user_id: str
    user_role: str

class StepCompletionRequest(BaseModel):
    user_id: str
    step_id: str
    completion_data: Dict[str, Any]

class FeedbackRequest(BaseModel):
    user_id: str
    step_id: str
    rating: int
    comment: str

# FastAPI 애플리케이션
app = FastAPI(title="Your Program 사용자 온보딩 시스템", version="1.0.0")

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# 전역 온보딩 매니저
onboarding_manager = OnboardingManager()

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작시 초기화"""
    logger.info("🎓 사용자 온보딩 시스템 시작됨")

@app.get("/", response_class=HTMLResponse)
async def onboarding_home():
    """온보딩 홈페이지"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Your Program 온보딩</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .role-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 16px;
                color: white;
                padding: 2rem;
                margin: 1rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                cursor: pointer;
            }
            .role-card:hover {
                transform: translateY(-8px);
                box-shadow: 0 16px 48px rgba(0, 0, 0, 0.18);
            }
            .feature-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
        </style>
    </head>
    <body class="bg-gray-50">
        <div class="container mx-auto px-4 py-8">
            <!-- 헤더 -->
            <div class="text-center mb-12">
                <h1 class="text-5xl font-bold text-gray-800 mb-4">
                    🎓 Your Program 온보딩
                </h1>
                <p class="text-xl text-gray-600 max-w-2xl mx-auto">
                    역할에 맞는 맞춤형 학습 경로로 플랫폼을 마스터하세요!
                </p>
            </div>
            
            <!-- 역할 선택 -->
            <div class="mb-16">
                <h2 class="text-3xl font-bold text-center text-gray-800 mb-8">
                    당신의 역할을 선택하세요
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                    <!-- 관리자 카드 -->
                    <div class="role-card" onclick="startOnboarding('admin')">
                        <div class="feature-icon text-center">🛠️</div>
                        <h3 class="text-2xl font-bold text-center mb-4">시스템 관리자</h3>
                        <ul class="space-y-2">
                            <li>• 시스템 운영 및 모니터링</li>
                            <li>• 사용자 및 권한 관리</li>
                            <li>• 보안 정책 설정</li>
                            <li>• 성능 최적화</li>
                        </ul>
                        <div class="mt-6 text-center">
                            <span class="bg-white bg-opacity-20 px-4 py-2 rounded-full text-sm">
                                ⏱️ 약 2.5시간 소요
                            </span>
                        </div>
                    </div>
                    
                    <!-- 일반 사용자 카드 -->
                    <div class="role-card" onclick="startOnboarding('user')">
                        <div class="feature-icon text-center">👤</div>
                        <h3 class="text-2xl font-bold text-center mb-4">일반 사용자</h3>
                        <ul class="space-y-2">
                            <li>• 대시보드 활용</li>
                            <li>• 데이터 분석 기초</li>
                            <li>• 보고서 생성</li>
                            <li>• 모바일 앱 사용</li>
                        </ul>
                        <div class="mt-6 text-center">
                            <span class="bg-white bg-opacity-20 px-4 py-2 rounded-full text-sm">
                                ⏱️ 약 1.5시간 소요
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 학습 진행률 (기존 사용자용) -->
            <div id="progress-section" class="bg-white rounded-2xl p-8 shadow-lg max-w-4xl mx-auto mb-16" style="display: none;">
                <h3 class="text-2xl font-bold text-gray-800 mb-6">📊 학습 진행률</h3>
                <div class="bg-gray-200 rounded-full h-4 mb-4">
                    <div id="progress-bar" class="bg-gradient-to-r from-blue-500 to-purple-600 h-4 rounded-full transition-all duration-500" style="width: 0%"></div>
                </div>
                <div class="flex justify-between text-sm text-gray-600">
                    <span id="progress-text">0% 완료</span>
                    <span id="time-spent">소요 시간: 0분</span>
                </div>
                <button id="continue-btn" class="mt-6 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
                    학습 계속하기
                </button>
            </div>
            
            <!-- 주요 기능 소개 -->
            <div class="mb-16">
                <h2 class="text-3xl font-bold text-center text-gray-800 mb-12">
                    🌟 온보딩 시스템 특징
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                    <div class="text-center">
                        <div class="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <span class="text-2xl">🎯</span>
                        </div>
                        <h3 class="text-xl font-semibold mb-2">맞춤형 학습 경로</h3>
                        <p class="text-gray-600">역할과 경험에 따른 개인화된 학습 과정</p>
                    </div>
                    <div class="text-center">
                        <div class="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <span class="text-2xl">🏃</span>
                        </div>
                        <h3 class="text-xl font-semibold mb-2">실습 중심 학습</h3>
                        <p class="text-gray-600">이론과 실습을 결합한 체험형 교육</p>
                    </div>
                    <div class="text-center">
                        <div class="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <span class="text-2xl">🏆</span>
                        </div>
                        <h3 class="text-xl font-semibold mb-2">인증 시스템</h3>
                        <p class="text-gray-600">완료 시 공식 인증서 발급</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            function startOnboarding(role) {
                // 사용자 ID 입력 받기
                const userId = prompt('사용자 ID를 입력하세요 (예: john.doe@company.com):');
                if (!userId) return;
                
                // 온보딩 시작 API 호출
                fetch('/api/onboarding/start', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_id: userId,
                        user_role: role
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'started' || data.status === 'resumed') {
                        // 온보딩 페이지로 이동
                        window.location.href = `/onboarding/${userId}`;
                    } else {
                        alert('온보딩 시작 중 오류가 발생했습니다.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('온보딩 시작 중 오류가 발생했습니다.');
                });
            }
            
            // 페이지 로드 시 기존 진행률 확인
            document.addEventListener('DOMContentLoaded', function() {
                const urlParams = new URLSearchParams(window.location.search);
                const userId = urlParams.get('user');
                
                if (userId) {
                    checkExistingProgress(userId);
                }
            });
            
            function checkExistingProgress(userId) {
                fetch(`/api/onboarding/progress/${userId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.progress) {
                        showProgressSection(data.progress);
                    }
                })
                .catch(error => {
                    console.error('Error checking progress:', error);
                });
            }
            
            function showProgressSection(progress) {
                const progressSection = document.getElementById('progress-section');
                const progressBar = document.getElementById('progress-bar');
                const progressText = document.getElementById('progress-text');
                const timeSpent = document.getElementById('time-spent');
                
                progressSection.style.display = 'block';
                progressBar.style.width = progress.overall_progress + '%';
                progressText.textContent = Math.round(progress.overall_progress) + '% 완료';
                timeSpent.textContent = `소요 시간: ${progress.total_time_spent}분`;
                
                document.getElementById('continue-btn').onclick = function() {
                    window.location.href = `/onboarding/${progress.user_id}`;
                };
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/onboarding/start")
async def start_onboarding(request: OnboardingStartRequest):
    """온보딩 시작 API"""
    try:
        result = await onboarding_manager.start_onboarding(request.user_id, request.user_role)
        return result
    except Exception as e:
        logger.error(f"온보딩 시작 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/onboarding/progress/{user_id}")
async def get_progress(user_id: str):
    """진행상황 조회 API"""
    progress = onboarding_manager.get_user_progress(user_id)
    if progress:
        return {"progress": asdict(progress)}
    else:
        return {"progress": None}

@app.get("/api/onboarding/current/{user_id}")
async def get_current_step(user_id: str):
    """현재 단계 조회 API"""
    return await onboarding_manager.get_current_step(user_id)

@app.post("/api/onboarding/complete")
async def complete_step(request: StepCompletionRequest):
    """단계 완료 API"""
    return await onboarding_manager.complete_step(
        request.user_id, 
        request.step_id, 
        request.completion_data
    )

@app.get("/api/onboarding/analytics")
async def get_analytics():
    """학습 분석 데이터 API"""
    return await onboarding_manager.get_learning_analytics()

@app.websocket("/ws/onboarding/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket 엔드포인트"""
    await websocket.accept()
    onboarding_manager.websocket_connections[user_id] = websocket
    logger.info(f"📡 온보딩 WebSocket 연결: {user_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            # 클라이언트로부터 메시지 처리
            message = json.loads(data)
            
            if message.get("type") == "heartbeat":
                await websocket.send_text(json.dumps({"type": "heartbeat", "status": "alive"}))
    
    except WebSocketDisconnect:
        if user_id in onboarding_manager.websocket_connections:
            del onboarding_manager.websocket_connections[user_id]
        logger.info(f"📡 온보딩 WebSocket 연결 종료: {user_id}")

@app.get("/onboarding/{user_id}", response_class=HTMLResponse)
async def onboarding_interface(user_id: str):
    """개별 온보딩 인터페이스"""
    # 실제 구현에서는 더 복잡한 인터랙티브 인터페이스를 제공
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>온보딩 - {user_id}</title>
        <meta charset="utf-8">
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto px-4 py-8">
            <h1 class="text-3xl font-bold mb-6">🎓 학습 진행 중...</h1>
            <div id="content">
                <p>온보딩 컨텐츠를 로딩 중입니다...</p>
            </div>
        </div>
        
        <script>
            // WebSocket 연결 및 실시간 업데이트
            const ws = new WebSocket(`ws://localhost:8080/ws/onboarding/{user_id}`);
            
            ws.onopen = function() {{
                loadCurrentStep();
            }};
            
            function loadCurrentStep() {{
                fetch(`/api/onboarding/current/{user_id}`)
                .then(response => response.json())
                .then(data => {{
                    if (data.step) {{
                        renderStep(data.step, data.progress);
                    }}
                }});
            }}
            
            function renderStep(step, progress) {{
                const content = document.getElementById('content');
                content.innerHTML = `
                    <div class="bg-white rounded-lg p-6 shadow-lg">
                        <h2 class="text-2xl font-bold mb-4">${{step.title}}</h2>
                        <p class="text-gray-600 mb-6">${{step.description}}</p>
                        <div class="bg-gray-200 rounded-full h-2 mb-4">
                            <div class="bg-blue-600 h-2 rounded-full" style="width: ${{progress.overall_progress}}%"></div>
                        </div>
                        <p class="text-sm text-gray-500">${{Math.round(progress.overall_progress)}}% 완료</p>
                        <button onclick="completeStep('${{step.step_id}}')" 
                                class="mt-6 bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
                            다음 단계로
                        </button>
                    </div>
                `;
            }}
            
            function completeStep(stepId) {{
                fetch('/api/onboarding/complete', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        user_id: '{user_id}',
                        step_id: stepId,
                        completion_data: {{
                            'completed': true,
                            'time_spent': 5
                        }}
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.next_step) {{
                        renderStep(data.next_step, data.progress);
                    }} else if (data.course_completed) {{
                        showCompletion(data);
                    }}
                }});
            }}
            
            function showCompletion(data) {{
                const content = document.getElementById('content');
                content.innerHTML = `
                    <div class="text-center">
                        <div class="text-6xl mb-4">🎉</div>
                        <h2 class="text-3xl font-bold text-green-600 mb-4">축하합니다!</h2>
                        <p class="text-lg text-gray-600 mb-6">온보딩 과정을 성공적으로 완료했습니다.</p>
                        ${{data.certifications ? `<p class="text-md text-blue-600">획득한 인증: ${{data.certifications.join(', ')}}</p>` : ''}}
                        <button onclick="window.location.href='/'" 
                                class="mt-6 bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700">
                            메인으로 돌아가기
                        </button>
                    </div>
                `;
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/health")
async def health_check():
    """헬스체크 API"""
    return {
        "status": "healthy",
        "active_connections": len(onboarding_manager.websocket_connections),
        "total_learning_paths": len(onboarding_manager.learning_paths),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info("🎓 Your Program 대화형 사용자 온보딩 시스템 시작")
    uvicorn.run(
        "interactive_user_onboarding:app",
        host="0.0.0.0", 
        port=8080,
        reload=False,
        log_level="info"
    ) 