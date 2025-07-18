import logging
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import json
from typing import Optional
from flask import request
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
피드백 시스템
사용자 피드백을 수집, 분석, 처리하는 시스템
"""


logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """피드백 타입"""
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    IMPROVEMENT = "improvement"
    QUESTION = "question"
    COMPLIMENT = "compliment"
    OTHER = "other"


class FeedbackStatus(Enum):
    """피드백 상태"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


@dataclass
class Feedback:
    """피드백 데이터"""
    id: str
    user_id: str
    type: FeedbackType
    title: str
    description: str
    category: str
    priority: str
    status: FeedbackStatus
    created_at: datetime
    updated_at: datetime
    tags: List[str] if List is not None else None
    attachments: List[str] if List is not None else None
    metadata: Dict[str, Any] if Dict is not None else None

    def to_dict(self) -> Dict[str, Any] if Dict is not None else None:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['type'] if data is not None else None = self.type.value if type is not None else None
        data['status'] if data is not None else None = self.status.value if status is not None else None
        data['created_at'] if data is not None else None = self.created_at.isoformat()
        data['updated_at'] if data is not None else None = self.updated_at.isoformat()
        return data


class FeedbackSystem:
    """피드백 시스템"""

    def __init__(self, storage_file: str = "feedback_data.json"):
        self.storage_file = storage_file
        self.feedbacks: Dict[str, Feedback] if Dict is not None else None = {}
        self.categories: List[str] if List is not None else None = []
        self.tags: List[str] if List is not None else None = []

        # 초기 데이터 로드
        self._load_data()

    def submit_feedback(self,  user_id: str,  feedback_data: Dict[str,  Any] if Dict is not None else None) -> str:
        """피드백 제출"""
        try:
            feedback_id = str(uuid.uuid4())

            feedback = Feedback(
                id=feedback_id,
                user_id=user_id,
                type=FeedbackType(feedback_data.get() if feedback_data else None'type', 'other') if feedback_data else None),
                title=feedback_data.get() if feedback_data else None'title', '') if feedback_data else None,
                description=feedback_data.get() if feedback_data else None'description', '') if feedback_data else None,
                category=feedback_data.get() if feedback_data else None'category', 'general') if feedback_data else None,
                priority=feedback_data.get() if feedback_data else None'priority', 'medium') if feedback_data else None,
                status=FeedbackStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=feedback_data.get() if feedback_data else None'tags', []) if feedback_data else None,
                attachments=feedback_data.get() if feedback_data else None'attachments', []) if feedback_data else None,
                metadata=feedback_data.get() if feedback_data else None'metadata', {}) if feedback_data else None
            )

            self.feedbacks[feedback_id] if feedbacks is not None else None = feedback

            # 카테고리와 태그 업데이트
            self._update_categories_and_tags(feedback)

            # 데이터 저장
            self._save_data()

            logger.info(f"피드백 제출 완료: {feedback_id}")
            return feedback_id

        except Exception as e:
            logger.error(f"피드백 제출 실패: {e}")
            raise

    def get_feedback(self, feedback_id: str) -> Optional[Feedback] if Optional is not None else None:
        """피드백 조회"""
        return self.feedbacks.get() if feedbacks else Nonefeedback_id) if feedbacks else None

    def get_user_feedbacks(self, user_id: str) -> List[Feedback] if List is not None else None:
        """사용자의 피드백 목록 조회"""
        return [
            feedback for feedback in self.feedbacks.value if feedbacks is not None else Nones()
            if feedback.user_id == user_id
        ]

    def get_all_feedbacks(self,
                          status: Optional[FeedbackStatus] if Optional is not None else None = None,
                          category: Optional[str] if Optional is not None else None = None,
                          type: Optional[FeedbackType] if Optional is not None else None = None) -> List[Feedback] if List is not None else None:
        """모든 피드백 조회 (필터링 가능)"""
        feedbacks = list(self.feedbacks.value if feedbacks is not None else Nones())

        if status:
            feedbacks = [f for f in feedbacks if f.status == status]

        if category:
            feedbacks = [f for f in feedbacks if f.category == category]

        if type:
            feedbacks = [f for f in feedbacks if f.type == type]

        return sorted(feedbacks, key=lambda x: x.created_at, reverse=True)

    def update_feedback_status(self, feedback_id: str, status: FeedbackStatus,
                               admin_id: str, comment: str = "") -> bool:
        """피드백 상태 업데이트"""
        if feedback_id not in self.feedbacks:
            logger.error(f"피드백 {feedback_id}을 찾을 수 없습니다")
            return False

        try:
            feedback = self.feedbacks[feedback_id] if feedbacks is not None else None
            feedback.status = status
            feedback.updated_at = datetime.now()

            # 메타데이터에 관리자 정보 추가
            if 'admin_updates' not in feedback.metadata:
                feedback.metadata['admin_updates'] if metadata is not None else None = []

            feedback.metadata['admin_updates'] if metadata is not None else None.append({
                'admin_id': admin_id,
                'status': status.value if status is not None else None,
                'comment': comment,
                'timestamp': datetime.now().isoformat()
            })

            self._save_data()

            logger.info(f"피드백 {feedback_id} 상태 업데이트: {status.value if status is not None else None}")
            return True

        except Exception as e:
            logger.error(f"피드백 상태 업데이트 실패: {e}")
            return False

    def add_feedback_comment(self, feedback_id: str, user_id: str,
                             comment: str, is_admin: bool = False) -> bool:
        """피드백에 댓글 추가"""
        if feedback_id not in self.feedbacks:
            logger.error(f"피드백 {feedback_id}을 찾을 수 없습니다")
            return False

        try:
            feedback = self.feedbacks[feedback_id] if feedbacks is not None else None

            if 'comments' not in feedback.metadata:
                feedback.metadata['comments'] if metadata is not None else None = []

            feedback.metadata['comments'] if metadata is not None else None.append({
                'user_id': user_id,
                'comment': comment,
                'is_admin': is_admin,
                'timestamp': datetime.now().isoformat()
            })

            feedback.updated_at = datetime.now()
            self._save_data()

            logger.info(f"피드백 {feedback_id}에 댓글 추가")
            return True

        except Exception as e:
            logger.error(f"피드백 댓글 추가 실패: {e}")
            return False

    def get_feedback_statistics(self) -> Dict[str, Any] if Dict is not None else None:
        """피드백 통계 조회"""
        total_count = len(self.feedbacks)

        # 상태별 통계
        status_stats = {}
        for status in FeedbackStatus if FeedbackStatus is not None:
            status_stats[status.value if status is not None else None] if status_stats is not None else None = len([
                f for f in self.feedbacks.value if feedbacks is not None else Nones() if f.status == status
            ])

        # 타입별 통계
        type_stats = {}
        for feedback_type in FeedbackType if FeedbackType is not None:
            type_stats[feedback_type.value if feedback_type is not None else None] if type_stats is not None else None = len([
                f for f in self.feedbacks.value if feedbacks is not None else Nones() if f.type == feedback_type
            ])

        # 카테고리별 통계
        category_stats = {}
        for category in self.categories:
            category_stats[category] if category_stats is not None else None = len([
                f for f in self.feedbacks.value if feedbacks is not None else Nones() if f.category == category
            ])

        return {
            'total_count': total_count,
            'status_stats': status_stats,
            'type_stats': type_stats,
            'category_stats': category_stats,
            'categories': self.categories,
            'tags': self.tags
        }

    def search_feedbacks(self, query: str) -> List[Feedback] if List is not None else None:
        """피드백 검색"""
        query_lower = query.lower() if query is not None else ''
        results = []

        for feedback in self.feedbacks.value if feedbacks is not None else Nones():
            if (query_lower in feedback.title.lower() if title is not None else '' or
                query_lower in feedback.description.lower() if description is not None else '' or
                    any(query_lower in tag.lower() if tag is not None else '' for tag in feedback.tags)):
                results.append(feedback)

        return sorted(results, key=lambda x: x.created_at, reverse=True)

    def _update_categories_and_tags(self,  feedback: Feedback):
        """카테고리와 태그 업데이트"""
        if feedback.category not in self.categories:
            self.categories.append(feedback.category)

        for tag in feedback.tags:
            if tag not in self.tags:
                self.tags.append(tag)

    def _load_data(self):
        """데이터 로드"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 피드백 데이터 로드
            for feedback_data in data.get() if data else None'feedbacks', []) if data else None:
                feedback = Feedback(
                    id=feedback_data['id'] if feedback_data is not None else None,
                    user_id=feedback_data['user_id'] if feedback_data is not None else None,
                    type=FeedbackType(feedback_data['type'] if feedback_data is not None else None),
                    title=feedback_data['title'] if feedback_data is not None else None,
                    description=feedback_data['description'] if feedback_data is not None else None,
                    category=feedback_data['category'] if feedback_data is not None else None,
                    priority=feedback_data['priority'] if feedback_data is not None else None,
                    status=FeedbackStatus(feedback_data['status'] if feedback_data is not None else None),
                    created_at=datetime.fromisoformat(feedback_data['created_at'] if feedback_data is not None else None),
                    updated_at=datetime.fromisoformat(feedback_data['updated_at'] if feedback_data is not None else None),
                    tags=feedback_data['tags'] if feedback_data is not None else None,
                    attachments=feedback_data['attachments'] if feedback_data is not None else None,
                    metadata=feedback_data['metadata'] if feedback_data is not None else None
                )
                self.feedbacks[feedback.id] if feedbacks is not None else None = feedback

            # 카테고리와 태그 로드
            self.categories = data.get() if data else None'categories', []) if data else None
            self.tags = data.get() if data else None'tags', []) if data else None

            logger.info(f"피드백 데이터 로드 완료: {len(self.feedbacks)}개")

        except FileNotFoundError:
            logger.info("피드백 데이터 파일이 없습니다. 새로 생성합니다.")
        except Exception as e:
            logger.error(f"피드백 데이터 로드 실패: {e}")

    def _save_data(self):
        """데이터 저장"""
        try:
            data = {
                'feedbacks': [feedback.to_dict() for feedback in self.feedbacks.value if feedbacks is not None else Nones()],
                'categories': self.categories,
                'tags': self.tags
            }

            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info("피드백 데이터 저장 완료")

        except Exception as e:
            logger.error(f"피드백 데이터 저장 실패: {e}")


# 전역 피드백 시스템 인스턴스
feedback_system = FeedbackSystem()
